"""Distance growth vs temporal lag on training trajectories: full latent L2 vs slow-feature (k) distance."""
import sys, numpy as np, torch
from eval_plan import sfa_basis, IMNET_MEAN, IMNET_STD, DATA
ck, task, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
model = torch.load(ck, map_location='cuda', weights_only=False).eval()
W = sfa_basis(model, task, k, 'cuda')
root = DATA / f'{task}_64'; px = np.load(root / 'pixels.npy', mmap_mode='r'); meta = np.load(root / 'meta.npz')
off, ln = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
g = np.random.default_rng(5)
lags = [1, 2, 5, 10, 15, 25, 35, 50, 75, 100, 150, 200]
@torch.no_grad()
def enc(idx):
    o = np.argsort(idx); out = []
    for i in range(0, len(idx), 1024):
        x = torch.as_tensor(np.ascontiguousarray(px[idx[o[i:i+1024]]]), device='cuda').permute(0,3,1,2).float().div_(255)
        x = ((x - IMNET_MEAN.cuda()) / IMNET_STD.cuda())[:, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            out.append(model.encode({'pixels': x})['emb'][:, 0].float())
    z = torch.cat(out); r = torch.empty_like(z); r[torch.as_tensor(o, device='cuda')] = z; return r
rows = []
for h in lags:
    okk = np.nonzero(ln > h + 1)[0]
    if len(okk) == 0: continue
    eps = g.choice(okk, 2000); a = off[eps] + (g.random(2000) * (ln[eps] - h - 1)).astype(np.int64)
    za, zb = enc(a), enc(a + h)
    df = (za - zb).norm(dim=-1); ds = ((za - zb) @ W).norm(dim=-1)
    rows.append((h, df.median().item(), ds.median().item()))
f0, s0 = rows[-1][1], rows[-1][2]
print(task, 'lag | full L2 (rel. to max lag) | slow (rel.)')
for h, f, s in rows: print('%4d  %.2f  %.2f' % (h, f / f0, s / s0))
