"""Does a temporally compressed causal video VAE reconstruct the same source frame differently depending
on where it falls inside a latent step ("phase"), and does it low-pass fast motion?

Design: for a real clip (DAVIS 2017, 480p) take windows starting at s+p, p in {0..P-1}, length 1+4k.
A source frame u lands at clip position t = u - s - p; its phase is (t-1) mod 4 for t>=1 (t=0 is the
separately-encoded first frame). Encode->decode each window with the frozen VAE and, for every source
frame covered by all windows, compare reconstruction error and temporal-difference error across phases.
Same content, different phase => phase effect is isolated from content difficulty.

VAE: Wan2.1 VAE (4x temporal, 8x spatial, causal), official Wan2.1 code (vendor/Wan2.1, 9737cba).
Usage: python vae_phase.py --out DIR --seqs all|a,b --len 33 --H 352 --W 640
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
import torch
from PIL import Image

WB = os.environ["WB"]
sys.path.insert(0, os.path.join(WB, "vendor", "Wan2.1"))
from wan.modules.vae import WanVAE  # noqa: E402


def load_seq(d, H, W):
    fs = sorted(glob.glob(os.path.join(d, "*.jpg")))
    fr = []
    for f in fs:
        im = Image.open(f).convert("RGB")
        w, h = im.size
        # centre-crop to H:W aspect then resize
        if h / w > H / W:
            nh = int(w * H / W); top = (h - nh) // 2; im = im.crop((0, top, w, top + nh))
        else:
            nw = int(h * W / H); left = (w - nw) // 2; im = im.crop((left, 0, left + nw, h))
        fr.append(np.asarray(im.resize((W, H), Image.BICUBIC)))
    return np.stack(fr)  # (T,H,W,3) uint8


def to_t(x, dev):
    return torch.from_numpy(x).permute(3, 0, 1, 2).float().div(127.5).sub(1).to(dev)  # (3,T,H,W)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seqs", default="all")
    ap.add_argument("--len", type=int, default=33)
    ap.add_argument("--phases", type=int, default=4)
    ap.add_argument("--H", type=int, default=352)
    ap.add_argument("--W", type=int, default=640)
    ap.add_argument("--vae", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    dev = "cuda"
    from huggingface_hub import hf_hub_download
    vae_path = a.vae or hf_hub_download("Skywork/Matrix-Game-2.0", "Wan2.1_VAE.pth")
    vae = WanVAE(vae_pth=vae_path, device=dev)
    root = os.path.join(WB, "data", "DAVIS", "JPEGImages", "480p")
    seqs = sorted(os.listdir(root)) if a.seqs == "all" else a.seqs.split(",")
    for sq in seqs:
        outf = os.path.join(a.out, f"{sq}.npz")
        if os.path.exists(outf):
            continue
        X = load_seq(os.path.join(root, sq), a.H, a.W)
        s = 0
        if X.shape[0] < s + a.phases - 1 + a.len:
            continue
        src = X[s: s + a.phases - 1 + a.len].astype(np.float32)
        rec = {}
        with torch.no_grad():
            for p in range(a.phases):
                clip = X[s + p: s + p + a.len]
                z = vae.encode([to_t(clip, dev)])[0]
                y = vae.decode([z])[0].clamp(-1, 1)
                rec[p] = ((y + 1) * 127.5).permute(1, 2, 3, 0).cpu().numpy()  # (T,H,W,3) float
        # per source frame u (absolute index within src), per phase: MSE and temporal-diff MSE
        U = src.shape[0]
        mse = np.full((U, a.phases), np.nan)
        dmse = np.full((U, a.phases), np.nan)
        pos = np.full((U, a.phases), -1)
        for p in range(a.phases):
            for t in range(a.len):
                u = t + p
                mse[u, p] = ((rec[p][t] - src[u]) ** 2).mean()
                pos[u, p] = t
                if t >= 1:
                    dmse[u, p] = (((rec[p][t] - rec[p][t - 1]) - (src[u] - src[u - 1])) ** 2).mean()
        motion = np.array([np.nan] + [np.abs(src[u] - src[u - 1]).mean() for u in range(1, U)])
        np.savez_compressed(outf, mse=mse, dmse=dmse, pos=pos, motion=motion, len=a.len)
        print(sq, "done", flush=True)


if __name__ == "__main__":
    main()
