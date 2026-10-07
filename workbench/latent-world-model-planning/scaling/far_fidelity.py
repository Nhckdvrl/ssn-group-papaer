"""Far-range metric fidelity of the latent L2 cost (TwoRoom): Spearman between ||z(s)-z(g)|| and the
geodesic distance (through the door) on pairs whose geodesic distance exceeds a threshold.
Writes <run>/eval/far_<ckpt>.json and prints it next to closed-loop success at offsets 50/75."""
import glob
import json
import os
import sys
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
import torch
from scipy.stats import spearmanr

from eval_plan import IMNET_MEAN, IMNET_STD, DATA
from oracle_bank import geodesic

meta = np.load(DATA / 'tworoom_64' / 'meta.npz')
px = np.load(DATA / 'tworoom_64' / 'pixels.npy', mmap_mode='r')
g = np.random.default_rng(3)
idx = np.sort(g.choice(len(px), 8000, replace=False))
S = meta['proprio'][idx, :2].astype(np.float64)
X = torch.as_tensor(np.ascontiguousarray(px[idx]))
i1, i2 = g.integers(0, len(idx), 40000), g.integers(0, len(idx), 40000)
geo = np.array([geodesic(S[a][None], S[b])[0] for a, b in zip(i1, i2)])


@torch.no_grad()
def far_fid(ck):
    model = torch.load(ck, map_location='cuda', weights_only=False).eval()
    zs = []
    for i in range(0, len(X), 2048):
        x = X[i:i + 2048].cuda().permute(0, 3, 1, 2).float().div_(255)
        x = ((x - IMNET_MEAN.cuda()) / IMNET_STD.cuda())[:, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            zs.append(model.encode({'pixels': x})['emb'][:, 0].float())
    z = torch.cat(zs).cpu().numpy()
    d = np.linalg.norm(z[i1] - z[i2], axis=1)
    out = {}
    for lo in [0, 30, 60, 90]:
        m = geo > lo
        out[f'sp_geo_gt{lo}'] = float(spearmanr(d[m], geo[m]).statistic)
    return out


if __name__ == '__main__':
    runs = sorted(glob.glob('/tmp/latent-wm-runs/scaling/tworoom_*') + glob.glob('/home/xiang/.cache/latent-wm-results/scaling/tworoom_*'))
    for rd in runs:
        ck = Path(rd) / 'model_0060000.pt'
        if not ck.exists():
            continue
        o = Path(rd) / 'eval' / 'far_model_0060000.json'
        r = json.loads(o.read_text()) if o.exists() else far_fid(str(ck))
        o.write_text(json.dumps(r))
        sr = {}
        for off in [25, 50, 75]:
            f = Path(rd) / 'eval' / f'0060000_off{off}_300x30_n200.json'
            if f.exists():
                sr[off] = json.loads(f.read_text())['success_rate']
        print('%-40s %s %s' % (Path(rd).name, ' '.join('%s %.3f' % (k[7:], v) for k, v in r.items()), sr), flush=True)
