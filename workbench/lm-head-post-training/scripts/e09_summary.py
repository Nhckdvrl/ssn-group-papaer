"""E09 summary: de-randomisation vs choice effect per family and problem set.
B2 (lockstep, e04_hybrid t_base_postmode) from /tmp/xiang_lmhead/e09/gen/<tag>*.jsonl (shards/seeds merged by
(index, sample-file)); B0 / B1 / P0 from the E08 vLLM anchors in /tmp/xiang_lmhead/e08/gen.
Usage: python3 e09_summary.py <fam> <set> <base_key> <post_key> <b2_glob>
  e.g. python3 e09_summary.py o math_l5_300 olmo3-base olmo3-rlzero-math 't_o_B2_math_l5_s*'"""
import glob
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def boot(per, n=4000, seed=0):
    ks = [k for k in per if per[k]]
    m = [sum(per[k]) / len(per[k]) for k in ks]
    rng = random.Random(seed)
    bs = sorted(sum(m[rng.randrange(len(m))] for _ in m) / len(m) for _ in range(n))
    return [round(sum(m) / len(m), 4), round(bs[int(0.025 * n)], 4), round(bs[int(0.975 * n)], 4), len(ks)]


def anchor(tag):
    f = Path("/tmp/xiang_lmhead/e08/gen") / f"{tag}.jsonl"
    if not f.exists():
        return None
    out = {}
    for l in open(f):
        r = json.loads(l)
        out[r["index"]] = [c["reward"] for c in r["completions"]]
    return out


def main():
    fam, s, bkey, pkey, pat = sys.argv[1:6]
    B2 = {}
    meta = {"files": [], "len": [], "trunc": [], "parse_fail": []}
    for f in sorted(glob.glob(f"/tmp/xiang_lmhead/e09/gen/{pat}.jsonl")):
        meta["files"].append(Path(f).name)
        for l in open(f):
            r = json.loads(l)
            B2.setdefault(r["index"], []).append(r["reward"])
            meta["len"].append(r["n_tokens"]); meta["trunc"].append(r["truncated"]); meta["parse_fail"].append(r["pred"] is None)
    B0, B1, P0 = anchor(f"a_{bkey}_{s}"), anchor(f"a_{bkey}-B1_{s}"), anchor(f"a_{pkey}_{s}")
    ks = sorted(set(B2) & set(B0 or {}) & set(B1 or {}) & set(P0 or {}))
    res = {"family": fam, "set": s, "n_problems": len(ks), "b2_files": meta["files"],
           "b2_samples": sum(len(B2[k]) for k in ks),
           "b2_mean_len": round(sum(meta["len"]) / max(1, len(meta["len"])), 1),
           "b2_trunc": round(sum(meta["trunc"]) / max(1, len(meta["trunc"])), 4),
           "b2_parse_fail": round(sum(meta["parse_fail"]) / max(1, len(meta["parse_fail"])), 4),
           "acc": {"B0": boot({k: B0[k] for k in ks}), "B1": boot({k: B1[k] for k in ks}),
                   "B2": boot({k: B2[k] for k in ks}), "P0": boot({k: P0[k] for k in ks})}}
    mean = lambda v: sum(v) / len(v)
    res["paired"] = {"gap P0-B0": boot({k: [mean(P0[k]) - mean(B0[k])] for k in ks}),
                     "derand B1-B0": boot({k: [mean(B1[k]) - mean(B0[k])] for k in ks}),
                     "choice B2-B1": boot({k: [mean(B2[k]) - mean(B1[k])] for k in ks}),
                     "remaining P0-B2": boot({k: [mean(P0[k]) - mean(B2[k])] for k in ks})}
    out = ROOT / "results" / "e09"; out.mkdir(parents=True, exist_ok=True)
    (out / f"summary_{fam}_{s}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
