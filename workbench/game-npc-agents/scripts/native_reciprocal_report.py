#!/usr/bin/env python3
"""E64 actual reciprocal transfers, resource attainment and downstream harm."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


def metrics(row, case):
    actors, items = case['actor_ids'], case['goal_item_ids']
    gifts, acquired = [[], []], [[], []]
    harm_by = [0, 0]
    for turn in row['turns']:
        ok = turn.get('legal') and turn.get('executed') and not turn.get('stochastic_failure')
        for i, (actor, item) in enumerate(zip(actors, items)):
            before = turn['before'].get(item, {}).get('container')
            after = turn['after'].get(item, {}).get('container')
            if before != actor and after == actor:
                acquired[i].append({'turn': turn['turn'], 'method': turn['event_type'], 'by': turn['index']})
            if ok and turn['event_type'] == 'GiveObjectEvent' and turn['index'] == 1-i and before == actors[1-i] and after == actor:
                gifts[1-i].append(turn['turn'])
        j = turn['index']
        harm_by[j] += max(0, turn['health_before'][1-j] - turn['health_after'][1-j])
    first_out = min(gifts[0]) if gifts[0] else None
    first_in = min(x['turn'] for x in acquired[0]) if acquired[0] else None
    outgoing_before_return = first_out is not None and (first_in is None or first_out < first_in)
    out = {'both_resources_ever_attained': float(all(row['ever_attained'])),
           'both_resources_finally_held': float(all(row['final_attained'])),
           'actual_two_way_give': float(bool(gifts[0]) and bool(gifts[1])),
           'focal_outgoing_give_before_acquisition': float(outgoing_before_return),
           'focal_outgoing_give_without_any_acquisition': float(bool(gifts[0]) and not row['ever_attained'][0]),
           'any_death': float(any(row['final_dead'])),
           'protocol_error': float(bool(row['protocol_error'])),
           'physical_turns': float(sum(t['turn'] >= 0 for t in row['turns']))}
    for i, name in enumerate(['focal', 'partner']):
        first = min((t['turn'] for t in row['turns'] if t['attained_after'][i]), default=32)
        own_turns = [t for t in row['turns'] if t['turn'] >= 0 and t['index'] == i]
        out.update({name+'_resource_ever_attained': float(row['ever_attained'][i]),
                    name+'_resource_finally_held': float(row['final_attained'][i]),
                    name+'_strict_goal_event': float(row['strict_goal_done'][i]),
                    name+'_goal_asset_gifted_to_partner': float(bool(gifts[i])),
                    name+'_hp_change': float(row['final_health'][i] - row['initial_state'][actors[i]]['health']),
                    name+'_damage_inflicted': float(harm_by[i]),
                    name+'_dead': float(row['final_dead'][i]),
                    name+'_first_acquisition_turn_capped32_POST_HOC': float(first),
                    name+'_pre_acquisition_emotes_POST_HOC': float(sum(t['event_type'] == 'EmoteEvent' and t['turn'] < first for t in own_turns)),
                    name+'_pre_acquisition_speech_POST_HOC': float(sum(t['event_type'] in ['SayEvent', 'TellEvent', 'WhisperEvent', 'ShoutEvent'] and t['turn'] < first for t in own_turns)),
                    name+'_non_speech_nonempty_utterance_POST_HOC': float(sum(
                        t['command'].split(' ', 1)[0] not in ['say', 'tell', 'whisper', 'shout']
                        and bool(t.get('choice', {}).get('utterance', '').strip()) for t in own_turns)),
                    name+'_theft_attempts_POST_HOC': float(sum(t['event_type'] == 'StealObjectEvent' for t in own_turns)),
                    name+'_successful_target_theft': float(any(x['method'] == 'StealObjectEvent' and x['by'] == i for x in acquired[i]))})
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--directory', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True); ap.add_argument('--profile', action='store_true')
    a = ap.parse_args()
    m = json.loads((a.directory / 'manifest.json').read_text())
    rt = json.loads((a.directory / 'runtime.json').read_text())
    rows = list(map(json.loads, (a.directory / 'episodes.jsonl').read_text().splitlines()))
    cases = {c['case_id']: c for c in map(json.loads, Path(m['arguments']['dataset']).read_text().splitlines())}
    ids, seeds = set(m['case_ids']), m['arguments']['seeds']
    assert len(ids) == (1 if a.profile else 9)
    assert a.profile == m['arguments']['profile']
    lookup = {(r['case_id'], r['seed'], r['persona'], r['cue']): r for r in rows}
    expected = {(cid, s, p, cue) for cid in ids for s in seeds for p in m['traits'] for cue in m['cues']}
    assert len(lookup) == len(rows) and set(lookup) == expected
    data = {k: metrics(r, cases[r['case_id']]) for k, r in lookup.items()}
    fields = list(next(iter(data.values())))
    report = {'scope': 'N=1 cost/closure profile' if a.profile else 'Nine-source-world exploratory native negotiation pilot',
              'manifest': m, 'runtime': rt, 'worlds': len(ids), 'episodes': len(rows),
              'cells': {}, 'persona_contrasts': {}, 'cue_contrasts': {}, 'per_case': {},
              'protocol_errors': sum(bool(r['protocol_error']) for r in rows),
              'engine_rejections': dict(Counter(t.get('error', 'unspecified') for r in rows for t in r['turns'] if not t['legal'])),
              'stochastic_failures': sum(bool(t.get('stochastic_failure')) for r in rows for t in r['turns']),
              'stop_reasons': dict(Counter(r['stop'] for r in rows)), 'native_action_counts_POST_HOC': {}}

    def cell(gs, p, cue):
        return {f: estimate([np.mean([data[cid, s, p, cue][f] for s in seeds]) for cid in sorted(gs)]) for f in fields}

    def contrast(left, right):
        return {f: estimate([np.mean([data[(cid, s, *left)][f] - data[(cid, s, *right)][f] for s in seeds])
                             for cid in sorted(ids)]) for f in fields}

    for p in m['traits']:
        for cue in m['cues']:
            report['cells'][p+'/'+cue] = cell(ids, p, cue)
            report['native_action_counts_POST_HOC'][p+'/'+cue] = {name: dict(Counter(t['event_type']
                for r in rows if r['persona'] == p and r['cue'] == cue
                for t in r['turns'] if t['turn'] >= 0 and t['index'] == i))
                for i, name in enumerate(['focal', 'partner'])}
        if 'check' in m['cues']:
            report['cue_contrasts'][p] = contrast((p, 'check'), (p, 'none'))
    for cue in m['cues']:
        report['persona_contrasts'][cue] = contrast(('agreeable', cue), ('firm', cue))
    for cid in sorted(ids):
        report['per_case'][cid] = {'goals': [q['goal'] for q in cases[cid]['quests']],
            'cells': {p+'/'+cue: {f: np.mean([data[cid, s, p, cue][f] for s in seeds]) for f in fields}
                      for p in m['traits'] for cue in m['cues']}}
    calls = list(map(json.loads, (a.directory / 'model_calls.jsonl').read_text().splitlines()))
    assert len(calls) == rt['calls']
    new_count = len(calls); prior_count = 0
    if m.get('resumed_from'):
        previous = list(map(json.loads, (Path(m['resumed_from'])/'model_calls.jsonl').read_text().splitlines()))
        assert len(previous) == rt['prior_run']['calls']
        prior_count = len(previous); calls = previous+calls
    report['calls'] = {'count': len(calls), 'new_count': new_count, 'prior_count': prior_count,
        'replayed_prior_decisions': rt.get('replayed_prior_decisions', 0),
        'parse_errors': sum(bool(r['parse_error']) for r in calls),
        'prompt_tokens': sum(r['prompt_tokens'] for r in calls), 'completion_tokens': sum(r['completion_tokens'] for r in calls)}
    report['raw_sha256'] = hashlib.sha256((a.directory / 'episodes.jsonl').read_bytes()).hexdigest()
    report['interpretation'] = ['Both target resources can enable hostile private motivations; ownership is not welfare.',
        'A successful exchange can coexist with later attack, resource loss or death, all retained.',
        'Opening is shared across focal cells; both action policies respond to actual observable history.',
        'This is a source-specific N=9 pilot, not a population benchmark or an intervention isolating pretraining origins.',
        'No semantic API labels; conditional language is inspected alongside physical transfers, not used as an automatic success score.']
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['scope', 'worlds', 'episodes', 'protocol_errors', 'stochastic_failures', 'stop_reasons', 'calls']}))


if __name__ == '__main__': main()
