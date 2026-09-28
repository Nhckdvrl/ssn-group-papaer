"""Matrix-Game 2.0 *foundation* (bidirectional, multi-step) model under the same paired sysid protocol.

The base model (HF Skywork/Matrix-Game-2.0 base_model/) is the bidirectional full-sequence teacher that
the causal few-step student was distilled from (report Sec. 4.2; 57-frame clips = 15 latents). We sample
it with deterministic flow-matching Euler (shift 5.0, as in the repo's FlowMatchScheduler), no CFG, all
15 latents denoised jointly. Same image/noise for the no-action reference and every action sequence.
Usage: python mg2_base.py --out DIR --images 0001 --seeds 0 --seqs impulse:0.1:9-40 --steps 30
"""
import argparse
import json
import os

import numpy as np
import torch
from einops import rearrange
from safetensors.torch import load_file

from mg2_probe import MG2, Runner, parse_range, snapshot  # noqa: F401
from mg2_sysid import build, expand
from wan.modules.model import WanModel
from utils.scheduler import FlowMatchScheduler
from wan.modules import action_module as _am

# The released MG2 code only exercises the causal path; in the bidirectional path ActionModule.forward keeps
# its default num_frame_per_block=3 and fails to broadcast. For is_causal=False the whole clip is one block.
_orig_fwd = _am.ActionModule.forward


def _fwd(self, x, tt, th, tw, *args, **kw):
    if not kw.get("is_causal", False):
        kw["num_frame_per_block"] = int(tt)
    return _orig_fwd(self, x, tt, th, tw, *args, **kw)


_am.ActionModule.forward = _fwd


def load_base(ckpt_dir, dev, dtype):
    cfg = json.load(open(os.path.join(MG2, "configs", "foundation_model", "config.json")))
    kw = {k: cfg[k] for k in ["dim", "eps", "ffn_dim", "freq_dim", "in_dim", "num_heads", "num_layers",
                              "out_dim", "text_len", "action_config"]}
    sd = load_file(os.path.join(ckpt_dir, "base_model", "diffusion_pytorch_model.safetensors"))
    # the released config says keyboard_dim_in=4 but the weights are 6-dim; trust the weights
    kw["action_config"] = dict(kw["action_config"],
                               keyboard_dim_in=sd["blocks.0.action_model.keyboard_embed.0.weight"].shape[1])
    m = WanModel(model_type="i2v", **kw)
    missing, unexpected = m.load_state_dict(sd, strict=False)
    print("base load: missing", len(missing), missing[:5], "unexpected", len(unexpected), unexpected[:5], flush=True)
    m.kb_dim = kw["action_config"]["keyboard_dim_in"]
    return m.to(dev, dtype).eval().requires_grad_(False)


@torch.no_grad()
def sample(R, model, img_path, seed, kb, ms, n_lat, steps):
    cc, vc = R.image_cond(img_path, n_lat)
    if kb.shape[1] < model.kb_dim:  # zero-pad keyboard to the base model's 6-dim action space
        kb = torch.cat([kb, torch.zeros(kb.shape[0], model.kb_dim - kb.shape[1])], 1)
    g = torch.Generator(device=R.dev).manual_seed(seed)
    x = torch.randn([1, 16, n_lat, 44, 80], device=R.dev, dtype=torch.float32, generator=g)
    sch = FlowMatchScheduler(shift=5.0, sigma_min=0.0, extra_one_step=True)
    sch.set_timesteps(steps)
    sig = sch.sigmas.tolist() + [0.0]
    for i in range(steps):
        t = torch.tensor([sch.timesteps[i]], device=R.dev)
        v = model(x.to(R.dtype), t=t, visual_context=vc, cond_concat=cc,
                  mouse_cond=ms[None].to(R.dev, R.dtype), keyboard_cond=kb[None].to(R.dev, R.dtype))
        x = x + (sig[i + 1] - sig[i]) * v.float()
    # decode all latents at once with the streaming decoder and a fresh cache
    from demo_utils.constant import ZERO_VAE_CACHE
    import copy
    cache = [None] * len(copy.deepcopy(ZERO_VAE_CACHE))
    vid, _ = R.pipe.vae_decoder(x.to(torch.float16).transpose(1, 2), *cache)
    v = rearrange(vid, "B T C H W -> B T H W C")
    return ((v.float() + 1) * 127.5).clip(0, 255)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--images", default="0001")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--seqs", required=True)
    ap.add_argument("--latents", type=int, default=15)
    ap.add_argument("--steps", type=int, default=30)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ckpt_dir = snapshot("Skywork/Matrix-Game-2.0")
    R = Runner(ckpt_dir)
    R.pipe.generator.to("cpu")  # free the distilled student; only VAE/CLIP/decoder are reused
    torch.cuda.empty_cache()
    model = load_base(ckpt_dir, R.dev, R.dtype)
    n = (a.latents - 1) * 4 + 1
    for im in a.images.split(","):
        path = os.path.join(MG2, "demo_images", "universal", f"{im}.png")
        for seed in parse_range(a.seeds):
            tag = f"{im}_s{seed}_L{a.latents}_K{a.steps}"
            ref_f = os.path.join(a.out, f"{tag}_none.npz")
            if not os.path.exists(ref_f):
                kb, ms = build("series:0", n)
                ref = sample(R, model, path, seed, kb, ms, a.latents, a.steps)
                ref2 = sample(R, model, path, seed, kb, ms, a.latents, a.steps)
                np.savez_compressed(ref_f, frames=ref[:, ::2, ::2].byte().cpu().numpy(),
                                    det_maxdiff=float((ref - ref2).abs().max()))
                print(tag, "ref T", ref.shape[0], "determinism", float((ref - ref2).abs().max()), flush=True)
            for spec in expand(a.seqs):
                f = os.path.join(a.out, f"{tag}_{spec.replace(':', '~')}.npz")
                if os.path.exists(f):
                    continue
                kb, ms = build(spec, n)
                v = sample(R, model, path, seed, kb, ms, a.latents, a.steps)
                np.savez_compressed(f, frames=v[:, ::2, ::2].byte().cpu().numpy(), spec=spec)
            print(tag, "done", flush=True)


if __name__ == "__main__":
    main()
