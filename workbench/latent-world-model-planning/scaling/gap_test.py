"""E23 maze diagnosis (POST-HOC): predicted vs realised slow-feature cost improvement per executed CEM plan."""
import json, os, sys
os.environ['LWM_GAP'] = '1'
import numpy as np
from pathlib import Path
from eval_plan import run
ck, off = sys.argv[1], int(sys.argv[2])
mode = sys.argv[3] if len(sys.argv) > 3 else 'sfa'
r = run(ck, 'pmazemedium', off, 200, 300, 30, 30, 5, 0, **({} if mode == 'l2' else {mode: 4}))
g = np.array(r['gap'])
pred, act = g[:, 0] - g[:, 1], g[:, 0] - g[:, 2]
out = {'ckpt': ck, 'mode': mode, 'offset': off, 'sr': r['success_rate'], 'n_steps': len(g),
       'pred_impr_mean': float(pred.mean()), 'act_impr_mean': float(act.mean()), 'realised_ratio': float(act.mean() / pred.mean()),
       'frac_worse': float((act < 0).mean()), 'overestimate_median': float(np.median(pred - act)),
       'c_scale_median': float(np.median(g[:, 0]))}
Path(ck).parent.joinpath('eval', f'gap_{mode}_off{off}.json').write_text(json.dumps({**out, 'gap': r['gap']}))
print(Path(ck).parent.name, json.dumps(out), flush=True)
