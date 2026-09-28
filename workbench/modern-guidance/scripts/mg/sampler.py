"""Instrumented rectified-flow sampler for FLUX.2 [klein] base with pluggable guidance rules.

Convention (diffusers FlowMatchEuler): x_sigma = (1 - sigma) * x0 + sigma * eps, model predicts
v = eps - x0, Euler step x <- x + (sigma_next - sigma) * v.  sigma runs 1 -> 0.

A guidance rule is a callable rule(vc, vu, ctx) -> v_guided, where vc / vu are the conditional /
unconditional velocity predictions (B, N, C) in float32 and ctx carries step index, sigma, latents
and a per-sample state dict.  Every step logs per-sample geometry of vc, vu, delta = vc - vu and the
applied correction g = v_guided - vu relative to delta (parallel coefficient / orthogonal norm).
"""
import math
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.abspath(os.path.join(HERE, "..", "..", "vendor", "diffusers-src", "src"))
if VENDOR not in sys.path:
    sys.path.insert(0, VENDOR)

from diffusers import Flux2KleinPipeline  # noqa: E402
from diffusers.pipelines.flux2.pipeline_flux2_klein import compute_empirical_mu, retrieve_timesteps  # noqa: E402

MODEL_ID = "black-forest-labs/FLUX.2-klein-base-4B"


def load_pipe(device="cuda", dtype=torch.bfloat16, revision=None):
    pipe = Flux2KleinPipeline.from_pretrained(MODEL_ID, torch_dtype=dtype, revision=revision)
    pipe.to(device)
    pipe.set_progress_bar_config(disable=True)
    return pipe


def _flat(x):
    return x.reshape(x.shape[0], -1).float()


def geometry(vc, vu, vg):
    """Per-sample scalar geometry of one step. All inputs (B, N, C)."""
    c, u, g = _flat(vc), _flat(vu), _flat(vg)
    d = c - u
    corr = g - u
    dn2 = (d * d).sum(1).clamp_min(1e-12)
    par = (corr * d).sum(1) / dn2  # effective scale at this step (== w for CFG)
    orth = corr - par[:, None] * d
    cos = lambda a, b: (a * b).sum(1) / (a.norm(dim=1) * b.norm(dim=1)).clamp_min(1e-12)
    return {
        "norm_c": c.norm(dim=1), "norm_u": u.norm(dim=1), "norm_d": d.norm(dim=1), "norm_g": g.norm(dim=1),
        "cos_cu": cos(c, u), "cos_dc": cos(d, c), "cos_du": cos(d, u),
        "w_eff": par, "orth_rel": orth.norm(dim=1) / dn2.sqrt(),
    }


@torch.no_grad()
def encode(pipe, prompts, device="cuda", max_sequence_length=512):
    pe, pid = pipe.encode_prompt(prompt=prompts, device=device, num_images_per_prompt=1,
                                 max_sequence_length=max_sequence_length)
    ne, nid = pipe.encode_prompt(prompt=[""] * len(prompts), device=device, num_images_per_prompt=1,
                                 max_sequence_length=max_sequence_length)
    return pe, pid, ne, nid


@torch.no_grad()
def sample(pipe, prompts, seeds, rule, steps=30, height=1024, width=1024, device="cuda",
           enc=None, log_geometry=True, return_latents=False, sigmas=None, stop_after=None, init_latents=None):
    """Generate one image per (prompt, seed). Returns dict(images=[PIL], geom={key: (T, B)}, ...)."""
    B = len(prompts)
    assert len(seeds) == B
    pe, pid, ne, nid = enc if enc is not None else encode(pipe, prompts, device)
    nch = pipe.transformer.config.in_channels // 4
    lats, lids = [], []
    for s in seeds:
        g = torch.Generator(device=device).manual_seed(int(s))
        l, li = pipe.prepare_latents(batch_size=1, num_latents_channels=nch, height=height, width=width,
                                     dtype=pe.dtype, device=device, generator=g, latents=None)
        lats.append(l)
        lids.append(li)
    latents = torch.cat(lats) if init_latents is None else init_latents.clone()
    lat_ids = torch.cat(lids)
    x0_noise = latents.clone()

    sig = np.linspace(1.0, 1 / steps, steps) if sigmas is None else np.asarray(sigmas)
    mu = compute_empirical_mu(image_seq_len=latents.shape[1], num_steps=steps)
    timesteps, _ = retrieve_timesteps(pipe.scheduler, steps, device, sigmas=list(sig), mu=mu)
    sched_sigmas = pipe.scheduler.sigmas.to(device).float()  # length steps+1, ends at 0

    geo = {}
    state = {}
    tr = pipe.transformer
    for i, t in enumerate(timesteps):
        if stop_after is not None and i >= stop_after:
            break
        ts = t.expand(B).to(latents.dtype)
        x_in = torch.cat([latents, latents]).to(tr.dtype)
        out = tr(hidden_states=x_in, timestep=torch.cat([ts, ts]) / 1000, guidance=None,
                 encoder_hidden_states=torch.cat([pe, ne]), txt_ids=torch.cat([pid, nid]),
                 img_ids=torch.cat([lat_ids, lat_ids]), return_dict=False)[0]
        vc, vu = out[:B], out[B:]
        vc = vc[:, : latents.shape[1]].float()
        vu = vu[:, : latents.shape[1]].float()
        s_cur, s_next = sched_sigmas[i].item(), sched_sigmas[i + 1].item()
        ctx = dict(i=i, n=len(timesteps), sigma=s_cur, sigma_next=s_next, x=latents.float(), state=state,
                   pipe=pipe, enc=(pe, pid, ne, nid), lat_ids=lat_ids, t=t)
        v = rule(vc, vu, ctx)
        if log_geometry:
            for k, val in geometry(vc, vu, v).items():
                geo.setdefault(k, []).append(val.cpu())
        if "x_override" in ctx:  # rules that define their own update (e.g. CFG++)
            latents = ctx.pop("x_override").to(latents.dtype)
        else:
            latents = (latents.float() + (s_next - s_cur) * v).to(latents.dtype)
    res = {"geom": {k: torch.stack(v).numpy() for k, v in geo.items()},
           "sigmas": sched_sigmas.cpu().numpy()}
    if return_latents:
        res["latents"] = latents.clone()
        res["noise"] = x0_noise
    if stop_after is None:
        res["images"] = decode(pipe, latents, lat_ids, height, width)
    return res


@torch.no_grad()
def decode(pipe, latents, lat_ids, height=1024, width=1024):
    lat = pipe._unpack_latents_with_ids(latents, lat_ids)
    bn_mean = pipe.vae.bn.running_mean.view(1, -1, 1, 1).to(lat.device, lat.dtype)
    bn_std = torch.sqrt(pipe.vae.bn.running_var.view(1, -1, 1, 1) + pipe.vae.config.batch_norm_eps).to(lat.device, lat.dtype)
    lat = lat * bn_std + bn_mean
    lat = pipe._unpatchify_latents(lat)
    img = pipe.vae.decode(lat.to(pipe.vae.dtype), return_dict=False)[0]
    return pipe.image_processor.postprocess(img, output_type="pil")
