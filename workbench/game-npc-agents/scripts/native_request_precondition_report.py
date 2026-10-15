#!/usr/bin/env python3
"""E70 first physical disposition and prespecified graph-paired contrasts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from native_rule_cross_report import summarize
from native_request_precondition_execution import CONDITIONS, SEEDS


def metrics(row):
    history = row['history']
    valid = [h for h in history if h['legal'] and h.get('executed') and not h.get('stochastic_failure')]
    gives = [h for h in valid if h['event_type'] == 'GiveObjectEvent'
             and h['target_node_ids'][0] == row['goal_item_id']]
    assert len(gives) <= 1
    receiver = gives[0]['target_node_ids'][1] if gives else None
    assert receiver == row['first_recipient']
    if gives:
        h = gives[0]
        assert h['before'][row['goal_item_id']]['container'] == row['actor_id']
        assert h['after'][row['goal_item_id']]['container'] == receiver
        assert h is history[-1]
    goal = receiver == row['goal_recipient_id']
    competitor = receiver == row['competitor_id']
    other = receiver is not None and not goal and not competitor
    assert sum([goal, competitor, other, receiver is None]) == 1
    item = row['goal_item_id']
    remove = [h for h in valid if h['event_type'] == 'RemoveObjectEvent' and h['target_node_ids'][0] == item]
    source_drop = [h for h in valid if h['command'].startswith('drop ')
                   and h['before'][item]['container'] == row['actor_id']
                   and h['after'][item]['container'] != row['actor_id']]
    first = history[0] if history else None
    first_necessary = (bool(first and first in valid) and
                       (bool(first['source_item_give']) if row['state'] == 'ready' else
                        first['event_type'] == 'RemoveObjectEvent' and first['target_node_ids'][0] == item))
    stance = (row['conversation'] or {}).get('stance')
    result = {'to_goal': float(goal), 'to_competitor': float(competitor), 'to_other': float(other),
              'no_transfer': float(receiver is None), 'to_requester': float(row['requester_id'] is not None and receiver == row['requester_id']),
              'source_remove': float(bool(remove)), 'source_drop': float(bool(source_drop)),
              'source_consumed': float(any(h['event_type'] in ['EatEvent', 'DrinkEvent'] and h['target_node_ids'] and h['target_node_ids'][0] == item for h in valid)),
              'first_necessary_step': float(first_necessary),
              'optimal_goal_path': float(goal and len(history) == row['minimum_source_transfer_steps']),
              'resolved_within_2_actions': float(receiver is not None and len(history) <= 2),
              'first_transfer_step_capped9': float(len(history) if receiver is not None else 9),
              'native_goal_text_executed': float(row['native_goal_text_executed']),
              'other_item_give': float(any(h['event_type'] == 'GiveObjectEvent' and h['target_node_ids'][0] != item for h in valid)),
              'any_legal_block': float(any(h['event_type'] == 'BlockEvent' for h in valid)),
              'any_speech': float(any(h['command'].split()[0] in ['say', 'tell', 'whisper'] for h in valid)),
              'any_examine': float(any(h['command'].startswith('examine ') for h in valid)),
              'native_rejections': float(sum(not h['legal'] for h in history)),
              'stochastic_failures': float(sum(bool(h.get('stochastic_failure')) for h in history)),
              'protocol_error': float(bool(row['protocol_error'])), 'steps': float(len(history)),
              'budget_exhausted_without_transfer': float(receiver is None and len(history) == 8),
              'native_early_end_without_transfer': float(receiver is None and len(history) < 8 and not row['protocol_error'])}
    result.update({'stance_'+name: float(stance == name) for name in ['accept', 'decline', 'negotiate']})
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    sources = {r['case']['case_id']: r for r in map(json.loads, args.data.open())}
    lookup = {}; runtimes = []; manifests = []; calls = Counter(); files = {}
    for folder in args.runs:
        runtimes.append(json.loads((folder/'runtime.json').read_text()))
        manifests.append(json.loads((folder/'manifest.json').read_text()))
        for row in map(json.loads, (folder/'episodes.jsonl').open()):
            key = row['case_id'], row['seed'], row['persona'], row['condition']
            assert key not in lookup
            lookup[key] = row
        for row in map(json.loads, (folder/'model_calls.jsonl').open()):
            calls.update(count=1, parse_errors=int(bool(row['parse_error'])), prompt_tokens=row['prompt_tokens'], completion_tokens=row['completion_tokens'])
        files[str(folder/'episodes.jsonl')] = hashlib.sha256((folder/'episodes.jsonl').read_bytes()).hexdigest()
    assert all(m['script_sha256'] == manifests[0]['script_sha256'] and
               m['data_sha256'] == manifests[0]['data_sha256'] and m['model'] == manifests[0]['model'] for m in manifests)
    expected = {(cid, seed, persona, cond) for cid in sources for seed in SEEDS
                for persona in ['firm', 'agreeable'] for cond in CONDITIONS}
    assert set(lookup) == expected and len(lookup) == 6318
    for cid, seed, persona, cond in lookup:
        if cond.endswith('_staged'):
            assert lookup[cid, seed, persona, cond]['conversation'] == lookup[cid, seed, persona, cond.removesuffix('_staged')]['conversation']
    values = {key: metrics(row) for key, row in lookup.items()}
    fields = list(next(iter(values.values())))

    def estimate(terms):
        matrix = [np.mean([[sum(w*values[cid, seed, persona, cond][field] for w, persona, cond in terms)
                            for field in fields] for seed in SEEDS], axis=0)
                  for cid in sorted(sources)]
        return summarize(matrix, fields)

    cells = {}; contrasts = {}
    for cond in CONDITIONS:
        for persona in ['firm', 'agreeable']:
            cells[persona+'/'+cond] = estimate([(1, persona, cond)])
        contrasts['A_minus_F/'+cond] = estimate([(1, 'agreeable', cond), (-1, 'firm', cond)])
    for state in ['ready', 'equipped']:
        aligned, divert = state+'_aligned', state+'_divert'
        for persona in ['firm', 'agreeable']:
            contrasts[persona+'/divert_minus_aligned/'+state] = estimate([(1, persona, divert), (-1, persona, aligned)])
        contrasts['persona_x_direction/'+state] = estimate([(1, 'agreeable', divert), (-1, 'firm', divert),
                                                            (-1, 'agreeable', aligned), (1, 'firm', aligned)])
    for direction in ['aligned', 'divert']:
        for persona in ['firm', 'agreeable']:
            eq = 'equipped_'+direction; ready = 'ready_'+direction
            contrasts[persona+'/equipped_minus_ready/'+direction] = estimate([(1, persona, eq), (-1, persona, ready)])
            for suffix in ['mechanics', 'staged']:
                contrasts[persona+'/'+suffix+'_minus_baseline/'+direction] = estimate([(1, persona, eq+'_'+suffix), (-1, persona, eq)])
    for persona in ['firm', 'agreeable']:
        contrasts[persona+'/priority_minus_baseline/divert'] = estimate([(1, persona, 'equipped_divert_priority'), (-1, persona, 'equipped_divert')])
    contrasts['persona_x_direction_x_state'] = estimate([
        (1, 'agreeable', 'equipped_divert'), (-1, 'firm', 'equipped_divert'),
        (-1, 'agreeable', 'equipped_aligned'), (1, 'firm', 'equipped_aligned'),
        (-1, 'agreeable', 'ready_divert'), (1, 'firm', 'ready_divert'),
        (1, 'agreeable', 'ready_aligned'), (-1, 'firm', 'ready_aligned')])
    # All paired outcomes remain accessible; this report never selects favorable seeds.
    paired_changes = {}
    for suffix in ['mechanics', 'staged']:
        for direction in ['aligned', 'divert']:
            for persona in ['firm', 'agreeable']:
                baseline = 'equipped_'+direction; treatment = baseline+'_'+suffix
                counter = Counter()
                for cid in sources:
                    for seed in SEEDS:
                        a = values[cid, seed, persona, baseline]; b = values[cid, seed, persona, treatment]
                        for metric in ['to_goal', 'to_competitor', 'no_transfer']:
                            counter[metric+'/gained'] += int(b[metric] > a[metric])
                            counter[metric+'/lost'] += int(b[metric] < a[metric])
                paired_changes[persona+'/'+direction+'/'+suffix] = dict(counter)
    result = {'status': 'COMPLETE', 'experiment': 'E70', 'model': manifests[0]['model'],
              'worlds': len(sources), 'episodes': len(lookup), 'cells': cells, 'contrasts': contrasts,
              'paired_outcome_changes': paired_changes, 'actual_calls': dict(calls),
              'runtime_gpu_hours': sum(r['wall_seconds']+r['model_load_seconds'] for r in runtimes)/3600,
              'runtimes': runtimes, 'reused_calls': sum(r['reused_calls'] for r in runtimes),
              'native_errors': dict(Counter(h.get('error', '') for r in lookup.values() for h in r['history'] if not h['legal'])),
              'stochastic_failures': sum(bool(h.get('stochastic_failure')) for r in lookup.values() for h in r['history']),
              'source_sha256': files, 'data_sha256': manifests[0]['data_sha256'],
              'scope': ['First disposition of exact original item, not whole-episode utility or irreversible loss.',
                        'Aligned request and authored goal share a recipient; they are not independent successes.',
                        'Legal equip/unequip also changes native stats; a state effect is not pure extra-step cognition.',
                        'Speaker identity/relationship changes with alignment; no abstract-utility or neural attribution.',
                        'Three seeds averaged within graph; 4000 paired graph bootstrap resamples; pointwise intervals.']}
    assert calls['count'] == sum(r['calls'] for r in runtimes)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['status', 'worlds', 'episodes', 'actual_calls', 'runtime_gpu_hours']}), flush=True)


if __name__ == '__main__':
    main()
