"""Per-condition accuracy + error decomposition for run_vllm.py outputs.
python analyze.py out1.jsonl [out2.jsonl ...]
Only worlds where the model got B0 right (prerequisite competence) are used for the transition contrasts.
Error types on OUT/OUTW/NEUT (gold = base): 'leak' = pred equals the supposition-world answer (= not base).
"""
import json, sys, collections


def load(p):
    return [json.loads(l) for l in open(p)]


def key(r):  # world id: item ids are s{idx}/sib{d}_{idx}/nest{d}_{idx}; conds of a world share the trailing idx
    return r["id"].split("_")[-1] if "_" in r["id"] else r["id"]


for p in sys.argv[1:]:
    rows = load(p)
    # ids of conds within the same world share prefix: rebuild by (family, id-suffix) using sequence in file
    print("=====", p, "n=", len(rows), "unparsed=", sum(r["pred"] is None for r in rows))
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["family"], r["cond"])].append(r)
    for (fam, c), rs in sorted(by.items()):
        acc = sum(r["pred"] == r["gold"] for r in rs) / len(rs)
        print(f"{fam:7s} {c:9s} n={len(rs):4d} acc={acc:.3f} yes-rate={sum(r['pred']=='Yes' for r in rs)/len(rs):.2f} "
              f"gold-yes={sum(r['gold']=='Yes' for r in rs)/len(rs):.2f}")
