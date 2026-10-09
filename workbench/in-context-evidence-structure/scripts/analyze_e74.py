"""Preregistered scoped signs and owner/foreign specificity; all contexts kept."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval as context_interval


def interval(value):
    return context_interval(value, seed=740, nboot=4000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d / 'run.json').read_text())
    assert run['sanity_max_error'] <= .1 and run['oracle_mismatches'] == 0
    rows = [json.loads(l) for l in (d / 'behavior.jsonl').read_text().splitlines()]
    assert len(rows) == run['args']['n']
    n = len(rows)
    raw = {k: np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    target_indices = np.array([[r['missing_kind'], 3 + r['missing_kind']] for r in rows])
    pairs = np.array([r['target_pair'] for r in rows])
    ni = np.arange(n)[:, None]
    heldmask = np.zeros((n, 12), dtype=bool)
    heldmask[ni, target_indices] = True
    out = {'run': run, 'conditions': {}, 'signed_responses': {}, 'specificity': {}, 'family_contrasts': {}}
    all_metrics, phi, ld = {}, {}, {}
    for k, v in raw.items():
        gold = np.array([[o['gold'] for o in r['oracles'][k]] for r in rows])
        correct = v[ni, np.arange(12)[None], gold]
        other = v.copy()
        other[ni, np.arange(12)[None], gold] = -np.inf
        margin = correct - other.max(-1)
        probs = np.exp(v - v.max(-1, keepdims=True));probs /= probs.sum(-1, keepdims=True)
        hvals = {}
        for name, mask in [('target_queries', heldmask), ('seen_control', ~heldmask)]:
            cnt = mask.sum(-1)
            item = {'accuracy': ((margin > 0) * mask).sum(-1) / cnt,
                    'margin': (margin * mask).sum(-1) / cnt,
                    'unknown_probability': (probs[..., 3] * mask).sum(-1) / cnt}
            hvals[name] = item
        all_metrics[k] = hvals
        out['conditions'][k] = {name: {stat: interval(value) for stat, value in m.items()} for name, m in hvals.items()}
        va = v[np.arange(n), target_indices[:, 0]]
        vb = v[np.arange(n), target_indices[:, 1]]
        la = va[np.arange(n), pairs[:, 0]] - va[np.arange(n), pairs[:, 1]]
        lb = vb[np.arange(n), pairs[:, 0]] - vb[np.arange(n), pairs[:, 1]]
        phi[k] = la - lb
        ld[k] = (la, lb)
        out['conditions'][k]['source_colour_contrast'] = interval(phi[k])
    for coverage in ['full', 'held']:
        for family in ['bijective', 'independent']:
            for instructed in [0, 1]:
                root = f'{coverage}.{family}.{instructed}.'
                base = root + 'base'
                out['signed_responses'][root + 'sync'] = interval(phi[base] - phi[root + 'scope_swap'])
                for owned, comp in [('owned_a', 'comp_a'), ('owned_b', 'comp_b')]:
                    # Psi=LD_A-LD_B: either owner's correct target swap reduces Psi.
                    # Both owner-minus-comp responses therefore have the same sign.
                    out['signed_responses'][root + owned + '_minus_comp'] = interval(phi[root + comp] - phi[root + owned])
                    which = 0 if owned == 'owned_a' else 1
                    oriented = 1 if which == 0 else -1
                    out['specificity'][root + owned] = {
                        'edited_source_ld_base_minus_edit': interval(oriented * (ld[base][which] - ld[root + owned][which])),
                        'untouched_source_ld_change': interval(ld[root + owned][1 - which] - ld[base][1 - which])}
                for change in ['foreign_swap', 'foreign_cycle', 'comp_a', 'comp_b']:
                    key = root + change
                    out['specificity'][key] = {'source_contrast_minus_base': interval(phi[key] - phi[base]),
                        **{stat + '_minus_base': interval(all_metrics[key]['target_queries'][stat] - all_metrics[base]['target_queries'][stat]) for stat in ['accuracy', 'margin', 'unknown_probability']}}
        for instructed in [0, 1]:
            x = f'{coverage}.bijective.{instructed}.base';y = f'{coverage}.independent.{instructed}.base'
            out['family_contrasts'][f'{coverage}.{instructed}'] = {
                'source_contrast_bijective_minus_independent': interval(phi[x] - phi[y]),
                'unknown_probability_bijective_minus_independent': interval(all_metrics[x]['target_queries']['unknown_probability'] - all_metrics[y]['target_queries']['unknown_probability'])}
    out['limitations'] = ['Conditional raw next-token choices, not unconstrained native capability.',
                          'Source-swap sign alone does not distinguish owner exclusion from peer borrowing.',
                          'Compensation-only controls intentionally change global counts; owner contrasts use source differences.',
                          'The oracle assumes the stated function family; no universal rationality claim.']
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    print('base', {k: v for k, v in out['conditions'].items() if k.endswith('.base')})
    print('signed', out['signed_responses'])
    print('specificity_held_bijection', {k: v for k, v in out['specificity'].items() if k.startswith('held.bijective.')})


if __name__ == '__main__':
    main()
