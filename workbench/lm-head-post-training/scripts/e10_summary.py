"""E10 summary: does a prefix written with sparse post-model choices (B2) let the base continue as well as a prefix written
by the post model itself? Compares Base continuations of B1 / B2 / Post / Base prefixes at each L on the same problems.
Reads /tmp/xiang_lmhead/e08/gen/h_q_{B1,B2,P,B}2B_math_l5_300.jsonl; writes results/e10/summary_math_l5_300.json."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G = Path("/tmp/xiang_lmhead/e08/gen")
SRC = {"B1": "h_q_B12B_math_l5_300", "B2": "h_q_B22B_math_l5_300", "Post": "h_q_P2B_math_l5_300", "Base": "h_q_B2B_math_l5_300"}


def boot(per, n=4000, seed=0):
    ks = [k for k in per if per[k]]
    m = [sum(per[k]) / len(per[k]) for k in ks]
    rng = random.Random(seed)
    bs = sorted(sum(m[rng.randrange(len(m))] for _ in m) / len(m) for _ in range(n))
    return [round(sum(m) / len(m), 4), round(bs[int(0.025 * n)], 4), round(bs[int(0.975 * n)], 4), len(ks)]


def main():
    rows = {k: [json.loads(l) for l in open(G / f"{t}.jsonl")] for k, t in SRC.items()}
    res = {"by_L": {}}
    for L in ("32", "256", "rel0.5"):
        per = {k: {} for k in SRC}
        for k, rr in rows.items():
            for r in rr:
                if r["L"] == L:
                    per[k].setdefault(r["index"], []).append(r["reward"])
        common = set.intersection(*[set(v) for v in per.values()])
        d = {"n_common": len(common)}
        for k in SRC:
            d[f"V_Base(s_{k})"] = boot({i: per[k][i] for i in common})
            d[f"prefix_len_{k}"] = round(sum(r["n_prefix"] for r in rows[k] if r["L"] == L) / max(1, sum(r["L"] == L for r in rows[k])), 1)
        for a, b in (("B2", "B1"), ("Post", "B2"), ("B2", "Base"), ("B1", "Base")):
            d[f"{a} - {b}"] = boot({i: [sum(per[a][i]) / len(per[a][i]) - sum(per[b][i]) / len(per[b][i])] for i in common})
        # by whether the trajectory the prefix was cut from was itself correct
        for k in ("B1", "B2"):
            for so in (1.0, 0.0):
                pp = {}
                for r in rows[k]:
                    if r["L"] == L and r["src_reward"] == so:
                        pp.setdefault(r["index"], []).append(r["reward"])
                d[f"V_Base(s_{k}) src_correct={int(so)}"] = boot(pp)
        res["by_L"][L] = d
    out = ROOT / "results" / "e10"; out.mkdir(parents=True, exist_ok=True)
    (out / "summary_math_l5_300.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
