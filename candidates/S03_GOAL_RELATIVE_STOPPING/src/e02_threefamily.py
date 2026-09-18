"""S03 — the three-family parameter-locus table, paired against each family's own Arm 0."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e01_rawlogit import rows_of, mean, boot_ci, sign_test

FAM = [
    ("OLMo-3 7B",   "results/e02/arm0_samepath/e01.jsonl",
     {"R": "results/e02/budget/R_st{st}_s{sd}/e01.jsonl",
      "Sbody": "results/e02/budget/Sbody_st{st}_s{sd}/e01.jsonl",
      "F": "results/e02/budget/F_st{st}_s{sd}/e01.jsonl"}, (0, 1)),
    ("Qwen2.5 7B",  "results/e02/repl/qwen2.5-7b_R_st1_s0/e01.jsonl",
     {a: "results/e02/repl/qwen2.5-7b_%s_st{st}_s{sd}/e01.jsonl" % a
      for a in ("R", "Sbody", "F")}, (0, 1, 2)),
    ("Llama-3.1 8B", "results/e02/repl/llama3.1-8b_R_st1_s0/e01.jsonl",
     {a: "results/e02/repl/llama3.1-8b_%s_st{st}_s{sd}/e01.jsonl" % a
      for a in ("R", "Sbody", "F")}, (0, 1, 2)),
]
ST = int(sys.argv[1]) if len(sys.argv) > 1 else 2250

print(f"\nParameter-locus replication at {ST} steps, paired against each "
      f"family's own Arm 0\n")
hdr = (f"{'family':<15}{'arm':<7}{'D dz_stop (reading)':>24}{'sign':>8}"
       f"{'D dz_cont (clearing)':>24}{'sign':>8}")
print(hdr); print("-" * len(hdr))
for name, a0, tmpl, seeds in FAM:
    base = rows_of([a0])
    for arm in ("R", "Sbody", "F"):
        ps = [tmpl[arm].format(st=ST, sd=s) for s in seeds]
        ps = [p for p in ps if os.path.exists(p)]
        if not ps:
            continue
        A = rows_of(ps)
        ks = sorted(set(A) & set(base))
        out = []
        for m in ("dz_stop", "dz_cont"):
            v = [A[k][m] - base[k][m] for k in ks]
            lo, hi = boot_ci(v); p, x, y = sign_test(v)
            out.append((mean(v), lo, hi, f"{x}/{y}"))
        (m1, l1, h1, s1), (m2, l2, h2, s2) = out
        print(f"{name if arm == 'R' else '':<15}{arm:<7}"
              f"{f'{m1:+.2f} [{l1:+.2f},{h1:+.2f}]':>24}{s1:>8}"
              f"{f'{m2:+.2f} [{l2:+.2f},{h2:+.2f}]':>24}{s2:>8}")
    print()
