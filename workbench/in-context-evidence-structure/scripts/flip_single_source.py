"""Post-hoc readouts on the SST-5 policy runs (computed after the confirmation runs, no new model runs):
per-query magnitude and flip rate of B's convention effect under A-only reading, and single-source accuracy."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e118_criterion_code_feature_crossing import interval

ROOT = Path(__file__).resolve().parents[1]
SRCS = [('Qwen3-8B', 'e123/qwen3_confirmation'), ('Qwen3-14B', 'e123/qwen14_confirmation'),
        ('Qwen3-32B', 'e131/qwen32_confirmation_function'), ('Mistral-7B', 'e123/mistral_confirmation'),
        ('Llama-3.1-8B', 'e123/llama_confirmation'), ('Llama-3.1-70B', 'e131/llama70_confirmation_function'),
        ('Gemma-2-2B', 'e123/gemma2_confirmation')]
out = {}
for m, s in SRCS:
    path = ROOT / 'results' / s / 'behavior.jsonl'
    if not path.exists():
        continue
    rows = [json.loads(x) for x in path.read_text().splitlines()]
    z = lambda k: np.array([r['conditions'][k]['z'] for r in rows])
    acc = lambda k: np.array([np.mean(r['conditions'][k]['argmax_correct']) for r in rows])
    res = {}
    for ns in ['shared', 'far']:
        o, c, w = z(f'origin_{ns}_normal_gate_0'), z(f'cross_{ns}_normal_gate_0'), z(f'within_{ns}_normal_gate_0')
        flip, wflip = (np.sign(c) != np.sign(o)).mean(1), (np.sign(w) != np.sign(o)).mean(1)
        res[ns] = {'query_abs': interval(abs(c - o).mean(1) / 2), 'within_query_abs': interval(abs(w - o).mean(1) / 2),
                   'flip': interval(flip * 100), 'within_flip': interval(wflip * 100),
                   'flip_minus_within': interval((flip - wflip) * 100)}
    res['single_shared'] = interval(100 * (acc('single_A') + (acc('single_B_origin_shared') + acc('single_B_cross_shared')) / 2) / 2)
    out[m] = res
(ROOT / "results/e123/flip_and_single_source_2026-10-13.json").write_text(json.dumps(out, indent=1) + '\n')
print({m: round(v['single_shared']['mean'], 1) for m, v in out.items()})
