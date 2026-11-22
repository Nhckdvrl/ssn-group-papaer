#!/usr/bin/env python3
"""E200 analysis: damage of en->X retrieval (M2) under conv / memory switches vs. token inflation of language X.
Usage: e200_analyze.py TOKENIZER_DIR PUD_JSON NONE.json NOCONV.json NOMEM.json OUT.json"""
import json
import sys

import numpy as np
from transformers import AutoTokenizer

LATIN, NONLATIN = ["fr", "de", "es", "tr"], ["ru", "zh", "ja", "ko", "ar", "hi", "th"]


def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main():
    tokdir, pud, fn, fc, fm, out = sys.argv[1:7]
    tok = AutoTokenizer.from_pretrained(tokdir)
    P = json.load(open(pud))
    n_tok = {lg: np.mean([len(tok(P["text"][s][lg], add_special_tokens=False)["input_ids"]) for s in P["ids"]]) for lg in P["langs"]}
    infl = {lg: n_tok[lg] / n_tok["en"] for lg in P["langs"]}
    R = {k: json.load(open(f)) for k, f in (("none", fn), ("noconv", fc), ("nomem", fm))}
    L = len(R["none"]["M2"]["fr"])  # capture indices: 0 = embedding, l + 1 = output of layer l
    sites = {"L2_out": 3, "L16_out": 17, "Lminus4_out": L - 4}
    langs = LATIN + NONLATIN
    res = {"inflation": infl, "sites": sites, "by_site": {}}
    rng = np.random.default_rng(200)
    for name, idx in sites.items():
        row = {}
        for c in ("noconv", "nomem"):
            dmg = {lg: R["none"]["M2"][lg][idx] - R[c]["M2"][lg][idx] for lg in langs}
            x = np.array([infl[lg] for lg in langs]); y = np.array([dmg[lg] for lg in langs])
            rho = spearman(x, y)
            perm = np.array([spearman(rng.permutation(x), y) for _ in range(10000)])
            row[c] = {"damage": dmg, "rho": rho, "p_one_sided": float((perm >= rho).mean()),
                      "latin_mean": float(np.mean([dmg[l] for l in LATIN])), "nonlatin_mean": float(np.mean([dmg[l] for l in NONLATIN])),
                      "none_M2": {lg: R["none"]["M2"][lg][idx] for lg in langs}}
        res["by_site"][name] = row
        c = row["noconv"]
        print(f"{name:12s} noconv rho={c['rho']:+.2f} p={c['p_one_sided']:.3f} latin={c['latin_mean']:.3f} nonlatin={c['nonlatin_mean']:.3f}"
              f" | nomem rho={row['nomem']['rho']:+.2f} latin={row['nomem']['latin_mean']:.3f} nonlatin={row['nomem']['nonlatin_mean']:.3f}")
        print("   ", " ".join(f"{lg}:{infl[lg]:.2f}/{c['none_M2'][lg]:.2f}->{c['none_M2'][lg]-c['damage'][lg]:.2f}" for lg in langs))
    json.dump(res, open(out, "w"))


if __name__ == "__main__":
    main()
