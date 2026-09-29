"""Build yaw-key replay trajectories from real human key presses (VPT contractor logs, 20 Hz) (E29).

Human a/d presses are replayed as turn-left/turn-right keys on a latent-rate interface: a latent is "pressed"
if the key is down at any time inside that latent's frames (latching, like a real key-event queue), and every
pressed latent commands `amp` degrees of yaw. Windows of `n_lat` latents (latent = 4 frames at `fps`) with
1-3 presses (onset at latent >= 2, isolated by >= 3 latents) are kept. Output: JSON list of
{src, t0, spec ('yawlist:k=v_...'), presses: [(onset_k, n_latents, sign)]}.

Default (legacy, used for the first E29/E29b runs): the window slides one latent at a time and is accepted as soon
as the constraints hold. This pins the last press's end to latent n_lat-4 in most windows, so a press's in-block
position is set by its duration (1-latent presses land on block-first latents) -- seam position and press duration
are confounded.

--balanced (phase-balanced replay): windows are taken on a fixed time grid that does not depend on where the
presses are, and every accepted window is emitted at `block` latent phase offsets (t0 + phi * latent, phi = 0..block-1).
Shifting t0 by whole latents shifts the latched command sequence exactly, so every press appears once at every
in-block position with the same duration; seam position is then independent of duration by construction. Extra
fields: wid (window id, shared by the copies) and phase (phi).
Usage: python vpt_press_specs.py data/vpt_actions results/raw/e29_specs.json [--fps 16 --n_lat 20 --max 24]
       python vpt_press_specs.py data/vpt_actions results/raw/e29b_specs.json --balanced --fps 16 --n_lat 20
"""
import argparse
import glob
import json
import os
from collections import Counter

import numpy as np


def presses(x):
    e = np.diff(np.r_[0, x, 0])
    return list(zip(np.flatnonzero(e == 1), np.flatnonzero(e == -1)))


def latch(sgn, t, t0, n_cmd, lat_s, amp):
    """Commands y[j-1] for latents j = 1..n_cmd; latent j covers [t0 + (j-1)*lat_s, t0 + j*lat_s)."""
    y = np.zeros(n_cmd)
    for j in range(1, n_cmd + 1):
        m = (t >= t0 + (j - 1) * lat_s) & (t < t0 + j * lat_s)
        s = sgn[m]
        if (s != 0).any():
            y[j - 1] = amp * np.sign(s[s != 0].mean())
    return y


def press_list(y):
    return [(int(on), int(off - on), int(np.sign(y[on]))) for on, off in presses((y != 0).astype(int))]


def valid(pr, n_lat, min_onset=2):
    return 1 <= len(pr) <= 3 and all(p[0] >= min_onset for p in pr) and \
        all(pr[i + 1][0] - (pr[i][0] + pr[i][1]) >= 3 for i in range(len(pr) - 1)) and \
        pr[-1][0] + pr[-1][1] <= n_lat - 4


def spec_of(y):
    return "yawlist:" + "_".join(f"{k}={v:g}" for k, v in enumerate(y) if v)


def load_signs(f):
    L = [json.loads(line) for line in open(f)]
    keys = [set(r.get("keyboard", {}).get("keys") or []) for r in L]
    sgn = np.array([("key.keyboard.d" in k) - ("key.keyboard.a" in k) for k in keys])  # +1 right, -1 left
    return sgn, np.arange(len(L)) / 20.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=16.0)
    ap.add_argument("--n_lat", type=int, default=20)
    ap.add_argument("--amp", type=float, default=3.0)
    ap.add_argument("--max", type=int, default=40, help="max windows (balanced: base windows, each emitted x block)")
    ap.add_argument("--per_file", type=int, default=2)
    ap.add_argument("--balanced", action="store_true")
    ap.add_argument("--block", type=int, default=4, help="latents per generation block (balanced mode)")
    a = ap.parse_args()
    lat_s = 4.0 / a.fps
    out = []
    for f in sorted(glob.glob(os.path.join(a.src, "*.jsonl"))):
        try:
            sgn, t = load_signs(f)
        except Exception:
            continue
        n_file = 0
        if a.balanced:
            n_ext = a.n_lat - 1 + a.block - 1  # commands for the widest shifted copy
            hop = (n_ext + 1) * lat_s  # non-overlapping grid, independent of press positions
            t0 = 0.0
            while t0 + hop < t[-1] and n_file < a.per_file and len({o["wid"] for o in out}) < a.max:
                y_ext = latch(sgn, t, t0, n_ext, lat_s, a.amp)
                pr_ext = press_list(y_ext)
                # identical presses in every copy: onset >= 2 after the largest shift, end fits the unshifted copy
                if pr_ext and valid(pr_ext, a.n_lat, min_onset=2 + a.block - 1):
                    wid = len({o["wid"] for o in out})
                    for phi in range(a.block):
                        y = y_ext[phi:phi + a.n_lat - 1]
                        pr = press_list(y)
                        assert [(p[1], p[2]) for p in pr] == [(p[1], p[2]) for p in pr_ext] and valid(pr, a.n_lat)
                        out.append(dict(src=os.path.basename(f), t0=round(t0 + phi * lat_s, 3), wid=wid, phase=phi,
                                        spec=spec_of(y), presses=pr))
                    n_file += 1
                t0 += hop
            if len({o["wid"] for o in out}) >= a.max:
                break
            continue
        win_s = a.n_lat * lat_s
        t0 = 0.0
        while t0 + win_s < t[-1] and len(out) < a.max and n_file < a.per_file:
            y = latch(sgn, t, t0, a.n_lat - 1, lat_s, a.amp)
            pr = press_list(y)
            if valid(pr, a.n_lat):
                out.append(dict(src=os.path.basename(f), t0=round(t0, 2), spec=spec_of(y), presses=pr))
                t0 += win_s
                n_file += 1
            else:
                t0 += lat_s
        if len(out) >= a.max:
            break
    json.dump(out, open(a.out, "w"), indent=1)
    P = [p for o in out for p in o["presses"]]
    seam = [(p[0] + 1) % a.block == 0 for p in P]
    dur = Counter((s, min(p[1], 4)) for s, p in zip(seam, P))
    print(f"{len(out)} windows from {len(set(o['src'] for o in out))} players; {len(P)} presses; "
          f"1-latent {sum(p[1] == 1 for p in P)}, onset on block-first {sum(seam)}")
    for s in (True, False):
        n = sum(v for (ss, _), v in dur.items() if ss == s)
        mix = {d if d < 4 else ">=4": round(dur[(s, d)] / max(n, 1), 2) for d in (1, 2, 3, 4)}
        print(f"  {'seam ' if s else 'other'} presses {n}: duration mix {mix}")


if __name__ == "__main__":
    main()
