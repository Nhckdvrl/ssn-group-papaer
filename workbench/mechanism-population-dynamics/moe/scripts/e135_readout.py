"""Fixed E135 native function/whole-predictor/U-A readouts plus final necessity.

One native teacher and one seed1 student; continuous remaining discrepancies
are reported, not converted into function-equivalence or freedom thresholds.
"""
from __future__ import annotations
import argparse, gc, json
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoeForCausalLM
import e124_compare as matching
import e131_predictor_compare as pred
import e132_bank_grafting as scoring
import e134_uniform_necessity as necessity
import e135_common as c
import e135_capture as functions

assets, base, WB = c.assets, c.base, c.WB
COMMON_SHA = "2a84af164ad55853f171effd345c2719c760219119b9200e8cb47768d435a989"
TRAIN_SHA = "8343f7e87b7ec8a1e027d3ec83bb3d2d7bfd649424a453ba9cc3e53ae3368cb7"
PREDICTOR_SHA = "ff594800990f15389250869704840602e806240058c29eeda9ded9f59dde5c14"
NECESSITY_SHA = "b5e7e55d39142f69ff0c3ce145eaf725d25323fc4a6c7d19f4519fca1a8da177"
CONDITIONS = ("teacher", "copy", "initial", "final")


def condition_states(args, manifest):
    teacher_path = args.cache_root / "teacher_block.pt"
    teacher = torch.load(teacher_path, map_location="cpu", mmap=True, weights_only=False)
    if c.tensor_state_hash(teacher["state"]) != manifest["teacher_block_tensor_sha256"]: raise ValueError("Native teacher block proof differs")
    states = {"teacher": teacher["state"], "copy": {key: value.float() for key, value in teacher["state"].items()}}
    proofs = {name: {"condition": name, "teacher_block_tensor_sha256": manifest["teacher_block_tensor_sha256"],
        "teacher_file_sha256": assets.sha(teacher_path), "storage": "bfloat16" if name == "teacher" else "float32 exact BF16-copy values"} for name in states}
    for name, step, path in (("initial", 0, args.student_dir / "initial.pt"), ("final", 4096, args.student_dir / "checkpoint.pt")):
        checkpoint = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
        if (checkpoint.get("experiment") != "E135" or checkpoint.get("schema") != "E135-student-v1" or checkpoint.get("step") != step
                or checkpoint.get("cache_manifest_sha256") != assets.sha(args.cache_root / "manifest.json")
                or checkpoint.get("teacher_block_tensor_sha256") != manifest["teacher_block_tensor_sha256"]): raise ValueError(f"Wrong {name} fixed student state")
        if any(value.dtype != torch.float32 for value in checkpoint["student_state"].values()): raise ValueError("Student master parameters must remain FP32")
        provenance = assets.read(args.student_dir / "provenance.json")
        if provenance["config_hash"] != checkpoint["config_hash"] or provenance["scientific"]["driver_sha256"] != TRAIN_SHA: raise ValueError("Student training source/config differs")
        if step == 4096:
            summary = assets.read(args.student_dir / "training_summary.json")
            if summary.get("status") != "complete" or summary.get("step") != 4096 or not np.array_equal(checkpoint["cache_batch_counts"], np.full(1024, 4)):
                raise ValueError("Final readout requires complete4096/four-pass endpoint, never best intermediate")
        digest = c.tensor_state_hash(checkpoint["student_state"])
        if step == 0 and digest != checkpoint["initial_tensor_sha256"]: raise ValueError("Initial student full tensor hash differs")
        states[name] = checkpoint["student_state"]
        proofs[name] = {"condition": name, "step": step, "checkpoint": str(path), "checkpoint_sha256": assets.sha(path),
            "tensor_sha256": digest, "initial_tensor_sha256": checkpoint["initial_tensor_sha256"], "config_hash": checkpoint["config_hash"], "storage": "float32"}
    return states, proofs


@torch.no_grad()
def held_function_mse(bank, manifest, args, budget):
    arrays = {key: np.load(args.cache_root / f"held_{key}.npy", mmap_mode="r", allow_pickle=False) for key in ("H", "Y")}
    rows = []; bank.inner.measurement = {}
    for index in range(32):
        budget.check(); hidden, target = c.from_bits(arrays["H"][index], "cuda:0"), c.from_bits(arrays["Y"][index], "cuda:0")
        with torch.autocast("cuda", dtype=torch.bfloat16): output = bank(hidden)[0]
        delta = output.float() - target.float()
        if not torch.isfinite(delta).all(): raise RuntimeError("Nonfinite held block-function discrepancy")
        rows.extend(delta.double().square().mean(-1).sum(-1).cpu().tolist())
    mse = float(np.sum(rows) / 262144)
    return {"positions": 262144, "MSE": mse, "normalized_by_fixed_training_energy": mse / manifest["splits"]["train"]["energy_mean"],
        "relative_to_held_teacher_energy": mse / manifest["splits"]["held"]["energy_mean"], "sequence_MSE_sums_per_position": rows}


@torch.no_grad()
def natural_predictions(model, original, banks, data, windows, items, metadata, args, budget):
    names = pred.NAMES; dolma, pos = {name: [] for name in banks}, {name: [] for name in banks}
    dtype = argparse.Namespace(device="cuda:0", dtype="bfloat16"); noise = {}; chain = __import__("hashlib").sha256()
    for index, (batch, info) in enumerate(data.iter_fixed("held", windows, 16)):
        budget.check(); chain.update(batch.numpy().astype("<i8", copy=False).tobytes()); batch = batch.to("cuda:0"); target = batch[:, 1:]
        model.model.layers[9].mlp = original
        q = base.forward_logits(model, batch[:, :-1], dtype).float().log_softmax(-1)
        if index == 0:
            repeated = base.forward_logits(model, batch[:, :-1], dtype).float().log_softmax(-1)
            noise["Dolma_teacher_repeat"] = pred.repeat_noise(q, repeated, target); del repeated
        for name, bank in banks.items():
            bank.inner.measurement = {}; model.model.layers[9].mlp = original if name == "teacher" else bank
            p = q if name == "teacher" else base.forward_logits(model, batch[:, :-1], dtype).float().log_softmax(-1)
            values = pred.previous.metrics(q, p, target)
            if not torch.isfinite(values).all(): raise RuntimeError(f"Nonfinite natural prediction: {name}")
            sums = values.double().sum(1).cpu().numpy()
            dolma[name].extend({**meta, "tokens": 512, **dict(zip(names, row.tolist()))} for meta, row in zip(info, sums))
            if name != "teacher": del p
        del q
    weight = model.lm_head.weight.detach().float(); bias = model.lm_head.bias.detach().float() if model.lm_head.bias is not None else None
    args.raw_output.mkdir(parents=True, exist_ok=True)
    logps = {name: np.lib.format.open_memmap(args.raw_output / f"{name}_POS_logp.npy", mode="w+", dtype=np.float32, shape=(512, weight.shape[0])) for name in banks}
    held_items, held_meta = zip(*[(item, meta) for item, meta in zip(items, metadata) if meta["split"] == "held"])
    if len(held_items) != 512: raise ValueError("Exact plan-held POS512 required")
    for start, ids, mask, last, target in functions.protocol.batches(held_items, 16, "cuda:0", model.config.pad_token_id or 1):
        budget.check(); model.model.layers[9].mlp = original
        q = pred.pos_logp(model, ids, mask, last, dtype, weight, bias)
        if start == 0:
            repeated = pred.pos_logp(model, ids, mask, last, dtype, weight, bias)
            noise["POS_teacher_repeat"] = pred.repeat_noise(q, repeated, target); del repeated
        for name, bank in banks.items():
            bank.inner.measurement = {}; model.model.layers[9].mlp = original if name == "teacher" else bank
            p = q if name == "teacher" else pred.pos_logp(model, ids, mask, last, dtype, weight, bias)
            logps[name][start:start + len(ids)] = p.cpu().numpy()
            values = pred.previous.metrics(q, p, target).double().cpu().numpy()
            if not np.isfinite(values).all(): raise RuntimeError("Nonfinite full-POS predictor metrics")
            pos[name].extend({**meta, "tokens": 1, "last": int(last[i]), "target": int(target[i]), **dict(zip(names, row.tolist()))}
                for i, (meta, row) in enumerate(zip(held_meta[start:start + len(ids)], values)))
            if name != "teacher": del p
        del q
    for value in logps.values(): value.flush()
    raw = args.raw_output / "natural_predictor_rows.json"; assets.write(raw, {"Dolma": dolma, "POS": pos})
    result = {name: {"Dolma": {"global": pred.previous.summarize(dolma[name]), "sources": {
        source: pred.previous.summarize([row for row in dolma[name] if row["source"] == source]) for source in sorted({row["source"] for row in dolma[name]})}},
        "POS_held": {"global": pred.word_summary(pos[name]), "precision": "BF16 backbone, genuine FP32 selected-last-hidden vocabulary head"}} for name in banks}
    model.model.layers[9].mlp = original
    return {"conditions": result, "identity_noise": noise, "Dolma_input_sha256": chain.hexdigest(), "raw": str(raw), "raw_sha256": assets.sha(raw),
        "POS_full_distributions": {name: {"path": str(args.raw_output / f"{name}_POS_logp.npy"), "sha256": assets.sha(args.raw_output / f"{name}_POS_logp.npy")} for name in banks},
        "scope": "q=public teacher; p=each condition; NLL gap=p minus q. File/word intervals are conditional evaluation uncertainty, not one-student population inference"}


@torch.no_grad()
def final_necessity(model, original, bank, data, windows, manifest, args, budget):
    modes = ("native", "c", "r", "zero", "recompose"); native_block = bank.block
    wrapper = necessity.UniformDecomposition(native_block); model.model.layers[9].mlp = wrapper
    raw = {mode: [] for mode in modes}; dtype = argparse.Namespace(device="cuda:0", dtype="bfloat16"); floor = None; chain = __import__("hashlib").sha256()
    for index, (batch, metadata) in enumerate(data.iter_fixed("held", windows, 16)):
        budget.check(); chain.update(batch.numpy().astype("<i8", copy=False).tobytes()); batch = batch.to("cuda:0"); target = batch[:, 1:]
        wrapper.begin_batch(index); wrapper.mode = "native"
        q = base.forward_logits(model, batch[:, :-1], dtype).float().log_softmax(-1)
        raw["native"].extend(scoring.rows_from_logps(q, q, target, metadata))
        if index == 0:
            model.model.layers[9].mlp = native_block
            unwrapped = base.forward_logits(model, batch[:, :-1], dtype).float().log_softmax(-1)
            floor = necessity.floor_record(unwrapped, q, target, metadata); del unwrapped; model.model.layers[9].mlp = wrapper
        for mode in modes[1:]:
            wrapper.mode = mode; p = base.forward_logits(model, batch[:, :-1], dtype).float().log_softmax(-1)
            raw[mode].extend(scoring.rows_from_logps(q, p, target, metadata)); del p
        wrapper.clear(); del q
    model.model.layers[9].mlp = original
    reference_path = WB / "results/e134/necessity.json"; teacher = assets.read(reference_path)
    teacher_row = teacher["settings"]["public_olmoe_main"]
    expected_shards = {name: value["sha256"] for name, value in manifest["prepare_proof"]["assets"]["assets"].items() if name.endswith(".safetensors")}
    if (teacher.get("script_sha256") != NECESSITY_SHA or teacher_row["status"] != "complete"
            or teacher_row["source_proof"]["weight_shards_verified"] != expected_shards
            or teacher_row["original_block_state_hash"] != manifest["teacher_block_tensor_sha256"]
            or teacher_row["native_prefix_hash"] != manifest["teacher_prefix_hash"] or teacher_row["held_window_hash"] != base.digest_json(windows)
            or teacher_row["input_sha256"] != chain.hexdigest()): raise ValueError("E134 teacher intervention baseline pin/input/precision differs")
    path = args.raw_output / "final_student_necessity_rows.json"; assets.write(path, raw)
    return {"conditions": {mode: scoring.summaries(raw[mode]) for mode in modes}, "native_wrapper_first_batch_floor": floor,
        "teacher_reference": {"path": str(reference_path), "sha256": assets.sha(reference_path), "conditions": {mode: teacher_row["conditions"][mode] for mode in modes}},
        "operator_sha256": NECESSITY_SHA, "input_sha256": chain.hexdigest(), "raw": str(path), "raw_sha256": assets.sha(path),
        "scope": "Prospective five-condition supplement, no gamma; helper teacher_nll/KL reference is FINAL STUDENT native here. Different model-specific uniform references/off-support outputs and remaining natural error prevent strict-equivalence claims"}


def preflight(args):
    if assets.sha(WB / "scripts/e135_common.py") != COMMON_SHA or assets.sha(WB / "scripts/e135_train.py") != TRAIN_SHA: raise ValueError("Frozen cache/training helper differs")
    if assets.sha(WB / "scripts/e131_predictor_compare.py") != PREDICTOR_SHA or assets.sha(WB / "scripts/e134_uniform_necessity.py") != NECESSITY_SHA: raise ValueError("Frozen readout/intervention helper differs")
    if assets.sha(WB / "scripts/e124_compare.py") != scoring.COMPARE_SHA: raise ValueError("Frozen function matching differs")
    c.source_proof(); manifest = c.cache_manifest(args.cache_root)
    states, proofs = condition_states(args, manifest)
    plan, items, metadata = functions.protocol.load_plan(args.plan)
    if assets.sha(args.plan) != assets.PLAN_SHA or len(items) != 1024 or sum(meta["split"] == "held" for meta in metadata) != 512: raise ValueError("Exact E124 population required")
    return manifest, states, proofs, items, metadata


@torch.no_grad()
def run(args):
    manifest, states, proofs, items, metadata = preflight(args)
    gpu = c.select_gpu(args.physical_gpu); args.raw_output.mkdir(parents=True, exist_ok=True)
    with c.Budget(Path(manifest["budget_file"]), "fixed_readouts") as budget:
        model = OlmoeForCausalLM.from_pretrained(manifest["model"], dtype=torch.bfloat16, local_files_only=True,
            attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False); model.config.use_cache = False
        original = model.model.layers[9].mlp; original_hash = c.tensor_state_hash(original.state_dict())
        if original_hash != manifest["teacher_block_tensor_sha256"] or base.sampled_parameter_hash(model, "model.layers.9.mlp.") != manifest["teacher_prefix_hash"]:
            raise ValueError("Runtime native teacher differs from function-cache teacher")
        banks = {name: functions.MeasuredPublic(state) for name, state in states.items()}; states.clear()
        before = {name: c.tensor_state_hash(bank.inner.state_dict()) for name, bank in banks.items()}
        data = base.TokenData(manifest["data"], 512); windows = data.fixed_windows("held", 512, 91023)
        if base.digest_json(windows) != manifest["held_window_hash"]: raise ValueError("Held window identity differs")
        result = {"experiment": "E135", "status": "partial", "source_sha256": {"readout": assets.sha(__file__),
            "capture": assets.sha(WB / "scripts/e135_capture.py"), "common": COMMON_SHA, "train": TRAIN_SHA,
            "predictor": PREDICTOR_SHA, "necessity": NECESSITY_SHA, "compare": scoring.COMPARE_SHA},
            "gpu_preflight": gpu, "cache_manifest_sha256": assets.sha(args.cache_root / "manifest.json"), "condition_proofs": proofs,
            "scope": __doc__, "errors": {}}
        def save(): assets.write(args.summary, result)
        for name, bank in banks.items():
            try: result.setdefault("held_function", {})[name] = held_function_mse(bank, manifest, args, budget)
            except Exception as error: result["errors"]["held_function_" + name] = f"{type(error).__name__}: {error}"
            save()
        try:
            result["natural_predictors"] = natural_predictions(model, original, banks, data, windows, items, metadata, args, budget)
            save()
        except Exception as error: result["errors"]["natural_predictors"] = f"{type(error).__name__}: {error}"; model.model.layers[9].mlp = original
        paths = {}
        for name, bank in banks.items():
            try:
                path, summary = functions.capture(model, original, bank, name, proofs[name], manifest, args, budget)
                paths[name] = path; result.setdefault("functional_arrays", {})[name] = summary
            except Exception as error: result["errors"]["functional_" + name] = f"{type(error).__name__}: {error}"; model.model.layers[9].mlp = original
            save()
        for name in ("copy", "initial", "final"):
            try:
                a, b = matching.load_capture(paths["teacher"]), matching.load_capture(paths[name])
                value = matching.compare(a, b, permutations=199, random_maps=199, seed=124, min_std=1e-8)
                value.update({"experiment": "E135", "reference": "teacher", "comparison": name,
                    "background_kind": "native_public_teacher", "capture_A_sha256": assets.sha(paths["teacher"]), "capture_B_sha256": assets.sha(paths[name]),
                    "interpretation": "U is signed action in the common native-public teacher background; A includes each condition's natural route availability/weights and other-position background. Scalar fingerprint correspondence does not establish equal effects or strict function equivalence.",
                    "scope": "Single student's fixed function constraint; cal-U fit only, held U/A validation; no same-function threshold or extra seed replication"})
                path = WB / "results/e135/comparison" / f"teacher_to_{name}.json"; assets.write(path, value)
                result.setdefault("function_matching", {})[name] = {"path": str(path), "sha256": assets.sha(path), "function": value["function"], "coverage": value["coverage"]}
            except Exception as error: result["errors"]["matching_" + name] = f"{type(error).__name__}: {error}"
            save()
        try: result["final_student_necessity"] = final_necessity(model, original, banks["final"], data, windows, manifest, args, budget)
        except Exception as error: result["errors"]["final_student_necessity"] = f"{type(error).__name__}: {error}"; model.model.layers[9].mlp = original
        if c.tensor_state_hash(original.state_dict()) != original_hash or base.sampled_parameter_hash(model, "model.layers.9.mlp.") != manifest["teacher_prefix_hash"]:
            raise RuntimeError("Native teacher/prefix parameters changed")
        if any(c.tensor_state_hash(bank.inner.state_dict()) != before[name] for name, bank in banks.items()): raise RuntimeError("Read-only condition parameters changed")
        result["status"] = "complete" if not result["errors"] else "partial"; save()
    return result


def self_test():
    result = functions.self_test()
    assert assets.sha(WB / "scripts/e134_uniform_necessity.py") == NECESSITY_SHA
    result.update({"readout_sha256": assets.sha(__file__), "common_sha256": COMMON_SHA, "train_sha256": TRAIN_SHA,
                   "five_final_interventions_no_gamma": ["native", "c", "r", "zero", "recompose"]})
    assets.write(WB / "results/e135/readout_self_test.json", result); return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--mode", choices=("preflight", "evaluate", "self-test"), default="preflight")
    parser.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    parser.add_argument("--student-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student"))
    parser.add_argument("--plan", type=Path, default=WB / "results/e124/plan.json")
    parser.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_readout"))
    parser.add_argument("--summary", type=Path, default=WB / "results/e135/readout.json"); parser.add_argument("--physical-gpu", type=int, default=0)
    args = parser.parse_args()
    if args.mode == "self-test": result = self_test()
    elif args.mode == "preflight":
        manifest, states, proofs, items, metadata = preflight(args)
        result = {"status": "CPU_preflight_only", "conditions": proofs, "items": len(items), "held_items": sum(row["split"] == "held" for row in metadata),
                  "cache_manifest_sha256": assets.sha(args.cache_root / "manifest.json"), "readout_sha256": assets.sha(__file__)}
    else: result = run(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
