"""Per-press registration for human key-press replays (E29: vpt_press_specs.py + mwm_sysid / mwm_overlap).

For each rollout <tag>_p<id>_s<seed>_<yawlist spec>.npz and its paired <tag>_..._none.npz, the realised yaw per
latent is the phase-correlation shift (per_latent). Presses are maximal runs of commanded latents. Registration of
a press = realised shift over [onset, onset+dur+2) / (g * commanded degrees), with g the model's own gain
(median px/deg over presses whose onset is not on a block-first latent and that last >= 2 latents).
Block-first onset: the press's first commanded latent k+1 is the first latent of a 4-latent block ((k+1) % 4 == 0).
Usage: python press_replay.py <raw_dir> [out_json]
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from mwm_bandwidth import per_latent  # noqa: E402
from sysid import shifts  # noqa: E402


def runs(y):
    e = np.diff(np.r_[0, (y != 0).astype(int), 0])
    return list(zip(np.flatnonzero(e == 1), np.flatnonzero(e == -1) - np.flatnonzero(e == 1)))


def main():
    raw = sys.argv[1]
    refs, rows = {}, defaultdict(list)
    for f in sorted(glob.glob(os.path.join(raw, "*.npz"))):
        m = re.match(r"(\w+?)_p(\d+)_s(\d+)_(.*)\.npz", os.path.basename(f))
        tag, spec = m.group(1), m.group(4)
        if spec == "none":
            continue
        key = f"{tag}_p{m.group(2)}_s{m.group(3)}"
        if key not in refs:
            refs[key] = shifts(np.load(os.path.join(raw, key + "_none.npz"))["frames"])
        z = np.load(f)
        y = z["yaw_cmd"]
        rl = per_latent(-(shifts(z["frames"]) - refs[key]), len(y) + 1)[1:]  # rl[k] = latent k+1
        for on, dur in runs(y):
            cmd = float(y[on:on + dur].sum())
            got = float(rl[on:on + dur + 2].sum())
            rows[tag].append(dict(seam=(on + 1) % 4 == 0, dur=int(dur), cmd=cmd, got=got))
        rows[tag + "@heading"].append((float(rl.sum()), float(y.sum())))
    res = {}
    for tag in sorted(t for t in rows if "@" not in t):
        R = rows[tag]
        g = float(np.median([r["got"] / r["cmd"] for r in R if not r["seam"] and r["dur"] >= 2]))
        reg = lambda sel: [r["got"] / (g * r["cmd"]) for r in R if sel(r)]  # noqa: E731
        seam, other = reg(lambda r: r["seam"]), reg(lambda r: not r["seam"])
        seam1, other1 = reg(lambda r: r["seam"] and r["dur"] == 1), reg(lambda r: not r["seam"] and r["dur"] == 1)
        H = rows[tag + "@heading"]
        herr = [abs(h / g - c) for h, c in H]
        res[tag] = dict(gain_px_per_deg=round(g, 3),
                        reg_seam=[round(float(np.mean(seam)), 3), len(seam)],
                        reg_other=[round(float(np.mean(other)), 3), len(other)],
                        lost_seam=round(float(np.mean(np.array(seam) < 0.3)), 3),
                        lost_other=round(float(np.mean(np.array(other) < 0.3)), 3),
                        reg_seam_1lat=[round(float(np.mean(seam1)), 3) if seam1 else None, len(seam1)],
                        reg_other_1lat=[round(float(np.mean(other1)), 3) if other1 else None, len(other1)],
                        heading_err_deg=[round(float(np.mean(herr)), 2), len(herr)])
        print(tag, res[tag])
    if len(sys.argv) > 2:
        json.dump(res, open(sys.argv[2], "w"), indent=1)


if __name__ == "__main__":
    main()
