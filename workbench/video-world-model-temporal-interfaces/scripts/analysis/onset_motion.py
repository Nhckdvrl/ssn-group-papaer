"""Motion read-out for the paired onset probe (mg2_probe.py output).

For every rollout and its no-action reference (same image, same noise): dense Farneback flow between
consecutive frames -> per-frame mean horizontal flow u_t (camera yaw) and mean divergence d_t (forward
motion / zoom). Response = action rollout minus reference, so content/noise motion cancels.

Reported per (image, seed, action, onset f):
- first_diff_frame: first frame whose pixels differ from the reference at all (from the probe);
- motion_onset: first frame t where the signed response exceeds thr (default 20% of its steady-state
  value over the last 8 frames) in the action's expected direction;
- pre_onset_resp: mean signed response over frames [first_diff_frame, f) normalised by steady state
  (>0 means the video already moves in the action's direction before the action starts).
Usage: python onset_motion.py <raw_dir> <out_csv>
"""
import csv
import glob
import os
import re
import sys

import cv2
import numpy as np

SIGN = {"cam_r": ("u", -1.0), "cam_l": ("u", 1.0), "fwd": ("div", 1.0)}  # expected sign of response


def flow_stats(frames):
    g = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in frames]
    u = [np.nan]
    dv = [np.nan]
    for a, b in zip(g[:-1], g[1:]):
        fl = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        u.append(float(fl[..., 0].mean()))
        H, W = a.shape
        ys, xs = np.mgrid[0:H, 0:W]
        rx, ry = xs - W / 2, ys - H / 2
        r = np.sqrt(rx ** 2 + ry ** 2) + 1e-6
        dv.append(float(((fl[..., 0] * rx + fl[..., 1] * ry) / r).mean()))  # mean radial flow
    return {"u": np.array(u), "div": np.array(dv)}


def main():
    raw, out = sys.argv[1], sys.argv[2]
    thr_frac = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
    cache = {}
    rows = []
    for f in sorted(glob.glob(os.path.join(raw, "*_f*.npz"))):
        m = re.match(r"(\d+)_s(\d+)_(\w+?)_f(\d+)(?:_d(\d+))?\.npz", os.path.basename(f))
        im, sd, act, onset = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
        dur = int(m.group(5)) if m.group(5) else 0
        ref_key = (im, sd)
        if ref_key not in cache:
            cache[ref_key] = flow_stats(np.load(os.path.join(raw, f"{im}_s{sd}_none.npz"))["frames"])
        z = np.load(f)
        st = flow_stats(z["frames"])
        key, sgn = SIGN[act]
        resp = sgn * (st[key] - cache[ref_key][key])
        steady = np.nanmean(resp[-8:])
        fd = int(z["first_diff_frame"])
        above = np.where(resp > thr_frac * steady)[0]
        above = above[above >= 1]
        mo = int(above[0]) if len(above) else -1
        pre = resp[max(fd, 1):onset]
        rows.append(dict(image=im, seed=sd, action=act, onset=onset, dur=dur, integral=round(float(np.nansum(resp)), 4),
                         first_diff_frame=fd, motion_onset=mo,
                         lag=mo - onset if mo >= 0 else "", steady=round(float(steady), 4),
                         pre_onset_resp=round(float(np.nanmean(pre) / steady), 4) if len(pre) and steady else "",
                         resp=" ".join(f"{x:.3f}" for x in np.nan_to_num(resp))))
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", len(rows), "rows to", out)


if __name__ == "__main__":
    main()
