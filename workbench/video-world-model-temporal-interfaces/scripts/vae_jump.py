"""Can the frozen Wan2.1 VAE carry a single-frame camera jump at every intra-latent phase?

Stimulus: a horizontal crop window slides over a real DAVIS frame. Before frame f the window is still,
between frames f and f+1 it jumps by J px, afterwards it is still again (or, with --pan V, the window
pans at V px/frame and the jump is added on top). Encode->decode with the VAE and measure the recovered
per-frame horizontal shift (phase correlation) in input vs reconstruction.
Usage: python vae_jump.py --out FILE --seqs a,b --jumps 4,8 --fs 5-16 --pan 0
"""
import argparse
import glob
import json
import os
import sys

import cv2
import numpy as np
import torch
from PIL import Image

WB = os.environ["WB"]
sys.path.insert(0, os.path.join(WB, "vendor", "Wan2.1"))
from wan.modules.vae import WanVAE  # noqa: E402
sys.path.insert(0, os.path.join(WB, "scripts", "analysis"))
from sysid import shifts  # noqa: E402


def parse_range(s):
    out = []
    for p in s.split(","):
        if "-" in p:
            a, b = p.split("-"); out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(p))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seqs", default="bear,blackswan,car-turn,dog,horsejump-high,kite-surf")
    ap.add_argument("--jumps", default="4,8")
    ap.add_argument("--fs", default="5-16")
    ap.add_argument("--pan", type=float, default=0.0)
    ap.add_argument("--T", type=int, default=21)
    ap.add_argument("--jitter", default="", help="comma list of periods: per-frame displacement J*sin(2pi t/P) (ignores --fs)")
    a = ap.parse_args()
    from huggingface_hub import hf_hub_download
    vae = WanVAE(vae_pth=hf_hub_download("Skywork/Matrix-Game-2.0", "Wan2.1_VAE.pth"), device="cuda")
    H, W = 352, 640
    rows = []
    for sq in a.seqs.split(","):
        src = Image.open(sorted(glob.glob(os.path.join(WB, "data/DAVIS/JPEGImages/480p", sq, "*.jpg")))[0]).convert("RGB")
        src = np.asarray(src.resize((int(src.width * H / src.height * 1.6), int(H * 1.6)), Image.BICUBIC))
        src = src[(src.shape[0] - H) // 2:(src.shape[0] - H) // 2 + H]
        for J in parse_range(a.jumps):
            fs = parse_range(a.fs) if not a.jitter else [float(P) for P in a.jitter.split(",")]
            for f in fs:
                x = []
                import math
                for t in range(a.T):
                    if a.jitter:
                        off = 10 + a.pan * t + sum(J * math.sin(2 * math.pi * u / f + 0.5) for u in range(1, t + 1))
                    else:
                        off = 10 + a.pan * t + (J if t > f else 0)
                    M = np.float32([[1, 0, -off], [0, 1, 0]])
                    x.append(cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT))
                x = np.stack(x)
                with torch.no_grad():
                    t_in = torch.from_numpy(x).permute(3, 0, 1, 2).float().div(127.5).sub(1).cuda()
                    y = vae.decode([vae.encode([t_in])[0]])[0].clamp(-1, 1)
                    y = ((y + 1) * 127.5).permute(1, 2, 3, 0).byte().cpu().numpy()
                sx, sy = -shifts(x), -shifts(y)
                if a.jitter:
                    k = np.arange(a.T); sel = k >= 1; w = 2 * np.pi / f
                    X = np.stack([np.sin(w * k[sel]), np.cos(w * k[sel])], 1)
                    ci, *_ = np.linalg.lstsq(X, sx[sel], rcond=None)
                    cr, *_ = np.linalg.lstsq(X, sy[sel], rcond=None)
                    rows.append(dict(seq=sq, J=J, P=f, pan=a.pan, gain=float(np.hypot(*cr) / max(np.hypot(*ci), 1e-9)),
                                     in_series=[round(float(v), 3) for v in sx], rec_series=[round(float(v), 3) for v in sy]))
                    continue
                rows.append(dict(seq=sq, J=J, f=f, phase=(f - 1) % 4, pan=a.pan,
                                 jump_in=float(sx[f + 1]), jump_rec=float(sy[f + 1]),
                                 rec_series=[round(float(v), 3) for v in sy]))
        print(sq, "done", flush=True)
    json.dump(rows, open(a.out, "w"))


if __name__ == "__main__":
    main()
