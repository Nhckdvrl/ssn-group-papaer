"""habit_heads: is the data-installed Flan switch implemented in init-determined heads?

Per-head mean-ablation (ablation_transfer Ablator) effect on the format effect FE = margin(c1_qa) - margin(c1_decl), on the retrieval probe items
(20 per category, 120 items), stored per item half for split-half reliability.
  habit_heads.py --recipe dolma1_7-no-code --seed default
  habit_heads.py --analyze
"""
import argparse
import itertools
import json

import numpy as np

import common as mc
OUT = mc.RESULTS / "habit_heads"
FLAN = ("dolma1_7", "dolma1_7-no-code", "dolma1_7-no-math-code", "dolma1_7-no-reddit")
NOFLAN = ("dolma1_7-no-flan",)


def compute(recipe, seed):
    from prompts import cand_logprob
    import prompts
    from ablation_transfer import setup
    f = OUT / f"{recipe}__{seed}.json"
    if f.exists():
        return
    model, tok, ab, *_ = setup(recipe, seed)
    R, ix = prompts.items()
    rng = np.random.default_rng(0)
    sub = []
    for c in sorted({R[i]["cat"] for i in ix}):
        cix = [i for i in ix if R[i]["cat"] == c]
        sub += sorted(rng.choice(cix, min(20, len(cix)), replace=False).tolist())  # same 120 items as ablation_transfer
    cells = [prompts.build(R[i])[0] for i in sub]
    D, A = [R[i]["dist"] for i in sub], [R[i]["ans"] for i in sub]
    half = np.arange(len(sub)) % 2

    def fe():
        m = {}
        for c in ("c1_decl", "c1_qa"):
            P = [x[c] for x in cells]
            m[c] = cand_logprob(model, tok, P, D, bs=60) - cand_logprob(model, tok, P, A, bs=60)
        v = m["c1_qa"] - m["c1_decl"]
        return [float(v[half == h].mean()) for h in (0, 1)], [float(m[c].mean()) for c in ("c1_decl", "c1_qa")]
    ab.set([])
    base, base_cells = fe()
    maps = np.zeros((2, ab.L, ab.H))
    cell_maps = np.zeros((2, ab.L, ab.H))  # per-head effect on the decl / qa margins (all items)
    for l, h in itertools.product(range(ab.L), range(ab.H)):
        ab.set([l * ab.H + h])
        v, cm = fe()
        maps[:, l, h] = np.array(v) - np.array(base)
        cell_maps[:, l, h] = np.array(cm) - np.array(base_cells)
    OUT.mkdir(exist_ok=True)
    f.write_text(json.dumps({"recipe": recipe, "seed": seed, "base_fe_halves": base, "base_cells": base_cells,
                             "fe_attr_halves": maps.round(6).tolist(), "decl_qa_attr": cell_maps.round(6).tolist()}))
    print(recipe, seed, "FE", np.round(base, 3), "min attr", float(maps.mean(0).min()), flush=True)


def analyze():
    import datadecide as dd
    from scipy.stats import spearmanr
    keys = [(r, s) for r in FLAN + NOFLAN for s in dd.SEEDS]
    D = {k: json.loads((OUT / f"{k[0]}__{k[1]}.json").read_text()) for k in keys if (OUT / f"{k[0]}__{k[1]}.json").exists()}
    A = {k: -np.array(v["fe_attr_halves"]) for k, v in D.items()}  # support for the switch = FE drop when ablated
    out = {"n_models": len(D)}
    out["split_half_reliability"] = {f"{k[0]}__{k[1]}": float(spearmanr(a[0].ravel(), a[1].ravel())[0]) for k, a in A.items()}
    out["base_fe"] = {f"{k[0]}__{k[1]}": float(np.mean(v["base_fe_halves"])) for k, v in D.items()}
    cls = lambda a, b: "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
    within = lambda a, b: float(np.nanmean([spearmanr(a[l], b[l])[0] for l in range(a.shape[0])]))
    fk = [k for k in A if k[0] in FLAN]
    g = {"SI": [], "SD": [], "DD": []}
    gw = {"SI": [], "SD": [], "DD": []}
    for a, b in itertools.combinations(fk, 2):
        x, y = A[a].mean(0), A[b].mean(0)
        g[cls(a, b)].append(float(spearmanr(x.ravel(), y.ravel())[0]))
        gw[cls(a, b)].append(within(x, y))
    out["flan_models_fe_attr"] = {"full": {c: float(np.mean(v)) for c, v in g.items()},
                                  "within_layer": {c: float(np.mean(v)) for c, v in gw.items()},
                                  "n": {c: len(v) for c, v in g.items()}}
    # Flan switch heads vs the same-init no-Flan model's general context-adoption heads (ablation_transfer-style C4_decl support)
    rows = []
    sup = {k[1]: -np.array(D[k]["decl_qa_attr"][0]) for k in D if k[0] == "dolma1_7-no-flan"}
    for s in dd.SEEDS:
        for r in FLAN:
            if (r, s) in A:
                for s2, m in sup.items():
                    rows.append({"same_init": s == s2, "rho": float(spearmanr(A[(r, s)].mean(0).ravel(), m.ravel())[0])})
    if rows:
        out["switch_vs_noflan_adoption_heads"] = {
            "same_init": float(np.mean([r["rho"] for r in rows if r["same_init"]])),
            "diff_init": float(np.mean([r["rho"] for r in rows if not r["same_init"]])), "n": len(rows)}
    OUT.mkdir(exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipe")
    ap.add_argument("--seed")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.recipe, a.seed)
