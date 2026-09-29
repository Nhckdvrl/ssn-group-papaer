"""Teacher-forced pose-impulse probe for minWM causal / bidirectional Wan Action2V models (no rollout).

For a real clip (clean latents + poses from an LMDB), every block is noised to the same sigma and the model
predicts x0 for all latents in one forward pass (causal model: each block sees the clean previous blocks, as in
teacher-forcing training; bidirectional model: all latents jointly). The counterfactual adds a yaw of `amp`
degrees to the camera from latent j on (c2w <- c2w @ R_y(amp)), exactly like a one-step impulse in the rollout
probes. Response at latent j' = horizontal shift (latent pixels, phase correlation of the channel-mean map)
between counterfactual and factual x0 predictions. A model that uses the pose change renders the new view from
latent j on; a model that ignores it predicts the same content.
Usage: python mwm_tf_probe.py --stage stage1_ar_tf [--ckpt export.pt] --lmdb data/e23_ctrl --rows 0-7
       --sigmas 0.9,0.6 --out results/raw/e26_tfprobe/tfbase.npz
"""
import argparse
import os
import sys

import cv2
import numpy as np
import torch

WB = os.environ["WB"]
sys.path.insert(0, os.path.join(WB, "scripts"))
import mwm_sysid as S  # noqa: E402,F401  (chdir to minWM, trajectory parser)
from minwm.config import apply_overrides, load  # noqa: E402
from minwm.data.datasets.lmdb import CameraLatentLMDBDataset  # noqa: E402
from minwm.engine import BaseInferencer  # noqa: E402
from minwm.sampling.schedulers import FlowMatchingScheduler  # noqa: E402


def parse_range(s):
    out = []
    for p in s.split(","):
        a, _, b = p.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def rot_y(deg):
    c, s = np.cos(np.deg2rad(deg)), np.sin(np.deg2rad(deg))
    R = np.eye(4, dtype=np.float32)
    R[0, 0], R[0, 2], R[2, 0], R[2, 2] = c, s, -s, c
    return torch.tensor(R)


def hshift(a, b):
    """Horizontal shift of b relative to a (latent pixels) via phase correlation of channel-mean maps."""
    a = a.float().mean(0).cpu().numpy().astype(np.float64)
    b = b.float().mean(0).cpu().numpy().astype(np.float64)
    win = cv2.createHanningWindow(a.shape[::-1], cv2.CV_64F)
    (dx, _), _ = cv2.phaseCorrelate(a, b, win)
    return dx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="stage1_ar_tf")
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--lmdb", required=True)
    ap.add_argument("--rows", default="0-7")
    ap.add_argument("--sigmas", default="0.9,0.6")
    ap.add_argument("--amp", type=float, default=3.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ov = [f"inference.checkpoint={a.ckpt}", "inference.prefer_ema=False"] if a.ckpt else []
    cfg = apply_overrides(load(f"configs/wan21/action2v/infer/{a.stage}.py"), ov)
    inf = BaseInferencer(cfg)
    model, adapter, dev = inf.loop.generator, inf.loop.adapter, inf.device
    model.eval()
    sched = FlowMatchingScheduler(num_train_timesteps=1000, shift=5.0, sigma_min=0.0, extra_one_step=True)
    ds = CameraLatentLMDBDataset(os.path.join(WB, a.lmdb) if not a.lmdb.startswith("/") else a.lmdb)
    sigmas = [float(s) for s in a.sigmas.split(",")]
    res = {}  # (sigma) -> array [rows, j, j'] of shifts
    for si, sig in enumerate(sigmas):
        t_val = float(sched.timesteps[(sched.sigmas - sig).abs().argmin()])
        sig_eff = float(sched.sigma_for(torch.tensor([t_val]))[0])
        R, DD = [], []
        for row in parse_range(a.rows):
            item = ds[row]
            x0 = item["clean_latent"][None].to(dev)  # [1,F,C,H,W]
            F = x0.shape[1]
            g = torch.Generator(device="cpu").manual_seed(1000 + row)
            eps = torch.randn(x0.shape, generator=g).to(dev)
            noisy = (1 - sig_eff) * x0 + sig_eff * eps
            ts = torch.full((1, F), t_val, device=dev)
            batch = {"prompts": [item["prompts"]]}
            with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
                cond = adapter.conditioning(batch, 1, dev)

                def x0_hat(vm):
                    v = adapter.denoise(model, noisy=noisy, timestep=ts, clean=x0 if adapter.causal else None,
                                        viewmats=vm[None].to(dev), Ks=item["Ks"][None].to(dev), **cond)
                    return (noisy - sig_eff * v.float())[0]

                base = x0_hat(item["viewmats"])
                M = np.full((F, F), np.nan)
                D = np.full((F, F), np.nan)
                for j in range(1, F):
                    vm = item["viewmats"].clone()
                    vm[j:] = rot_y(-a.amp) @ vm[j:]  # w2c' = R_y(-amp) w2c  <=>  c2w' = c2w R_y(amp)
                    cf = x0_hat(vm)
                    for jj in range(1, F):
                        M[j, jj] = hshift(base[jj], cf[jj])
                        D[j, jj] = float((cf[jj] - base[jj]).abs().mean() / base[jj].abs().mean())
            R.append(M)
            DD.append(D)
            print(f"sigma={sig_eff:.3f} row={row} shift(j'=j):", np.round(np.diag(M)[1:], 2),
                  " reldiff(j'=j):", np.round(np.diag(D)[1:], 3), " reldiff(j'=j-1):", np.round(np.diag(D, -1)[1:], 3), flush=True)
        res[f"s{si}"] = np.stack(R)
        res[f"d{si}"] = np.stack(DD)
        res[f"sigma{si}"] = sig_eff
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    np.savez(a.out, **res)


if __name__ == "__main__":
    main()
