"""E32: cue strength / abstraction / cue-vs-semantics of the Flan QA switch. Protocol: experiments/E32-*.md.

Usage: e32_cues.py --check ; e32_cues.py --repo allenai/DataDecide-dolma1_7-1B --seed default ; --analyze
"""
import argparse
import json

import numpy as np

import mp_common as mc

OUT = mc.RESULTS / "e32"
CELLS = ("decl", "A_only", "Q_only", "QA", "QA_short", "novel", "incongruent")
RECS = ("dolma1_7-1B", "dolma1_7-no-flan-1B", "c4-1B", "dclm-baseline-1B")


def parts(r):
    coh = r["Coherent Conflict"]
    i = coh.rfind(" Question:")
    q, stem = (x.strip() for x in coh[i + len(" Question:"):].split(" Answer:"))
    sub = r["Substitution Conflict"]
    S = sub[:sub.find(r["dist"]) + len(r["dist"])].strip()
    return S if S.endswith(".") else S + ".", q, stem


def build_all(R):
    by_cat = {}
    for i, r in enumerate(R):
        by_cat.setdefault(r["cat"], []).append(i)
    other = {}
    for c, ix in by_cat.items():  # q' = question of the next item (same category, fixed order) whose question
        for k, i in enumerate(ix):  # mentions neither this item's answer nor its distractor
            for step in range(1, len(ix)):
                j = ix[(k + step) % len(ix)]
                qj = parts(R[j])[1]
                if R[i]["ans"] not in qj and R[i]["dist"] not in qj and R[j]["subj"] != R[i]["subj"]:
                    other[i] = j
                    break
    out = []
    for i, r in enumerate(R):
        S, q, stem = parts(r)
        q2 = parts(R[other[i]])[1]
        out.append({"decl": f"{S} {stem}", "A_only": f"{S} Answer: {stem}", "Q_only": f"{S} Question: {q} {stem}",
                    "QA": f"{S} Question: {q} Answer: {stem}", "QA_short": f"{S} Q: {q} A: {stem}",
                    "novel": f"{S} Query: {q} Response: {stem}", "incongruent": f"{S} Question: {q2} Answer: {stem}"})
    return out


def check():
    import e18_trait as e18
    import e26_factorial as e26
    R = e18.rows()
    B = build_all(R)
    same = sum(B[i]["QA"] == e26.build(R[i])[0]["c1_qa"] for i in range(len(R)))
    qpart = lambda i: B[i]["incongruent"].split(" Question: ")[1].split(" Answer: ")[0]
    leak = sum(R[i]["dist"] in qpart(i) or R[i]["ans"] in qpart(i) for i in range(len(R)))
    print("items", len(R), "| QA identical to E26 c1_qa:", same, "| incongruent question leaks answer/distractor:", leak)
    for c in CELLS:
        print(f"--- {c}: {B[0][c]!r}")


def compute(repo, seed):
    import torch
    import dd_common as dd
    import e18_trait as e18
    from e20_recipe import cand_logprob
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16)
    R = e18.rows()
    B = build_all(R)
    res = {"repo": repo, "seed": seed, "cells": {}}
    for c in CELLS:
        P = [b[c] for b in B]
        res["cells"][c] = (cand_logprob(model, tok, P, [r["dist"] for r in R])
                           - cand_logprob(model, tok, P, [r["ans"] for r in R])).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    (OUT / f"{repo.split('DataDecide-')[1]}__{seed}.json").write_text(json.dumps(res))
    print(repo, seed, {c: round(float(np.mean(v)), 2) for c, v in res["cells"].items()}, flush=True)


def analyze():
    import dd_common as dd
    import e18_trait as e18
    R = e18.rows()
    cats = sorted({r["cat"] for r in R})
    known = [set(json.loads((mc.RESULTS / "e26" / f"{r}__{s}.json").read_text())["known"]) for r in RECS[:2] for s in dd.SEEDS]
    sh = sorted(set.intersection(*known))
    by = [[i for i in sh if R[i]["cat"] == c] for c in cats]

    def eff(d):
        m = {c: float(np.mean([np.mean(np.array(d["cells"][c])[ix]) for ix in by if len(ix) >= 10])) for c in CELLS}
        return {c: m[c] - m["decl"] for c in CELLS if c != "decl"}
    E = {(r, s): eff(json.loads((OUT / f"{r}__{s}.json").read_text())) for r in RECS for s in dd.SEEDS}
    out = {"n_shared": len(sh), "cells": {}}
    for c in CELLS[1:]:
        v = {r: np.array([E[(r, s)][c] for s in dd.SEEDS]) for r in RECS}
        se = np.sqrt(np.mean([x.var(ddof=1) for x in v.values()])) * np.sqrt(2 / 3)
        out["cells"][c] = {"flan": v[RECS[0]].mean(), "noflan": v[RECS[1]].mean(), "delta": v[RECS[0]].mean() - v[RECS[1]].mean(), "se": se}
    C = out["cells"]
    sed = lambda a, b: np.sqrt(C[a]["se"] ** 2 + C[b]["se"] ** 2)
    out["positive_control_QA"] = bool(C["QA"]["delta"] > 2 * C["QA"]["se"])
    out["P1_cue_strength"] = bool(C["QA"]["delta"] - C["A_only"]["delta"] > sed("QA", "A_only")
                                  and C["QA"]["delta"] - C["Q_only"]["delta"] > sed("QA", "Q_only"))
    out["P2_novel_triggers"] = bool(C["novel"]["delta"] > 2 * C["novel"]["se"])
    out["P2_template_only"] = bool(C["novel"]["delta"] < C["novel"]["se"] and C["QA_short"]["delta"] > 2 * C["QA_short"]["se"])
    out["P2_ratio_novel_over_QA"] = C["novel"]["delta"] / C["QA"]["delta"]
    out["P3_cue_driven"] = bool(C["incongruent"]["delta"] > 2 * C["incongruent"]["se"])
    out["P3_semantic"] = bool(C["incongruent"]["delta"] < C["incongruent"]["se"])
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
