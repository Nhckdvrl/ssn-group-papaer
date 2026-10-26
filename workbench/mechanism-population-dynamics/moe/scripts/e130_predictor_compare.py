"""POST-HOC E130 predictor comparison; BF16 logits -> FP32 log_softmax, no training."""
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import OlmoForCausalLM
import e123_frozen_moe as base
import e127_predictive_fidelity as fidelity
import e130_finalize as endpoint
from e124_functional_capture import tensor_state_hash

WB = Path(__file__).resolve().parents[1]
ANCHOR = "5082e19161cc6eed4276c03490e531b982e27fb74c1eab8a0f452d1dc0824851"
EXTRA = ("kl_student_to_teacher", "top1_agreement")


def metrics(q, p, targets):
    standard = fidelity.token_metrics(q, p, targets)
    reverse = (p.exp() * (p - q)).sum(-1)
    agreement = (q.argmax(-1) == p.argmax(-1)).float()
    return torch.cat((standard, reverse[..., None], agreement[..., None]), -1)


def summarize(rows):
    result = fidelity.summarize(rows, 1000)
    groups = {}
    for row in rows:
        groups.setdefault((row["source"], row["file_id"]), np.zeros(3))[:] += [row[k] for k in EXTRA] + [row["tokens"]]
    values = np.array(list(groups.values()))
    draws = np.random.default_rng(127).integers(0, len(values), (1000, len(values)))
    samples, total = values[draws].sum(1), values.sum(0)
    intervals = np.quantile(samples[:, :2] / samples[:, 2:], [.025, .975], axis=0)
    result.update({k: {"mean": float(total[i] / total[2]), "ci95": intervals[:, i].tolist()} for i, k in enumerate(EXTRA)})
    return result


def read_run(path):
    path = Path(path).resolve()
    if path.name != "checkpoint.pt":
        raise ValueError("Only the registered final checkpoint.pt is accepted")
    summary, provenance, protocol = endpoint.validate(path.parent)
    checksum = base.sha256_file(path)
    archive = Path.home() / "mechpop_cache" / f"e130_{summary['run_id'].removeprefix('E130-')}_512m" / "archive_manifest.json"
    if not archive.is_file() or json.loads(archive.read_text())["checkpoint_sha256"] != checksum:
        raise ValueError("Completed archive/checkpoint SHA256 differs or is missing")
    checkpoint = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
    state = checkpoint["replacement_state"]
    if any(t.dtype != torch.float32 for t in state.values()):
        raise ValueError("Registered replacement weights must be FP32")
    proof = {"checkpoint": str(path), "checkpoint_sha256": checksum,
             "replacement_tensor_sha256": tensor_state_hash(state), "config_hash": summary["config_hash"],
             "provenance_sha256": base.sha256_file(path.parent / "provenance.json"),
             "protocol_sha256": base.sha256_file(path.parent / "driver_protocol.json"),
             "archive_manifest_sha256": base.sha256_file(archive), "step": checkpoint["step"],
             "seed": provenance["args"]["seed"], "order_seed": provenance["args"]["order_seed"]}
    return state, provenance, summary, proof


@torch.no_grad()
def evaluate(args):
    started = time.monotonic()
    paths = {"reference": args.reference}
    for specification in args.compare:
        name, path = specification.split("=", 1)
        if not name or name in paths:
            raise ValueError("Comparison IDs must be nonempty and unique")
        paths[name] = path
    runs = {name: read_run(path) for name, path in paths.items()}
    config = runs["reference"][1]["args"]
    if runs["reference"][3]["replacement_tensor_sha256"] != ANCHOR:
        raise ValueError("Reference is not the bit-identical original seed0 endpoint bank")
    resolve = lambda path: Path(path) if Path(path).is_absolute() else WB / path
    data = base.TokenData(resolve(args.data or config["data"]), config["seq_len"])
    windows = data.fixed_windows("held", config["eval_sequences"], config["eval_seed"])
    if (len(windows), config["seq_len"], config["batch_size"], config["dtype"]) != (512, 512, 16, "bfloat16"):
        raise ValueError("Expected the E130 512-window/262144-token BF16 evaluation")
    for _, prov, _, _ in runs.values():
        fidelity.guard_inputs(prov, data, windows)
        if any(prov["args"][key] != config[key] for key in ("model", "layer", "expert_size", "experts", "top_k")):
            raise ValueError("Model/bank architecture differs between runs")
    scoring = argparse.Namespace(device=args.device, dtype="bfloat16")
    model = OlmoForCausalLM.from_pretrained(resolve(args.model or config["model"]), local_files_only=True,
                dtype=torch.bfloat16, attn_implementation="sdpa").to(args.device).eval().requires_grad_(False)
    layer, prefix = config["layer"], f"model.layers.{config['layer']}.mlp."
    original, frozen = model.model.layers[layer].mlp, base.sampled_parameter_hash(model, prefix)
    banks, proofs, expected = {}, {}, {}
    for name, (state, prov, summary, proof) in runs.items():
        if prov["frozen_sample_hash"] != frozen:
            raise ValueError("Frozen backbone fingerprint differs")
        bank = base.TensorMoE(model.config.hidden_size, config["expert_size"], config["experts"], config["top_k"], config["init_std"])
        bank.load_state_dict(state, strict=True)
        banks[name] = bank.to(args.device).eval().requires_grad_(False)
        proofs[name], expected[name] = proof, next(e["held"]["file"]["mean"] for e in summary["evaluations"] if e["step"] == 62500)
    del runs, state
    names = fidelity.METRICS + EXTRA
    rows, input_hash, noise = {name: [] for name in args_ids(paths)}, hashlib.sha256(), None
    try:
        for batch_index, (batch, metadata) in enumerate(data.iter_fixed("held", windows, 16)):
            if time.monotonic() - started > args.max_seconds:
                raise TimeoutError("Read-only diagnostic resource budget exhausted")
            input_hash.update(batch.numpy().astype("<i8", copy=False).tobytes())
            batch = batch.to(args.device)
            model.model.layers[layer].mlp = banks["reference"]
            q = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
            if batch_index == 0:
                repeated = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
                identity = metrics(q, repeated, batch[:, 1:])
                noise = {"forward_kl_max_abs": float(identity[..., 0].abs().max()),
                         "reverse_kl_max_abs": float(identity[..., 4].abs().max()), "top1_agreement": float(identity[..., 5].mean()),
                         "max_abs_log_probability_difference": float((q - repeated).abs().max()), "tokens": batch[:, 1:].numel()}
                del repeated, identity
            for name in rows:
                model.model.layers[layer].mlp = banks[name]
                p = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
                sums = metrics(q, p, batch[:, 1:]).double().sum(1).cpu().numpy()
                rows[name].extend({**meta, "tokens": 512, **dict(zip(names, values.tolist()))} for meta, values in zip(metadata, sums))
                del p
            del q
    finally:
        model.model.layers[layer].mlp = original
        if base.sampled_parameter_hash(model, prefix) != frozen:
            raise RuntimeError("Frozen backbone mutated during diagnostic")
        args.raw_dir.mkdir(parents=True, exist_ok=True)
        base.write_json(args.raw_dir / "sequences.json", rows)
    result = {"experiment": "E130", "post_hoc": True, "temperature": 1, "reference_proxy_matches_anchor_tensor_sha256": ANCHOR,
              "readout": "BF16 model logits -> FP32 log_softmax, matching E127; replacement FP32", "proofs": proofs,
              "input_sha256": input_hash.hexdigest(), "held_window_hash": base.digest_json(windows), "frozen_sample_hash": frozen,
              "identity_first_batch_repeat": noise, "raw_sequences": str((args.raw_dir / 'sequences.json').resolve()),
              "source_sha256": {name: base.sha256_file(WB / 'scripts' / name) for name in [Path(__file__).name, 'e130_finalize.py', *endpoint.FROZEN]},
              "comparisons": {}, "seconds": time.monotonic() - started, "torch": torch.__version__,
              "scope": "Conditional file-bootstrap evaluation uncertainty only; no seed CI, scientific gate or U/A claim upgrade."}
    for name, records in rows.items():
        global_metrics = summarize(records)
        result["comparisons"][name] = {"global": global_metrics,
            "sources": {s: summarize([r for r in records if r['source'] == s]) for s in sorted({r['source'] for r in records})},
            "endpoint_nll_difference": {"reference": global_metrics['teacher_nll']['mean'] - expected['reference'],
                                        "comparison": global_metrics['student_nll']['mean'] - expected[name]}}
    base.write_json(args.output, result)
    return result


def args_ids(paths):
    return [name for name in paths if name != "reference"]


def self_test():
    q, p = torch.tensor([.8, .15, .05], dtype=torch.float64).log(), torch.tensor([.1, .3, .6], dtype=torch.float64).log()
    result = metrics(q[None, None], p[None, None], torch.tensor([[1]]))[0, 0].numpy()
    assert np.allclose(result[[0, 4]], [(q.exp() * (q-p)).sum(), (p.exp() * (p-q)).sum()])
    assert result[0] > 0 and result[4] > 0 and result[0] != result[4] and result[5] == 0
    assert np.isclose(result[3], -np.log(.3) + np.log(.15))
    identity = metrics(q[None, None], q[None, None], torch.tensor([[1]]))[0, 0]
    assert identity[0] == identity[4] == identity[3] == 0 and identity[5] == 1
    return {"passed": True, "known_distribution_forward_reverse_kl": result[[0, 4]].tolist(), "target_alignment": "checked target index1"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("evaluate", "self-test"), default="evaluate")
    parser.add_argument("--reference"); parser.add_argument("--compare", action="append", default=[])
    parser.add_argument("--model"); parser.add_argument("--data"); parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--max-seconds", type=float, default=720.)
    parser.add_argument("--output", type=Path, default=WB / "results/e130/predictor_comparison.json")
    parser.add_argument("--raw-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e130_predictor_compare"))
    args = parser.parse_args()
    if args.mode == "evaluate" and (not args.reference or not args.compare):
        parser.error("evaluate requires --reference and at least one --compare ID=checkpoint")
    print(json.dumps(self_test() if args.mode == "self-test" else evaluate(args), allow_nan=False))
