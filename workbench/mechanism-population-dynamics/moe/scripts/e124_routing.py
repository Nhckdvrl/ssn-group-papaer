#!/usr/bin/env python3
"""Compare fixed-held, same-word MoE routing pairs with the validated N1 null.

No model forward is performed. Inputs are per-seed captures containing the
L9 router inputs, gate matrix, word labels, and cal/held labels. Hcal is loaded
separately from the frozen dense backbone. N1 is delegated to moe_measure.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

import moe_measure as mm

N_EXPERTS = 64
HIDDEN_SIZE = 2048
TOP_K = 8
N1_DRAWS = 32
N1_SEED = 124
FP16_ATOL = 1e-3
FP16_RTOL = 1e-3
STD_FLOOR = 1e-8
MIN_PAIRS_PER_WORD = 3
DEFAULT_CACHE = Path("/home/xiang/mechpop_cache/e124_routing")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _first_key(z, keys, required=True):
    for key in keys:
        if key in z:
            return np.asarray(z[key]).copy()
    if required:
        raise KeyError(f"Capture missing one of required keys: {keys}")
    return None


def load_capture(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        htarget = _first_key(z, ("Htarget", "H_target", "htarget"))
        gate = _first_key(z, ("gate", "gate_weight", "router_weight", "W"))
        word = _first_key(z, ("word", "words"))
        split = _first_key(z, ("split", "splits"))
        item_id = _first_key(z, ("item_id", "item_ids", "input_id", "input_ids"))
        anchor_hash = _first_key(z, ("input_sha256", "anchor_sha256", "input_hash"))
        bias = _first_key(z, ("gate_bias", "bias", "b"), required=False)
        hcal_in_capture = _first_key(z, ("Hcal", "hcal", "H_cal"), required=False)
        metadata_json = _first_key(z, ("metadata_json",))

    htarget = np.asarray(htarget, dtype=np.float32)
    gate = np.asarray(gate, dtype=np.float32)
    word = np.asarray(word).astype(str)
    split = np.asarray(split).astype(str)
    anchor_hash = np.asarray(anchor_hash).astype(str)
    if htarget.ndim != 2 or htarget.shape[1] != HIDDEN_SIZE:
        raise ValueError(f"{path}: Htarget must have shape (N,{HIDDEN_SIZE}), got {htarget.shape}")
    if gate.shape != (N_EXPERTS, HIDDEN_SIZE):
        raise ValueError(f"{path}: gate must have shape ({N_EXPERTS},{HIDDEN_SIZE}), got {gate.shape}")
    if len(word) != len(htarget) or len(split) != len(htarget):
        raise ValueError(f"{path}: word/split length must equal Htarget row count")
    if not np.isfinite(htarget).all() or not np.isfinite(gate).all():
        raise ValueError(f"{path}: Htarget or gate contains nonfinite values")
    if bias is not None and (np.asarray(bias).size and not np.allclose(bias, 0, atol=0, rtol=0)):
        raise ValueError(f"{path}: nonzero router bias is incompatible with the preregistered b=0 measurement")
    if item_id is not None and len(item_id) != len(htarget):
        raise ValueError(f"{path}: item_id length mismatch")
    if anchor_hash is not None and len(anchor_hash) != len(htarget):
        raise ValueError(f"{path}: input hash length mismatch")
    metadata = json.loads(str(np.asarray(metadata_json).item()))
    required_meta = ("source_sha256", "plan_sha256", "selected_inputs_sha256")
    missing_meta = [key for key in required_meta if key not in metadata]
    if missing_meta:
        raise ValueError(f"{path}: metadata_json missing anchor fields {missing_meta}")
    return {"Htarget": htarget, "gate": gate, "word": word, "split": split,
            "item_id": np.asarray(item_id), "anchor_hash": anchor_hash,
            "Hcal_in_capture": None if hcal_in_capture is None else np.asarray(hcal_in_capture, dtype=np.float32),
            "metadata": metadata,
            "capture_sha256": file_sha256(path), "capture_path": str(path.resolve())}


def _unwrap_hcal(obj):
    if isinstance(obj, torch.Tensor):
        return obj.detach().to(torch.float32).cpu().numpy()
    if isinstance(obj, np.ndarray):
        return obj
    if isinstance(obj, dict):
        for key in ("Hcal", "hcal", "H_cal", "dense_hcal", "hidden", "arr_0"):
            if key in obj:
                return _unwrap_hcal(obj[key])
        if len(obj) == 1:
            return _unwrap_hcal(next(iter(obj.values())))
    if isinstance(obj, (tuple, list)) and len(obj) == 1:
        return _unwrap_hcal(obj[0])
    raise ValueError("Could not find Hcal tensor/array in the supplied file")


def load_hcal(path: Path) -> np.ndarray:
    suffix = path.suffix.lower()
    if suffix == ".npy":
        value = np.load(path, allow_pickle=False)
    elif suffix == ".npz":
        with np.load(path, allow_pickle=False) as z:
            value = {key: np.asarray(z[key]).copy() for key in z.files}
    else:
        # weights_only prevents arbitrary Python object deserialization.
        value = torch.load(path, map_location="cpu", weights_only=True)
    arr = np.asarray(_unwrap_hcal(value), dtype=np.float32)
    if arr.ndim != 2 or arr.shape[1] != HIDDEN_SIZE:
        raise ValueError(f"Hcal must have shape (N,{HIDDEN_SIZE}), got {arr.shape}")
    if arr.shape[0] < 2 or not np.isfinite(arr).all():
        raise ValueError("Hcal needs at least two finite rows")
    return arr


def held_same_word_pairs(word: np.ndarray, split: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    held = split == "held"
    pairs_i, pairs_j, pair_word = [], [], []
    for w in np.unique(word[held]):
        idx = np.flatnonzero(held & (word == w))
        if len(idx) < 2:
            continue
        i, j = np.triu_indices(len(idx), k=1)
        pairs_i.extend(idx[i].tolist())
        pairs_j.extend(idx[j].tolist())
        pair_word.extend([w] * len(i))
    if not pairs_i:
        raise ValueError("No held same-word pairs available")
    return np.asarray(pairs_i, dtype=np.int64), np.asarray(pairs_j, dtype=np.int64), np.asarray(pair_word, dtype=str)


def safe_corr(a: np.ndarray, b: np.ndarray, floor: float = STD_FLOOR):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    if a.size < 2 or b.size != a.size or not np.isfinite(a).all() or not np.isfinite(b).all():
        return None, {"reason": "insufficient_or_nonfinite_values", "n": int(a.size)}
    sa, sb = float(a.std()), float(b.std())
    if sa <= floor or sb <= floor:
        return None, {"reason": "near_zero_variance", "n": int(a.size), "std_a": sa, "std_b": sb}
    ac, bc = a - a.mean(), b - b.mean()
    value = float(np.dot(ac, bc) / (np.linalg.norm(ac) * np.linalg.norm(bc)))
    return float(np.clip(value, -1, 1)), {"n": int(a.size), "std_a": sa, "std_b": sb}


def summarize_pairs(a: np.ndarray, b: np.ndarray, pair_word: np.ndarray,
                    std_floor: float = STD_FLOOR) -> dict:
    per_word = []
    all_a, all_b, all_wc_a, all_wc_b = [], [], [], []
    eligible, valid, word_corrs = 0, 0, []
    words = np.unique(pair_word)
    for w in words:
        mask = pair_word == w
        x, y = np.asarray(a[mask], dtype=np.float64), np.asarray(b[mask], dtype=np.float64)
        all_a.append(x)
        all_b.append(y)
        xc, yc = x - x.mean(), y - y.mean()
        all_wc_a.append(xc)
        all_wc_b.append(yc)
        if len(x) >= MIN_PAIRS_PER_WORD:
            eligible += 1
            r, detail = safe_corr(xc, yc, std_floor)
            if r is not None:
                valid += 1
                word_corrs.append(r)
            per_word.append({"word": str(w), "n_pairs": len(x), "T": r,
                             "std_a": float(x.std()), "std_b": float(y.std()),
                             "validity": detail if r is None else None})
        else:
            per_word.append({"word": str(w), "n_pairs": len(x), "T": None,
                             "std_a": float(x.std()), "std_b": float(y.std()),
                             "validity": {"reason": "fewer_than_three_pairs", "minimum": MIN_PAIRS_PER_WORD, "n": len(x)}})
    pooled_a, pooled_b = np.concatenate(all_wc_a), np.concatenate(all_wc_b)
    pooled, pooled_detail = safe_corr(pooled_a, pooled_b, std_floor)
    raw_a, raw_b = np.concatenate(all_a), np.concatenate(all_b)
    raw_corr, raw_detail = safe_corr(raw_a, raw_b, std_floor)
    return {
        "per_word": per_word,
        "n_words_with_pairs": int(len(words)), "n_words_eligible_for_T": int(eligible),
        "n_words_valid_T": int(valid),
        "effective_word_fraction": float(valid / eligible) if eligible else None,
        "effective_word_fraction_denominator": "words with at least two held same-word pairs",
        "T_equal_word_mean": float(np.mean(word_corrs)) if word_corrs else None,
        "T_pooled_after_within_word_centering": pooled,
        "pooled_centered_validity": None if pooled is not None else pooled_detail,
        "D_std_all_pairs_A_B": [float(a.std()), float(b.std())],
        "D_std_after_word_centering_A_B": [float(pooled_a.std()), float(pooled_b.std())],
        "rawC_auxiliary": {"T_pooled_unadjusted": raw_corr,
                           "pooled_validity": None if raw_corr is not None else raw_detail,
                           "T_equal_word_mean": float(np.mean(word_corrs)) if word_corrs else None},
    }


def _cache_path(cache_dir: Path, run: dict, hcal_sha: str, pair_sha: str,
                device: torch.device) -> Path:
    key = hashlib.sha256((run["capture_sha256"] + hcal_sha + pair_sha +
                          f"N1-{N1_DRAWS}-{N1_SEED}-k{TOP_K}-{device}").encode()).hexdigest()[:20]
    return cache_dir / f"{Path(run['capture_path']).stem}__{key}.npz"


def compute_one(run: dict, hcal: np.ndarray, hcal_sha: str, hcal_path: Path,
                pair_i: np.ndarray, pair_j: np.ndarray, pair_word: np.ndarray,
                device: torch.device, cache_dir: Path) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    pair_sha = hashlib.sha256(pair_i.tobytes() + pair_j.tobytes() + pair_word.astype("U").tobytes()).hexdigest()
    cp = _cache_path(cache_dir, run, hcal_sha, pair_sha, device)
    cache_meta = {"capture_sha256": run["capture_sha256"], "hcal_sha256": hcal_sha,
                  "hcal_path": str(hcal_path.resolve()), "kind": "N1", "n_draws": N1_DRAWS,
                  "seed": N1_SEED, "k": TOP_K, "bias": "zero", "device": str(device),
                  "pair_sha256": pair_sha,
                  "moe_measure_sha256": file_sha256(Path(mm.__file__))}
    if cp.is_file():
        with np.load(cp, allow_pickle=False) as z:
            if json.loads(str(z["metadata_json"].item())) == cache_meta:
                return {"C": z["C"].copy(), "B": z["B"].copy(), "D": z["D"].copy(),
                        "cache_path": str(cp), "cache_hit": True}

    Ht = torch.as_tensor(run["Htarget"], dtype=torch.float32, device=device)
    W = torch.as_tensor(run["gate"], dtype=torch.float32, device=device)
    Hc = torch.as_tensor(hcal, dtype=torch.float32, device=device)
    b = torch.zeros(N_EXPERTS, dtype=torch.float32, device=device)
    pairs = (torch.as_tensor(pair_i, dtype=torch.long, device=device),
             torch.as_tensor(pair_j, dtype=torch.long, device=device))
    selected = mm.topk(Ht @ W.T, TOP_K)
    C = mm.coroute(selected, N_EXPERTS, TOP_K, pairs).detach().cpu().numpy().astype(np.float64)
    null = mm.null_expectation(W, b, Hc, Ht, TOP_K, "N1", n_draws=N1_DRAWS,
                               seed=N1_SEED, pairs=pairs)
    B = null["B"].detach().cpu().numpy().astype(np.float64)
    D = C - B
    np.savez_compressed(cp, C=C, B=B, D=D, pair_i=pair_i, pair_j=pair_j,
                        pair_word=pair_word, metadata_json=np.asarray(json.dumps(cache_meta, sort_keys=True)))
    return {"C": C, "B": B, "D": D, "cache_path": str(cp), "cache_hit": False,
            "null_load_tv": float(null["load_tv"])}


def analyze(a: dict, b: dict, hcal: np.ndarray, hcal_path: Path,
            device: torch.device, cache_dir: Path) -> dict:
    if not np.array_equal(a["word"], b["word"]) or not np.array_equal(a["split"], b["split"]):
        raise ValueError("A/B word or split anchors differ")
    if not np.array_equal(a["item_id"], b["item_id"]):
        raise ValueError("A/B item_id anchors differ")
    if not np.array_equal(a["anchor_hash"], b["anchor_hash"]):
        raise ValueError("A/B anchor hashes differ")
    metadata_keys = ("source_sha256", "plan_sha256", "selected_inputs_sha256")
    for key in metadata_keys:
        va, vb = a["metadata"].get(key), b["metadata"].get(key)
        if va != vb:
            raise ValueError(f"A/B capture metadata mismatch: {key}")
    if a["Htarget"].shape != b["Htarget"].shape:
        raise ValueError("A/B Htarget shapes differ")
    max_abs = float(np.max(np.abs(a["Htarget"] - b["Htarget"])))
    if not np.allclose(a["Htarget"], b["Htarget"], atol=FP16_ATOL, rtol=FP16_RTOL):
        raise ValueError(f"A/B Htarget differs beyond fp16 tolerance (max abs diff={max_abs})")
    for who, run in (("A", a), ("B", b)):
        if run["Hcal_in_capture"] is not None and run["Hcal_in_capture"].size:
            if run["Hcal_in_capture"].shape != hcal.shape or not np.allclose(
                    run["Hcal_in_capture"], hcal, atol=FP16_ATOL, rtol=FP16_RTOL):
                raise ValueError(f"{who} capture Hcal differs from the independent --hcal file")
    if len(a["word"]) != len(a["Htarget"]):
        raise ValueError("A/B labels do not align with Htarget rows")
    pair_i, pair_j, pair_word = held_same_word_pairs(a["word"], a["split"])
    hcal_sha = file_sha256(hcal_path)
    ra = compute_one(a, hcal, hcal_sha, hcal_path, pair_i, pair_j, pair_word, device, cache_dir)
    rb = compute_one(b, hcal, hcal_sha, hcal_path, pair_i, pair_j, pair_word, device, cache_dir)
    result = summarize_pairs(ra["D"], rb["D"], pair_word)
    raw = summarize_pairs(ra["C"], rb["C"], pair_word)
    result["rawC_auxiliary"] = {"T_pooled_unadjusted": raw["rawC_auxiliary"]["T_pooled_unadjusted"],
                                "T_equal_word_mean": raw["T_equal_word_mean"],
                                "per_word": raw["per_word"]}
    result.update({
        "protocol": {"null": "N1 expert-geometry preserving", "n_draws": N1_DRAWS,
                     "null_seed": N1_SEED, "k": TOP_K, "router_bias": "zero",
                     "pair_population": "held, distinct sample pairs within the same word only",
                     "word_centering": "subtract the per-word mean D before per-word T and pooled centered T",
                     "variance_floor": STD_FLOOR,
                     "minimum_pairs_per_word_for_T": MIN_PAIRS_PER_WORD,
                     "Htarget_fp16_tolerance": {"atol": FP16_ATOL, "rtol": FP16_RTOL}},
        "anchors": {"n_samples": len(a["word"]), "n_held_samples": int(np.sum(a["split"] == "held")),
                    "n_held_same_word_pairs": int(len(pair_i)), "n_held_words_with_pairs": int(len(np.unique(pair_word))),
                    "Htarget_max_abs_difference": max_abs,
                    "Htarget_allclose_within_fp16_tolerance": True},
        "D_A": {"cache_path": ra["cache_path"], "cache_hit": ra["cache_hit"],
                "null_load_tv": ra.get("null_load_tv")},
        "D_B": {"cache_path": rb["cache_path"], "cache_hit": rb["cache_hit"],
                "null_load_tv": rb.get("null_load_tv")},
        "Hcal": {"path": str(hcal_path.resolve()), "sha256": hcal_sha,
                 "shape": list(hcal.shape), "source": "independent dense calibration file"},
        "capture_A": {"path": a["capture_path"], "sha256": a["capture_sha256"],
                      "anchor_manifest": {key: a["metadata"][key] for key in metadata_keys}},
        "capture_B": {"path": b["capture_path"], "sha256": b["capture_sha256"],
                      "anchor_manifest": {key: b["metadata"][key] for key in metadata_keys}},
        "device": str(device),
        "warning": "No cross-word/R4 pairs are used. Undefined or near-zero-variance T values are null, not interpreted as high similarity."
    })
    return result


def self_test():
    words = np.asarray(["a"] * 4 + ["b"] * 4)
    same = np.asarray([1., 3., 2., 8., 4., 2., 3., 1.])
    same_result = summarize_pairs(same, same.copy(), words)
    assert np.isclose(same_result["T_equal_word_mean"], 1.0)
    assert np.isclose(same_result["T_pooled_after_within_word_centering"], 1.0)
    neg_result = summarize_pairs(same, -same, words)
    assert np.isclose(neg_result["T_equal_word_mean"], -1.0)
    assert np.isclose(neg_result["T_pooled_after_within_word_centering"], -1.0)
    const_result = summarize_pairs(np.ones(8), np.ones(8), words)
    assert const_result["T_equal_word_mean"] is None
    assert const_result["T_pooled_after_within_word_centering"] is None
    assert all(x["T"] is None for x in const_result["per_word"])
    print("E124 routing NumPy known-answer checks passed: identical D -> 1, negated D -> -1, constant D -> null.")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--a", type=Path)
    p.add_argument("--b", type=Path)
    p.add_argument("--hcal", type=Path)
    p.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    p.add_argument("--output", type=Path)
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if any(x is None for x in (args.a, args.b, args.hcal, args.output)):
        p.error("--a, --b, --hcal, and --output are required")
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        p.error("--device cuda requested, but CUDA is unavailable")
    a, b = load_capture(args.a), load_capture(args.b)
    hcal = load_hcal(args.hcal)
    result = analyze(a, b, hcal, args.hcal, device, args.cache_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
