"""E121 analysis.

  e121_analyze.py r12 REV [NULL]           R1 switch rates, R2 raw / residual same-vs-different-label co-routing (POS, sense)
  e121_analyze.py r4 NULL REV1 REV2 ...    R4 within-run boundary stability on fixed anchors (held-out POS items)
  e121_analyze.py r3                       R3 expert-differentiation summaries from r3_raw.pt
NULL in {N1, N2}; default N2.  Outputs results/e121/*.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch

import moe_measure as mm
from e121_olmoe import RES, STORE, read_items

torch.set_default_dtype(torch.float32)
DEV = "cuda"
K, E = 8, 64


def load_cap(rev):
    return torch.load(STORE / rev / "capture.pt")


def word_pairs(items, idx):
    """All within-word pairs among item indices idx (same set). Returns i, j, same-label flag, word id."""
    by = {}
    for n in idx:
        by.setdefault((items[n]["set"], items[n]["word"]), []).append(n)
    I, J, S, Wd = [], [], [], []
    for w, (key, lst) in enumerate(sorted(by.items())):
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                I.append(lst[a]); J.append(lst[b]); Wd.append(w)
                S.append(items[lst[a]]["label"] == items[lst[b]]["label"])
    return np.array(I), np.array(J), np.array(S), np.array(Wd)


def residual_layer(cap, L, idx, pairs_t, kind, seed=0, n_draws=32):
    H = cap["H_last"][L][idx].to(DEV).float()
    Hc = cap["H_cal"][L].to(DEV).float()
    W = cap["gates"][L].to(DEV)
    b = torch.zeros(E, device=DEV)
    S = mm.topk(H @ W.T + b, K)
    C = mm.coroute(S, E, K, pairs_t)
    ne = mm.null_expectation(W, b, Hc, H, K, kind, n_draws, seed, pairs_t)
    return C, C - ne["B"], ne["load_tv"]


def delta_stats(x, same, word, n_perm=1000, n_boot=1000, seed=0):
    """Word-balanced mean(x|same) - mean(x|diff); permutation of the same/diff flag within word; word bootstrap."""
    rng = np.random.default_rng(seed)
    _, w = np.unique(word, return_inverse=True)
    nw = w.max() + 1
    srt = np.argsort(w, kind="stable")

    def per_word(s):
        s = s.astype(float)
        n1, n0 = np.bincount(w, s, nw), np.bincount(w, 1 - s, nw)
        m1 = np.bincount(w, x * s, nw) / np.maximum(n1, 1)
        m0 = np.bincount(w, x * (1 - s), nw) / np.maximum(n0, 1)
        ok = (n1 > 0) & (n0 > 0)
        return (m1 - m0)[ok]

    pw = per_word(same)
    obs = pw.mean()
    perm = np.empty(n_perm)
    for t in range(n_perm):
        order = np.lexsort((rng.random(len(w)), w))
        s2 = np.empty_like(same)
        s2[srt] = same[order]
        perm[t] = per_word(s2).mean()
    boot = [pw[rng.integers(0, len(pw), len(pw))].mean() for _ in range(n_boot)]
    return {"delta": float(obs), "perm_p": float((np.abs(perm) >= abs(obs)).mean()), "perm_q975": float(np.quantile(np.abs(perm), 0.95)),
            "ci": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))], "n_words": int(len(pw))}


def r12(rev, kind="N2"):
    import os
    sets = os.environ.get("E121_SETS", "pos,sense").split(",")
    lay = os.environ.get("E121_LAYERS")
    layers = list(range(int(lay.split("-")[0]), int(lay.split("-")[1]) + 1)) if lay else None
    nperm = int(os.environ.get("E121_NPERM", "1000"))
    tag = os.environ.get("E121_TAG", "")
    cap = load_cap(rev)
    items = read_items()
    out = {"rev": rev, "null": kind, "n_perm": nperm}
    for setname in sets:
        idx = np.array([n for n, it in enumerate(items) if it["set"] == setname])
        loc = {n: a for a, n in enumerate(idx)}
        I, J, S, Wd = word_pairs(items, idx)
        pt = (torch.tensor([loc[i] for i in I], device=DEV), torch.tensor([loc[j] for j in J], device=DEV))
        res = []
        for L in (layers or range(cap["H_last"].shape[0])):
            C, D, tv = residual_layer(cap, L, idx, pt, kind)
            C, D = C.cpu().numpy(), D.cpu().numpy()
            per_word_C = [C[Wd == w].mean() for w in np.unique(Wd)]
            same_C = [C[(Wd == w) & S].mean() for w in np.unique(Wd)]
            res.append({"layer": L, "switch_rate": float(1 - np.mean(per_word_C)), "switch_rate_same_label": float(1 - np.mean(same_C)),
                        "raw": delta_stats(C, S, Wd, n_perm=nperm), "resid": delta_stats(D, S, Wd, n_perm=nperm), "load_tv": tv,
                        "normD": float(D.std())})
            r = res[-1]
            print(setname, L, f"switch {r['switch_rate']:.3f} raw δ {r['raw']['delta']:.4f} (p {r['raw']['perm_p']:.3f}) "
                  f"resid δ {r['resid']['delta']:.4f} (p {r['resid']['perm_p']:.3f}) tv {tv:.3f}", flush=True)
        out[setname] = res
    (RES / f"r12_{rev}_{kind}{tag}.json").write_text(json.dumps(out, indent=1))


def r4(kind, revs):
    items = read_items()
    idx = np.array([n for n, it in enumerate(items) if it["set"] == "pos" and it["split"] == "held"])
    pt = mm.upper_pairs(len(idx), DEV)
    Ds, Cs = {}, {}
    caps = {r: load_cap(r) for r in revs}
    nL = caps[revs[0]]["H_last"].shape[0]
    out = {"null": kind, "revs": revs, "n_anchor": int(len(idx)), "layers": []}
    for L in range(nL):
        for r in revs:
            C, D, _ = residual_layer(caps[r], L, idx, pt, kind, seed=1)
            Cs[r], Ds[r] = C, D
        _, D2, _ = residual_layer(caps[revs[0]], L, idx, pt, kind, seed=2)
        row = {"layer": L, "ceiling_T_" + revs[0]: mm.corr(Ds[revs[0]], D2)}
        for a in range(len(revs)):
            for b in range(a + 1, len(revs)):
                row[f"T_{revs[a]}|{revs[b]}"] = mm.corr(Ds[revs[a]], Ds[revs[b]])
                row[f"corrC_{revs[a]}|{revs[b]}"] = mm.corr(Cs[revs[a]], Cs[revs[b]])
        row["normD"] = {r: float(Ds[r].std()) for r in revs}
        out["layers"].append(row)
        print(json.dumps(row), flush=True)
    (RES / f"r4_{kind}.json").write_text(json.dumps(out, indent=1))


def r3(n_boot=1000, seed=0):
    """R3 summaries. Expert noun preference is residualised by word (noun share of the word subtracted) and estimated
    on the calibration split; selectivity uses held-out items only."""
    rng = np.random.default_rng(seed)
    raw = torch.load(STORE / "main" / "r3_raw.pt")
    cap = load_cap("main")
    items = read_items()
    pos_idx = np.array([n for n, it in enumerate(items) if it["set"] == "pos"])
    pos = [items[n] for n in pos_idx]
    split = np.array([it["split"] for it in pos])
    noun = np.array([it["label"] == "NOUN" for it in pos], dtype=float)
    words = np.array([it["word"] for it in pos])
    share = {w: noun[(words == w) & (split == "cal")].mean() for w in np.unique(words)}
    resid_noun = noun - np.array([share[w] for w in words])
    out = {"layers": []}
    nL = cap["H_last"].shape[0]
    for L in range(nL):
        H = cap["H_last"][L][pos_idx].float()
        top1 = (H @ cap["gates"][L].T).argmax(-1).numpy()
        pref, cnt = np.full(E, np.nan), np.zeros(E)
        for e in range(E):
            m = (top1 == e) & (split == "cal")
            cnt[e] = m.sum()
            if m.sum() >= 3:
                pref[e] = resid_noun[m].mean()
        row = {"layer": L}
        for key, v in raw.items():
            if not key.startswith(f"L{L}_"):
                continue
            tag = key.split("_", 1)[1]
            kl, dn = v["kl"].numpy(), v["dnll"].numpy()
            row[tag] = {"kl_mean": float(kl.mean()), "dnll_mean": float(dn.mean()),
                        "kl_cal": float(kl[split == "cal"].mean()), "kl_held": float(kl[split == "held"].mean()),
                        "dnll_cal": float(dn[split == "cal"].mean()), "dnll_held": float(dn[split == "held"].mean()),
                        "absmax_dnll": float(np.abs(dn).max())}
            if tag in ("swap9_s0", "swaprand_s0"):
                old, new = v["old"].numpy(), v["new"].numpy()
                po, pn = pref[old], pref[new]
                ok = (split == "held") & ~np.isnan(po) & ~np.isnan(pn)
                opp = ok & (np.sign(po) != np.sign(pn))
                same = ok & (np.sign(po) == np.sign(pn))
                if opp.sum() >= 10 and same.sum() >= 10:
                    g = kl[opp].mean() - kl[same].mean()
                    bo = []
                    io, isame = np.where(opp)[0], np.where(same)[0]
                    for _ in range(n_boot):
                        bo.append(kl[rng.choice(io, len(io))].mean() - kl[rng.choice(isame, len(isame))].mean())
                    d = np.abs(po - pn)
                    row[tag]["selectivity"] = {"gamma_kl": float(g), "ci": [float(np.quantile(bo, .025)), float(np.quantile(bo, .975))],
                                               "n_opp": int(opp.sum()), "n_same": int(same.sum()),
                                               "spearman_kl_vs_prefgap": float(__import__("scipy.stats", fromlist=["spearmanr"]).spearmanr(d[ok], kl[ok])[0])}
        out["layers"].append(row)
        print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk in ("kl_mean", "kl_cal", "kl_held", "selectivity")}) for k, v in row.items()})[:900], flush=True)
    (RES / "r3_summary.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "r12":
        r12(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "N2")
    elif cmd == "r4":
        r4(sys.argv[2], sys.argv[3:])
    elif cmd == "r3":
        r3()
