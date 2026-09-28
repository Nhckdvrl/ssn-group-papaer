"""Analysis of mg2_sysid.py outputs (paired against the same-seed no-action reference).

Yaw read-out: per-frame global horizontal shift from phase correlation (Hann window, grayscale) between
consecutive frames; response r_t = shift(action) - shift(reference); sign flipped so that a right turn
(positive yaw command) gives positive response.

impulse: kernel h_tau = r_{f+1+tau}, tau = -4..8; integral over all frames; grouped by amplitude and by
         phase of the pulse frame f inside its latent step, (f-1) mod 4 (f=1..4 -> latent 1 ...).
sine:    least-squares fit of r_t (t >= t0+4) on sin/cos at the input frequency -> gain and phase lag
         (in frames); plus residual power at the alias frequencies |k/4 - 1/P|.
Usage: python sysid.py <raw_dir> <out_json>
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

import cv2
import numpy as np


def shifts(frames):
    g = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32) for f in frames]
    win = cv2.createHanningWindow(g[0].shape[::-1], cv2.CV_32F)
    out = [0.0]
    for a, b in zip(g[:-1], g[1:]):
        (dx, dy), _ = cv2.phaseCorrelate(a, b, win)
        out.append(dx)
    return np.array(out)


def main():
    raw, out = sys.argv[1], sys.argv[2]
    refs = {}
    imp = defaultdict(list)
    sines = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(raw, "*.npz"))):
        b = os.path.basename(f)
        m = re.match(r"((\d+)_s(\d+)_L\d+(?:_K\d+)?)_(.*)\.npz", b)
        key, im, sd, spec = m.group(1), m.group(2), int(m.group(3)), m.group(4).replace("~", ":")
        if spec == "none":
            continue
        if key not in refs:
            refs[key] = shifts(np.load(os.path.join(raw, f"{key}_none.npz"))["frames"])
        r = -(shifts(np.load(f)["frames"]) - refs[key])  # camera right -> content moves left
        p = spec.split(":")
        if p[0] == "impulse":
            A, fr = float(p[1]), int(p[2])
            ker = [r[fr + 1 + t] if 0 <= fr + 1 + t < len(r) else np.nan for t in range(-4, 9)]
            imp[(A, (fr - 1) % 4)].append(dict(image=im, seed=sd, f=fr, integral=float(np.nansum(r)),
                                                kernel=[float(x) for x in ker]))
        elif p[0] == "sine":
            A, P, phi, t0 = float(p[1]), float(p[2]), float(p[3]), 9
            t = np.arange(len(r))
            sel = t >= t0 + 4
            w = 2 * np.pi / P
            X = np.stack([np.sin(w * (t[sel] - t0) + phi), np.cos(w * (t[sel] - t0) + phi)], 1)
            coef, *_ = np.linalg.lstsq(X, r[sel], rcond=None)
            gain = float(np.hypot(*coef))
            lag = float(-np.arctan2(coef[1], coef[0]) / w)  # frames
            resid = r[sel] - X @ coef
            sines[P].append(dict(image=im, seed=sd, phi=phi, gain=gain, lag_frames=lag,
                                 resid_rms=float(resid.std()), resp_rms=float(r[sel].std())))
    res = {"impulse": {}, "sine": {}}
    for (A, ph), v in sorted(imp.items()):
        K = np.array([x["kernel"] for x in v])
        I = np.array([x["integral"] for x in v])
        res["impulse"][f"A{A}_phase{ph}"] = dict(n=len(v), integral_mean=float(I.mean()),
                                                 integral_sem=float(I.std() / np.sqrt(len(I))),
                                                 kernel_mean=[round(float(x), 3) for x in np.nanmean(K, 0)],
                                                 rows=v)
    for P, v in sorted(sines.items()):
        g = np.array([x["gain"] for x in v])
        res["sine"][str(P)] = dict(n=len(v), gain_mean=float(g.mean()), gain_sem=float(g.std() / np.sqrt(len(g))),
                                   lag_mean=float(np.mean([x["lag_frames"] for x in v])),
                                   resid_over_resp=float(np.mean([x["resid_rms"] / max(x["resp_rms"], 1e-6) for x in v])),
                                   rows=v)
    json.dump(res, open(out, "w"), indent=1)
    print("impulse integral by amplitude/phase:")
    for k, v in res["impulse"].items():
        print(f"  {k}: {v['integral_mean']:.2f} +- {v['integral_sem']:.2f} (n={v['n']}) kernel {v['kernel_mean']}")
    print("sine gain by period (frames):")
    for k, v in res["sine"].items():
        print(f"  P={k}: gain {v['gain_mean']:.3f} +- {v['gain_sem']:.3f} lag {v['lag_mean']:.2f} resid/resp {v['resid_over_resp']:.2f} (n={v['n']})")


if __name__ == "__main__":
    main()
