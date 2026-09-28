"""Impulse response of minWM rollouts resolved by the in-block position of the pose change.

Files <tag>_p<id>_s<seed>_<spec>.npz (mwm_sysid.py / mwm_shift.py) with spec impulse:A:k. A one-step yaw at step k
changes the pose from latent k+1 on. Block grid: latents [0-3],[4-7],... for normal rollouts; for mwm_shift tag
'sh1' the generated latents form blocks [1-4],[5-8],... (latent 0 is a clean prefix), so position = k mod 4.
Response = realised yaw integral (px, phase correlation, latents >= 1) per commanded degree.
Usage: python phase_survival.py <raw_dir> [<out_json>]
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


def main():
    raw = sys.argv[1]
    refs, resp = {}, defaultdict(lambda: defaultdict(list))
    for f in sorted(glob.glob(os.path.join(raw, "*.npz"))):
        m = re.match(r"(\w+?)_p(\d+)_s(\d+)_(.*)\.npz", os.path.basename(f))
        tag, spec = m.group(1), m.group(4).replace("~", ":")
        if not spec.startswith("impulse:"):
            continue
        key = f"{tag}_p{m.group(2)}_s{m.group(3)}"
        z = np.load(f)
        n_lat = len(z["yaw_cmd"]) + 1
        if key not in refs:
            refs[key] = shifts(np.load(os.path.join(raw, key + "_none.npz"))["frames"])
        r = -(shifts(z["frames"]) - refs[key])
        A, k = float(spec.split(":")[1]), int(spec.split(":")[2])
        resp[tag][k].append(float(per_latent(r, n_lat)[1:].sum() / A))
    out = {}
    for tag, d in sorted(resp.items()):
        off = 1 if tag == "sh1" else 0
        rows = {k: dict(pos=(k + 1 - off) % 4, mean=round(float(np.mean(v)), 3), n=len(v),
                        each=[round(x, 2) for x in v]) for k, v in sorted(d.items())}
        bypos = defaultdict(list)
        for k, v in d.items():
            bypos[(k + 1 - off) % 4] += v
        out[tag] = dict(per_k=rows, per_pos={p: [round(float(np.mean(v)), 3), len(v)] for p, v in sorted(bypos.items())})
        print(f"== {tag}  (px per commanded degree; pos 0 = pose change on the block's first latent)")
        print("   " + "  ".join(f"k{k}[p{r['pos']}]={r['mean']:.2f}" for k, r in rows.items()))
        print("   by position:", out[tag]["per_pos"])
    if len(sys.argv) > 2:
        json.dump(out, open(sys.argv[2], "w"), indent=1)


if __name__ == "__main__":
    main()
