"""Causal localisation of the student's impulse rebound: hide an action frame from chosen latents only.

In MG2's ActionModule latent L reads the per-frame mouse actions of frames 4L-12 .. 4L-1 (window positions
0..11). A 1-frame yaw impulse at frame F therefore sits in the windows of three latents. We zero it in the
window of a chosen subset of latents (all other inputs, the noise and the rest of the rollout unchanged)
and read out the per-frame yaw response against the same-seed no-action reference.

Mask spec: comma-separated latent offsets relative to L1 = F//4 + 1 (the latent that should render F+1):
  "" = no masking, "1" = hide from L1+1, "1,2" = hide from L1+1 and L1+2, "0" = hide from L1 only ...
Usage: python mg2_mask.py --out DIR --images 0001 --seeds 0 --frames 13-16 --masks ",0,1,2,1+2"
"""
import argparse
import os

import numpy as np
import torch

import mg2_probe as P
from mg2_sysid import build
from wan.modules import action_module as am

CTX = {"start": 0, "hide": set()}  # hide: set of (abs_latent, abs_frame)
_orig_fwd = am.ActionModule.forward
_real_torch = am.torch


class _TorchProxy:
    """Delegates to torch; intercepts torch.stack for the mouse window groups to apply the mask."""

    def __getattr__(self, name):
        return getattr(_real_torch, name)

    def stack(self, tensors, dim=0, *a, **k):
        out = _real_torch.stack(tensors, dim, *a, **k)
        if CTX["hide"] and dim == 1 and out.ndim == 4 and out.shape[-1] == 2:  # (B, nf, pad_t=12, C=2)
            out = out.clone()
            for i in range(out.shape[1]):
                L = CTX["start"] + i
                for p in range(out.shape[2]):
                    if (L, 4 * L - 12 + p) in CTX["hide"]:
                        out[:, i, p] = 0
        return out


am.torch = _TorchProxy()


def _fwd(self, x, tt, th, tw, *args, **kw):
    CTX["start"] = int(kw.get("start_frame", 0))
    return _orig_fwd(self, x, tt, th, tw, *args, **kw)


am.ActionModule.forward = _fwd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--images", default="0001")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--frames", default="13-16")
    ap.add_argument("--masks", default=",0,1,2,1+2")
    ap.add_argument("--amp", type=float, default=0.1)
    ap.add_argument("--latents", type=int, default=12)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = P.Runner(P.snapshot("Skywork/Matrix-Game-2.0"))
    n = (a.latents - 1) * 4 + 1
    for im in a.images.split(","):
        path = os.path.join(P.MG2, "demo_images", "universal", f"{im}.png")
        for seed in P.parse_range(a.seeds):
            ref_f = os.path.join(a.out, f"{im}_s{seed}_L{a.latents}_none.npz")
            if not os.path.exists(ref_f):
                CTX["hide"] = set()
                kb, ms = build("series:0", n)
                np.savez_compressed(ref_f, frames=R.rollout(path, seed, kb, ms, a.latents)[:, ::2, ::2].byte().cpu().numpy())
            for F in P.parse_range(a.frames):
                kb, ms = build(f"impulse:{a.amp}:{F}", n)
                L1 = F // 4 + 1
                for m in a.masks.split(","):
                    offs = [int(x) for x in m.split("+")] if m else []
                    CTX["hide"] = {(L1 + o, F) for o in offs}
                    tag = f"{im}_s{seed}_L{a.latents}_impulse~{a.amp}~{F}~mask{m or 'none'}"
                    f = os.path.join(a.out, tag + ".npz")
                    if os.path.exists(f):
                        continue
                    v = R.rollout(path, seed, kb, ms, a.latents)
                    np.savez_compressed(f, frames=v[:, ::2, ::2].byte().cpu().numpy())
                    print(tag, flush=True)
    CTX["hide"] = set()


if __name__ == "__main__":
    main()
