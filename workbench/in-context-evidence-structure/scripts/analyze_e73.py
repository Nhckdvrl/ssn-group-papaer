"""Censored answers on common trajectories; no survivor filtering."""
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
    assert run['prefix_mismatches'] == 0
    n = run['args']['n']
    rows = [json.loads(l) for l in (d / 'trajectories.jsonl').read_text().splitlines()]
    assert len(rows) == 16 * n * 3
    assert len({(r['uid'], r['interface']) for r in rows}) == len(rows)
    out = {'run': run, 'conditions': {}, 'budget_contrasts': {}, 'mode_contrasts': {}}
    metrics = {}
    for schema in ['source_only', 'orthogonal_prefix', 'entity_binding', 'single_source']:
        for interface in ['chat', 'chat_instruction', 'thinking_instruction']:
            rs = sorted([r for r in rows if r['schema'] == schema and r['interface'] == interface], key=lambda r: (r['context'], r['query']))
            assert len(rs) == 4 * n
            for horizon in ['96', '2048', '4096']:
                key = schema + '.' + interface + '.' + horizon
                vals = {
                    'accuracy': np.array([r['reads'][horizon]['prediction'] == r['gold'] for r in rs]).reshape(n, 4).mean(1),
                    'valid_format': np.array([r['reads'][horizon]['prediction'] >= 0 for r in rs]).reshape(n, 4).mean(1),
                    'truncated': np.array([r['reads'][horizon]['truncated'] for r in rs]).reshape(n, 4).mean(1),
                    'tokens': np.array([r['reads'][horizon]['tokens'] for r in rs]).reshape(n, 4).mean(1)}
                metrics[key] = vals
                out['conditions'][key] = {name: interval(v) for name, v in vals.items()}
            for short in ['96', '2048']:
                x = schema + '.' + interface + '.4096'
                y = schema + '.' + interface + '.' + short
                out['budget_contrasts'][schema + '.' + interface + '.4096_minus_' + short] = {name: interval(metrics[x][name] - metrics[y][name]) for name in metrics[x]}
        for horizon in ['96', '2048', '4096']:
            for label, x, y in [('instruction', 'chat_instruction', 'chat'), ('thinking', 'thinking_instruction', 'chat_instruction')]:
                kx = schema + '.' + x + '.' + horizon
                ky = schema + '.' + y + '.' + horizon
                out['mode_contrasts'][schema + '.' + label + '.' + horizon] = {name: interval(metrics[kx][name] - metrics[ky][name]) for name in metrics[kx]}
    out['limitations'] = ['Small context-only bootstrap; one sampled path per query/mode.',
                          'Budgets share exact trajectories; modes have different templates and independent samples.',
                          'Nonthinking outputs may contain natural-language analysis.',
                          'Censoring failures do not prove source-binding incapacity.']
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    for k, value in out['conditions'].items():
        if k.endswith('.4096'):
            print(k, {stat: val for stat, val in value.items() if stat != 'tokens'})
    print('mode_contrasts', out['mode_contrasts'])


if __name__ == '__main__':
    main()
