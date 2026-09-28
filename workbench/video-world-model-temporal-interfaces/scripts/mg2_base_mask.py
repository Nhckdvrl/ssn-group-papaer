"""Window-masking localisation on the bidirectional teacher (same protocol as mg2_mask.py).

Does the teacher avoid the rebound because the latent after the impulse reads the impulse from its action
*history* (window positions 0..7)? Hide the impulse from chosen latents' windows and compare.
Usage: python mg2_base_mask.py --out DIR --images 0001 --frames 13-16 --masks ",0,1,2,1+2,0+1+2"
"""
import argparse
import os

import numpy as np

import mg2_mask as M  # installs the window-mask proxy on the action module
import mg2_base as B  # installs the bidirectional num_frame_per_block patch (wraps M's forward)
from mg2_sysid import build


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--images", default="0001")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--frames", default="13-16")
    ap.add_argument("--masks", default=",0,1,2,1+2,0+1+2")
    ap.add_argument("--amp", type=float, default=0.1)
    ap.add_argument("--steps", type=int, default=30)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ckpt = B.snapshot("Skywork/Matrix-Game-2.0")
    R = B.Runner(ckpt)
    R.pipe.generator.to("cpu")
    model = B.load_base(ckpt, R.dev, R.dtype)
    L = 15
    n = (L - 1) * 4 + 1
    for im in a.images.split(","):
        path = os.path.join(B.MG2, "demo_images", "universal", f"{im}.png")
        for seed in B.parse_range(a.seeds):
            ref_f = os.path.join(a.out, f"{im}_s{seed}_L{L}_K{a.steps}_none.npz")
            if not os.path.exists(ref_f):
                M.CTX["hide"] = set()
                kb, ms = build("series:0", n)
                np.savez_compressed(ref_f, frames=B.sample(R, model, path, seed, kb, ms, L, a.steps)[:, ::2, ::2].byte().cpu().numpy())
            for F in B.parse_range(a.frames):
                kb, ms = build(f"impulse:{a.amp}:{F}", n)
                L1 = F // 4 + 1
                for m in a.masks.split(","):
                    offs = [int(x) for x in m.split("+")] if m else []
                    M.CTX["hide"] = {(L1 + o, F) for o in offs}
                    tag = f"{im}_s{seed}_L{L}_K{a.steps}_impulse~{a.amp}~{F}~mask{m or 'none'}"
                    f = os.path.join(a.out, tag + ".npz")
                    if os.path.exists(f):
                        continue
                    v = B.sample(R, model, path, seed, kb, ms, L, a.steps)
                    np.savez_compressed(f, frames=v[:, ::2, ::2].byte().cpu().numpy())
                    print(tag, flush=True)
    M.CTX["hide"] = set()


if __name__ == "__main__":
    main()
