"""E130 held-word cluster intervals, conditional on the saved cal-U mapping/offsets."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import e124_compare as comparison
import e130_analyze as analysis

WB = Path(__file__).resolve().parents[1]
ITERATIONS, SEED, FLOOR = 999, 131, 1e-8


def sufficient(x, y, words):
    labels = np.unique(words)
    blocks = [np.flatnonzero(words == word) for word in labels]
    counts = np.array([len(rows) for rows in blocks], dtype=float)
    sums = np.stack([np.stack([x[r].sum(0), y[r].sum(0), (x[r]**2).sum(0),
                              (y[r]**2).sum(0), (x[r]*y[r]).sum(0)]) for r in blocks])
    return counts, sums, labels


def from_counts(weights, counts, sums):
    n = (weights @ counts)[:, None]
    sx, sy, xx, yy, xy = np.moveaxis(np.einsum("dw,wke->dke", weights, sums), 1, 0)
    vx, vy = np.maximum(xx/n - (sx/n)**2, 0), np.maximum(yy/n - (sy/n)**2, 0)
    valid = (np.sqrt(vx) > FLOOR) & (np.sqrt(vy) > FLOOR)
    rho = np.full_like(vx, np.nan)
    np.divide(xy/n - sx*sy/n**2, np.sqrt(vx*vy), out=rho, where=valid)
    rho = np.clip(rho, -1, 1)
    number = valid.sum(1)
    mean = np.full(len(number), np.nan)
    np.divide(np.nansum(rho, axis=1), number, out=mean, where=number > 0)
    return mean, valid


def interval(x, y, words):
    counts, sums, labels = sufficient(x, y, words)
    observed, observed_valid = from_counts(np.ones((1, len(labels))), counts, sums)
    draws = np.random.default_rng(SEED).integers(0, len(labels), (ITERATIONS, len(labels)))
    weights = np.stack([np.bincount(draw, minlength=len(labels)) for draw in draws])
    values, valid = from_counts(weights, counts, sums)
    changed = np.any(valid != observed_valid, axis=1)
    finite = np.isfinite(values)
    comparable = bool(finite.all() and not changed.any() and np.isfinite(observed[0]))
    unique, frequencies = np.unique(valid.sum(1), return_counts=True)
    return {"observed_mean": float(observed[0]) if np.isfinite(observed[0]) else None,
            "ci95": np.quantile(values, [.025, .975]).tolist() if comparable else None,
            "held_words": len(labels), "held_items": int(counts.sum()),
            "mapped_columns": x.shape[1], "observed_valid_columns": int(observed_valid.sum()),
            "observed_valid_mapping_positions": np.flatnonzero(observed_valid[0]).tolist(),
            "bootstrap_draws": ITERATIONS, "finite_draws": int(finite.sum()),
            "undefined_draws": int((~finite).sum()), "coverage_change_draws": int(changed.sum()),
            "valid_column_count_histogram": {str(int(k)): int(v) for k, v in zip(unique, frequencies)},
            "coverage_comparable": comparable,
            "interval_note": "Fixed cal offsets/mapping; no rematching. CI withheld if a draw is undefined or changes the valid-column target; no draws or words deleted."}


def self_test():
    rng = np.random.default_rng(61)
    x = rng.normal(size=(12, 3)); y = x * np.array([1., -1., .3]) + rng.normal(size=(12, 3)) * .2
    x[:, 2] = y[:, 2] = 4  # Preserve a genuinely undefined column.
    words = np.array(["a"]*2 + ["b"]*4 + ["c"]*6)
    counts, sums, labels = sufficient(x, y, words)
    errors = []
    for draw in ([0, 0, 2], [2, 1, 2]):
        observed, valid = from_counts(np.bincount(draw, minlength=3)[None, :], counts, sums)
        rows = np.concatenate([np.flatnonzero(words == labels[i]) for i in draw])
        xc, yc = x[rows]-x[rows].mean(0), y[rows]-y[rows].mean(0)
        direct = (xc[:, :2]*yc[:, :2]).sum(0) / np.sqrt((xc[:, :2]**2).sum(0)*(yc[:, :2]**2).sum(0))
        errors.append(float(abs(observed[0]-direct.mean())))
        assert np.array_equal(valid[0], [True, True, False]) and errors[-1] < 1e-12
    assert interval(x[:, 2:], y[:, 2:], words)["ci95"] is None
    return {"passed": True, "brute_resample_two_draw_max_errors": errors, "undefined_column_preserved": True}


def evaluate(args):
    summary_bytes = args.summary.read_bytes()
    summary = json.loads(summary_bytes)
    frozen = {"analysis": analysis.assets.sha(Path(analysis.__file__)),
              "comparison": analysis.assets.sha(Path(comparison.__file__))}
    if (summary["analysis_script_sha256"] != frozen["analysis"]
            or summary["comparison_script_sha256"] != frozen["comparison"]):
        raise ValueError("Saved analysis/comparator source SHA differs")
    cache, pairs = {}, {}

    def load(side, expected_metadata):
        path = Path(side["path"])
        if path not in cache:
            if analysis.assets.sha(path) != side["sha256"]:
                raise ValueError(f"Capture SHA differs: {path}")
            capture = comparison.load_capture(path)
            if capture["metadata"]["script_sha256"] != analysis.assets.FROZEN["e124_functional_capture.py"]:
                raise ValueError("Capture source SHA differs")
            cache[path] = (capture, side["sha256"])
        capture, checksum = cache[path]
        if checksum != side["sha256"] or capture["metadata"] != expected_metadata:
            raise ValueError("Saved pair metadata differs from the immutable capture")
        for name, key in (("provenance.json", "provenance_sha256"), ("training_summary.json", "training_summary_sha256")):
            if analysis.assets.sha(path.parent / name) != side[key]:
                raise ValueError("Saved training provenance SHA differs")
        return capture

    for kind, a, alabel, b, blabel in analysis.planned_pairs():
        pair_id = f"{a}_{alabel}__{b}_{blabel}"
        original = summary["pairs"].get(pair_id, {})
        pairs[pair_id] = {"status": original.get("status", "missing"), "kind": kind}
        if original.get("status") != "complete":
            continue
        path = args.summary.parent / "comparison/batch" / f"{pair_id}.json"
        pair = json.loads(path.read_text()); identity = pair["batch_identity"]
        if (pair["status"] != "complete" or pair["pair_id"] != pair_id
                or identity["analysis_script_sha256"] != frozen["analysis"]
                or identity["comparison_script_sha256"] != frozen["comparison"]
                or pair["variance_floor_nats"] != FLOOR or identity["parameters"] != analysis.PARAMETERS):
            raise ValueError("Saved pair source/identity/parameters differ")
        first, second = [load(identity[side], pair["identity"]["metadata_"+side]) for side in ("A", "B")]
        if any(not np.array_equal(first[k], second[k]) for k in ("item_id", "input_sha256", "word", "split")):
            raise ValueError("Fixed input identities differ")
        mapping = pair["mapping_A_to_B"]
        ia = np.array([i for i, j in enumerate(mapping) if j is not None], dtype=int)
        ib = np.array([mapping[i] for i in ia], dtype=int)
        if len(ia) != pair["n_matched_columns"] or len(set(ib)) != len(ib):
            raise ValueError("Saved cal-U assignment is not one-to-one")
        cal, held, words = first["split"] == "cal", first["split"] == "held", first["word"]
        result = {"status": "complete", "kind": kind, "pair_file_sha256": analysis.assets.sha(path),
                  "capture_sha256": {side: identity[side]["sha256"] for side in ("A", "B")}, "function": {}}
        for key in ("U", "A"):
            x, hx, _ = comparison.residualize(first[key], words, cal, held)
            y, hy, _ = comparison.residualize(second[key], words, cal, held)
            use = hx & hy
            value = interval(x[use][:, ia], y[use][:, ib], words[use])
            saved = pair["function"][key]["held_conditional_columns"]
            if value["observed_valid_columns"] != saved["n_valid_columns"]:
                raise ValueError("Independent sufficient-statistic valid-column coverage differs")
            if (value["observed_mean"] is None) != (saved["mean"] is None) or (saved["mean"] is not None
                    and not np.isclose(value["observed_mean"], saved["mean"], atol=1e-12, rtol=1e-12)):
                raise ValueError("Sufficient-statistic point estimate differs from saved result")
            result["function"][key] = value
        pairs[pair_id] = result
    completed = sum(p["status"] == "complete" for p in pairs.values())
    result = {"experiment": "E130", "status": "complete" if completed == 17 else "partial",
              "completed_pairs": completed, "expected_pairs": 17, "iterations": ITERATIONS, "seed": SEED,
              "variance_floor_nats": FLOOR, "source_sha256": analysis.assets.sha(__file__),
              "batch_summary_sha256": hashlib.sha256(summary_bytes).hexdigest(), "frozen_sources": frozen,
              "scope": "Registered held-word cluster measurement uncertainty conditional on cal offsets and cal-U assignment; not a seed CI or a CI over ten dependent seed pairs.",
              "pairs": pairs}
    analysis.assets.write(args.output, result)
    return {k: result[k] for k in ("status", "completed_pairs", "expected_pairs", "source_sha256")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--summary", type=Path, default=WB / "results/e130/batch_summary.json")
    parser.add_argument("--output", type=Path, default=WB / "results/e130/evaluation_uncertainty.json")
    args = parser.parse_args()
    print(json.dumps(self_test() if args.self_test else evaluate(args), allow_nan=False))
