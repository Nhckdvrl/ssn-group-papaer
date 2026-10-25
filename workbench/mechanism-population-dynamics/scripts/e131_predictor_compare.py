"""Registered E131 predictor diagnostic at5120/24576/62500; natural models only.

q=ordered, p=permuted. Dolma uses BF16 logits then FP32 logsoftmax; the
fixed plan-held POS group uses a genuine FP32 last-hidden vocabulary head.
"""
from __future__ import annotations
import argparse, contextlib, gc, hashlib, json, os, time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
from torch.nn import functional as F
from transformers import OlmoForCausalLM
import e123_frozen_moe as base
import e124_functional_capture as functional
import e130_predictor_compare as previous
import e131_finalize as endpoint

WB, assets = endpoint.WB, endpoint.tools
NAMES = (*previous.fidelity.METRICS, *previous.EXTRA)
STEPS = (5120, 24576, 62500)
PREDICTOR_SHA = "886cebfc51521fb8873a12aa4ee8db38838c20ba712c9c7dbb75ffd8ac4ea9a4"
FINALIZER_SHA = "8d545eae5f01190e1fea8f7d4382b02d8cb897754db2cc62132bbf887bd99c57"


def source_checks():
    frozen = {**assets.FROZEN, "e130_predictor_compare.py": PREDICTOR_SHA,
              "e130_finalize.py": endpoint.HELPER_SHA, "e131_order_history.py": endpoint.DRIVER_SHA, "e131_finalize.py": FINALIZER_SHA}
    if {name: assets.sha(WB / "scripts" / name) for name in frozen} != frozen: raise ValueError("Frozen diagnostic/training sources differ")
    return frozen


def locations(folder, step):
    checkpoint = folder / ("checkpoint.pt" if step == 62500 else ("snapshots/step005120.pt" if step == 5120 else "snapshots/diagnostic_step024576.pt"))
    capture = folder / ("functional_final.npz" if step == 62500 else ("pulse_function.npz" if step == 5120 else "diagnostic_common24576.npz"))
    return checkpoint, capture


def held_plan(path):
    if assets.sha(path) != assets.PLAN_SHA: raise ValueError("E124 fixed sample-plan SHA differs")
    plan, items, metadata = functional.load_plan(path)
    chosen = [(item, row) for item, row in zip(items, metadata) if row["split"] == "held"]
    if len(chosen) != 512: raise ValueError("Require exactly the plan-held512 POS population")
    items, metadata = map(list, zip(*chosen))
    signature = [{**row, "ids": item["ids"], "last": len(item["ids"]) - 1, "target": item["next_id"]} for item, row in zip(items, metadata)]
    return items, metadata, {"plan_sha256": assets.sha(path), "POS_source_sha256": plan["source_sha256"],
        "all_selected_inputs_sha256": plan["selected_inputs_sha256"], "held_input_target_last_sha256": base.digest_json(signature),
        "items": len(items), "words": len({row["word"] for row in metadata})}


def read_run(folder, branch, step, plan_metadata, plan_proof):
    path, capture_path = locations(folder, step)
    provenance, protocol = assets.read(folder / "provenance.json"), assets.read(folder / "driver_protocol.json")
    if (not provenance or provenance != protocol or provenance.get("experiment") != "E131" or provenance.get("cpu_test") is not False
            or provenance["args"].get("driver_sha256") != endpoint.DRIVER_SHA or provenance["args"].get("branch") != branch
            or provenance.get("frozen_sample_hash") != endpoint.FROZEN or provenance.get("initial_tensor_sha256") != endpoint.INITIAL
            or provenance["parent"].get("checkpoint_sha256") != endpoint.PARENT_SHA or provenance["parent"].get("config_hash") != endpoint.PARENT_CONFIG
            or provenance.get("pulse_plan_sha256") != endpoint.PLAN_SHA
            or assets.sha(Path(provenance["args"]["pulse_plan"]) / "manifest.json") != endpoint.PLAN_SHA):
        raise ValueError(f"Invalid E131 parent/protocol provenance: {branch}")
    history = endpoint.checkpoint_metadata(path, provenance, step)
    checkpoint = torch.load(path, map_location="cpu", mmap=True, weights_only=False); state = checkpoint["replacement_state"]
    if any(value.dtype != torch.float32 for value in state.values()): raise ValueError("Replacement parameters must remain FP32")
    tensor_hash = functional.tensor_state_hash(state)
    with np.load(capture_path, allow_pickle=False) as capture:
        header = json.loads(str(capture["metadata_json"])); held = capture["split"] == "held"
        expected = {"step": step, "seed": 0, "order_seed": 0, "layer": 9, "experts": 64, "top_k": 8,
            "checkpoint_config_hash": provenance["config_hash"], "checkpoint_moe_tensor_sha256": tensor_hash,
            "backbone_sample_hash": endpoint.FROZEN, "plan_sha256": plan_proof["plan_sha256"],
            "source_sha256": plan_proof["POS_source_sha256"], "selected_inputs_sha256": plan_proof["all_selected_inputs_sha256"]}
        if any(header.get(key) != value for key, value in expected.items()): raise ValueError("CP and actual functional capture fingerprints differ")
        for key in ("item_id", "input_sha256", "word", "label", "document", "split"):
            if not np.array_equal(capture[key][held], np.array([row[key] for row in plan_metadata])):
                raise ValueError(f"Actual capture POS population/order differs from plan: {key}")
        expected_pos_nll = np.asarray(capture["normal_nll"])[held].astype(float).tolist()
    summary_path = WB / "results/e131/pulse_stage" / branch / "training_summary.json" if step == 5120 else folder / "training_summary.json"
    summary = assets.read(summary_path)
    if not summary or summary.get("config_hash") != provenance["config_hash"]: raise ValueError("Legacy evaluation summary/config differs")
    if step == 62500 and not assets.ready(summary, assets.read(folder / "failure.json")): raise ValueError("62500 scoring requires the completed fixed endpoint")
    evaluations = [row for row in summary["evaluations"] if row["step"] == step]
    if len(evaluations) != 1: raise ValueError(f"Missing/duplicate exact legacy evaluation at{step}")
    legacy = {"source": str(summary_path), "evaluation_step": step, "evaluation_sha256": base.digest_json(evaluations[0]),
              "held_file": evaluations[0]["held"]["file"], "scope": "Exact registered-step event, never the current/latest NLL"}
    proof = {"branch": branch, "step": step, "checkpoint": str(path), "checkpoint_sha256": assets.sha(path),
        "replacement_tensor_sha256": tensor_hash, "config_hash": provenance["config_hash"], "parent": provenance["parent"],
        "provenance_sha256": assets.sha(folder / "provenance.json"), "protocol_sha256": assets.sha(folder / "driver_protocol.json"),
        "functional_capture": str(capture_path), "functional_capture_sha256": assets.sha(capture_path), "history": history, "legacy": legacy}
    return {"state": state, "provenance": provenance, "proof": proof, "expected_POS_nll": expected_pos_nll}


def preflight(args):
    frozen = source_checks(); items, pos_meta, plan_proof = held_plan(args.plan)
    runs = {branch: read_run(getattr(args, branch + "_dir"), branch, args.step, pos_meta, plan_proof) for branch in ("ordered", "permuted")}
    config = runs["ordered"]["provenance"]["args"]
    if any(config[key] != value for key, value in {"layer": 9, "experts": 64, "expert_size": 1024, "top_k": 8,
        "seq_len": 512, "batch_size": 16, "eval_sequences": 512, "dtype": "bfloat16", "seed": 0, "order_seed": 0}.items()):
        raise ValueError("Expected the fixed E131 architecture/evaluation contract")
    data = base.TokenData(config["data"], 512); windows = data.fixed_windows("held", 512, config["eval_seed"])
    for run in runs.values():
        previous.fidelity.guard_inputs(run["provenance"], data, windows)
        if any(run["provenance"]["args"][key] != config[key] for key in ("model", "layer", "experts", "expert_size", "top_k", "dtype")):
            raise ValueError("Branch architecture/model source differs")
    report = {"experiment": "E131", "status": "preflight_only_no_GPU", "step": args.step, "script_sha256": assets.sha(__file__),
        "frozen_sources": frozen, "proofs": {branch: run["proof"] for branch, run in runs.items()}, "POS_plan": plan_proof,
        "Dolma_held_window_hash": base.digest_json(windows), "data_identity_sha256": base.digest_json(data.provenance),
        "common_segment_input_hash_equal": runs["ordered"]["proof"]["history"]["common_input_hash"] == runs["permuted"]["proof"]["history"]["common_input_hash"]}
    return runs, data, windows, items, pos_meta, report


@torch.no_grad()
def pos_logp(model, ids, mask, last, scoring, weight, bias):
    with functional.amp(scoring): hidden = model.model(input_ids=ids, attention_mask=mask, use_cache=False).last_hidden_state
    at_target = hidden[torch.arange(len(ids), device=ids.device), last].float()
    context = torch.autocast("cuda", enabled=False) if scoring.device.startswith("cuda") else contextlib.nullcontext()
    with context: logits = F.linear(at_target, weight, bias)
    return logits.log_softmax(-1)


def word_summary(rows):
    # Same equal-word point estimate and seed51025 bootstrap as E123 pos_summary.
    words = list(dict.fromkeys(row["word"] for row in rows))
    values = np.array([[np.mean([row[key] for row in rows if row["word"] == word]) for key in NAMES] for word in words])
    means = values.mean(0); draws = np.random.default_rng(51025).integers(0, len(words), (1000, len(words)))
    intervals = np.quantile(values[draws].mean(1), [.025, .975], axis=0)
    return {"items": len(rows), "words": len(words), "word_bootstrap_iterations": 1000, "weighting": "equal word means, matching existing POS summary",
            **{key: {"mean": float(means[i]), "ci95": intervals[:, i].tolist()} for i, key in enumerate(NAMES)}}


def repeat_noise(q, repeated, targets):
    values = previous.metrics(q, repeated, targets)
    if not torch.isfinite(values).all(): raise RuntimeError("Nonfinite repeated-distribution metrics")
    return {"forward_KL_max_abs": float(values[..., 0].abs().max()), "reverse_KL_max_abs": float(values[..., 4].abs().max()),
            "NLL_delta_max_abs": float(values[..., 3].abs().max()), "top1_agreement": float(values[..., 5].mean()),
            "log_probability_max_abs": float((q - repeated).abs().max()), "targets": targets.numel()}


@torch.no_grad()
def evaluate(args):
    started = time.monotonic(); runs, data, windows, items, pos_meta, report = preflight(args)
    gpu = assets.gpu_status(args.physical_gpu)
    if not assets.gpu_free(gpu): return {**report, "status": "deferred_gpu_busy_or_unavailable", "gpu_preflight": gpu}
    if torch.cuda.is_initialized(): raise RuntimeError("CUDA initialized before physical GPU preflight")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if visible and visible != str(args.physical_gpu): raise ValueError("Visible/requested physical GPU differ")
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.physical_gpu)
    budget_path = args.raw_dir / "budget.json"; budget = assets.read(budget_path)
    charged = budget.get("seconds", 0.) if budget and budget.get("script_sha256") == report["script_sha256"] else 0.
    def check_budget():
        if charged + time.monotonic() - started >= args.max_seconds: raise TimeoutError("Cumulative 0.5GPUh diagnostic budget exhausted")
    config = runs["ordered"]["provenance"]["args"]; scoring = argparse.Namespace(device="cuda:0", dtype="bfloat16")
    model = OlmoForCausalLM.from_pretrained(config["model"], dtype=torch.bfloat16, local_files_only=True,
        attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False); model.config.use_cache = False
    original = model.model.layers[9].mlp; frozen = base.sampled_parameter_hash(model, "model.layers.9.mlp.")
    if frozen != endpoint.FROZEN: raise ValueError("Loaded frozen backbone differs")
    banks = {}
    for branch, run in runs.items():
        with torch.device("meta"): bank = base.TensorMoE(2048, 1024, 64, 8, .02)
        bank.load_state_dict(run["state"], strict=True, assign=True); banks[branch] = bank.to("cuda:0").eval().requires_grad_(False)
    folder = args.raw_dir / f"step{args.step:06d}"; folder.mkdir(parents=True, exist_ok=True)
    attempt = len(list(folder.glob("attempt*_rows.json"))) + 1; stem = folder / f"attempt{attempt:02d}"
    dolma_rows, pos_rows, noise, errors, files = [], [], {}, {}, {}
    token_path = stem.with_name(stem.name + "_Dolma_token_metrics.npy")
    token_metrics = np.lib.format.open_memmap(token_path, mode="w+", dtype=np.float32, shape=(512, 512, len(NAMES)))
    input_hash, pos_input_hash = hashlib.sha256(), hashlib.sha256()
    try:
        for index, (batch, metadata) in enumerate(data.iter_fixed("held", windows, 16)):
            check_budget(); input_hash.update(batch.numpy().astype("<i8", copy=False).tobytes()); batch = batch.to("cuda:0"); targets = batch[:, 1:]
            distributions = {}
            for branch in ("ordered", "permuted"):
                model.model.layers[9].mlp = banks[branch]
                distributions[branch] = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
                if index == 0:
                    repeated = base.forward_logits(model, batch[:, :-1], scoring).float().log_softmax(-1)
                    noise["Dolma_" + branch] = repeat_noise(distributions[branch], repeated, targets); del repeated
            values = previous.metrics(distributions["ordered"], distributions["permuted"], targets)
            if not torch.isfinite(values).all(): raise RuntimeError("Nonfinite Dolma predictor metrics")
            token_metrics[index * 16:index * 16 + len(batch)] = values.cpu().numpy()
            sums = values.double().sum(1).cpu().numpy()
            dolma_rows.extend({**meta, "tokens": 512, **dict(zip(NAMES, row.tolist()))} for meta, row in zip(metadata, sums))
            del distributions, values
        token_metrics.flush()
    except Exception as error: errors["Dolma"] = f"{type(error).__name__}: {error}"
    head_weight = model.lm_head.weight.detach().float(); head_bias = model.lm_head.bias.detach().float() if model.lm_head.bias is not None else None
    pos_paths = {branch: stem.with_name(stem.name + f"_POS_{branch}_logp.npy") for branch in banks}
    pos_distributions = {branch: np.lib.format.open_memmap(path, mode="w+", dtype=np.float32, shape=(512, head_weight.shape[0])) for branch, path in pos_paths.items()}
    try:
        for start, ids, mask, last, targets in functional.batches(items, 16, "cuda:0", model.config.pad_token_id or 1):
            check_budget()
            for value in (ids, mask, last, targets):
                array = value.cpu().numpy().astype("<i8", copy=False); pos_input_hash.update(str(array.shape).encode() + array.tobytes())
            distributions = {}
            for branch in banks:
                model.model.layers[9].mlp = banks[branch]
                distributions[branch] = pos_logp(model, ids, mask, last, scoring, head_weight, head_bias)
                pos_distributions[branch][start:start + len(ids)] = distributions[branch].cpu().numpy()
                if start == 0:
                    repeated = pos_logp(model, ids, mask, last, scoring, head_weight, head_bias)
                    noise["POS_" + branch] = repeat_noise(distributions[branch], repeated, targets); del repeated
            values = previous.metrics(distributions["ordered"], distributions["permuted"], targets).double().cpu().numpy()
            if not np.isfinite(values).all(): raise RuntimeError("Nonfinite POS predictor metrics")
            pos_rows.extend({**meta, "last": int(last[i]), "target": int(targets[i]), "tokens": 1, **dict(zip(NAMES, row.tolist()))}
                            for i, (meta, row) in enumerate(zip(pos_meta[start:start + len(ids)], values)))
            del distributions
        for value in pos_distributions.values(): value.flush()
    except Exception as error: errors["POS"] = f"{type(error).__name__}: {error}"
    model.model.layers[9].mlp = original
    if base.sampled_parameter_hash(model, "model.layers.9.mlp.") != frozen: raise RuntimeError("Frozen backbone mutated")
    for branch, bank in banks.items():
        if functional.tensor_state_hash(bank.state_dict()) != runs[branch]["proof"]["replacement_tensor_sha256"]: raise RuntimeError("Source replacement mutated")
    raw_path = stem.with_name(stem.name + "_rows.json")
    assets.write(raw_path, {"Dolma": dolma_rows, "POS": pos_rows, "POS_inputs": [{**meta, "ids": item["ids"], "last": len(item["ids"]) - 1, "target": item["next_id"]} for item, meta in zip(items, pos_meta)]})
    for name, path, valid in (("rows", raw_path, len(dolma_rows)), ("Dolma_token_metrics", token_path, len(dolma_rows)),
                              *[("POS_" + branch, path, len(pos_rows)) for branch, path in pos_paths.items()]):
        files[name] = {"path": str(path), "sha256": assets.sha(path), "valid_rows": valid}
    result = {**report, "status": "complete" if len(dolma_rows) == len(pos_rows) == 512 and not errors else "partial",
        "post_hoc_registered_before_scoring": True, "direction": "q=ordered, p=permuted; nll_gap=NLL(p)-NLL(q)",
        "gpu_preflight": gpu, "identity_first_batch_repeats": noise, "errors": errors, "raw": files, "groups": {},
        "scope": "Two natural prediction populations/precision paths, reported separately; no U/A interventions, mapping, same-function claim or scientific threshold"}
    if len(dolma_rows) == 512:
        value = previous.summarize(dolma_rows)
        result["groups"]["Dolma"] = {"precision": "BF16 logits -> FP32 logsoftmax", "input_sha256": input_hash.hexdigest(), "global": value,
            "sources": {source: previous.summarize([row for row in dolma_rows if row["source"] == source]) for source in sorted({row["source"] for row in dolma_rows})},
            "legacy_NLL_difference": {"ordered": value["teacher_nll"]["mean"] - runs["ordered"]["proof"]["legacy"]["held_file"]["mean"],
                                      "permuted": value["student_nll"]["mean"] - runs["permuted"]["proof"]["legacy"]["held_file"]["mean"]}}
    if len(pos_rows) == 512:
        result["groups"]["POS_plan_held"] = {"precision": "BF16 backbone -> selected last hidden FP32 -> actual FP32 lm_head/logsoftmax",
            "input_padding_last_target_sha256": pos_input_hash.hexdigest(), "global": word_summary(pos_rows),
            "captured_natural_NLL_max_abs_difference": {branch: float(np.max(np.abs(np.array([row["teacher_nll" if branch == "ordered" else "student_nll"] for row in pos_rows]) - run["expected_POS_nll"]))) for branch, run in runs.items()}}
    elapsed = time.monotonic() - started; result["seconds_this_step"] = elapsed; result["cumulative_seconds"] = charged + elapsed
    assets.write(budget_path, {"script_sha256": report["script_sha256"], "seconds": charged + elapsed})
    del model, banks, head_weight, pos_distributions, token_metrics; gc.collect(); torch.cuda.empty_cache()
    return result


def self_test():
    previous.self_test(); torch.manual_seed(131)
    class Backbone(torch.nn.Module):
        def __init__(self): super().__init__(); self.register_buffer("table", torch.randn(16, 4).bfloat16())
        def forward(self, input_ids, attention_mask, use_cache): return SimpleNamespace(last_hidden_state=self.table[input_ids])
    model = SimpleNamespace(model=Backbone()); weight = torch.randn(16, 4).bfloat16().float()
    items = [{"ids": [3, 5], "next_id": 11}, {"ids": [7], "next_id": 12}, {"ids": [4, 6, 8], "next_id": 13}]
    _, ids, mask, last, target = next(functional.batches(items, 3, "cpu", 1))
    assert last.tolist() == [1, 0, 2] and target.tolist() == [11, 12, 13] and ids.tolist() == [[3, 5, 1], [7, 1, 1], [4, 6, 8]]
    got = pos_logp(model, ids, mask, last, SimpleNamespace(device="cpu", dtype="float32"), weight, None)
    hidden = model.model.table[ids][torch.arange(3), last]
    expected = F.linear(hidden.float(), weight).log_softmax(-1)
    rounded = F.linear(hidden, weight.bfloat16()).float().log_softmax(-1)
    assert torch.equal(got, expected) and not torch.equal(got, rounded)
    assert set(STEPS) == {5120, 24576, 62500}
    rows = [{"word": word, **{key: value for key in NAMES}} for word, value in (("a", 1.), ("a", 1.), ("b", 3.))]
    assert word_summary(rows)[NAMES[0]]["mean"] == 2.
    items_real, metadata_real, proof = held_plan(WB / "results/e124/plan.json")
    assert len(items_real) == len(metadata_real) == proof["items"] == 512 and all(row["split"] == "held" for row in metadata_real)
    return {"passed": True, "CPU_only": True, "true_FP32_head_not_cast_BF16_logits": True, "exact_last_target_padding_contract": True,
            "POS_exact_plan_held512": proof, "bidirectional_metrics_known_answer": True, "word_bootstrap_equal_word_means": True,
            "script_sha256": assets.sha(__file__), "frozen_sources": source_checks()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--mode", choices=("preflight", "evaluate", "self-test"), default="evaluate")
    parser.add_argument("--step", type=int, choices=STEPS); parser.add_argument("--ordered-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e131_ordered"))
    parser.add_argument("--permuted-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e131_permuted"))
    parser.add_argument("--plan", type=Path, default=WB / "results/e124/plan.json")
    parser.add_argument("--raw-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e131_predictor_compare"))
    parser.add_argument("--summary-dir", type=Path, default=WB / "results/e131/predictor_comparison")
    parser.add_argument("--physical-gpu", type=int, default=3); parser.add_argument("--max-seconds", type=float, default=1800.)
    args = parser.parse_args()
    if args.mode == "self-test":
        result = self_test(); assets.write(args.summary_dir / "self_test.json", result)
    else:
        if args.step is None or not 0 < args.max_seconds <= 1800: parser.error("Specify registered step and cumulative budget<=1800s")
        if args.raw_dir.resolve().is_relative_to(WB): parser.error("Raw arrays must be outside git")
        result = preflight(args)[-1] if args.mode == "preflight" else evaluate(args)
        suffix = "_preflight" if args.mode == "preflight" else ""
        assets.write(args.summary_dir / f"step{args.step:06d}{suffix}.json", result)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
