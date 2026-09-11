#!/usr/bin/env python
"""Assemble the adjudicated natural `before` set (v2) from the annotation batches."""
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
GOLD = {"R": "YES", "U": "NOT_DETERMINED", "N": "NO"}
COND = {"R": "natural_realized", "U": "natural_unresolved", "N": "natural_prevented"}


def main():
    sheet = {
        j["cand_id"]: j
        for j in (
            json.loads(l)
            for l in open(os.path.join(PROJ, "data", "natural_sheet.jsonl"), encoding="utf-8")
        )
    }
    rows, counts = [], collections.Counter()
    for path in sorted(glob.glob(os.path.join(PROJ, "data", "annotations", "natural_b*.tsv"))):
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            cid, judge, target = line.rstrip("\n").split("\t")
            counts[judge] += 1
            if judge == "X":
                continue
            s = sheet[cid]
            rows.append(
                {
                    "item_id": cid,
                    "base_id": cid,
                    "passage": s["sentence"],
                    "target": target,
                    "gold_strict": GOLD[judge],
                    "condition": COND[judge],
                    "clause_cue": "modal" if s["marked_modal"] else "plain_past",
                    "source": s["source"],
                }
            )
    path = os.path.join(PROJ, "data", "natural_before_v2.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("adjudicated:", dict(counts))
    print("kept:", len(rows), collections.Counter(r["condition"] for r in rows))
    print("cue x status:", collections.Counter((r["clause_cue"], r["condition"]) for r in rows))
    print("->", path)


if __name__ == "__main__":
    main()
