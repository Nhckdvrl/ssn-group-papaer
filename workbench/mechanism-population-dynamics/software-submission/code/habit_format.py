"""habit_format: 4 contexts x 2 endings factorial on ParaConflict items.

Usage: habit_format.py --check              (CPU: build prompts, verify mention counts / length matching)
       habit_format.py --repo allenai/DataDecide-dolma1_7-1B --seed default
       habit_format.py --analyze
"""
import argparse
import json

import numpy as np

import common as mc
from prompts import FILLER, build

OUT = mc.RESULTS / "habit_format"
CELLS = [f"{c}_{e}" for c in ("c1", "cK", "cP", "cF") for e in ("decl", "qa")]






def check():
    import prompts
    R = prompts.rows()
    bad, stats = [], []
    for r in R:
        cells, k = build(r)
        m = {c: cells[c].count(r["dist"]) for c in CELLS}
        exp = {"c1": 1, "cK": k, "cP": k, "cF": 1}
        ok = all(m[c] == exp[c.split("_")[0]] for c in CELLS) and k >= 1
        ok &= all(w not in FILLER for w in (r["dist"], r["ans"]) if " " not in w) and r["ans"] not in " ".join(FILLER)
        wp, wf = len(cells["cP_decl"].split()), len(cells["cF_decl"].split())
        stats.append((k, wp, wf, len(cells["c1_decl"].split()), len(cells["cK_decl"].split())))
        if not ok or abs(wp - wf) > 15:
            bad.append((r["cat"], r["subj"], m, wp, wf))
    s = np.array(stats)
    print("items", len(R), "bad", len(bad), bad[:3])
    print("k mean/min/max", s[:, 0].mean(), s[:, 0].min(), s[:, 0].max(), "| words cP", s[:, 1].mean(), "cF", s[:, 2].mean(),
          "c1", s[:, 3].mean(), "cK", s[:, 4].mean(), "| max |cP-cF| words", np.abs(s[:, 1] - s[:, 2]).max())
    r = R[0]
    cells, _ = build(r)
    for c in CELLS:
        print(f"--- {c}: {cells[c][:160]!r} ... {cells[c][-90:]!r}")
    return len(bad) == 0


def compute(repo, seed):
    import torch
    import datadecide as dd
    import prompts
    from prompts import cand_logprob
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16)
    R = prompts.rows()
    clean_t = cand_logprob(model, tok, [r["clean"] for r in R], [r["ans"] for r in R])
    clean_d = cand_logprob(model, tok, [r["clean"] for r in R], [r["dist"] for r in R])
    built = [build(r)[0] for r in R]
    res = {"repo": repo, "seed": seed, "known": [int(i) for i in np.where(clean_t > clean_d)[0]], "cells": {}}
    for c in CELLS:
        P = [b[c] for b in built]
        bs = 8 if c.startswith(("cP", "cF")) else 32
        lt = cand_logprob(model, tok, P, [r["ans"] for r in R], bs=bs)
        ld = cand_logprob(model, tok, P, [r["dist"] for r in R], bs=bs)
        res["cells"][c] = (ld - lt).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    name = f"{repo.split('DataDecide-')[1]}__{seed}.json"
    (OUT / name).write_text(json.dumps(res))
    kn = res["known"]
    print(name, {c: round(float(np.mean(np.array(v)[kn])), 2) for c, v in res["cells"].items()}, flush=True)


def analyze():
    import datadecide as dd
    import prompts
    R = prompts.rows()
    cats = sorted({r["cat"] for r in R})
    recs = ["dolma1_7-1B", "dolma1_7-no-flan-1B"]
    D = {(r, s): json.loads((OUT / f"{r}__{s}.json").read_text()) for r in recs for s in dd.SEEDS}
    shared = sorted(set.intersection(*[set(d["known"]) for d in D.values()]))
    by_cat = {c: [i for i in shared if R[i]["cat"] == c] for c in cats}

    def cell_mean(d, c):  # equal weight per category (as habit_format)
        v = np.array(d["cells"][c])
        return float(np.mean([v[ix].mean() for ix in by_cat.values() if len(ix) >= 10]))

    def contrasts(d):
        m = {c: cell_mean(d, c) for c in CELLS}
        avg = lambda ctx: (m[f"{ctx}_decl"] + m[f"{ctx}_qa"]) / 2
        return {"format": np.mean([m[f"{c}_qa"] - m[f"{c}_decl"] for c in ("c1", "cK", "cP", "cF")]),
                "count": avg("cK") - avg("c1"), "discourse": avg("cP") - avg("cK"), "length": avg("cF") - avg("c1"),
                **{f"cell:{c}": m[c] for c in CELLS}}

    C = {k: contrasts(d) for k, d in D.items()}
    # extra recipes only for the pooled seed SD (each on its own 3-seed shared-known items)
    extra = {}
    for r in ("c4-1B", "dclm-baseline-1B"):
        Dx = {s: json.loads((OUT / f"{r}__{s}.json").read_text()) for s in dd.SEEDS}
        sh = sorted(set.intersection(*[set(d["known"]) for d in Dx.values()]))
        bc = {c: [i for i in sh if R[i]["cat"] == c] for c in cats}
        saved = dict(by_cat)
        by_cat.clear(); by_cat.update(bc)
        extra[r] = [contrasts(Dx[s]) for s in dd.SEEDS]
        by_cat.clear(); by_cat.update(saved)
    out = {"n_shared_items": {c: len(v) for c, v in by_cat.items()},
           "positive_control_count_all_positive": bool(all(v["count"] > 0 for v in C.values())), "contrasts": {}}
    for x in C[next(iter(C))]:
        a = np.array([C[("dolma1_7-1B", s)][x] for s in dd.SEEDS])
        b = np.array([C[("dolma1_7-no-flan-1B", s)][x] for s in dd.SEEDS])
        ex = [np.array([e[x] for e in extra[r]]) for r in extra]
        sd = np.sqrt(np.mean([v.var(ddof=1) for v in [a, b] + ex]))  # pooled over 4 recipes, df = 8
        se = sd * np.sqrt(1 / 3 + 1 / 3)
        out["contrasts"][x] = {"flan": a.mean(), "noflan": b.mean(), "delta": a.mean() - b.mean(), "se": se,
                               "sig": bool(a.mean() - b.mean() > 2 * se)}
    X = ["format", "count", "discourse", "length"]
    sig = [x for x in X if out["contrasts"][x]["sig"]]
    dl = {x: out["contrasts"][x]["delta"] for x in X}
    out["attribution"] = (sig[0] if len(sig) == 1 and all(dl[sig[0]] >= 2 * abs(dl[y]) for y in X if y != sig[0])
                          else ("multi:" + ",".join(sig) if sig else "none"))
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--seed", default="default")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    check() if a.check else analyze() if a.analyze else compute(a.repo, a.seed)
