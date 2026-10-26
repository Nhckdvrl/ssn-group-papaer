"""E136 oracle readouts: imposed identity A is primary; original cal-U retained.

Initial A controls shared support. It is not subtracted to manufacture a pure
specialization effect; neither predefined correspondence is selected by held.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoeForCausalLM
import e124_compare as matching
import e135_readout as original
import e135_capture as operators
import e136_train as training
import e136_capture as profiles

c, assets, base, WB = training.c, training.assets, training.base, training.WB
TRAIN_SHA = "8c620871df90c2a10ea9be5b629727ce063164483ab8a0d22cb846e6f6841b55"
E135_READOUT_SHA = "70274a65f532097cd4dfd017c4ce5f3def9496bb08d87e6b77b3267fc8e5690c"
E135_CAPTURE_SHA = "d528f12afabad26a503bcedd02f8192bd243dc8edd22113ace65970e2dfaf9f4"


def fixed_scores(teacher, oracle, ia, ib):
    for key in ("word", "split", "item_id", "input_sha256"):
        if not np.array_equal(teacher[key], oracle[key]): raise ValueError("Fixed-correspondence population differs")
    cal, held = teacher["split"] == "cal", teacher["split"] == "held"
    residuals, coverage, use = {}, {}, held.copy()
    for who, capture in (("teacher", teacher), ("oracle", oracle)):
        for key in ("U", "A"):
            residuals[who, key], eligible, coverage[who + "_" + key] = matching.residualize(capture[key], capture["word"], cal, held)
            use &= eligible
    words = teacher["word"][use]; groups = [np.flatnonzero(words == word) for word in np.unique(words)]
    result = {"coverage": coverage, "held_items": int(use.sum()), "held_words": len(groups), "mapped_columns": len(ia), "function": {}}
    rng = np.random.default_rng(136); selections = [np.concatenate([groups[index] for index in draw]) for draw in rng.integers(0, len(groups), (1000, len(groups)))] if groups else []
    for key in ("U", "A"):
        a, b = residuals["teacher", key][use], residuals["oracle", key][use]
        observed = matching.column_scores(a, b, ia, ib, 1e-8)
        bootstrap = [matching.column_scores(a[index], b[index], ia, ib, 1e-8) for index in selections]
        finite = [value["mean"] for value in bootstrap if value["mean"] is not None]; counts = [value["n_valid_columns"] for value in bootstrap]
        changed = sum(value["valid_mapping_positions"] != observed["valid_mapping_positions"] for value in bootstrap)
        comparable = len(bootstrap) == len(finite) == 1000 and changed == 0
        result["function"][key] = {"held_conditional_columns": observed,
            "fixed_map_word_bootstrap_ci95": np.quantile(finite, [.025, .975]).tolist() if comparable else None,
            "bootstrap_draws": 1000, "finite_bootstrap_draws": len(finite), "valid_column_count_range": [min(counts), max(counts)] if counts else [],
            "undefined_bootstrap_draws": len(bootstrap) - len(finite), "valid_mapping_positions_changed_draws": changed,
            "coverage_comparable": comparable,
            "raw_effect_difference": matching.raw_difference(teacher[key][use], oracle[key][use], ia, ib),
            "conditional_strength_nats": {"teacher_held_RMS": float(np.sqrt(np.square(a).mean())), "oracle_held_RMS": float(np.sqrt(np.square(b).mean()))},
            "bootstrap_scope": "Resample held word clusters with cal offsets/map fixed; CI withheld unless all1000 draws finite with exactly the observed valid mapping positions; no draw/word filtering or student-population CI"}
    return result


def correspondences(teacher, oracle):
    conventional = matching.compare(teacher, oracle, permutations=199, random_maps=199, seed=124, min_std=1e-8)
    mapping = conventional["mapping_A_to_B"]; ia = np.array([i for i, value in enumerate(mapping) if value is not None], dtype=int)
    ib = np.array([value for value in mapping if value is not None], dtype=int); e = teacher["U"].shape[1]
    conventional["interpretation"] = "Native-public teacher U background; original cal-U estimator retained, not selected against known imposed identity. A includes natural availability/background."
    return {"known_identity": {"mapping": list(range(e)), "scope": "Teacher gate rows supplied before learning; known interface coordinates, not task-discovered identity",
                              **fixed_scores(teacher, oracle, np.arange(e), np.arange(e))},
            "cal_U": {"mapping": mapping, "scope": "Original cal-U Hungarian, held evaluated without rematching", **fixed_scores(teacher, oracle, ia, ib)},
            "original_cal_U_reference": conventional,
            "baseline_note": "Oracle-initial A includes common support/gate effects; final minus initial is not purified specialization. All predefined maps/undefined columns retained."}


def preflight(args):
    for name, expected in (("e136_train.py", TRAIN_SHA), ("e135_readout.py", E135_READOUT_SHA), ("e135_capture.py", E135_CAPTURE_SHA)):
        if assets.sha(WB / "scripts" / name) != expected: raise ValueError("Frozen oracle/source dependency differs")
    manifest, arrays, orders, dims, expected_initial, rng, initialization = training.preflight(args)
    teacher = torch.load(args.cache_root / "teacher_block.pt", map_location="cpu", mmap=True, weights_only=False)
    states = {"teacher": teacher["state"]}; proofs = {}
    provenance = assets.read(args.oracle_dir / "provenance.json")
    conditions = [("oracle_initial", 0, args.oracle_dir / "initial.pt")]
    if args.phase == "all": conditions.append(("oracle_final", 4096, args.oracle_dir / "checkpoint.pt"))
    for name, step, path in conditions:
        checkpoint = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
        if (checkpoint.get("experiment") != "E136" or checkpoint.get("schema") != "E136-assignment-oracle-v1" or checkpoint.get("step") != step
                or checkpoint.get("initialization") != initialization or checkpoint.get("config_hash") != provenance["config_hash"]
                or provenance["scientific"]["driver_sha256"] != TRAIN_SHA): raise ValueError("Oracle checkpoint/source/initialization differs")
        state = checkpoint["student_state"]
        if any(value.dtype != torch.float32 for value in state.values()) or training.gate_hash(state) != initialization["oracle_gate_FP32_sha256"]:
            raise ValueError("Frozen supplied gate or FP32 storage differs")
        if step == 0 and training.expert_hash(state) != initialization["source_expert_only_sha256"]: raise ValueError("Oracle initial expert identity differs")
        if step == 4096:
            summary = assets.read(args.oracle_dir / "training_summary.json")
            if summary.get("status") != "complete" or summary.get("step") != step or not np.array_equal(checkpoint["cache_batch_counts"], np.full(1024, 4)):
                raise ValueError("Only fixed4096 complete oracle endpoint is evaluated")
        states[name] = state
        proofs[name] = {"experiment": "E136", "condition": name, "step": step, "checkpoint": str(path), "checkpoint_sha256": assets.sha(path),
            "full_tensor_sha256": c.tensor_state_hash(state), "expert_only_tensor_sha256": training.expert_hash(state),
            "gate_tensor_sha256": training.gate_hash(state), "initialization": initialization, "config_hash": checkpoint["config_hash"]}
    plan, items, metadata = operators.protocol.load_plan(args.plan)
    if assets.sha(args.plan) != assets.PLAN_SHA or len(items) != 1024: raise ValueError("Fixed plan population differs")
    teacher_profile = args.e135_raw / "teacher_functional.npz"; teacher_summary = assets.read(WB / "results/e135/functional/teacher.json")
    if not teacher_summary or assets.sha(teacher_profile) != teacher_summary["output_sha256"]: raise ValueError("Immutable native teacher profile differs")
    _, reuse_proof = profiles.reused_initial_u(args, proofs["oracle_initial"], manifest, metadata)
    proofs["oracle_initial"]["U_coupled_reuse_proof"] = reuse_proof
    _, support_proof = profiles.teacher_support(args, manifest, metadata)
    for proof in proofs.values(): proof["teacher_support_source_proof"] = support_proof
    return manifest, states, proofs, items, metadata


@torch.no_grad()
def run(args):
    manifest, states, proofs, items, metadata = preflight(args); gpu = c.select_gpu(args.physical_gpu)
    args.raw_output.mkdir(parents=True, exist_ok=True)
    with training.Budget(args.budget_file, "oracle_readout") as budget:
        model = OlmoeForCausalLM.from_pretrained(manifest["model"], dtype=torch.bfloat16, local_files_only=True,
            attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False); model.config.use_cache = False
        teacher = model.model.layers[9].mlp; original_hash = c.tensor_state_hash(teacher.state_dict())
        if original_hash != manifest["teacher_block_tensor_sha256"] or base.sampled_parameter_hash(model, "model.layers.9.mlp.") != manifest["teacher_prefix_hash"]:
            raise ValueError("Native teacher runtime source differs")
        banks = {name: operators.MeasuredPublic(state) for name, state in states.items()}; states.clear()
        before = {name: c.tensor_state_hash(bank.inner.state_dict()) for name, bank in banks.items()}
        data = base.TokenData(manifest["data"], 512); windows = data.fixed_windows("held", 512, 91023)
        if base.digest_json(windows) != manifest["held_window_hash"]: raise ValueError("Held windows differ")
        result = {"experiment": "E136", "status": "partial", "phase": args.phase, "driver_sha256": assets.sha(__file__),
            "capture_sha256": assets.sha(WB / "scripts/e136_capture.py"), "train_sha256": TRAIN_SHA, "cache_manifest_sha256": assets.sha(args.cache_root / "manifest.json"),
            "condition_proofs": proofs, "gpu_preflight": gpu, "scope": __doc__, "errors": {}, "expected_conditions": ["oracle_initial", "oracle_final"]}
        def save(): assets.write(args.summary, result)
        for name in proofs:
            try: result.setdefault("held_function", {})[name] = original.held_function_mse(banks[name], manifest, args, budget)
            except Exception as error: result["errors"]["held_function_" + name] = f"{type(error).__name__}: {error}"
        try: result["natural_predictors"] = original.natural_predictions(model, teacher, banks, data, windows, items, metadata, args, budget); save()
        except Exception as error: result["errors"]["natural_predictors"] = f"{type(error).__name__}: {error}"; model.model.layers[9].mlp = teacher
        teacher_path = args.e135_raw / "teacher_functional.npz"
        for name in proofs:
            try:
                path, summary = profiles.capture(model, teacher, banks[name], name, proofs[name], manifest, args, budget)
                result.setdefault("functional_arrays", {})[name] = summary
                support = summary["teacher_support"]
                if support["teacher_slot_mismatch_rows"] or support["teacher_mask_mismatch_rows"] or support["teacher_weight_max_abs_difference"] != 0:
                    result["errors"]["actual_support_" + name] = support
                scores = correspondences(matching.load_capture(teacher_path), matching.load_capture(path))
                output = WB / "results/e136/comparison" / f"teacher_to_{name}.json"; assets.write(output, {"experiment": "E136", **scores})
                result.setdefault("correspondences", {})[name] = {"path": str(output), "sha256": assets.sha(output),
                    "known_identity": scores["known_identity"], "cal_U": scores["cal_U"]}
            except Exception as error: result["errors"]["functional_or_comparison_" + name] = f"{type(error).__name__}: {error}"; model.model.layers[9].mlp = teacher
            save()
        if "oracle_final" in banks:
            try: result["final_oracle_necessity"] = original.final_necessity(model, teacher, banks["oracle_final"], data, windows, manifest, args, budget)
            except Exception as error: result["errors"]["final_oracle_necessity"] = f"{type(error).__name__}: {error}"; model.model.layers[9].mlp = teacher
        if c.tensor_state_hash(teacher.state_dict()) != original_hash or base.sampled_parameter_hash(model, "model.layers.9.mlp.") != manifest["teacher_prefix_hash"]:
            raise RuntimeError("Teacher/prefix parameters changed")
        if any(c.tensor_state_hash(bank.inner.state_dict()) != before[name] for name, bank in banks.items()): raise RuntimeError("Oracle parameter/gate mutation")
        result["status"] = "complete" if args.phase == "all" and not result["errors"] else "partial"; save()
    return result


def self_test():
    rng = np.random.default_rng(136); n, e = 160, 4; words = np.array([f"w{i%8}" for i in range(n)])
    values = rng.normal(size=(n, e)); permutation = np.array([2, 0, 3, 1])
    teacher = {"U": values, "A": values * .3, "word": words, "split": np.array(["cal"] * 80 + ["held"] * 80),
        "item_id": np.arange(n), "input_sha256": np.array([str(i) for i in range(n)])}
    oracle = {**teacher, "U": values[:, permutation], "A": values[:, permutation] * .3}
    # Use the fixed-map helper directly; 199-reference matching remains frozen code.
    identity = fixed_scores(teacher, oracle, np.arange(e), np.arange(e))
    cal_u = fixed_scores(teacher, oracle, np.arange(e), np.argsort(permutation))
    assert cal_u["function"]["A"]["held_conditional_columns"]["mean"] > .999999
    assert identity["function"]["A"]["held_conditional_columns"]["mean"] < .99
    assert len(cal_u["function"]["A"]["held_conditional_columns"]["column_rho"]) == e
    assert cal_u["function"]["A"]["finite_bootstrap_draws"] == 1000
    sparse = {"U": np.array([[0.,0.,0.]] * 4 + [[1.,0.,-1.], [0.,2.,-2.]]), "word": np.array(["a","a","b","b","a","b"]),
        "split": np.array(["cal"] * 4 + ["held"] * 2), "item_id": np.arange(6), "input_sha256": np.array([str(i) for i in range(6)])}
    sparse["A"] = sparse["U"] * .3
    withheld = fixed_scores(sparse, sparse, np.arange(3), np.arange(3))["function"]["A"]
    assert withheld["held_conditional_columns"]["mean"] > .999999 and withheld["undefined_bootstrap_draws"] > 0
    assert withheld["valid_mapping_positions_changed_draws"] > 0 and withheld["fixed_map_word_bootstrap_ci95"] is None
    result = {"passed": True, "CPU_only": True, "imposed_identity_and_calU_both_reported": True,
        "fixed_cal_preprocessing_held_word_cluster_CI": True, "CI_withheld_when_any_draw_or_valid_mapping_set_changes": True,
        "all_columns_and_raw_effects_retained": True,
        "driver_sha256": assets.sha(__file__), "capture_sha256": assets.sha(WB / "scripts/e136_capture.py")}
    assets.write(WB / "results/e136/readout_self_test.json", result); return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--mode", choices=("preflight", "evaluate", "self-test"), default="preflight")
    parser.add_argument("--phase", choices=("initial", "all"), default="all")
    parser.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache"))
    parser.add_argument("--reference-initial", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_student/initial.pt"))
    parser.add_argument("--oracle-dir", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_oracle"))
    parser.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_budget.json"))
    parser.add_argument("--e135-raw", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_readout"))
    parser.add_argument("--plan", type=Path, default=WB / "results/e124/plan.json")
    parser.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e136_readout"))
    parser.add_argument("--summary", type=Path, default=WB / "results/e136/readout.json"); parser.add_argument("--physical-gpu", type=int, default=1)
    args = parser.parse_args()
    if args.mode == "self-test": result = self_test()
    elif args.mode == "preflight":
        manifest, states, proofs, items, metadata = preflight(args)
        result = {"status": "CPU_preflight_only", "conditions": proofs, "plan_items": len(items), "driver_sha256": assets.sha(__file__)}
    else: result = run(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
