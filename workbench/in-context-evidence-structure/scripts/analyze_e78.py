"""Context bootstrap without selecting recognized sources or good header order."""
import argparse
import json
from pathlib import Path

import numpy as np


GROUPS = {'seen': [2, 7], 'interpolation': [3, 4, 5, 6], 'extrapolation': [0, 1, 8, 9]}
METHODS = ['input_first', 'source_first', 'empty_rule', 'auto_code', 'gold_code', 'opposite_code']
SCOPES = ['mixed', 'single', 'mixed_scope']
ORDERS = ['copy_first', 'subtract_first']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d / 'run.json').read_text())
    assert run['no_op_max_error'] <= .1 and run['full_forward_max_error'] <= .1
    rows = [json.loads(line) for line in (d / 'behavior.jsonl').read_text().splitlines()]
    n = len(rows)
    assert n == run['args']['n']
    assert [r['context'] for r in rows] == list(range(n))
    theta = np.array([r['theta'][:2] for r in rows])
    x = np.arange(10)[None, None, :]
    gold = np.where(theta[:, :, None] == 1, x, 9 - x)
    opposite = 9 - gold
    boot = np.random.default_rng(780).integers(n, size=(4000, n))

    def summarize(mean, samples):
        assert np.isfinite(samples).all()
        return {'mean': float(mean), 'ci95': np.quantile(samples, [.025, .975]).tolist(), 'n_contexts': n}

    def ci(values):
        return summarize(values.mean(), values[boot].mean(1))

    def ratio_parts(num, den):
        bd = den[boot].sum(1)
        assert (bd > 0).all()
        return num.sum() / den.sum(), num[boot].sum(1) / bd

    def ratio(num, den):
        return summarize(*ratio_parts(num, den))

    def by_rule(correct, xs=None):
        # Each context can have zero copies/complements. Bootstrap the ratio
        # of total successes to total eligible queries; never drop contexts.
        values = correct[:, :, xs] if xs is not None else correct
        if xs is not None:
            values = values.mean(-1)
        out = {}
        for t, name in [(1, 'copy'), (-1, 'subtract')]:
            mask = theta == t
            out[name + '_accuracy'] = ratio((values * mask).sum(1), mask.sum(1))
        return out

    out = {'run': run, 'rule_identification': {}, 'numeric': {}, 'contrasts': {}, 'header_bias_shift': {},
           'limitations': ['Operator identification is not TR label-space recognition.',
               'Exact candidate scores, not native free-generation accuracy.',
               'Code selection uses restricted candidates without gold; all error propagation retained.',
               'Explicit code adds computation and an instruction-following parameter field.',
               'Separate Rule query may induce computation absent from the numeric query.']}
    acc, stats, rule_correct = {}, {}, {}
    for scope in SCOPES:
        for order in ORDERS:
            key = scope + '.' + order
            r = [row['results'][key] for row in rows]
            rv = np.array([v['rule_logp'] for v in r])
            assert rv.shape == (n, 2, 2) and np.isfinite(rv).all()
            ridx = (theta != 1).astype(int)
            rule_margin = np.take_along_axis(rv, ridx[:, :, None], -1)[:, :, 0] - np.take_along_axis(rv, 1 - ridx[:, :, None], -1)[:, :, 0]
            rc = rule_margin > 0
            rule_correct[key] = rc
            choice = np.array([v['chosen'] for v in r])
            assert np.array_equal(choice, rv.argmax(-1))
            vocab_top1 = np.array([v['rule_vocab_top1'] for v in r])
            words = json.loads((d / 'preflight.json').read_text())['word_ids']
            out['rule_identification'][key] = {'accuracy': ci(rc.mean(1)), 'margin': ci(rule_margin.mean(1)),
                'candidate_mass': ci(np.exp(rv).sum(-1).mean(1)), 'vocab_top1_is_candidate': ci(np.isin(vocab_top1, words).mean(1)), **by_rule(rc)}
            for method in METHODS:
                nk = key + '.' + method
                v = np.array([z['numeric'][method] for z in r]).reshape(n, 2, 10, 10)
                assert np.isfinite(v).all()
                correct = np.take_along_axis(v, gold[:, :, :, None], -1)[:, :, :, 0]
                other = v.copy()
                np.put_along_axis(other, gold[:, :, :, None], -np.inf, -1)
                margin = correct - other.max(-1)
                acc[nk] = margin > 0
                pred = v.argmax(-1)
                vals = {'accuracy': acc[nk], 'margin': margin, 'demo_word_choice': np.isin(pred, [2, 7]),
                        'opposite_function_choice': pred == opposite, 'candidate_mass': np.exp(v).sum(-1)}
                if method in ['auto_code', 'gold_code', 'opposite_code']:
                    ct = np.where(choice == 0, 1, -1) if method == 'auto_code' else (theta if method == 'gold_code' else -theta)
                    cg = np.where(ct[:, :, None] == 1, x, 9 - x)
                    vals['code_adherence'] = pred == cg
                stats[nk] = vals
                out['numeric'][nk] = {group: {**{name: ci(value[:, :, xs].mean((1, 2))) for name, value in vals.items()},
                                                  **by_rule(acc[nk], xs)} for group, xs in GROUPS.items()}
        # An equally weighted two-order estimate reuses paired contexts.
        key = scope + '.both_orders'
        rc = np.mean([rule_correct[scope + '.' + order] for order in ORDERS], axis=0)
        out['rule_identification'][key] = {'accuracy': ci(rc.mean(1)), **by_rule(rc)}
        for method in METHODS:
            nk = key + '.' + method
            ac = np.mean([acc[scope + '.' + order + '.' + method] for order in ORDERS], axis=0)
            out['numeric'][nk] = {group: {'accuracy': ci(ac[:, :, xs].mean((1, 2))), **by_rule(ac, xs)} for group, xs in GROUPS.items()}

    comparisons = [('source_first_minus_input_first', 'source_first', 'input_first'),
                   ('auto_minus_empty', 'auto_code', 'empty_rule'),
                   ('auto_minus_source_first', 'auto_code', 'source_first')]
    for scope in SCOPES:
        for order in ORDERS + ['both_orders']:
            for label, ma, mb in comparisons:
                av = [acc[scope + '.' + o + '.' + ma] for o in ORDERS] if order == 'both_orders' else [acc[scope + '.' + order + '.' + ma]]
                bv = [acc[scope + '.' + o + '.' + mb] for o in ORDERS] if order == 'both_orders' else [acc[scope + '.' + order + '.' + mb]]
                delta = np.mean(av, axis=0) - np.mean(bv, axis=0)
                out['contrasts'][scope + '.' + order + '.' + label] = {g: ci(delta[:, :, xs].mean((1, 2))) for g, xs in GROUPS.items()}
        for method in METHODS:
            # A copy-minus-subtract accuracy bias for each definition order,
            # followed by the paired change after reversing the blocks.
            out['header_bias_shift'][scope + '.' + method] = {}
            for g, xs in GROUPS.items():
                order_bias = []
                for order in ORDERS:
                    rates = []
                    for t in [1, -1]:
                        mask = theta == t
                        values = acc[scope + '.' + order + '.' + method][:, :, xs].mean(-1)
                        rates.append(ratio_parts((values * mask).sum(1), mask.sum(1)))
                    order_bias.append((rates[0][0] - rates[1][0], rates[0][1] - rates[1][1]))
                out['header_bias_shift'][scope + '.' + method][g] = summarize(order_bias[1][0] - order_bias[0][0], order_bias[1][1] - order_bias[0][1])
    for label, sa, sb in [('single_minus_mixed', 'single', 'mixed'), ('scope_minus_mixed', 'mixed_scope', 'mixed')]:
        for method in METHODS:
            av = np.mean([acc[sa + '.' + o + '.' + method] for o in ORDERS], axis=0)
            bv = np.mean([acc[sb + '.' + o + '.' + method] for o in ORDERS], axis=0)
            out['contrasts'][label + '.' + method] = {g: ci((av[:, :, xs] - bv[:, :, xs]).mean((1, 2))) for g, xs in GROUPS.items()}
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    print(json.dumps({'identification': {k: v for k, v in out['rule_identification'].items() if k.endswith('both_orders')},
                      'numeric': {k: v for k, v in out['numeric'].items() if '.both_orders.' in k},
                      'contrasts': {k: v for k, v in out['contrasts'].items() if '.both_orders.' in k}}, indent=2))


if __name__ == '__main__':
    main()
