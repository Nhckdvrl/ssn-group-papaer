"""S03 — the three-family parameter-locus table, paired against each family's own Arm 0."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e01_rawlogit import rows_of, mean, boot_ci, sign_test

# OLMo's 750-step runs predate the budget ladder and live under results/e02/final/
# (config.json confirms steps=750 for every one of them).  Each arm therefore
# carries a LIST of path templates and the first that resolves is used; without
# this, the 750-step table silently dropped OLMo's R and F rows.
FAM = [
    ("OLMo-3 7B",   "results/e02/arm0_samepath/e01.jsonl",
     {"R": ["results/e02/budget/R_st{st}_s{sd}/e01.jsonl",
            "results/e02/final/R_s{sd}/e01.jsonl@750"],
      "Sbody": ["results/e02/budget/Sbody_st{st}_s{sd}/e01.jsonl"],
      "F": ["results/e02/budget/F_st{st}_s{sd}/e01.jsonl",
            "results/e02/final/F_s{sd}/e01.jsonl@750"]}, (0, 1)),
    # NOTE: the *_R_st1_s0 Arm 0 paths are same-path zero-update baselines
    # (config.json has "lr": 0.0), not 1-step training runs.
    ("Qwen2.5 7B",  "results/e02/repl/qwen2.5-7b_R_st1_s0/e01.jsonl",
     {a: ["results/e02/repl/qwen2.5-7b_%s_st{st}_s{sd}/e01.jsonl" % a]
      for a in ("R", "Sbody", "F")}, (0, 1, 2)),
    ("Llama-3.1 8B", "results/e02/repl/llama3.1-8b_R_st1_s0/e01.jsonl",
     {a: ["results/e02/repl/llama3.1-8b_%s_st{st}_s{sd}/e01.jsonl" % a]
      for a in ("R", "Sbody", "F")}, (0, 1, 2)),
]


def resolve(templates, st, seeds):
    """First template that resolves to at least one existing file.

    A template may carry an '@N' suffix meaning it is only valid at budget N.
    """
    for t in templates:
        t, _, only = t.partition("@")
        if only and int(only) != st:
            continue
        ps = [t.format(st=st, sd=s) for s in seeds]
        ps = [p for p in ps if os.path.exists(p)]
        if ps:
            return ps
    return []
ST = int(sys.argv[1]) if len(sys.argv) > 1 else 2250

print(f"\nParameter-locus replication at {ST} steps, paired against each "
      f"family's own Arm 0\n")
hdr = (f"{'family':<15}{'arm':<7}"
       f"{'D d_goal  (STOP vs CONT)':>24}{'sign':>8}"
       f"{'D dz_stop':>11}{'D dz_cont':>11}")
print(hdr); print("-" * len(hdr))
for name, a0, tmpl, seeds in FAM:
    base = rows_of([a0])
    shown = False
    for arm in ("R", "Sbody", "F"):
        ps = resolve(tmpl[arm], ST, seeds)
        if not ps:
            continue
        A = rows_of(ps)
        ks = sorted(set(A) & set(base))
        out = []
        for m in ("d_goal", "dz_stop", "dz_cont"):
            v = [A[k][m] - base[k][m] for k in ks]
            lo, hi = boot_ci(v); p, x, y = sign_test(v)
            out.append((mean(v), lo, hi, f"{x}/{y}"))
        (g1, gl, gh, gs), (m1, l1, h1, s1), (m2, l2, h2, s2) = out
        # label on the first row that actually prints, not on arm R, which may
        # be missing at some budgets
        lab = "" if shown else name
        shown = True
        print(f"{lab:<15}{arm:<7}"
              f"{f'{g1:+.2f} [{gl:+.2f},{gh:+.2f}]':>24}{gs:>8}"
              f"{f'{m1:+.2f}':>11}{f'{m2:+.2f}':>11}")
    print()
