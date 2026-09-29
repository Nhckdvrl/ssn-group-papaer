"""Paired single-step yaw impulses on HY-World 1.5 (WorldPlay, HunyuanVideo-8B, 4-latent AR chunks).

Same protocol as mwm_sysid.py: identical seed/noise, a pure-yaw pose trajectory (per latent, WorldPlay pose
convention: pose i is latent i, latent 0 = reference image) that is zero except for one step of A degrees at
motion index k, so the pose changes from latent k+1 on. Chunks are latents [0-3],[4-7],..., so k with
(k+1) % 4 == 0 puts the change on a chunk's first latent.
WorldPlay's training data are mostly human game recordings and SfM-posed real videos, i.e. action changes at
arbitrary phases (unlike minWM's block-locked synthetic trajectories).
Run with torchrun --nproc_per_node=1 (the pipeline builds a device mesh).
Usage: torchrun --nproc_per_node=1 wp_sysid.py --model_path HY15 --action_ckpt CKPT --out DIR
       --images street=a.png,room=b.png --seqs impulse:3:3,impulse:3:4 [--n_lat 16] [--tag wpdist]
"""
import argparse
import os
import sys
import types

import numpy as np
import torch

WB = os.environ["WB"]
sys.path.insert(0, os.path.join(WB, "vendor", "HY-WorldPlay"))
for m in ("moviepy", "moviepy.editor"):  # only used by generate.py's keyboard overlay
    sys.modules.setdefault(m, types.SimpleNamespace(VideoFileClip=None, VideoClip=None))
from hyvideo.generate import pose_to_input  # noqa: E402  (also initializes the parallel state)
from hyvideo.generate_custom_trajectory import generate_camera_trajectory_local  # noqa: E402
from hyvideo.commons.infer_state import initialize_infer_state  # noqa: E402
from hyvideo.pipelines.worldplay_video_pipeline import HunyuanVideo_1_5_Pipeline  # noqa: E402

PROMPTS = {
    "street": "A first-person view walking down a quiet city street lined with shops and parked cars on a clear day.",
    "forest": "A first-person view of a forest trail surrounded by tall trees, green foliage and dappled sunlight.",
    "room": "A first-person view inside a bright living room with a sofa, a wooden table, bookshelves and windows.",
}


def yaw_list(spec, n_mot):
    y = np.zeros(n_mot)
    if spec != "none":
        kind, A, k = spec.split(":")
        if kind == "impulse":
            y[int(k)] = float(A)
        elif kind == "step":
            y[int(k):] = float(A)
        else:
            raise ValueError(spec)
    return y


def pose_json(yaw_deg):
    motions = [{"yaw": float(np.deg2rad(v))} if v else {} for v in yaw_deg]
    poses = generate_camera_trajectory_local(motions)
    K = [[969.6969696969696, 0.0, 960.0], [0.0, 969.6969696969696, 540.0], [0.0, 0.0, 1.0]]
    return {str(i): {"extrinsic": np.asarray(p).tolist(), "K": K} for i, p in enumerate(poses)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_path", required=True)
    ap.add_argument("--action_ckpt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--images", required=True, help="comma-separated name=path.png (name picks the prompt)")
    ap.add_argument("--seqs", required=True)
    ap.add_argument("--n_lat", type=int, default=16)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--tag", default="wpdist")
    ap.add_argument("--prompts_json", default=None, help="name -> caption (e.g. data/wp_scenes/prompts.json)")
    a = ap.parse_args()
    if a.prompts_json:
        import json
        PROMPTS.update(json.load(open(a.prompts_json)))
    os.makedirs(a.out, exist_ok=True)
    initialize_infer_state(argparse.Namespace(
        sage_blocks_range="0-53", use_sageattn=False, enable_torch_compile=False, use_fp8_gemm=False,
        quant_type="fp8-per-block", include_patterns="double_blocks", use_vae_parallel=False))
    pipe = HunyuanVideo_1_5_Pipeline.create_pipeline(
        pretrained_model_name_or_path=a.model_path, transformer_version="480p_i2v", enable_offloading=True,
        enable_group_offloading=None, create_sr_pipeline=False, force_sparse_attn=False,
        transformer_dtype=torch.bfloat16, action_ckpt=a.action_ckpt)
    video_length = 4 * (a.n_lat - 1) + 1
    for item in a.images.split(","):
        name, path = item.split("=")
        for spec in ["none"] + a.seqs.split(","):
            f = os.path.join(a.out, f"{a.tag}_p{name}_s{a.seed}_{spec.replace(':', '~')}.npz")
            if os.path.exists(f):
                continue
            y = yaw_list(spec, a.n_lat - 1)
            viewmats, Ks, action = pose_to_input(pose_json(y), a.n_lat)
            out = pipe(enable_sr=False, prompt=PROMPTS[name], aspect_ratio="16:9", num_inference_steps=a.steps,
                       sr_num_inference_steps=None, video_length=video_length, negative_prompt="", seed=a.seed,
                       output_type="pt", prompt_rewrite=False, return_pre_sr_video=False,
                       viewmats=viewmats.unsqueeze(0), Ks=Ks.unsqueeze(0), action=action.unsqueeze(0),
                       few_step=a.steps <= 4, chunk_latent_frames=4, model_type="ar", user_height=480,
                       user_width=832, transformer_resident_ar_rollout=True, reference_image=path)
            v = out.videos[0]  # (C, F, H, W) in [0, 1]
            v = (v * 255).clamp(0, 255).to(torch.uint8).permute(1, 2, 3, 0)[:, ::2, ::2]
            np.savez_compressed(f, frames=v.cpu().numpy(), yaw_cmd=y, spec=spec, action=action.numpy())
            print(a.tag, name, spec, tuple(v.shape), flush=True)


if __name__ == "__main__":
    main()
