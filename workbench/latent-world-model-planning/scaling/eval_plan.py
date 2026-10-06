"""Batched closed-loop CEM evaluation of a LeWM-family checkpoint on held-out episodes.

Semantics follow stable-worldmodel CEMSolver + LeWM eval: goal = dataset state `offset` env steps
after the start state of a held-out episode; horizon H action blocks of `frameskip` env steps;
receding horizon = H (execute the whole plan, then replan); first candidate = current mean;
elites update mean/std; cost = squared L2 between final predicted latent and goal latent;
eval budget = 2 * offset env steps; success = env termination (TwoRoom dist<16, PushT pose).
"""
import argparse
import json
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import time
from pathlib import Path

os.environ.setdefault('MUJOCO_GL', 'egl')
import cv2
import numpy as np
import torch
torch.set_num_threads(2)

from wm import IMNET_MEAN, IMNET_STD  # noqa: F401  (also puts vendor/le-wm on sys.path)

DATA = Path(os.environ.get('LWM_DATA', '/tmp/latent-wm-data/lowres'))


def eval_set(task, res, n, offset, seed=0, split_seed=0, val_frac=0.05):
    meta = np.load(DATA / f'{task}_{res}' / 'meta.npz')
    ep_off, ep_len = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
    rng = np.random.default_rng(split_seed)
    perm = rng.permutation(len(ep_len))
    val_eps = np.sort(perm[:int(round(val_frac * len(ep_len)))])
    if task == 'reacher':
        st = np.concatenate([meta['qpos'], meta['qvel']], 1)
    else:
        st = meta['proprio' if task == 'tworoom' else 'state']
    g = np.random.default_rng(1000 + seed + offset)
    eligible = val_eps[ep_len[val_eps] > offset + 1]
    eps = g.choice(eligible, size=n, replace=len(eligible) < n)
    rows = []
    for e in eps:
        s = g.integers(0, ep_len[e] - offset - 1)
        i = ep_off[e] + s
        rows.append((int(e), int(s), st[i].astype(np.float64), st[i + offset].astype(np.float64)))
    return rows


def make_env(task):
    import gymnasium as gym
    import stable_worldmodel  # noqa: F401
    if task == 'reacher':
        return gym.make('swm/ReacherDMControl-v0', task='qpos_match').unwrapped
    name = 'swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1'
    return gym.make(name, render_mode='rgb_array').unwrapped


def reset_env(env, task, start, goal, seed):
    if task == 'tworoom':
        env.reset(seed=seed)
        env._set_state(start.astype(np.float32))
        env._set_goal_state(goal.astype(np.float32))
        goal_img = env._target_img.cpu().numpy().transpose(1, 2, 0)
    elif task == 'reacher':
        nq = len(start) // 2
        env.reset(seed=seed, options={'target_qpos': goal[:nq]})
        env.set_state(goal[:nq], np.zeros(nq))
        goal_img = np.asarray(env.render()).copy()
        env.set_state(start[:nq], start[nq:])
    else:
        env.reset(seed=seed, options={'state': start, 'goal_state': goal})
        goal_img = env._goal
    return goal_img


def dist_info(env, task):
    if task == 'tworoom':
        return float(torch.norm(env.agent_position - env.target_position))
    if task == 'reacher':
        return float(np.abs(env.env.physics.data.qpos - env.env.task.target_qpos).max())
    st = np.asarray(env._get_obs(), dtype=np.float64)
    _, d = env.eval_state(env.goal_state, st)
    return float(d)


def prep(imgs, res, dev):
    x = np.stack([cv2.resize(np.ascontiguousarray(im), (res, res), interpolation=cv2.INTER_AREA) for im in imgs])
    x = torch.as_tensor(x, device=dev).permute(0, 3, 1, 2).float().div_(255)
    x = (x - IMNET_MEAN.to(dev)) / IMNET_STD.to(dev)
    return x[:, None]  # (B,1,3,H,W)


@torch.no_grad()
def rollout_cost(model, emb0, goal, cand, chunk=8192, hist=3):
    """emb0 (B,D), goal (B,D), cand (B,S,H,A) -> cost (B,S)."""
    B, S, H, A = cand.shape
    out = torch.empty(B, S, device=cand.device)
    flat = cand.reshape(B * S, H, A)
    e0 = emb0[:, None].expand(B, S, -1).reshape(B * S, -1)
    g0 = goal[:, None].expand(B, S, -1).reshape(B * S, -1)
    res = []
    for i in range(0, B * S, chunk):
        a = flat[i:i + chunk]
        emb = e0[i:i + chunk, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            act_emb = model.action_encoder(a)
            for t in range(H):
                pred = model.predict(emb[:, -hist:], act_emb[:, max(0, t + 1 - hist):t + 1])[:, -1:]
                emb = torch.cat([emb, pred.float()], 1)
        res.append((emb[:, -1] - g0[i:i + chunk]).pow(2).sum(-1))
    return torch.cat(res).view(B, S)


@torch.no_grad()
def cem(model, emb0, goal, H, A, S, iters, topk, gen):
    B = emb0.shape[0]
    mean = torch.zeros(B, H, A, device=emb0.device)
    std = torch.ones(B, H, A, device=emb0.device)
    for _ in range(iters):
        cand = torch.randn(B, S, H, A, device=emb0.device, generator=gen) * std[:, None] + mean[:, None]
        cand[:, 0] = mean
        cost = rollout_cost(model, emb0, goal, cand)
        idx = cost.topk(topk, dim=1, largest=False).indices
        el = torch.gather(cand, 1, idx[..., None, None].expand(-1, -1, H, A))
        mean, std = el.mean(1), el.std(1, correction=0)
    return mean


def run(ckpt, task, offset, n, samples, iters, topk, horizon, seed, res=64, frameskip=5, dev='cuda'):
    cfg_path = Path(ckpt).parent / 'config.json'
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text())
        am, asd = np.array(cfg['act_mean']), np.array(cfg['act_std'])
        res = cfg.get('res', res)
    else:  # released checkpoint: dataset column statistics
        act = np.load(DATA / f'{task}_64' / 'meta.npz')['action'].astype(np.float64)
        am, asd = np.nanmean(act, 0), np.nanstd(act, 0)
    model = torch.load(ckpt, map_location=dev, weights_only=False).eval()
    rows = eval_set(task, 64, n, offset, seed=seed)
    envs = [make_env(task) for _ in rows]
    goals = [reset_env(env, task, r[2], r[3], seed=seed * 100000 + k) for k, (env, r) in enumerate(zip(envs, rows))]
    A = 2 * frameskip
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        g_emb = model.encode({'pixels': prep(goals, res, dev)})['emb'][:, 0].float()
    done = np.zeros(len(rows), bool)
    success = np.zeros(len(rows), bool)
    steps = np.zeros(len(rows), int)
    budget = 2 * offset
    gen = torch.Generator(device=dev).manual_seed(seed)
    t0 = time.time()
    n_plans = 0
    while not done.all() and steps.max() < budget:
        act_idx = np.nonzero(~done)[0]
        imgs = [envs[k].render() for k in act_idx]
        with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
            e0 = model.encode({'pixels': prep(imgs, res, dev)})['emb'][:, 0].float()
        plan = cem(model, e0, g_emb[act_idx], horizon, A, samples, iters, topk, gen)
        n_plans += 1
        acts = plan.cpu().numpy().reshape(len(act_idx), horizon * frameskip, 2) * asd + am
        for j, k in enumerate(act_idx):
            for a in acts[j]:
                if steps[k] >= budget:
                    break
                _, _, term, trunc, _ = envs[k].step(np.clip(a, -1, 1).astype(np.float32))
                steps[k] += 1
                if term:
                    success[k] = True
                    done[k] = True
                    break
            if steps[k] >= budget:
                done[k] = True
    final = [dist_info(env, task) for env in envs]
    return {'ckpt': str(ckpt), 'task': task, 'offset': offset, 'n': len(rows), 'samples': samples,
            'iters': iters, 'topk': topk, 'horizon': horizon, 'seed': seed,
            'success': success.tolist(), 'steps': steps.tolist(), 'final_dist': final,
            'episodes': [[r[0], r[1]] for r in rows], 'success_rate': float(success.mean()),
            'seconds': time.time() - t0, 'n_plans': n_plans}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt', required=True)
    p.add_argument('--task', required=True)
    p.add_argument('--offsets', default='25')
    p.add_argument('--n', type=int, default=100)
    p.add_argument('--budgets', default='300x30')  # samplesxiters, comma separated
    p.add_argument('--topk', type=int, default=30)
    p.add_argument('--horizon', type=int, default=5)
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--res', type=int, default=64)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    out = Path(a.out)
    results = json.loads(out.read_text()) if out.exists() else []
    have = {(r['offset'], r['samples'], r['iters'], r['seed']) for r in results}
    for off in [int(x) for x in a.offsets.split(',')]:
        for b in a.budgets.split(','):
            s, it = [int(x) for x in b.split('x')]
            if (off, s, it, a.seed) in have:
                continue
            r = run(a.ckpt, a.task, off, a.n, s, it, min(a.topk, s // 2), a.horizon, a.seed, res=a.res)
            results.append(r)
            out.write_text(json.dumps(results))
            print(json.dumps({k: r[k] for k in ['offset', 'samples', 'iters', 'success_rate', 'seconds']}), flush=True)


if __name__ == '__main__':
    main()
