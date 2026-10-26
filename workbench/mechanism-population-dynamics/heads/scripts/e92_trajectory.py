"""E92 trajectories: learned-then-lost capabilities, emergence-time dispersion across seeds, loss jumps.

Usage: e92_trajectory.py [--min_ckpts 5] -> prints per size and writes results/e92/trajectory.json
Definitions (per run x task, accuracy at the available checkpoints, final = rev main = step 143000):
  lost       peak >= 0.15, and the last two checkpoints are both <= peak - max(0.1, 0.5 * peak)
             (a fall that persists to the end of training)
  emergence  first checkpoint with accuracy >= 0.5 * (median final accuracy across the size's normal seeds),
             only for tasks whose median final accuracy >= 0.3
  loss jump  validation loss rises by > 0.05 nats between consecutive available checkpoints
Normal seeds exclude the two PolyPythias outliers (410M seed3, seed4).
"""
import argparse
import glob
import json
import re

import numpy as np

import mp_common as mc

DIR = mc.RESULTS / "e92"
OUTLIERS = {("410m", "seed3"), ("410m", "seed4")}


def load():
    R = {}
    for f in glob.glob(str(DIR / "pythia-*__*.json")):
        m = re.match(r"pythia-(\d+m)(-seed\d)?__(.+)\.json", f.split("/")[-1])
        size, seed, rev = m.group(1), (m.group(2) or "-seed0")[1:], m.group(3)
        step = 143000 if rev == "main" else int(rev[4:])
        R.setdefault(size, {}).setdefault(seed, {})[step] = json.loads(open(f).read())
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min_ckpts", type=int, default=5)
    a = ap.parse_args()
    R = load()
    out = {}
    for size in ("14m", "31m", "70m", "160m", "410m"):
        if size not in R:
            continue
        runs = {s: v for s, v in R[size].items() if len(v) >= a.min_ckpts and 143000 in v}
        if not runs:
            continue
        tasks = list(next(iter(runs.values()))[143000]["tasks"])
        normal = [s for s in runs if (size, s) not in OUTLIERS]
        print(f"\n== {size}: {len(runs)} runs with >= {a.min_ckpts} checkpoints (steps of first: {sorted(next(iter(runs.values())))})")
        lost, emerg, jumps = {}, {}, {}
        for s, traj in sorted(runs.items()):
            steps = sorted(traj)
            L = [traj[st]["lm_loss"] for st in steps]
            jumps[s] = [(steps[i], round(L[i] - L[i - 1], 3)) for i in range(1, len(steps)) if L[i] - L[i - 1] > 0.05]
            for t in tasks:
                acc = np.array([traj[st]["tasks"][t]["acc"] for st in steps])
                pk = acc.max()
                if pk >= 0.15 and len(acc) >= 3 and acc[-1] <= pk - max(0.1, 0.5 * pk) and acc[-2] <= pk - max(0.1, 0.5 * pk):
                    lost.setdefault(t, []).append({"seed": s, "peak": round(float(pk), 2), "peak_step": int(steps[int(acc.argmax())]),
                                                   "final": round(float(acc[-1]), 2)})
        for t in tasks:
            med = np.median([runs[s][143000]["tasks"][t]["acc"] for s in normal])
            if med < 0.3:
                continue
            e = []
            for s in normal:
                steps = sorted(runs[s])
                hit = [st for st in steps if runs[s][st]["tasks"][t]["acc"] >= 0.5 * med]
                e.append(hit[0] if hit else None)
            emerg[t] = e
        print("loss jumps (>0.05 nats):", {s: j for s, j in jumps.items() if j})
        print("learned-then-lost (task: n_normal_seeds | details):")
        for t, v in sorted(lost.items(), key=lambda kv: -len(kv[1])):
            nn = sum((size, x["seed"]) not in OUTLIERS for x in v)
            print(f"  {t:28s} normal={nn} all={len(v)} | " + "; ".join(f"{x['seed']} {x['peak']}@{x['peak_step']}->{x['final']}" for x in v))
        print("emergence step across normal seeds (tasks with median final >= 0.3):")
        for t, e in emerg.items():
            ev = [x for x in e if x is not None]
            print(f"  {t:28s} " + " ".join(str(x) for x in e) + (f" | spread {min(ev)}..{max(ev)}" if ev else ""))
        out[size] = {"lost": lost, "emergence": emerg, "loss_jumps": jumps, "runs": sorted(runs)}
    (DIR / "trajectory.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
