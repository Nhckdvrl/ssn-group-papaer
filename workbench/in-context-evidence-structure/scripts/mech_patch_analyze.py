"""E38 analysis. usage: mech_patch_analyze.py MODEL
noise effect per base: maj and min (noisy - clean); components bias=(maj-min)/2, cond=(maj+min)/2.
For each patch set and layer: remaining effect (patched - clean) in the same components; recovery = 1 - remaining/effect."""
import sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    m = sys.argv[1]; z = np.load(ROOT / f"results/mech/{sys.argv[2] if len(sys.argv) > 2 else 'patch'}_{m}.npz"); layers = z["layers"]
    D = pd.DataFrame(dict(uid=z["uid"])); D["task"] = D.uid.str.split(":").str[0]; D["role"] = D.uid.str.split("|").str[1]
    D["base"] = D.uid.str.split("|").str[2]
    for task in ("mag_nat", "sst"):
        I = {r: D[(D.task == task) & (D.role == r)].set_index("base").index for r in ("maj", "min")}
        common = I["maj"].intersection(I["min"])
        g = lambda key, r: np.array([z[key][D[(D.task == task) & (D.role == r) & (D.base == b)].index[0]] for b in common])
        eff = {r: g("noisy", r) - g("clean", r) for r in ("maj", "min")}
        comp = lambda x: {"bias": (x["maj"] - x["min"]) / 2, "cond": (x["maj"] + x["min"]) / 2}
        E = comp(eff)
        print(f"\n===== {m} / {task}  n={len(common)}   noise effect: bias {E['bias'].mean():+.2f}  cond {E['cond'].mean():+.2f}  (maj {eff['maj'].mean():+.2f}, min {eff['min'].mean():+.2f})")
        for ps in [k for k in ("all", "anchors", "inputs", "noise_anchors", "pred", "after") if k in z.files]:
            rem = {r: g(ps, r) - g("clean", r)[:, None] for r in ("maj", "min")}
            R = comp(rem)
            line = []
            for c in ("bias", "cond"):
                rec = 1 - R[c].mean(0) / E[c].mean()
                line.append(f"{c} recovery " + " ".join(f"{v:+.2f}" for v in rec[::2]))
            print(f"  {ps:13s} " + " | ".join(line))
        print(f"  (layers shown: {layers[::2].tolist()})")


if __name__ == "__main__":
    main()
