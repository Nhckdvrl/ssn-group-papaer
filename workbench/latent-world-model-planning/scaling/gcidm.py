"""Amortized controller on a frozen world-model latent: Goal-Conditioned IDM (Nguyen et al. 2605.08732).

Official architecture (vendor/gc-idm/idm/model.py): 3x512 MLP on [z_t, z_goal], AdaLN-Zero horizon
modulation, MSE to the next action block. Here: action block = frameskip(5) env steps (same unit as
the planner), goals sampled 1..max_h env steps ahead in the same training episode, embeddings from
the world model encoder in eval mode (exactly what the controller sees at test time).
Closed-loop eval: same held-out (start, goal) pairs, same budget, re-encode after every block.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor' / 'gc-idm'))
from idm.model import GoalConditionedIDM, IDMConfig  # noqa: E402

from wm import GPUData  # noqa: E402
from eval_plan import eval_set, make_env, reset_env, dist_info, prep  # noqa: E402


@torch.no_grad()
def encode_all(model, data):
    N = data.pixels.shape[0]
    out = torch.empty(N, model.projector.net[-1].out_features if hasattr(model.projector, 'net') else 192,
                      device='cuda', dtype=torch.float32)
    for i in range(0, N, 2048):
        px = data.pixels[i:i + 2048].to('cuda', non_blocking=True).permute(0, 3, 1, 2).float().div_(255)
        px = ((px - data.mean) / data.std)[:, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            out[i:i + 2048] = model.encode({'pixels': px})['emb'][:, 0].float()
    return out


def train(ckpt, steps=20000, max_h=None, bs=8192, lr=3e-4, seed=0):
    cfg = json.loads((Path(ckpt).parent / 'config.json').read_text())
    if max_h is None:  # same protocol as before for the original tasks; long-range mazes need 200
        max_h = 200 if cfg['task'].startswith('pmaze') else 100
    data = GPUData(cfg['task'], res=cfg.get('res', 64), device='cuda', pixels_on='cpu')
    wm = torch.load(ckpt, map_location='cuda', weights_only=False).eval()
    z = encode_all(wm, data)  # indexed by remapped frame index
    meta = data.meta
    ep_off, ep_len = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
    fs = data.fs
    # valid (i, ep_end) pairs on training episodes
    idx, ends = [], []
    for e in data.train_eps:
        L = ep_len[e]
        if L > fs + 1:
            i = ep_off[e] + np.arange(L - fs)
            idx.append(i)
            ends.append(np.full(len(i), ep_off[e] + L - 1))
    idx = torch.as_tensor(np.concatenate(idx), device='cuda')
    ends = torch.as_tensor(np.concatenate(ends), device='cuda')
    torch.manual_seed(seed)
    D = z.shape[1]
    net = GoalConditionedIDM(IDMConfig(embed_dim=D, action_dim=data.actions.shape[-1], frameskip=fs, max_horizon=max_h)).cuda()
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps, eta_min=lr / 100)
    gen = torch.Generator(device='cuda').manual_seed(seed)
    t0 = time.time()
    for s in range(steps):
        k = torch.randint(len(idx), (bs,), device='cuda', generator=gen)
        i, end = idx[k], ends[k]
        span = torch.clamp(end - i, max=max_h)
        h = 1 + (torch.rand(bs, device='cuda', generator=gen) * span).long().clamp(max=span - 1)
        g = i + h
        a = data.actions[i[:, None] + torch.arange(fs, device='cuda')[None]].reshape(bs, -1)
        pred = net(z[data.remap[i]], z[data.remap[g]], h)
        loss = (pred - a).pow(2).mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step(); sched.step()
        if s % 5000 == 0:
            print('gcidm', s, round(loss.item(), 4), round(time.time() - t0), flush=True)
    net.eval()
    return net, wm, data


@torch.no_grad()
def closed_loop(net, wm, data, task, offset, n, seed=0, res=64):
    rows = eval_set(task, 64, n, offset, seed=seed)
    envs = [make_env(task) for _ in rows]
    goals = [reset_env(env, task, r[2], r[3], seed=seed * 100000 + k) for k, (env, r) in enumerate(zip(envs, rows))]
    with torch.autocast('cuda', dtype=torch.bfloat16):
        g = wm.encode({'pixels': prep(goals, res, 'cuda')})['emb'][:, 0].float()
    fs = data.fs
    budget = 2 * offset
    done = np.zeros(len(rows), bool); success = np.zeros(len(rows), bool); steps = np.zeros(len(rows), int)
    am, asd = data.act_mean, data.act_std
    while not done.all():
        act_idx = np.nonzero(~done)[0]
        imgs = [envs[k].render() for k in act_idx]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            e = wm.encode({'pixels': prep(imgs, res, 'cuda')})['emb'][:, 0].float()
        # remaining horizon to the goal as in training: the dataset offset minus steps taken (>=fs)
        rem = torch.as_tensor(np.maximum(offset - steps[act_idx], fs), device='cuda')
        a = net(e, g[act_idx], rem).float().cpu().numpy().reshape(len(act_idx), fs, len(am)) * asd + am
        for j, k in enumerate(act_idx):
            for x in a[j]:
                _, _, term, _, _ = envs[k].step(np.clip(x, -1, 1).astype(np.float32))
                steps[k] += 1
                if term:
                    success[k] = done[k] = True
                    break
                if steps[k] >= budget:
                    done[k] = True
                    break
    return {'success': success.tolist(), 'success_rate': float(success.mean()),
            'final_dist': [dist_info(env, task) for env in envs], 'offset': offset, 'n': len(rows)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt', required=True)
    p.add_argument('--offsets', default='25,50')
    p.add_argument('--n', type=int, default=200)
    p.add_argument('--steps', type=int, default=20000)
    a = p.parse_args()
    ck = Path(a.ckpt)
    out = ck.parent / 'eval' / f'gcidm_{ck.stem}.json'
    if out.exists():
        print('exists'); return
    out.parent.mkdir(exist_ok=True)
    task = json.loads((ck.parent / 'config.json').read_text())['task']
    net, wm, data = train(a.ckpt, steps=a.steps)
    res = [closed_loop(net, wm, data, task, int(o), a.n) for o in a.offsets.split(',')]
    out.write_text(json.dumps(res))
    print(json.dumps([(r['offset'], r['success_rate']) for r in res]), flush=True)


if __name__ == '__main__':
    main()
