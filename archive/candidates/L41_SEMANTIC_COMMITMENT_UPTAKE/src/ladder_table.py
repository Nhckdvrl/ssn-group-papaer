"""E01-A direct-control exposure ladder table.

For every evaluation checkpoint in a run, report

  U(A+), U(A-)                 raw pre->post neutral-belief change
  drift                        same quantity on NEVER-TRAINED propositions
  spill                        same quantity on the near-miss probe of a
                               *trained* proposition (agent seen, event not)
  U+_c, U-_c                   drift-corrected  (U - drift)
  D = U+ - U-                  unaffected by any common additive drift
  CI, p                        bootstrap over proposition identity
  genNLL                       held-out generic-text NLL (capability sanity)
"""
import json, sys, random, argparse, statistics as st

IFACE = "fs"
def mean(x): return sum(x) / len(x) if x else float("nan")

def uptake(bb, ba, pid, iface, nm=False):
    if nm:
        return ba[pid]["nm_" + iface] - bb[pid]["nm_" + iface]
    return mean(ba[pid][iface]) - mean(bb[pid][iface])

def boot_diff(a, b, B=10000, seed=7):
    rng = random.Random(seed)
    pt = mean(a) - mean(b)
    dr = sorted(mean([a[rng.randrange(len(a))] for _ in a]) -
                mean([b[rng.randrange(len(b))] for _ in b]) for _ in range(B))
    p = 2 * min(sum(d <= 0 for d in dr), sum(d >= 0 for d in dr)) / B
    return pt, dr[int(.025 * B)], dr[int(.975 * B)], min(1.0, p)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--iface", default=IFACE)
    ap.add_argument("--plus", default="Ap")
    ap.add_argument("--minus", default="An")
    a = ap.parse_args()

    for path in a.runs:
        r = json.load(open(path))
        ar, bb, asg = r["args"], r["B_before"], r["assign"]
        print(f"\n=== {path.split('/')[-1]}   lr={ar['lr']:.0e} bs={ar['bs']} "
              f"n_docs={ar['n_docs']} sched={ar.get('sched','?')} "
              f"generic_ratio={ar.get('generic_ratio',0)} "
              f"base wikiNLL={r['generic_nll_before']:.3f} "
              f"base pileNLL={r.get('pile_nll_before',float('nan')):.3f}")
        print(f"{'exp':>5} {'U(A+)':>8} {'U(A-)':>8} {'drift':>8} {'spill':>8} "
              f"{'U+_c':>8} {'U-_c':>8} {'D':>8} {'95% CI':>18} {'p':>7} {'wikiNLL':>8} {'pileNLL':>8}")
        for k in sorted(r["traj"], key=int):
            t = r["traj"][k]; ba = t["B"]
            up = [uptake(bb, ba, p, a.iface) for p in asg if asg[p] == a.plus]
            un = [uptake(bb, ba, p, a.iface) for p in asg if asg[p] == a.minus]
            dr = [uptake(bb, ba, p, a.iface) for p in asg if asg[p] == "HOLD"]
            sp = [uptake(bb, ba, p, a.iface, nm=True) for p in asg if asg[p] in (a.plus, a.minus)]
            d, lo, hi, pv = boot_diff(up, un)
            dm = mean(dr) if dr else 0.0
            print(f"{t['exposures']:5d} {mean(up):+8.3f} {mean(un):+8.3f} {dm:+8.3f} "
                  f"{mean(sp):+8.3f} {mean(up)-dm:+8.3f} {mean(un)-dm:+8.3f} {d:+8.3f} "
                  f"[{lo:+6.2f},{hi:+6.2f}] {pv:7.4f} {t['generic_nll']:8.3f} {t.get('pile_nll',float('nan')):8.3f}")

main()
