"""Context trust of the DataDecide 1B models on ParaConflict (two conflict forms x six relations): on facts the model
knows, the share of items where it adopts the counterfactual context and the mean log-probability margin of the
counterfactual over the memorized answer. Input of seed_effect_behaviour.py.
Usage: context_trust_1b.py --repo allenai/DataDecide-c4-1B --seed default
"""
import argparse
import json

import numpy as np
import torch

import datadecide as dd
import prompts
import common as mc
from prompts import cand_logprob

OUT = mc.RESULTS / "context_trust_1b"


def compute(repo, seed):
    torch.set_grad_enabled(False)
    model, tok = dd.load(repo, dd.rev(dd.FINAL_1B, seed), dtype=torch.bfloat16)
    R = prompts.rows()
    clean_t = cand_logprob(model, tok, [r["clean"] for r in R], [r["ans"] for r in R])
    clean_d = cand_logprob(model, tok, [r["clean"] for r in R], [r["dist"] for r in R])
    known = clean_t > clean_d
    res = {"repo": repo, "seed": seed, "step": dd.FINAL_1B, "conditions": {}, "known_items": {}}
    for f in prompts.FORMS:
        P = [r[f] for r in R]
        bs = 8 if f == "Coherent Conflict" else 32
        lt = cand_logprob(model, tok, P, [r["ans"] for r in R], bs=bs)
        ld = cand_logprob(model, tok, P, [r["dist"] for r in R], bs=bs)
        for cat in sorted({r["cat"] for r in R}):
            all_idx = [i for i, r in enumerate(R) if r["cat"] == cat]
            idx = np.array([i for i in all_idx if known[i]])
            res["known_items"][cat] = [int(i) for i in idx]
            res["conditions"][f"{cat}|{f}"] = {
                "n_items": len(all_idx), "n_known": int(len(idx)), "known_frac": float(len(idx) / len(all_idx)),
                "clean_margin": float((clean_t - clean_d)[all_idx].mean()),
                "adoption": float((ld[idx] > lt[idx]).mean()) if len(idx) else None,
                "margin": float((ld - lt)[idx].mean()) if len(idx) else None,
                "margin_all_items": {int(i): float(ld[i] - lt[i]) for i in all_idx}}
    OUT.mkdir(exist_ok=True)
    name = f"{repo.split('DataDecide-')[1]}__{seed}.json"
    (OUT / name).write_text(json.dumps(res))
    print(name, {k.split("|")[0][:8] + "|" + k.split("|")[1][:3]: (v["n_known"], round(v["margin"] or 0, 2))
                 for k, v in res["conditions"].items()}, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--seed", required=True)
    a = ap.parse_args()
    compute(a.repo, a.seed)


if __name__ == "__main__":
    main()
