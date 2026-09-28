"""System identification of Matrix-Game 2.0's action->motion map with arbitrary per-frame action sequences.

Each sequence is run with the same image and noise as a no-action reference (paired counterfactual; the
rollout is bit-deterministic given the seed). Sequence families:
  impulse:A:f     mouse yaw = A only at frame f (1-frame pulse)
  sine:A:P:phi    mouse yaw = A*sin(2*pi*t/P + phi) for t >= t0 (t0=9), 0 before
  kimpulse:f      keyboard 'forward' only at frame f
Usage: python mg2_sysid.py --out DIR --images 0000,0001 --seeds 0 --seqs impulse:0.1:9-32,sine:0.1:4:0 --latents 12
"""
import argparse
import hashlib
import math
import os

import numpy as np
import torch

from mg2_probe import MG2, Runner, parse_range, snapshot  # noqa: F401  (MG2 import sets cwd)


def build(spec, n):
    kb = torch.zeros(n, 4)
    ms = torch.zeros(n, 2)
    p = spec.split(":")
    if p[0] == "impulse":
        ms[int(p[2]), 1] = float(p[1])
    elif p[0] == "sine":
        A, P, phi, t0 = float(p[1]), float(p[2]), float(p[3]), 9
        for t in range(t0, n):
            ms[t, 1] = A * math.sin(2 * math.pi * (t - t0) / P + phi)
    elif p[0] == "kimpulse":
        kb[int(p[1]), 0] = 1.0
    elif p[0] == "ktap":  # ktap:key_idx:f:dur  (keyboard key held for dur frames starting at f)
        kb[int(p[2]):int(p[2]) + int(p[3]), int(p[1])] = 1.0
    elif p[0] == "series":  # explicit comma-free series: series:v0_v1_v2...
        v = [float(x) for x in p[1].split("_")]
        ms[: len(v), 1] = torch.tensor(v[:n])
    else:
        raise ValueError(spec)
    return kb, ms


def expand(seqs):
    out = []
    for s in seqs.split(","):
        p = s.split(":")
        if p[0] == "impulse" and "-" in p[2]:
            out += [f"impulse:{p[1]}:{f}" for f in parse_range(p[2])]
        elif p[0] == "ktap" and "-" in p[2]:
            out += [f"ktap:{p[1]}:{f}:{p[3]}" for f in parse_range(p[2])]
        elif p[0] == "kimpulse" and "-" in p[1]:
            out += [f"kimpulse:{f}" for f in parse_range(p[1])]
        else:
            out.append(s)
    return out


def spec_tag(spec):
    t = spec.replace(":", "~")
    return t if len(t) <= 60 else "series~" + hashlib.md5(spec.encode()).hexdigest()[:10]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--images", default="0000")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--seqs", required=True)
    ap.add_argument("--latents", type=int, default=12)
    ap.add_argument("--ckpt", default="base_distilled_model/base_distill.safetensors")
    ap.add_argument("--nfpb", type=int, default=0, help="override latents per block at inference (0 = config)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = Runner(snapshot("Skywork/Matrix-Game-2.0"), ckpt=a.ckpt)
    if a.nfpb:
        R.pipe.num_frame_per_block = a.nfpb
        R.pipe.generator.model.num_frame_per_block = a.nfpb
    n = (a.latents - 1) * 4 + 1
    for im in a.images.split(","):
        path = os.path.join(MG2, "demo_images", "universal", f"{im}.png")
        for seed in parse_range(a.seeds):
            ref_f = os.path.join(a.out, f"{im}_s{seed}_L{a.latents}_none.npz")
            if not os.path.exists(ref_f):
                kb, ms = build("series:0", n)
                ref = R.rollout(path, seed, kb, ms, a.latents)
                np.savez_compressed(ref_f, frames=ref[:, ::2, ::2].byte().cpu().numpy())
            for spec in expand(a.seqs):
                f = os.path.join(a.out, f"{im}_s{seed}_L{a.latents}_{spec_tag(spec)}.npz")
                if os.path.exists(f):
                    continue
                kb, ms = build(spec, n)
                v = R.rollout(path, seed, kb, ms, a.latents)
                np.savez_compressed(f, frames=v[:, ::2, ::2].byte().cpu().numpy(), yaw_cmd=ms[:, 1].numpy(),
                                    fwd_cmd=kb[:, 0].numpy(), spec=spec)
            print(im, seed, "done", flush=True)


if __name__ == "__main__":
    main()
