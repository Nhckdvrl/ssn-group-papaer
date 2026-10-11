"""CT03 E05 -- can the cheap proxy SCREEN candidates for exact evaluation?

CPD asked the estimator to carry a job it failed at: distilling a privileged
gold-gradient signal into a global linear router that generalises across
problems. This asks it to do the job the fidelity numbers actually support, and
the one the parent's validated action mechanism (EPO) needs:

    rank the K x m candidates by proxy, exact-evaluate only the top m',
    and keep the exact labels for the preference update.

The question is purely operational: how much of the ORACLE counterfactual gain
survives when only the proxy's top m' candidates are ever exactly evaluated?

Zero GPU. Uses exact/proxy grids already collected on the same tokens and the
same pairs (Qwen L28/36/44 from E03.6, OLMoE L1..L15 from E03.7b).
"""
import argparse, json, sys
from collections import defaultdict
import numpy as np

MS = [1, 2, 4, 8, 16, 32]


def load(proxy_f, exact_f):
    px, ex = defaultdict(dict), defaultdict(dict)
    for r in map(json.loads, open(proxy_f)):
        px[(r["q"], r["layer"], r["pos"])][(r["i"], r["j"])] = r["px"]
    for r in map(json.loads, open(exact_f)):
        ex[(r["q"], r["layer"], r["pos"])][(r["i"], r["j"])] = r["dL"]
    return px, ex


def curve(px, ex, name):
    cells = defaultdict(list)
    for k in px:
        if k not in ex or set(px[k]) != set(ex[k]) or len(px[k]) < 8:
            continue
        pairs = sorted(px[k])
        p = np.array([px[k][q] for q in pairs])          # lower = predicted better
        d = np.array([ex[k][q] for q in pairs])          # lower = actually better
        best = d.min()
        if best >= 0:                # no beneficial swap exists; gain is undefined
            continue
        order = p.argsort()
        for m in MS:
            sel = order[:m]
            got = d[sel].min()
            cells[(k[1], m)].append(dict(
                recall=float(int(d.argmin()) in sel.tolist()),
                retained=float(min(got, 0.0) / best),     # in [0,1], 1 = full oracle
                regret=float(got - best)))
    layers = sorted({l for l, _ in cells})
    print(f"\n### {name}   (tokens with a beneficial swap: "
          f"{len(cells[(layers[0], 1)]) if layers else 0} per layer)")
    print(f"{'layer':>6}{'m':>4}{'exact-best recall':>19}{'retained oracle gain':>22}"
          f"{'mean regret':>13}{'reruns saved':>14}")
    out = {}
    for l in layers:
        for m in MS:
            v = cells[(l, m)]
            if not v:
                continue
            row = dict(recall=float(np.mean([x["recall"] for x in v])),
                       retained=float(np.mean([x["retained"] for x in v])),
                       regret=float(np.mean([x["regret"] for x in v])),
                       n=len(v))
            out[f"{l}|{m}"] = row
            print(f"{l:>6}{m:>4}{row['recall']:>19.3f}{row['retained']:>22.3f}"
                  f"{row['regret']:>13.4f}{1 - m / 32:>13.0%}")
        print()
    return out


def main(a):
    res = {}
    res["qwen"] = curve(*load("results/e036_proxy.jsonl",
                              "results/c0_eval_base_pairs.jsonl"), "Qwen3-30B-A3B")
    res["olmoe"] = curve(*load("results/e037_olmoe_proxy.jsonl",
                               "results/e037_olmoe_exact.jsonl"), "OLMoE-1B-7B")
    json.dump(res, open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/e05_screening.json")
    main(ap.parse_args())
