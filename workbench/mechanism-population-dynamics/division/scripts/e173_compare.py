#!/usr/bin/env python3
"""E173 CPU comparisons: recipe pairs (seed0 vs seed1) against the E167 baseline init pair and the 15-pair ruler.

Readouts (fixed in experiments/E173-recipe-contrast-axis.md before the new runs were seen):
  (i)   T_D per layer at 0 / 1e8 / 2e8 / 4e8 / 8e8 (analyze_routing.py, unchanged; each recipe's own step-0 floor)
  (ii)  route fingerprint Hungarian-matched corr at 8e8 (analyze_functional.py route, unchanged)
  (iii) E170 cell decomposition by UD variable at 8e8 (functions copied verbatim from e170_decompose.py):
        deep-mean share / cellcorr / residcorr per variable, share permutation 95th pct, top-3 by share,
        Spearman of the 9 variable shares against the baseline pair
  (iv)  held-out CE at step 3000 and at the end (train logs), UD-text base NLL (functional_probe)
  (v)   T_D-vs-token curves
Writes results/e173/{routing.json, functional_route.json, decomp_800000000.json, summary.json, table.md}.

Usage: e173_compare.py [--skip-routing] [--skip-decomp]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

WB = Path(__file__).resolve().parents[1]
S = WB / "scripts"
A = Path.home() / "mechpop_cache/e173_analysis"
A167 = Path.home() / "mechpop_cache/e167_analysis"
RUNS = {"e173": Path.home() / "mechpop_cache/e173_runs", "e167": Path.home() / "mechpop_cache/e167_runs"}
PY = str(Path.home() / ".venvs/mechpop/bin/python")
OUT = WB / "results/e173"
OUT.mkdir(parents=True, exist_ok=True)
TOKS = [0, 100000000, 200000000, 400000000, 800000000]
END = 800000000
DEEP = list(range(6, 12))
RECIPES = {  # name -> (run A, run B, label)
    "base": ("I0D0", "I1D0", "基线（E167 配方）"),
    "frz": ("FRZ_I0", "FRZ_I1", "(e) 冻结随机路由器"),
    "lb0": ("LB0_I0", "LB0_I1", "(a) lb=0"),
    "lb0001": ("LB0001_I0", "LB0001_I1", "(a') lb=0.001"),
    "g16": ("G16_I0", "G16_I1", "(c) 16 专家 top-2"),
    "g256": ("G256_I0", "G256_I1", "(d) 256 专家 top-32"),
    "lb01": ("LB01_I0", "LB01_I1", "(b) lb=0.1"),
    "rerun": ("I0D0", "BASE_I0", "I0D0 精确配置重跑（A100）"),  # 11-06: second rerun ceiling at 8e8
}
WINDOWS = [(500, 1000), (1000, 2000), (2000, 2500), (2500, 3000)]
HELD_STEPS = [500, 1000, 1500, 2000, 2500, 3000]
VAR_ORDER = ["upos", "feats", "deprel", "head_upos", "prev_upos", "next_upos", "sentpos", "genre", "doc"]


def have(sub, run, t):
    return (A / sub / f"{run}__ckpt_{t}.npz").exists()


def run_dir(run):
    return RUNS["e167"] / run if run[0] == "I" and "_" not in run else RUNS["e173"] / run


# ------------------------------------------------------------------ (i) routing
def routing(skip):
    specs, idx = [], []
    for name, (a, b, _) in RECIPES.items():
        for t in TOKS:
            if have("routing", a, t) and have("routing", b, t):
                specs.append(f"{a}__ckpt_{t}.npz:{b}__ckpt_{t}.npz"); idx.append((name, t))
    if not skip:
        subprocess.run([PY, "-B", str(S / "analyze_routing.py"), str(A / "routing"), str(OUT / "routing.json")] + specs,
                       check=True, env=dict(os.environ, E167_NPERM="0"), stdout=subprocess.DEVNULL)
    R = {(r["A"].split("__")[0], r["B"].split("__")[0], r["tokens_A"]): r for r in json.loads((OUT / "routing.json").read_text())["results"]}
    out = {}
    for name, (a, b, _) in RECIPES.items():
        for t in TOKS:
            r = R.get((a, b, t))
            if r is None:
                continue
            L = r["layers"]
            out.setdefault(name, {})[t] = {"T_D": [l["T_D"] for l in L], "T_D_ci": [l["T_D_ci"] for l in L],
                                          "T_ctx": [l["T_ctx"] for l in L], "T_h": [l["T_h"] for l in L],
                                          "L11": L[11]["T_D"], "L11_ci": L[11]["T_D_ci"],
                                          "deep": float(np.mean([L[l]["T_D"] for l in DEEP])),
                                          "shallow": float(np.mean([L[l]["T_D"] for l in range(6)]))}
    return out


def ruler():
    """Baseline 15 only-init pairs: L11 / deep range at each token count (from E167 results; 1e8 computed here once)."""
    rng = {}
    for t in TOKS[1:]:
        f = WB / f"results/e167/routing_{t}.json"
        if not f.exists():
            f = OUT / f"baseline15_routing_{t}.json"
            if not f.exists():
                runs = [f"I{i}D0" for i in range(6)]
                specs = [f"{runs[i]}__ckpt_{t}.npz:{runs[j]}__ckpt_{t}.npz" for i in range(6) for j in range(i + 1, 6)]
                subprocess.run([PY, "-B", str(S / "analyze_routing.py"), str(A167 / "routing"), str(f)] + specs,
                               check=True, env=dict(os.environ, E167_NPERM="0"), stdout=subprocess.DEVNULL)
        R = json.loads(f.read_text())["results"]
        init = [[l["T_D"] for l in r["layers"]] for r in R
                if r["tokens_A"] == t and r["A"][2:4] == "D0" and r["B"][2:4] == "D0" and r["A"][:4] != r["B"][:4]]
        l11 = [x[11] for x in init]; deep = [float(np.mean(x[6:])) for x in init]
        rng[t] = {"n": len(init), "L11": [min(l11), float(np.mean(l11)), max(l11)], "deep": [min(deep), float(np.mean(deep)), max(deep)]}
    return rng


# ------------------------------------------------------------------ (ii) route fingerprints
def route_fp():
    specs, names = [], []
    for name, (a, b, _) in RECIPES.items():
        if have("functional", a, END) and have("functional", b, END):
            specs.append(f"{a}__ckpt_{END}.npz:{b}__ckpt_{END}.npz"); names.append(name)
    if not specs:
        return {}
    subprocess.run([PY, "-B", str(S / "analyze_functional.py"), "route", str(A / "functional"), str(OUT / "functional_route.json")] + specs,
                   check=True, stdout=subprocess.DEVNULL)
    F = json.loads((OUT / "functional_route.json").read_text())["results"]
    out = {}
    for name, r in zip(names, F):
        L = r["layers"]
        out[name] = {"matched": [l["matched"] for l in L], "deep_matched": float(np.mean([L[l]["matched"] for l in DEEP])),
                     "deep_random97.5": float(np.mean([l["random95"][1] for l in L[6:]])),
                     "deep_reliab": [float(np.mean([l["reliab_A"] for l in L[6:]])), float(np.mean([l["reliab_B"] for l in L[6:]]))],
                     "deep_ratio": float(np.mean([l["ratio"] for l in L[6:]]))}
    return out


# ------------------------------------------------------------------ (iii) E170 cell decomposition (functions verbatim)
def decomp(skip):
    cache = OUT / f"decomp_{END}.json"
    pairs = {n: (a, b) for n, (a, b, _) in RECIPES.items() if have("routing", a, END) and have("routing", b, END)}
    if skip and cache.exists():
        return json.loads(cache.read_text())
    P = np.load(A / "routing/pairs.npz")
    pi, pj, ptype = P["i"], P["j"], P["type"]
    nT = int(ptype.max()) + 1
    ann = json.loads((WB / "results/e167/ud_annotations.json").read_text())
    AN = [ann[int(w)] for w in P["anchor_word"]]
    posclass = lambda a: "init" if a["sent_init"] else ("final" if a["sent_final"] else "mid")
    VARS = {"upos": [a["upos"] for a in AN], "deprel": [a["deprel"] for a in AN], "head_upos": [a["head_upos"] for a in AN],
            "prev_upos": [a["prev_upos"] for a in AN], "next_upos": [a["next_upos"] for a in AN],
            "sentpos": [posclass(a) for a in AN], "feats": [a["feats"] for a in AN], "genre": [a["genre"] for a in AN],
            "doc": [a["doc_id"] for a in AN]}
    ENC = {k: np.unique(np.array(v), return_inverse=True)[1] for k, v in VARS.items()}
    MIN_CELL, N_PERM = 3, 20

    def cw(x):
        s = np.bincount(ptype, x, nT); c = np.bincount(ptype, None, nT)
        return x - (s / np.maximum(c, 1))[ptype]

    def cells_for(lab):
        la, lb = lab[pi], lab[pj]
        lo, hi = np.minimum(la, lb), np.maximum(la, lb)
        key = (ptype.astype(np.int64) * (lab.max() + 1) + lo) * (lab.max() + 1) + hi
        _, cid, cnt = np.unique(key, return_inverse=True, return_counts=True)
        return cid, cnt[cid]

    def cell_mean(x, cid, cnt):
        s = np.bincount(cid, x); n = np.bincount(cid)
        m = (s / np.maximum(n, 1))[cid]
        m[cnt < MIN_CELL] = 0.0
        return m

    def corr(a, b):
        a = a - a.mean(); b = b - b.mean()
        return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-30))

    def cov(a, b):
        return float(((a - a.mean()) * (b - b.mean())).mean())

    def loadD(run):
        Z = np.load(A / "routing" / f"{run}__ckpt_{END}.npz")
        return {l: cw(Z[f"C{l}"].astype(float) - Z[f"B{l}"].astype(float)) for l in DEEP}

    rng = np.random.default_rng(173)
    wtype = np.unique(P["anchor_type"], return_inverse=True)[1]
    type_idx = [np.where(wtype == t)[0] for t in np.unique(wtype)]
    perm_cells = {}
    for k in VAR_ORDER:
        lab, pcs = ENC[k], []
        for _ in range(N_PERM):
            perm = np.arange(len(lab))
            for idx in type_idx:
                perm[idx] = idx[rng.permutation(len(idx))]
            pcs.append(cells_for(lab[perm]))
        perm_cells[k] = pcs
    cells = {k: cells_for(ENC[k]) for k in VAR_ORDER}
    out = {"tokens": END, "min_cell": MIN_CELL, "n_perm": N_PERM, "layers": DEEP, "pairs": {}}
    for name, (a, b) in pairs.items():
        DA, DB = loadD(a), loadD(b)
        rec = {}
        for k in VAR_ORDER:
            cid, cnt = cells[k]
            sh, cc, rc, tot, p95 = [], [], [], [], []
            for l in DEEP:
                xa, xb = DA[l], DB[l]
                ma, mb = cell_mean(xa, cid, cnt), cell_mean(xb, cid, cnt)
                cab = cov(xa, xb)
                sh.append(cov(ma, mb) / cab); cc.append(corr(ma, mb)); rc.append(corr(xa - ma, xb - mb)); tot.append(corr(xa, xb))
                p95.append(float(np.percentile([cov(cell_mean(xa, c, n), cell_mean(xb, c, n)) / cab for c, n in perm_cells[k]], 95)))
            rec[k] = {"share": float(np.mean(sh)), "share_perm95": float(np.mean(p95)), "cellcorr": float(np.mean(cc)),
                      "residcorr": float(np.mean(rc)), "T": float(np.mean(tot)), "coverage": float((cnt >= MIN_CELL).mean())}
        top = sorted(VAR_ORDER, key=lambda k: -rec[k]["share"])
        out["pairs"][name] = {"vars": rec, "top3_share": top[:3]}
        print(f"decomp {name:7s} top3 " + ", ".join(f"{k} {rec[k]['share']:.2f}" for k in top[:3]), flush=True)
    if "base" in out["pairs"]:
        bs = [out["pairs"]["base"]["vars"][k]["share"] for k in VAR_ORDER]
        b3 = set(out["pairs"]["base"]["top3_share"])
        for name, r in out["pairs"].items():
            rs = [r["vars"][k]["share"] for k in VAR_ORDER]
            r["spearman_vs_base"] = float(spearmanr(bs, rs).correlation)
            r["top3_overlap_base"] = len(b3 & set(r["top3_share"]))
    cache.write_text(json.dumps(out, indent=1))
    return out


# ------------------------------------------------------------------ (iv) losses and training health
def health(run):
    d = run_dir(run)
    if not (d / "train_log.jsonl").exists():
        return None
    rows = [json.loads(l) for l in open(d / "train_log.jsonl")]
    steps = [r for r in rows if "step" in r and r["step"] <= 3052]
    h3000 = next((r["held_ce"] for r in steps if r["step"] == 3000 and "held_ce" in r), None)
    fin = json.loads((d / "DONE.json").read_text()) if (d / "DONE.json").exists() and "_" in run else None
    late = [r for r in steps if r["step"] >= 2500]
    held_by_step = {r["step"]: r["held_ce"] for r in steps if "held_ce" in r}  # every 500 steps (lcm of log 20, eval 250)
    # same data_seed -> identical batches at identical steps, so windowed train CE is batch-matched across runs
    win = {f"{a}-{b}": float(np.mean([r["ce"] for r in steps if a < r["step"] <= b])) for a, b in WINDOWS
           if steps and steps[-1]["step"] >= b}
    return {"held_ce_3000": h3000, "held_by_step": held_by_step, "train_ce_window": win, "held_ce_end": fin["held_ce"] if fin else None, "last_step": steps[-1]["step"] if steps else 0,
            "dead_max": max((r["dead"] for r in steps), default=None), "dead_late_max": max((r["dead"] for r in late), default=None),
            "maxload_late_mean": float(np.mean([np.mean(r["maxload"]) for r in late])) if late else None,
            "tok_s_median": float(np.median([r["tok_s"] for r in steps if r.get("tok_s")])) if steps else None,
            "nan": any(not np.isfinite(r["ce"]) for r in steps)}


def ud_nll(run):
    f = A / "functional" / f"{run}__ckpt_{END}.npz"
    return float(np.load(f)["base_nll"]) if f.exists() else None


# ------------------------------------------------------------------ main
def main():
    skip_r = "--skip-routing" in sys.argv
    T = routing(skip_r)
    rule = ruler()
    RF = route_fp()
    DC = decomp("--skip-decomp" in sys.argv)
    summary = {"ruler_15pairs": rule, "recipes": {}}
    for name, (a, b, label) in RECIPES.items():
        if name not in T and health(a) is None:
            continue
        hA, hB = health(a), health(b)
        rec = {"label": label, "runs": [a, b], "routing": T.get(name, {}), "route_fp": RF.get(name),
               "decomp": DC["pairs"].get(name) if DC else None, "health": {a: hA, b: hB},
               "ud_nll": [ud_nll(a), ud_nll(b)]}
        summary["recipes"][name] = rec
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
    # markdown table
    f2 = lambda x: "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.3f}"
    lines = ["| 配方 | held CE @3000 步（seed0 / seed1） | L11 T_D @8 亿 [CI] | 深层 L6–11 T_D | 自身 step-0 地板 L11 / 深层 | route 指纹深层 | UD share 前三（share） | share Spearman vs 基线 |",
             "|---|---|---|---|---|---|---|---|"]
    for name, r in summary["recipes"].items():
        t8, t0 = r["routing"].get(END), r["routing"].get(0)
        h = [r["health"][x]["held_ce_3000"] if r["health"][x] else None for x in r["runs"]]
        dc = r["decomp"]
        top = ", ".join(f"{k} {dc['vars'][k]['share']:.2f}" for k in dc["top3_share"]) if dc else "—"
        lines.append(f"| {r['label']} | {f2(h[0])} / {f2(h[1])} | "
                     + (f"{t8['L11']:.3f} [{t8['L11_ci'][0]:.3f}, {t8['L11_ci'][1]:.3f}] | {t8['deep']:.3f}" if t8 else "— | —")
                     + f" | {(f2(t0['L11']) + ' / ' + f2(t0['deep'])) if t0 else '—'} | {f2(r['route_fp']['deep_matched']) if r['route_fp'] else '—'} | {top} | "
                     + (f"{dc['spearman_vs_base']:.2f}（前三重合 {dc['top3_overlap_base']}）" if dc and "spearman_vs_base" in dc else "—") + " |")
    r8 = rule.get(END)
    if r8:
        lines.append(f"\n尺子：基线 15 个只换初始化对在 8 亿处 L11 {r8['L11'][0]:.3f}–{r8['L11'][2]:.3f}（均值 {r8['L11'][1]:.3f}），深层 {r8['deep'][0]:.3f}–{r8['deep'][2]:.3f}（均值 {r8['deep'][1]:.3f}）。")
    # held-out CE aligned by step, and batch-matched train CE windows (seed0 / seed1)
    lines += ["", "按步对齐的留出 CE（同一 128 个留出窗口；seed0 / seed1）：", "",
              "| 配方 | " + " | ".join(f"{s_} 步" for s_ in HELD_STEPS) + " |", "|---|" + "---|" * len(HELD_STEPS)]
    for name, r in summary["recipes"].items():
        cells = []
        for s_ in HELD_STEPS:
            v = [r["health"][x]["held_by_step"].get(s_) if r["health"][x] else None for x in r["runs"]]
            cells.append(" / ".join(f2(x) for x in v))
        lines.append(f"| {r['label']} | " + " | ".join(cells) + " |")
    lines += ["", "同批训练 CE 窗口均值（同 data_seed，同一步看到同一批数据；seed0 / seed1）：", "",
              "| 配方 | " + " | ".join(f"{a}–{b} 步" for a, b in WINDOWS) + " |", "|---|" + "---|" * len(WINDOWS)]
    for name, r in summary["recipes"].items():
        cells = []
        for a, b in WINDOWS:
            v = [r["health"][x]["train_ce_window"].get(f"{a}-{b}") if r["health"][x] else None for x in r["runs"]]
            cells.append(" / ".join(f2(x) for x in v))
        lines.append(f"| {r['label']} | " + " | ".join(cells) + " |")
    (OUT / "table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("\nT_D curves (L11 / deep):")
    for name, r in summary["recipes"].items():
        print(f"{name:7s} " + "  ".join(f"{t/1e8:.0f}e8 {v['L11']:.3f}/{v['deep']:.3f}" for t, v in sorted(r["routing"].items())))


if __name__ == "__main__":
    main()
