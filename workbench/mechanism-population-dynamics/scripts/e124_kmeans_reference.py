#!/usr/bin/env python3
"""K-means self-reproducibility reference for E124 routing residuals.

This is a pure-geometry algorithm reference on frozen dense Hcal/Htarget. It
is neither the N1 null nor an upper bound, and it is not a model-seed result.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import time

import numpy as np
import torch
from sklearn.cluster import KMeans

import moe_measure as mm
import e124_routing as routing

DEFAULT_CAPTURE = Path("/tmp/xiang-moe-20261025/e124_calibration_seed0.npz")
DEFAULT_CACHE = Path("/home/xiang/mechpop_cache/e124_kmeans")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "results/e124/kmeans_reference.json"
N_CLUSTERS = 64
TOP_K = 8
KMEANS_SEEDS = tuple(range(5))
KMEANS_MAX_ITER = 50
KMEANS_TOL = 1e-4
N1_DRAWS = 32
N1_SEED = 124
MC_REFERENCE_SEED = 125
GPU_BUDGET_SECONDS = 1080.0


class BudgetExceeded(RuntimeError):
    pass


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def array_sha256(value: np.ndarray) -> str:
    a = np.ascontiguousarray(value)
    h = hashlib.sha256()
    h.update(a.dtype.str.encode())
    h.update(json.dumps(a.shape, separators=(",", ":")).encode())
    h.update(memoryview(a).cast("B"))
    return h.hexdigest()


def load_anchor(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        required = ("Hcal", "Htarget", "word", "split", "item_id", "input_sha256", "metadata_json")
        missing = [key for key in required if key not in z]
        if missing:
            raise KeyError(f"Calibration capture missing keys {missing}")
        hcal = np.asarray(z["Hcal"], dtype=np.float32)
        htarget = np.asarray(z["Htarget"], dtype=np.float32)
        word = np.asarray(z["word"]).astype(str)
        split = np.asarray(z["split"]).astype(str)
        item_id = np.asarray(z["item_id"])
        input_sha = np.asarray(z["input_sha256"]).astype(str)
        metadata = json.loads(str(np.asarray(z["metadata_json"]).item()))
    if hcal.ndim != 2 or hcal.shape[1] != 2048 or htarget.ndim != 2 or htarget.shape[1] != 2048:
        raise ValueError(f"Expected hidden size 2048; Hcal={hcal.shape}, Htarget={htarget.shape}")
    if htarget.shape[0] != len(word) or len(split) != len(word) or len(item_id) != len(word) or len(input_sha) != len(word):
        raise ValueError("Anchor features and word/split/identity arrays have inconsistent lengths")
    if not np.isfinite(hcal).all() or not np.isfinite(htarget).all():
        raise ValueError("Hcal/Htarget contains nonfinite values")
    if not np.any(split == "cal") or not np.any(split == "held"):
        raise ValueError("Expected both cal and held rows")
    return {"Hcal": hcal, "Htarget": htarget, "word": word, "split": split,
            "item_id": item_id, "input_sha256": input_sha, "metadata": metadata,
            "capture_sha256": file_sha256(path), "capture_path": str(path.resolve()),
            "hcal_sha256": array_sha256(hcal), "htarget_sha256": array_sha256(htarget),
            "input_identity_sha256": array_sha256(input_sha)}


def gate_from_centroids(centroids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    c = np.asarray(centroids, dtype=np.float32)
    return 2.0 * c, -np.square(c).sum(axis=1, dtype=np.float32)


def route_coroute(Htarget: np.ndarray, W: np.ndarray, b: np.ndarray,
                  pair_i: np.ndarray, pair_j: np.ndarray, device: torch.device) -> np.ndarray:
    h = torch.as_tensor(Htarget, dtype=torch.float32, device=device)
    w = torch.as_tensor(W, dtype=torch.float32, device=device)
    bias = torch.as_tensor(b, dtype=torch.float32, device=device)
    pairs = (torch.as_tensor(pair_i, dtype=torch.long, device=device),
             torch.as_tensor(pair_j, dtype=torch.long, device=device))
    selected = mm.topk(h @ w.T + bias, TOP_K)
    return mm.coroute(selected, N_CLUSTERS, TOP_K, pairs).detach().cpu().numpy().astype(np.float64)


def cache_metadata(anchor: dict, seed: int, null_seed: int) -> dict:
    return {"capture_sha256": anchor["capture_sha256"], "Hcal_sha256": anchor["hcal_sha256"],
            "Htarget_sha256": anchor["htarget_sha256"], "input_identity_sha256": anchor["input_identity_sha256"],
            "kmeans_seed": seed, "kmeans": "sklearn KMeans++ Euclidean Lloyd",
            "n_clusters": N_CLUSTERS, "n_init": 1, "max_iter": KMEANS_MAX_ITER, "tol": KMEANS_TOL,
            "top_k": TOP_K, "N1_draws": N1_DRAWS, "N1_seed": null_seed}


def fit_and_measure(anchor: dict, seed: int, null_seed: int,
                    pair_i: np.ndarray, pair_j: np.ndarray, pair_word: np.ndarray,
                    device: torch.device, cache_dir: Path,
                    budget_state: dict, budget_seconds: float) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cp = cache_dir / f"kmeans_seed{seed}_N1seed{null_seed}.npz"
    meta = cache_metadata(anchor, seed, null_seed)
    if cp.is_file():
        with np.load(cp, allow_pickle=False) as z:
            if json.loads(str(z["metadata_json"].item())) == meta:
                return {"C": z["C"].copy(), "B": z["B"].copy(), "D": z["D"].copy(),
                        "centroids": z["centroids"].copy(),
                        "inertia": float(z["inertia"]), "n_iter": int(z["n_iter"]),
                        "null_load_tv": float(z["null_load_tv"]), "cache_path": str(cp),
                        "cache_hit": True}
    model = KMeans(n_clusters=N_CLUSTERS, init="k-means++", n_init=1,
                   max_iter=KMEANS_MAX_ITER, tol=KMEANS_TOL,
                   algorithm="lloyd", random_state=seed, copy_x=True)
    model.fit(anchor["Hcal"])
    centroids = model.cluster_centers_.astype(np.float32, copy=False)
    W, b = gate_from_centroids(centroids)
    route_started = time.monotonic()
    C = route_coroute(anchor["Htarget"], W, b, pair_i, pair_j, device)
    route_seconds = time.monotonic() - route_started
    budget_state["elapsed"] += route_seconds
    if budget_state["elapsed"] + 0.05 >= budget_seconds:
        raise BudgetExceeded(f"GPU reference budget reached before N1 for KMeans seed {seed}")
    Hc = torch.as_tensor(anchor["Hcal"], dtype=torch.float32, device=device)
    Ht = torch.as_tensor(anchor["Htarget"], dtype=torch.float32, device=device)
    wt = torch.as_tensor(W, dtype=torch.float32, device=device)
    bt = torch.as_tensor(b, dtype=torch.float32, device=device)
    torch.cuda.synchronize(device)
    started = time.monotonic()
    null = mm.null_expectation(wt, bt, Hc, Ht, TOP_K, "N1",
                               n_draws=N1_DRAWS, seed=null_seed,
                               pairs=(torch.as_tensor(pair_i, dtype=torch.long, device=device),
                                      torch.as_tensor(pair_j, dtype=torch.long, device=device)))
    B = null["B"].detach().cpu().numpy().astype(np.float64)
    torch.cuda.synchronize(device)
    n1_seconds = time.monotonic() - started
    budget_state["elapsed"] += n1_seconds
    D = C - B
    np.savez_compressed(cp, C=C, B=B, D=D, centroids=centroids,
                        pair_i=pair_i, pair_j=pair_j, pair_word=pair_word,
                        inertia=np.asarray(float(model.inertia_)),
                        n_iter=np.asarray(int(model.n_iter_)),
                        null_load_tv=np.asarray(float(null["load_tv"])),
                        n1_seconds=np.asarray(n1_seconds),
                        route_seconds=np.asarray(route_seconds),
                        metadata_json=np.asarray(json.dumps(meta, sort_keys=True)))
    return {"C": C, "B": B, "D": D, "centroids": centroids,
            "inertia": float(model.inertia_), "n_iter": int(model.n_iter_),
            "null_load_tv": float(null["load_tv"]), "n1_seconds": n1_seconds,
            "cache_path": str(cp), "cache_hit": False}


def run_self_test():
    rng = np.random.default_rng(17)
    x0 = rng.normal(loc=(-5., -5.), scale=.05, size=(24, 2)).astype(np.float32)
    x1 = rng.normal(loc=(5., 5.), scale=.05, size=(24, 2)).astype(np.float32)
    x = np.concatenate([x0, x1])
    truth = np.array([0] * len(x0) + [1] * len(x1))
    km = KMeans(n_clusters=2, init="k-means++", n_init=1, max_iter=50, tol=1e-4,
                algorithm="lloyd", random_state=0).fit(x)
    same0, same1 = km.labels_[:len(x0)], km.labels_[len(x0):]
    assert len(np.unique(km.labels_)) == 2
    assert (np.all(same0 == same0[0]) and np.all(same1 == same1[0]) and same0[0] != same1[0])
    points = torch.from_numpy(x)
    centers = km.cluster_centers_.astype(np.float32)
    W, b = gate_from_centroids(centers)
    s1 = mm.topk(points @ torch.from_numpy(W).T + torch.from_numpy(b), 1)
    W_relabel, b_relabel = gate_from_centroids(centers[::-1].copy())
    s2 = mm.topk(points @ torch.from_numpy(W_relabel).T + torch.from_numpy(b_relabel), 1)
    c1, c2 = mm.coroute(s1, 2, 1), mm.coroute(s2, 2, 1)
    assert torch.equal(c1, c2)
    print("E124 KMeans known-answer checks passed: separated two clusters and relabel-invariant co-routing.")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", type=Path, default=DEFAULT_CAPTURE)
    p.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--gpu-budget-seconds", type=float, default=GPU_BUDGET_SECONDS)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    if not torch.cuda.is_available() and args.device.startswith("cuda"):
        p.error("CUDA requested but unavailable")
    if args.gpu_budget_seconds <= 0:
        p.error("--gpu-budget-seconds must be positive")
    device = torch.device(args.device)
    anchor = load_anchor(args.capture)
    pair_i, pair_j, pair_word = routing.held_same_word_pairs(anchor["word"], anchor["split"])
    cache_dir = args.cache_dir.expanduser().resolve()
    output_path = args.output.resolve()
    wall_start = time.monotonic()
    budget_state = {"elapsed": 0.0}

    # Persist incremental seed results so a budget stop or interruption can resume.
    runs: dict[int, dict] = {}
    mc_repeat = None
    status = "complete"
    try:
        for seed in KMEANS_SEEDS:
            if budget_state["elapsed"] >= args.gpu_budget_seconds:
                raise BudgetExceeded(f"GPU reference budget reached before KMeans seed {seed}")
            run = fit_and_measure(anchor, seed, N1_SEED, pair_i, pair_j, pair_word,
                                  device, cache_dir, budget_state, args.gpu_budget_seconds)
            runs[seed] = run
            per_run = {
                "seed": seed, "inertia": run["inertia"], "n_iter": run["n_iter"],
                "converged_before_max_iter": run["n_iter"] < KMEANS_MAX_ITER,
                "n1_load_tv": run["null_load_tv"],
                "D_rms_all_pairs": float(np.sqrt(np.mean(run["D"] ** 2))),
                "D_std_all_pairs": float(run["D"].std()),
                "D_rms_after_word_centering": float(np.sqrt(np.mean([
                    float(np.mean((run["D"][pair_word == word] - run["D"][pair_word == word].mean()) ** 2))
                    for word in np.unique(pair_word)]))),
                "cache_path": run["cache_path"], "cache_hit": run["cache_hit"],
            }
            if seed == 0:
                if budget_state["elapsed"] >= args.gpu_budget_seconds:
                    raise BudgetExceeded("GPU reference budget reached before seed0 MC repeat")
                mc = fit_and_measure(anchor, seed, MC_REFERENCE_SEED, pair_i, pair_j, pair_word,
                                     device, cache_dir, budget_state, args.gpu_budget_seconds)
                mc_repeat = routing.summarize_pairs(run["D"], mc["D"], pair_word)
                mc_repeat = {"comparison": mc_repeat,
                             "null_seed_A": N1_SEED, "null_seed_B": MC_REFERENCE_SEED,
                             "note": "Same KMeans centroids and same C; only the N1 Monte Carlo draws differ."}
                per_run["mc_repeat_cache_path"] = mc["cache_path"]
                per_run["mc_repeat_load_tv"] = mc["null_load_tv"]
            runs[seed]["summary"] = per_run
            print(f"completed KMeans seed={seed} inertia={run['inertia']:.6g} n_iter={run['n_iter']} "
                  f"GPU_elapsed_s={budget_state['elapsed']:.1f}", flush=True)
    except BudgetExceeded as exc:
        status = "gpu_budget_exceeded"
        print(str(exc), flush=True)

    summaries = []
    for seed in sorted(runs):
        summaries.append(runs[seed]["summary"])
    pairwise = []
    seeds = sorted(runs)
    for i, seed_a in enumerate(seeds):
        for seed_b in seeds[i + 1:]:
            da, db = runs[seed_a]["D"], runs[seed_b]["D"]
            ca, cb = runs[seed_a]["C"], runs[seed_b]["C"]
            pairwise.append({
                "seed_A": seed_a, "seed_B": seed_b,
                "D": routing.summarize_pairs(da, db, pair_word),
                "rawC_auxiliary": routing.summarize_pairs(ca, cb, pair_word),
            })
    result = {
        "status": status, "reference_type": "pure-geometry KMeans algorithm self-reproducibility",
        "scientific_scope": "Not the N1 null, not an upper bound, and not a model cross-seed result.",
        "capture": {"path": anchor["capture_path"], "sha256": anchor["capture_sha256"],
                    "metadata": anchor["metadata"]},
        "anchors": {"Hcal_sha256": anchor["hcal_sha256"], "Htarget_sha256": anchor["htarget_sha256"],
                    "input_identity_sha256": anchor["input_identity_sha256"],
                    "n_cal": len(anchor["Hcal"]), "n_anchor": len(anchor["Htarget"]),
                    "n_held": int(np.sum(anchor["split"] == "held")),
                    "n_held_same_word_pairs": len(pair_i),
                    "n_held_words_with_pairs": int(len(np.unique(pair_word)))},
        "kmeans": {"method": "sklearn.cluster.KMeans algorithm='lloyd', Euclidean",
                   "init": "k-means++", "n_init": 1, "n_clusters": N_CLUSTERS,
                   "max_iter": KMEANS_MAX_ITER, "tol": KMEANS_TOL,
                   "seeds": list(KMEANS_SEEDS)},
        "router_mapping": "W=2*centroids; b=-||centroid||^2; top-8 selects nearest eight centers.",
        "N1": {"kind": "moe_measure.null_expectation", "draws": N1_DRAWS,
               "seed": N1_SEED, "top_k": TOP_K, "bias_recalibration": "preserve each router's Hcal load"},
        "elapsed_gpu_reference_seconds": round(budget_state["elapsed"], 2),
        "elapsed_wall_seconds": round(time.monotonic() - wall_start, 2),
        "gpu_budget_seconds": args.gpu_budget_seconds,
        "per_run": summaries, "pairwise_10_comparisons": pairwise if len(runs) == 5 else pairwise,
        "seed0_MC_repeat_reference": mc_repeat,
        "arrays": {"cache_dir": str(cache_dir), "files": sorted(p.name for p in cache_dir.glob("kmeans_seed*.npz"))},
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": status, "completed_seeds": sorted(runs),
                      "pairwise_comparisons": len(pairwise), "output": str(output_path),
                      "cache_dir": str(cache_dir)}, indent=2))
    return 0 if status == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
