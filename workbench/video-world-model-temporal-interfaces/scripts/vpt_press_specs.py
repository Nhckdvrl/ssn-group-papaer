"""Build yaw-key replay trajectories from real human key presses (VPT contractor logs, 20 Hz) (E29).

Human a/d presses are replayed as turn-left/turn-right keys on a latent-rate interface: a latent is "pressed"
if the key is down at any time inside that latent's frames (latching, like a real key-event queue), and every
pressed latent commands `amp` degrees of yaw. Windows of `n_lat` latents (latent = 4 frames at `fps`) with
1-3 presses (onset at latent >= 2, isolated by >= 3 latents) are kept. Output: JSON list of
{src, t0, spec ('yawlist:k=v_...'), presses: [(onset_k, n_latents, sign)]}.
Usage: python vpt_press_specs.py data/vpt_actions results/raw/e29_specs.json [--fps 16 --n_lat 20 --max 24]
"""
import argparse
import glob
import json
import os

import numpy as np


def presses(x):
    e = np.diff(np.r_[0, x, 0])
    return list(zip(np.flatnonzero(e == 1), np.flatnonzero(e == -1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=16.0)
    ap.add_argument("--n_lat", type=int, default=20)
    ap.add_argument("--amp", type=float, default=3.0)
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--per_file", type=int, default=2)
    a = ap.parse_args()
    lat_s = 4.0 / a.fps
    out = []
    for f in sorted(glob.glob(os.path.join(a.src, "*.jsonl"))):
        try:
            L = [json.loads(l) for l in open(f)]
        except Exception:
            continue
        keys = [set(l.get("keyboard", {}).get("keys") or []) for l in L]
        sgn = np.array([("key.keyboard.d" in k) - ("key.keyboard.a" in k) for k in keys])  # +1 right, -1 left
        t = np.arange(len(L)) / 20.0
        win_s = a.n_lat * lat_s
        t0, n_file = 0.0, 0
        while t0 + win_s < t[-1] and len(out) < a.max and n_file < a.per_file:
            sel = (t >= t0) & (t < t0 + win_s)
            # latent j (1..n_lat-1) covers [t0 + (j-1)*lat_s + lat_s/4 , t0 + j*lat_s]; command y[j-1]
            y = np.zeros(a.n_lat - 1)
            for j in range(1, a.n_lat):
                m = sel & (t >= t0 + (j - 1) * lat_s) & (t < t0 + j * lat_s)
                s = sgn[m]
                if (s != 0).any():
                    y[j - 1] = a.amp * np.sign(s[s != 0].mean())
            pr = [(int(on), int(off - on), int(np.sign(y[on]))) for on, off in presses((y != 0).astype(int))]
            ok = 1 <= len(pr) <= 3 and all(p[0] >= 2 for p in pr) and \
                all(pr[i + 1][0] - (pr[i][0] + pr[i][1]) >= 3 for i in range(len(pr) - 1)) and \
                pr[-1][0] + pr[-1][1] <= a.n_lat - 4
            if ok:
                spec = "yawlist:" + "_".join(f"{k}={v:g}" for k, v in enumerate(y) if v)
                out.append(dict(src=os.path.basename(f), t0=round(t0, 2), spec=spec, presses=pr))
                t0 += win_s
                n_file += 1
            else:
                t0 += lat_s
        if len(out) >= a.max:
            break
    json.dump(out, open(a.out, "w"), indent=1)
    P = [p for o in out for p in o["presses"]]
    print(f"{len(out)} windows from {len(set(o['src'] for o in out))} players; {len(P)} presses; "
          f"1-latent {sum(p[1] == 1 for p in P)}, onset on block-first {sum((p[0] + 1) % 4 == 0 for p in P)}")


if __name__ == "__main__":
    main()
