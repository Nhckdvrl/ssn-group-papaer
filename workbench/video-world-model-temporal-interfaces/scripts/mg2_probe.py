"""Matrix-Game 2.0 (distilled, universal) action-timing probe.

Paired counterfactual design: for a fixed (image, noise seed), generate a reference rollout with no action
and rollouts where one action switches on at frame f (and stays on). Because rollout is causal given the
same noise, frames that come before the action's influence should be bit-identical to the reference; the
first frame that departs from it is the model's response onset.

Official pipeline code is used unchanged (CausalInferencePipeline, Wan2.1 VAE, checkpoint
base_distilled_model/base_distill.safetensors, config inference_universal.yaml: 3 steps, 3 latents/block,
local attention 6 latents, 352x640).

Usage: python mg2_probe.py --out DIR --images 0000,0003 --seeds 0,1 --actions cam_r,fwd --onsets 1-24 --latents 12
Writes DIR/<image>_s<seed>_<action>_f<onset>.npz with frames (T,H/2,W/2,3 uint8) and per-frame stats.
"""
import argparse
import os
import sys
import time

import numpy as np
import torch
from einops import rearrange
from omegaconf import OmegaConf
from safetensors.torch import load_file

MG2 = os.environ["MG2"]
sys.path.insert(0, MG2)
os.chdir(MG2)

from diffusers.utils import load_image  # noqa: E402
from torchvision.transforms import v2  # noqa: E402
from demo_utils.vae_block3 import VAEDecoderWrapper  # noqa: E402
from pipeline import CausalInferencePipeline  # noqa: E402
from utils.wan_wrapper import WanDiffusionWrapper  # noqa: E402
from wan.vae.wanx_vae import get_wanx_vae_wrapper  # noqa: E402

CAM = 0.1
ACTIONS = {  # (keyboard[4] = fwd, back, left, right ; mouse[2] = pitch, yaw)
    "none": ([0, 0, 0, 0], [0, 0]),
    "cam_r": ([0, 0, 0, 0], [0, CAM]),
    "cam_l": ([0, 0, 0, 0], [0, -CAM]),
    "fwd": ([1, 0, 0, 0], [0, 0]),
    "left": ([0, 0, 1, 0], [0, 0]),
}


def snapshot(repo):
    from huggingface_hub import snapshot_download
    return snapshot_download(repo)


class Runner:
    def __init__(self, ckpt_dir, config="configs/inference_yaml/inference_universal.yaml",
                 ckpt="base_distilled_model/base_distill.safetensors"):
        self.dev = torch.device("cuda")
        self.dtype = torch.bfloat16
        self.cfg = OmegaConf.load(config)
        self.mode = self.cfg.pop("mode")
        gen = WanDiffusionWrapper(**getattr(self.cfg, "model_kwargs", {}), is_causal=True)
        dec = VAEDecoderWrapper()
        sd = torch.load(os.path.join(ckpt_dir, "Wan2.1_VAE.pth"), map_location="cpu")
        dec.load_state_dict({k: v for k, v in sd.items() if "decoder." in k or "conv2" in k})
        dec.to(self.dev, torch.float16).requires_grad_(False).eval()
        self.pipe = CausalInferencePipeline(self.cfg, generator=gen, vae_decoder=dec)
        self.pipe.generator.load_state_dict(load_file(os.path.join(ckpt_dir, ckpt)))
        self.pipe = self.pipe.to(device=self.dev, dtype=self.dtype)
        self.pipe.vae_decoder.to(torch.float16)
        vae = get_wanx_vae_wrapper(ckpt_dir, torch.float16)
        vae.requires_grad_(False)  # wrapper is not an nn.Module: these do not return self
        vae.eval()
        self.vae = vae.to(self.dev, self.dtype)
        self.tf = v2.Compose([v2.Resize(size=(352, 640), antialias=True), v2.ToTensor(),
                              v2.Normalize(mean=[0.5] * 3, std=[0.5] * 3)])
        self._img_cache = {}

    def _resizecrop(self, image, th=352, tw=640):
        w, h = image.size
        if h / w > th / tw:
            nw, nh = int(w), int(int(w) * th / tw)
        else:
            nh, nw = int(h), int(int(h) * tw / th)
        l, t = (w - nw) / 2, (h - nh) / 2
        return image.crop((l, t, l + nw, t + nh))

    @torch.no_grad()
    def image_cond(self, path, n_lat):
        key = (path, n_lat)
        if key not in self._img_cache:
            im = self.tf(self._resizecrop(load_image(path)))[None, :, None].to(self.dev, self.dtype)
            pad = torch.zeros_like(im).repeat(1, 1, 4 * (n_lat - 1), 1, 1)
            tk = {"tiled": True, "tile_size": [44, 80], "tile_stride": [23, 38]}
            ic = self.vae.encode(torch.cat([im, pad], 2), device=self.dev, **tk).to(self.dev)
            m = torch.ones_like(ic)
            m[:, :, 1:] = 0
            self._img_cache[key] = (torch.cat([m[:, :4], ic], 1).to(self.dtype),
                                    self.vae.clip.encode_video(im).to(self.dtype))
        return self._img_cache[key]

    @torch.no_grad()
    def rollout(self, img_path, seed, keyboard, mouse, n_lat):
        cc, vc = self.image_cond(img_path, n_lat)
        g = torch.Generator(device=self.dev).manual_seed(seed)
        noise = torch.randn([1, 16, n_lat, 44, 80], device=self.dev, dtype=self.dtype, generator=g)
        torch.manual_seed(seed)  # pipeline re-noising between steps uses the global RNG
        cond = {"cond_concat": cc, "visual_context": vc,
                "keyboard_cond": keyboard[None].to(self.dev, self.dtype),
                "mouse_cond": mouse[None].to(self.dev, self.dtype)}
        vids = self.pipe.inference(noise=noise, conditional_dict=cond, return_latents=False, mode=self.mode)
        v = rearrange(torch.cat(vids, 1), "B T C H W -> B T H W C")
        return ((v.float() + 1) * 127.5).clip(0, 255)[0]  # (T, H, W, 3) float on GPU


def action_seq(name, onset, n_frames, base="none", dur=0):
    """Action `name` on for frames [onset, onset+dur) (dur=0: stays on to the end)."""
    kb = torch.tensor([ACTIONS[base][0]] * n_frames, dtype=torch.float32)
    ms = torch.tensor([ACTIONS[base][1]] * n_frames, dtype=torch.float32)
    if name != "none":
        end = n_frames if dur == 0 else min(n_frames, onset + dur)
        kb[onset:end] = torch.tensor(ACTIONS[name][0], dtype=torch.float32)
        ms[onset:end] = torch.tensor(ACTIONS[name][1], dtype=torch.float32)
    return kb, ms


def parse_range(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--images", default="0000")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--actions", default="cam_r")
    ap.add_argument("--onsets", default="1-24")
    ap.add_argument("--latents", type=int, default=12)
    ap.add_argument("--ckpt", default="base_distilled_model/base_distill.safetensors")
    ap.add_argument("--durs", default="0", help="pulse durations in frames; 0 = step (stays on)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ckpt_dir = snapshot("Skywork/Matrix-Game-2.0")
    R = Runner(ckpt_dir, ckpt=a.ckpt)
    n_frames = (a.latents - 1) * 4 + 1
    for im in a.images.split(","):
        path = os.path.join(MG2, "demo_images", "universal", f"{im}.png")
        for seed in parse_range(a.seeds):
            ref_f = os.path.join(a.out, f"{im}_s{seed}_none.npz")
            kb, ms = action_seq("none", 0, n_frames)
            t0 = time.time()
            ref = R.rollout(path, seed, kb, ms, a.latents)
            dt = time.time() - t0
            # determinism check: a second identical rollout must match exactly
            ref2 = R.rollout(path, seed, kb, ms, a.latents)
            det = float((ref - ref2).abs().max())
            np.savez_compressed(ref_f, frames=ref[:, ::2, ::2].byte().cpu().numpy(), sec=dt, det_maxdiff=det)
            print(f"{im} s{seed} ref T={ref.shape[0]} {dt:.1f}s determinism_maxdiff={det}", flush=True)
            for act in a.actions.split(","):
                for f in parse_range(a.onsets):
                  for dur in parse_range(a.durs):
                    kb, ms = action_seq(act, f, n_frames, dur=dur)
                    v = R.rollout(path, seed, kb, ms, a.latents)
                    diff = (v - ref).abs().mean(dim=(1, 2, 3)).cpu().numpy()  # per-frame MAE vs reference
                    first = int(np.argmax(diff > 0)) if (diff > 0).any() else -1
                    tag = f"{im}_s{seed}_{act}_f{f:02d}" + (f"_d{dur:02d}" if dur else "")
                    np.savez_compressed(os.path.join(a.out, tag + ".npz"),
                                        frames=v[:, ::2, ::2].byte().cpu().numpy(), mae_vs_ref=diff, onset=f,
                                        dur=dur, first_diff_frame=first)
                    print(f"  {act} onset={f:2d} dur={dur} first_diff_frame={first:2d} mae@first={diff[first] if first>=0 else 0:.3f}", flush=True)


if __name__ == "__main__":
    main()
