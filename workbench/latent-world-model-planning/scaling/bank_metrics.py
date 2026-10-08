"""Score checkpoints on fixed candidate banks and compute ranking / best-of-N metrics.

Per (checkpoint, bank): costs (M,K) saved to <run>/eval/bank_<bank>_<ckpt>.npz and metrics json:
  spearman_all: mean over pairs of Spearman(cost, true final distance) over all K candidates
  spearman_random: same within the random population only (CEM's first iteration)
  expert_top1: fraction of pairs where the expert sequence has the lowest cost among all K
  expert_pct: mean percentile rank of the expert (0 = best)
  bon_sel[N], bon_oracle[N], bon_rand[N]: best-of-N over random candidates — mean true distance of the
     model-selected / truly-best / random candidate among N random draws (500 subsets per pair)
  bon_succ_sel[N], bon_succ_oracle[N]: same for end-of-sequence goal success
"""
import argparse
import glob
import json
import os
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

NS = [1, 2, 4, 8, 16, 32, 64]


def metrics(costs, b, n_sub=500, seed=0):
    dist, ok, kind = b['dist'], b['end_ok'].astype(float), b['kind']
    rnd = np.nonzero(kind == 'random')[0]
    ex = int(np.nonzero(kind == 'expert')[0][0])
    M = costs.shape[0]
    sp_all = np.nanmean([spearmanr(costs[i], dist[i]).statistic for i in range(M)])
    sp_r = np.nanmean([spearmanr(costs[i, rnd], dist[i, rnd]).statistic for i in range(M)])
    ranks = (costs < costs[:, ex:ex + 1]).sum(1)
    out = {'spearman_all': float(sp_all), 'spearman_random': float(sp_r),
           'expert_top1': float((ranks == 0).mean()), 'expert_pct': float((ranks / (costs.shape[1] - 1)).mean())}
    rng = np.random.default_rng(seed)
    for N in NS:
        sel, ora, rr, ssel, sora = [], [], [], [], []
        for i in range(M):
            sub = np.stack([rng.choice(rnd, N, replace=False) for _ in range(n_sub)])
            c, d, o = costs[i, sub], dist[i, sub], ok[i, sub]
            a = c.argmin(1)
            sel.append(d[np.arange(n_sub), a].mean()); ssel.append(o[np.arange(n_sub), a].mean())
            ora.append(d.min(1).mean()); sora.append(o.max(1).mean()); rr.append(d.mean())
        out[f'bon_sel_{N}'] = float(np.mean(sel)); out[f'bon_oracle_{N}'] = float(np.mean(ora))
        out[f'bon_rand_{N}'] = float(np.mean(rr))
        out[f'bon_succ_sel_{N}'] = float(np.mean(ssel)); out[f'bon_succ_oracle_{N}'] = float(np.mean(sora))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runs', nargs='+', required=True)
    p.add_argument('--banks', default='/home/xiang/.cache/latent-wm-results/banks')
    a = p.parse_args()
    from bank import score
    for r in a.runs:
        r = Path(r)
        task = json.loads((r / 'config.json').read_text())['task']
        for bf in sorted(glob.glob(f'{a.banks}/{task}_off*.npz')):
            bname = Path(bf).stem
            b = np.load(bf)
            for ck in sorted(r.glob('model_*.pt')):
                if os.environ.get('CKS') and ck.stem.split('_')[1] not in os.environ['CKS'].split(','):
                    continue
                o = r / 'eval' / f'bank_{bname}_{ck.stem}.json'
                if o.exists():
                    continue
                o.parent.mkdir(exist_ok=True)
                costs = score(bf, str(ck), 64, str(o.with_suffix('.npz')))
                m = metrics(costs, b)
                o.write_text(json.dumps(m))
                print(r.name, bname, ck.stem, {k: round(m[k], 3) for k in ['spearman_all', 'spearman_random', 'expert_top1', 'bon_sel_64', 'bon_oracle_64', 'bon_rand_64']}, flush=True)


if __name__ == '__main__':
    main()
