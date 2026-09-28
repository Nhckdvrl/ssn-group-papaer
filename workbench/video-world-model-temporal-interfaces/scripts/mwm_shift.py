"""Dissociate block position from absolute time in minWM causal students.

Unshifted: 20 latents, blocks [0-3],[4-7],... . Shifted: 21 latents with latent 0 supplied as a clean prefix
(initial_latent) taken from the unshifted no-action rollout of the same prompt/seed, so the 20 generated
latents form blocks [1-4],[5-8],... . A one-step yaw at step k changes the pose from latent k+1 on.
If event loss is set by block position, the dropped k moves from {3,7,11} (unshifted) to {4,8,12} (shifted).
Usage: python mwm_shift.py --stage stage3_ar_dmd --out DIR --prompts 1,2 --ks 3-12 --amp 3
"""
import argparse
import math
import os
import sys

import numpy as np
import torch

WB = os.environ["WB"]
sys.path.insert(0, os.path.join(WB, "scripts"))
import mwm_sysid as S  # noqa: E402  (installs the yaw-list trajectory parser, chdir to minWM)
from minwm.config import apply_overrides, load  # noqa: E402
from minwm.engine import BaseInferencer  # noqa: E402
from minwm.engine.inferencer import read_benchmark  # noqa: E402
from minwm.utils.seed import set_seed  # noqa: E402


def parse_range(s):
    out = []
    for p in s.split(","):
        if "-" in p:
            a, b = p.split("-"); out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(p))
    return out


def run(inf, caption, yaw, noise, seed, initial_latent=None):
    traj = "yaw:" + "_".join(f"{v:.5f}" for v in yaw)
    set_seed(seed)
    with torch.inference_mode():
        batch = inf.build_batch({"prompt": caption, "trajectory": traj})
        batch["noise"] = noise
        if initial_latent is not None:
            batch["initial_latent"] = initial_latent
        res = inf.loop.generate(batch)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="stage3_ar_dmd")
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompts", default="1")
    ap.add_argument("--ks", default="3-12")
    ap.add_argument("--amp", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfg = apply_overrides(load(f"configs/wan21/action2v/infer/{a.stage}.py"), [])
    inf = BaseInferencer(cfg)
    bench = {str(s["id"]): s for s in read_benchmark("assets/example_t2v.json")}
    C, H, W = cfg["inference"]["latent_shape"]
    for pid in a.prompts.split(","):
        caption = bench[pid]["prompt"]
        g = torch.Generator(device=inf.device).manual_seed(1000 + a.seed)
        noise21 = torch.randn(1, 21, C, H, W, generator=g, device=inf.device, dtype=inf.dtype)
        # unshifted reference (20 latents) -> its latent 0 becomes the clean prefix for all shifted runs
        ref20 = run(inf, caption, np.zeros(19), noise21[:, :20], a.seed)
        prefix = ref20["latents"][:, :1].to(inf.dtype)
        for shift, n_lat in [(0, 20), (1, 21)]:
            for spec in ["none"] + [f"impulse:{a.amp:g}:{k}" for k in parse_range(a.ks)]:
                f = os.path.join(a.out, f"sh{shift}_p{pid}_s{a.seed}_{spec.replace(':', '~')}.npz")
                if os.path.exists(f):
                    continue
                y = np.zeros(n_lat - 1)
                if spec != "none":
                    y[int(spec.split(":")[2])] = a.amp
                res = run(inf, caption, y, noise21[:, :n_lat], a.seed, prefix if shift else None)
                v = (res["video"][0] * 255.0).clamp(0, 255).permute(0, 2, 3, 1).to(torch.uint8)
                np.savez_compressed(f, frames=v[:, ::2, ::2].cpu().numpy(), yaw_cmd=y, spec=spec, shift=shift)
                print(pid, shift, spec, tuple(v.shape), flush=True)


if __name__ == "__main__":
    main()
