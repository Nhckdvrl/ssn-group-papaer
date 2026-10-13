"""Completeness, full-output reporting, and plots for the frozen E123 wave.

Does not modify scientific scores or primary candidate-space readouts.
"""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from e118_criterion_code_feature_crossing import interval

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = [('qwen3', 'Qwen3-8B'), ('mistral', 'Mistral-7B'),
            ('llama', 'Llama-3.1-8B'), ('qwen14', 'Qwen3-14B')]
POLICIES = ['normal', 'answer_cross_off', 'all_cross_off']
SCOPES = ['native', 'gate']
CONDITIONS = [('normal_native', 'Native'), ('answer_cross_off_native', 'Answer\nformation'),
              ('all_cross_off_native', 'All cross-source\nformation'), ('normal_gate', 'Query\nonly'),
              ('answer_cross_off_gate', 'Answer +\nquery'), ('all_cross_off_gate', 'All formation\n+ query')]


def output_metrics(raw, preflight):
    """Readouts on the exact same primary world/source/query weighting."""
    agg, out, differences = {}, {}, {}
    for ns in ['shared', 'far']:
        for policy in POLICIES:
            for scope in SCOPES:
                correct = np.asarray([[[r['conditions'][f'{w}_{ns}_{policy}_{scope}_{owner}']['argmax_correct']
                    for owner in [0, 1]] for w in ['origin', 'cross']] for r in raw], dtype=float)
                other_word = np.asarray([[[[int(t in preflight['word_ids']['far' if owner == 0 else 'shared'])
                    if ns == 'far' else 0 for t in r['conditions'][f'{w}_{ns}_{policy}_{scope}_{owner}']['argmax_token']]
                    for owner in [0, 1]] for w in ['origin', 'cross']] for r in raw], dtype=float)
                values = {'both': correct.mean((1, 2, 3)), 'A': correct[:, :, 0].mean((1, 2)),
                          'B': correct[:, :, 1].mean((1, 2)), 'opposite_convention': correct[:, 0].mean((1, 2)),
                          'same_convention': correct[:, 1].mean((1, 2)),
                          'other_source_word': other_word.mean((1, 2, 3)),
                          'A_other_source_word': other_word[:, :, 0].mean((1, 2)),
                          'B_other_source_word': other_word[:, :, 1].mean((1, 2))}
                agg[ns, policy, scope] = values
                out[f'{ns}_{policy}_{scope}'] = {k: interval(v) for k, v in values.items()}
        for scope in SCOPES:
            for policy in POLICIES[1:]:
                differences[f'{ns}_{policy}_minus_normal_{scope}'] = {k: interval(
                    agg[ns, policy, scope][k] - agg[ns, 'normal', scope][k]) for k in agg[ns, 'normal', scope]}
            differences[f'{ns}_answer_minus_all_{scope}'] = {k: interval(
                agg[ns, 'answer_cross_off', scope][k] - agg[ns, 'all_cross_off', scope][k])
                for k in agg[ns, 'normal', scope]}
        for policy in POLICIES:
            differences[f'{ns}_query_isolation_{policy}'] = {k: interval(
                agg[ns, policy, 'gate'][k] - agg[ns, policy, 'native'][k]) for k in agg[ns, policy, 'native']}
    return {'policy_accuracy': out, 'contrasts': differences,
            'scope': 'Secondary full-vocabulary and other-source-word readouts; original primary unchanged.'}


