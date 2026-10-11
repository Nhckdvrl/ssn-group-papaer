"""E23 C2: metric horizon of frozen DINOv2 features (the DINO-WM planning space) as a function of encoder size.
For each lag h, median L2 distance between frames h env steps apart on training trajectories (native 224px),
for the CLS embedding and for all patch tokens concatenated (DINO-WM's cost). Writes results/E23_fm_horizon.json."""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
import torch

from eval_plan import droot, frames

LAGS = (1, 2, 5, 10, 15, 25, 35, 50, 75, 100, 150)
OUT = Path(__file__).resolve().parents[1] / 'results' / 'E23_fm_horizon.json'


@torch.no_grad()
def enc(model, px):
    mean = torch.tensor([0.485, 0.456, 0.406], device='cuda')[:, None, None]
    std = torch.tensor([0.229, 0.224, 0.225], device='cuda')[:, None, None]
    cls, patch = [], []
    for i in range(0, len(px), 128):
        x = torch.as_tensor(px[i:i + 128], device='cuda').permute(0, 3, 1, 2).float().div_(255)
        x = (x - mean) / std
        with torch.autocast('cuda', dtype=torch.bfloat16):
            h = model(pixel_values=x).last_hidden_state.float()
        cls.append(h[:, 0]); patch.append(h[:, 1:].flatten(1).half().cpu())
    return torch.cat(cls), torch.cat(patch)


def main():
    tasks = sys.argv[1].split(',') if len(sys.argv) > 1 else ['tworoom', 'pusht']
    from transformers import AutoModel
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    for task in tasks:
        meta = np.load(droot(task, 224) / 'meta.npz')
        off, ln = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
        g = np.random.default_rng(2)
        pairs = []
        for h in LAGS:
            ok = np.nonzero(ln > h + 1)[0]
            if len(ok) == 0:
                break
            eps = g.choice(ok, 1000)
            a = off[eps] + (g.random(1000) * (ln[eps] - h - 1)).astype(np.int64)
            pairs.append((h, a, a + h))
        idx = np.unique(np.concatenate([np.concatenate([a, b]) for _, a, b in pairs]))
        px = frames(task, idx, 224)
        pos = {int(j): k for k, j in enumerate(idx)}
        for size in ['small', 'base', 'large', 'giant']:
            key = f'{task}/dinov2-{size}'
            if key in res:
                continue
            model = AutoModel.from_pretrained(f'facebook/dinov2-{size}').cuda().eval()
            zc, zp = enc(model, px)
            out = {}
            for name, z in [('cls', zc), ('patch', zp)]:
                curve = []
                for h, a, b in pairs:
                    ia = torch.as_tensor([pos[int(x)] for x in a], device=z.device)
                    ib = torch.as_tensor([pos[int(x)] for x in b], device=z.device)
                    d = torch.cat([(z[ia[j:j + 100]].cuda().float() - z[ib[j:j + 100]].cuda().float()).norm(dim=-1)
                                   for j in range(0, len(ia), 100)])
                    curve.append((h, d.median().item()))
                pl = curve[-1][1]
                out[name] = {'curve': curve, 'metric_horizon': next(h for h, m in curve if m >= 0.9 * pl)}
            res[key] = out
            OUT.write_text(json.dumps(res, indent=1))
            print(key, 'cls mh', out['cls']['metric_horizon'], 'patch mh', out['patch']['metric_horizon'], flush=True)
            del model
            torch.cuda.empty_cache()


if __name__ == '__main__':
    main()
