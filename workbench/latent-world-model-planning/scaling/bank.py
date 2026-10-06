"""Fixed candidate banks with simulated ground-truth outcomes, and model scoring on them.

build: for M held-out (start, goal) pairs, K candidate open-loop action sequences of H blocks
(H*frameskip env steps) in normalized action space: K_r random N(0,1) (CEM's first population),
the expert's own next actions, and the expert perturbed with noise sigma in {0.1, 0.3, 0.6}.
Each candidate is executed in the simulator from the start state; we store final true distance to
goal and whether the goal condition was met at the end / at any step.
score: for a model checkpoint, cost of every candidate (same rollout as the planner); metrics
saved per pair so that best-of-N curves and rank statistics can be computed later.
"""
import argparse
import json
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
from multiprocessing import Pool
from pathlib import Path

import numpy as np

DATA = Path(os.environ.get('LWM_DATA', '/tmp/latent-wm-data/lowres'))


def _sim(args):
    task, start, goal, acts, seed = args
    import torch
    torch.set_num_threads(1)
    from eval_plan import make_env, reset_env, dist_info
    env = make_env(task)
    out = []
    goal_img = None
    for k, a in enumerate(acts):
        g = reset_env(env, task, start, goal, seed)
        if k == 0:
            goal_img = g
            start_img = env.render()
        hit = False
        for x in a:
            _, _, term, _, _ = env.step(np.clip(x, -1, 1).astype(np.float32))
            hit = hit or bool(term)
        d = dist_info(env, task)
        if task == 'tworoom':
            end_ok = d < 16.0
        elif task == 'reacher':
            end_ok = d < 0.05
        else:
            st = np.asarray(env._get_obs(), dtype=np.float64)
            end_ok, _ = env.eval_state(env.goal_state, st)
        out.append((d, bool(end_ok), hit))
    return out, start_img, goal_img


def build(task, offset, M, K_r, H, seed, out):
    from eval_plan import eval_set
    meta = np.load(DATA / f'{task}_64' / 'meta.npz')
    act = meta['action'].astype(np.float64)
    am, asd = np.nanmean(act, 0), np.nanstd(act, 0)
    rows = eval_set(task, 64, M, offset, seed=seed)
    ep_off = meta['ep_offset'].astype(np.int64)
    rng = np.random.default_rng(seed + 7)
    fs = 5
    steps = H * fs
    jobs, cands = [], []
    for k, (e, s, start, goal) in enumerate(rows):
        i0 = ep_off[e] + s
        expert = act[i0:i0 + steps].copy()
        expert = np.nan_to_num((expert - am) / asd)
        if len(expert) < steps:
            expert = np.concatenate([expert, np.zeros((steps - len(expert), 2))])
        c = [rng.standard_normal((steps, 2)) for _ in range(K_r)]
        c.append(expert)
        for sig in [0.1, 0.3, 0.6]:
            c += [expert + sig * rng.standard_normal((steps, 2)) for _ in range(K_r // 4)]
        c = np.stack(c)  # (K, steps, 2) normalized
        cands.append(c)
        jobs.append((task, start, goal, c * asd + am, seed * 100000 + k))
    with Pool(8) as pool:
        res = pool.map(_sim, jobs)
    dist = np.array([[r[0] for r in rr[0]] for rr in res])
    end_ok = np.array([[r[1] for r in rr[0]] for rr in res])
    hit = np.array([[r[2] for r in rr[0]] for rr in res])
    start_px = np.stack([rr[1] for rr in res])
    goal_px = np.stack([rr[2] for rr in res])
    kind = np.array(['random'] * K_r + ['expert'] + [f'exp{s}' for s in [0.1, 0.3, 0.6] for _ in range(K_r // 4)])
    np.savez_compressed(out, cands=np.stack(cands).astype(np.float32), dist=dist, end_ok=end_ok, hit=hit,
                        start_px=start_px, goal_px=goal_px, kind=kind, episodes=np.array([[r[0], r[1]] for r in rows]),
                        H=H, offset=offset, act_mean=am, act_std=asd)
    print('built', out, dist.shape, 'expert end_ok', end_ok[:, K_r].mean(), 'random end_ok', end_ok[:, :K_r].mean())


def score(bank, ckpt, res, out):
    import torch
    from eval_plan import prep, rollout_cost
    b = np.load(bank)
    model = torch.load(ckpt, map_location='cuda', weights_only=False).eval()
    cfg_path = Path(ckpt).parent / 'config.json'
    if cfg_path.exists():
        res = json.loads(cfg_path.read_text()).get('res', res)
    H = int(b['H'])
    c = torch.as_tensor(b['cands'], device='cuda')  # (M,K,steps,2)
    M, K = c.shape[:2]
    c = c.view(M, K, H, -1)  # blocks of frameskip*2
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        e0 = model.encode({'pixels': prep(list(b['start_px']), res, 'cuda')})['emb'][:, 0].float()
        g = model.encode({'pixels': prep(list(b['goal_px']), res, 'cuda')})['emb'][:, 0].float()
    costs = rollout_cost(model, e0, g, c).cpu().numpy()
    np.savez_compressed(out, costs=costs)
    return costs


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')
    b = sub.add_parser('build')
    b.add_argument('--task'); b.add_argument('--offset', type=int, default=25); b.add_argument('--M', type=int, default=100)
    b.add_argument('--Kr', type=int, default=64); b.add_argument('--H', type=int, default=5); b.add_argument('--seed', type=int, default=0)
    b.add_argument('--out')
    s = sub.add_parser('score')
    s.add_argument('--bank'); s.add_argument('--ckpt'); s.add_argument('--res', type=int, default=64); s.add_argument('--out')
    a = p.parse_args()
    if a.cmd == 'build':
        build(a.task, a.offset, a.M, a.Kr, a.H, a.seed, a.out)
    else:
        score(a.bank, a.ckpt, a.res, a.out)


if __name__ == '__main__':
    main()
