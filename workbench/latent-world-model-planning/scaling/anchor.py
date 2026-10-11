"""E23 C: released LeWM checkpoints (official 224px recipe). Metric-horizon curves (full latent / slow k=4,
native 224px training frames) and n=200 closed-loop success with full L2, slow-feature and auto costs.
Writes <out>/anchor_<task>.json incrementally."""
import json
import sys
from pathlib import Path

import torch

from eval_plan import metric_horizon, run, sfa_basis

CK = {'tworoom': '/home/xiang/.cache/huggingface/latent-wm-derived/lewm-tworoom-object.ckpt',
      'pusht': '/home/xiang/.cache/huggingface/latent-wm-derived/lewm-pusht-object.ckpt'}
OFFS = {'tworoom': [25, 50, 75], 'pusht': [25, 50]}

if __name__ == '__main__':
    task, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    f = out / f'anchor_{task}.json'
    res = json.loads(f.read_text()) if f.exists() else {'runs': []}
    if 'mh' not in res:
        model = torch.load(CK[task], map_location='cuda', weights_only=False).eval()
        full = metric_horizon(model, task, 'cuda', return_curve=True, res=224)
        slow = metric_horizon(model, task, 'cuda', return_curve=True, W=sfa_basis(model, task, 4, 'cuda', res=224), res=224)
        res['mh'] = {'full': full, 'sfa4': slow, 'metric_horizon': next(h for h, m in full if m >= 0.9 * full[-1][1])}
        f.write_text(json.dumps(res))
        print(task, 'metric horizon', res['mh']['metric_horizon'], full, flush=True)
        del model
    for mode in ['l2', 'sfa', 'auto']:
        for off in OFFS[task]:
            if any(r['mode'] == mode and r['offset'] == off for r in res['runs']):
                continue
            r = run(CK[task], task, off, 200, 300, 30, 30, 5, 0, **({} if mode == 'l2' else {mode: 4}))
            r['mode'] = mode
            res['runs'].append(r)
            f.write_text(json.dumps(res))
            print(task, mode, 'off', off, 'sr', r['success_rate'], flush=True)
