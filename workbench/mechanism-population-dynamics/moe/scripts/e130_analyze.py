"""CPU-only fixed E130 functional comparisons; incomplete coverage stays explicit."""
from __future__ import annotations
import argparse, hashlib, itertools, json, os
from pathlib import Path
for variable in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[variable] = "1"
import numpy as np
import e124_compare as comparison
import e130_finalize as assets

WB = assets.WB
OUT = WB / "results/e130"
COMPARE_SHA = "1cd3df24aea09e1fb2db86d9e4db52fe53ca42d7564141a0987ff6ccd7313671"
PARAMETERS = {"permutations": 199, "random_maps": 199, "seed": 124, "min_std": 1e-8}
INDEPENDENT = ["seed0_anchor", *[f"seed{i}_order0" for i in range(1, 5)]]
MODELS = {**{name: (i, 0) for i, name in enumerate(INDEPENDENT)}, "seed0_repeat": (0, 0), "seed0_order1": (0, 1)}
COMMON_KEYS = ("backbone_sample_hash", "plan_sha256", "source_sha256", "selected_inputs_sha256", "Hcal_sha256",
               "input_identity_sha256", "Hcal_data_identity_sha256", "Hcal_window_hash")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def planned_pairs():
    pairs = [("cross_seed", a, "final", b, "final") for a, b in itertools.combinations(INDEPENDENT, 2)]
    pairs += [("late_to_final", name, "late", name, "final") for name in INDEPENDENT]
    pairs += [("rerun", "seed0_anchor", "final", "seed0_repeat", "final"),
              ("order", "seed0_anchor", "final", "seed0_order1", "final")]
    return pairs


def load_bank(path, seed, order, step, config_hash):
    bank = comparison.load_capture(path)
    metadata = bank["metadata"]
    expected = {"seed": seed, "order_seed": order, "step": step, "layer": 9, "experts": 64, "top_k": 8,
                "dtype": "bfloat16", "alpha": .125, "checkpoint_config_hash": config_hash,
                "script_sha256": assets.FROZEN["e124_functional_capture.py"], "plan_sha256": assets.PLAN_SHA}
    if any(metadata.get(key) != value for key, value in expected.items()): raise ValueError(f"Capture metadata differs: {path}")
    if bank["U"].shape != (1024, 64) or bank["A"].shape != (1024, 64): raise ValueError("Expected fixed 1024×64 U/A")
    if (bank["split"] == "cal").sum() != 512 or (bank["split"] == "held").sum() != 512:
        raise ValueError("Expected the fixed 512 cal / 512 held plan")
    hcal = metadata["hcal"]
    if any(hcal.get(key) != value for key, value in {"cal_seed": 91024, "seq_len": 512, "stride": 4, "split": "train"}.items()):
        raise ValueError("Hcal configuration differs")
    with np.load(path, allow_pickle=False) as raw:
        values = np.asarray(raw["Hcal"], dtype="<f4")
        if values.shape != (8192, 2048) or not np.isfinite(values).all(): raise ValueError("Invalid Hcal content/shape")
        hcal_hash = hashlib.sha256(values.tobytes()).hexdigest()
    identity = {key: metadata[key] for key in COMMON_KEYS[:4]}
    identity.update({"Hcal_sha256": hcal_hash, "Hcal_data_identity_sha256": hcal["data_identity_sha256"],
                     "Hcal_window_hash": hcal["window_hash"], "input_identity_sha256": digest({
                         key: bank[key].tolist() for key in ("item_id", "input_sha256", "word", "split")})})
    return bank, {"path": str(path), "sha256": assets.sha(path), **identity}


def validate_training(summary, provenance, protocol, name):
    if not assets.ready(summary, None): raise ValueError("Training is not complete62500/512M; no score-based exclusion")
    seed, order = MODELS[name]
    args = provenance["args"]
    expected = {"seed": seed, "order_seed": order, "steps": 62500, "max_train_tokens": 512_000_000,
                "seq_len": 512, "batch_size": 16, "accum": 1, "replacement": "moe", "layer": 9,
                "experts": 64, "expert_size": 1024, "top_k": 8, "dtype": "bfloat16"}
    if any(args.get(key) != value for key, value in expected.items()): raise ValueError("Training identity/architecture/budget differs")
    experiment, driver = ("E128", assets.FROZEN["e128_epoch_recovery.py"]) if name == "seed0_anchor" else ("E130", assets.DRIVER_SHA)
    if (protocol.get("experiment") != experiment or protocol.get("driver_sha256") != driver
            or args.get("driver_sha256") != driver or protocol.get("cpu_test") is not False):
        raise ValueError("Registered training driver protocol differs")
    if (summary.get("config_hash") != provenance.get("config_hash")
            or summary.get("initial_tensor_sha256") != provenance.get("initial_tensor_sha256")
            or summary.get("frozen_sample_hash_before") != summary.get("frozen_sample_hash_after")
            or summary.get("frozen_sample_hash_after") != provenance.get("frozen_sample_hash")):
        raise ValueError("Summary/provenance/frozen fingerprint mismatch")


def quality(summary, provenance, name):
    evaluations = [row for row in summary["evaluations"] if row["step"] == 62500]
    if len(evaluations) != 1: raise ValueError("Missing or duplicate fixed endpoint evaluation")
    final = evaluations[0]
    fidelity_path = WB / "results/e128/predictive_fidelity.json" if name == "seed0_anchor" else OUT / "fidelity" / f"{name}.json"
    fidelity = assets.read(fidelity_path)
    if fidelity and (fidelity.get("step") != 62500 or fidelity.get("frozen_sample_hash") != provenance["frozen_sample_hash"]
                     or fidelity.get("held_window_hash") != provenance.get("held_window_hash")):
        raise ValueError("Fidelity score does not match the fixed endpoint/input identity")
    return {"held": final["held"], "held_delta_dense": final["held_delta_dense"], "pos": final["pos"],
            "pos_delta_dense": final["pos_delta_dense"], "fidelity": fidelity,
            "fidelity_path": str(fidelity_path), "fidelity_sha256": assets.sha(fidelity_path) if fidelity else None,
            "scope": "File/word evaluation intervals; not uncertainty across independent training seeds"}


def staged_file(folder, filename, stage):
    path = folder / filename
    record = stage["files"].get(filename)
    if not record: raise FileNotFoundError(f"No SHA-verified staging record: {filename}")
    if (Path(record["path"]).resolve() != path.resolve() or path.stat().st_size != record["size_bytes"]
            or assets.sha(path) != record["sha256"]): raise ValueError(f"Staged asset SHA/path/size mismatch: {filename}")
    return record


def load_models(root, manifest):
    report, banks = {}, {}
    stages = {record["id"]: record for record in manifest.get("models", [])} if manifest else {}
    for name, (seed, order) in MODELS.items():
        folder = root / name
        info = {"status": "missing", "errors": {}, "required_captures": ["final", "late"] if name in INDEPENDENT else ["final"],
                "captures": {}, "quality": None, "seed": seed, "order_seed": order}
        report[name] = info
        summary, provenance = assets.read(folder / "training_summary.json"), assets.read(folder / "provenance.json")
        try:
            stage = stages[name]
            info["staging_source"] = {key: stage.get(key) for key in ("source_host", "source_dir", "status", "endpoints")}
            info["verified_staging_sources"] = {filename: staged_file(folder, filename, stage)
                for filename in ("training_summary.json", "provenance.json", "driver_protocol.json")}
            if not summary or not provenance: raise FileNotFoundError("Staged training_summary.json/provenance.json missing")
            if assets.read(folder / "failure.json") is not None: raise ValueError("Staged training failure is recorded")
            validate_training(summary, provenance, assets.read(folder / "driver_protocol.json"), name)
            info["training_summary_sha256"], info["provenance_sha256"] = assets.sha(folder / "training_summary.json"), assets.sha(folder / "provenance.json")
            info["quality"] = quality(summary, provenance, name)
        except Exception as error:
            info["errors"]["training_or_quality"] = f"{type(error).__name__}: {error}"; continue
        for label in info["required_captures"]:
            try:
                info["verified_staging_sources"][label + ".npz"] = staged_file(folder, label + ".npz", stage)
                bank, identity = load_bank(folder / f"{label}.npz", seed, order, 62500 if label == "final" else 61440, summary["config_hash"])
                if identity["backbone_sample_hash"] != provenance["frozen_sample_hash"]:
                    raise ValueError("Capture backbone differs from its training provenance")
                info["captures"][label] = identity; banks[name, label] = bank
            except Exception as error: info["errors"][label] = f"{type(error).__name__}: {error}"
        if not info["quality"]["fidelity"]: info["errors"]["fidelity"] = "Fixed-endpoint fidelity file missing"
        info["status"] = "complete" if not info["errors"] else "partial"
    # A single fixed input/Hcal identity must hold across every admitted capture.
    anchor = report["seed0_anchor"]["captures"].get("final")
    for name, info in report.items():
        for label, identity in list(info["captures"].items()):
            if anchor is None or any(identity[key] != anchor[key] for key in COMMON_KEYS):
                info["errors"][label] = "Fixed common plan/input/Hcal content identity differs or anchor unavailable"
                info["status"] = "partial"; banks.pop((name, label), None); del info["captures"][label]
    return report, banks


def compare_pair(specification, models, banks):
    kind, a, alabel, b, blabel = specification
    pair_id = f"{a}_{alabel}__{b}_{blabel}"
    identity = {"kind": kind, "A": {**models[a]["captures"][alabel], "training_summary_sha256": models[a]["training_summary_sha256"],
                                    "provenance_sha256": models[a]["provenance_sha256"]},
                "B": {**models[b]["captures"][blabel], "training_summary_sha256": models[b]["training_summary_sha256"],
                       "provenance_sha256": models[b]["provenance_sha256"]},
                "analysis_script_sha256": assets.sha(__file__), "comparison_script_sha256": COMPARE_SHA, "parameters": PARAMETERS}
    path = OUT / "comparison/batch" / f"{pair_id}.json"
    old = assets.read(path)
    if old and old.get("batch_identity") == identity and old.get("status") == "complete": return old, path
    try:
        result = comparison.compare(banks[a, alabel], banks[b, blabel], **PARAMETERS)
        result.update({"status": "complete", "pair_id": pair_id, "batch_identity": identity,
                       "identity": comparison.comparison_identity(banks[a, alabel], banks[b, blabel], "auto")})
    except Exception as error:
        result = {"status": "failed", "pair_id": pair_id, "batch_identity": identity,
                  "error": f"{type(error).__name__}: {error}"}
    assets.write(path, result)
    return result, path


def compact(result):
    if result["status"] != "complete": return {"status": result["status"], "error": result.get("error")}
    return {"status": "complete", "n_matched_columns": result["n_matched_columns"], "n_cal_items": result["n_cal_items"],
            "n_held_items_evaluated": result["n_held_items_evaluated"], "coverage": result["coverage"],
            "function": {key: {"rho": value["held_conditional_columns"]["mean"],
                               "valid_columns": value["held_conditional_columns"]["n_valid_columns"],
                               "raw_difference": value["raw_effect_difference_under_cal_U_mapping"],
                               "conditional_strength": value["conditional_strength_nats"],
                               "raw_strength": value["raw_unaligned_effect_summary_nats"],
                               "cal_shuffle_reference": value["cal_word_shuffle_rematch_reference"],
                               "random_mapping_reference": value["random_mapping_reference"]} for key, value in result["function"].items()}}


def matrices(pairs):
    result = {}
    for key in ("U", "A"):
        fields = {name: [[None] * 5 for _ in range(5)] for name in ("rho", "valid_columns", "raw_rmse_nats", "row_model_held_strength_nats", "row_model_raw_rms_nats")}
        finite, observed_models = [], set()
        for specification in planned_pairs():
            kind, a, alabel, b, blabel = specification
            if kind != "cross_seed": continue
            pair = pairs[f"{a}_{alabel}__{b}_{blabel}"]
            if pair["status"] != "complete": continue
            value = pair["function"][key]; i, j = INDEPENDENT.index(a), INDEPENDENT.index(b)
            for field, number in (("rho", value["rho"]), ("valid_columns", value["valid_columns"]),
                                  ("raw_rmse_nats", value["raw_difference"]["rmse_nats"] if value["raw_difference"] else None)):
                fields[field][i][j] = fields[field][j][i] = number
            for row, col, who in ((i, j, "A"), (j, i, "B")):
                fields["row_model_held_strength_nats"][row][col] = value["conditional_strength"][who + "_held_rms"]
                fields["row_model_raw_rms_nats"][row][col] = value["raw_strength"][who + "_rms"]
            if value["rho"] is not None: finite.append(value["rho"]); observed_models.update((a, b))
        result[key] = {"matrices": fields, "per_seed_mean": {
            name: {"mean": float(np.mean([x for x in row if x is not None])) if any(x is not None for x in row) else None,
                   "finite_pairs": sum(x is not None for x in row), "expected_pairs": 4}
            for name, row in zip(INDEPENDENT, fields["rho"])},
            "descriptive_pair_mean": float(np.mean(finite)) if finite else None, "finite_pair_scores": len(finite),
            "expected_pair_scores": 10, "independent_training_units": 5,
            "observed_training_units_with_finite_pairs": len(observed_models),
            "sampling_note": "Ten pairs share five seeds; descriptive mean only, no pair-based confidence interval or significance."}
    return result


def initial_reference(anchor):
    path = OUT / "comparison/initial_seed0_seed1.json"
    result = assets.read(path)
    if not result: return {"status": "missing", "path": str(path)}
    try:
        if result.get("script_sha256") != COMPARE_SHA or result.get("reference_seed") != 124:
            raise ValueError("Initial-reference comparator/seed differs")
        for key in ("U", "A"):
            for name in ("cal_word_shuffle_rematch_reference", "random_mapping_reference"):
                if result["function"][key][name]["n_draws"] != 199: raise ValueError("Initial-reference counts differ")
        if result.get("variance_floor_nats") != 1e-8: raise ValueError("Initial-reference numeric floor differs")
        sources = {}
        for side, seed in (("A", 0), ("B", 1)):
            metadata = result["identity"]["metadata_" + side]
            _, identity = load_bank(Path(result["capture_" + side]), seed, 0, 0, metadata["checkpoint_config_hash"])
            if any(identity[key] != anchor[key] for key in COMMON_KEYS): raise ValueError("Initial reference uses a different common input/Hcal")
            sources[side] = identity
        return {**compact({**result, "status": "complete"}), "path": str(path), "source_json_sha256": assets.sha(path),
                "capture_sources": sources, "scope": "Previously computed fixed untrained seed0/1 auxiliary reference; not a null or extra trained replication"}
    except Exception as error: return {"status": "failed", "path": str(path), "error": f"{type(error).__name__}: {error}"}


def plot(summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import colors
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "pdf.fonttype": 42, "ps.fonttype": 42})
    figure, axes = plt.subplots(2, 2, figsize=(11.2, 8.4), gridspec_kw={"height_ratios": [1.25, 1]})
    for column, key in enumerate(("U", "A")):
        axis = axes[0, column]; matrix = np.array(summary["cross_seed"][key]["matrices"]["rho"], dtype=float)
        cmap = plt.get_cmap("coolwarm").copy(); cmap.set_bad("#eeeeee")
        im = axis.imshow(np.ma.masked_invalid(matrix), cmap=cmap, norm=colors.Normalize(-1, 1))
        axis.set_xticks(range(5), range(5)); axis.set_yticks(range(5), range(5))
        axis.set_xlabel("Independent initialization seed"); axis.set_ylabel("Independent initialization seed")
        axis.set_title(f"{key}: held conditional column correlation")
        for i in range(5):
            for j in range(5):
                axis.text(j, i, "—" if not np.isfinite(matrix[i, j]) else f"{matrix[i,j]:.3f}", ha="center", va="center",
                          color="white" if np.isfinite(matrix[i,j]) and abs(matrix[i,j]) > .65 else "black", fontsize=9)
        figure.colorbar(im, ax=axis, fraction=.046, pad=.04, ticks=[-1, -.5, 0, .5, 1])
        labels, values = [], []
        for specification in planned_pairs()[10:]:
            kind, a, alabel, b, blabel = specification
            labels.append(f"S{MODELS[a][0]} late→final" if kind == "late_to_final" else ("S0 rerun" if kind == "rerun" else "S0 order1"))
            pair = summary["pairs"][f"{a}_{alabel}__{b}_{blabel}"]
            values.append(pair["function"][key]["rho"] if pair["status"] == "complete" else None)
        labels.append("Initial S0/S1"); initial = summary["initial_reference"]
        values.append(initial["function"][key]["rho"] if initial["status"] == "complete" else None)
        axis = axes[1, column]
        for i, number in enumerate(values):
            if number is None: axis.text(i, 0, "missing", rotation=90, ha="center", va="bottom", color="gray", fontsize=8)
            else:
                axis.bar(i, number, color="#4477aa")
                axis.text(i, number - .08 if number > .9 else number + (.035 if number >= 0 else -.07),
                          f"{number:.3f}", ha="center", fontsize=8, color="white" if number > .9 else "black")
        axis.set_ylim(-1, 1); axis.set_yticks([-1, -.5, 0, .5, 1]); axis.axhline(0, color="gray", linewidth=.6)
        axis.set_xticks(range(len(labels)), labels, rotation=40, ha="right"); axis.set_title(f"{key}: references, shown separately")
        axis.set_ylabel("Held conditional column correlation")
    figure.suptitle(f"E130 fixed-budget functional comparisons — {summary['status']}")
    figure.text(.5, .015, "Cal-only U matching; 512 held items. Five independent seeds; ten overlapping pairs. Gray cells are unmeasured/undefined.\nReferences are descriptive controls; no division by self-similarity and no pair-based inference.", ha="center", fontsize=9)
    figure.tight_layout(rect=(0, .07, 1, .95))
    folder = OUT / "figures"; folder.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf"): figure.savefig(folder / f"functional_batch.{suffix}", dpi=300, bbox_inches="tight")
    plt.close(figure)


def run(args):
    if assets.sha(WB / "scripts/e124_compare.py") != COMPARE_SHA: raise ValueError("Frozen comparator source differs")
    manifest = assets.read(args.staging_manifest)
    if manifest and Path(manifest["staging_root"]).resolve() != args.analysis_root.resolve():
        raise ValueError("Staging root differs from the SHA manifest")
    models, banks = load_models(args.analysis_root, manifest)
    pairs, missing = {}, []
    ready_all = all(info["status"] == "complete" for info in models.values())
    for specification in planned_pairs():
        kind, a, alabel, b, blabel = specification; pair_id = f"{a}_{alabel}__{b}_{blabel}"
        if (a, alabel) not in banks or (b, blabel) not in banks or (not args.available_only and not ready_all):
            pairs[pair_id] = {"status": "pending", "kind": kind}; missing.append(pair_id); continue
        result, path = compare_pair(specification, models, banks)
        pairs[pair_id] = {**compact(result), "kind": kind, "path": str(path), "sha256": assets.sha(path)}
    anchor = models["seed0_anchor"]["captures"].get("final")
    initial = initial_reference(anchor) if anchor else {"status": "pending", "reason": "Anchor missing"}
    complete = ready_all and all(pair["status"] == "complete" for pair in pairs.values()) and initial["status"] == "complete"
    summary = {"experiment": "E130", "status": "complete" if complete else "partial", "analysis_script_sha256": assets.sha(__file__),
               "comparison_script_sha256": COMPARE_SHA, "parameters": PARAMETERS, "analysis_root": str(args.analysis_root),
               "staging_manifest": manifest, "models": models, "pairs": pairs,
               "expected_pair_coverage": {"cross_seed": 10, "late_to_final": 5, "rerun": 1, "order": 1},
               "completed_pairs": sum(pair["status"] == "complete" for pair in pairs.values()), "expected_pairs": 17,
               "missing_pairs": missing, "failed_pairs": [name for name, pair in pairs.items() if pair["status"] == "failed"],
               "missing_or_incomplete_models": [name for name, info in models.items() if info["status"] != "complete"],
               "initial_reference": initial, "cross_seed": matrices(pairs),
               "interpretation": "Fixed finite-budget descriptive readouts; no NLL eligibility gate, no independent-pair inference, no automatic claim upgrade."}
    assets.write(OUT / "batch_summary.json", summary); plot(summary)
    print(json.dumps({"status": summary["status"], "completed_pairs": summary["completed_pairs"],
                      "missing_models": summary["missing_or_incomplete_models"], "cross_seed": {
                          key: {name: value for name, value in data.items() if name != "matrices"} for key, data in summary["cross_seed"].items()}}, indent=2), flush=True)
    return summary


def self_test():
    pairs = planned_pairs()
    assert len(pairs) == 17 and len({tuple(item) for item in pairs}) == 17
    assert sum(pair[0] == "cross_seed" for pair in pairs) == 10 and sum(pair[0] == "late_to_final" for pair in pairs) == 5
    assert MODELS["seed0_anchor"] == MODELS["seed0_repeat"] == (0, 0) and MODELS["seed0_order1"] == (0, 1)
    # Keep the existing cal-only matching/held-isolation known answers authoritative.
    comparison.self_test()
    print(json.dumps({"passed": True, "CPU_only": True, "fixed_pair_counts": "10+5+2", "script_sha256": assets.sha(__file__)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e130_analysis"))
    parser.add_argument("--staging-manifest", type=Path, default=OUT / "analysis_staging.json")
    parser.add_argument("--available-only", action="store_true"); parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test: self_test()
    else:
        result = run(args)
        if not args.available_only and result["status"] != "complete": raise SystemExit(2)
