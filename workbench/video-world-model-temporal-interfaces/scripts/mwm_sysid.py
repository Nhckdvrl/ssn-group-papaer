"""minWM (Wan2.1-1.3B Action2V) control-bandwidth probe across the distillation ladder.

minWM conditions on one camera pose per latent frame (PRoPE). A yaw sequence y_k (degrees per latent
step, k = 1..T-1) is turned into w2c poses exactly like the repo's trajectory parser (patched to accept
"yaw:v1_v2_..."). Every sequence is run with the same prompt and seed as a zero-motion reference
(paired counterfactual). Stages use the official infer configs in configs/wan21/action2v/infer/.

Sequence specs (latent units): none | step:A:k0 | impulse:A:k | sine:A:P  (A in degrees per latent step)
Usage: python mwm_sysid.py --stage stage3_ar_dmd --out DIR --prompts 1,2 --seqs sine:3:2,sine:3:4 --seed 0
"""
import argparse
import math
import os
import sys

import numpy as np
import torch

WB = os.environ["WB"]
MWM = os.path.join(WB, "vendor", "minWM")
sys.path.insert(0, MWM)
os.chdir(MWM)

import minwm.processors.camera as cam  # noqa: E402
from minwm.config import apply_overrides, load  # noqa: E402
from minwm.engine import BaseInferencer  # noqa: E402
from minwm.engine.inferencer import read_benchmark  # noqa: E402
from minwm.utils.seed import set_seed  # noqa: E402

_orig_parse = cam.parse_trajectory


def _parse(traj):
    if traj.startswith("yaw:"):
        motions = [{"yaw": math.radians(float(v))} for v in traj[4:].split("_")]
        c2w = cam._generate_c2w_trajectory(motions)
        return np.stack([np.linalg.inv(c).astype(np.float32) for c in c2w])
    return _orig_parse(traj)


cam.parse_trajectory = _parse

T_LAT = 20  # latents per clip in the official configs


def yaw_seq(spec, n=T_LAT - 1):
    p = spec.split(":")
    y = np.zeros(n)
    if p[0] == "step":
        y[int(p[2]):] = float(p[1])
    elif p[0] == "impulse":
        y[int(p[2])] = float(p[1])
    elif p[0] == "sine":
        A, P = float(p[1]), float(p[2])
        k0 = 3
        for k in range(k0, n):
            y[k] = A * math.sin(2 * math.pi * (k - k0) / P + (math.pi / 2 if P == 2 else 0.0))
    elif p[0] == "yawlist":  # yawlist:k=v_k=v  (explicit per-step yaw in degrees)
        for kv in p[1].split("_"):
            k, v = kv.split("=")
            y[int(k)] = float(v)
    elif p[0] != "none":
        raise ValueError(spec)
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompts", default="1")
    ap.add_argument("--seqs", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--ckpt", default=None, help="override inference.checkpoint (exported .pt with a 'model' entry)")
    ap.add_argument("--tag", default=None, help="name used in output files instead of the stage name")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ov = [f"inference.checkpoint={a.ckpt}", "inference.prefer_ema=False"] if a.ckpt else []
    cfg = apply_overrides(load(f"configs/wan21/action2v/infer/{a.stage}.py"), ov)
    name = a.tag or a.stage
    inf = BaseInferencer(cfg)
    bench = {str(s["id"]): s for s in read_benchmark("assets/example_t2v.json")}
    for pid in a.prompts.split(","):
        caption = bench[pid].get("caption") or bench[pid].get("prompt")
        for spec in ["none"] + a.seqs.split(","):
            f = os.path.join(a.out, f"{name}_p{pid}_s{a.seed}_{spec.replace(':', '~')}.npz")
            if os.path.exists(f):
                continue
            y = yaw_seq(spec)
            traj = "yaw:" + "_".join(f"{v:.5f}" for v in y)
            set_seed(a.seed)
            with torch.inference_mode():
                batch = inf.build_batch({"prompt": caption, "trajectory": traj})
                res = inf.loop.generate(batch)
            v = (res["video"][0] * 255.0).clamp(0, 255).permute(0, 2, 3, 1).to(torch.uint8)  # F,H,W,C
            np.savez_compressed(f, frames=v[:, ::2, ::2].cpu().numpy(), yaw_cmd=y, spec=spec)
            print(name, pid, spec, tuple(v.shape), flush=True)


if __name__ == "__main__":
    main()
