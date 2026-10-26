"""E92 analysis: seed distributions of capabilities per size, and per-run trajectories (learned / lost).

Usage: e92_analyze.py -> prints the endpoint table and writes results/e92/analysis.json
Endpoint readout per size x task: accuracy of the 10 seeds (final = rev main), spread, the largest gap between sorted
seed values (a crude bimodality check with 10 points), and the fraction of seeds above 0.5 accuracy.
"""
import glob
import json
import re

import numpy as np

import mp_common as mc

DIR = mc.RESULTS / "e92"
SIZES = ["14m", "31m", "70m", "160m", "410m"]


def load():
    R = {}
    for f in glob.glob(str(DIR / "pythia-*__*.json")):
        m = re.match(r"pythia-(\d+m)(-seed\d)?__(.+)\.json", f.split("/")[-1])
        size, seed, rev = m.group(1), m.group(2) or "-seed0", m.group(3)
        step = 143000 if rev == "main" else int(rev[4:])
        R.setdefault(size, {}).setdefault(seed[1:], {})[step] = json.loads(open(f).read())
    return R


def main():
    R = load()
    tasks = list(next(iter(next(iter(R.values())).values()))[143000]["tasks"].keys())
    out = {"endpoint": {}}
    for size in SIZES:
        if size not in R:
            continue
        seeds = sorted(s for s in R[size] if 143000 in R[size][s])
        print(f"\n== {size}  ({len(seeds)} seeds)   task: mean | min..max | largest gap | frac>0.5 | per-seed (seed0..9)")
        for t in tasks:
            v = np.array([R[size][s][143000]["tasks"][t]["acc"] for s in seeds])
            sv = np.sort(v)
            gaps = np.diff(sv)
            g = float(gaps.max()) if len(gaps) else 0.0
            row = {"seeds": seeds, "acc": v.round(3).tolist(), "mean": float(v.mean()), "range": [float(v.min()), float(v.max())],
                   "largest_gap": g, "gap_at": float(sv[int(np.argmax(gaps))]) if len(gaps) else None, "frac_gt_half": float((v > .5).mean())}
            out["endpoint"].setdefault(size, {})[t] = row
            flag = " <<" if g >= 0.25 and 0.05 < (v > sv[int(np.argmax(gaps))]).mean() < 0.95 else ""
            print(f"{t:28s} {v.mean():.2f} | {v.min():.2f}..{v.max():.2f} | {g:.2f} | {(v > .5).mean():.1f} | {' '.join(f'{x:.2f}' for x in v)}{flag}")
        losses = [R[size][s][143000]["lm_loss"] for s in seeds]
        print(f"{'lm_loss':28s} " + " ".join(f"{x:.3f}" for x in losses))
    (DIR / "analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
