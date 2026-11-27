"""E08 summary: handoff 2x2 on identical prefixes + equal-compute majority voting.
Reads /tmp/xiang_lmhead/e08/gen/{a_*.jsonl, h_<fam>_<src>2<cont>_<set>.jsonl}; writes results/e08/summary_<fam>_<set>.json.
Usage: python3 e08_summary.py <fam: q|o> <set> <base_key> <post_key>
  e.g. python3 e08_summary.py q math_l5_300 qwen3-8b-base qwen3-8b"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = Path("/tmp/xiang_lmhead/e08/gen")


def boot(vals, n=4000, seed=0):
    """vals: dict problem -> list of values; bootstrap over problems of the per-problem mean."""
    keys = [k for k in vals if vals[k]]
    if not keys:
        return None
    means = [sum(vals[k]) / len(vals[k]) for k in keys]
    rng = random.Random(seed)
    bs = sorted(sum(means[rng.randrange(len(means))] for _ in means) / len(means) for _ in range(n))
    return [round(sum(means) / len(means), 4), round(bs[int(0.025 * n)], 4), round(bs[int(0.975 * n)], 4), len(keys)]


def anchor(tag):
    f = GEN / f"{tag}.jsonl"
    if not f.exists():
        return None
    return {json.loads(l)["index"]: json.loads(l)["completions"] for l in open(f)}


def handoff(tag):
    f = GEN / f"{tag}.jsonl"
    if not f.exists():
        return None
    return {(r["index"], r["k"], r["L"]): r for r in (json.loads(l) for l in open(f))}


def maj_curve(comps, ks=(1, 2, 3, 4, 6, 8), reps=200, seed=0):
    """Expected majority-vote accuracy and expected total tokens when voting over k of the 8 samples."""
    rng = random.Random(seed)
    out = {}
    for k in ks:
        acc, tok = [], []
        for idx, cs in comps.items():
            if len(cs) < k:
                continue
            a = t = 0.0
            for _ in range(reps):
                sub = rng.sample(cs, k)
                votes = Counter(c["pred"] for c in sub if c["pred"] is not None)
                if votes:
                    top = votes.most_common(1)[0][0]
                    a += next(c["reward"] for c in sub if c["pred"] == top)
                t += sum(len(c["token_ids"]) for c in sub)
            acc.append(a / reps); tok.append(t / reps)
        if acc:
            out[k] = {"acc": round(sum(acc) / len(acc), 4), "tokens": round(sum(tok) / len(tok), 1)}
    return out


def main():
    fam, s, bkey, pkey = sys.argv[1:5]
    A = {"B0": anchor(f"a_{bkey}_{s}"), "P0": anchor(f"a_{pkey}_{s}"), "B1": anchor(f"a_{bkey}-B1_{s}")}
    H = {c: handoff(f"h_{fam}_{c}_{s}") for c in ("P2B", "P2B1", "P2P", "B2B", "B2P")}
    res = {"family": fam, "set": s, "anchors": {}, "handoff": {}, "paired": {}, "by_source_outcome": {}, "equal_compute": {}}
    for name, a in A.items():
        if a:
            res["anchors"][name] = {"acc": boot({k: [c["reward"] for c in v] for k, v in a.items()}),
                                    "mean_len": round(sum(len(c["token_ids"]) for v in a.values() for c in v) / sum(len(v) for v in a.values()), 1),
                                    "trunc": round(sum(c["finish"] == "length" for v in a.values() for c in v) / sum(len(v) for v in a.values()), 4)}
    Ls = ["32", "256", "rel0.5"]
    for c, h in H.items():
        if not h:
            continue
        res["handoff"][c] = {}
        for L in Ls:
            rows = [r for (i, k, l), r in h.items() if l == L]
            if not rows:
                continue
            per = {}
            for r in rows:
                per.setdefault(r["index"], []).append(r["reward"])
            res["handoff"][c][L] = {"acc": boot(per), "n_prefix": len(rows),
                                    "mean_total_len": round(sum(r["total_len"] for r in rows) / len(rows), 1),
                                    "mean_prefix": round(sum(r["n_prefix"] for r in rows) / len(rows), 1),
                                    "trunc": round(sum(r["finish"] == "length" for r in rows) / len(rows), 4)}
    # paired differences on identical prefixes
    pairs = [("P2P", "P2B", "G on Post prefixes (Post cont - Base cont)"), ("P2B1", "P2B", "B1 cont - Base cont on Post prefixes"),
             ("P2P", "P2B1", "Post cont - B1 cont on Post prefixes"), ("B2P", "B2B", "G on Base prefixes (Post cont - Base cont)")]
    for a, b, label in pairs:
        if not (H[a] and H[b]):
            continue
        for L in Ls:
            keys = [key for key in H[a] if key[2] == L and key in H[b]]
            per = {}
            for key in keys:
                per.setdefault(key[0], []).append(H[a][key]["reward"] - H[b][key]["reward"])
            res["paired"][f"{label} @L={L}"] = boot(per)
    # by whether the source completion (from which the prefix was cut) was itself correct
    for c in ("P2B", "P2B1", "P2P", "B2B", "B2P"):
        if not H[c]:
            continue
        for L in Ls:
            for so in (1.0, 0.0):
                per = {}
                for (i, k, l), r in H[c].items():
                    if l == L and r["src_reward"] == so:
                        per.setdefault(i, []).append(r["reward"])
                res["by_source_outcome"][f"{c} @L={L} src_correct={int(so)}"] = boot(per)
    for name, a in A.items():
        if a:
            res["equal_compute"][name] = maj_curve(a)
    out = ROOT / "results" / "e08"; out.mkdir(parents=True, exist_ok=True)
    (out / f"summary_{fam}_{s}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
