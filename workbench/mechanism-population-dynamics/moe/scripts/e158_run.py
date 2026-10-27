"""E158: factual entity/attribute path interchange in fixed mature checkpoints."""
import argparse
import os
_early_parser = argparse.ArgumentParser(add_help=False)
_early_parser.add_argument("--physical-gpu", type=int, default=0)
_early, _ = _early_parser.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_early.physical_gpu)):
    raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
import json
import platform
from pathlib import Path
import numpy as np
import torch
import transformers
import transformers.cache_utils as cache_library
import e156_run as prev
import e158_data as data
import e158_engine as engine
import e158_analyze as analysis

n, loading = prev.n, prev.loading
RESULT = n.WB / "results/e158"
RAW = Path.home() / "mechpop_cache/e158_factual_role_interchange"
SOURCES, SCENARIOS, COMPONENTS = ("P", "A", "B"), ("entity", "attribute", "paraphrase"), ("R", "S", "RS")


def proof():
    return {**prev.proof(), **{f: n.sha(n.WB / "scripts" / f) for f in
            ("e158_data.py", "e158_engine.py", "e158_run.py", "e158_analyze.py")}}


def software():
    return {"python": platform.python_version(), "torch": torch.__version__,
            "transformers": transformers.__version__, "numpy": np.__version__,
            "cache_library": {"path": str(Path(cache_library.__file__).resolve()), "sha256": n.sha(cache_library.__file__)}}


def self_test():
    tests = {"data": data.self_test(), "cached_native_interchange": engine.self_test(), "statistics": analysis.self_test()}
    n.write(RESULT / "self_test.json", {"status": "passed", "CPU_only": True,
            "source_sha256": proof(), "software": software(), "tests": tests})
    return {"status": "passed", "CPU_only": True}


def prepare():
    test = n.read(RESULT / "self_test.json")
    if test["status"] != "passed" or test["source_sha256"] != proof() or test["software"] != software():
        raise ValueError("Matching complete CPU tests required")
    dp = n.read(RESULT / "data_plan.json")
    if dp["data_script_sha256"] != n.sha(data.__file__):
        raise ValueError("Data implementation differs")
    for record in dp["assets"].values():
        if n.sha(record["path"]) != record["sha256"]:
            raise ValueError("Frozen factual inputs differ")
    old_plan = n.read(prev.RESULT / "plan.json")
    old_manifest = n.read(prev.RESULT / "manifest.json")
    if old_manifest["status"] != "complete" or old_manifest["source_sha256"] != prev.proof():
        raise ValueError("Complete canonical reference source required")
    if n.sha(prev.RESULT / "plan.json") != old_manifest["plan_sha256"]:
        raise ValueError("Canonical reference plan differs")
    result = {"experiment": "E158", "status": "prepared", "source_sha256": proof(), "software": software(),
              "data_plan_sha256": n.sha(RESULT / "data_plan.json"), "data": dp["assets"]["data.npz"],
              "input_assets": dp["assets"], "reference_plan_sha256": n.sha(prev.RESULT / "plan.json"),
              "reference_manifest_sha256": n.sha(prev.RESULT / "manifest.json"),
              "source_records": old_plan["source_records"], "legacy_cal_input": old_plan["legacy_cal_input"],
              "source_names": list(SOURCES), "scenario_names": list(SCENARIOS), "component_names": list(COMPONENTS),
              "layers": list(range(16)), "queries": 96, "targets": 48, "patch_rows": 20736,
              "baseline_gate": {"joint_native_top10_minimum_per_relation": 8, "applied_before_patching": True},
              "cache_engineering_floor": {"uncached_to_cached_KL_max": .005, "argmax_disagreement_fraction_max": .05},
              "bootstrap": {"seed": 158001, "resamples": 1000, "unit": "target country; fixed source mapping"},
              "scope": "Within-model factual input interchange, same last input token, all fixed layers and paths, zero training."}
    n.old.immutable_json(RESULT / "plan.json", result)
    return {"status": "prepared", "new_patch_rows": 20736}


class Budget(n.old.Budget):
    def __init__(self):
        self.path, self.experiment, self.phase, self.limit = RESULT / "budget.json", "e158", "factual_cached_interchange", 10800


def top10(lp):
    return lp.topk(10).indices.cpu().numpy()


def immutable_npz(path, values):
    if path.exists():
        with np.load(path, allow_pickle=False) as old:
            if set(old.files) != set(values) or any(not np.array_equal(old[k], v) for k, v in values.items()):
                raise ValueError("Refusing to overwrite different raw: " + str(path))
    else:
        np.savez_compressed(path, **values)


def component_pack(query_sets):
    result = {}
    for name in ("hidden", "routed", "shared"):
        stacked = torch.stack([torch.stack([torch.stack(getattr(q, name)) for q in group]) for group in query_sets])
        # [model,query,layer,1,1,hidden], preserve actual BF16 bits, not a float recast.
        result[name] = stacked.squeeze(3).squeeze(3).contiguous().view(torch.uint16).cpu().numpy()
        del stacked
    result["final_residual"] = torch.stack([torch.stack([q.final_residual for q in group]) for group in query_sets]).squeeze(2).squeeze(2).contiguous().view(torch.uint16).cpu().numpy()
    result["encoding"] = np.array("bfloat16_uint16_bits")
    return result


@torch.no_grad()
def evaluate(physical):
    plan = n.read(RESULT / "plan.json")
    if plan["source_sha256"] != proof() or n.read(RESULT / "self_test.json")["source_sha256"] != proof() or plan["software"] != software():
        raise ValueError("Frozen complete source/software differs")
    if n.sha(RESULT / "data_plan.json") != plan["data_plan_sha256"]:
        raise ValueError("Data plan differs")
    if n.sha(prev.RESULT / "plan.json") != plan["reference_plan_sha256"] or n.sha(prev.RESULT / "manifest.json") != plan["reference_manifest_sha256"]:
        raise ValueError("Canonical source records differ")
    for record in list(plan["input_assets"].values()) + [plan["legacy_cal_input"]]:
        if n.sha(record["path"]) != record["sha256"]:
            raise ValueError("Frozen data/calibration differs")
    final_path = RAW / "scores.npz"
    if final_path.exists() or (RESULT / "manifest.json").exists():
        raise ValueError("Refusing to replace an E158 completed record")
    with np.load(plan["data"]["path"], allow_pickle=False) as f:
        a = {k: f[k].copy() for k in f.files}
    analysis.validate_data(a)
    with np.load(plan["legacy_cal_input"]["path"], allow_pickle=False) as f:
        cal, cv = f["cal"][:2, :129].copy(), f["cal_mask"][:2, :128].copy()
    lock = None
    try:
        with Budget() as budget:
            lock = n.old.gpu_lock(physical)
            selected_ids = torch.from_numpy(a["token_union"].astype(np.int64)).to("cuda:0")
            models, before, before_buffers = [], [], []
            ids = torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
            attention = torch.cat((torch.ones((2, 1), dtype=torch.bool, device="cuda:0"), torch.from_numpy(cv).to("cuda:0")), 1)
            for label in SOURCES:
                budget.check()
                model = loading.load_cpu_bf16(label)
                models.append(model)
                if sum(p.numel() for p in model.parameters()) != 13568641024 or len(model.model.layers) != 16:
                    raise ValueError("Unexpected mature architecture")
                record = plan["source_records"][label]
                ph, bh = n.old.tensor_hash(model.state_dict()), n.old.tensor_hash(n.buffers(model))
                if ph != record["parameter_hash"] or bh != record["buffer_hash"]:
                    raise ValueError("Native canonical parameters/buffers differ")
                before.append(ph)
                before_buffers.append(bh)
                native_cal = record["calibration"]
                if n.sha(native_cal["path"]) != native_cal["sha256"]:
                    raise ValueError("Canonical native calibration differs")
                with np.load(native_cal["path"], allow_pickle=False) as f:
                    expected = torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                if not torch.equal(n.fwd(model, ids[:, :-1], attention[:, :-1]), expected):
                    raise ValueError("Native canonical logits differ")
                del expected
                n.old.emit("E158_source_loaded", source=label, peak_GB=torch.cuda.max_memory_allocated() / 1e9)
            del ids, attention
            raw = {"source_names": np.array(SOURCES), "scenario_names": np.array(SCENARIOS), "component_names": np.array(COMPONENTS),
                   "native_lp_selected": np.empty((3, 96, 38), np.float32), "uncached_lp_selected": np.empty((3, 96, 38), np.float32),
                   "native_top_tokens": np.empty((3, 96, 10), np.int64), "uncached_top_tokens": np.empty((3, 96, 10), np.int64),
                   "cache_KL": np.empty((3, 96), np.float64)}
            query_sets, identity_count = [], 0
            for m, (label, model) in enumerate(zip(SOURCES, models)):
                group = []
                for q in range(96):
                    budget.check()
                    token_ids = a["ids"][a["offsets"][q]:a["offsets"][q + 1]]
                    query = engine.capture(model, token_ids, int(a["gold_token"][q]))
                    group.append(query)
                    raw["native_lp_selected"][m, q] = query.lp[selected_ids].cpu().numpy()
                    raw["uncached_lp_selected"][m, q] = query.uncached_lp[selected_ids].cpu().numpy()
                    raw["native_top_tokens"][m, q] = top10(query.lp)
                    raw["uncached_top_tokens"][m, q] = top10(query.uncached_lp)
                    raw["cache_KL"][m, q] = query.uncached_to_cached_KL
                    if q in (0, 48):
                        engine.routed_native_identity(model, query)
                        for layer in range(16):
                            for component in COMPONENTS:
                                identity = engine.interchange(model, query, query, layer, component)
                                if not torch.equal(identity, query.lp):
                                    raise ValueError("Same-query component interchange changed prediction")
                                identity_count += 1
                                del identity
                    if (q + 1) % 24 == 0:
                        n.old.emit("E158_native_queries", source=label, queries=q + 1, total=96,
                                   peak_GB=torch.cuda.max_memory_allocated() / 1e9)
                query_sets.append(group)
            baseline_path = RAW / "baseline.npz"
            immutable_npz(baseline_path, raw)
            components_path = RAW / "component_cache.npz"
            immutable_npz(components_path, component_pack(query_sets))
            changed = (raw["native_top_tokens"][:, :, 0] != raw["uncached_top_tokens"][:, :, 0]).sum(-1)
            if raw["cache_KL"].max() > .005 or np.any(changed / 96 > .05):
                n.write(RESULT / "cache_floor_failure.json", {"status": "engineering_preflight_failed", "raw_baseline": str(baseline_path),
                        "cache_KL_max": float(raw["cache_KL"].max()), "argmax_changes": changed.tolist(), "scientific_patches_read": False})
                raise ValueError("Cached execution numerical floor exceeded the preregistered engineering scale")
            hits = (raw["native_top_tokens"] == a["gold_token"][None, :, None]).any(-1)
            joint_counts = hits[:, a["target_query_index"]].all(0).sum(-1)
            patch_obtained = bool(np.all(joint_counts >= 8))
            raw["positive_lp_selected"] = np.empty((3, 3, 2, 24, 38), np.float32)
            raw["positive_top_tokens"] = np.empty((3, 3, 2, 24, 10), np.int64)
            positive_count = 0
            for m, model in enumerate(models):
                for scenario in range(3):
                    budget.check()
                    for relation in range(2):
                        for country in range(24):
                            target = query_sets[m][int(a["target_query_index"][relation, country])]
                            source = query_sets[m][int(a["source_query_index"][scenario, relation, country])]
                            lp = engine.interchange(model, target, source, 15, "residual")
                            if not torch.equal(lp, source.lp):
                                raise ValueError("Final residual did not reproduce source distribution")
                            raw["positive_lp_selected"][m, scenario, relation, country] = lp[selected_ids].cpu().numpy()
                            raw["positive_top_tokens"][m, scenario, relation, country] = top10(lp)
                            del lp
                            positive_count += 1
            n.old.emit("E158_structural_controls_passed", same_query_cases=identity_count,
                       final_residual_cases=positive_count, joint_native_top10=joint_counts.tolist(), run_patches=patch_obtained)
            if patch_obtained:
                raw["patched_lp_selected"] = np.empty((3, 3, 3, 16, 2, 24, 38), np.float32)
                raw["patched_top_tokens"] = np.empty((3, 3, 3, 16, 2, 24, 10), np.int64)
                raw["patched_KL_vs_native"] = np.empty((3, 3, 3, 16, 2, 24), np.float64)
                completed = 0
                for m, (label, model) in enumerate(zip(SOURCES, models)):
                    for scenario in range(3):
                        for relation in range(2):
                            for country in range(24):
                                budget.check()
                                target = query_sets[m][int(a["target_query_index"][relation, country])]
                                source = query_sets[m][int(a["source_query_index"][scenario, relation, country])]
                                for layer in range(16):
                                    for c, component in enumerate(COMPONENTS):
                                        lp = engine.interchange(model, target, source, layer, component)
                                        key = (m, scenario, c, layer, relation, country)
                                        raw["patched_lp_selected"][key] = lp[selected_ids].cpu().numpy()
                                        raw["patched_top_tokens"][key] = top10(lp)
                                        raw["patched_KL_vs_native"][key] = prev.kl(target.lp, lp)
                                        del lp
                                completed += 48
                                if (country + 1) % 8 == 0:
                                    n.old.emit("E158_interchange_rows", source=label, scenario=SCENARIOS[scenario],
                                               relation=relation, countries=country + 1, rows=completed, total_rows=20736,
                                               peak_GB=torch.cuda.max_memory_allocated() / 1e9)
            for model, ph, bh in zip(models, before, before_buffers):
                if n.old.tensor_hash(model.state_dict()) != ph or n.old.tensor_hash(n.buffers(model)) != bh:
                    raise ValueError("Source parameters/buffers mutated")
                if any("forward" in layer.mlp.__dict__ or layer.mlp._forward_hooks or layer._forward_hooks for layer in model.model.layers):
                    raise ValueError("Temporary forward/hook not restored")
            for name, array in raw.items():
                if array.dtype.kind in "fiu" and not np.isfinite(array).all():
                    raise ValueError("Nonfinite readout: " + name)
            immutable_npz(final_path, raw)
            n.write(RESULT / "manifest.json", {"experiment": "E158", "status": "complete", "patch_data_obtained": patch_obtained,
                    "source_sha256": proof(), "plan_sha256": n.sha(RESULT / "plan.json"),
                    "raw": {"path": str(final_path), "sha256": n.sha(final_path), "size_bytes": final_path.stat().st_size},
                    "baseline": {"path": str(baseline_path), "sha256": n.sha(baseline_path)},
                    "component_cache": {"path": str(components_path), "sha256": n.sha(components_path), "encoding": "BF16 bits in uint16"},
                    "source_parameter_hashes": before, "source_buffer_hashes": before_buffers,
                    "joint_native_top10_counts": joint_counts.tolist(), "same_query_identity_cases": identity_count,
                    "final_residual_control_cases": positive_count, "scientific_patch_rows": 20736 if patch_obtained else 0,
                    "controls": {"canonical_parameters_buffers_and_legacy_cal_exact": True, "all_queries_fast_vs_native_cached_exact": True,
                                 "all_query_layers_component_reconstruction_exact": True, "native_S_zero_routed_taps_exact_fixed_queries": True,
                                 "same_query_interchanges_exact_fixed_queries": True, "final_residual_source_distributions_exact": True,
                                 "prefix_cache_and_forward_restored": True, "source_parameters_buffers_unchanged": True},
                    "physical_gpu": physical, "visible_device_uuid": str(torch.cuda.get_device_properties(0).uuid),
                    "peak_allocated_bytes": torch.cuda.max_memory_allocated(), "software": software(),
                    "scope": "Canonical answer first-token mediation within each model; fixed factual probes, no seed-population or full-answer generation claim."})
    finally:
        if lock is not None:
            lock.close()
    return {"status": "complete"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("self-test", "prepare", "evaluate"))
    parser.add_argument("--physical-gpu", type=int, default=0)
    args = parser.parse_args()
    torch.set_num_threads(4)
    out = self_test() if args.mode == "self-test" else prepare() if args.mode == "prepare" else evaluate(args.physical_gpu)
    print(json.dumps(out, indent=2), flush=True)
