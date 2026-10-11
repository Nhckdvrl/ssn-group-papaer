"""Bandwidth law on frozen foundation-model features (the representations used by DINO-WM-style world models).

For each encoder, frames (224px, from the original HDF5) of a task are encoded; two metrics:
  cls   : CLS / pooled embedding (L2)
  patch : concatenation of all patch tokens (DINO-WM's planning cost is MSE over patch tokens)
For each: effective dimension D_eff = (tr K)^2 / ||K||_F^2 of the centred Gram matrix (= covariance
participation ratio), and the bandwidth of the normalized kernel k(r) vs true state distance r
(Gaussian fit and half-decay), plus Spearman of latent distance with true distance (near / far).
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '4')
import hdf5plugin  # noqa: F401
import h5py
import numpy as np
import torch
from scipy.optimize import curve_fit
from scipy.stats import spearmanr

SRC = {'tworoom': '/tmp/latent-wm-data/tworoom.h5', 'pusht': '/tmp/latent-wm-data/pusht_expert_train.h5'}


def load_frames(task, n, seed=0):
    g = np.random.default_rng(seed)
    with h5py.File(SRC[task], 'r') as h:
        N = h['pixels'].shape[0]
        idx = np.sort(g.choice(N, n, replace=False))
        # read in contiguous chunks of the HDF5 chunking (100 frames) to keep random access cheap
        px = np.stack([h['pixels'][i] for i in idx])
        st = h['proprio'][:][idx, :2] if task == 'tworoom' else h['state'][:][idx, :4]
    return px, st.astype(np.float64)


def kernel_stats(Z, st, g):
    Z = Z - Z.mean(0, keepdims=True)
    G = Z @ Z.T  # (n,n)
    tr = np.trace(G)
    deff = tr ** 2 / (G ** 2).sum()
    n = len(Z)
    i1, i2 = g.integers(0, n, 60000), g.integers(0, n, 60000)
    sq = np.diag(G)
    d2 = sq[i1] + sq[i2] - 2 * G[i1, i2]
    k = 1 - d2 / (2 * tr / n)
    r = np.linalg.norm(st[i1] - st[i2], axis=1)
    bins = np.linspace(0, np.percentile(r, 95), 40)
    cen, kk = [], []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (r >= lo) & (r < hi)
        if m.sum() > 50:
            cen.append(r[m].mean()); kk.append(k[m].mean())
    cen, kk = np.array(cen), np.array(kk)
    try:
        (a, ell, b), _ = curve_fit(lambda x, a, l, b: a * np.exp(-x ** 2 / (2 * l ** 2)) + b, cen, kk, p0=[1, 20, 0], maxfev=20000)
    except Exception:
        ell = np.nan
    half = float(cen[np.argmax(kk < (kk[0] + kk[-5:].mean()) / 2)])
    d = np.sqrt(np.maximum(d2, 0))
    near, far = r < np.percentile(r, 20), r > np.percentile(r, 50)
    return {'deff': float(deff), 'ell': float(abs(ell)), 'half': half,
            'sp_all': float(spearmanr(d, r).statistic), 'sp_near': float(spearmanr(d[near], r[near]).statistic),
            'sp_far': float(spearmanr(d[far], r[far]).statistic)}


@torch.no_grad()
def encode(name, px):
    from transformers import AutoImageProcessor, AutoModel
    proc = AutoImageProcessor.from_pretrained(name)
    model = AutoModel.from_pretrained(name, torch_dtype=torch.float16).cuda().eval()
    cls, patch = [], []
    for i in range(0, len(px), 64):
        inp = proc(images=list(px[i:i + 64]), return_tensors='pt', do_center_crop=False,
                   size={'height': 224, 'width': 224} if 'siglip' in name else {'shortest_edge': 224})
        out = model(pixel_values=inp['pixel_values'].cuda().half()) if 'siglip' not in name else \
            model.vision_model(pixel_values=inp['pixel_values'].cuda().half())
        h = out.last_hidden_state.float()
        if 'siglip' in name:
            cls.append(out.pooler_output.float().cpu()); patch.append(h.flatten(1).cpu())
        else:
            cls.append(h[:, 0].cpu()); patch.append(h[:, 1:].flatten(1).cpu())
    return torch.cat(cls).numpy(), torch.cat(patch).numpy()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--task', default='tworoom')
    p.add_argument('--n', type=int, default=6000)
    p.add_argument('--models', default='facebook/dinov2-small,facebook/dinov2-base,facebook/dinov2-large,facebook/dinov2-giant')
    p.add_argument('--out', default='/home/xiang/ssn-group-papaer/workbench/latent-world-model-planning/results/E22_fm_bandwidth.json')
    a = p.parse_args()
    out = Path(a.out)
    res = json.loads(out.read_text()) if out.exists() else {}
    px, st = load_frames(a.task, a.n)
    g = np.random.default_rng(0)
    for name in a.models.split(','):
        key = f'{a.task}|{name}'
        if key in res:
            continue
        cls, patch = encode(name, px)
        res[key] = {'cls': kernel_stats(cls, st, g), 'patch': kernel_stats(patch.astype(np.float32), st, g),
                    'dim_cls': int(cls.shape[1]), 'dim_patch': int(patch.shape[1])}
        out.write_text(json.dumps(res, indent=1))
        print(key, json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items()} if isinstance(v, dict) else v for k, v in res[key].items()}), flush=True)


if __name__ == '__main__':
    main()
