"""habit_popqa: Flan QA-format switch on PopQA counterfactuals.

Usage: habit_popqa.py --check ; habit_popqa.py --repo allenai/DataDecide-dolma1_7-1B --seed default ; --analyze
"""
import argparse
import json

import numpy as np

import common as mc
OUT = mc.RESULTS / "habit_popqa"
RECS = ("dolma1_7-1B", "dolma1_7-no-flan-1B", "c4-1B", "dclm-baseline-1B")
STEM = {"occupation": "{s}'s occupation is", "place of birth": "{s} was born in", "genre": "The genre of {s} is",
        "father": "The father of {s} is", "country": "{s} is located in the country of", "producer": "The producer of {s} is",
        "director": "The director of {s} is", "capital of": "{s} is the capital of", "screenwriter": "The screenwriter of {s} is",
        "composer": "The composer of {s} is", "color": "The color of {s} is", "religion": "The religion of {s} is",
        "sport": "{s} plays the sport of", "author": "The author of {s} is", "mother": "The mother of {s} is",
        "capital": "The capital of {s} is"}


def items():
    from datasets import load_dataset
    ds = load_dataset("akariasai/PopQA", split="test")
    rng = np.random.default_rng(0)
    by = {}
    for i, (p, sj, ob, q) in enumerate(zip(ds["prop"], ds["subj"], ds["obj"], ds["question"])):
        if sj and ob and q:  # skip rows with missing subject / object / question
            by.setdefault(p, []).append(i)
    out = []
    for p in sorted(by):
        ix = sorted(rng.choice(by[p], min(150, len(by[p])), replace=False).tolist())
        rows = [ds[int(i)] for i in ix]
        for k, r in enumerate(rows):
            poss = set(json.loads(r["possible_answers"])) | {r["obj"]}
            dist = None
            for step in range(1, len(rows)):
                o = rows[(k + step) % len(rows)]["obj"]
                if o not in poss and o != r["obj"] and o not in r["subj"] and r["obj"] not in o:
                    dist = o
                    break
            if dist is None:
                continue
            stem = STEM[p].format(s=r["subj"])
            S = f"{stem} {dist}."
            out.append({"prop": p, "subj": r["subj"], "ans": r["obj"], "dist": dist, "clean": stem,
                        "decl": f"{S} {stem}", "qa": f"{S} Question: {r['question']} Answer: {stem}", "s_pop": r["s_pop"]})
    return out


def check():
    I = items()
    import collections
    print("items", len(I), dict(collections.Counter(x["prop"] for x in I)))
    bad = [x for x in I if x["dist"] == x["ans"] or x["qa"].count(x["dist"]) != 1 or x["decl"].count(x["dist"]) != 1]
    print("bad (distractor==answer or distractor count != 1):", len(bad))
    for x in I[:2] + I[-2:]:
        print(repr(x["qa"]))


def compute(repo, seed):
    import torch
    import datadecide as dd
    from prompts import cand_logprob
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16)
    I = items()
    A, Dd = [x["ans"] for x in I], [x["dist"] for x in I]
    clean = cand_logprob(model, tok, [x["clean"] for x in I], A) - cand_logprob(model, tok, [x["clean"] for x in I], Dd)
    res = {"repo": repo, "seed": seed, "known": [int(i) for i in np.where(clean > 0)[0]], "cells": {}}
    for c in ("decl", "qa"):
        P = [x[c] for x in I]
        res["cells"][c] = (cand_logprob(model, tok, P, Dd) - cand_logprob(model, tok, P, A)).round(4).tolist()
    OUT.mkdir(exist_ok=True)
    (OUT / f"{repo.split('DataDecide-')[1]}__{seed}.json").write_text(json.dumps(res))
    kn = res["known"]
    print(repo, seed, "known", len(kn), {c: round(float(np.mean(np.array(v)[kn])), 2) for c, v in res["cells"].items()}, flush=True)


def analyze():
    import datadecide as dd
    I = items()
    props = sorted({x["prop"] for x in I})
    D = {(r, s): json.loads((OUT / f"{r}__{s}.json").read_text()) for r in RECS for s in dd.SEEDS}
    sh = sorted(set.intersection(*[set(D[(r, s)]["known"]) for r in RECS[:2] for s in dd.SEEDS]))

    def eff(d, items_by):
        m = {c: float(np.mean([np.mean(np.array(d["cells"][c])[ix]) for ix in items_by if len(ix) >= 5])) for c in ("decl", "qa")}
        return {"FE": m["qa"] - m["decl"], "decl": m["decl"], "qa": m["qa"]}
    E = {}
    for r in RECS:
        shr = sorted(set.intersection(*[set(D[(r, s)]["known"]) for s in dd.SEEDS])) if r in RECS[2:] else sh
        byr = [[i for i in shr if I[i]["prop"] == p] for p in props]
        for s in dd.SEEDS:
            E[(r, s)] = eff(D[(r, s)], byr)
    out = {"n_items": len(I), "n_shared": len(sh),
           "pc_decl_adoption_gt_50": bool(all(float((np.array(D[(r, s)]["cells"]["decl"])[sh] > 0).mean()) > 0.5
                                              for r in RECS[:2] for s in dd.SEEDS))}
    for k in ("FE", "decl", "qa"):
        v = {r: np.array([E[(r, s)][k] for s in dd.SEEDS]) for r in RECS}
        se = np.sqrt(np.mean([x.var(ddof=1) for x in v.values()])) * np.sqrt(2 / 3)
        out[k] = {"flan": v[RECS[0]].mean(), "noflan": v[RECS[1]].mean(), "delta": v[RECS[0]].mean() - v[RECS[1]].mean(), "se": se}
    out["replicates"] = bool(out["FE"]["delta"] > 2 * out["FE"]["se"] and abs(out["decl"]["delta"]) < out["FE"]["delta"] / 2)
    out["adoption_rates_shared"] = {f"{r}__{s}": {c: float((np.array(D[(r, s)]["cells"][c])[sh] > 0).mean()) for c in ("decl", "qa")}
                                    for r in RECS[:2] for s in dd.SEEDS}
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
