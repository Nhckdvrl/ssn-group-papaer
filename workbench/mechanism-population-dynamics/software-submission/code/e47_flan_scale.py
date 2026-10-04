"""E47: does the Flan-installed "Question:" switch exist across DataDecide sizes?

  e47_flan_scale.py --repo allenai/DataDecide-dolma1_7-300M --rev step45787-seed-default --name 300M__dolma1_7__default
  e47_flan_scale.py --analyze
Readout = E32 cells (adoption margin lp(dist) - lp(ans), EOS start) + clean knowledge (lp(ans) > lp(dist) on the clean
prompt). Items: shared-known by all 6 models of a size (2 recipes x 3 seeds); category-equal weighting (as E26/E32).
"""
import argparse
import json

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e47"
SIZES = ("60M", "90M", "150M", "300M", "530M", "750M")
SEEDS = ("default", "small-aux-2", "small-aux-3")


def compute(repo, rev, name):
    import torch
    import dd_common as dd
    import e18_trait as e18
    from e20_recipe import cand_logprob
    from e32_cues import CELLS, build_all
    f = OUT / f"{name}.json"
    if f.exists():
        return
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, rev, dtype=torch.bfloat16)
    R = e18.rows()
    B = build_all(R)
    D, A = [r["dist"] for r in R], [r["ans"] for r in R]
    clean = [r["clean"] for r in R]
    res = {"repo": repo, "rev": rev, "known": np.flatnonzero(cand_logprob(model, tok, clean, A)
                                                             > cand_logprob(model, tok, clean, D)).tolist(), "cells": {}}
    for c in CELLS:
        P = [b[c] for b in B]
        res["cells"][c] = (cand_logprob(model, tok, P, D) - cand_logprob(model, tok, P, A)).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    f.write_text(json.dumps(res))
    print(name, "known", len(res["known"]), {c: round(float(np.mean(v)), 2) for c, v in res["cells"].items()}, flush=True)


def analyze():
    import e18_trait as e18
    from e32_cues import CELLS
    R = e18.rows()
    cats = sorted({r["cat"] for r in R})
    out = {}
    for size in SIZES:
        files = {(rec, s): OUT / f"{size}__{rec}__{s}.json" for rec in ("dolma1_7", "dolma1_7-no-flan") for s in SEEDS}
        if not all(f.exists() for f in files.values()):
            continue
        D = {k: json.loads(f.read_text()) for k, f in files.items()}
        sh = sorted(set.intersection(*[set(d["known"]) for d in D.values()]))
        by = [[i for i in sh if R[i]["cat"] == c] for c in cats]
        by = [ix for ix in by if len(ix) >= 10]

        def eff(d):
            m = {c: float(np.mean([np.mean(np.array(d["cells"][c])[ix]) for ix in by])) for c in CELLS}
            return {**{c: m[c] - m["decl"] for c in CELLS if c != "decl"}, "decl_level": m["decl"]}
        E = {k: eff(d) for k, d in D.items()} if by else {}
        row = {"n_shared_known": len(sh), "n_categories_used": len(by), "cells": {}}
        for c in [c for c in CELLS if c != "decl"] + ["decl_level"]:
            if not E:
                break
            v = {rec: np.array([E[(rec, s)][c] for s in SEEDS]) for rec in ("dolma1_7", "dolma1_7-no-flan")}
            se = np.sqrt((v["dolma1_7"].var(ddof=1) + v["dolma1_7-no-flan"].var(ddof=1)) / 2) * np.sqrt(2 / 3)
            d = v["dolma1_7"].mean() - v["dolma1_7-no-flan"].mean()
            row["cells"][c] = {"flan": float(v["dolma1_7"].mean()), "noflan": float(v["dolma1_7-no-flan"].mean()),
                               "delta": float(d), "se": float(se), "sig": bool(abs(d) > 2 * se)}
        out[size] = row
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    for size, row in out.items():
        c = row["cells"]
        print(size, "shared", row["n_shared_known"], {k: f"{v['delta']:+.2f}({v['se']:.2f}){'*' if v['sig'] else ''}"
                                                       for k, v in c.items()})


def batch(jobs, worker, nworkers):
    import time
    from census import available
    mine = [l.split() for j, l in enumerate(open(jobs)) if l.strip() and j % nworkers == worker]
    while True:
        left = 0
        for fam, repo, rev, out, name in mine:
            if (OUT / f"{name}.json").exists():
                continue
            left += 1
            if available(fam, repo, rev):
                try:
                    compute(repo, rev, name)
                except Exception as e:
                    print("ERROR", name, repr(e)[:200], flush=True)
        if left == 0:
            return
        time.sleep(60)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs")
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--nworkers", type=int, default=1)
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    ap.add_argument("--name")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.jobs:
        batch(a.jobs, a.worker, a.nworkers)
    else:
        analyze() if a.analyze else compute(a.repo, a.rev, a.name)
