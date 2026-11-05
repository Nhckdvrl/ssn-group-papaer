#!/usr/bin/env python3
"""E174 pipeline check for e174_coarse_null.py: recomputed top-8 from hidden H, W, b vs cached routing S on the pre-registered anchors (aligned by word id)."""
import json, numpy as np, torch
from pathlib import Path
HID=Path.home()/"mechpop_cache/e167_analysis/hidden"; CAP=Path.home()/"mechpop_cache/e167_analysis/routing"
aw=np.load(CAP/"pairs.npz")["anchor_word"]; out={}
for spec in ["I4D0@3200000000","I4D0R@3200000000"]+[f"{r}@3999793152" for r in ["I0D0","I1D0","I2D0","I3D0","I0D1","I1D1"]]+["I0D0@0","I1D0@0"]:
    r,t=spec.split("@"); z=np.load(HID/f"{r}__ckpt_{t}.npz"); R=np.load(CAP/f"{r}__ckpt_{t}.npz")
    pos={int(x):i for i,x in enumerate(z["word_idx"])}; rows=np.array([pos[int(x)] for x in aw])
    out[spec]={}
    for l in (6,11):
        S=(torch.from_numpy(z[f"H{l}"][rows].astype(np.float32))@torch.from_numpy(z[f"W{l}"]).T+torch.from_numpy(z[f"b{l}"])).topk(8,-1).indices.numpy()
        out[spec][l]=float(np.mean([len(set(x)&set(y))/8 for x,y in zip(S,R[f"S{l}"])]))
    print(spec,out[spec],flush=True)
Path("results/e174/coarse_alignment_check.json").write_text(json.dumps(out,indent=1))
