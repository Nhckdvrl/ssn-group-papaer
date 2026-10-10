"""Prespecified E82 structural contrasts. All contexts; paired bootstrap."""
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
    metrics = dict(margin={k: (v * signs).mean(1) for k, v in raw.items()},
                   accuracy={k: (v * signs > 0).mean(1) for k, v in raw.items()},
                   output_source_ranking={k: ((v[:, :2]-v[:, 2:]) * signs[:, :2] > 0).mean(1) for k, v in raw.items()},
                   abs_common_component={k: np.abs((v[:, :2]+v[:, 2:])/2).mean(1) for k, v in raw.items()})
    ci = lambda x: interval(x, seed=820, nboot=4000)
    out = dict(run=run, conditions={}, contrasts={}, factorial={}, attention={}, limitations=[
        'Conditional log-weight splicing renormalizes other groups; it is not pure edge mediation.',
        'Replay uses recorded native attention; query values and residuals remain live.',
        'Source output ranking is not internal source selection; donor may already contain answer-related selection.'])
    for k in raw:
        out['conditions'][k] = {name: ci(v[k]) for name, v in metrics.items()}
        out['attention'][k] = {}
        for site, stats in [('carrier', ['mass', 'within_source', 'within_kind', 'final_mass', 'final_within_source', 'final_within_kind']),
                            ('label', ['mass', 'within_source', 'within_kind', 'final_mass', 'final_within_source', 'final_within_kind']),
                            ('query', ['mass', 'final_mass'])]:
            for stat in stats:
                vals = np.array([[r['attention'][k][str(l)][site][stat] for l in range(run['n_layers'])] for r in rows])
                out['attention'][k][site + '.' + stat] = ci(vals.mean((1, 2)))
    pairs = [('layout.native', 'D1.native', 'D0.native'),
             ('frozen_base.minus_carrier_live', 'D0.frozen_base', 'D0.carrier_live'),
             ('full.minus_native', 'D0.full', 'D0.native'),
             ('full.minus_label_query', 'D0.full', 'D0.label_query'),
             ('label.minus_label_final', 'D0.label', 'D0.label_final')]
    pairs += [(mode + '.minus_frozen_base', 'D0.' + mode, 'D0.frozen_base')
              for mode in ['full', 'label', 'query', 'label_query', 'label_final']]
    for name, x, y in pairs:
        out['contrasts'][name] = {metric: ci(v[x]-v[y]) for metric, v in metrics.items()}
    for name, v in metrics.items():
        s, l, q, b = [v['D0.'+m] for m in ['frozen_base', 'label', 'query', 'label_query']]
        out['factorial'][name] = dict(label_shapley=ci(.5*((l-s)+(b-q))),
                                      query_shapley=ci(.5*((q-s)+(b-l))),
                                      interaction=ci(b-l-q+s))
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(dict(conditions=out['conditions'], contrasts=out['contrasts'], factorial=out['factorial']), indent=2))


if __name__ == '__main__':
    main()
