"""S03 / E02 — the four-arm comparison table.

Reads each arm's E01 measurements and its held-out stopping co-metric, and
prints them against the two frozen reference points (Arm 0 = pretrained base in
the E02 format, and the naturally post-trained SFT sibling).

The co-metric column is load-bearing: an arm that never learned generic
boundary stopping has not failed the goal test, it has failed to train, and its
d_stop must not be read as evidence about where goal information lives.
"""
import argparse, json, math, os, sys
from collections import defaultdict

EPS = 1e-45


def mean(v): return sum(v) / len(v) if v else float("nan")


def boot_ci(v, n=4000, seed=0):
    import random
    rng = random.Random(seed); k = len(v)
    ms = sorted(mean([v[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n)]


def d_stop_of(path, pos="p2", fam=None):
    rows = [json.loads(l) for l in open(path)]
    if fam:
        rows = [r for r in rows if r["family"].startswith(fam)]
    ds = [math.log(max(r[f"cmp_{pos}_p_stop"], EPS)) - math.log(max(r[f"inc_{pos}_p_stop"], EPS))
          for r in rows]
    dg = [r[f"d_goal_{pos}"] for r in rows]
    pos_n = sum(1 for x in ds if x > 0)
    return dict(n=len(ds), d_stop=mean(ds), ci=boot_ci(ds), d_goal=mean(dg),
                sign=f"{pos_n}/{len(ds)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", nargs="+", required=True,
                    help="results/e02/<tag> directories")
    ap.add_argument("--base", default="results/e01/olmo3-7b_base_grafted.jsonl")
    ap.add_argument("--target", default="results/e01/olmo3-7b_sft_eosonly.jsonl")
    ap.add_argument("--pos", default="p2")
    args = ap.parse_args()

    ref = [("Arm 0  base (no training)", args.base, None),
           ("natural SFT (target)", args.target, None)]
    rows = []
    for name, path, _ in ref:
        if os.path.exists(path):
            rows.append((name, d_stop_of(path, args.pos), None))
    for d in args.arms:
        p = f"{d}/e01.jsonl"
        if not os.path.exists(p):
            print(f"[skip] no e01 eval in {d}", file=sys.stderr); continue
        cfg = json.load(open(f"{d}/config.json"))
        hist = [json.loads(l) for l in open(f"{d}/history.jsonl")]
        co = hist[-1]
        rows.append((f"Arm {cfg['arm']}  (lr {cfg['lr']}, {cfg['n_trainable']:,} params)",
                     d_stop_of(p, args.pos), co))

    print(f"\n{'':<44}{'d_stop':>9}{'95% CI':>16}{'sign':>9}"
          f"{'d_goal':>9}{'val_loss':>10}{'bnd_auc':>9}")
    print("-" * 106)
    for name, s, co in rows:
        extra = (f"{co['val_loss']:>10.4f}{co['boundary_auc']:>9.4f}"
                 if co else f"{'':>10}{'':>9}")
        print(f"{name:<44}{s['d_stop']:>9.2f}"
              f"{f'[{s['ci'][0]:.1f},{s['ci'][1]:.1f}]':>16}{s['sign']:>9}"
              f"{s['d_goal']:>9.2f}{extra}")

    # per-family
    print(f"\nby family (d_stop)")
    fams = [("A bounded quantity", "A"), ("B semantic predicate", "B"),
            ("C slot requirement", "C")]
    hdr = f"{'':<44}" + "".join(f"{f[0][:18]:>20}" for f in fams)
    print(hdr); print("-" * len(hdr))
    for name, _, co in rows:
        path = (args.base if name.startswith("Arm 0") else
                args.target if name.startswith("natural") else None)
        if path is None:
            d = [a for a in args.arms
                 if f"Arm {json.load(open(f'{a}/config.json'))['arm']}  " in name][0]
            path = f"{d}/e01.jsonl"
        cells = "".join(f"{d_stop_of(path, args.pos, f[1])['d_stop']:>20.2f}" for f in fams)
        print(f"{name:<44}{cells}")


if __name__ == "__main__":
    main()
