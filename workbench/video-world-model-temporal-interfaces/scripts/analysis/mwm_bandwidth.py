"""Latent-rate control bandwidth for minWM stages (outputs of mwm_sysid.py).

Per-frame horizontal shift (phase correlation) of action rollout minus same-seed reference, summed over
the frames of each latent step (frame 0 = latent 0; latent k>=1 covers frames 4k-3..4k) -> realised yaw
per latent step r_k. Commanded yaw per step y_k (degrees). Reports per stage and period P (latents):
gain = LS amplitude of r_k at the input frequency / A, normalised by the stage's step-response gain,
plus impulse integrals.
Usage: python mwm_bandwidth.py <raw_dir> <out_json>
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from sysid import shifts  # noqa: E402


def per_latent(r, n_lat):
    out = [r[0]]
    for k in range(1, n_lat):
        out.append(r[4 * k - 3:4 * k + 1].sum())
    return np.array(out)


def main():
    raw, out = sys.argv[1], sys.argv[2]
    refs, rows = {}, defaultdict(list)
    for f in sorted(glob.glob(os.path.join(raw, "*.npz"))):
        m = re.match(r"(\w+?)_p(\d+)_s(\d+)_(.*)\.npz", os.path.basename(f))
        stage, pid, sd, spec = m.group(1), m.group(2), m.group(3), m.group(4).replace("~", ":")
        if spec == "none":
            continue
        key = f"{stage}_p{pid}_s{sd}"
        if key not in refs:
            refs[key] = shifts(np.load(os.path.join(raw, key + "_none.npz"))["frames"])
        z = np.load(f)
        r = -(shifts(z["frames"]) - refs[key])
        n_lat = (len(r) - 1) // 4 + 1
        rl = per_latent(r, n_lat)[1:]  # response of latent k=1..n-1 <-> command y_{k-1} (pose k)
        y = z["yaw_cmd"][: len(rl)]
        rows[(stage, spec.split(":")[0], spec)].append(dict(pid=pid, r=rl.tolist(), y=y.tolist()))
    res = {}
    for stage in sorted({k[0] for k in rows}):
        st = {}
        steps = rows.get((stage, "step", next((k[2] for k in rows if k[0] == stage and k[1] == "step"), "")), [])
        g0 = np.nan
        if steps:
            R = np.array([x["r"] for x in steps]); Y = np.array([x["y"] for x in steps])
            sel = Y[0] != 0
            g0 = float(np.mean(R[:, sel][:, 2:]) / np.mean(Y[:, sel][:, 2:]))  # steady px per degree
            st["step_px_per_deg"] = g0
        for (s2, kind, spec), v in sorted(rows.items()):
            if s2 != stage or kind == "step":
                continue
            p = spec.split(":")
            if kind == "sine":
                A, P = float(p[1]), float(p[2])
                gains = []
                for x in v:
                    y, r = np.array(x["y"]), np.array(x["r"])
                    k = np.arange(len(y)); sel = k >= 5
                    w = 2 * np.pi / P
                    X = np.stack([np.sin(w * k[sel]), np.cos(w * k[sel])], 1)
                    cy, *_ = np.linalg.lstsq(X, y[sel], rcond=None)
                    cr, *_ = np.linalg.lstsq(X, r[sel], rcond=None)
                    gains.append(np.hypot(*cr) / max(np.hypot(*cy), 1e-9))
                st[spec] = dict(n=len(v), gain_px_per_deg=float(np.mean(gains)),
                                gain_norm=float(np.mean(gains) / g0) if g0 == g0 else None)
            elif kind == "impulse":
                I = [np.sum(x["r"]) for x in v]
                st[spec] = dict(n=len(v), integral_px=float(np.mean(I)),
                                integral_norm=float(np.mean(I) / (g0 * float(p[1]))) if g0 == g0 else None,
                                kernel=np.mean([x["r"] for x in v], 0).round(3).tolist())
        res[stage] = st
    json.dump(res, open(out, "w"), indent=1)
    for stage, st in res.items():
        print("==", stage, "step px/deg %.3f" % st.get("step_px_per_deg", float("nan")))
        for k, v in st.items():
            if k != "step_px_per_deg":
                print("  ", k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "kernel"})


if __name__ == "__main__":
    main()
