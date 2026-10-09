"""POST-HOC descriptive decomposition of paired query logits (not an ability test).

Ground truth defines the interaction basis. Centered accuracies use evaluation
query means and must NOT be presented as an independently deployable repair.
"""
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
    rows = [json.loads(l) for l in (d / 'behavior.jsonl').read_text().splitlines()]
    contexts = [json.loads(l) for l in (d / 'contexts.jsonl').read_text().splitlines()]
    assert len(rows) == len(contexts)
    out = {'post_hoc': True, 'evaluation_centering_not_deployable': True, 'conditions': {}, 'paired_changes': {}}
    data = {}
    for condition in ['base', 'drop_direct.base', 'drop_relay.base', 'drop_both.base']:
        entries = []
        for r, ctx in zip(rows, contexts):
            v = np.array(r['scores'][condition])
            g = np.array(r['signs'])
            s = 2 * np.array([q['source'] for q in ctx['queries']]) - 1
            x = g * s
            basis = np.stack([np.ones_like(s), s, x, g])
            assert np.allclose(basis @ basis.T, len(s) * np.eye(4))
            coef = basis @ v / len(s)
            resid = v - coef @ basis
            halves = len(v) // 2
            assert [q['word'] for q in ctx['queries'][:halves]] == [q['word'] for q in ctx['queries'][halves:]]
            m = {'source_correct_interaction': coef[3], 'abs_intercept': abs(coef[0]),
                 'abs_source_main': abs(coef[1]), 'abs_input_main': abs(coef[2]),
                 'residual_rms': np.mean(resid ** 2) ** 0.5,
                 'native_accuracy': np.mean(v * g > 0),
                 'paired_source_ranking': np.mean((v[:halves] - v[halves:]) * g[:halves] > 0),
                 'evaluation_global_centered_accuracy': np.mean((v - coef[0]) * g > 0),
                 'evaluation_source_centered_accuracy': np.mean((v - coef[0] - coef[1] * s) * g > 0)}
            entries.append(m)
        data[condition] = {k: np.array([e[k] for e in entries]) for k in entries[0]}
        out['conditions'][condition] = {k: interval(vals) for k, vals in data[condition].items()}
    out['paired_changes']['drop_direct_minus_base'] = {k: interval(data['drop_direct.base'][k] - data['base'][k]) for k in data['base']}
    (d / 'factorial_posthoc.json').write_text(json.dumps(out, indent=2))
    print(d.name, out['paired_changes']['drop_direct_minus_base'])

if __name__ == '__main__':
    main()
