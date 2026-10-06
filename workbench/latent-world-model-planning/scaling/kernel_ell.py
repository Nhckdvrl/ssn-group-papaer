"""Correlation length of the latent metric vs effective dimension (distance-concentration test).

For normalized latents (unit total variance per dim on average), ||phi(x)-phi(x')||^2 / (2 var) = 1 - k(x,x').
Fit k(r) = exp(-r^2 / (2 ell^2)) on pairs of held-out encoder latents, r = true state distance
(TwoRoom: agent position, px). Report ell and D_eff (participation ratio) per checkpoint.
Prediction (packing argument): ell ~ D_eff^(-1/d), d = intrinsic state dimension.
"""
import argparse
import glob
import json
import os
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
import torch
from scipy.optimize import curve_fit

from wm import GPUData


@torch.no_grad()
def measure(ckpt, data, key_fn, n=12000, seed=0):
    model = torch.load(ckpt, map_location='cuda', weights_only=False).eval()
    g = np.random.default_rng(seed)
    idx = np.concatenate([data.meta['ep_offset'][e] + np.arange(data.meta['ep_len'][e]) for e in data.val_eps])
    idx = g.choice(idx, n, replace=False)
    px = data.pixels[data.remap[torch.as_tensor(idx, device=data.remap.device)].to(data.pixels.device)]
    zs = []
    for i in range(0, n, 2048):
        x = px[i:i + 2048].to('cuda').permute(0, 3, 1, 2).float().div_(255)
        x = ((x - data.mean) / data.std)[:, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            zs.append(model.encode({'pixels': x})['emb'][:, 0].float().cpu())
    z = torch.cat(zs).numpy()
    s = key_fn(idx)
    var = ((z - z.mean(0)) ** 2).sum(1).mean()
    c = np.cov(z.T)
    eig = np.clip(np.linalg.eigvalsh(c), 0, None)
    deff = eig.sum() ** 2 / (eig ** 2).sum()
    i1, i2 = g.integers(0, n, 60000), g.integers(0, n, 60000)
    r = np.linalg.norm(s[i1] - s[i2], axis=1)
    k = 1 - ((z[i1] - z[i2]) ** 2).sum(1) / (2 * var)
    bins = np.linspace(0, np.percentile(r, 95), 40)
    cen, kk = [], []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (r >= lo) & (r < hi)
        if m.sum() > 50:
            cen.append(r[m].mean()); kk.append(k[m].mean())
    cen, kk = np.array(cen), np.array(kk)
    f = lambda x, a, ell, b: a * np.exp(-x ** 2 / (2 * ell ** 2)) + b
    try:
        (a, ell, b), _ = curve_fit(f, cen, kk, p0=[1, 20, 0], maxfev=20000)
    except Exception:
        a, ell, b = np.nan, np.nan, np.nan
    # half-decay distance (model free): first r where k drops below (k(0)+k_inf)/2
    half = float(cen[np.argmax(kk < (kk[0] + kk[-5:].mean()) / 2)])
    return {'deff': float(deff), 'ell': float(abs(ell)), 'amp': float(a), 'floor': float(b), 'half': half,
            'curve': [cen.tolist(), kk.tolist()]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--task', default='tworoom')
    p.add_argument('--roots', default='/tmp/latent-wm-runs/scaling,/home/xiang/.cache/latent-wm-results/scaling')
    a = p.parse_args()
    data = GPUData(a.task, device='cuda', pixels_on='cpu')
    if a.task == 'tworoom':
        st = data.meta['proprio'][:, :2].astype(np.float64)
        key_fn = lambda idx: st[idx]
    elif a.task == 'pusht':
        st = data.meta['state'].astype(np.float64)
        key_fn = lambda idx: np.concatenate([st[idx, :4], 50 * np.stack([np.cos(st[idx, 4]), np.sin(st[idx, 4])], 1)], 1)
    runs = sorted(sum([glob.glob(f'{r}/{a.task}_*') for r in a.roots.split(',')], []))
    for rd in runs:
        for ck in sorted(Path(rd).glob('model_*.pt')):
            if os.environ.get('CKS') and ck.stem.split('_')[1] not in os.environ['CKS'].split(','):
                continue
            o = Path(rd) / 'eval' / f'kell_{ck.stem}.json'
            if o.exists():
                continue
            o.parent.mkdir(exist_ok=True)
            res = measure(str(ck), data, key_fn)
            o.write_text(json.dumps(res))
            print('%-40s %s deff %6.1f ell %6.2f half %6.1f amp %.2f floor %.2f' % (Path(rd).name, ck.stem, res['deff'], res['ell'], res['half'], res['amp'], res['floor']), flush=True)


if __name__ == '__main__':
    main()
