#!/usr/bin/env python3
"""E229 summary: per model x format x dataset, knowledge-gated correction rates for C / S / O
(Wilson 95% CI) and paired bootstrap CIs for O-C and S-C.
usage: python e229_summarize.py out.json base=results229/base.judged.jsonl sft=... instruct=...
"""
import json, math, random, sys, collections


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 3), round(c - h, 3), round(c + h, 3)]


def boot(pairs, B=2000, seed=0):
    rng = random.Random(seed)
    n = len(pairs)
    if n == 0:
        return None
    est = sum(a - b for a, b in pairs) / n
    s = sorted(sum(a - b for a, b in (pairs[rng.randrange(n)] for _ in range(n))) / n for _ in range(B))
    return [round(est, 3), round(s[int(.025 * B)], 3), round(s[int(.975 * B)], 3)]


def main():
    out, specs = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
    res = {}
    for name, path in specs.items():
        rows = [json.loads(l) for l in open(path)]
        by = collections.defaultdict(dict)  # (fmt, ds, id) -> cond -> judge
        for r in rows:
            by[(r["fmt"], r["ds"], r["id"])][r["cond"]] = r["judge"]
        for fmt in sorted({k[0] for k in by}):
            for ds in sorted({k[1] for k in by}):
                keys = [k for k in by if k[0] == fmt and k[1] == ds]
                gated = [k for k in keys if by[k].get("clean")]
                cell = dict(n_items=len(keys), gate_pass=len(gated), gate_rate=round(len(gated) / max(1, len(keys)), 3))
                for c in ["C", "S", "O"]:
                    k_ = sum(by[k][c] for k in gated)
                    cell[c] = wilson(k_, len(gated))
                    cell[c + "_ungated"] = wilson(sum(by[k][c] for k in keys), len(keys))
                cell["O-C"] = boot([(by[k]["O"], by[k]["C"]) for k in gated])
                cell["S-C"] = boot([(by[k]["S"], by[k]["C"]) for k in gated])
                cell["O-S"] = boot([(by[k]["O"], by[k]["S"]) for k in gated])
                res[f"{name}|{fmt}|{ds}"] = cell
    json.dump(res, open(out, "w"), indent=1)
    print(f"{'model|fmt|ds':32s} gate   C                 S                 O                 O-C               S-C")
    for k, c in res.items():
        f = lambda v: f"{v[0]:.2f} [{v[1]:.2f},{v[2]:.2f}]" if v and v[0] is not None else "  -  "
        print(f"{k:32s} {c['gate_pass']:3d}/{c['n_items']:<3d} {f(c['C']):17s} {f(c['S']):17s} {f(c['O']):17s} {f(c['O-C']):17s} {f(c['S-C'])}")


if __name__ == "__main__":
    main()
