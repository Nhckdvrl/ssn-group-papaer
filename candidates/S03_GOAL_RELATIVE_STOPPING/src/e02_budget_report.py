"""S03 / E02b — the R-vs-F budget ladder."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from e02_paired import load, mean, boot_ci, sign_test

BASE = "results/e01/olmo3-7b_base_grafted.jsonl"
SEEDS = ["0", "1"]
RUNGS = [(250, "results/e02/budget/{a}_st250_s{s}/e01.jsonl"),
         (750, "results/e02/final/{a}_s{s}/e01.jsonl"),
         (2250, "results/e02/budget/{a}_st2250_s{s}/e01.jsonl")]

base = load([BASE])
print(f"{'steps':>6} {'R d_stop':>10} {'F d_stop':>10} {'F - R (paired)':>18}"
      f" {'95% CI':>16} {'sign p':>8} {'+/-':>8}")
print("-" * 82)
print(f"{'0':>6} {mean(list(base.values())):>10.2f} "
      f"{mean(list(base.values())):>10.2f}")
for st, tmpl in RUNGS:
    pr = [tmpl.format(a="R", s=s) for s in SEEDS]
    pf = [tmpl.format(a="F", s=s) for s in SEEDS]
    pr = [x for x in pr if os.path.exists(x)]
    pf = [x for x in pf if os.path.exists(x)]
    if not (pr and pf):
        print(f"{st:>6}  (incomplete)"); continue
    R, Fa = load(pr), load(pf)
    ks = sorted(set(R) & set(Fa))
    d = [Fa[k] - R[k] for k in ks]
    lo, hi = boot_ci(d)
    p, a, b = sign_test(d)
    print(f"{st:>6} {mean([R[k] for k in ks]):>10.2f} "
          f"{mean([Fa[k] for k in ks]):>10.2f} {mean(d):>18.2f}"
          f" {f'[{lo:.2f}, {hi:.2f}]':>16} {p:>8.2} {f'{a}/{b}':>8}")
print("\nnatural SFT (full Tulu-3 recipe, orientation only): d_stop +12.50")
