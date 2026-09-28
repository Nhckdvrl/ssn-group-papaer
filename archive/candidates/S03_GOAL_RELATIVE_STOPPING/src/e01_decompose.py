"""
S03 / E01 decisive control — is d_goal a STOP-side effect or a CONTINUATION-side
effect?

d_goal is a margin difference, so it is invariant to the softmax normalisation
of the two (different) prompts:

    d_goal = [log p_stop(cmp) - log p_stop(inc)] - [log p_comp(cmp) - log p_comp(inc)]
           =            d_stop                   -            d_comp

Both halves are individually comparable across conditions because they are
log-probabilities.  The distinction matters for the parent question:

  * d_stop >> 0  : satisfying the user's goal genuinely RAISES the stop action.
                   This is goal-relative stopping.
  * d_stop ~ 0, d_comp << 0 : the model merely keeps CONTINUING when the goal
                   is unmet.  That is goal-relative continuation, and it does
                   NOT show that goal completion controls the stop action.

Scientific invariant 3 in reverse: a margin can move without the stop action
moving at all, and we must not report the former as the latter.
"""
import json, math, sys
from collections import defaultdict

EPS = 1e-45


def mean(v): return sum(v) / len(v) if v else float("nan")


def boot_ci(v, n=4000, seed=0):
    import random
    rng = random.Random(seed); k = len(v)
    ms = sorted(mean([v[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n)]


def main():
    pos = "p2"
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for a in sys.argv[1:]:
        if a.startswith("--pos="): pos = a.split("=")[1]
    print(f"{'file':<34}{'fam':<6}{'n':>4}{'d_goal':>9}{'d_stop':>9}"
          f"{'d_stop CI':>16}{'d_comp':>9}{'stop%':>8}")
    print("-" * 95)
    for f in args:
        rows = [json.loads(l) for l in open(f)]
        by = defaultdict(list)
        for r in rows:
            by[r["family"][0]].append(r)
        by["*"] = rows
        for fam in sorted(by):
            rs = by[fam]
            dstop, dcomp, dgoal = [], [], []
            for r in rs:
                ds = math.log(max(r[f"cmp_{pos}_p_stop"], EPS)) - math.log(max(r[f"inc_{pos}_p_stop"], EPS))
                dc = math.log(max(r[f"cmp_{pos}_p_comp"], EPS)) - math.log(max(r[f"inc_{pos}_p_comp"], EPS))
                dstop.append(ds); dcomp.append(dc); dgoal.append(r[f"d_goal_{pos}"])
            lo, hi = boot_ci(dstop)
            # share of the margin shift carried by the stop side
            share = 100 * mean(dstop) / mean(dgoal) if mean(dgoal) != 0 else float("nan")
            name = f.split("/")[-1].replace(".jsonl", "")
            print(f"{name:<34}{fam:<6}{len(rs):>4}{mean(dgoal):>9.2f}{mean(dstop):>9.2f}"
                  f"{f'[{lo:.1f},{hi:.1f}]':>16}{mean(dcomp):>9.2f}{share:>8.0f}")
        print()


if __name__ == "__main__":
    main()
