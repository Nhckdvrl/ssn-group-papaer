"""Fixed E81 outputs, factor effects, and role-aligned attention statistics."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d / 'run.json').read_text())
    assert max(run['control'].values()) <= .01
    rows = [json.loads(x) for x in (d / 'behavior.jsonl').read_text().splitlines()]
    assert len(rows) == run['args']['n']
    signs = np.array([r['signs'] for r in rows])
    assert signs.shape == (len(rows), 4) and np.array_equal(signs[:, :2], -signs[:, 2:])
    raw = {k: np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    assert all(v.shape == signs.shape and np.isfinite(v).all() for v in raw.values())
    metrics = {
        'margin': {k: (v * signs).mean(1) for k, v in raw.items()},
        'accuracy': {k: (v * signs > 0).mean(1) for k, v in raw.items()},
        'output_source_ranking': {k: ((v[:, :2] - v[:, 2:]) * signs[:, :2] > 0).mean(1) for k, v in raw.items()}}
    ci = lambda v: interval(v, seed=810, nboot=4000)
    out = dict(run=run, conditions={}, contrasts={}, factorial={}, attention={}, limitations=[
        'Output source ranking is not direct evidence selection.',
        'Factor interventions clamp the actual code carrier at all query positions; other probabilities and V remain live.',
        'Full-attention donor aligns demonstration roles, not query receiver roles; residual layout gap has multiple explanations.'])
    for k in raw:
        out['conditions'][k] = {name: ci(v[k]) for name, v in metrics.items()}
        out['attention'][k] = {}
        for site in ['carrier', 'label']:
            for stat in ['mass', 'within_source', 'final_mass', 'final_within_source']:
                vals = np.array([[r['attention'][k][str(l)][site][stat] for l in range(run['n_layers'])] for r in rows])
                out['attention'][k][site + '.' + stat] = ci(vals.mean((1, 2)))
                for scope, lo, hi in [('early', 0, 12), ('middle', 12, 24), ('late', 24, 36)]:
                    out['attention'][k][scope + '.' + site + '.' + stat] = ci(vals[:, lo:hi].mean((1, 2)))
    for layout in (0, 1):
        pre = f'D{layout}.'
        for mode in ['mass', 'within', 'both', 'source_flip', 'full_attention', 'instruction']:
            out['contrasts'][pre + mode + '.minus_native'] = {name: ci(v[pre+mode] - v[pre+'native']) for name, v in metrics.items()}
        out['factorial'][pre] = {}
        for name, v in metrics.items():
            s, m, p, b = [v[pre+x] for x in ['self', 'mass', 'within', 'both']]
            out['factorial'][pre][name] = {
                'mass_shapley': ci(.5*((m-s)+(b-p))),
                'within_shapley': ci(.5*((p-s)+(b-m))),
                'interaction': ci(b-m-p+s), 'both_minus_self': ci(b-s)}
    # Here both runs are clamped to the same donor mass/pi, despite layout.
    pairs = [('native', 'D1.native', 'D0.native'), ('both_use_D0_m_pi', 'D1.both', 'D0.self'),
             ('both_use_D1_m_pi', 'D1.self', 'D0.both'),
             ('both_use_D0_mass_own_pi', 'D1.mass', 'D0.self'),
             ('both_use_D1_mass_own_pi', 'D1.self', 'D0.mass')]
    for label, x, y in pairs:
        out['contrasts']['layout.' + label] = {name: ci(v[x] - v[y]) for name, v in metrics.items()}
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    print(json.dumps({'native': {k: out['conditions'][k] for k in ['D0.native', 'D1.native']},
                      'contrasts': out['contrasts'], 'factorial': out['factorial']}, indent=2))


if __name__ == '__main__':
    main()
