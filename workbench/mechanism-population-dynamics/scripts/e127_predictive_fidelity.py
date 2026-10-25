"""E127: fixed-endpoint KL(dense teacher || student), temperature 1; no training.
BF16 full-model logits -> FP32 log_softmax, matching E125 scoring precision.
Only replacement weights leave a CPU-mmap checkpoint; optimizer is never moved.
"""
import argparse
import hashlib
import json
import tempfile
import time
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoConfig, OlmoForCausalLM
from transformers.models.olmo.modeling_olmo import OlmoMLP
import e123_frozen_moe as base
from e124_functional_capture import tensor_state_hash

WB = Path(__file__).resolve().parents[1]
METRICS = ("kl_teacher_to_student", "teacher_nll", "student_nll", "nll_gap")


def guard_step(step, expected, reference):
    if expected != 15625 and not (reference and expected == 3906):
        raise ValueError("Only fixed step15625, or explicit reference-calibration step3906, is allowed")
    if step != expected:
        raise ValueError(f"Checkpoint step {step} differs from required fixed endpoint {expected}")


def guard_inputs(provenance, data, windows):
    identity = lambda rows: [(r["source"], r["file_id"], r["sha256"], r["windows"], r["dtype"]) for r in rows]
    if identity(provenance["data"]["held"]) != identity(data.provenance["held"]):
        raise ValueError("Held file content/identity differs from training evaluation")
    if provenance["held_window_hash"] != base.digest_json(windows):
        raise ValueError("Fixed held windows differ from training evaluation")


def token_metrics(teacher, student, targets):
    kl = (teacher.exp() * (teacher - student)).sum(-1)
    teacher_nll = -teacher.gather(-1, targets[..., None])[..., 0]
    student_nll = -student.gather(-1, targets[..., None])[..., 0]
    return torch.stack((kl, teacher_nll, student_nll, student_nll - teacher_nll), -1)


def summarize(rows, iterations=1000):
    groups = {}
    for row in rows:
        key = (row["source"], row["file_id"])
        groups.setdefault(key, np.zeros(5))[:] += np.array([row[k] for k in METRICS] + [row["tokens"]])
    values = np.array(list(groups.values()))
    draws = np.random.default_rng(127).integers(0, len(values), (iterations, len(values)))
    samples = values[draws].sum(1)
    intervals = np.quantile(samples[:, :4] / samples[:, 4:], [.025, .05, .95, .975], axis=0)
    totals = values.sum(0)
    return {"files": len(values), "tokens": int(totals[4]), "file_bootstrap_iterations": iterations,
            "ci_degenerate": len(values) < 2,
            **{key: {"mean": float(totals[i] / totals[4]), "ci90": intervals[[1, 2], i].tolist(),
                     "ci95": intervals[[0, 3], i].tolist()} for i, key in enumerate(METRICS)}}


@torch.no_grad()
def evaluate(args):
    started = time.monotonic()
    checkpoint_path = Path(args.checkpoint).resolve()
    provenance_path = checkpoint_path.parent / "provenance.json"
    provenance = json.loads(provenance_path.read_text())
    config = provenance["args"]
    checkpoint = torch.load(checkpoint_path, map_location="cpu", mmap=True, weights_only=False)
    guard_step(int(checkpoint["step"]), args.expected_step, args.reference_calibration)
    resolve = lambda p: Path(p) if Path(p).is_absolute() else WB / p
    data = base.TokenData(resolve(args.data or config["data"]), config["seq_len"])
    windows = data.fixed_windows("held", config["eval_sequences"], config["eval_seed"])
    guard_inputs(provenance, data, windows)
    scoring = argparse.Namespace(device=args.device, dtype=config["dtype"])
    if args.device == "cpu" and scoring.dtype != "float32":
        raise ValueError("CPU self-test requires float32 checkpoint scoring")
    model = OlmoForCausalLM.from_pretrained(resolve(args.model or config["model"]), local_files_only=True,
                dtype=getattr(torch, scoring.dtype), attn_implementation="sdpa").to(args.device).eval()
    model.requires_grad_(False)
    layer = config["layer"]
    original = model.model.layers[layer].mlp
    prefix = f"model.layers.{layer}.mlp."
    frozen_hash = base.sampled_parameter_hash(model, prefix)
    if checkpoint["frozen_sample_hash"] != frozen_hash:
        raise ValueError("Frozen backbone fingerprint differs from checkpoint")
    kind = checkpoint.get("replacement_kind", config.get("replacement", "moe"))
    replacement = (OlmoMLP(model.config) if kind == "dense" else base.TensorMoE(model.config.hidden_size,
                   config["expert_size"], config["experts"], config["top_k"], config.get("init_std", .02)))
    state = checkpoint["replacement_state"] if "replacement_state" in checkpoint else checkpoint["moe"]
    parameter_hash = tensor_state_hash(state)
    replacement.load_state_dict(state, strict=True)
    replacement = replacement.to(args.device).eval()
    replacement.requires_grad_(False)
    del checkpoint, state
    rows, input_hash, noise = [], hashlib.sha256(), {"teacher_repeat_kl_max_abs": 0., "student_repeat_kl_max_abs": 0.}
    for batch_index, (batch, metadata) in enumerate(data.iter_fixed("held", windows, config["batch_size"])):
        input_hash.update(batch.numpy().astype("<i8", copy=False).tobytes())
        batch = batch.to(args.device)
        model.model.layers[layer].mlp = original
        teacher = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
        if batch_index == 0:
            repeated = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
            noise["teacher_repeat_kl_max_abs"] = float(token_metrics(teacher, repeated, batch[:, 1:])[..., 0].abs().max())
            del repeated
        model.model.layers[layer].mlp = replacement
        student = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
        if batch_index == 0:
            repeated = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
            noise["student_repeat_kl_max_abs"] = float(token_metrics(student, repeated, batch[:, 1:])[..., 0].abs().max())
            del repeated
        sums = token_metrics(teacher, student, batch[:, 1:]).double().sum(1).cpu().numpy()
        rows.extend({**meta, "tokens": config["seq_len"], **dict(zip(METRICS, values.tolist()))} for meta, values in zip(metadata, sums))
        del teacher, student
    model.model.layers[layer].mlp = original
    if base.sampled_parameter_hash(model, prefix) != frozen_hash:
        raise RuntimeError("Frozen backbone changed during read-only evaluation")
    result = {"checkpoint": str(checkpoint_path), "step": args.expected_step, "reference_calibration": args.reference_calibration,
              "replacement": kind, "temperature": 1, "dtype": scoring.dtype, "readout": "BF16 logits then FP32 log_softmax; no FP32 lm_head substitution",
              "metrics": summarize(rows, args.bootstrap), "noise": noise,
              "sources": {source: summarize([r for r in rows if r["source"] == source], args.bootstrap)
                          for source in sorted({r["source"] for r in rows})},
              "missing_sources": sorted(set(data.sources_available) - {r["source"] for r in rows}),
              "input_sha256": input_hash.hexdigest(), "held_window_hash": base.digest_json(windows),
              "replacement_tensor_sha256": parameter_hash, "frozen_sample_hash": frozen_hash,
              "provenance_sha256": base.sha256_file(provenance_path), "script_sha256": base.sha256_file(__file__),
              "seconds": time.monotonic() - started, "scope": "fixed held input distribution; supplementary metric, no new recovery gate"}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    base.write_json(output, result)
    base.write_json(output.with_name(output.stem + "_sequences.json"), rows)
    return result


def self_test():
    torch.set_num_threads(1)
    with tempfile.TemporaryDirectory(prefix="e127_cpu_") as directory:
        root = Path(directory)
        torch.manual_seed(127)
        cfg = OlmoConfig(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=2,
                         num_attention_heads=4, num_key_value_heads=4, max_position_embeddings=32, pad_token_id=1)
        model = OlmoForCausalLM(cfg).eval()
        model.save_pretrained(root / "model")
        rng = np.random.default_rng(127)
        for split in ("train", "held"):
            np.save(root / f"{split}.npy", rng.integers(3, 32, 90, dtype=np.uint16))
        data = base.TokenData(root, 8)
        windows = data.fixed_windows("held", 4, 127)
        provenance = {"args": {"model": str(root / "model"), "data": str(root), "seq_len": 8,
                      "eval_sequences": 4, "eval_seed": 127, "batch_size": 2, "dtype": "float32", "layer": 1},
                      "data": data.provenance, "held_window_hash": base.digest_json(windows)}
        base.write_json(root / "provenance.json", provenance)
        torch.save({"step": 15625, "replacement_kind": "dense", "replacement_state": model.model.layers[1].mlp.state_dict(),
                    "frozen_sample_hash": base.sampled_parameter_hash(model, "model.layers.1.mlp."),
                    "optimizer": {"cpu_only_sentinel": torch.ones(2)}}, root / "checkpoint.pt")
        args = argparse.Namespace(checkpoint=str(root / "checkpoint.pt"), model=None, data=None, device="cpu",
                                  output=str(root / "result.json"), expected_step=15625, reference_calibration=False, bootstrap=30)
        result = evaluate(args)
        equal_kl = result["metrics"]["kl_teacher_to_student"]["mean"]
        q = torch.tensor([[[0., 1., 2.]]]).log_softmax(-1)
        p = torch.tensor([[[2., 1., 0.]]]).log_softmax(-1)
        shifted = float(token_metrics(q, p, torch.tensor([[1]]))[0, 0, 0])
        assert equal_kl == 0 and shifted > 0 and result["metrics"]["nll_gap"]["mean"] == 0
        for check in (lambda: guard_step(100, 15625, False), lambda: guard_step(3906, 3906, False),
                      lambda: guard_inputs({**provenance, "held_window_hash": "wrong"}, data, windows),
                      lambda: guard_inputs({**provenance, "data": {"held": []}}, data, windows)):
            try:
                check()
            except ValueError:
                continue
            raise AssertionError("Step/input/hash guard accepted invalid input")
        guard_step(3906, 3906, True)
        summary = {"passed": True, "device": "cpu", "identical_predictions_kl": equal_kl, "shifted_toy_kl": shifted,
                   "noise": result["noise"], "step_input_hash_guards": "passed", "script_sha256": base.sha256_file(__file__)}
        target = WB / "results/e127/self_test.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        base.write_json(target, summary)
        return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("evaluate", "self-test"), required=True)
    for name in ("checkpoint", "model", "data", "output"):
        parser.add_argument("--" + name)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--expected-step", type=int, default=15625)
    parser.add_argument("--reference-calibration", action="store_true")
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()
    if args.mode != "self-test" and not (args.checkpoint and args.output):
        parser.error("evaluate requires --checkpoint and --output")
    print(json.dumps(self_test() if args.mode == "self-test" else evaluate(args), ensure_ascii=False, allow_nan=False))
