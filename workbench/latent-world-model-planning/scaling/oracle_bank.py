"""Mechanism test for TwoRoom inverse scaling: geometry vs. model accuracy as optimization pressure.

For each checkpoint and each (start, goal) pair of a bank with true end frames:
  c_pred : planner cost with the model's own rollout  ||z_pred(final) - z_goal||^2
  c_or   : 'oracle-dynamics' cost: same encoder/cost, but the TRUE end frame is encoded
  geo    : true quality = geodesic distance from the true end position to the goal (path via door)
Reported separately for same-room and cross-room pairs:
  rank fidelity of each cost to geo (Spearman), agreement c_pred vs c_or,
  best-of-N (random candidates) geodesic distance of the selected candidate under c_pred / c_or.
If inverse scaling shows up under c_or too -> the latent geometry itself degrades with scale.
If c_or is size-independent but c_pred tracks c_or more closely for bigger models -> model accuracy
is acting as optimization pressure on a misaligned proxy.
"""
import argparse
import glob
import json
import os
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
import torch
from scipy.stats import spearmanr

from eval_plan import prep, rollout_cost

WALL, DOOR, HALF = 112.0, 49.0, 14.0


def geodesic(p, g):
    """p: (...,2), g: (2,). Wall separates state coordinate 0 at WALL; door spans coordinate 1 in DOOR±HALF
    (verified from the dataset: positions inside the wall band only occur for coord1 in ~[32,64])."""
    p = np.asarray(p, float)
    same = (p[..., 0] - WALL) * (g[0] - WALL) >= 0
    ys = np.linspace(DOOR - HALF + 4, DOOR + HALF - 4, 25)
    d = np.stack([np.stack([np.full_like(ys, WALL), ys], 1)])  # (1,25,2)
    via = (np.linalg.norm(p[..., None, :] - d, axis=-1) + np.linalg.norm(d - g, axis=-1)).min(-1)
    return np.where(same, np.linalg.norm(p - g, axis=-1), via)


@torch.no_grad()
def analyze(ckpt, b, Ns=(4, 16, 64), n_sub=500):
    model = torch.load(ckpt, map_location='cuda', weights_only=False).eval()
    M, K = b['dist'].shape
    H = int(b['H'])
    with torch.autocast('cuda', dtype=torch.bfloat16):
        zs = model.encode({'pixels': prep(list(b['start_px']), 64, 'cuda')})['emb'][:, 0].float()
        zg = model.encode({'pixels': prep(list(b['goal_px']), 64, 'cuda')})['emb'][:, 0].float()
        fp = b['final_px'].reshape(M * K, 64, 64, 3)
        zf = torch.cat([model.encode({'pixels': prep(list(fp[i:i + 2048]), 64, 'cuda')})['emb'][:, 0].float()
                        for i in range(0, len(fp), 2048)]).view(M, K, -1)
    c = torch.as_tensor(b['cands'], device='cuda').view(M, K, H, -1)
    c_pred = rollout_cost(model, zs, zg, c).cpu().numpy()
    c_or = ((zf - zg[:, None]) ** 2).sum(-1).cpu().numpy()
    goal = b['states'][:, 2:4]
    start = b['states'][:, :2]
    geo = np.stack([geodesic(b['final_state'][i][:, :2], goal[i]) for i in range(M)])
    cross = (start[:, 0] - WALL) * (goal[:, 0] - WALL) < 0
    rnd = np.nonzero(b['kind'] == 'random')[0]
    rng = np.random.default_rng(0)
    out = {}
    for name, sel in [('same', ~cross), ('cross', cross)]:
        idx = np.nonzero(sel)[0]
        o = {'n_pairs': int(len(idx))}
        o['sp_pred_geo'] = float(np.nanmean([spearmanr(c_pred[i, rnd], geo[i, rnd]).statistic for i in idx]))
        o['sp_or_geo'] = float(np.nanmean([spearmanr(c_or[i, rnd], geo[i, rnd]).statistic for i in idx]))
        o['sp_pred_or'] = float(np.nanmean([spearmanr(c_pred[i, rnd], c_or[i, rnd]).statistic for i in idx]))
        for N in Ns:
            a_p, a_o, a_g, a_r = [], [], [], []
            for i in idx:
                sub = np.stack([rng.choice(rnd, N, replace=False) for _ in range(n_sub)])
                g = geo[i, sub]
                a_p.append(g[np.arange(n_sub), c_pred[i, sub].argmin(1)].mean())
                a_o.append(g[np.arange(n_sub), c_or[i, sub].argmin(1)].mean())
                a_g.append(g.min(1).mean())
                a_r.append(g.mean())
            o[f'bon{N}_pred'], o[f'bon{N}_or'] = float(np.mean(a_p)), float(np.mean(a_o))
            o[f'bon{N}_best'], o[f'bon{N}_rand'] = float(np.mean(a_g)), float(np.mean(a_r))
        out[name] = o
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--bank', default='/home/xiang/.cache/latent-wm-results/banks/tworoom_off50f.npz')
    p.add_argument('--runs', nargs='+', required=True)
    p.add_argument('--ck', default='0060000')
    a = p.parse_args()
    b = dict(np.load(a.bank))
    for r in a.runs:
        ck = Path(r) / f'model_{a.ck}.pt'
        if not ck.exists():
            continue
        o = Path(r) / 'eval' / f'oracle_{Path(a.bank).stem}_{ck.stem}.json'
        if o.exists():
            res = json.loads(o.read_text())
        else:
            res = analyze(str(ck), b)
            o.write_text(json.dumps(res))
        print(Path(r).name, json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in res.items()}), flush=True)


if __name__ == '__main__':
    main()
