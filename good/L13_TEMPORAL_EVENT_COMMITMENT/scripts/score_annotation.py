#!/usr/bin/env python
"""Score the author annotation against the by-construction gold."""
import collections
import glob
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
MAP = {"YES": "YES", "NO": "NO", "ND": "NOT_DETERMINED"}


def main():
    key = json.load(open(os.path.join(PROJ, "data", "annotation_key.json"), encoding="utf-8"))
    ann = {}
    for path in sorted(glob.glob(os.path.join(PROJ, "data", "annotations", "author_batch*.tsv"))):
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            aid, strict, lik, nat = line.split()
            ann[aid] = {"strict": MAP[strict], "likelihood": int(lik), "naturalness": int(nat)}

    missing = set(key) - set(ann)
    assert not missing, f"unannotated: {sorted(missing)[:5]}"

    agree = collections.Counter()
    total = collections.Counter()
    disagreements = []
    lik = collections.defaultdict(list)
    nat = collections.defaultdict(list)
    for aid, k in key.items():
        a = ann[aid]
        cond, gold = k["condition"], k["gold_strict"]
        total[cond] += 1
        if a["strict"] == gold:
            agree[cond] += 1
        else:
            disagreements.append((aid, k["item_id"], cond, gold, a["strict"]))
        lik[cond].append(a["likelihood"])
        nat[cond].append(a["naturalness"])

    n = sum(total.values())
    print(f"strict-commitment agreement with construction gold: {sum(agree.values())}/{n} "
          f"= {sum(agree.values())/n:.3f}\n")
    print(f"{'condition':22s} {'agree':>10s} {'E[likelihood]':>14s} {'median nat':>11s} {'min nat':>8s}")
    for cond in sorted(total):
        print(f"{cond:22s} {agree[cond]}/{total[cond]:<8d} "
              f"{statistics.fmean(lik[cond]):>14.2f} "
              f"{statistics.median(nat[cond]):>11.1f} {min(nat[cond]):>8d}")

    low = [(aid, key[aid]["item_id"], ann[aid]["naturalness"]) for aid in key if ann[aid]["naturalness"] < 4]
    print(f"\nitems with naturalness < 4: {len(low)}")
    for aid, iid, v in sorted(low, key=lambda x: x[2]):
        print(f"  {iid:28s} naturalness {v}")
    print(f"\nstrict-commitment disagreements: {len(disagreements)}")
    for d in disagreements:
        print("  ", d)

    out = {
        "n": n,
        "strict_agreement": round(sum(agree.values()) / n, 4),
        "per_condition": {
            c: {
                "agreement": round(agree[c] / total[c], 4),
                "mean_likelihood": round(statistics.fmean(lik[c]), 3),
                "median_naturalness": statistics.median(nat[c]),
            }
            for c in total
        },
        "low_naturalness_items": [{"item_id": i, "naturalness": v} for _, i, v in low],
        "disagreements": [
            {"item_id": i, "condition": c, "gold": g, "annotation": a}
            for _, i, c, g, a in disagreements
        ],
        "annotations": {key[aid]["item_id"]: ann[aid] for aid in key},
    }
    with open(os.path.join(PROJ, "data", "annotations", "author_scored.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
