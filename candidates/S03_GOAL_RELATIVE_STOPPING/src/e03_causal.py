"""
S03 / E03 — within-family causal test of the boundary-competence account.

The cross-family correlation (Arm 0 generic boundary_auc vs whether readout-only
adaptation helps) is only n=3 and could be confounded by anything else that
differs between OLMo, Qwen and Llama.  This test stays inside ONE model and
manipulates exactly one quantity.

Intervention: remove a fraction lambda of the stop row's projection onto the
generic response-boundary direction b.  Hidden states, training data, optimiser,
schedule and every other parameter are untouched; only the readout's GENERIC
boundary competence is degraded.

If arm R's goal-relative gain shrinks or reverses as lambda grows -- same model,
same state, same data -- the boundary-competence account becomes causal rather
than correlational.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e01_rawlogit import rows_of, mean, boot_ci, sign_test
import json

ROWS = [
    ("lambda=0  (original)", "results/e02/arm0_samepath/e01.jsonl",
     ["results/e02/budget/R_st2250_s0/e01.jsonl",
      "results/e02/budget/R_st2250_s1/e01.jsonl"]),
    ("lambda=0.5 (~Llama-like)", "results/e02/degrade/arm0_lam0.5/e01.jsonl",
     [f"results/e02/degrade/R_lam0.5_s{s}/e01.jsonl" for s in (0, 1)]),
    ("lambda=1.0 (destroyed)", "results/e02/degrade/arm0_lam1.0/e01.jsonl",
     [f"results/e02/degrade/R_lam1.0_s{s}/e01.jsonl" for s in (0, 1)]),
]


def auc_of(d):
    p = os.path.join(os.path.dirname(d), "history.jsonl")
    try:
        return json.loads(open(p).readline())["boundary_auc"]
    except Exception:
        return float("nan")


def auc_after(ps):
    v = []
    for p in ps:
        h = os.path.join(os.path.dirname(p), "history.jsonl")
        try:
            v.append(json.loads(open(h).read().strip().split("\n")[-1])["boundary_auc"])
        except Exception:
            pass
    return mean(v) if v else float("nan")


print(f"\n{'condition':<26}{'auc before':>11}{'auc after R':>12}"
      f"{'D d_goal (R - Arm0)':>23}{'sign':>8}")
print("-" * 80)
for name, a0, rs in ROWS:
    rs = [p for p in rs if os.path.exists(p)]
    if not (os.path.exists(a0) and rs):
        print(f"{name:<26}   (pending)")
        continue
    base, A = rows_of([a0]), rows_of(rs)
    ks = sorted(set(A) & set(base))
    v = [A[k]["d_goal"] - base[k]["d_goal"] for k in ks]
    lo, hi = boot_ci(v)
    p, x, y = sign_test(v)
    print(f"{name:<26}{auc_of(a0):>11.5f}{auc_after(rs):>12.5f}"
          f"{f'{mean(v):+.2f} [{lo:+.2f},{hi:+.2f}]':>23}{f'{x}/{y}':>8}")
print()
