"""E29: QA-format switch over pretraining (Flan pair, 3 seeds, intermediate checkpoints).

Usage: e29_timecourse.py --repo allenai/DataDecide-dolma1_7-1B --seed default --step 7500 ; e29_timecourse.py --analyze
"""
import argparse
import json

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e29"
STEPS = [2500, 7500, 17500, 35000, 69369]
RECS = ("dolma1_7-1B", "dolma1_7-no-flan-1B")


def compute(repo, seed, step):
    import torch
    import dd_common as dd
    import e18_trait as e18
    import e26_factorial as e26
    from e20_recipe import cand_logprob
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(step, seed), dtype=torch.bfloat16)
    R = e18.rows()
    ct = cand_logprob(model, tok, [r["clean"] for r in R], [r["ans"] for r in R])
    cd = cand_logprob(model, tok, [r["clean"] for r in R], [r["dist"] for r in R])
    built = [e26.build(r)[0] for r in R]
    res = {"repo": repo, "seed": seed, "step": step, "known": [int(i) for i in np.where(ct > cd)[0]],
           "clean": (ct - cd).round(4).tolist(), "cells": {}}
    for c in ("c1_decl", "c1_qa"):
        P = [b[c] for b in built]
        lt = cand_logprob(model, tok, P, [r["ans"] for r in R])
        ld = cand_logprob(model, tok, P, [r["dist"] for r in R])
        res["cells"][c] = (ld - lt).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    (OUT / f"{repo.split('DataDecide-')[1]}__{seed}__{step}.json").write_text(json.dumps(res))
    kn = res["known"]
    print(repo, seed, step, "n_known", len(kn), {c: round(float(np.mean(np.array(v)[kn])), 2) for c, v in res["cells"].items()},
          "K", round(float(np.mean(res["clean"])), 2), flush=True)


def load(r, s, step):
    if step == 69369:  # final checkpoint: reuse E26 (same cells, same items); clean from E20
        d = json.loads((mc.RESULTS / "e26" / f"{r}__{s}.json").read_text())
        return {"known": d["known"], "cells": d["cells"], "clean": None}
    return json.loads((OUT / f"{r}__{s}__{step}.json").read_text())


def analyze():
    import dd_common as dd
    import e18_trait as e18
    R = e18.rows()
    cats = sorted({r["cat"] for r in R})
    out = {"steps": {}}
    Kpos = {}
    for step in STEPS:
        D = {(r, s): load(r, s, step) for r in RECS for s in dd.SEEDS}
        sh = sorted(set.intersection(*[set(d["known"]) for d in D.values()]))
        by = [[i for i in sh if R[i]["cat"] == c] for c in cats]
        m = lambda d, c: float(np.mean([np.mean(np.array(d["cells"][c])[ix]) for ix in by if len(ix) >= 10]))
        row = {"n_shared": len(sh)}
        for name, f in (("FE_c1", lambda d: m(d, "c1_qa") - m(d, "c1_decl")), ("decl", lambda d: m(d, "c1_decl")),
                        ("qa", lambda d: m(d, "c1_qa"))):
            a = np.array([f(D[(RECS[0], s)]) for s in dd.SEEDS])
            b = np.array([f(D[(RECS[1], s)]) for s in dd.SEEDS])
            se = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2) * np.sqrt(2 / 3)
            row[name] = {"flan": a.mean(), "noflan": b.mean(), "delta": a.mean() - b.mean(), "se": se,
                         "sig": bool(abs(a.mean() - b.mean()) > 2 * se) if name == "decl" else bool(a.mean() - b.mean() > 2 * se)}
        for k, d in D.items():
            if d["clean"] is not None:  # category-equal-weighted, same definition as E20 clean_margin averaged
                cl = np.array(d["clean"])
                Kpos.setdefault(k, {})[step] = float(np.mean([cl[[i for i, r in enumerate(R) if r["cat"] == c]].mean()
                                                             for c in cats]))
        out["steps"][step] = row
    for k in Kpos:  # final K from E20 (clean margin over all items, same definition)
        c = json.loads((mc.RESULTS / "e20" / f"{k[0]}__{k[1]}.json").read_text())["conditions"]
        Kpos[k][69369] = float(np.mean([v["clean_margin"] for v in c.values()]))
    out["positive_control_K_rises"] = bool(all(v[69369] > v[2500] for v in Kpos.values()))
    out["K_by_model"] = {f"{k[0]}__{k[1]}": v for k, v in Kpos.items()}
    present = [s for s in STEPS if out["steps"][s]["FE_c1"]["sig"]]
    out["earliest_present"] = present[0] if present else None
    out["persists_after_onset"] = bool(present and all(out["steps"][s]["FE_c1"]["sig"] for s in STEPS if s >= present[0]))
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--seed", default="default")
    ap.add_argument("--step", type=int)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    analyze() if a.analyze else compute(a.repo, a.seed, a.step)
