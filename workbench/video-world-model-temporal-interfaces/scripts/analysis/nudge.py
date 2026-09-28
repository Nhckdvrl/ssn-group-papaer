"""Evaluate minWM students on the sparse camera-nudge task and on single-step impulses.

For every model tag in <raw_dir> (files <tag>_p<id>_s<seed>_<spec>.npz from mwm_sysid.py):
- gain g (px per degree per latent step) = mean realised/commanded yaw over the 3-degree in-block impulses
  at steps 5, 6, 8, 9, 10 (so each model is scored in its own units);
- impulse survival = realised total yaw / (g * commanded) per step position and amplitude;
- nudge task: final heading error |sum(realised)/g - sum(commanded)| in degrees, and per-nudge registration
  computed from the per-latent response summed over the 6 latents after the nudge (isolated nudges only).
Usage: python nudge.py <raw_dir> <out_json>
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


def load(raw):
    refs, out = {}, defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(raw, "*.npz"))):
        m = re.match(r"(\w+?)_p(\d+)_s(\d+)_(.*)\.npz", os.path.basename(f))
        tag, pid, spec = m.group(1), m.group(2), m.group(4).replace("~", ":")
        if spec == "none":
            continue
        key = f"{tag}_p{pid}_s{m.group(3)}"
        if key not in refs:
            refs[key] = shifts(np.load(os.path.join(raw, key + "_none.npz"))["frames"])
        z = np.load(f)
        r = -(shifts(z["frames"]) - refs[key])
        out[tag][(pid, spec)] = (per_latent(r, 20)[1:], z["yaw_cmd"][:19])
    return out


def main():
    raw, dst = sys.argv[1], sys.argv[2]
    data = load(raw)
    res = {}
    for tag, d in data.items():
        gains = [rl.sum() / y.sum() for (pid, spec), (rl, y) in d.items()
                 if spec.startswith("impulse:3:") and int(spec.split(":")[2]) in (5, 6, 8, 9, 10)]
        g = float(np.mean(gains)) if gains else np.nan
        surv = defaultdict(list)
        for (pid, spec), (rl, y) in d.items():
            if spec.startswith("impulse:"):
                A, k = float(spec.split(":")[1]), int(spec.split(":")[2])
                surv[f"A{A:g}_k{k}"].append(float(rl.sum() / (g * A)))
        errs, reg_b, reg_nb = [], [], []
        for (pid, spec), (rl, y) in d.items():
            if not spec.startswith("yawlist:"):
                continue
            errs.append(abs(rl.sum() / g - y.sum()))
            ks = sorted(int(kv.split("=")[0]) for kv in spec[8:].split("_"))
            for i, k in enumerate(ks):
                nxt = ks[i + 1] if i + 1 < len(ks) else 99
                prv = ks[i - 1] if i > 0 else -99
                if nxt - k < 6 or k - prv < 6 or k + 6 > 19:
                    continue  # isolated nudges only
                resp = rl[max(0, k - 4):k + 6].sum() / (g * y[k])
                (reg_b if (k + 1) % 4 == 0 else reg_nb).append(float(resp))
        cont = {}
        for (pid, spec), (rl, y) in d.items():
            if spec == "step:3:3":
                cont.setdefault("step3", []).append(float(rl[8:].mean() / (g * 3.0)))
            elif spec.startswith("sine:3:"):
                P = float(spec.split(":")[2])
                k = np.arange(len(y))
                sel = k >= 5
                w = 2 * np.pi / P
                X = np.stack([np.sin(w * k[sel]), np.cos(w * k[sel])], 1)
                cy, *_ = np.linalg.lstsq(X, y[sel], rcond=None)
                cr, *_ = np.linalg.lstsq(X, rl[sel], rcond=None)
                cont.setdefault(f"sine{P:g}", []).append(float(np.hypot(*cr) / max(np.hypot(*cy), 1e-9) / g))
        res_cont = {k: [round(float(np.mean(v)), 3), len(v)] for k, v in cont.items()}
        res[tag] = dict(gain_px_per_deg=g, continuous=res_cont,
                        impulse_survival={k: [round(float(np.mean(v)), 3), len(v)] for k, v in sorted(surv.items())},
                        nudge_final_heading_err_deg=[round(float(np.mean(errs)), 3), len(errs)] if errs else None,
                        nudge_registration_block_first=[round(float(np.mean(reg_b)), 3), len(reg_b)] if reg_b else None,
                        nudge_registration_other=[round(float(np.mean(reg_nb)), 3), len(reg_nb)] if reg_nb else None)
    json.dump(res, open(dst, "w"), indent=1)
    for tag, r in res.items():
        print("==", tag, "gain %.3f px/deg" % r["gain_px_per_deg"])
        print("  impulse survival:", r["impulse_survival"])
        print("  continuous (rel. to own in-block gain):", r["continuous"])
        print("  nudge heading err (deg):", r["nudge_final_heading_err_deg"], " registration block-first:",
              r["nudge_registration_block_first"], " other:", r["nudge_registration_other"])


if __name__ == "__main__":
    main()
