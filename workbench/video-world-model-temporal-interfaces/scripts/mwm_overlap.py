"""Seam-overlap rollout for minWM causal students + paired impulse probe (E27).

Standard rollout: blocks [0-3],[4-7],... so every 4th latent is generated at a block seam, where control changes
are ignored. Overlap rollout: after the first block, every block is [m-1, m, m+1, m+2] where m-1 is the last kept
latent (re-generated jointly and discarded); the KV cache only ever holds kept latents. Every new latent is then
generated at in-block position 1-3, so a pose change at latent m is an in-block contrast with m-1.
Cost: 4/3 of the standard rollout.
Usage: python mwm_overlap.py --stage stage3_ar_dmd --out DIR --prompts 1,2 --seqs impulse:3:3,... [--tag ovl]
"""
import argparse
import os
import sys

import numpy as np
import torch

WB = os.environ["WB"]
sys.path.insert(0, os.path.join(WB, "scripts"))
import mwm_sysid as S  # noqa: E402  (chdir to minWM, yaw-list trajectory parser, yaw_seq)
from minwm.config import apply_overrides, load  # noqa: E402
from minwm.engine import BaseInferencer  # noqa: E402
from minwm.engine.inferencer import read_benchmark  # noqa: E402
from minwm.engine.inference.loop import _inference_autocast  # noqa: E402
from minwm.utils.seed import set_seed  # noqa: E402

PAD = 2  # extra latents so the last overlapped block fits in the cache


@torch.no_grad()
def generate_overlap(loop, batch):
    noise, vm, Ks = batch["noise"], batch["viewmats"], batch["Ks"]
    B, F = noise.shape[:2]
    Fp = F + PAD
    noise = torch.cat([noise, torch.randn_like(noise[:, :PAD])], 1)
    vm = torch.cat([vm, vm[:, -1:].expand(-1, PAD, -1, -1)], 1)
    Ks = torch.cat([Ks, Ks[:, -1:].expand(-1, PAD, -1, -1)], 1)
    H, W = noise.shape[3:]
    fs = (H // loop.generator.patch_size[1]) * (W // loop.generator.patch_size[2])
    nb = loop.num_frame_per_block
    ad, gen = loop.adapter, loop.generator
    cond = ad.conditioning(batch, B, noise.device)
    use_cfg = loop.guidance_scale > 1.0
    streams = [cond] + ([ad.null_conditioning(batch, B, noise.device)] if use_cfg else [])
    with _inference_autocast(ad, noise.dtype, noise.device):
        caches = [ad.rollout_init_cache(gen, batch_size=B, num_frames=Fp, frame_seqlen=fs, seq_len=Fp * fs,
                                        dtype=noise.dtype, device=noise.device, cond=c,
                                        use_prope_cache=True, use_local_window=True) for c in streams]
        out = torch.zeros_like(noise)
        start, kept, cached = 0, 0, 0  # block start frame, frames kept so far, frames written to cache
        bi = 0
        while kept < F:
            sl = slice(start, start + nb)
            meta = dict(block_idx=bi, f_start=start, f_end=start + nb, frame_seqlen=fs, seq_len=Fp * fs,
                        current_start=start * fs, context_noise=0)

            def forward(x, t, meta=meta, sl=sl):
                fl = [ad.rollout_forward(gen, noisy_block=x, timestep=t, cache=c, cond=s, meta=meta,
                                         viewmats=vm[:, sl], Ks=Ks[:, sl], action=None)
                      for s, c in zip(streams, caches)]
                return fl[0] if not use_cfg else fl[1] + loop.guidance_scale * (fl[0] - fl[1])

            clean = loop.sampler.step(forward=forward, noise=noise[:, sl], batch_size=B, num_frames=nb,
                                      device=noise.device)
            first_new = 0 if bi == 0 else 1  # the overlap latent (start) is discarded after block 0
            out[:, start + first_new:start + nb] = clean[:, first_new:]
            kept = start + nb
            # cache every kept latent except the newest one (it is re-generated as the next block's overlap)
            cs, ce = cached, kept - 1
            cmeta = dict(block_idx=bi, f_start=cs, f_end=ce, frame_seqlen=fs, seq_len=Fp * fs,
                         current_start=cs * fs, cache_start=cs * fs, context_noise=0)
            for s, c in zip(streams, caches):
                ad.rollout_refresh_cache(gen, clean_block=out[:, cs:ce], cache=c, cond=s, meta=cmeta,
                                         viewmats=vm[:, cs:ce], Ks=Ks[:, cs:ce], action=None)
            cached, start, bi = ce, kept - 1, bi + 1
        caches = None
    out = out[:, :F]
    gen.to("cpu")
    torch.cuda.empty_cache()
    video = ad.decode_latents(loop.vae, out)
    gen.to(noise.device)
    return {"latents": out, "video": (video * 0.5 + 0.5).clamp(0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="stage3_ar_dmd")
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompts", default="1")
    ap.add_argument("--seqs", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="ovl")
    ap.add_argument("--ov", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ov = [f"inference.checkpoint={a.ckpt}", "inference.prefer_ema=False"] if a.ckpt else []
    ov += [o for o in a.ov.split(";") if o]
    inf = BaseInferencer(apply_overrides(load(f"configs/wan21/action2v/infer/{a.stage}.py"), ov))
    bench = {str(s["id"]): s for s in read_benchmark("assets/example_t2v.json")}
    for pid in a.prompts.split(","):
        caption = bench[pid].get("caption") or bench[pid].get("prompt")
        for spec in ["none"] + a.seqs.split(","):
            f = os.path.join(a.out, f"{a.tag}_p{pid}_s{a.seed}_{spec.replace(':', '~')}.npz")
            if os.path.exists(f):
                continue
            y = S.yaw_seq(spec)
            set_seed(a.seed)
            batch = inf.build_batch({"prompt": caption, "trajectory": "yaw:" + "_".join(f"{v:.5f}" for v in y)})
            res = generate_overlap(inf.loop, batch)
            v = (res["video"][0] * 255.0).clamp(0, 255).permute(0, 2, 3, 1).to(torch.uint8)
            np.savez_compressed(f, frames=v[:, ::2, ::2].cpu().numpy(), yaw_cmd=y, spec=spec)
            print(a.tag, pid, spec, tuple(v.shape), flush=True)


if __name__ == "__main__":
    main()
