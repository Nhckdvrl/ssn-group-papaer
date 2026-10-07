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
    elif task == 'cube':
        st = np.concatenate([meta['qpos'], meta['qvel'], meta['privileged_block_0_pos'], meta['privileged_block_0_quat']], 1)
    else:
        st = meta['proprio' if (task == 'tworoom' or task.startswith('pmaze')) else 'state']
    g = np.random.default_rng(1000 + seed + offset)
    eligible = val_eps[ep_len[val_eps] > offset + 1]
    eps = g.choice(eligible, size=n, replace=len(eligible) < n)
    rows = []
    for e in eps:
        s = g.integers(0, ep_len[e] - offset - 1)
        i = ep_off[e] + s
        rows.append((int(e), int(s), st[i].astype(np.float64), st[i + offset].astype(np.float64)))
    return rows


class PMazeEnv:
    """OGBench pointmaze with the same fixed global top-down render as render_pmaze.py (goal marker hidden)."""

    def __init__(self, size):
        import sys as _s
        _s.argv = _s.argv[:1] + [size]
        import render_pmaze
        render_pmaze.SIZE = size
        self.u, self.r, self.cam = render_pmaze.make_renderer()
        self.u._terminate_at_goal = True

    def render(self):
        self.r.update_scene(self.u.data, camera=self.cam)
        return self.r.render()

    def step(self, a):
        return self.u.step(a)


def make_env(task):
    if task.startswith('pmaze'):
        return PMazeEnv(task[len('pmaze'):])
    import gymnasium as gym
    import stable_worldmodel  # noqa: F401
    if task == 'reacher':
        return gym.make('swm/ReacherDMControl-v0', task='qpos_match').unwrapped
    if task == 'cube':
        return gym.make('swm/OGBCube-v0', env_type='single', ob_type='states', width=224, height=224, multiview=False,
                        visualize_info=False, terminate_at_goal=True).unwrapped
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
    elif task.startswith('pmaze'):
        env.u.reset(seed=seed)
        env.u.set_state(goal[:2], np.zeros(2))
        goal_img = np.asarray(env.render()).copy()
        env.u.set_state(start[:2], np.zeros(2))
        env.u.set_goal(goal_xy=np.asarray(goal[:2], dtype=np.float64))
    elif task == 'cube':
        env.reset(seed=seed)
        env.set_state(goal[:21], np.zeros(20))
        goal_img = np.asarray(env.render()).copy()
        env.set_state(start[:21], start[21:41])
        env.set_target_pos(0, goal[41:44], goal[44:48])
    else:
        env.reset(seed=seed, options={'state': start, 'goal_state': goal})
        goal_img = env._goal
    return goal_img


def dist_info(env, task):
    if task == 'tworoom':
        return float(torch.norm(env.agent_position - env.target_position))
    if task == 'reacher':
        return float(np.abs(env.env.physics.data.qpos - env.env.task.target_qpos).max())
    if task.startswith('pmaze'):
        return float(np.linalg.norm(env.u.get_xy() - env.u.cur_goal_xy))
    if task == 'cube':
        return float(np.linalg.norm(env._data.joint('object_joint_0').qpos[:3] - env._data.mocap_pos[env._cube_target_mocap_ids[0]]))
    st = np.asarray(env._get_obs(), dtype=np.float64)
    _, d = env.eval_state(env.goal_state, st)
    return float(d)


def prep(imgs, res, dev):
    x = np.stack([cv2.resize(np.ascontiguousarray(im), (res, res), interpolation=cv2.INTER_AREA) for im in imgs])
    x = torch.as_tensor(x, device=dev).permute(0, 3, 1, 2).float().div_(255)
    x = (x - IMNET_MEAN.to(dev)) / IMNET_STD.to(dev)
    return x[:, None]  # (B,1,3,H,W)


@torch.no_grad()
def rollout_cost(model, emb0, goal, cand, chunk=8192, hist=3, proj=None):
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
        diff = emb[:, -1] - g0[i:i + chunk]
        if callable(proj):
            res.append(proj(diff))
            continue
        if proj is not None:
            diff = diff @ proj
        res.append(diff.pow(2).sum(-1))
    return torch.cat(res).view(B, S)


@torch.no_grad()
def cem(model, emb0, goal, H, A, S, iters, topk, gen, proj=None):
    B = emb0.shape[0]
    mean = torch.zeros(B, H, A, device=emb0.device)
    std = torch.ones(B, H, A, device=emb0.device)
    for _ in range(iters):
        cand = torch.randn(B, S, H, A, device=emb0.device, generator=gen) * std[:, None] + mean[:, None]
        cand[:, 0] = mean
        cost = rollout_cost(model, emb0, goal, cand, proj=proj)
        idx = cost.topk(topk, dim=1, largest=False).indices
        el = torch.gather(cand, 1, idx[..., None, None].expand(-1, -1, H, A))
        mean, std = el.mean(1), el.std(1, correction=0)
    return mean


@torch.no_grad()
def pca_basis(model, task, k, dev, n=20000, seed=0):
    """Top-k principal directions of encoder latents on training frames (low-frequency subspace)."""
    px = np.load(DATA / f'{task}_64' / 'pixels.npy', mmap_mode='r')
    idx = np.sort(np.random.default_rng(seed).choice(len(px), n, replace=False))
    zs = []
    for i in range(0, n, 2048):
        x = torch.as_tensor(np.ascontiguousarray(px[idx[i:i + 2048]]), device=dev).permute(0, 3, 1, 2).float().div_(255)
        x = ((x - IMNET_MEAN.to(dev)) / IMNET_STD.to(dev))[:, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            zs.append(model.encode({'pixels': x})['emb'][:, 0].float())
    z = torch.cat(zs)
    z = z - z.mean(0)
    U, S, V = torch.linalg.svd(z, full_matrices=False)
    return V[:k].T.contiguous()  # (D,k)


@torch.no_grad()
def sfa_basis(model, task, k, dev, n=20000, seed=0, lag=5):
    """Slow-feature directions of encoder latents: minimise E||W^T (z_{t+lag} - z_t)||^2 s.t. W^T Sigma W = I."""
    root = DATA / f'{task}_64'
    px = np.load(root / 'pixels.npy', mmap_mode='r')
    meta = np.load(root / 'meta.npz')
    off, ln = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
    g = np.random.default_rng(seed)
    eps = g.choice(len(ln), n, replace=True)
    t0 = (g.random(n) * np.maximum(ln[eps] - lag, 1)).astype(np.int64)
    a = off[eps] + t0
    b = a + lag
    def enc(idx):
        order = np.argsort(idx)
        zs = []
        for i in range(0, len(idx), 2048):
            j = idx[order[i:i + 2048]]
            x = torch.as_tensor(np.ascontiguousarray(px[j]), device=dev).permute(0, 3, 1, 2).float().div_(255)
            x = ((x - IMNET_MEAN.to(dev)) / IMNET_STD.to(dev))[:, None]
            with torch.autocast('cuda', dtype=torch.bfloat16):
                zs.append(model.encode({'pixels': x})['emb'][:, 0].float())
        z = torch.cat(zs)
        out = torch.empty_like(z); out[torch.as_tensor(order, device=dev)] = z
        return out
    za, zb = enc(a), enc(b)
    z = torch.cat([za, zb]); z = z - z.mean(0)
    C = z.T @ z / len(z) + 1e-5 * torch.eye(z.shape[1], device=dev)
    dz = zb - za
    Cd = dz.T @ dz / len(dz)
    L = torch.linalg.cholesky(C)
    Li = torch.linalg.inv(L)
    M = Li @ Cd @ Li.T
    ev, V = torch.linalg.eigh(M)  # ascending: slowest first
    W = Li.T @ V[:, :k]  # whitened slow directions
    return W.contiguous()


@torch.no_grad()
def metric_horizon(model, task, dev, frac=0.9, n=2000, seed=2, lags=(1, 2, 5, 10, 15, 25, 35, 50, 75, 100, 150), return_plateau=False):
    """Smallest temporal lag at which the median full-latent L2 distance reaches `frac` of its plateau
    (plateau = median at the largest available lag), measured on training trajectories."""
    root = DATA / f'{task}_64'
    px = np.load(root / 'pixels.npy', mmap_mode='r')
    meta = np.load(root / 'meta.npz')
    off, ln = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
    g = np.random.default_rng(seed)
    def enc(idx):
        o = np.argsort(idx); out = []
        for i in range(0, len(idx), 1024):
            x = torch.as_tensor(np.ascontiguousarray(px[idx[o[i:i + 1024]]]), device=dev).permute(0, 3, 1, 2).float().div_(255)
            x = ((x - IMNET_MEAN.to(dev)) / IMNET_STD.to(dev))[:, None]
            with torch.autocast('cuda', dtype=torch.bfloat16):
                out.append(model.encode({'pixels': x})['emb'][:, 0].float())
        z = torch.cat(out); r = torch.empty_like(z); r[torch.as_tensor(o, device=dev)] = z
        return r
    med = []
    for h in lags:
        okk = np.nonzero(ln > h + 1)[0]
        if len(okk) == 0:
            break
        eps = g.choice(okk, n)
        a = off[eps] + (g.random(n) * (ln[eps] - h - 1)).astype(np.int64)
        med.append((h, (enc(a) - enc(a + h)).norm(dim=-1).median().item()))
    plateau = med[-1][1]
    if return_plateau:
        return next(h for h, m in med if m >= frac * plateau), plateau
    return next(h for h, m in med if m >= frac * plateau)


@torch.no_grad()
def slow_threshold(model, task, W, dev, lag=25, n=4000, seed=1):
    """Median squared slow-feature distance between training frames `lag` env steps apart."""
    root = DATA / f'{task}_64'
    px = np.load(root / 'pixels.npy', mmap_mode='r')
    meta = np.load(root / 'meta.npz')
    off, ln = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
    g = np.random.default_rng(seed)
    ok = np.nonzero(ln > lag + 1)[0]
    eps = g.choice(ok, n)
    a = off[eps] + (g.random(n) * (ln[eps] - lag - 1)).astype(np.int64)
    def enc(idx):
        zs = []
        for i in range(0, len(idx), 1024):
            x = torch.as_tensor(np.ascontiguousarray(px[np.sort(idx[i:i + 1024])]), device=dev).permute(0, 3, 1, 2).float().div_(255)
            x = ((x - IMNET_MEAN.to(dev)) / IMNET_STD.to(dev))[:, None]
            with torch.autocast('cuda', dtype=torch.bfloat16):
                zs.append(model.encode({'pixels': x})['emb'][:, 0].float())
        return torch.cat(zs)
    o = np.argsort(a)
    a = a[o]
    za, zb = enc(a), enc(a + lag)
    return float(((za - zb) @ W).pow(2).sum(-1).median())


def run(ckpt, task, offset, n, samples, iters, topk, horizon, seed, res=64, frameskip=5, dev='cuda', pca=0, sfa=0, mix=0, gate=0, switch=0, auto=0, sat=0):
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
    adim = len(am)
    A = adim * frameskip
    proj = pca_basis(model, task, pca, dev) if pca else (sfa_basis(model, task, sfa, dev) if sfa else None)
    if sat:  # saturation rule: full L2 while the current-goal full-L2 distance is below 0.9 x its plateau, else slow features
        Wsat = sfa_basis(model, task, sat, dev)
        _, plateau = metric_horizon(model, task, dev, return_plateau=True)
        print('sat: full-L2 plateau', round(plateau, 3), flush=True)
    if auto:  # same as switch, threshold at the measured full-L2 metric horizon (no cap)
        switch, uncapped = auto, True
    else:
        uncapped = False
    if switch:  # slow-then-fast: slow-feature cost until the goal is within one planning horizon, then full L2
        Wsw = sfa_basis(model, task, switch, dev)
        mh = metric_horizon(model, task, dev)  # where the full L2 stops carrying ordering information
        thr = slow_threshold(model, task, Wsw, dev, lag=mh if uncapped else max(1, min(mh, horizon * frameskip)))
        print('switch: full-L2 metric horizon', mh, 'steps; slow threshold', round(thr, 3), flush=True)
    if gate:  # distance-gated multi-scale cost: slow-feature distance everywhere; full L2 switched on near the goal
        W = sfa_basis(model, task, gate, dev)
        D = W.shape[0]
        tau2 = 0.2 * gate  # slow features are whitened: random pairs have squared distance ~2k

        def proj(diff, W=W, D=D, tau2=tau2):
            ds = (diff @ W).pow(2).sum(-1)
            df = diff.pow(2).sum(-1) * (gate / D)
            return ds + torch.exp(-ds / tau2) * df
    if mix:  # multi-scale cost: full latent L2 (local precision) + slow-feature L2 (long range), equal far-field scale
        W = sfa_basis(model, task, mix, dev)
        D = W.shape[0]
        proj = torch.cat([W * (D / mix) ** 0.5, torch.eye(D, device=dev)], 1)
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
        if sat:
            near = ((e0 - g_emb[act_idx]).norm(dim=-1) < 0.9 * plateau).cpu().numpy()
            plan = torch.empty(len(act_idx), horizon, A, device=dev)
            for mask, pr in [(near, None), (~near, Wsat)]:
                if mask.any():
                    sel = torch.as_tensor(np.nonzero(mask)[0], device=dev)
                    plan[sel] = cem(model, e0[sel], g_emb[act_idx][sel], horizon, A, samples, iters, topk, gen, proj=pr)
        elif switch:
            near = (((e0 - g_emb[act_idx]) @ Wsw).pow(2).sum(-1) <= thr).cpu().numpy()
            plan = torch.empty(len(act_idx), horizon, A, device=dev)
            for mask, pr in [(near, None), (~near, Wsw)]:
                if mask.any():
                    sel = torch.as_tensor(np.nonzero(mask)[0], device=dev)
                    plan[sel] = cem(model, e0[sel], g_emb[act_idx][sel], horizon, A, samples, iters, topk, gen, proj=pr)
        else:
            plan = cem(model, e0, g_emb[act_idx], horizon, A, samples, iters, topk, gen, proj=proj)
        n_plans += 1
        acts = plan.cpu().numpy().reshape(len(act_idx), horizon * frameskip, adim) * asd + am
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
