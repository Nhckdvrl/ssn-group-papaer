"""E81 analysis: reliability-corrected correspondence of attention roles vs causal carriers.

Usage: e81_analyze.py  -> results/e81/analysis.json + printed tables
Statistic (as E35 / E74): within-layer Spearman between [layer x head] maps, averaged over layers.
Reliability: within-model split-half of the same statistic, Spearman-Brown corrected to the full sample.
POST-HOC (flagged): whole-map Pearson for DLA / ablation, with Pearson split-half reliability.
"""
import glob
import itertools
import json

import numpy as np
from scipy.stats import pearsonr, spearmanr

import mp_common as mc

OUT = mc.RESULTS / "e81"
MAPS = ("ind", "prev", "att_io", "att_s2", "abl", "dla")
SB = lambda r: 2 * r / (1 + r)  # noqa: E731


def within(a, b):
    return float(np.nanmean([spearmanr(a[l], b[l])[0] for l in range(a.shape[0])]))


def load():
    D = {}
    for f in sorted(glob.glob(str(OUT / "*.npz"))):
        z = np.load(f)
        D[f.split("/")[-1][:-4]] = {k: z[k] for k in z.files}
    return D


def rel(d):
    out = {k: SB(within(d[k][0], d[k][1])) for k in MAPS}
    for k in ("dla", "abl"):
        out[k + "_pearson"] = SB(pearsonr(d[k][0].ravel(), d[k][1].ravel())[0])
    return out


def top(m, k=3):
    H = m.shape[1]
    return [(int(t // H), int(t % H)) for t in np.argsort(m.ravel())[::-1][:k]]


def compare(dx, dy, rx, ry):
    res = {}
    for k in MAPS:
        x, y = dx[k].mean(0), dy[k].mean(0)
        r = within(x, y)
        res[k] = {"r": r, "corrected": r / np.sqrt(max(rx[k], 1e-6) * max(ry[k], 1e-6))}
    for k in ("dla", "abl"):
        x, y = dx[k].mean(0).ravel(), dy[k].mean(0).ravel()
        r = pearsonr(x, y)[0]
        res[k + "_pearson"] = {"r": float(r), "corrected": float(r / np.sqrt(rx[k + "_pearson"] * ry[k + "_pearson"]))}
    for k in ("dla", "abl"):
        tx, ty = top(dx[k].mean(0)), top(dy[k].mean(0))
        res[f"top3_overlap_{k}"] = len(set(tx) & set(ty))
    ay = dy["abl"].mean(0)
    own = sum(ay[l, h] for l, h in top(ay))
    res["additive_transfer_abl"] = float(sum(ay[l, h] for l, h in top(dx["abl"].mean(0))) / own) if own > 0 else None
    res["top3_dla"] = [[f"{l}.{h}" for l, h in top(dx["dla"].mean(0))], [f"{l}.{h}" for l, h in top(dy["dla"].mean(0))]]
    return res


def summarize(rows):
    keys = [k for k in rows[0] if isinstance(rows[0][k], dict)]
    out = {k: {"r": float(np.mean([r[k]["r"] for r in rows])), "corrected": float(np.mean([r[k]["corrected"] for r in rows]))}
           for k in keys}
    for k in ("top3_overlap_dla", "top3_overlap_abl", "additive_transfer_abl"):
        v = [r[k] for r in rows if r[k] is not None]
        out[k] = float(np.mean(v)) if v else None
    out["n_pairs"] = len(rows)
    return out


def main():
    D = load()
    R = {t: rel(d) for t, d in D.items()}
    res = {"reliability": R, "A": {}, "B": {}}
    # (A) DataDecide crossing
    dd = {t: t.split("__") for t in D if t.startswith("dd__")}
    groups = {"same_seed_diff_corpus": [], "same_corpus_diff_seed": [], "both_differ": []}
    for a, b in itertools.combinations(sorted(dd), 2):
        ca, sa = dd[a][1], dd[a][2].split("seed-")[1]
        cb, sb_ = dd[b][1], dd[b][2].split("seed-")[1]
        g = ("same_seed_diff_corpus" if sa == sb_ and ca != cb else
             "same_corpus_diff_seed" if ca == cb and sa != sb_ else "both_differ" if ca != cb else None)
        if g:
            groups[g].append(compare(D[a], D[b], R[a], R[b]))
    res["A"] = {g: summarize(v) for g, v in groups.items() if v}
    # (B) continuation chains and the sibling reference
    O = "hf__OLMo-2-0425-1B__"
    chain = [("stage1 -> stage2 i1 @5B", O + "stage1-step1907359-tokens4001B", O + "stage2-ingredient1-step2000-tokens5B"),
             ("stage2 i1 @5B -> @51B", O + "stage2-ingredient1-step2000-tokens5B", O + "stage2-ingredient1-step23852-tokens51B"),
             ("stage1 -> stage2 i1 end", O + "stage1-step1907359-tokens4001B", O + "stage2-ingredient1-step23852-tokens51B"),
             ("stage1 -> stage2 i2 end", O + "stage1-step1907359-tokens4001B", O + "stage2-ingredient2-step23852-tokens51B"),
             ("stage1 -> stage2 i3 end", O + "stage1-step1907359-tokens4001B", O + "stage2-ingredient3-step23852-tokens51B"),
             ("base main -> SFT", O + "main", "hf__OLMo-2-0425-1B-SFT__main"),
             ("SFT -> DPO", "hf__OLMo-2-0425-1B-SFT__main", "hf__OLMo-2-0425-1B-DPO__main"),
             ("DPO -> Instruct", "hf__OLMo-2-0425-1B-DPO__main", "hf__OLMo-2-0425-1B-Instruct__main"),
             ("base main -> Instruct", O + "main", "hf__OLMo-2-0425-1B-Instruct__main"),
             ("pythia-410m 66k -> 100k", "pythia__pythia-410m__66000", "pythia__pythia-410m__100000"),
             ("pythia-410m 100k -> 143k", "pythia__pythia-410m__100000", "pythia__pythia-410m__143000"),
             ("pythia-410m 66k -> 143k", "pythia__pythia-410m__66000", "pythia__pythia-410m__143000"),
             ("SIBLING pythia-410m std vs dedup", "pythia__pythia-410m__143000", "pythia__pythia-410m-deduped__143000")]
    for name, a, b in chain:
        if a in D and b in D:
            res["B"][name] = compare(D[a], D[b], R[a], R[b])
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=float))
    print("reliability (SB, within-layer Spearman; *_pearson whole-map)")
    for t, r in sorted(R.items()):
        print(f"  {t[:58]:58s}", {k: round(v, 2) for k, v in r.items()})
    print("\n(A) DataDecide crossing: raw r -> corrected")
    for g, s in res["A"].items():
        print(f"  {g} (n={s['n_pairs']}):", {k: f"{s[k]['r']:.2f}->{s[k]['corrected']:.2f}" for k in MAPS + ('dla_pearson', 'abl_pearson')},
              "top3 dla/abl", round(s["top3_overlap_dla"], 2), round(s["top3_overlap_abl"], 2), "transfer", s["additive_transfer_abl"])
    print("\n(B) continuation / sibling")
    for n, c in res["B"].items():
        print(f"  {n:34s}", {k: f"{c[k]['r']:.2f}->{c[k]['corrected']:.2f}" for k in ('ind', 'att_io', 'abl', 'dla_pearson')},
              "top3 dla", c["top3_overlap_dla"], "abl", c["top3_overlap_abl"], "transfer", None if c["additive_transfer_abl"] is None else round(c["additive_transfer_abl"], 2), c["top3_dla"])


if __name__ == "__main__":
    main()
