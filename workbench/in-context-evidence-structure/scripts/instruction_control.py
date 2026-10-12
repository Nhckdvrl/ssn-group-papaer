"""Post-hoc aggregate of the pre-specified one-sentence instruction condition on the SST-5 policy runs."""
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
    ctx = lambda fmt: np.array([np.mean([np.mean(r['conditions'][fmt.format(w=w, o=o)]['argmax_correct'])
                                         for w in ['origin', 'cross'] for o in [0, 1]]) for r in rows])
    ins, nat, sel = ctx('{w}_shared_instruction_{o}'), ctx('{w}_shared_normal_native_{o}'), ctx('{w}_shared_answer_cross_off_native_{o}')
    out[m] = {'instruction_minus_native': interval(100 * (ins - nat)), 'selective_minus_instruction': interval(100 * (sel - ins)),
              'native': float(100 * nat.mean()), 'instruction': float(100 * ins.mean())}
(ROOT / 'results/e123/instruction_control_2026-10-13.json').write_text(json.dumps(out, indent=1) + '\n')
for m, v in out.items():
    print(m, {k: (round(x['mean'], 2), [round(c, 2) for c in x['ci95']]) if isinstance(x, dict) else round(x, 2) for k, x in v.items()})
