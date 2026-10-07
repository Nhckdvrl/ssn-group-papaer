"""E23 theory check. For an embedding with covariance Sigma, the normalized kernel
K(s,s') = <phi(s)-mu, phi(s')-mu> / tr(Sigma) satisfies E[K^2] = tr(Sigma^2)/tr(Sigma)^2 = 1/D_eff exactly
(independent pairs), so by Markov  P(|K| >= kappa) <= 1 / (kappa^2 D_eff):
the fraction of state pairs whose latent L2 distance is below (1-kappa) of its random-pair level
cannot exceed 1/(kappa^2 D_eff). This script measures, per final checkpoint, D_eff, E[K^2] (identity check),
P(K >= kappa) and the bound, plus the same along trajectories at the lags used for the metric horizon.
Writes <run>/eval/kbound_model_0060000.json."""
import glob
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
import torch

from eval_plan import DATA, IMNET_MEAN, IMNET_STD

KAPPAS = (0.25, 0.5, 0.75)
LAGS = (1, 2, 5, 10, 15, 25, 35, 50, 75, 100)


@torch.no_grad()
def enc(model, px, idx):
    zs = []
    for i in range(0, len(idx), 2048):
        x = torch.as_tensor(np.ascontiguousarray(px[idx[i:i + 2048]]), device='cuda').permute(0, 3, 1, 2).float().div_(255)
        x = ((x - IMNET_MEAN.cuda()) / IMNET_STD.cuda())[:, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            zs.append(model.encode({'pixels': x})['emb'][:, 0].float())
    return torch.cat(zs)


def measure(ck, task):
    root = DATA / f'{task}_64'
    px = np.load(root / 'pixels.npy', mmap_mode='r')
    meta = np.load(root / 'meta.npz')
    off, ln = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
    g = np.random.default_rng(0)
    model = torch.load(ck, map_location='cuda', weights_only=False).eval()
    idx = np.sort(g.choice(len(px), 16000, replace=False))
    z = enc(model, px, idx)
    mu = z.mean(0)
    zc = z - mu
    C = zc.T @ zc / len(zc)
    tr = torch.trace(C)
    deff = float(tr ** 2 / (C ** 2).sum())
    a, b = g.integers(0, len(z), 200000), g.integers(0, len(z), 200000)
    keep = a != b
    K = ((zc[a[keep]] * zc[b[keep]]).sum(-1) / tr).cpu().numpy()
    out = {'deff': deff, 'EK2': float((K ** 2).mean()), 'inv_deff': 1 / deff,
           'P_K_ge': {str(k): float((K >= k).mean()) for k in KAPPAS},
           'bound': {str(k): min(1.0, 1 / (k * k * deff)) for k in KAPPAS}, 'traj': []}
    for h in LAGS:
        ok = np.nonzero(ln > h + 1)[0]
        if len(ok) == 0:
            break
        eps = g.choice(ok, 2000)
        s = off[eps] + (g.random(2000) * (ln[eps] - h - 1)).astype(np.int64)
        o = np.argsort(s)
        za, zb = enc(model, px, s[o]) - mu, enc(model, px, s[o] + h) - mu
        Kt = ((za * zb).sum(-1) / tr).cpu().numpy()
        out['traj'].append({'lag': h, 'K_median': float(np.median(Kt)), 'P_K_ge_0.5': float((Kt >= 0.5).mean())})
    return out


if __name__ == '__main__':
    pat = re.compile(r'^(?P<task>[a-z]+)_(XXS|XS|S|M|L)_ep0_s\d_st60000(sigreg_w[0-9.]+)?$')
    roots = sys.argv[1].split(',') if len(sys.argv) > 1 else ['/tmp/latent-wm-runs/scaling', '/home/xiang/.cache/latent-wm-results/scaling']
    for r in roots:
        for rd in sorted(glob.glob(f'{r}/*')):
            m = pat.match(Path(rd).name)
            ck = Path(rd) / 'model_0060000.pt'
            o = Path(rd) / 'eval' / 'kbound_model_0060000.json'
            if not m or not ck.exists() or o.exists() or not (DATA / f"{m['task']}_64").exists():
                continue
            res = measure(str(ck), m['task'])
            o.write_text(json.dumps(res))
            print(Path(rd).name, 'deff %.1f EK2 %.4f 1/deff %.4f' % (res['deff'], res['EK2'], res['inv_deff']),
                  'P(K>=.5) %.4f bound %.4f' % (res['P_K_ge']['0.5'], res['bound']['0.5']),
                  'traj K_med', [round(t['K_median'], 2) for t in res['traj']], flush=True)
