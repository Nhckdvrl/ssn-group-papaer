#!/usr/bin/env python3
"""Graph-paired E53 estimates across strict nonoverlapping completed shards."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--directories', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    rows, manifests, runtimes = [], [], []
    ids = set()
    for d in a.directories:
        m = json.loads((d/'manifest.json').read_text())
        rt = json.loads((d/'runtime.json').read_text())
        assert not ids.intersection(m['case_ids']), 'overlapping shards'
        ids.update(m['case_ids'])
        rows.extend(map(json.loads, (d/'branches.jsonl').read_text().splitlines()))
        manifests.append(m); runtimes.append(rt)
    ref = manifests[0]
    for m in manifests:
        for k in ['conditions', 'personas', 'source_dialogue_sha256', 'script_sha256']:
            assert m[k] == ref[k], k
        for k in ['seeds', 'model', 'dataset', 'source']:
            assert m['arguments'][k] == ref['arguments'][k], k
    seeds = ref['arguments']['seeds']; conditions = ref['conditions']
    lookup = {(r['case_id'], r['seed'], r['persona'], r['condition']): r for r in rows}
    assert len(lookup) == len(rows) == len(ids)*len(seeds)*2*len(conditions)
    report = {'manifests': manifests, 'runtimes': runtimes, 'graphs': len(ids),
              'branches': len(rows), 'cells': {}, 'contrasts': {}, 'stance_strata': {},
              'protocol_errors': sum(bool(r['protocol_error']) for r in rows),
              'illegal_actions': sum(not h['legal'] for r in rows for h in r['history']),
              'scope': 'first allocation/consumption/equipment within six native actions; not total utility'}
    def graph_est(rs, metric):
        g = defaultdict(list)
        for r in rs: g[r['case_id']].append(metric(r))
        return estimate([np.mean(v) for v in g.values()])
    req = lambda r: float(r['flags']['request'])
    own = lambda r: float(r['flags']['own_task'])
    for p in ['firm', 'agreeable']:
        for c in conditions:
            rs = [r for r in rows if r['persona'] == p and r['condition'] == c]
            report['cells'][p+'/'+c] = {'branches': len(rs),
                'request_count': sum(req(r) for r in rs), 'own_count': sum(own(r) for r in rs),
                'request': graph_est(rs, req), 'own_task': graph_est(rs, own),
                'steps': graph_est(rs, lambda r: r['steps']),
                'stances': dict(Counter(r['conversation']['stance'] for r in rs))}
        for left, right in [('own_executed', 'both_unexecuted'),
                            ('request_executed', 'both_unexecuted'),
                            ('own_executed_truth', 'both_unexecuted'),
                            ('request_executed_truth', 'both_unexecuted'),
                            ('own_executed_truth', 'own_executed'),
                            ('request_executed_truth', 'request_executed'),
                            ('both_unexecuted', 'none')]:
            points = []
            for cid in sorted(ids):
                points.append(np.mean([req(lookup[(cid, s, p, left)])-req(lookup[(cid, s, p, right)]) for s in seeds]))
            report['contrasts'][p+'/'+left+'-'+right] = estimate(points)
        for stance in ['accept', 'decline', 'negotiate']:
            for c in conditions:
                rs = [r for r in rows if r['persona'] == p and r['condition'] == c and r['conversation']['stance'] == stance]
                report['stance_strata'][p+'/'+stance+'/'+c] = {'branches': len(rs), 'request': graph_est(rs, req), 'own_task': graph_est(rs, own)}
    for c in conditions:
        points = [np.mean([req(lookup[(cid, s, 'agreeable', c)])-req(lookup[(cid, s, 'firm', c)]) for s in seeds]) for cid in sorted(ids)]
        report['contrasts']['persona/'+c] = estimate(points)
    calls = []
    for d in a.directories: calls.extend(map(json.loads, (d/'model_calls.jsonl').read_text().splitlines()))
    report['calls'] = {'count': len(calls), 'parse_errors': sum(bool(r['parse_error']) for r in calls),
                       'prompt_tokens': sum(r['prompt_tokens'] for r in calls),
                       'completion_tokens': sum(r['completion_tokens'] for r in calls)}
    report['branch_sha256'] = {str(d): hashlib.sha256((d/'branches.jsonl').read_bytes()).hexdigest() for d in a.directories}
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'graphs': len(ids), 'branches': len(rows), 'contrasts': report['contrasts'], 'protocol_errors': report['protocol_errors']}))


if __name__ == '__main__': main()
