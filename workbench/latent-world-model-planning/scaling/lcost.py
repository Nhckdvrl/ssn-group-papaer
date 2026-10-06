"""Learned planning objective on a frozen world-model latent (temporal-distance head), planned with CEM.

Head f(z, z_goal) regresses log(1 + steps between two frames of the same training episode)
(frame-separation supervision as in 'The Objective Is the Bottleneck' / temporal-distance heads; no
reachability negatives). The planner is the same CEM as eval_plan.py with the same world model
rollout; only the terminal cost ||z_T - z_g||^2 is replaced by f(z_T, z_g).
Outputs <run>/eval/lcost_<ckpt>.json: closed-loop success at each offset, n=200.
"""
import argparse
import json
import os
import time
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
import torch
from torch import nn

from wm import GPUData
from gcidm import encode_all
from eval_plan import eval_set, make_env, reset_env, dist_info, prep


class DistHead(nn.Module):
    def __init__(self, d, h=512):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(2 * d, h), nn.LayerNorm(h), nn.GELU(), nn.Linear(h, h), nn.LayerNorm(h),
                                 nn.GELU(), nn.Linear(h, h), nn.LayerNorm(h), nn.GELU(), nn.Linear(h, 1))

    def forward(self, z, g):
        return self.net(torch.cat([z, g], -1)).squeeze(-1)


def train_head(ckpt, steps=20000, max_h=None, bs=8192, lr=3e-4, seed=0):
    cfg = json.loads((Path(ckpt).parent / 'config.json').read_text())
    if max_h is None:  # same protocol as before for the original tasks; long-range mazes need 200
        max_h = 200 if cfg['task'].startswith('pmaze') else 100
    data = GPUData(cfg['task'], res=cfg.get('res', 64), device='cuda', pixels_on='cpu')
    wm = torch.load(ckpt, map_location='cuda', weights_only=False).eval()
    z = encode_all(wm, data)
    ep_off, ep_len = data.meta['ep_offset'].astype(np.int64), data.meta['ep_len'].astype(np.int64)
    idx, ends = [], []
    for e in data.train_eps:
        i = ep_off[e] + np.arange(ep_len[e] - 1)
        idx.append(i); ends.append(np.full(len(i), ep_off[e] + ep_len[e] - 1))
    idx = torch.as_tensor(np.concatenate(idx), device='cuda')
    ends = torch.as_tensor(np.concatenate(ends), device='cuda')
    torch.manual_seed(seed)
    head = DistHead(z.shape[1]).cuda()
    opt = torch.optim.AdamW(head.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps, eta_min=lr / 100)
    gen = torch.Generator(device='cuda').manual_seed(seed)
    for s in range(steps):
        k = torch.randint(len(idx), (bs,), device='cuda', generator=gen)
        i, end = idx[k], ends[k]
        span = torch.clamp(end - i, max=max_h)
        h = (torch.rand(bs, device='cuda', generator=gen) * (span + 1)).long().clamp(max=span)
        pred = head(z[data.remap[i]], z[data.remap[i + h]])
        loss = (pred - torch.log1p(h.float())).pow(2).mean()
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); sched.step()
    head.eval()
    return head, wm, data


@torch.no_grad()
def rollout_final(model, emb0, cand, chunk=8192, hist=3):
    B, S, H, A = cand.shape
    flat = cand.reshape(B * S, H, A)
    e0 = emb0[:, None].expand(B, S, -1).reshape(B * S, -1)
    outs = []
    for i in range(0, B * S, chunk):
        a = flat[i:i + chunk]
        emb = e0[i:i + chunk, None]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            act_emb = model.action_encoder(a)
            for t in range(H):
                p = model.predict(emb[:, -hist:], act_emb[:, max(0, t + 1 - hist):t + 1])[:, -1:]
                emb = torch.cat([emb, p.float()], 1)
        outs.append(emb[:, -1])
    return torch.cat(outs).view(B, S, -1)


@torch.no_grad()
def plan_eval(head, wm, data, task, offset, n, S=300, iters=30, topk=30, H=5, seed=0, res=64):
    rows = eval_set(task, 64, n, offset, seed=seed)
    envs = [make_env(task) for _ in rows]
    goals = [reset_env(env, task, r[2], r[3], seed=seed * 100000 + k) for k, (env, r) in enumerate(zip(envs, rows))]
    with torch.autocast('cuda', dtype=torch.bfloat16):
        g = wm.encode({'pixels': prep(goals, res, 'cuda')})['emb'][:, 0].float()
    adim = data.actions.shape[-1]
    fs, A = data.fs, adim * data.fs
    am, asd = data.act_mean, data.act_std
    budget = 2 * offset
    done = np.zeros(len(rows), bool); success = np.zeros(len(rows), bool); steps = np.zeros(len(rows), int)
    gen = torch.Generator(device='cuda').manual_seed(seed)
    while not done.all():
        ai = np.nonzero(~done)[0]
        with torch.autocast('cuda', dtype=torch.bfloat16):
            e0 = wm.encode({'pixels': prep([envs[k].render() for k in ai], res, 'cuda')})['emb'][:, 0].float()
        B = len(ai)
        mean = torch.zeros(B, H, A, device='cuda'); std = torch.ones(B, H, A, device='cuda')
        gg = g[ai]
        for _ in range(iters):
            cand = torch.randn(B, S, H, A, device='cuda', generator=gen) * std[:, None] + mean[:, None]
            cand[:, 0] = mean
            zf = rollout_final(wm, e0, cand)
            cost = head(zf, gg[:, None].expand_as(zf))
            idx = cost.topk(topk, dim=1, largest=False).indices
            el = torch.gather(cand, 1, idx[..., None, None].expand(-1, -1, H, A))
            mean, std = el.mean(1), el.std(1, correction=0)
        acts = mean.cpu().numpy().reshape(B, H * fs, adim) * asd + am
        for j, k in enumerate(ai):
            for x in acts[j]:
                _, _, term, _, _ = envs[k].step(np.clip(x, -1, 1).astype(np.float32))
                steps[k] += 1
                if term:
                    success[k] = done[k] = True
                    break
                if steps[k] >= budget:
                    done[k] = True
                    break
    return {'offset': offset, 'n': len(rows), 'success': success.tolist(), 'success_rate': float(success.mean()),
            'final_dist': [dist_info(env, task) for env in envs]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ckpt', required=True)
    p.add_argument('--offsets', default='25,50')
    p.add_argument('--n', type=int, default=200)
    a = p.parse_args()
    ck = Path(a.ckpt)
    out = ck.parent / 'eval' / f'lcost_{ck.stem}.json'
    if out.exists():
        print('exists'); return
    out.parent.mkdir(exist_ok=True)
    task = json.loads((ck.parent / 'config.json').read_text())['task']
    t0 = time.time()
    head, wm, data = train_head(a.ckpt)
    res = [plan_eval(head, wm, data, task, int(o), a.n) for o in a.offsets.split(',')]
    out.write_text(json.dumps(res))
    print(json.dumps([(r['offset'], r['success_rate']) for r in res]), round(time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
