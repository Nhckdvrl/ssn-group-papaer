"""Summarise fork-swap decoding runs (E04-D): accuracy with per-problem bootstrap CI, paired differences between
conditions on the same problems, fork rate and argmax agreement at forks.
Usage: python3 e04_hybrid_summary.py <out_json> <tag> [<tag> ...]   (reads /tmp/xiang_lmhead/e04/gen/<tag>.jsonl)"""
import itertools
import json
import random
import sys
from pathlib import Path

GEN = Path("/tmp/xiang_lmhead/e04/gen")


def load(tag):
    rows = [json.loads(l) for l in open(GEN / f"{tag}.jsonl")]
    by = {}
    for r in rows:
        by.setdefault(r["index"], []).append(r["reward"])
    return {k: sum(v) / len(v) for k, v in by.items()}, rows


def boot(vals, n=2000, seed=0):
    rng = random.Random(seed)
    bs = sorted(sum(vals[rng.randrange(len(vals))] for _ in vals) / len(vals) for _ in range(n))
    return [bs[int(0.025 * n)], bs[int(0.975 * n)]]


def main():
    out, tags = sys.argv[1], sys.argv[2:]
    data = {t: load(t) for t in tags if (GEN / f"{t}.jsonl").exists()}
    res = {"conditions": {}, "paired": {}}
    for t, (acc, rows) in data.items():
        v = list(acc.values())
        nt = sum(r["n_tokens"] for r in rows); nf = sum(r["n_fork"] for r in rows)
        res["conditions"][t] = {"n_problems": len(v), "acc": sum(v) / len(v), "ci95": boot(v),
                                "parse_fail": sum(r["pred"] is None for r in rows) / len(rows),
                                "truncated": sum(r["truncated"] for r in rows) / len(rows),
                                "mean_len": nt / len(rows), "fork_rate": nf / max(1, nt),
                                "argmax_agree_at_forks": sum(r["n_fork_agree"] for r in rows) / max(1, nf)}
    for a, b in itertools.combinations(data, 2):
        common = sorted(set(data[a][0]) & set(data[b][0]))
        d = [data[a][0][k] - data[b][0][k] for k in common]
        if d:
            res["paired"][f"{a} - {b}"] = {"n": len(d), "diff": sum(d) / len(d), "ci95": boot(d)}
    Path(out).write_text(json.dumps(res, indent=1))
    for t, c in res["conditions"].items():
        print(f"{t:18s} n {c['n_problems']} acc {c['acc']:.3f} [{c['ci95'][0]:.3f},{c['ci95'][1]:.3f}] parse {c['parse_fail']:.3f} "
              f"trunc {c['truncated']:.3f} len {c['mean_len']:.0f} fork_rate {c['fork_rate']:.3f} agree@fork {c['argmax_agree_at_forks']:.3f}")
    for k, v in res["paired"].items():
        print(f"  {k:40s} {v['diff']:+.3f} [{v['ci95'][0]:+.3f},{v['ci95'][1]:+.3f}] n={v['n']}")


if __name__ == "__main__":
    main()
