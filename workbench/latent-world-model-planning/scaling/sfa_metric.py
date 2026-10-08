"""Bandwidth / long-range fidelity of the slow-feature projected metric vs the full latent metric."""
import sys, json, numpy as np, torch
from scipy.stats import spearmanr
from eval_plan import sfa_basis, IMNET_MEAN, IMNET_STD, DATA
ck, task, ks = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
model = torch.load(ck, map_location='cuda', weights_only=False).eval()
meta = np.load(DATA / f'{task}_64' / 'meta.npz'); px = np.load(DATA / f'{task}_64' / 'pixels.npy', mmap_mode='r')
g = np.random.default_rng(1); idx = np.sort(g.choice(len(px), 12000, replace=False))
with torch.no_grad():
    zs = []
    for i in range(0, len(idx), 2048):
        x = torch.as_tensor(np.ascontiguousarray(px[idx[i:i+2048]]), device='cuda').permute(0,3,1,2).float().div_(255)
        x = ((x - IMNET_MEAN.cuda()) / IMNET_STD.cuda())[:, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            zs.append(model.encode({'pixels': x})['emb'][:, 0].float())
    z = torch.cat(zs)
s = meta['proprio'][idx, :2] if task == 'tworoom' else meta['state'][idx, :4]
i1, i2 = g.integers(0, len(idx), 40000), g.integers(0, len(idx), 40000)
r = np.linalg.norm(s[i1] - s[i2], axis=1)
def report(name, zz):
    d = np.linalg.norm(zz[i1] - zz[i2], axis=1)
    near = r < np.percentile(r, 20); far = r > np.percentile(r, 50)
    print('%-8s spearman all %.3f near %.3f far %.3f' % (name, spearmanr(d, r).statistic, spearmanr(d[near], r[near]).statistic, spearmanr(d[far], r[far]).statistic), flush=True)
report('full', z.cpu().numpy())
for k in ks:
    W = sfa_basis(model, task, k, 'cuda')
    report(f'sfa{k}', (z @ W).cpu().numpy())
