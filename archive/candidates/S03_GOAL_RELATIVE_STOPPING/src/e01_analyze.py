"""S03 / E01 analysis: goal effect, continuation awareness, closure control."""
import argparse, glob, json, math, os
from collections import defaultdict


def mean(v): return sum(v) / len(v) if v else float("nan")


def sd(v):
    if len(v) < 2: return float("nan")
    m = mean(v); return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def boot_ci(v, n=10000, seed=0):
    import random
    rng = random.Random(seed)
    if not v: return (float("nan"), float("nan"))
    k = len(v)
    ms = sorted(mean([v[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n)]


def sign_test(v):
    """Two-sided exact binomial sign test against median 0 (zeros dropped)."""
    pos = sum(1 for x in v if x > 0); neg = sum(1 for x in v if x < 0)
    n = pos + neg
    if n == 0: return 1.0, pos, neg
    c = lambda n, k: math.comb(n, k)
    tail = sum(c(n, k) for k in range(min(pos, neg) + 1)) / 2 ** n
    return min(1.0, 2 * tail), pos, neg


def report(rows, tag, pos="p2"):
    by_fam = defaultdict(list)
    for r in rows:
        by_fam[r["family"]].append(r)
    print(f"\n{'='*78}\n{tag}   (decision position {pos})\n{'='*78}")
    hdr = f"{'family':<22}{'n':>4}{'d_goal':>9}{'95% CI':>18}{'sign p':>9}{'+/-':>9}"
    print(hdr); print("-" * len(hdr))
    allv = []
    for fam in sorted(by_fam) + ["ALL"]:
        rs = rows if fam == "ALL" else by_fam[fam]
        v = [r[f"d_goal_{pos}"] for r in rs]
        lo, hi = boot_ci(v)
        p, a, b = sign_test(v)
        print(f"{fam:<22}{len(v):>4}{mean(v):>9.3f}{f'[{lo:.2f},{hi:.2f}]':>18}{p:>9.4f}{f'{a}/{b}':>9}")
    # levels
    print(f"\n{'family':<22}{'margin_cmp':>12}{'margin_inc':>12}{'p_stop_cmp':>12}{'p_stop_inc':>12}")
    for fam in sorted(by_fam) + ["ALL"]:
        rs = rows if fam == "ALL" else by_fam[fam]
        print(f"{fam:<22}"
              f"{mean([r[f'cmp_{pos}_margin'] for r in rs]):>12.3f}"
              f"{mean([r[f'inc_{pos}_margin'] for r in rs]):>12.3f}"
              f"{mean([r[f'cmp_{pos}_p_stop'] for r in rs]):>12.4f}"
              f"{mean([r[f'inc_{pos}_p_stop'] for r in rs]):>12.4f}")
    # continuation awareness in the INCOMPLETE condition
    print(f"\ncontinuation awareness (incomplete cond, {pos}): "
          f"rank of the correct missing token")
    print(f"{'family':<22}{'median rank':>13}{'rank<=1':>9}{'rank<=5':>9}{'rank<=20':>10}{'p_comp':>9}")
    for fam in sorted(by_fam) + ["ALL"]:
        rs = rows if fam == "ALL" else by_fam[fam]
        rk = sorted(r[f"inc_{pos}_comp_rank"] for r in rs)
        med = rk[len(rk) // 2]
        f1 = sum(1 for x in rk if x < 1) / len(rk)
        f5 = sum(1 for x in rk if x < 5) / len(rk)
        f20 = sum(1 for x in rk if x < 20) / len(rk)
        print(f"{fam:<22}{med:>13}{f1:>9.2f}{f5:>9.2f}{f20:>10.2f}"
              f"{mean([r[f'inc_{pos}_p_comp'] for r in rs]):>9.4f}")
    return {fam: mean([r[f"d_goal_{pos}"] for r in (rows if fam == 'ALL' else by_fam[fam])])
            for fam in list(by_fam) + ["ALL"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--pos", default="p2")
    ap.add_argument("--aware-only", action="store_true",
                    help="restrict to items where continuation awareness holds "
                         "(correct missing token in the incomplete condition is "
                         "top-5)")
    args = ap.parse_args()
    for f in args.files:
        rows = [json.loads(l) for l in open(f)]
        if args.aware_only:
            n0 = len(rows)
            rows = [r for r in rows if r[f"inc_{args.pos}_comp_rank"] < 5]
            print(f"[aware-only] {f}: kept {len(rows)}/{n0}")
        if rows:
            report(rows, os.path.basename(f), args.pos)


if __name__ == "__main__":
    main()
