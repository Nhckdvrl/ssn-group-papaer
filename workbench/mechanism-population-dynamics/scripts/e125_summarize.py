"""CPU E125 endpoint summary. Never selects an intermediate best checkpoint.

Requires M-small/M-cover/D-cover outputs at complete step15625/128M tokens.
Missing/incomplete endpoints produce pending without effect estimates or plots.
All bootstrap intervals describe evaluation-file/word uncertainty, not seed CI.
"""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np


WB = Path(__file__).resolve().parents[1]
EXPECTED_STEP, EXPECTED_TOKENS = 15625, 128_000_000
OPERATIONAL = {"mode", "output", "resume", "max_updates", "save_every", "eval_every", "max_hours", "init_registry", "run_id", "summary"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    tmp.replace(path)


def paired_file_bootstrap(first, second, iterations=1000, seed=125):
    """first-minus-second on identical held sequences, resampling original files."""
    key = lambda row: (row["source"], row["file_id"], int(row["window"]), int(row["tokens"]))
    if not first or [key(r) for r in first] != [key(r) for r in second]:
        raise ValueError("Paired held anchors/order/tokens differ")
    groups = {}
    for a, b in zip(first, second):
        values = np.array([a["nll_sum"], b["nll_sum"], a["tokens"]], dtype=float)
        if not np.isfinite(values).all() or values[2] <= 0:
            raise ValueError("Invalid sequence loss/token record")
        groups.setdefault((a["source"], a["file_id"]), np.zeros(3))[:] += values
    values = np.stack(list(groups.values()))
    total = values.sum(0)
    rng = np.random.default_rng(seed)
    selected = rng.integers(0, len(values), (iterations, len(values)))
    samples = values[selected].sum(1)
    differences = (samples[:, 0] - samples[:, 1]) / samples[:, 2]
    return {"first_nll": float(total[0] / total[2]), "second_nll": float(total[1] / total[2]),
            "difference_nats_first_minus_second": float((total[0] - total[1]) / total[2]),
            "ci90": np.quantile(differences, [.05, .95]).tolist(),
            "ci95": np.quantile(differences, [.025, .975]).tolist(),
            "file_clusters": len(values), "sequences": len(first), "tokens": int(total[2]),
            "ci_unit": "original held file; evaluation uncertainty, not independent seeds",
            "ci_degenerate": len(values) < 2, "bootstrap_iterations": iterations, "bootstrap_seed": seed}


def word_effect(values, iterations, seed):
    values = np.asarray(values, dtype=float)
    if not len(values):
        return {"mean": None, "ci90": [], "ci95": [], "words": 0}
    rng = np.random.default_rng(seed)
    boot = values[rng.integers(0, len(values), (iterations, len(values)))].mean(1)
    return {"mean": float(values.mean()), "ci90": np.quantile(boot, [.05, .95]).tolist(),
            "ci95": np.quantile(boot, [.025, .975]).tolist(), "words": len(values)}


def paired_pos(first, second, iterations, seed):
    if len(first) != len(second) or [(r["word"], r["condition"]) for r in first] != [(r["word"], r["condition"]) for r in second]:
        raise ValueError("Paired POS records differ in count/order/labels")
    if not first:
        return {"status": "unavailable", "items": 0}
    words = {}
    for a, b in zip(first, second):
        delta = float(a["nll"]) - float(b["nll"])
        if not np.isfinite(delta):
            raise ValueError("Nonfinite POS effect")
        words.setdefault(a["word"], {}).setdefault(a["condition"], []).append(delta)
    overall = [np.mean([x for rows in word.values() for x in rows]) for word in words.values()]
    conditions = {}
    for i, condition in enumerate(sorted({r["condition"] for r in first})):
        values = [np.mean(word[condition]) for word in words.values() if condition in word]
        conditions[condition] = word_effect(values, iterations, seed + 10 + i)
    contrast = [np.mean(word["NOUN"]) - np.mean(word["VERB"]) for word in words.values() if "NOUN" in word and "VERB" in word]
    return {"items": len(first), "overall_word_balanced": word_effect(overall, iterations, seed),
            "conditions_word_balanced": conditions,
            "paired_within_word_NOUN_minus_VERB": word_effect(contrast, iterations, seed + 20),
            "ci_unit": "word form; evaluation uncertainty, not seed uncertainty",
            "sign": "first-minus-second NLL; negative favors first"}


def endpoint_status(directory):
    path = Path(directory) / "training_summary.json"
    if not path.exists():
        return {"ready": False, "reason": "missing training_summary.json"}
    try:
        run = read_json(path)
    except (OSError, json.JSONDecodeError) as error:
        return {"ready": False, "reason": "unreadable/in-progress summary: " + str(error)}
    complete = (run.get("status") == "complete" and run.get("step") == EXPECTED_STEP
                and run.get("planned_steps") == EXPECTED_STEP and run.get("train_tokens") == EXPECTED_TOKENS)
    required = ("provenance.json", "final_held_sequences.json", "dense_reference_held.json", "final_pos.json", "dense_reference_pos.json")
    missing = [name for name in required if not (Path(directory) / name).exists()]
    return {"ready": complete and not missing, "status": run.get("status"), "step": run.get("step"),
            "planned_steps": run.get("planned_steps"), "train_tokens": run.get("train_tokens"),
            "missing_files": missing, "reason": None if complete and not missing else "fixed endpoint or final artifacts not complete"}


def validate_pos_source(provenance, records):
    """Recover the training-time POS hash by reconstructing its signed config."""
    args = provenance["args"]
    path = Path(args["pos_items"]) if args.get("pos_items") else None
    if path is None or not path.exists():
        raise ValueError("POS source missing; cannot verify positional pairing")
    contents = path.read_bytes()
    source_hash = hashlib.sha256(contents).hexdigest()
    config = {"args": {key: value for key, value in args.items() if key not in OPERATIONAL},
              "data": provenance["data"], "frozen_sample_hash": provenance["frozen_sample_hash"],
              "initial_tensor_sha256": provenance["initial_tensor_sha256"], "pos_sha256": source_hash,
              "script_sha256": provenance["script_sha256"], "e123_sha256": provenance["e123_script_sha256"],
              "e124_sha256": provenance["e124_script_sha256"]}
    if digest(config) != provenance["config_hash"]:
        raise ValueError("Training config/POS source hash cannot be reproduced")
    source = [json.loads(line) for line in contents.decode().splitlines() if line.strip()]
    source = [r for r in source if r["split"] in ("held", "test", "eval")]
    expected = [(r.get("word", r.get("form", "unknown")), r.get("pos", r.get("label", "unknown"))) for r in source]
    if expected != [(r["word"], r["condition"]) for r in records]:
        raise ValueError("POS sequence order differs from the hashed source")
    return source_hash


def load_run(directory, label):
    directory = Path(directory)
    run, provenance = read_json(directory / "training_summary.json"), read_json(directory / "provenance.json")
    args = provenance["args"]
    if args["steps"] != EXPECTED_STEP or args["seq_len"] * args["batch_size"] * args["accum"] * args["steps"] != EXPECTED_TOKENS:
        raise ValueError("Provenance schedule is not the registered 128M endpoint")
    if (args["seq_len"], args["batch_size"], args["accum"], args["seed"], args["order_seed"], args["dtype"]) != (512, 16, 1, 0, 0, "bfloat16"):
        raise ValueError("Expected registered seq512/batch16/accum1/seed0/order0/BF16")
    if run["config_hash"] != provenance["config_hash"]:
        raise ValueError("Summary/provenance configuration hash differs")
    expected_kind = "dense" if label == "D-cover" else "moe"
    if run["replacement"] != expected_kind or provenance["replacement_kind"] != expected_kind:
        raise ValueError("Replacement kind differs from condition label")
    if run["frozen_sample_hash_before"] != run["frozen_sample_hash_after"] or run["frozen_sample_hash_after"] != provenance["frozen_sample_hash"]:
        raise ValueError("Frozen backbone hashes differ")
    if run["initial_tensor_sha256"] != provenance["initial_tensor_sha256"]:
        raise ValueError("Initial full tensor hash differs between run records")
    for value in (run["initial_tensor_sha256"], run["coverage"]["source_schedule_hash"]):
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("Missing/malformed full initialization or source-schedule SHA256")
    if run["coverage"]["drawn_windows"] != EXPECTED_STEP * args["batch_size"] * args["accum"]:
        raise ValueError("Exposure draw count differs from endpoint step")
    coverage = run["coverage"]
    if not (0 <= coverage["unique_windows"] <= min(coverage["drawn_windows"], coverage["available_windows"])):
        raise ValueError("Invalid unique-window count")
    if coverage["reused_windows"] != coverage["drawn_windows"] - coverage["unique_windows"] or not np.isclose(coverage["reuse_fraction"], 1 - coverage["unique_windows"] / coverage["drawn_windows"], atol=1e-12, rtol=0):
        raise ValueError("Exposure reuse count/rate do not agree")
    final, teacher = read_json(directory / "final_held_sequences.json"), read_json(directory / "dense_reference_held.json")
    files = {(r["source"], r["file_id"]): i for i, r in enumerate(provenance["data"]["held"])}
    window_indices = [(files[(row["source"], row["file_id"])], row["window"]) for row in final]
    if digest(window_indices) != provenance["held_window_hash"]:
        raise ValueError("Held sequence index hash differs from provenance")
    if len(final) != 512 or any(row["tokens"] != 512 for row in final):
        raise ValueError("Expected the original 512 held windows, each scoring 512 tokens")
    pos, teacher_pos = read_json(directory / "final_pos.json"), read_json(directory / "dense_reference_pos.json")
    pos_hash = validate_pos_source(provenance, pos)
    if [(r["word"], r["condition"]) for r in pos] != [(r["word"], r["condition"]) for r in teacher_pos]:
        raise ValueError("Teacher POS anchors differ")
    endpoints = [row for row in run["evaluations"] if row["step"] == EXPECTED_STEP]
    if not endpoints:
        raise ValueError("Full curve does not contain the final endpoint")
    final_mean = sum(row["nll_sum"] for row in final) / sum(row["tokens"] for row in final)
    if not np.isclose(final_mean, endpoints[-1]["held"]["sequence"]["mean"], rtol=0, atol=1e-10):
        raise ValueError("Final raw sequence losses do not match the fixed endpoint evaluation")
    return {"summary": run, "provenance": provenance, "final": final, "teacher": teacher,
            "pos": pos, "teacher_pos": teacher_pos, "pos_hash": pos_hash, "directory": str(directory.resolve())}


def conservative_interpretation(conditions, contrast):
    recovered = {key: value["held_teacher_gap"]["engineering_noninferiority"] for key, value in conditions.items()}
    effect, ci95, ci90 = contrast["difference_nats_first_minus_second"], contrast["ci95"], contrast["ci90"]
    improvement = effect <= -.03 and ci95[1] < 0
    reverse = effect >= .03 and ci95[0] > 0
    close = ci90[0] >= -.03 and ci90[1] <= .03
    if reverse:
        text = "M-small performs better than M-cover at the registered material-effect scale; report the reverse result without preserving the coverage hypothesis."
    elif recovered["M-small"] and recovered["M-cover"] and close:
        text = "Both MoE conditions recover and are close at this evaluation resolution. The old 32M schedule/exposure budget was insufficient; coverage alone is not identified as the cause."
    elif improvement and recovered["M-cover"]:
        text = "Coverage materially improves MoE held loss and M-cover passes the engineering recovery check. This supports repairing the platform with the coverage pool before a separate cross-seed study."
    elif improvement:
        text = "Coverage materially helps but M-cover has not recovered. This is a platform-learning limitation, not evidence for functional freedom; do not expand seeds yet."
    elif not recovered["M-small"] and not recovered["M-cover"] and recovered["D-cover"] and close:
        text = "The dense replacement recovers while both MoE conditions do not, with little resolved coverage effect. Investigate MoE optimization/granularity; different total parameter counts and auxiliary losses prevent a router-only attribution."
    elif not any(recovered.values()):
        text = "No replacement passes the engineering recovery check. Review the frozen-layer learning platform before interpreting organizational differences."
    else:
        text = "The registered comparisons do not resolve a single branch. Report all endpoint effects and coverage; neither nonsignificance nor partial recovery establishes equivalence or functional freedom."
    return {"engineering_recovery": recovered, "material_coverage_improvement": improvement,
            "material_reverse_effect": reverse, "evaluation_closeness_ci90_within_003": close,
            "reading": text, "decision_scope": "single initialization/order; conservative platform diagnostic, no automatic scientific decision"}


def summarize(directories, iterations=1000, seed=125):
    statuses = {name: endpoint_status(path) for name, path in directories.items()}
    output = {"experiment": "E125", "endpoint_status": statuses, "required_step": EXPECTED_STEP,
              "required_train_tokens": EXPECTED_TOKENS, "selection_rule": "fixed endpoint only; no intermediate best selection",
              "independent_initializations": 1, "file_and_word_intervals_are_not_seed_intervals": True}
    if not all(status["ready"] for status in statuses.values()):
        output.update({"status": "pending", "conclusion": None, "conditions": None, "curve": None})
        return output, None
    runs = {name: load_run(path, name) for name, path in directories.items()}
    a, b, d = [runs[name] for name in ("M-small", "M-cover", "D-cover")]
    if a["summary"]["initial_tensor_sha256"] != b["summary"]["initial_tensor_sha256"]:
        raise ValueError("M-small/M-cover full initial tensor hashes differ")
    source_hashes = {r["summary"]["coverage"]["source_schedule_hash"] for r in runs.values()}
    if len(source_hashes) != 1:
        raise ValueError("Source-choice schedules differ across conditions")
    for field in ("held_window_hash", "frozen_sample_hash", "original_file_probability_vector"):
        if any(r["provenance"][field] != a["provenance"][field] for r in runs.values()):
            raise ValueError(f"Cross-condition contract mismatch: {field}")
    for field in ("lr", "warmup_fraction", "weight_decay", "layer", "init_std", "grad_clip"):
        if any(r["provenance"]["args"][field] != a["provenance"]["args"][field] for r in runs.values()):
            raise ValueError(f"Cross-condition optimization/backbone mismatch: {field}")
    for field in ("experts", "expert_size", "top_k", "lb_coef", "z_coef"):
        if a["provenance"]["args"][field] != b["provenance"]["args"][field]:
            raise ValueError(f"MoE configuration mismatch: {field}")
    if len({r["pos_hash"] for r in runs.values()}) != 1:
        raise ValueError("POS source hashes differ across conditions")
    file_identity = lambda run: [(r["source"], r["file_id"]) for r in run["provenance"]["data"]["train"]]
    if any(file_identity(r) != file_identity(a) for r in runs.values()):
        raise ValueError("Original training source-file identities/order differ")
    held_identity = lambda run: [(r["source"], r["file_id"], r["sha256"], r["windows"]) for r in run["provenance"]["data"]["held"]]
    if any(held_identity(r) != held_identity(a) for r in runs.values()):
        raise ValueError("Held content hash/window pools differ")
    if [r["sha256"] for r in b["provenance"]["data"]["train"]] != [r["sha256"] for r in d["provenance"]["data"]["train"]]:
        raise ValueError("M-cover/D-cover token pools differ")
    conditions = {}
    for i, (name, run) in enumerate(runs.items()):
        gap = paired_file_bootstrap(run["final"], run["teacher"], iterations, seed + i)
        gap.update({"engineering_noninferiority": bool(not gap["ci_degenerate"] and gap["ci90"][1] <= .02),
                    "recovery_definition": "paired teacher-gap 90% bootstrap CI upper bound <= +0.02 nats; engineering noninferiority, not two-sided TOST equivalence"})
        coverage = run["summary"]["coverage"]
        conditions[name] = {"directory": run["directory"], "replacement": run["summary"]["replacement"],
                            "held_teacher_gap": gap,
                            "POS_teacher_gap": paired_pos(run["pos"], run["teacher_pos"], iterations, seed + 20 + i),
                            "coverage": {key: coverage[key] for key in ("drawn_windows", "unique_windows", "reused_windows", "reuse_fraction", "available_windows", "source_schedule_hash")},
                            "initial_full_tensor_sha256": run["summary"]["initial_tensor_sha256"],
                            "elapsed_wall_seconds": run["summary"].get("elapsed_wall_seconds"),
                            "held_source_coverage": sorted({row["source"] for row in run["final"]})}
    contrast = paired_file_bootstrap(b["final"], a["final"], iterations, seed + 50)
    cross = {"held_M_cover_minus_M_small": contrast,
             "POS_M_cover_minus_M_small": paired_pos(b["pos"], a["pos"], iterations, seed + 60),
             "dense_reference_max_sequence_NLL_drift_nats": float(max(abs(x["nll_sum"] / x["tokens"] - y["nll_sum"] / y["tokens"])
                 for run in runs.values() for x, y in zip(run["teacher"], a["teacher"])))}
    output.update({"status": "complete", "conditions": conditions, "comparisons": cross,
                   "contracts": {"source_schedule_hash_equal_all_three": True,
                                  "M_small_M_cover_full_initial_tensor_hash_equal": True,
                                  "held_inputs_and_content_hashes_equal": True, "POS_source_config_hashes_verified": True},
                   "conclusion": conservative_interpretation(conditions, contrast),
                   "interval_limit": "One initialization/order. Original-file and word bootstrap quantify evaluation sampling uncertainty only; no seed/generalization certification."})
    return output, runs


def draw_curve(runs, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.8), sharex=True)
    full_ax, zoom_ax = axes
    plot_data = {}
    all_y = []
    for name, run in runs.items():
        # Every recorded evaluation is retained; no smoothing or best-point pick.
        rows = run["summary"]["evaluations"]
        x = [r["step"] * 8192 / 1e6 for r in rows]
        y = [r["held"]["sequence"]["mean"] for r in rows]
        plot_data[name] = (x, y)
        all_y.extend(y)
    teacher = sum(r["nll_sum"] for r in runs["M-small"]["teacher"]) / sum(r["tokens"] for r in runs["M-small"]["teacher"])
    all_y.extend((teacher, teacher + .02))
    for ax in axes:
        for name, (x, y) in plot_data.items():
            ax.plot(x, y, marker=".", markersize=3, linewidth=1.4, label=name)
            ax.scatter(x[-1], y[-1], s=24)
        ax.axhline(teacher, color="black", linestyle="--", linewidth=1, label="Original dense")
        ax.axhline(teacher + .02, color="gray", linestyle=":", linewidth=1, label="Dense + 0.02 nats")
        ax.set_xlabel("Training target tokens (millions)")
        ax.grid(alpha=.2)
    full_ax.set_ylabel("Held next-token NLL (nats)")
    full_ax.set_title("Full y-range")
    full_ax.set_ylim(min(all_y) - .05, max(all_y) + .25)
    zoom_ax.set_title("Recovery region (zoom)")
    zoom_ax.set_ylim(2.45, 3.35)
    handles, labels = full_ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .96),
               ncol=5, fontsize=9, frameon=False)
    fig.suptitle("E125 frozen-layer recovery: all recorded evaluations", y=.995)
    fig.tight_layout(rect=(0, 0, 1, .89))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def self_test():
    a = [{"source": "s", "file_id": f"f{i // 2}", "window": i, "tokens": 512, "nll_sum": 1024.} for i in range(8)]
    b = [{**r, "nll_sum": r["nll_sum"] + 51.2} for r in a]
    check = paired_file_bootstrap(b, a, 100, 1)
    assert np.isclose(check["difference_nats_first_minus_second"], .1)
    assert np.allclose(check["ci90"], [.1, .1]) and np.allclose(check["ci95"], [.1, .1])
    wrong = [{**r} for r in a]
    wrong[0]["window"] = 999
    try:
        paired_file_bootstrap(b, wrong)
        raise AssertionError("Mismatched held keys were accepted")
    except ValueError:
        pass
    pos = [{"word": w, "condition": c, "nll": 2.} for w in ("work", "run") for c in ("NOUN", "VERB")]
    changed = [{**r, "nll": r["nll"] + (.1 if r["condition"] == "NOUN" else .3)} for r in pos]
    p = paired_pos(changed, pos, 100, 1)
    assert np.isclose(p["overall_word_balanced"]["mean"], .2)
    assert np.isclose(p["paired_within_word_NOUN_minus_VERB"]["mean"], -.2)
    with tempfile.TemporaryDirectory(prefix="e125_summary_test_") as directory:
        root = Path(directory)
        folders = {name: root / name for name in ("M-small", "M-cover", "D-cover")}
        for folder in folders.values():
            folder.mkdir()
            write_json(folder / "training_summary.json", {"status": "running", "step": 512,
                       "planned_steps": EXPECTED_STEP, "train_tokens": 512 * 8192})
        pending, runs = summarize(folders)
        assert pending["status"] == "pending" and pending["conclusion"] is None and runs is None
        # A summary claiming complete but short of the endpoint stays pending.
        write_json(folders["M-small"] / "training_summary.json", {"status": "complete", "step": 512,
                   "planned_steps": EXPECTED_STEP, "train_tokens": 512 * 8192})
        assert summarize(folders)[0]["status"] == "pending"
        # Hash validation is independently exercised without loading real runs.
        source = root / "pos.jsonl"
        source.write_text(json.dumps({"word": "work", "label": "NOUN", "split": "held"}) + "\n")
        provenance = {"args": {"pos_items": str(source)}, "data": {}, "frozen_sample_hash": "f",
                      "initial_tensor_sha256": "i", "script_sha256": "s", "e123_script_sha256": "a",
                      "e124_script_sha256": "b", "config_hash": "intentionally_wrong_hash"}
        try:
            validate_pos_source(provenance, [{"word": "work", "condition": "NOUN"}])
            raise AssertionError("Mismatched POS/config hash was accepted")
        except ValueError:
            pass
    print("E125 summary known-answer tests passed: signed paired effects/CIs, POS conditions, anchor/hash rejection, pending endpoints.")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--m-small", type=Path)
    p.add_argument("--m-cover", type=Path)
    p.add_argument("--d-cover", type=Path)
    p.add_argument("--output", type=Path, default=WB / "results/e125/three_condition_summary.json")
    p.add_argument("--figure", type=Path, default=WB / "results/e125/held_curve.png")
    p.add_argument("--bootstrap", type=int, default=1000)
    p.add_argument("--seed", type=int, default=125)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if any(path is None for path in (args.m_small, args.m_cover, args.d_cover)):
        p.error("All three output directories are required")
    if args.bootstrap < 1:
        p.error("--bootstrap must be positive")
    directories = {"M-small": args.m_small, "M-cover": args.m_cover, "D-cover": args.d_cover}
    try:
        result, runs = summarize(directories, args.bootstrap, args.seed)
        if runs is not None:
            draw_curve(runs, args.figure)
            result["curve"] = str(args.figure.resolve())
        result["summary_script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        write_json(args.output, result)
    except (ValueError, KeyError) as error:
        write_json(args.output, {"status": "invalid_contract", "conclusion": None,
                                "error": str(error), "no_intermediate_selection": True})
        raise
    print(json.dumps({"status": result["status"], "output": str(args.output), "conclusion": result.get("conclusion")}, indent=2))


if __name__ == "__main__":
    main()
