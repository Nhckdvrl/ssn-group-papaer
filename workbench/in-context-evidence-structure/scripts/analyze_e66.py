"""Paired context bootstrap; distinguish deployment from donor responsiveness."""
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
    assert run['sanity_max_error'] <= 0.1 and run['masked_attention_mass_max'] == 0
    rows = [json.loads(l) for l in (d / 'behavior.jsonl').read_text().splitlines()]
    values = {k: np.array([np.array(r['scores'][k]) * r['signs'] for r in rows]) for k in rows[0]['scores']}
    means = {k: v.mean(1) for k, v in values.items()}
    acc = {k: (v > 0).mean(1) for k, v in values.items()}
    out = {'run': run, 'conditions': {}, 'contrasts': {}}
    for k, v in values.items():
        out['conditions'][k] = {'margin': interval(means[k]), 'accuracy': interval(acc[k]),
             'source_means': [interval(v[:, sl].mean(1)) for sl in (slice(0, 2), slice(2, 4))],
             'class_means': [interval(v[:, [0, 2]].mean(1)), interval(v[:, [1, 3]].mean(1))]}
    pairs = [('clause.base', 'clause.base.null'), ('clause.single.base', 'clause.single.base.null'),
             ('answer.base', 'answer.null'), ('clause.base', 'native.base'), ('answer.base', 'original.base'),
             ('name.base', 'clause.base'), ('clause.instruction', 'clause.base')]
    for x, y in pairs:
        out['contrasts'][x + '_minus_' + y] = {'margin': interval(means[x] - means[y]), 'accuracy': interval(acc[x] - acc[y])}
    for prefix in ['native', 'native.single', 'clause', 'clause.single', 'name', 'answer', 'original']:
        base, flip = prefix + '.base', prefix + '.flip'
        out['contrasts'][prefix + '.rule_flip'] = {'effect': interval(means[base] - means[flip])}
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    for k in ['native.base', 'clause.base', 'clause.base.null', 'clause.single.base', 'clause.single.base.null',
              'answer.base', 'answer.null', 'clause.instruction']:
        print(k, out['conditions'][k]['margin'], out['conditions'][k]['accuracy'])
    print(json.dumps(out['contrasts'], indent=2))

if __name__ == '__main__':
    main()
