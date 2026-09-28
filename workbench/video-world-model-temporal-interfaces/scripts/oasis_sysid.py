"""Open-Oasis 500M (per-frame ViT-VAE latents, no temporal compression; generation unit = 1 frame) under
the same paired system-identification protocol. Official sampling loop from vendor/open-oasis/generate.py
(etched-ai/open-oasis@f59deef), weights from the MIT-licensed mirror camenduru/oasis-500m.

Sequence specs on the camera-yaw channel (ACTION_KEYS index --yaw_idx, value in [-1, 1]):
  none | impulse:A:f | sine:A:P | step:A:f
Usage: python oasis_sysid.py --out DIR --seqs impulse:0.3:9-20,sine:0.3:4 --frames 40 --seed 0
"""
import argparse
import math
import os
import sys

import numpy as np
import torch
from einops import rearrange
from torch import autocast

WB = os.environ["WB"]
OA = os.path.join(WB, "vendor", "open-oasis")
sys.path.insert(0, OA)
from dit import DiT_models  # noqa: E402
from utils import load_prompt, sigmoid_beta_schedule  # noqa: E402
from vae import VAE_models  # noqa: E402



def parse_range(s):  # (inlined: importing mg2_probe would shadow Oasis' own `utils` module)
    out = []
    for p in str(s).split(","):
        if "-" in p:
            a, b = p.split("-"); out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(p))
    return out

DEV = "cuda:0"


def expand(seqs):
    out = []
    for s in seqs.split(","):
        p = s.split(":")
        if p[0] in ("impulse", "step") and "-" in p[2]:
            out += [f"{p[0]}:{p[1]}:{f}" for f in parse_range(p[2])]
        else:
            out.append(s)
    return out


def yaw(spec, n, t0=9):
    y = np.zeros(n)
    p = spec.split(":")
    if p[0] == "impulse":
        y[int(p[2])] = float(p[1])
    elif p[0] == "step":
        y[int(p[2]):] = float(p[1])
    elif p[0] == "sine":
        A, P = float(p[1]), float(p[2])
        for t in range(t0, n):
            y[t] = A * math.sin(2 * math.pi * (t - t0) / P + (math.pi / 2 if P == 2 else 0.0))
    return y


@torch.no_grad()
def rollout(model, vae, x0, actions, seed, total, ddim_steps=32):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    x = x0.clone()
    B = 1
    max_noise_level = 1000
    noise_range = torch.linspace(-1, max_noise_level - 1, ddim_steps + 1)
    betas = sigmoid_beta_schedule(max_noise_level).float().to(DEV)
    ac = rearrange(torch.cumprod(1.0 - betas, dim=0), "T -> T 1 1 1")
    for i in range(x.shape[1], total):
        chunk = torch.clamp(torch.randn((B, 1, *x.shape[-3:]), device=DEV), -20, 20)
        x = torch.cat([x, chunk], dim=1)
        start = max(0, i + 1 - model.max_frames)
        for ni in reversed(range(1, ddim_steps + 1)):
            t_ctx = torch.full((B, i), 14, dtype=torch.long, device=DEV)
            t = torch.cat([t_ctx, torch.full((B, 1), noise_range[ni], dtype=torch.long, device=DEV)], 1)
            tn = torch.full((B, 1), noise_range[ni - 1], dtype=torch.long, device=DEV)
            tn = torch.cat([t_ctx, torch.where(tn < 0, t[:, -1:], tn)], 1)
            xc, t, tn = x[:, start:].clone(), t[:, start:], tn[:, start:]
            with autocast("cuda", dtype=torch.half):
                v = model(xc, t, actions[:, start:i + 1])
            xs = ac[t].sqrt() * xc - (1 - ac[t]).sqrt() * v
            xn = ((1 / ac[t]).sqrt() * xc - xs) / (1 / ac[t] - 1).sqrt()
            an = ac[tn]
            an[:, :-1] = 1
            if ni == 1:
                an[:, -1:] = 1
            x[:, -1:] = (an.sqrt() * xs + xn * (1 - an).sqrt())[:, -1:]
    z = rearrange(x, "b t c h w -> (b t) (h w) c")
    img = (vae.decode(z / 0.07843137255) + 1) / 2
    return (rearrange(img, "(b t) c h w -> b t h w c", t=total)[0].clamp(0, 1) * 255).byte()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seqs", required=True)
    ap.add_argument("--frames", type=int, default=40)
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--yaw_idx", type=int, default=16)
    ap.add_argument("--prompts", default="sample_data/sample_image_0.png")
    ap.add_argument("--ddim_steps", type=int, default=32)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    from huggingface_hub import snapshot_download
    d = snapshot_download("camenduru/oasis-500m")
    model = DiT_models["DiT-S/2"]()
    model.load_state_dict(torch.load(os.path.join(d, "oasis500m.pt"), weights_only=True), strict=False)
    model = model.to(DEV).eval()
    vae = VAE_models["vit-l-20-shallow-encoder"]()
    vae.load_state_dict(torch.load(os.path.join(d, "vit-l-20.pt"), weights_only=True))
    vae = vae.to(DEV).eval()
    for pi, pp in enumerate(a.prompts.split(",")):
        x = load_prompt(os.path.join(OA, pp), video_offset=None, n_prompt_frames=1).to(DEV)
        H, W = x.shape[-2:]
        with torch.no_grad(), autocast("cuda", dtype=torch.half):
            z = vae.encode(rearrange(x, "b t c h w -> (b t) c h w") * 2 - 1).mean * 0.07843137255
        x0 = rearrange(z, "(b t) (h w) c -> b t c h w", t=1, h=H // vae.patch_size, w=W // vae.patch_size)
        for seed in parse_range(a.seeds):
            for spec in ["none"] + expand(a.seqs):
                f = os.path.join(a.out, f"p{pi}_s{seed}_{spec.replace(':', '~')}.npz")
                if os.path.exists(f):
                    continue
                act = torch.zeros(1, a.frames, 25, device=DEV)
                # generate.py prepends a zero action for the prompt frame: action t conditions frame t
                act[0, :, a.yaw_idx] = torch.tensor(yaw(spec, a.frames), device=DEV)
                v = rollout(model, vae, x0, act, seed, a.frames, a.ddim_steps)
                np.savez_compressed(f, frames=v[:, ::2, ::2].cpu().numpy(), yaw_cmd=yaw(spec, a.frames), spec=spec)
                print(pi, seed, spec, flush=True)


if __name__ == "__main__":
    main()
