"""Train one LeWM-family world model (size x data x seed) with GPU-resident data.

Usage: python train.py --task tworoom --size S --episodes 0 --seed 0 --steps 100000 --out DIR
episodes=0 means all training episodes.
"""
import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch

from wm import GPUData, SIGReg, add_aux_heads, build_model, lewm_loss, n_params


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--task', required=True)
    p.add_argument('--size', default='S')
    p.add_argument('--latent', type=int, default=0)
    p.add_argument('--episodes', type=int, default=0)
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--steps', type=int, default=100_000)
    p.add_argument('--batch', type=int, default=128)
    p.add_argument('--lr', type=float, default=5e-5)
    p.add_argument('--wd', type=float, default=1e-3)
    p.add_argument('--warmup', type=int, default=2000)
    p.add_argument('--res', type=int, default=64)
    p.add_argument('--patch', type=int, default=8)
    p.add_argument('--ckpts', default='')
    p.add_argument('--compile', type=int, default=1)
    p.add_argument('--aux', default='')
    p.add_argument('--aux_w', type=float, default=0.1)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'complete.json').exists():
        print('already complete'); return
    torch.manual_seed(a.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    np.random.seed(a.seed)
    dev = 'cuda'
    data = GPUData(a.task, res=a.res, episodes=a.episodes or None, device=dev)
    adim = data.fs * data.actions.shape[-1]
    model = add_aux_heads(build_model(a.size, img=a.res, patch=a.patch, latent=a.latent or None, action_dim=adim), a.aux, action_dim=adim).to(dev)
    sigreg = SIGReg(knots=17, num_proj=1024).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.wd)

    def lr_at(s):
        if s < a.warmup:
            return a.lr * (s + 1) / a.warmup
        q = (s - a.warmup) / max(1, a.steps - a.warmup)
        return a.lr * 0.5 * (1 + math.cos(math.pi * q))

    ckpts = sorted(set([int(x) for x in a.ckpts.split(',') if x] + [a.steps]))
    cfg = vars(a) | {'params': n_params(model), 'train_episodes': int(len(data.train_eps)),
                     'train_windows': data.n_train_transitions(), 'val_episodes': int(len(data.val_eps)),
                     'act_mean': data.act_mean.tolist(), 'act_std': data.act_std.tolist(),
                     'gpu': torch.cuda.get_device_name()}
    (out / 'config.json').write_text(json.dumps(cfg, indent=1))
    np.savez(out / 'split.npz', train_eps=data.train_eps, val_eps=data.val_eps)
    print(json.dumps({k: cfg[k] for k in ['size', 'params', 'train_episodes', 'train_windows']}), flush=True)
    loss_fn = (lambda b: lewm_loss(model, sigreg, b, aux=a.aux, aux_w=a.aux_w))
    if a.compile:
        loss_fn = torch.compile(loss_fn)
    gen = torch.Generator(device=dev).manual_seed(a.seed)
    vgen = torch.Generator(device=dev).manual_seed(12345)
    log = []
    t0 = time.time()
    model.train()
    for step in range(1, a.steps + 1):
        for g in opt.param_groups:
            g['lr'] = lr_at(step - 1)
        batch = data.batch(a.batch, gen)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            loss, pl, sl, _ = loss_fn(batch)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % 500 == 0 or step == 1:
            row = {'step': step, 'loss': loss.item(), 'pred': pl.item(), 'sigreg': sl.item(),
                   'sec': time.time() - t0}
            if step % 2500 == 0:
                model.eval()
                with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                    vp, vs = [], []
                    for _ in range(8):
                        _, vpl, vsl, _ = lewm_loss(model, sigreg, data.batch(256, vgen, val=True))
                        vp.append(vpl.item()); vs.append(vsl.item())
                row |= {'val_pred': float(np.mean(vp)), 'val_sigreg': float(np.mean(vs))}
                model.train()
            log.append(row)
            print(json.dumps(row), flush=True)
        if step in ckpts:
            model.eval()
            torch.save(model, out / f'model_{step:07d}.pt')
            model.train()
            (out / 'log.json').write_text(json.dumps(log))
    (out / 'log.json').write_text(json.dumps(log))
    (out / 'complete.json').write_text(json.dumps({'steps': a.steps, 'seconds': time.time() - t0}))


if __name__ == '__main__':
    main()
