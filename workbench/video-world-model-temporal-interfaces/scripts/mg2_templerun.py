"""Matrix-Game 2.0 Temple Run model: do brief discrete key taps register, as a function of their phase?

Temple Run actions are naturally brief taps (jump, slide, turn). Keyboard is one-hot over
[nomove, jump, slide, turnleft, turnright, leftside, rightside]; the reference rollout holds `nomove`.
A tap sets action k for frames [f, f+dur); dur=40 = held to the end (full effect reference).
Official config inference_templerun.yaml (4 denoising steps, 3 latents/block) and checkpoint
templerun_distilled_model/templerun_7dim_onlykey.safetensors.
Usage: python mg2_templerun.py --out DIR --images 0000,0001 --seeds 0 --keys 3,1 --onsets 9-20 --durs 1,2,4,40
"""
import argparse
import os

import numpy as np
import torch

import mg2_probe as P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--images", default="0000")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--keys", default="3")
    ap.add_argument("--onsets", default="9-20")
    ap.add_argument("--durs", default="1,2,4,40")
    ap.add_argument("--latents", type=int, default=12)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = P.Runner(P.snapshot("Skywork/Matrix-Game-2.0"), config="configs/inference_yaml/inference_templerun.yaml",
                 ckpt="templerun_distilled_model/templerun_7dim_onlykey.safetensors")
    n = (a.latents - 1) * 4 + 1
    ms = torch.zeros(n, 2)
    for im in a.images.split(","):
        path = os.path.join(P.MG2, "demo_images", "temple_run", f"{im}.png")
        for seed in P.parse_range(a.seeds):
            ref_f = os.path.join(a.out, f"{im}_s{seed}_none.npz")
            kb0 = torch.zeros(n, 7)
            kb0[:, 0] = 1
            if not os.path.exists(ref_f):
                np.savez_compressed(ref_f, frames=R.rollout(path, seed, kb0, ms, a.latents)[:, ::2, ::2].byte().cpu().numpy())
            for k in P.parse_range(a.keys):
                for f in P.parse_range(a.onsets):
                    for dur in P.parse_range(a.durs):
                        if dur >= 40 and f != P.parse_range(a.onsets)[0]:
                            continue  # one held reference per key
                        tag = os.path.join(a.out, f"{im}_s{seed}_k{k}_f{f:02d}_d{dur:02d}.npz")
                        if os.path.exists(tag):
                            continue
                        kb = kb0.clone()
                        kb[f:f + dur] = 0
                        kb[f:f + dur, k] = 1
                        v = R.rollout(path, seed, kb, ms, a.latents)
                        np.savez_compressed(tag, frames=v[:, ::2, ::2].byte().cpu().numpy())
            print(im, seed, "done", flush=True)


if __name__ == "__main__":
    main()
