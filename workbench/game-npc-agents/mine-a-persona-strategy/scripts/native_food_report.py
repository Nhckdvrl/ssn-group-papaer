#!/usr/bin/env python3
"""E57 native endpoints and acquisition paths; world-clustered, every seed kept."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import numpy as np
from commitment_behavior_report import estimate


def target_command(turn, name):
    return bool(re.search(r'(?<!\w)' + re.escape(name.lower()) + r'(?!\w)', turn['command'].lower()))


def metrics(r, c):
    name = json.loads(c['quests'][0]['graph'])['nodes'][c['item_id']]['name']
    focal, partner = c['actor_ids']; transitions = []; thefts = []
    for t in r['turns']:
        if t['turn'] < 0: continue
        old = t['before'].get(c['item_id'], {}); new = t['after'].get(c['item_id'], {})
        if old.get('container') != focal and new.get('container') == focal:
            transitions.append({'turn': t['turn'], 'actor': t['index'], 'method': t['event_type']})
        if t['index'] == 0 and t['command'].startswith('steal ') and target_command(t, name): thefts.append(t)
    consumed = [t for t in r['turns'] if t['event_type'] in ['EatEvent', 'DrinkEvent'] and target_command(t, name)
                and t.get('executed') and not t.get('stochastic_failure')]
    assert len(consumed) <= 1
    # POST-HOC source correction: switch/quest.py also accepts partner Give for
    # the controlled character's Get/Steal goal. Preserve strict event flags.
    attained = list(r['goal_done'])
    for i, q in enumerate(c['quests']):
        if q['goal'].split()[0] not in ['get', 'steal']: continue
        recipient = c['actor_ids'][i]
        attained[i] = attained[i] or any(t['index'] != i and t['event_type'] == 'GiveObjectEvent'
            and t.get('executed') and not t.get('stochastic_failure')
            and t['after'][c['item_id']]['container'] == recipient
            and t['before'][c['item_id']]['container'] != recipient for t in r['turns'])
    harm_to_partner = sum(max(0, t['before'].get(partner, {}).get('health', 0) - t['after'].get(partner, {}).get('health', 0))
                          for t in r['turns'] if t['index'] == 0)
    return {'focal_consumed': float(r['consumer'] == 0), 'partner_consumed': float(r['consumer'] == 1),
            'unconsumed': float(r['consumer'] is None), 'focal_goal_event': float(r['goal_done'][0]),
            'partner_goal_event': float(r['goal_done'][1]), 'both_goal_events': float(all(r['goal_done'])),
            'focal_attainment_with_source_reverse': float(attained[0]),
            'partner_attainment_with_source_reverse': float(attained[1]),
            'both_attainment_with_source_reverse': float(all(attained)),
            'consumption_turns_capped24': float(consumed[0]['turn'] + 1 if consumed else 24),
            'focal_target_theft_attempted': float(bool(thefts)),
            'focal_target_theft_succeeded': float(any(t.get('executed') and not t.get('stochastic_failure') for t in thefts)),
            'partner_handover_to_focal': float(any(t['actor'] == 1 and t['method'] == 'GiveObjectEvent' for t in transitions)),
            'focal_first_acquisition': transitions[0]['method'] if transitions else 'initially_held' if c['initial_holder'] == focal else 'no_acquisition',
            'focal_first_acquisition_by': transitions[0]['actor'] if transitions else None,
            'harm_to_partner_by_focal': float(harm_to_partner),
            'focal_health_change': float(r['final_state'][focal].get('health', 0) - r['initial_state'][focal].get('health', 0))}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--directories', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    rows = []; ids = set(); manifests = []; runtimes = []; calls = []
    for d in a.directories:
        m = json.loads((d / 'manifest.json').read_text()); rt = json.loads((d / 'runtime.json').read_text())
        assert not ids.intersection(m['case_ids']); ids.update(m['case_ids']); manifests.append(m); runtimes.append(rt)
        rows.extend(map(json.loads, (d / 'episodes.jsonl').read_text().splitlines()))
        calls.extend(map(json.loads, (d / 'model_calls.jsonl').read_text().splitlines()))
    ref = manifests[0]
    for m in manifests:
        for key in ['dataset_sha256', 'script_sha256', 'personas', 'max_action_turns']: assert m[key] == ref[key], key
        for key in ['model', 'seeds', 'dataset', 'shards']: assert m['arguments'][key] == ref['arguments'][key], key
    seeds = ref['arguments']['seeds']
    cases = {c['case_id']: c for c in map(json.loads, Path(ref['arguments']['dataset']).read_text().splitlines())}
    assert len(cases) == len(ids) == 39 and len(rows) == 234
    lookup = {(r['case_id'], r['seed'], r['persona']): r for r in rows}; assert len(lookup) == len(rows)
    computed = {k: metrics(r, cases[r['case_id']]) for k, r in lookup.items()}
    fields = [k for k in next(iter(computed.values())) if k not in ['focal_first_acquisition', 'focal_first_acquisition_by']]
    report = {'manifests': manifests, 'runtimes': runtimes, 'graphs': 39, 'episodes': 234,
              'cells': {}, 'persona_contrasts': {}, 'initial_holder_strata_POST_HOC': {}, 'paired_outcomes': {},
              'protocol_errors': sum(bool(r['protocol_error']) for r in rows),
              'engine_rejections': dict(Counter(t.get('error', 'unspecified') for r in rows for t in r['turns'] if not t['legal']))}
    for p in ['firm', 'agreeable']:
        bygraph = {cid: [computed[cid, s, p] for s in seeds] for cid in sorted(ids)}
        report['cells'][p] = {f: estimate([np.mean([x[f] for x in xs]) for xs in bygraph.values()]) for f in fields}
        report['cells'][p]['first_acquisition'] = dict(Counter(computed[cid, s, p]['focal_first_acquisition'] for cid in ids for s in seeds))
        report['cells'][p]['stops'] = dict(Counter(lookup[cid, s, p]['stop'] for cid in ids for s in seeds))
    def diff(gs, f):
        return estimate([np.mean([computed[cid, s, 'agreeable'][f] - computed[cid, s, 'firm'][f] for s in seeds]) for cid in sorted(gs)])
    report['persona_contrasts'] = {f: diff(ids, f) for f in fields}
    for category in ['focal', 'partner', 'other']:
        gs = {cid for cid in ids if ('focal' if cases[cid]['initial_holder'] == cases[cid]['actor_ids'][0] else
                                    'partner' if cases[cid]['initial_holder'] == cases[cid]['actor_ids'][1] else 'other') == category}
        report['initial_holder_strata_POST_HOC'][category] = {'graphs': len(gs), 'contrasts': {f: diff(gs, f) for f in fields}}
    report['paired_outcomes'] = dict(Counter(str((lookup[cid, s, 'firm']['consumer'], lookup[cid, s, 'agreeable']['consumer'])) for cid in ids for s in seeds))
    report['calls'] = {'count': len(calls), 'parse_errors': sum(bool(r['parse_error']) for r in calls),
                       'prompt_tokens': sum(r['prompt_tokens'] for r in calls), 'completion_tokens': sum(r['completion_tokens'] for r in calls)}
    assert len(calls) == sum(rt['calls'] for rt in runtimes)
    report['raw_sha256'] = {str(d): hashlib.sha256((d / 'episodes.jsonl').read_bytes()).hexdigest() for d in a.directories}
    report['scope'] = ['Source two-quest pairings, not the original retrieval partner training.',
        'Food consumption and health are native physical facts; original goal event flags are not total long-term welfare.',
        'POST-HOC source reverse attainment adds partner Give for Get/Steal, as switch/quest.py reverse_task; strict event statistics are preserved. This is not the full original DM/RL scorer.',
        'Initial-holder strata are POST-HOC cross-world comparisons, not causal interventions on ownership.',
        'Restricted consumption timing caps unresolved episodes at 24 action turns and is not wall-clock latency.',
        'Persona total effects include the responsive partner, not separately identified dialogue mediation.']
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'graphs': 39, 'episodes': 234, 'contrasts': report['persona_contrasts'], 'calls': report['calls']}))


if __name__ == '__main__': main()
