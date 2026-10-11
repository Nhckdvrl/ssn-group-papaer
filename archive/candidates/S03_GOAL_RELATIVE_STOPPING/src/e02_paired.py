"""
S03 / E02 — paired within-item arm contrasts.

Comparing arms by whether their mean d_stop confidence intervals overlap is
weak: the arms are evaluated on the SAME items, so the item-to-item variance is
shared and should be differenced out.  This script pairs by item_id and tests
the per-item difference, which is the powerful and correct comparison.

  d_stop_arm(item) = log p_stop(complete) - log p_stop(incomplete)

For each arm pair we report the mean paired difference, a bootstrap CI over
items, and an exact sign test.  Seeds are pooled by averaging an item's value
across seeds first, so seed noise does not inflate the item count.
"""
import argparse, json, math, os
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


def load(paths, pos="p2"):
    """key -> d_stop, averaged over the given seed files.

    Keyed by ROW ORDER, not item_id: every run iterates the same stimuli file in
    the same order, whereas item_id is a human-readable label that is not
    guaranteed unique (three A/B labels collide after truncation).  Keying on
    item_id silently merged those items and dropped the item count from 50 to
    47.  The item_id is still carried along and asserted to match across files.
    """
    acc = defaultdict(list)
    labels = {}
    for p in paths:
        for i, l in enumerate(open(p)):
            r = json.loads(l)
            key = (i, r["family"])
            if key in labels:
                assert labels[key] == r["item_id"], \
                    f"stimulus order differs between runs at row {i}"
            labels[key] = r["item_id"]
            d = (math.log(max(r[f"cmp_{pos}_p_stop"], EPS))
                 - math.log(max(r[f"inc_{pos}_p_stop"], EPS)))
            acc[key].append(d)
    return {k: mean(v) for k, v in acc.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/e02/final")
    ap.add_argument("--seeds", nargs="+", default=["0", "1"])
    ap.add_argument("--stim", default="e01.jsonl")
    ap.add_argument("--base", default="results/e01/olmo3-7b_base_grafted.jsonl")
    ap.add_argument("--pos", default="p2")
    args = ap.parse_args()

    arms = {}
    for a in ["R", "Rmlp", "S", "F"]:
        ps = [f"{args.dir}/{a}_s{s}/{args.stim}" for s in args.seeds]
        ps = [p for p in ps if os.path.exists(p)]
        if ps:
            arms[a] = load(ps, args.pos)
            print(f"{a}: {len(ps)} seed file(s)")
    if os.path.exists(args.base):
        arms["base"] = load([args.base], args.pos)

    print(f"\nmean d_stop per arm (items averaged over seeds)")
    for a, d in arms.items():
        v = list(d.values())
        lo, hi = boot_ci(v)
        print(f"  {a:<6} n={len(v):<4} {mean(v):7.2f}  [{lo:.2f}, {hi:.2f}]")

    pairs = [("R", "base"), ("Rmlp", "base"), ("S", "base"), ("F", "base"),
             ("S", "R"), ("F", "R"), ("Rmlp", "R"), ("F", "S")]
    print(f"\npaired within-item contrasts")
    hdr = f"  {'contrast':<14}{'n':>4}{'mean diff':>11}{'95% CI':>18}{'sign p':>9}{'+/-':>9}"
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for a, b in pairs:
        if a not in arms or b not in arms:
            continue
        ks = sorted(set(arms[a]) & set(arms[b]))
        v = [arms[a][k] - arms[b][k] for k in ks]
        lo, hi = boot_ci(v)
        p, pos_n, neg_n = sign_test(v)
        print(f"  {a + ' - ' + b:<14}{len(v):>4}{mean(v):>11.2f}"
              f"{f'[{lo:.2f}, {hi:.2f}]':>18}{p:>9.2}{f'{pos_n}/{neg_n}':>9}")

    # how much of the base -> F gain does the frozen-state readout recover?
    if all(k in arms for k in ("R", "F", "base")):
        ks = sorted(set(arms["R"]) & set(arms["F"]) & set(arms["base"]))
        gR = mean([arms["R"][k] - arms["base"][k] for k in ks])
        gF = mean([arms["F"][k] - arms["base"][k] for k in ks])
        print(f"\n  readout-only recovers {100 * gR / gF:.0f}% of the "
              f"base->full-SFT gain ({gR:.2f} of {gF:.2f} log-units)")


if __name__ == "__main__":
    main()
