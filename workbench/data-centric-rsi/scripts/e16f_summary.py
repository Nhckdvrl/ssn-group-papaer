"""E16 stage 0, function-level: summary table with problem-clustered bootstrap 95% CIs.
Rows: model x bug source for disc_ref (given the reference): valid rate, success over all attempts, success given a
valid input; plus judge bug-detection and reference-acceptance rates and solve pass rate.
Usage: python3 e16f_summary.py --dir /tmp/xiang_e16 [--out summary.json]
"""
import argparse
import collections
import json
import random

MODELS = [("c15", "Qwen2.5-Coder-1.5B-Instruct"), ("c7", "Qwen2.5-Coder-7B-Instruct"),
          ("c14", "Qwen2.5-Coder-14B-Instruct"), ("qwen", "Qwen2.5-7B-Instruct"), ("cure", "ReasonFlux-Coder-7B (CURE)"),
          ("r1", "DeepSeek-R1-Distill-Qwen-7B"), ("tcs", "TCS-7B")]


def boot(rows, f, B=2000):
    by = collections.defaultdict(list)
    for r in rows:
        by[r["pid"]].append(r)
    ps = sorted(by)
    rng = random.Random(0)
    vals = []
    for _ in range(B):
        samp = [r for p in (rng.choice(ps) for _ in ps) for r in by[p]]
        v = f(samp)
        if v is not None:
            vals.append(v)
    vals.sort()
    return (vals[int(.025 * len(vals))], vals[int(.975 * len(vals)) - 1]) if vals else (None, None)


def rate(rs, key):
    return sum(bool(r.get(key)) for r in rs) / len(rs) if rs else None


def succ_valid(rs):
    v = [r for r in rs if r.get("valid")]
    return rate(v, "success") if v else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    table = []
    for t, name in MODELS:
        try:
            S = [json.loads(l) for l in open(f"{a.dir}/fscored/solve_{t}.jsonl")]
            R = [json.loads(l) for l in open(f"{a.dir}/fscored/ev_{t}.jsonl")]
        except FileNotFoundError:
            continue
        row = {"model": name, "solve_pass": rate(S, "pass_all")}
        for src in ("external", "mutant", "own"):
            rs = [r for r in R if r["task"] == "disc_ref" and r["source"] == src]
            if not rs:
                continue
            row[src] = {"n": len(rs), "problems": len({r["pid"] for r in rs}), "valid": rate(rs, "valid"),
                        "success": rate(rs, "success"), "success_ci": boot(rs, lambda x: rate(x, "success")),
                        "success_given_valid": succ_valid(rs), "sgv_ci": boot(rs, succ_valid)}
        J = [r for r in R if r["task"] == "judge"]
        row["judge_bug_detect"] = rate([r for r in J if r["label"] == "bug"], "right")
        row["judge_ref_accept"] = rate([r for r in J if r["label"] == "correct"], "right")
        table.append(row)
    for row in table:
        print(f"{row['model']}: solve {row['solve_pass']:.2f}  judge bug-detect {row['judge_bug_detect']:.2f} "
              f"ref-accept {row['judge_ref_accept']:.2f}")
        for src in ("external", "mutant", "own"):
            if src in row:
                d = row[src]
                lo, hi = d["success_ci"]; lo2, hi2 = d["sgv_ci"]
                sgv = "-" if d["success_given_valid"] is None else f"{d['success_given_valid']:.2f} [{lo2:.2f},{hi2:.2f}]"
                print(f"   {src:8s} n={d['n']:3d} ({d['problems']} problems) valid {d['valid']:.2f}  "
                      f"success {d['success']:.2f} [{lo:.2f},{hi:.2f}]  success|valid {sgv}")
    if a.out:
        json.dump(table, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
