#!/usr/bin/env python3
"""E233: build on-policy items from a model's judged clean answers on GSM8K (wrong -> 'onpolicy_wrong', right -> 'onpolicy_right').
Empty or number-free answers are dropped (not an answer at all). usage: python e233_onpolicy_items.py <clean.judged.jsonl> <out_wrong.json> <out_right.json>"""
import json, re, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if json.loads(l)["cond"] == "clean"]
W, R = [], []
for r in rows:
    c = r["cont"].strip()
    if len(c) < 10 or not re.search(r"\d", c):
        continue
    it = dict(ds="onpolicy_right" if r["judge"] else "onpolicy_wrong", id=r["id"], type=r["fmt"], q=r["q"], err=c, gold=r["gold"], wrong=r["gold"])
    (R if r["judge"] else W).append(it)
json.dump(W, open(sys.argv[2], "w")); json.dump(R, open(sys.argv[3], "w"))
print(sys.argv[1], "wrong", len(W), "right", len(R), "dropped", len(rows) - len(W) - len(R))
