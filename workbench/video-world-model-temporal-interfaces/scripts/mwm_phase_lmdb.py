"""Phase-shifted re-encoding of the official minWM training videos (tests the data-phase hypothesis).

Every velocity change in the official trajectories (preencode_input.json) happens at latent 5, 9 or 13, i.e. at
in-block position 1 of the causal student's 4-latent blocks: the training data never contains a velocity change
across a block boundary. Here each 77-frame video is cropped to 61 frames (16 latents) starting at frame 4*s, so
new latent j = old latent j+s and the changes move to in-block position (1-s) mod 4. Poses are the official
pose_str poses [s, s+16) re-expressed relative to the new first frame.
  --shifts 0,4      -> changes stay at position 1 (control; two crops for the same content diversity)
  --shifts 0,1,2,3  -> changes uniformly at positions 1,0,3,2 (phase-randomized)
Usage: python mwm_phase_lmdb.py --out DIR/s0 --shifts 0,1,2,3 --n 1200 --part 0/2  (DIR = sharded LMDB parent)
"""
import argparse
import json
import os
import re
import sys

import numpy as np
import torch

WB = os.environ["WB"]
MWM = os.path.join(WB, "vendor", "minWM")
sys.path.insert(0, MWM)
sys.path.insert(0, os.path.join(MWM, "tools", "data", "wan21"))

import lmdb  # noqa: E402  (vendored wheel on PYTHONPATH)
from scipy.spatial.transform import Rotation  # noqa: E402
from build_worldplaygen_lmdb import Wan21VAE, _parse_pose_string, load_video_frames  # noqa: E402
from minwm.data.preprocessing.trajectory import generate_camera_trajectory_local  # noqa: E402

N_LAT = 16
N_FRAMES = 4 * (N_LAT - 1) + 1  # 61
FX, FY = 969.6969696969696 / 1920.0, 969.6969696969696 / 1080.0


def shifted_poses(pose_str, s):
    c2w = [np.array(m) for m in generate_camera_trajectory_local(_parse_pose_string(pose_str))]
    ref = np.linalg.inv(c2w[s])
    poses = np.zeros((N_LAT, 7), dtype=np.float32)
    for j in range(N_LAT):
        w2c = np.linalg.inv(ref @ c2w[s + j])
        poses[j, :3] = w2c[:3, 3]
        poses[j, 3:] = Rotation.from_matrix(w2c[:3, :3]).as_quat()
    return np.array([FX, FY, 0.5, 0.5], dtype=np.float32), poses


def change_latents(pose_str, s):
    k, out = 0, []
    for seg in [c.strip() for c in pose_str.split(",") if c.strip()][:-1]:
        k += int(float(seg.split("-")[1]))
        if 1 <= k + 1 - s < N_LAT:
            out.append(k + 1 - s)
    return out


def vpath(video_dir, i, it):
    return os.path.join(video_dir, f"{i:06d}_" + re.sub(r"[^a-z0-9]", "", it["pose_str"].lower()), "gen.mp4")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--shifts", required=True)
    ap.add_argument("--n", type=int, default=2400)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--part", default="0/1", help="i/m: encode the i-th of m contiguous slices of the sampled list")
    ap.add_argument("--video_dir", default=os.path.join(WB, "data", "minwm_videos", "videos"))
    a = ap.parse_args()
    from huggingface_hub import hf_hub_download
    items = json.load(open(hf_hub_download("MIN-Lab/minWM-data", "preencode_input.json", repo_type="dataset")))
    shifts = [int(x) for x in a.shifts.split(",")]
    have = [i for i, it in enumerate(items) if os.path.exists(vpath(a.video_dir, i, it))]
    rng = np.random.default_rng(a.seed)
    idx = rng.permutation(have)[:a.n]
    sh = rng.choice(shifts, size=len(idx))
    pi, pm = map(int, a.part.split("/"))
    sl = slice(pi * len(idx) // pm, (pi + 1) * len(idx) // pm)
    idx, sh = idx[sl], sh[sl]
    vae = Wan21VAE(os.path.join(MWM, "ckpts", "Wan2.1-T2V-1.3B", "Wan2.1_VAE.pth"), torch.device("cuda"))
    os.makedirs(a.out, exist_ok=True)
    env = lmdb.open(a.out, map_size=int(a.n * (N_LAT * 16 * 60 * 104 * 2 + 10000) * 1.3))
    manifest, c = [], 0
    for i, s in zip(idx, sh):
        it = items[int(i)]
        v = load_video_frames(vpath(a.video_dir, int(i), it))
        if v is None:
            continue
        lat = vae.encode(v[:, 4 * s:4 * s + N_FRAMES].unsqueeze(0).cuda()).cpu().numpy()[0]
        intr, poses = shifted_poses(it["pose_str"], int(s))
        with env.begin(write=True) as txn:
            txn.put(f"latents_{c}_data".encode(), lat.tobytes())
            txn.put(f"prompts_{c}_data".encode(), it["caption"].encode())
            txn.put(f"intrinsics_{c}_data".encode(), intr.tobytes())
            txn.put(f"poses_{c}_data".encode(), poses.tobytes())
        manifest.append(dict(row=c, src=int(i), shift=int(s), pose_str=it["pose_str"],
                             change_latents=change_latents(it["pose_str"], int(s))))
        c += 1
        if c % 100 == 0:
            print(c, lat.shape, flush=True)
    with env.begin(write=True) as txn:
        txn.put(b"latents_shape", f"{c} {N_LAT} 16 60 104".encode())
        txn.put(b"prompts_shape", str(c).encode())
        txn.put(b"intrinsics_shape", f"{c} 4".encode())
        txn.put(b"poses_shape", f"{c} {N_LAT} 7".encode())
    env.close()
    json.dump(manifest, open(os.path.join(a.out, "manifest.json"), "w"))
    pos = np.bincount([k % 4 for m in manifest for k in m["change_latents"]], minlength=4)
    print(f"wrote {c} rows; velocity changes by in-block position 0..3: {pos.tolist()}")


if __name__ == "__main__":
    main()
