"""Independent NumPy audit of E141 raw sufficient statistics; no E141 imports/GPU."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WB = Path(__file__).resolve().parents[1]
PAIRS = ((0, 1), (0, 2), (1, 2))
MAIN = {"cohort_total_per_position": "total_SSE", "cohort_xor_per_position": "xor_SSE",
        "cohort_both_per_position": "both_SSE"}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()


def maxabs(value): return float(np.max(np.abs(value)))


def same(a, b, tolerance=1e-12):
    if a is None or b is None:
        if a is not None or b is not None: raise AssertionError((a, b))
        return 0.
    difference = abs(float(a) - float(b))
    if difference > max(tolerance, 1e-11 * max(abs(float(a)), abs(float(b)))):
        raise AssertionError((a, b, difference))
    return difference


def numbers(totals, positions, fields):
    field = {name: i for i, name in enumerate(fields)}
    result = {key: float(totals[:, field[column]].sum() / (9 * positions)) for key, column in MAIN.items()}
    for p, (left, right) in enumerate(PAIRS):
        stem = f"seed{left}_seed{right}/"; row = totals[p]; common = row[field["both_on_count"]]
        for name, column in field.items(): result[stem + name + "_per_position"] = float(row[column] / positions)
        result[stem + "both_f_SSE_per_common_on"] = float(row[field["both_f_SSE"]] / common) if common else None
        energy = row[field["both_f_left_energy"]] * row[field["both_f_right_energy"]]
        result[stem + "both_f_pooled_cosine"] = float(row[field["both_f_dot"]] / np.sqrt(energy)) if energy > 0 else None
        for name in ("both_w_left_sum", "both_w_right_sum", "both_w_delta_squared"):
            result[stem + name + "_per_common_on"] = float(row[field[name]] / common) if common else None
    return result


def check_group(name, record, report):
    if sha(record["raw"]) != record["raw_sha256"] or sha(record["metadata"]) != record["metadata_sha256"]:
        raise ValueError(f"{name}: E141 raw/metadata SHA differs")
    metadata = json.loads(Path(record["metadata"]).read_text()); fields = metadata["fields"]
    field = {label: i for i, label in enumerate(fields)}
    with np.load(record["raw"], allow_pickle=False) as archive: raw = np.array(archive["statistics"], copy=True)
    if raw.shape != (512, 64, 3, len(fields)) or not np.isfinite(raw).all(): raise ValueError(f"{name}: raw shape/finiteness differs")
    rows = metadata["rows"]; labels = list(dict.fromkeys((row["source"], row["file_id"]) for row in rows))
    if len(rows) != 512 or len(labels) != 32: raise ValueError(f"{name}: held population differs")
    groups = [np.flatnonzero([(row["source"], row["file_id"]) == label for row in rows]) for label in labels]
    positions = np.array([len(index) * 512 for index in groups]); grouped = np.stack([raw[index].sum((0, 1)) for index in groups])
    checks = {"support_partition": maxabs(raw[..., field["both_on_count"]] + raw[..., field["xor_count"]]
        + raw[..., field["neither_on_count"]] - 512),
        "left_right_counts": maxabs(raw[..., field["left_on_count"]] + raw[..., field["right_on_count"]]
            - 2 * raw[..., field["both_on_count"]] - raw[..., field["xor_count"]]),
        "pair_SSE_partition": maxabs(raw[..., field["total_SSE"]] - raw[..., field["xor_SSE"]] - raw[..., field["both_SSE"]]),
        "common_f_distance": maxabs(raw[..., field["both_f_SSE"]] - raw[..., field["both_f_left_energy"]]
            - raw[..., field["both_f_right_energy"]] + 2 * raw[..., field["both_f_dot"]]),
        "FP64_gate_content_cross": maxabs(raw[..., field["ideal_product_delta_SSE"]] - raw[..., field["gate_term_SSE"]]
            - raw[..., field["content_term_SSE"]] - raw[..., field["gate_content_cross"]]),
        "actual_BF16_ideal_floor": maxabs(raw[..., field["both_SSE"]] - raw[..., field["ideal_product_delta_SSE"]]
            - raw[..., field["product_floor_delta_SSE"]] - raw[..., field["ideal_floor_cross"]]),
        "recorded_scalar_residual": maxabs(raw[..., field["actual_ideal_floor_scalar_residual"]]
            - (raw[..., field["both_SSE"]] - raw[..., field["ideal_product_delta_SSE"]]
                - raw[..., field["product_floor_delta_SSE"]] - raw[..., field["ideal_floor_cross"]]))}
    source = json.loads(Path(metadata["descriptor"]["readout"]).read_text())
    reference = source
    for key in metadata["descriptor"]["components_path"]: reference = reference[key]
    if sha(reference["raw"]) != reference["raw_sha256"] or sha(reference["metadata"]) != reference["metadata_sha256"]:
        raise ValueError(f"{name}: original E139/E140 component raw source SHA differs")
    with np.load(reference["raw"], allow_pickle=False) as archive: old = np.array(archive["expert"], copy=True)
    old_fields = json.loads(Path(reference["metadata"]).read_text())["expert_fields"]
    checks["original_pair_SSE"] = max(maxabs(raw[:, :, p, field["total_SSE"]]
        - old[:, :, old_fields.index(f"pair_seed{left}_seed{right}_SSE")]) for p, (left, right) in enumerate(PAIRS))
    checks["original_cohort_variance"] = maxabs(raw[..., field["total_SSE"]].sum(2) / 9
        - old[:, :, old_fields.index("cohort_variance")])
    if name == "fixed" and (np.any(raw[..., field["xor_count"]] != 0) or np.any(raw[..., field["xor_SSE"]] != 0)):
        raise AssertionError("Fixed common gate/identity map has nonzero XOR")
    if max(checks.values()) > 1e-8: raise AssertionError(f"{name}: raw closure failed: {checks}")
    point = numbers(raw.sum((0, 1)), 262144, fields)
    expected = record["summary"]["global"]
    if set(point) != set(expected): raise AssertionError(f"{name}: global field set differs")
    point_error = max(same(value, expected[key]["point"]) for key, value in point.items())
    draws = np.random.default_rng(141).integers(0, len(groups), (1000, len(groups)))
    bootstrap = [numbers(grouped[draw].sum(0), positions[draw].sum(), fields) for draw in draws]
    interval_error, withheld = 0., 0
    for key in point:
        valid = [sample[key] for sample in bootstrap if sample[key] is not None and np.isfinite(sample[key])]
        if len(valid) != expected[key]["defined_draws"]: raise AssertionError(f"{name}: defined draw count differs: {key}")
        interval = np.quantile(valid, [.025, .975]).tolist() if point[key] is not None and len(valid) == 1000 else None
        if interval is None: withheld += 1
        for left, right in zip(interval or [], expected[key]["ci95"] or []): interval_error = max(interval_error, same(left, right))
        if (interval is None) != (expected[key]["ci95"] is None): raise AssertionError(f"{name}: CI withholding differs: {key}")
    table = record["summary"]["per_expert"]
    if len(table) != 64: raise AssertionError(f"{name}: expert table length differs")
    table_error = 0.
    for expert in range(64):
        if table[expert]["seed1_coordinate"] != expert: raise AssertionError(f"{name}: canonical expert order differs")
        for p, (left, right) in enumerate(PAIRS):
            prior = table[expert]["pairs"][f"seed{left}_seed{right}"]; totals = raw[:, expert, p].sum(0)
            for label, value in zip(fields, totals): table_error = max(table_error, same(value, prior["raw_totals"][label], 1e-9))
            recomputed = numbers(np.stack([totals] * 3), 262144, fields)
            stem = f"seed{left}_seed{right}/"
            for key, value in prior["statistics"].items(): table_error = max(table_error, same(recomputed[stem + key], value))
    return {"rows": rows, "fields": fields, "grouped": grouped, "positions": positions,
        "checks": checks, "point": point, "point_max_abs_error": point_error,
        "bootstrap_ci_max_abs_error": interval_error, "expert_table_max_abs_error": table_error,
        "audited_global_metrics": len(point), "audited_expert_pair_tables": 64 * 3, "withheld_global_intervals": withheld,
        "original_component_raw_sha256": sha(reference["raw"])}


def run(args):
    report = json.loads(args.summary.read_text())
    if report.get("experiment") != "E141" or report.get("status") != "complete" or report.get("errors") or set(report["groups"]) != {"free", "fixed", "warm"}:
        raise ValueError("Complete error-free E141 three-group raw required")
    audits = {name: check_group(name, report["groups"][name], report) for name in ("free", "fixed", "warm")}
    first = audits["free"]
    if any(audits[name]["rows"] != first["rows"] or not np.array_equal(audits[name]["positions"], first["positions"])
            for name in ("fixed", "warm")): raise AssertionError("Groups do not share exact held file rows/clusters")
    draws = np.random.default_rng(141).integers(0, len(first["positions"]), (1000, len(first["positions"])))
    contrasts = {}
    for left, right in (("free", "fixed"), ("warm", "fixed"), ("warm", "free")):
        key = f"{left}_minus_{right}"; contrasts[key] = {}
        for metric, column in MAIN.items():
            field = audits[left]["fields"].index(column)
            left_draw = audits[left]["grouped"][draws, :, field].sum((1, 2)) / (9 * audits[left]["positions"][draws].sum(1))
            right_draw = audits[right]["grouped"][draws, :, field].sum((1, 2)) / (9 * audits[right]["positions"][draws].sum(1))
            point = audits[left]["point"][metric] - audits[right]["point"][metric]
            stated = report["contrasts"][key][metric]
            point_error = same(point, stated["point"])
            ci = np.quantile(left_draw - right_draw, [.025, .975]).tolist()
            ci_error = max(same(a, b) for a, b in zip(ci, stated["paired_file_ci95"]))
            contrasts[key][metric] = {"point": point, "paired_file_ci95": ci,
                "point_abs_error": point_error, "ci_max_abs_error": ci_error}
    output = {"experiment": "E141", "status": "complete", "method": "Independent NumPy recomputation from immutable raw NPZ; no import from E141 statistics source, no GPU/model forward.",
        "source_summary": str(args.summary), "source_summary_sha256": sha(args.summary),
        "scope": "Finite fixed three-student cohorts and original held 512 sequences/32 file clusters. CI resamples input files with identical 1000 seed141 draws across groups; not seed-level or causal treatment uncertainty. Support XOR and both-on are descriptive actual contributions, not mask interventions. Matched seed1 coordinates and fixed maps are inherited from E139/E140.",
        "groups": {name: {key: value for key, value in audit.items() if key not in ("rows", "fields", "grouped", "positions", "point")}
            | {"main_points": {metric: audit["point"][metric] for metric in MAIN}}
            for name, audit in audits.items()},
        "paired_contrasts": contrasts}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"status": output["status"], "source_summary_sha256": output["source_summary_sha256"],
        "groups": {name: audit["main_points"] for name, audit in output["groups"].items()},
        "max_global_ci_error": max(audit["bootstrap_ci_max_abs_error"] for audit in output["groups"].values())}, allow_nan=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=WB / "results/e141/support_partition.json")
    parser.add_argument("--output", type=Path, default=WB / "results/e141/independent_audit.json")
    run(parser.parse_args())
