"""E18: context-reliance per (run, ParaConflict category x conflict form). Protocol: experiments/E18-*.md.

Usage: e18_trait.py --repo EleutherAI/pythia-410m-seed3 ; e18_trait.py --analyze 410m|160m
"""
import argparse
import itertools
import json

import numpy as np
import torch
from datasets import load_dataset
from scipy.stats import spearmanr

import mp_common as mc
import e13_arbitration as e13

OUT = mc.RESULTS / "e18"
FORMS = ["Substitution Conflict", "Coherent Conflict"]


def rows():
    ds = load_dataset("gaotang/ParaConflict", split="test")
    out = []
    for r in ds:
        ans = r["Answer"] if isinstance(r["Answer"], list) else [r["Answer"]]
        out.append({"cat": r["Category"], "subj": r["Subject"], "ans": ans[0], "dist": r["Distracted Token"],
                    "clean": r["Clean Prompt"], **{f: r[f] for f in FORMS}})
    return out


def compute(repo):
    torch.set_grad_enabled(False)
    model = mc.load_tl_model(repo, 143000)
    R = rows()
    clean_t = e13.cand_logprob(model, [r["clean"] for r in R], [r["ans"] for r in R])
    clean_d = e13.cand_logprob(model, [r["clean"] for r in R], [r["dist"] for r in R])
    known = clean_t > clean_d
    res = {"repo": repo, "conditions": {}}
    for f in FORMS:
        P = [r[f] for r in R]
        lt = e13.cand_logprob(model, P, [r["ans"] for r in R], bs=16 if f == "Coherent Conflict" else 64)
        ld = e13.cand_logprob(model, P, [r["dist"] for r in R], bs=16 if f == "Coherent Conflict" else 64)
        adopt = ld > lt
        for cat in sorted({r["cat"] for r in R}):
            idx = np.array([i for i, r in enumerate(R) if r["cat"] == cat and known[i]])
            if len(idx) == 0:
                res["conditions"][f"{cat}|{f}"] = {"n_known": 0}
                continue
            a = adopt[idx].astype(float)
            marg = (ld - lt)[idx]
            boots = [np.random.default_rng(i).choice(a, len(a)).mean() for i in range(500)]
            res["conditions"][f"{cat}|{f}"] = {"n_known": int(len(idx)), "adoption": float(a.mean()),
                                              "margin": float(marg.mean()),
                                              "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}
    OUT.mkdir(exist_ok=True)
    (OUT / f"{repo.split('/')[-1]}.json").write_text(json.dumps(res, indent=1))
    print(repo, {k.split("|")[0][:10] + "|" + k.split("|")[1][:3]: (v.get("n_known"), round(v.get("adoption", float("nan")), 2))
                 for k, v in res["conditions"].items()}, flush=True)


def analyze(size):
    runs = [f"pythia-{size}"] + [f"pythia-{size}-seed{i}" for i in range(1, 10)]
    data = {r: json.loads((OUT / f"{r}.json").read_text())["conditions"] for r in runs if (OUT / f"{r}.json").exists()}
    conds = sorted(next(iter(data.values())))
    ok = [c for c in conds if all(data[r][c].get("n_known", 0) >= 30 for r in data)]

    def mean_pairwise(rs, key, cs):
        M = np.array([[data[r][c][key] for r in rs] for c in cs])  # [cond, run]
        rhos = [spearmanr(M[i], M[j])[0] for i, j in itertools.combinations(range(len(cs)), 2)]
        return float(np.nanmean(rhos)), M

    rs = list(data)
    rs_no4 = [r for r in rs if not r.endswith("seed4")]
    ok_adopt = [c for c in ok if np.mean([data[r][c]["adoption"] for r in rs]) <= 0.97]
    p1_all, M = mean_pairwise(rs, "adoption", ok_adopt) if len(ok_adopt) >= 2 else (None, None)
    p1_no4 = mean_pairwise(rs_no4, "adoption", ok_adopt)[0] if len(ok_adopt) >= 2 else None
    p1m_all, Mm = mean_pairwise(rs, "margin", ok)
    p1m_no4 = mean_pairwise(rs_no4, "margin", ok)[0]
    sig = 0
    for c in ok:
        a = [data[r][c]["adoption"] for r in rs]
        hw = np.mean([(data[r][c]["ci95"][1] - data[r][c]["ci95"][0]) / 2 for r in rs])
        sig += (max(a) - min(a)) > 2 * hw
    out = {"size": size, "n_runs": len(rs), "usable_conditions": ok, "adoption_conditions": ok_adopt,
           "P1_all": p1_all, "P1_without_seed4": p1_no4, "P1_margin_all": p1m_all, "P1_margin_without_seed4": p1m_no4,
           "P2_conditions_significant": int(sig), "run_mean_margin": dict(zip(rs, Mm.mean(0).tolist()))}
    (OUT / f"analysis_{size}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--analyze")
    a = ap.parse_args()
    analyze(a.analyze) if a.analyze else compute(a.repo)
