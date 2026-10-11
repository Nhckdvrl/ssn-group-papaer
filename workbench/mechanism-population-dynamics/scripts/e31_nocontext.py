"""E31: QA-format effect without conflicting context (control for C04). Protocol: experiments/E31-*.md.

Usage: e31_nocontext.py --check ; e31_nocontext.py --repo allenai/DataDecide-dolma1_7-1B --seed default ; --analyze
"""
import argparse
import json

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e31"
CELLS = ("n_decl", "n_qa", "f_decl", "f_qa")
RECS = ("dolma1_7-1B", "dolma1_7-no-flan-1B", "c4-1B", "dclm-baseline-1B")


def build(r):
    import e26_factorial as e26
    coh = r["Coherent Conflict"]
    i = coh.rfind(" Question:")
    P, tail = coh[:i].strip(), coh[i + len(" Question:"):]
    q, stem = (x.strip() for x in tail.split(" Answer:"))
    sub = r["Substitution Conflict"]
    S = sub[:sub.find(r["dist"]) + len(r["dist"])].strip()
    F = e26.filler(max(0, len(P.split()) - len(S.split())))  # identical filler to E26 cF, without S
    qa = "Question: " + q + " Answer: " + stem
    return {"n_decl": stem, "n_qa": qa, "f_decl": (F + " " + stem).strip(), "f_qa": (F + " " + qa).strip()}


def check():
    import e18_trait as e18
    R = e18.rows()
    bad = [r["subj"] for r in R if any(r["dist"] in v for v in build(r).values())]
    print("items", len(R), "cells containing the distractor (must be 0):", len(bad))
    for k, v in build(R[0]).items():
        print(f"--- {k}: ...{v[-120:]!r}")
    return not bad


def compute(repo, seed):
    import torch
    import dd_common as dd
    import e18_trait as e18
    from e20_recipe import cand_logprob
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16)
    R = e18.rows()
    B = [build(r) for r in R]
    res = {"repo": repo, "seed": seed, "cells": {}}
    for c in CELLS:
        P = [b[c] for b in B]
        bs = 8 if c.startswith("f") else 32
        res["cells"][c] = (cand_logprob(model, tok, P, [r["ans"] for r in R], bs=bs)
                           - cand_logprob(model, tok, P, [r["dist"] for r in R], bs=bs)).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    (OUT / f"{repo.split('DataDecide-')[1]}__{seed}.json").write_text(json.dumps(res))
    print(repo, seed, {c: round(float(np.mean(v)), 2) for c, v in res["cells"].items()}, flush=True)


def analyze():
    import dd_common as dd
    import e18_trait as e18
    R = e18.rows()
    cats = sorted({r["cat"] for r in R})
    known = [set(json.loads((mc.RESULTS / "e26" / f"{r}__{s}.json").read_text())["known"])
             for r in RECS[:2] for s in dd.SEEDS]
    sh = sorted(set.intersection(*known))
    by = [[i for i in sh if R[i]["cat"] == c] for c in cats]

    def nfe(d):
        m = {c: float(np.mean([np.mean(np.array(d["cells"][c])[ix]) for ix in by if len(ix) >= 10])) for c in CELLS}
        return {"NFE": ((m["n_qa"] - m["n_decl"]) + (m["f_qa"] - m["f_decl"])) / 2, **m}
    E = {(r, s): nfe(json.loads((OUT / f"{r}__{s}.json").read_text())) for r in RECS for s in dd.SEEDS}
    out = {"n_shared": len(sh), "positive_control_memory_margin_positive": bool(all(v["n_decl"] > 0 for v in E.values()))}
    for k in ("NFE",) + CELLS:
        v = {r: np.array([E[(r, s)][k] for s in dd.SEEDS]) for r in RECS}
        sd = np.sqrt(np.mean([x.var(ddof=1) for x in v.values()]))
        se = sd * np.sqrt(2 / 3)
        out[k] = {"flan": v[RECS[0]].mean(), "noflan": v[RECS[1]].mean(), "delta": v[RECS[0]].mean() - v[RECS[1]].mean(), "se": se}
    d, se = out["NFE"]["delta"], out["NFE"]["se"]
    out["context_specific"] = bool(abs(d) < 2 * se and abs(d) < 0.74)
    out["general_answer_mode"] = bool(abs(d) > 2 * se)
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
