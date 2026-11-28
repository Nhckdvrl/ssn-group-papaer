"""E17-0 positive control input: for one model, pick up to --k problems (seeded) where it wrote a wrong program, and
one wrong program per problem (lowest sample index); write {id, prog: "<model>:<sample>", code} for e17_infer --phase
condtests. Usage: python3 e17_condfile.py --matrix m.jsonl.gz --gen <dir> --model tag --out cond_<tag>.jsonl [--k 60]
"""
import argparse
import gzip
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from e17_execute import extract_prog  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--matrix", required=True); ap.add_argument("--gen", required=True)
ap.add_argument("--model", required=True); ap.add_argument("--out", required=True); ap.add_argument("--k", type=int, default=60)
a = ap.parse_args()
code = {(g["pid"], g["sample"]): extract_prog(g["text"]) for g in map(json.loads, open(f"{a.gen}/solve_{a.model}.jsonl"))}
cand = []
for r in map(json.loads, gzip.open(a.matrix, "rt")):
    W = sorted(p["sample"] for p in r["programs"] if p["model"] == a.model and not p["noprog"] and not p["correct"])
    if W and r["ref_ok"]:
        cand.append((r["id"], W[0]))
random.Random(0).shuffle(cand)
with open(a.out, "w") as f:
    for pid, s in cand[:a.k]:
        f.write(json.dumps(dict(id=pid, prog=f"{a.model}:{s}", code=code[(pid, s)])) + "\n")
print(a.model, "problems with own wrong programs", len(cand), "written", min(len(cand), a.k))
