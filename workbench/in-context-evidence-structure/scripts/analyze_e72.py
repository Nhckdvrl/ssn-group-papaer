"""Keep native generation, conditional choice, and format failures separate."""
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
    assert run['sanity_max_error'] <= .1 and run['token_sum_error_max'] <= 1e-5
    scores = [json.loads(l) for l in (d / 'scores.jsonl').read_text().splitlines()]
    generations = [json.loads(l) for l in (d / 'generations.jsonl').read_text().splitlines()]
    n = run['args']['n']
    schemas = ['source_only', 'linked_prefix', 'orthogonal_prefix', 'entity_binding', 'single_source']
    assert len(scores) == n * 4 * len(schemas) * 4
    assert len(generations) == n * 4 * len(schemas) * 3
    assert len({(r['uid'], r['interface']) for r in scores}) == len(scores)
    assert len({(r['uid'], r['interface']) for r in generations}) == len(generations)
    out = {'run': run, 'candidate': {}, 'generation': {}, 'candidate_contrasts': {}, 'generation_contrasts': {}}
    cmetrics, gmetrics = {}, {}
    for schema in schemas:
        for interface in ['raw', 'raw_instruction', 'chat', 'chat_instruction']:
            rs = sorted([r for r in scores if r['schema'] == schema and r['interface'] == interface], key=lambda r: (r['context'], r['query']))
            assert len(rs) == n * 4
            v = np.array([r['candidate_lp'][1] - r['candidate_lp'][0] for r in rs]).reshape(n, 4)
            signs = np.array([2 * r['gold'] - 1 for r in rs]).reshape(n, 4)
            assert np.array_equal(signs[:, :2], -signs[:, 2:])
            vals = {'margin': (v * signs).mean(1), 'accuracy': (v * signs > 0).mean(1),
                    'source_ranking': ((v[:, :2] - v[:, 2:]) * signs[:, :2] > 0).mean(1)}
            key = schema + '.' + interface
            cmetrics[key] = vals
            out['candidate'][key] = {k: interval(x) for k, x in vals.items()}
        for interface in ['chat', 'chat_instruction', 'thinking_instruction']:
            rs = sorted([r for r in generations if r['schema'] == schema and r['interface'] == interface], key=lambda r: (r['context'], r['query']))
            assert len(rs) == n * 4
            vals = {'accuracy': np.array([r['prediction'] == r['gold'] for r in rs]).reshape(n, 4).mean(1),
                    'valid_format': np.array([r['prediction'] >= 0 for r in rs]).reshape(n, 4).mean(1),
                    'truncated': np.array([r['truncated'] for r in rs]).reshape(n, 4).mean(1),
                    'tokens': np.array([r['tokens'] for r in rs]).reshape(n, 4).mean(1)}
            key = schema + '.' + interface
            gmetrics[key] = vals
            out['generation'][key] = {k: interval(x) for k, x in vals.items()}
        for name, x, y in [('chat_minus_raw', 'chat', 'raw'), ('raw_instruction', 'raw_instruction', 'raw'), ('chat_instruction', 'chat_instruction', 'chat')]:
            out['candidate_contrasts'][schema + '.' + name] = {k: interval(cmetrics[schema + '.' + x][k] - cmetrics[schema + '.' + y][k]) for k in ['margin', 'accuracy', 'source_ranking']}
        for name, x, y in [('instruction', 'chat_instruction', 'chat'), ('thinking', 'thinking_instruction', 'chat_instruction')]:
            out['generation_contrasts'][schema + '.' + name] = {k: interval(gmetrics[schema + '.' + x][k] - gmetrics[schema + '.' + y][k]) for k in ['accuracy', 'valid_format', 'truncated', 'tokens']}
    out['limitations'] = ['Context bootstrap only; one sampled response per query and fixed decode protocol.',
                          'Conditional Answer-prefill choices and unconstrained generation accuracy are separate.',
                          'Qwen models share developer lineage; this is not a frontier or cross-developer proof.',
                          'Thinking truncation is a budget limit, not evidence of inability.']
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    print('candidate', {k: v for k, v in out['candidate'].items() if k.startswith('source_only.') or k.endswith('.raw')})
    print('generation', out['generation'])


if __name__ == '__main__':
    main()
