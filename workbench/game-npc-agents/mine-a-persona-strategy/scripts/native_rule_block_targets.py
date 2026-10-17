#!/usr/bin/env python3
"""POST-HOC: identify recipients of native blocking without changing the block endpoint."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    sources = {r['case']['case_id']: r['case'] for r in map(json.loads, a.dataset.read_text().splitlines())}
    groups, graphs = defaultdict(Counter), defaultdict(set)
    for folder in a.runs:
        assert (folder / 'runtime.json').exists(), 'Only completed queues are analyzed.'
        for line in (folder / 'episodes.jsonl').open():
            row = json.loads(line)
            if row['mode'] != 'goal_item':
                continue
            case = sources[row['case_id']]
            blocks = [h for h in row['history'] if h['legal'] and h.get('executed')
                      and not h.get('stochastic_failure') and h['event_type'] == 'BlockEvent']
            targets = [h['after'][case['actor_id']]['blocking'] for h in blocks]
            assert all(targets)
            for scope in ['all'] + (['wear_wield'] if case['goal_kind'] in ['wear', 'wield'] else []):
                key = '/'.join([scope, row['persona'], row['upstream_rule'], row['exec_rule'], row['feedback']])
                groups[key].update(episodes=1, legal_block_events=len(blocks),
                    requester_block_events=sum(t == case['requester_id'] for t in targets),
                    other_block_events=sum(t != case['requester_id'] for t in targets),
                    episodes_requester_block=int(case['requester_id'] in targets),
                    episodes_other_block=int(any(t != case['requester_id'] for t in targets)),
                    first_step_requester_block=int(any(h['step'] == 0 and t == case['requester_id'] for h,t in zip(blocks,targets))),
                    first_step_other_block=int(any(h['step'] == 0 and t != case['requester_id'] for h,t in zip(blocks,targets))))
                graphs[key].add(row['case_id'])
    result = {'analysis': 'POST-HOC native block-target identity; original endpoints unchanged; no utility judgment.',
              'cells': {key: dict(counts, independent_graphs=len(graphs[key])) for key,counts in groups.items()},
              'dataset_sha256': hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
              'source_runs': list(map(str,a.runs)), 'model_calls': 0}
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
