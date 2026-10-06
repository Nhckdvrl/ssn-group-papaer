"""Model-agnostic prediction diagnostics for a checkpoint (eval mode, as used by the planner).

On held-out windows (val episodes, split_seed 0):
  nmse_k: open-loop k-step latent error normalized by target variance (1 - R^2), k=1..4 blocks
  probe_r2: ridge probe latent -> true state (fit on train windows, scored on val encoder latents)
  probe_pred_err_k: physical error of the probe applied to k-step predicted latents vs true state
                    (state units: TwoRoom agent position px; PushT agent+block position px)
  act_sens: mean ||pred(a) - pred(a')|| / mean ||tgt - mean|| for random action swaps (1 step)
  eff_dim: participation ratio of the latent covariance
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
import torch

from wm import GPUData


def ridge(X, Y, lam=1e-3):
    X1 = np.concatenate([X, np.ones((len(X), 1))], 1)
    A = X1.T @ X1 + lam * len(X) * np.eye(X1.shape[1])
    return np.linalg.solve(A, X1.T @ Y)


def apply(W, X):
    return np.concatenate([X, np.ones((len(X), 1))], 1) @ W


@torch.no_grad()
def analyze(ckpt, data, n_val=4096, n_train=8192, seed=0):
    model = torch.load(ckpt, map_location='cuda', weights_only=False).eval()
    task = data.task
    key = 'proprio' if task == 'tworoom' else 'state'
    st = torch.as_tensor(data.meta[key][:, :4 if task == 'pusht' else 2].astype(np.float32), device='cuda')
    gen = torch.Generator(device='cuda').manual_seed(seed)

    def windows(val, n):
        pool = data.val_starts if val else data.train_starts
        s = pool[torch.randint(len(pool), (n,), device='cuda', generator=gen)]
        fidx = s[:, None] + torch.arange(data.T, device='cuda')[None] * data.fs
        px = data.pixels[data.remap[fidx]].permute(0, 1, 4, 2, 3).float().div_(255)
        B = px.shape[0]
        px = ((px.flatten(0, 1) - data.mean) / data.std).view(B, data.T, 3, px.shape[-2], px.shape[-1])
        aidx = s[:, None] + torch.arange(data.T * data.fs, device='cuda')[None]
        act = data.actions[aidx].view(B, data.T, -1)
        return px, act, st[fidx]

    def encode(px):
        out = []
        for i in range(0, len(px), 512):
            with torch.autocast('cuda', dtype=torch.bfloat16):
                out.append(model.encode({'pixels': px[i:i + 512]})['emb'].float())
        return torch.cat(out)

    # probe fit on train-window encoder latents
    pxt, _, stt = windows(False, n_train)
    et = encode(pxt).flatten(0, 1).cpu().numpy()
    W = ridge(et, stt.flatten(0, 1).cpu().numpy())
    px, act, stv = windows(True, n_val)
    emb = encode(px)  # (B,T,D)
    ev = emb.flatten(0, 1).cpu().numpy()
    sv = stv.flatten(0, 1).cpu().numpy()
    probe_r2 = 1 - ((apply(W, ev) - sv) ** 2).sum(0) / ((sv - sv.mean(0)) ** 2).sum(0)
    # open-loop rollout from frame 0 with true actions
    hist = [emb[:, :1]]
    preds = []
    with torch.autocast('cuda', dtype=torch.bfloat16):
        ae = model.action_encoder(act)
        cur = emb[:, :1]
        for t in range(data.T - 1):
            p = model.predict(cur[:, -3:], ae[:, max(0, t + 1 - 3):t + 1])[:, -1:].float()
            cur = torch.cat([cur, p], 1)
            preds.append(p[:, 0])
    var = ((emb - emb.flatten(0, 1).mean(0)) ** 2).sum(-1).mean().item()
    out = {'ckpt': str(ckpt), 'probe_r2': probe_r2.tolist(), 'latent_var': var}
    for k, p in enumerate(preds, 1):
        tgt = emb[:, k]
        out[f'nmse_{k}'] = ((p - tgt) ** 2).sum(-1).mean().item() / var
        phys = np.linalg.norm(apply(W, p.cpu().numpy())[:, :2] - stv[:, k, :2].cpu().numpy(), axis=-1)
        out[f'probe_pred_err_{k}'] = float(phys.mean())
        if task == 'pusht':
            physb = np.linalg.norm(apply(W, p.cpu().numpy())[:, 2:4] - stv[:, k, 2:4].cpu().numpy(), axis=-1)
            out[f'probe_pred_err_block_{k}'] = float(physb.mean())
    # probe error on true encoder latents (floor)
    out['probe_enc_err'] = float(np.linalg.norm(apply(W, emb[:, 1].cpu().numpy())[:, :2] - stv[:, 1, :2].cpu().numpy(), axis=-1).mean())
    # action sensitivity: swap actions within batch at step 0
    perm = torch.randperm(len(act), device='cuda', generator=gen)
    with torch.autocast('cuda', dtype=torch.bfloat16):
        p1 = model.predict(emb[:, :1], ae[:, :1])[:, -1].float()
        p2 = model.predict(emb[:, :1], ae[perm][:, :1])[:, -1].float()
    out['act_sens'] = ((p1 - p2) ** 2).sum(-1).mean().item() / var
    # latent-distance vs true-distance curve on random pairs of held-out encoder latents
    rng = np.random.default_rng(seed)
    i1, i2 = rng.integers(0, len(ev), 20000), rng.integers(0, len(ev), 20000)
    ld = np.linalg.norm(ev[i1] - ev[i2], axis=1) / np.sqrt(2 * var)
    td = np.linalg.norm(sv[i1, :2] - sv[i2, :2], axis=1)
    from scipy.stats import spearmanr
    out['dist_spearman'] = float(spearmanr(ld, td).statistic)
    bins = np.quantile(td, np.linspace(0, 1, 11))
    out['dist_curve'] = [[float(td[(td >= lo) & (td < hi)].mean()), float(ld[(td >= lo) & (td < hi)].mean())]
                         for lo, hi in zip(bins[:-1], bins[1:])]
    near = td < np.quantile(td, 0.2)
    out['dist_spearman_near'] = float(spearmanr(ld[near], td[near]).statistic)
    out['dist_spearman_far'] = float(spearmanr(ld[~near], td[~near]).statistic)
    c = np.cov(ev.T)
    eig = np.clip(np.linalg.eigvalsh(c), 0, None)
    out['eff_dim'] = float(eig.sum() ** 2 / (eig ** 2).sum())
    out['latent_dim'] = int(ev.shape[1])
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runs', nargs='+', required=True)
    a = p.parse_args()
    cache = {}
    for r in a.runs:
        r = Path(r)
        cfg = json.loads((r / 'config.json').read_text())
        if cfg['task'] not in cache:
            cache[cfg['task']] = GPUData(cfg['task'], res=cfg.get('res', 64), device='cuda')
        data = cache[cfg['task']]
        for ck in sorted(r.glob('model_*.pt')):
            o = r / 'eval' / f'diag_{ck.stem}.json'
            if o.exists():
                continue
            o.parent.mkdir(exist_ok=True)
            res = analyze(ck, data)
            o.write_text(json.dumps(res))
            print(r.name, ck.stem, {k: round(v, 4) if isinstance(v, float) else v for k, v in res.items() if k in
                                     ('nmse_1', 'nmse_3', 'probe_pred_err_1', 'probe_pred_err_3', 'act_sens', 'eff_dim')}, flush=True)


if __name__ == '__main__':
    main()
