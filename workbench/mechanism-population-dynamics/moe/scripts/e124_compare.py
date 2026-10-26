"""CPU-only E124 function matching. Run real captures only after the E123 gate.

Input contract: U/A (N,E), word/split/input_sha256 (N), item_id (N),
metadata_json (scalar JSON); optional selected_mask and gate_weights (N,E).
No model forward. No routing N1 calculation is performed by this script.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment


def correlation_matrix(a, b, floor):
    """Pairwise column Pearson on common rows; zero-variance columns are invalid."""
    ac, bc = a - a.mean(0), b - b.mean(0)
    sa, sb = np.sqrt((ac * ac).mean(0)), np.sqrt((bc * bc).mean(0))
    va, vb = sa > floor, sb > floor
    matrix = np.full((a.shape[1], b.shape[1]), np.nan)
    if va.any() and vb.any():
        matrix[np.ix_(va, vb)] = np.clip(
            ac[:, va].T @ bc[:, vb] / len(a) / (sa[va, None] * sb[None, vb]), -1, 1)
    return matrix, va, vb


def match_columns(a, b, floor):
    matrix, va, vb = correlation_matrix(a, b, floor)
    ia, ib = np.flatnonzero(va), np.flatnonzero(vb)
    if not len(ia) or not len(ib):
        return np.empty(0, dtype=int), np.empty(0, dtype=int), va, vb
    row, col = linear_sum_assignment(-matrix[np.ix_(ia, ib)])
    return ia[row], ib[col], va, vb


def residualize(values, words, cal, held):
    # Row centering does not fit any held parameter; word offsets use cal only.
    centered = values - values.mean(1, keepdims=True)
    offsets = {word: centered[cal & (words == word)].mean(0) for word in np.unique(words[cal])}
    covered = np.array([word in offsets for word in words])
    result = np.full_like(centered, np.nan, dtype=float)
    for word, offset in offsets.items():
        rows = words == word
        result[rows] = centered[rows] - offset
    use_held = held & covered
    return result, use_held, {"cal_words": len(offsets), "held_items_total": int(held.sum()),
                             "held_items_covered": int(use_held.sum()),
                             "held_word_coverage": float(len(set(words[use_held])) / max(1, len(set(words[held])))),
                             "missing_held_words": sorted(set(words[held]) - set(offsets))}


def column_scores(a, b, ia, ib, floor):
    if not len(ia) or len(a) < 2:
        return {"mean": None, "median": None, "n_valid_columns": 0,
                "column_rho": [], "valid_mapping_positions": []}
    x, y = a[:, ia], b[:, ib]
    xc, yc = x - x.mean(0), y - y.mean(0)
    sx, sy = np.sqrt((xc * xc).mean(0)), np.sqrt((yc * yc).mean(0))
    valid = (sx > floor) & (sy > floor)
    rho = np.full(len(ia), np.nan)
    rho[valid] = np.clip((xc[:, valid] * yc[:, valid]).mean(0) / (sx[valid] * sy[valid]), -1, 1)
    good = rho[valid]
    return {"mean": float(good.mean()) if len(good) else None,
            "median": float(np.median(good)) if len(good) else None,
            "n_valid_columns": len(good), "column_rho": [float(x) if np.isfinite(x) else None for x in rho],
            "valid_mapping_positions": np.flatnonzero(valid).tolist()}


def raw_difference(a, b, ia, ib):
    if not len(ia) or not len(a):
        return None
    difference = a[:, ia] - b[:, ib]
    return {"signed_mean_nats_A_minus_B": float(difference.mean()),
            "mean_absolute_difference_nats": float(np.abs(difference).mean()),
            "rmse_nats": float(np.sqrt(np.square(difference).mean())),
            "per_expert_signed_mean_nats": difference.mean(0).tolist(),
            "raw_mean_A_nats": float(a[:, ia].mean()), "raw_mean_B_nats": float(b[:, ib].mean())}


def reference_summary(scores, observed):
    valid = [s["mean"] for s in scores if s["mean"] is not None]
    counts = [s["n_valid_columns"] for s in scores]
    comparable = bool(observed["mean"] is not None and len(valid) == len(scores)
                      and len(scores) > 0 and all(c == observed["n_valid_columns"] for c in counts))
    return {"n_draws": len(scores), "n_finite_scores": len(valid),
            "mean_rho_q025_q50_q975": np.quantile(valid, [.025, .5, .975]).tolist() if valid else [],
            "valid_column_count_range": [min(counts), max(counts)] if counts else [],
            "coverage_comparable": comparable,
            "reference_tail_probability_greater": float((1 + sum(v >= observed["mean"] for v in valid)) / (len(valid) + 1)) if comparable else None,
            "tail_note": "Conditional calibration/random-mapping reference, not independent-seed significance; withheld for undefined scores or changing coverage."}


def compare(a, b, permutations=199, random_maps=199, seed=124, min_std=1e-8):
    for key in ("item_id", "input_sha256", "word", "split"):
        if not np.array_equal(a[key], b[key]):
            raise ValueError(f"Capture anchors/order differ: {key}")
    if a["U"].shape != b["U"].shape or a["A"].shape != a["U"].shape or b["A"].shape != b["U"].shape:
        raise ValueError("U/A dimensions differ")
    if any(not np.isfinite(run[key]).all() for run in (a, b) for key in ("U", "A")):
        raise ValueError("Nonfinite U/A; retain failure rather than silently select entries")
    words, split = np.asarray(a["word"]), np.asarray(a["split"])
    cal, held = split == "cal", split == "held"
    if cal.sum() < 2 or held.sum() < 2:
        raise ValueError("Need at least two fixed cal and held samples")
    residuals = {}
    coverage = {}
    for who, run in (("A", a), ("B", b)):
        for key in ("U", "A"):
            residuals[who, key], use, cov = residualize(run[key], words, cal, held)
            coverage[f"{who}_{key}"] = cov
            if "shared_held" not in residuals:
                residuals["shared_held"] = use
            else:
                residuals["shared_held"] &= use
    h = residuals["shared_held"]
    if h.sum() < 2:
        raise ValueError("Insufficient held coverage from cal words")
    uac, ubc = residuals["A", "U"][cal], residuals["B", "U"][cal]
    ia, ib, va, vb = match_columns(uac, ubc, min_std)
    E = a["U"].shape[1]
    mapping = [None] * E
    for i, j in zip(ia, ib):
        mapping[int(i)] = int(j)
    result = {"mapping_A_to_B": mapping, "cal_valid_U_columns_A": int(va.sum()),
              "cal_valid_U_columns_B": int(vb.sum()), "n_matched_columns": len(ia),
              "n_experts": E, "coverage": coverage, "n_cal_items": int(cal.sum()),
              "n_held_items_evaluated": int(h.sum()), "n_held_words": len(set(words[h])),
              "variance_floor_nats": min_std, "variance_floor_note": "Numeric/configured floor only; compare conditional strength against separately measured intervention noise before a scientific conclusion.",
              "function": {}}
    rng_shuffle, rng_random = np.random.default_rng(seed), np.random.default_rng(seed + 1)
    cal_words = words[cal]
    groups = [np.flatnonzero(cal_words == word) for word in np.unique(cal_words)]
    shuffle_maps = []
    for _ in range(permutations):
        order = np.arange(len(ubc))
        for group in groups:
            order[group] = rng_shuffle.permutation(group)
        si, sj, _, _ = match_columns(uac, ubc[order], min_std)
        shuffle_maps.append((si, sj))
    random_mapping = []
    ai, bi = np.flatnonzero(va), np.flatnonzero(vb)
    for _ in range(random_maps):
        n = min(len(ai), len(bi))
        random_mapping.append((rng_random.permutation(ai)[:n], rng_random.permutation(bi)[:n]))
    for key in ("U", "A"):
        ar, br = residuals["A", key][h], residuals["B", key][h]
        observed = column_scores(ar, br, ia, ib, min_std)
        observed["effective_column_fraction_of_all_experts"] = observed["n_valid_columns"] / E
        result["function"][key] = {
            "held_conditional_columns": observed,
            "raw_effect_difference_under_cal_U_mapping": raw_difference(a[key][h], b[key][h], ia, ib),
            "raw_unaligned_effect_summary_nats": {
                "A_mean": float(a[key][h].mean()), "B_mean": float(b[key][h].mean()),
                "A_rms": float(np.sqrt(np.square(a[key][h]).mean())),
                "B_rms": float(np.sqrt(np.square(b[key][h]).mean()))},
            "conditional_strength_nats": {"A_cal_rms": float(np.sqrt(np.square(residuals["A", key][cal]).mean())),
                                            "B_cal_rms": float(np.sqrt(np.square(residuals["B", key][cal]).mean())),
                                            "A_held_rms": float(np.sqrt(np.square(ar).mean())),
                                            "B_held_rms": float(np.sqrt(np.square(br).mean()))},
            "cal_word_shuffle_rematch_reference": reference_summary(
                [column_scores(ar, br, si, sj, min_std) for si, sj in shuffle_maps], observed),
            "random_mapping_reference": reference_summary(
                [column_scores(ar, br, si, sj, min_std) for si, sj in random_mapping], observed)}
    result["interpretation"] = "U is signed common-dense-probe action; A includes natural route availability/weights. Column shape correlations do not imply equal effect size or all natural responsibilities. Undefined fingerprints are unmeasurable, not evidence of reorganization."
    return result


def load_capture(path):
    required = ("U", "A", "word", "split", "input_sha256", "item_id")
    with np.load(path, allow_pickle=False) as data:
        result = {key: np.asarray(data[key], dtype=float if key in ("U", "A") else None) for key in required}
        result["metadata"] = json.loads(str(data["metadata_json"]))
        if not np.isclose(result["metadata"].get("alpha", np.nan), .125):
            raise ValueError("Capture must declare the fixed U injection alpha=1/8")
    return result


def comparison_identity(a, b, override):
    ma, mb = a.get("metadata", {}), b.get("metadata", {})
    sa, sb = ma.get("seed"), mb.get("seed")
    oa, ob = ma.get("order_seed"), mb.get("order_seed")
    if override != "auto":
        kind = override
    elif ma.get("step") == 0 or mb.get("step") == 0:
        kind = "initialization_reference"
    elif sa is None or sb is None:
        kind = "unknown"
    elif sa != sb:
        kind = "different_initializations"
    elif oa != ob:
        kind = "same_seed_different_order_reference"
    elif ma.get("step") != mb.get("step"):
        kind = "same_seed_checkpoint_reference"
    else:
        kind = "same_seed_rerun_or_identity_reference"
    return {"kind": kind, "metadata_A": ma, "metadata_B": mb,
            "independent_seed_pair_count": None,
            "sampling_unit_note": "Independent initializations are the unit; pairwise comparisons share seeds. Same-seed, initialization, and checkpoint references are not additional independent-seed replications."}


def self_test():
    rng = np.random.default_rng(18)
    n, e = 160, 6
    words = np.array([f"w{i % 8}" for i in range(n)])
    split = np.array(["cal"] * 80 + ["held"] * 80)
    conditional = rng.normal(size=(n, 4)) @ rng.normal(size=(4, e))
    word_effect = rng.normal(size=(8, e)) * 10
    raw = conditional + word_effect[np.arange(n) % 8] + rng.normal(size=(n, 1)) * 3
    base = {"U": raw, "A": raw * .3, "word": words, "split": split,
            "item_id": np.arange(n), "input_sha256": np.array([f"h{i}" for i in range(n)])}
    permutation = rng.permutation(e)
    other = dict(base, U=raw[:, permutation], A=raw[:, permutation] * .3)
    result = compare(base, other, permutations=9, random_maps=9)
    for key in ("U", "A"):
        assert np.isclose(result["function"][key]["held_conditional_columns"]["mean"], 1)
        assert result["function"][key]["raw_effect_difference_under_cal_U_mapping"]["rmse_nats"] < 1e-10
    assert result["mapping_A_to_B"] == np.argsort(permutation).tolist()
    identical = dict(base, U=np.repeat(raw[:, :1], e, axis=1), A=np.repeat(raw[:, :1], e, axis=1))
    null = compare(identical, identical, permutations=9, random_maps=9)
    assert null["n_matched_columns"] == 0
    for key in ("U", "A"):
        score = null["function"][key]
        assert score["held_conditional_columns"]["mean"] is None
        assert score["held_conditional_columns"]["n_valid_columns"] == 0
        assert score["cal_word_shuffle_rematch_reference"]["reference_tail_probability_greater"] is None
    # A per-position common shift must not alter conditional matching, but raw
    # effects must expose its magnitude. Held data never changes the mapping.
    shifted = dict(other, U=other["U"] + 4, A=other["A"] - 2)
    check = compare(base, shifted, permutations=0, random_maps=0)
    assert np.isclose(check["function"]["U"]["held_conditional_columns"]["mean"], 1)
    assert np.isclose(check["function"]["U"]["raw_effect_difference_under_cal_U_mapping"]["rmse_nats"], 4)
    altered = dict(other, U=other["U"].copy())
    altered["U"][split == "held"] = rng.normal(size=(80, e))
    assert compare(base, altered, permutations=0, random_maps=0)["mapping_A_to_B"] == result["mapping_A_to_B"]
    print("E124 NumPy/SciPy known-answer tests passed: permutation recovery, zero fingerprint, raw-strength separation, held isolation.")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--a", type=Path)
    p.add_argument("--b", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--permutations", type=int, default=199)
    p.add_argument("--random-maps", type=int, default=199)
    p.add_argument("--seed", type=int, default=124)
    p.add_argument("--min-std-nats", type=float, default=1e-8)
    p.add_argument("--comparison-kind", default="auto", choices=("auto", "different_initializations", "same_seed_rerun_reference", "same_seed_different_order_reference", "same_seed_checkpoint_reference", "initialization_reference", "unknown"))
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if any(v is None for v in (args.a, args.b, args.output)):
        p.error("--a, --b and --output are required")
    if min(args.permutations, args.random_maps) < 0 or args.min_std_nats < 0:
        p.error("Reference counts and variance floor must be nonnegative")
    a, b = load_capture(args.a), load_capture(args.b)
    result = compare(a, b, args.permutations, args.random_maps, args.seed, args.min_std_nats)
    result.update({"identity": comparison_identity(a, b, args.comparison_kind),
                   "capture_A": str(args.a.resolve()), "capture_B": str(args.b.resolve()),
                   "reference_seed": args.seed, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "routing_N1": "Not calculated: this CPU script implements the signed-function matching contract only."})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
