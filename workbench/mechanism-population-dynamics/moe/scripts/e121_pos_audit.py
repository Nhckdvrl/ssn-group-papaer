"""Correct E121 POS label randomisation without a new model forward.

Run only after registering the audit: --device cpu (default) or cuda.
--self-test uses only NumPy and a six-point known-answer example.
The pair cache is independent of inference permutations/bootstrap settings.
Historical E121 result files are never overwritten.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np


WB = Path(__file__).resolve().parents[1]
RES = WB / "results" / "e121"


def pairs_by_word(words):
    i, j, w = [], [], []
    names = sorted(set(words))
    words = np.asarray(words)
    for wi, name in enumerate(names):
        ids = np.flatnonzero(words == name)
        a, b = np.triu_indices(len(ids), 1)
        i.extend(ids[a]); j.extend(ids[b]); w.extend([wi] * len(a))
    return np.asarray(i, dtype=int), np.asarray(j, dtype=int), np.asarray(w, dtype=int), names


def per_word_delta(values, same, pair_word, n_words):
    """One value per word; undefined same/different contrasts remain NaN."""
    n1 = np.bincount(pair_word, weights=same, minlength=n_words)
    n0 = np.bincount(pair_word, weights=~same, minlength=n_words)
    s1 = np.bincount(pair_word, weights=values * same, minlength=n_words)
    s0 = np.bincount(pair_word, weights=values * ~same, minlength=n_words)
    out = np.full(n_words, np.nan)
    ok = (n1 > 0) & (n0 > 0)
    out[ok] = s1[ok] / n1[ok] - s0[ok] / n0[ok]
    return out


def summarize(C, D, i, j, pair_word, names, words, labels, scope,
              n_perm=999, n_boot=1000, seed=0):
    """Shuffle sample labels within word, then rebuild every incident pair flag."""
    keep = scope[i] & scope[j]
    i, j, pw = i[keep], j[keep], pair_word[keep]
    values = np.concatenate((C[:, keep], D[:, keep]), axis=0)
    nw = len(names)
    same = labels[i] == labels[j]
    observed_pw = np.stack([per_word_delta(x, same, pw, nw) for x in values])
    valid = np.isfinite(observed_pw[0])
    if not valid.any():
        raise ValueError("No word has both same-label and different-label pairs")
    observed = observed_pw[:, valid].mean(1)
    groups = [np.flatnonzero(scope & (words == name)) for name in names]
    rng_perm = np.random.default_rng(seed)
    perm = np.empty((n_perm, len(values)))
    for t in range(n_perm):
        shuffled = labels.copy()
        for ids in groups:
            shuffled[ids] = labels[rng_perm.permutation(ids)]
        flags = shuffled[i] == shuffled[j]
        perm[t] = [per_word_delta(x, flags, pw, nw)[valid].mean() for x in values]
    rng_boot = np.random.default_rng(seed + 1)
    boot_ids = rng_boot.integers(0, valid.sum(), (n_boot, valid.sum()))
    boot = observed_pw[:, valid][:, boot_ids].mean(2)
    out = {"n_items": int(scope.sum()), "n_pairs": len(i), "n_valid_words": int(valid.sum()),
           "excluded_words": [name for name, ok in zip(names, valid) if not ok], "layers": []}
    nl = len(C)
    for layer in range(nl):
        row = {}
        for metric, n in (("raw", layer), ("resid", nl + layer)):
            row[metric] = {"delta": float(observed[n]),
                           "ci95_word_bootstrap": np.quantile(boot[n], [.025, .975]).tolist(),
                           "sample_label_perm_p": float((1 + (np.abs(perm[:, n]) >= abs(observed[n])).sum()) / (n_perm + 1)),
                           "perm_abs_q95": float(np.quantile(np.abs(perm[:, n]), .95))}
        ratio = observed[nl + layer] / observed[layer] if observed[layer] != 0 else None
        row["resid_over_raw"] = None if ratio is None else float(ratio)
        row["meets_preregistered_20pct_effect"] = bool(ratio is not None and ratio >= .2 and observed[nl + layer] > 0)
        out["layers"].append(row)
    return out


def compute_pair_cache(args, items, i, j):
    # Delayed imports keep the known-answer self-test strictly NumPy-only.
    import torch
    import moe_measure as mm
    torch.set_num_threads(args.threads)
    cap = torch.load(args.capture, map_location="cpu", mmap=True, weights_only=False)
    layers = list(range(cap["gates"].shape[0])) if args.layers == "all" else [int(v) for v in args.layers.split(",")]
    C, D, tv = [], [], []
    device = args.device
    pair_t = (torch.as_tensor(i, device=device), torch.as_tensor(j, device=device))
    for layer in layers:
        W = cap["gates"][layer].to(device).float()
        H = cap["H_last"][layer, :len(items)].to(device).float()
        Hc = cap["H_cal"][layer].to(device).float()
        E = W.shape[0]
        selected = mm.topk(H @ W.T, args.k)
        c = mm.coroute(selected, E, args.k, pair_t)
        target = mm.loads(mm.topk(Hc @ W.T, args.k), E)
        # N1 Wn = (U*S) Q V^T. Project H once; algebra is identical to
        # full-dimensional mm.null_expectation, up to fp32 rounding.
        U, S, V = mm.readout(W)
        hc, ha = Hc @ V, H @ V
        del Hc, H
        gen = torch.Generator().manual_seed(args.null_seed)
        acc = torch.zeros_like(c)
        errors = []
        for _ in range(args.draws):
            Q = mm.haar(len(S), gen).to(device=device, dtype=W.dtype)
            wn = (U * S) @ Q
            bn = mm.fit_bias(hc, wn, args.k, target)
            acc += mm.coroute(mm.topk(ha @ wn.T + bn, args.k), E, args.k, pair_t)
            load = mm.loads(mm.topk(hc @ wn.T + bn, args.k), E)
            errors.append(float(((load / load.sum()) - (target / target.sum())).abs().sum() / 2))
        C.append(c.cpu().numpy())
        D.append((c - acc / args.draws).cpu().numpy())
        tv.append(float(np.mean(errors)))
        print(f"layer {layer}: cached {len(i)} pairs, null load TV {tv[-1]:.6g}", flush=True)
    return np.stack(C), np.stack(D), layers, tv


def self_test():
    words = np.array(["w"] * 6)
    labels = np.array([0, 0, 0, 1, 1, 1])
    i, j, pw, names = pairs_by_word(words)
    x = (labels[i] == labels[j]).astype(float)
    assert per_word_delta(x, labels[i] == labels[j], pw, 1)[0] == 1
    exact = []
    for group in itertools.combinations(range(6), 3):
        lab = np.zeros(6, dtype=int)
        lab[list(group)] = 1
        flags = lab[i] == lab[j]
        exact.append(per_word_delta(x, flags, pw, 1)[0])
        # Every rebuilt same relation is a valid equivalence relation.
        same_matrix = lab[:, None] == lab[None, :]
        for a, b, c in itertools.product(range(6), repeat=3):
            assert not (same_matrix[a, b] and same_matrix[b, c]) or same_matrix[a, c]
    assert sum(abs(t) >= 1 for t in exact) == 2  # Exact two-sided p = 2/20.
    assert np.isclose(min(exact), -1 / 9)
    a = summarize(x[None], .5 * x[None], i, j, pw, names, words, labels,
                  np.ones(6, dtype=bool), n_perm=999, n_boot=20, seed=7)
    b = a["layers"][0]
    assert b["raw"]["delta"] == 1 and b["resid"]["delta"] == .5
    assert .06 < b["raw"]["sample_label_perm_p"] < .14
    assert b["raw"]["ci95_word_bootstrap"] == [1, 1]
    print("NumPy known-answer test passed: exact p=0.1, delta=1, residual delta=0.5")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--capture", type=Path, default=Path("/home/xiang/mechpop_cache/e121/main/capture.pt"))
    p.add_argument("--items", type=Path, default=RES / "items_pos.jsonl")
    p.add_argument("--output", type=Path, default=RES / "pos_audit_20261025.json")
    p.add_argument("--pair-cache", type=Path, default=RES / "pos_audit_20261025_pairs.npz")
    p.add_argument("--device", default="cpu")
    p.add_argument("--threads", type=int, default=8)
    p.add_argument("--layers", default="all")
    p.add_argument("--k", type=int, default=8)
    p.add_argument("--draws", type=int, default=32)
    p.add_argument("--null-seed", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--permutations", type=int, default=999)
    p.add_argument("--bootstrap", type=int, default=1000)
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if min(args.draws, args.permutations, args.bootstrap) < 1:
        p.error("draws, permutations, and bootstrap must be positive")
    items_bytes = args.items.read_bytes()
    items = [json.loads(line) for line in items_bytes.decode().splitlines() if line]
    words = np.array([it["word"] for it in items])
    labels = np.array([it["label"] for it in items])
    i, j, pw, names = pairs_by_word(words)
    stat = args.capture.stat()
    manifest = {"items_sha256": hashlib.sha256(items_bytes).hexdigest(), "capture": str(args.capture.resolve()),
                "capture_size": stat.st_size, "capture_mtime_ns": stat.st_mtime_ns,
                "layers": args.layers, "k": args.k, "draws": args.draws, "null_seed": args.null_seed,
                "null": "N1", "computation": "fp32 readout-subspace projection"}
    if args.pair_cache.exists():
        with np.load(args.pair_cache, allow_pickle=False) as cache:
            if json.loads(str(cache["manifest"])) != manifest:
                raise ValueError("Pair-cache manifest mismatch; choose a fresh --pair-cache path")
            C, D = cache["C"], cache["D"]
            layers, tv = cache["layers"].tolist(), cache["load_tv"].tolist()
            assert np.array_equal(i, cache["i"]) and np.array_equal(j, cache["j"])
    else:
        C, D, layers, tv = compute_pair_cache(args, items, i, j)
        args.pair_cache.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.pair_cache, C=C, D=D, i=i, j=j, pair_word=pw,
                            layers=layers, load_tv=tv, manifest=json.dumps(manifest, sort_keys=True))
    out = {"manifest": manifest, "pair_cache": str(args.pair_cache.resolve()), "layers": layers,
           "load_tv": tv, "permutations": args.permutations, "bootstrap": args.bootstrap,
           "analysis_seed": args.seed, "primary_scope": "held", "ci_unit": "word form",
           "note": "No model forward. H_cal is the original calibration capture (POS and sense contexts). "
                   "Permutation shuffles sample labels within word, retaining sample-pair dependence. "
                   "Residuals depend on N1; this is not a cross-seed or causal-function claim."}
    for scope_name, scope in (("held", np.array([it["split"] == "held" for it in items])),
                              ("all", np.ones(len(items), dtype=bool))):
        out[scope_name] = summarize(C, D, i, j, pw, names, words, labels, scope,
                                    args.permutations, args.bootstrap, args.seed)
        for layer, row in zip(layers, out[scope_name]["layers"]):
            row["layer"] = layer
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
