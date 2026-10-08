"""Why does the slow-feature cost get worse with model size on the visual PointMaze? (E23 diagnosis, POST-HOC)

For each final maze checkpoint, four measurements:
 A  closed-loop failures by start-goal geodesic distance (paired: same held-out episodes for every model)
 B  geometry: Spearman of latent distance (full / slow k=2,4,8) with maze geodesic and with straight-line
    distance; 'descent agreement' = for dataset steps (t -> t+5) that move along the geodesic toward a goal
    by >= 1 unit, how often the cost also decreases (and the converse for steps that move away)
 C  prediction error in the cost space: 25-step (5-block) open-loop rollout from a dataset frame with the
    logged actions; error of the predicted endpoint vs the encoded true endpoint, relative to the true
    start->end distance, for full latent and slow k=4
 D  candidate bank (simulated outcomes, offset 50): pick the min-cost candidate with (i) encoder of the
    TRUE final frame (geometry only), (ii) the planner's predicted rollout; geodesic of the chosen endpoint
Writes <run>/eval/mazediag_model_0060000.json."""
import glob
import json
import os
import re
import sys
from collections import deque
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
import torch
from scipy.stats import spearmanr

from eval_plan import DATA, IMNET_MEAN, IMNET_STD, PMazeEnv, eval_set, prep, rollout_cost, sfa_basis

TASK = 'pmazemedium'
BANK = '/home/xiang/.cache/latent-wm-results/banks/pmazemedium_off50.npz'


class Geo:
    def __init__(self):
        env = PMazeEnv('medium')
        u = env.u
        self.u, self.m = u, np.asarray(u.maze_map)
        free = [(i, j) for i in range(self.m.shape[0]) for j in range(self.m.shape[1]) if self.m[i, j] == 0]
        self.idx = {c: k for k, c in enumerate(free)}
        n = len(free)
        self.D = np.full((n, n), np.inf)
        for s, c in enumerate(free):
            self.D[s, s] = 0
            q = deque([c])
            while q:
                i, j = q.popleft()
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nb = (i + di, j + dj)
                    if nb in self.idx and self.D[s, self.idx[nb]] == np.inf:
                        self.D[s, self.idx[nb]] = self.D[s, self.idx[(i, j)]] + 1
                        q.append(nb)

    def cell(self, xy):
        i, j = self.u.xy_to_ij(xy)
        return self.idx.get((i, j), None)

    def __call__(self, a, b):
        ca, cb = self.cell(a), self.cell(b)
        e = float(np.linalg.norm(np.asarray(a) - np.asarray(b)))
        if ca is None or cb is None or ca == cb:
            return e
        return 4.0 * self.D[ca, cb] + 0.01 * e  # cell-graph geodesic (maze unit 4), straight line breaks ties


@torch.no_grad()
def encode(model, px):
    out = []
    for i in range(0, len(px), 2048):
        x = torch.as_tensor(np.ascontiguousarray(px[i:i + 2048]), device='cuda').permute(0, 3, 1, 2).float().div_(255)
        x = ((x - IMNET_MEAN.cuda()) / IMNET_STD.cuda())[:, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            out.append(model.encode({'pixels': x})['emb'][:, 0].float())
    return torch.cat(out)


def part_a(rd, geo):
    out = {}
    for mode in ['sfa', 'l2']:
        for off in [50, 100]:
            if mode == 'sfa':
                d = json.loads((rd / 'eval' / 'sfa_model_0060000.json').read_text()) if (rd / 'eval' / 'sfa_model_0060000.json').exists() else []
                r = next((x for x in d if x['offset'] == off and x['pca'] == 4), None)
            else:
                f = rd / 'eval' / f'0060000_off{off}_300x30_n200.json'
                r = json.loads(f.read_text()) if f.exists() else None
            if r is None:
                continue
            rows = eval_set(TASK, 64, 200, off)
            g = np.array([geo(s[:2], t[:2]) for _, _, s, t in rows])
            e = np.array([np.linalg.norm(s[:2] - t[:2]) for _, _, s, t in rows])
            suc = np.array(r['success'], bool)
            bins = [0, 8, 16, 24, 1e9]
            out[f'{mode}_off{off}'] = {
                'sr': float(suc.mean()),
                'sr_by_geodesic': {f'{lo}-{hi}': [float(suc[(g >= lo) & (g < hi)].mean()) if ((g >= lo) & (g < hi)).any() else None,
                                                  int(((g >= lo) & (g < hi)).sum())] for lo, hi in zip(bins[:-1], bins[1:])},
                'sr_detour': float(suc[g > 1.5 * e + 4].mean()) if (g > 1.5 * e + 4).any() else None,
                'sr_direct': float(suc[g <= 1.5 * e + 4].mean()),
                'success': suc.tolist()}
    return out


@torch.no_grad()
def part_bc(model, geo, cfg, Ws):
    meta = np.load(DATA / f'{TASK}_64' / 'meta.npz')
    px = np.load(DATA / f'{TASK}_64' / 'pixels.npy', mmap_mode='r')
    off, ln = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
    xy = meta['proprio'][:, :2].astype(np.float64)
    g = np.random.default_rng(0)
    # B: pairs
    idx = np.sort(g.choice(len(px), 6000, replace=False))
    z = encode(model, px[idx])
    i1, i2 = g.integers(0, len(idx), 30000), g.integers(0, len(idx), 30000)
    geod = np.array([geo(xy[idx[a]], xy[idx[b]]) for a, b in zip(i1, i2)])
    eucl = np.linalg.norm(xy[idx[i1]] - xy[idx[i2]], axis=1)
    far = geod > np.percentile(geod, 50)
    res = {'B': {}, 'C': {}}
    spaces = {'full': None, **{f'sfa{k}': W for k, W in Ws.items()}}
    for name, W in spaces.items():
        zz = z if W is None else z @ W
        d = (zz[torch.as_tensor(i1, device='cuda')] - zz[torch.as_tensor(i2, device='cuda')]).norm(dim=-1).cpu().numpy()
        res['B'][name] = {'sp_geo': float(spearmanr(d, geod).statistic), 'sp_euc': float(spearmanr(d, eucl).statistic),
                          'sp_geo_far': float(spearmanr(d[far], geod[far]).statistic),
                          'sp_euc_far': float(spearmanr(d[far], eucl[far]).statistic)}
    # descent agreement: steps t -> t+5 relative to random goals
    ok = np.nonzero(ln > 30)[0]
    eps = g.choice(ok, 3000)
    t = off[eps] + (g.random(3000) * (ln[eps] - 6)).astype(np.int64)
    gl = idx[g.integers(0, len(idx), 3000)]
    o = np.argsort(t); t = t[o]; gl = gl[o]
    za = encode(model, px[t]); zb = encode(model, px[t + 5]); zg = encode(model, px[np.sort(gl)])
    og = np.argsort(np.argsort(gl)); zg = zg[torch.as_tensor(og, device='cuda')]
    dgeo = np.array([geo(xy[b], xy[c]) - geo(xy[a], xy[c]) for a, b, c in zip(t, t + 5, gl)])
    toward, away = dgeo <= -1, dgeo >= 1
    for name, W in spaces.items():
        f = (lambda v: v) if W is None else (lambda v, W=W: v @ W)
        dc = ((f(zb) - f(zg)).norm(dim=-1) - (f(za) - f(zg)).norm(dim=-1)).cpu().numpy()
        res['B'][name]['descent_toward'] = float((dc[toward] < 0).mean())
        res['B'][name]['ascent_away'] = float((dc[away] > 0).mean())
        far_goal = np.array([geo(xy[a], xy[c]) for a, c in zip(t, gl)]) > 16
        res['B'][name]['descent_toward_far'] = float((dc[toward & far_goal] < 0).mean())
    # C: 25-step open-loop prediction error
    am, asd = np.array(cfg['act_mean']), np.array(cfg['act_std'])
    ok = np.nonzero(ln > 30)[0]
    eps = g.choice(ok, 2000)
    t = np.sort(off[eps] + (g.random(2000) * (ln[eps] - 27)).astype(np.int64))
    acts = np.stack([(meta['action'][s:s + 25] - am) / asd for s in t]).reshape(len(t), 5, -1).astype(np.float32)
    z0, z25 = encode(model, px[t]), encode(model, px[t + 25])
    emb = z0[:, None]
    a = torch.as_tensor(acts, device='cuda')
    with torch.autocast('cuda', dtype=torch.bfloat16):
        ae = model.action_encoder(a)
        for s in range(5):
            p = model.predict(emb[:, -3:], ae[:, max(0, s + 1 - 3):s + 1])[:, -1:]
            emb = torch.cat([emb, p.float()], 1)
    pred = emb[:, -1]
    for name, W in spaces.items():
        f = (lambda v: v) if W is None else (lambda v, W=W: v @ W)
        err = (f(pred) - f(z25)).norm(dim=-1); move = (f(z25) - f(z0)).norm(dim=-1)
        res['C'][name] = {'rel_err_median': float((err / move.clamp_min(1e-6)).median()),
                          'err_over_move_mean': float(err.mean() / move.mean())}
    return res


@torch.no_grad()
def part_d(model, geo, Ws):
    b = np.load(BANK)
    goals = b['states'][:, 2:4] if b['states'].shape[1] >= 4 else None
    out = {}
    zf = encode(model, b['final_px'].reshape(-1, 64, 64, 3)).view(100, 113, -1)
    zg = torch.cat([model.encode({'pixels': prep(b['goal_px'][i:i + 50], 64, 'cuda')})['emb'][:, 0].float() for i in range(0, 100, 50)])
    zs = torch.cat([model.encode({'pixels': prep(b['start_px'][i:i + 50], 64, 'cuda')})['emb'][:, 0].float() for i in range(0, 100, 50)])
    cand = torch.as_tensor(b['cands'].reshape(100, 113, 5, -1), device='cuda')
    fgeo = np.array([[geo(b['final_state'][i, k], goals[i]) for k in range(113)] for i in range(100)])
    best = fgeo.min(1)
    for name, W in {'full': None, **{f'sfa{k}': W for k, W in Ws.items()}}.items():
        f = (lambda v: v) if W is None else (lambda v, W=W: v @ W)
        c_true = (f(zf) - f(zg)[:, None]).norm(dim=-1).cpu().numpy()
        c_pred = rollout_cost(model, zs, zg, cand, proj=W).cpu().numpy()
        for tag, c in [('true_frames', c_true), ('predicted', c_pred)]:
            ch = fgeo[np.arange(100), c.argmin(1)]
            out[f'{name}_{tag}'] = {'geo_of_choice': float(ch.mean()), 'regret': float((ch - best).mean()),
                                    'sp_cost_geo': float(np.mean([spearmanr(c[i], fgeo[i]).statistic for i in range(100)]))}
    out['geo_best'] = float(best.mean())
    return out


if __name__ == '__main__':
    pat = re.compile(r'^pmazemedium_(XXS|XS|S|M|L)_ep0_s\d_st60000$')
    geo = Geo()
    runs = sorted(glob.glob('/tmp/latent-wm-runs/scaling/pmazemedium_*') + glob.glob('/home/xiang/.cache/latent-wm-results/scaling/pmazemedium_*'))
    for rd in map(Path, runs):
        ck = rd / 'model_0060000.pt'
        o = rd / 'eval' / 'mazediag_model_0060000.json'
        if not pat.match(rd.name) or not ck.exists() or (o.exists() and '--force' not in sys.argv):
            continue
        cfg = json.loads((rd / 'config.json').read_text())
        model = torch.load(ck, map_location='cuda', weights_only=False).eval()
        Ws = {k: sfa_basis(model, TASK, k, 'cuda') for k in (2, 4, 8)}
        res = {'A': part_a(rd, geo), **part_bc(model, geo, cfg, Ws), 'D': part_d(model, geo, Ws)}
        o.write_text(json.dumps(res))
        B, C, D = res['B'], res['C'], res['D']
        print(rd.name, {k: res['A'][k]['sr'] for k in res['A']}, flush=True)
        for name in ['full', 'sfa2', 'sfa4', 'sfa8']:
            print('   %-5s geo %.2f euc %.2f geo_far %.2f | descent %.2f far %.2f ascent %.2f | pred err %.2f | bank regret true %.1f pred %.1f'
                  % (name, B[name]['sp_geo'], B[name]['sp_euc'], B[name]['sp_geo_far'], B[name]['descent_toward'],
                     B[name]['descent_toward_far'], B[name]['ascent_away'], C[name]['err_over_move_mean'],
                     D[f'{name}_true_frames']['regret'], D[f'{name}_predicted']['regret']), flush=True)
        del model
        torch.cuda.empty_cache()
