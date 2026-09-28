"""Keyboard tap analysis (mg2_sysid.py ktap outputs): strafe key held for `dur` frames from frame f.

Lateral translation shows up as a global horizontal image shift (with parallax); read-out = per-frame
phase-correlation shift of the tap rollout minus the same-seed reference, sign-aligned with the step
response. Reports displacement integral per (dur, phase of f) normalised by the step response's steady
per-frame shift x dur (1.0 = the tap moved as far as `dur` frames of holding the key).
Usage: python ktap.py <tap_dir> <step_dir> <out_json>
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


def main():
    tap_dir, step_dir, out = sys.argv[1:4]
    steady, sign = {}, {}
    for f in glob.glob(os.path.join(step_dir, "*ktap~*.npz")):
        im = os.path.basename(f)[:4]
        ref = shifts(np.load(os.path.join(step_dir, f"{im}_s0_L12_none.npz"))["frames"])
        r = shifts(np.load(f)["frames"]) - ref
        s = np.mean(r[-12:])
        sign[im], steady[im] = np.sign(s), abs(s)
    rows = defaultdict(list)
    refs = {}
    for f in sorted(glob.glob(os.path.join(tap_dir, "*ktap~*.npz"))):
        b = os.path.basename(f)
        m = re.match(r"(\d+)_s(\d+)_L12_ktap~(\d+)~(\d+)~(\d+)\.npz", b)
        im, key, fr, dur = m.group(1), m.group(3), int(m.group(4)), int(m.group(5))
        if dur == 0 or im not in steady:
            continue
        if im not in refs:
            refs[im] = shifts(np.load(os.path.join(tap_dir, f"{im}_s0_L12_none.npz"))["frames"])
        r = sign[im] * (shifts(np.load(f)["frames"]) - refs[im])
        rows[(dur, (fr - 1) % 4)].append(dict(image=im, f=fr, integral=float(r.sum()),
                                              norm=float(r.sum() / (steady[im] * dur)),
                                              kernel=[round(float(x), 3) for x in r[fr - 1:fr + 8]]))
    res = {f"dur{d}_phase{p}": dict(n=len(v), norm_mean=float(np.mean([x["norm"] for x in v])),
                                    norm_sem=float(np.std([x["norm"] for x in v]) / np.sqrt(len(v))),
                                    kernel_mean=np.mean([x["kernel"] for x in v], 0).round(3).tolist())
           for (d, p), v in sorted(rows.items())}
    res["steady_px_per_frame"] = steady
    json.dump(res, open(out, "w"), indent=1)
    for k, v in res.items():
        if k.startswith("dur"):
            print(f"{k}: {v['norm_mean']:.2f} +- {v['norm_sem']:.2f} (n={v['n']}) kernel {v['kernel_mean']}")
    print("steady", steady)


if __name__ == "__main__":
    main()
