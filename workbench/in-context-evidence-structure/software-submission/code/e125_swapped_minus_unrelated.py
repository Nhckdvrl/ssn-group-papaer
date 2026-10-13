"""Public word-set table (E125): formation-only gains of the correct and swapped tables relative to the unrelated table.

Same aggregation as e125_public_output_schema_coordination.analyze (full-vocabulary accuracy, equal weights over
convention worlds, requested sources and queries within a prompt). Writes
results/e125/swapped_minus_unrelated_2026-10-13.json.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e118_criterion_code_feature_crossing import interval

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ['origin', 'cross']
out = {}
for m in ['qwen3', 'mistral', 'llama']:
    rows = [json.loads(x) for x in (ROOT / f'results/e125/{m}_confirmation/behavior.jsonl').read_text().splitlines()]

    def agg(key):
        full = np.asarray([[[r['conditions'][f'{w}_{key}_{o}']['argmax_correct'] for o in [0, 1]] for w in WORLDS]
                           for r in rows], dtype=float)
        return full.mean((1, 2, 3))

    gain = {roster: agg(f'{roster}_f1r0') - agg(f'{roster}_f0r0') for roster in ['true', 'unrelated', 'swapped']}
    out[m] = {'swapped_minus_unrelated': interval(100 * (gain['swapped'] - gain['unrelated'])),
              'true_minus_unrelated': interval(100 * (gain['true'] - gain['unrelated'])),
              'true_minus_swapped': interval(100 * (gain['true'] - gain['swapped'])),
              'unrelated_raw': interval(100 * gain['unrelated']), 'swapped_raw': interval(100 * gain['swapped'])}
(ROOT / 'results/e125/swapped_minus_unrelated_2026-10-13.json').write_text(json.dumps(out, indent=1) + '\n')
print({m: round(v['swapped_minus_unrelated']['mean'], 2) for m, v in out.items()})
