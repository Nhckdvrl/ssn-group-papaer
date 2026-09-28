"""Build an event-rich conditioning LMDB for minWM Wan Action2V DMD fine-tuning.

DMD in minWM is data-free with respect to video: the recipe only uses the latent *shape*, the prompt and the
camera trajectory (ARDMDRecipe docstring). The official training trajectories (MIN-Lab/minWM-data
preencode_input.json) are concatenations of constant segments of 4/7/8/11 latent steps, i.e. they never
contain brief camera events. This script keeps the official captions/trajectories and, for a fraction of
rows, superimposes brief yaw events (1-2 latent steps) at uniformly random positions, so about 1/4 of the
events land on block-first latents. Poses use the official conversion (build_worldplaygen_lmdb.py).

Usage: python mwm_event_lmdb.py --out DIR --n 800 --event_frac 0.5 --seed 0 [--start 0]
"""
import argparse
import json
import os
import sys

import numpy as np

WB = os.environ["WB"]
MWM = os.path.join(WB, "vendor", "minWM")
sys.path.insert(0, MWM)
sys.path.insert(0, os.path.join(MWM, "tools", "data", "wan21"))

import lmdb  # noqa: E402  (vendored wheel on PYTHONPATH)
from scipy.spatial.transform import Rotation  # noqa: E402
from minwm.data.preprocessing.trajectory import generate_camera_trajectory_local  # noqa: E402

N_LATENT = 20
LAT_SHAPE = (20, 16, 60, 104)  # (F, C, H, W) as in the official LMDB
FX, FY = 969.6969696969696 / 1920.0, 969.6969696969696 / 1080.0


def parse_pose_string(pose_string):  # verbatim semantics of build_worldplaygen_lmdb._parse_pose_string
    fs, yaw, pitch = 0.08, np.deg2rad(3), np.deg2rad(3)
    table = {"w": {"forward": fs}, "s": {"forward": -fs}, "a": {"right": -fs}, "d": {"right": fs},
             "up": {"pitch": pitch}, "down": {"pitch": -pitch}, "left": {"yaw": -yaw}, "right": {"yaw": yaw}}
    motions = []
    for cmd in [c.strip() for c in pose_string.split(",") if c.strip()]:
        act, n = cmd.split("-")
        motions += [dict(table[act.strip()]) for _ in range(int(float(n)))]
    return motions


def poses_from_motions(motions):
    c2w = generate_camera_trajectory_local(motions)[:N_LATENT]
    poses = np.zeros((N_LATENT, 7), dtype=np.float32)
    for i, m in enumerate(c2w):
        w2c = np.linalg.inv(np.array(m))
        poses[i, :3] = w2c[:3, 3]
        poses[i, 3:] = Rotation.from_matrix(w2c[:3, :3]).as_quat()
    return np.array([FX, FY, 0.5, 0.5], dtype=np.float32), poses


def add_events(motions, rng):
    motions = [dict(m) for m in motions]
    events = []
    for _ in range(rng.integers(1, 4)):
        k = int(rng.integers(1, len(motions)))
        dur = int(rng.choice([1, 1, 2]))
        amp = float(rng.choice([3.0, 3.0, 1.5, 6.0])) * float(rng.choice([-1, 1]))
        for j in range(k, min(k + dur, len(motions))):
            motions[j]["yaw"] = motions[j].get("yaw", 0.0) + np.deg2rad(amp)
        events.append((k, dur, amp))
    return motions, events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=800)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--event_frac", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    from huggingface_hub import hf_hub_download
    items = json.load(open(hf_hub_download("MIN-Lab/minWM-data", "preencode_input.json", repo_type="dataset")))
    rng = np.random.default_rng(a.seed)
    idx = rng.permutation(len(items))[a.start:a.start + a.n]
    os.makedirs(a.out, exist_ok=True)
    env = lmdb.open(a.out, map_size=int(a.n * (np.prod(LAT_SHAPE) * 2 + 10000) * 1.2))
    zeros = np.zeros(LAT_SHAPE, dtype=np.float16).tobytes()
    manifest = []
    with env.begin(write=True) as txn:
        for c, i in enumerate(idx):
            it = items[int(i)]
            motions = parse_pose_string(it["pose_str"])
            events = []
            if rng.random() < a.event_frac:
                motions, events = add_events(motions, rng)
            intr, poses = poses_from_motions(motions)
            txn.put(f"latents_{c}_data".encode(), zeros)
            txn.put(f"prompts_{c}_data".encode(), it["caption"].encode())
            txn.put(f"intrinsics_{c}_data".encode(), intr.tobytes())
            txn.put(f"poses_{c}_data".encode(), poses.tobytes())
            manifest.append(dict(row=c, src=int(i), pose_str=it["pose_str"], events=events))
        txn.put(b"latents_shape", " ".join(map(str, (a.n,) + LAT_SHAPE)).encode())
        txn.put(b"prompts_shape", str(a.n).encode())
        txn.put(b"intrinsics_shape", f"{a.n} 4".encode())
        txn.put(b"poses_shape", f"{a.n} {N_LATENT} 7".encode())
    env.close()
    json.dump(manifest, open(os.path.join(a.out, "manifest.json"), "w"))
    n_ev = sum(len(m["events"]) for m in manifest)
    n_b = sum(1 for m in manifest for e in m["events"] if (e[0] + 1) % 4 == 0)
    print(f"wrote {a.n} rows, {sum(1 for m in manifest if m['events'])} with events, {n_ev} events, {n_b} block-first")


if __name__ == "__main__":
    main()
