"""
S03 — normalizer-free decomposition of the goal effect.

Why this exists.  The headline quantity has been

    d_stop = log p(STOP | goal complete) - log p(STOP | goal incomplete)

but log p_stop = z_stop - log Z, so d_stop carries a  -(log Z_c - log Z_i)
term: a whole-vocabulary normalizer difference between two *different* prompts.
That term is not a property of the stop action, so any statement of the form
"this component is the stop readout and that component is internal state"
should not rest on it.

This script recomputes everything from the stored raw logits:

    dz_stop = z_STOP(complete) - z_STOP(incomplete)
    dz_cont = z_CONT(complete) - z_CONT(incomplete)
    d_goal  = dz_stop - dz_cont          (exact; the normalizer cancels)
    dlogZ   = dz_stop - d_stop           (how much normalizer drift there was)

If the conclusions are the same under dz_stop as under d_stop, the normalizer
was never load-bearing and the claim is safe.  No GPU needed.
"""
import argparse, json, math, os, sys
from collections import defaultdict

EPS = 1e-45


def mean(v): return sum(v) / len(v) if v else float("nan")


def boot_ci(v, n=20000, seed=0):
    import random
    rng = random.Random(seed); k = len(v)
    ms = sorted(mean([v[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n)]


def sign_test(v):
    pos = sum(1 for x in v if x > 0); neg = sum(1 for x in v if x < 0)
    n = pos + neg
    if n == 0: return 1.0, pos, neg
    tail = sum(math.comb(n, k) for k in range(min(pos, neg) + 1)) / 2 ** n
    return min(1.0, 2 * tail), pos, neg


def rows_of(paths, pos="p2"):
    """row index -> dict of per-item quantities, averaged over seed files."""
    acc = defaultdict(lambda: defaultdict(list))
    for p in paths:
        for i, l in enumerate(open(p)):
            r = json.loads(l)
            dz_stop = r[f"cmp_{pos}_stop_logit"] - r[f"inc_{pos}_stop_logit"]
            dz_cont = r[f"cmp_{pos}_comp_logit"] - r[f"inc_{pos}_comp_logit"]
            d_stop = (math.log(max(r[f"cmp_{pos}_p_stop"], EPS))
                      - math.log(max(r[f"inc_{pos}_p_stop"], EPS)))
            acc[i]["dz_stop"].append(dz_stop)
            acc[i]["dz_cont"].append(dz_cont)
            acc[i]["d_goal"].append(dz_stop - dz_cont)
            acc[i]["d_stop"].append(d_stop)
            d_comp = (math.log(max(r[f"cmp_{pos}_p_comp"], EPS))
                      - math.log(max(r[f"inc_{pos}_p_comp"], EPS)))
            acc[i]["d_comp"].append(d_comp)
            acc[i]["dlogZ"].append(dz_stop - d_stop)
            acc[i]["family"] = r["family"]
    return {i: {k: (mean(v) if isinstance(v, list) else v) for k, v in d.items()}
            for i, d in acc.items()}


def resolve(spec):
    """'name=path[,path...]' -> (name, [paths])"""
    name, _, paths = spec.partition("=")
    ps = [p for p in paths.split(",") if os.path.exists(p)]
    return name, ps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+", help="label=path[,path2]")
    ap.add_argument("--pos", default="p2")
    ap.add_argument("--vs", default=None, help="label to take paired contrasts against")
    ap.add_argument("--metrics", nargs="+", default=["dz_stop", "dz_cont", "d_goal"],
                    help="which quantities to take paired contrasts on")
    args = ap.parse_args()

    data = {}
    for spec in args.specs:
        name, ps = resolve(spec)
        if not ps:
            print(f"[skip] {name}: no files", file=sys.stderr); continue
        data[name] = rows_of(ps, args.pos)

    print(f"\n{'':<14}| gauge-free |---- probability gauge ----|--- raw-logit gauge ---|")
    print(f"{'':<14}{'d_goal':>9} | {'d_stop':>8}{'d_comp':>9}{'stop%':>7} | "
          f"{'dz_stop':>9}{'dz_cont':>9}{'dlogZ':>8}")
    print("-" * 82)
    for name, d in data.items():
        g = mean([r["d_goal"] for r in d.values()])
        ds = mean([r["d_stop"] for r in d.values()])
        print(f"{name:<14}{g:>9.2f} | {ds:>8.2f}"
              f"{mean([r['d_comp'] for r in d.values()]):>9.2f}"
              f"{100 * ds / g if g else float('nan'):>6.0f}% | "
              f"{mean([r['dz_stop'] for r in d.values()]):>9.2f}"
              f"{mean([r['dz_cont'] for r in d.values()]):>9.2f}"
              f"{mean([r['dlogZ'] for r in d.values()]):>8.2f}")

    if args.vs and args.vs in data:
        base = data[args.vs]
        for metric in args.metrics:
            print(f"\npaired contrasts against '{args.vs}'  --  {metric}")
            hdr = (f"  {'contrast':<24}{'diff':>9}{'95% CI':>16}{'sign p':>9}{'+/-':>9}")
            print(hdr); print("  " + "-" * (len(hdr) - 2))
            for name, d in data.items():
                if name == args.vs: continue
                ks = sorted(set(d) & set(base))
                v = [d[k][metric] - base[k][metric] for k in ks]
                lo, hi = boot_ci(v); p, a, b = sign_test(v)
                print(f"  {name + ' - ' + args.vs:<24}{mean(v):>9.2f}"
                      f"{f'[{lo:.2f},{hi:.2f}]':>16}{p:>9.2}{f'{a}/{b}':>9}")


if __name__ == "__main__":
    main()
