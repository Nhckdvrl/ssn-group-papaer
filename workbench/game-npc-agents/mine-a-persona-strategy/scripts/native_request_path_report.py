#!/usr/bin/env python3
"""Descriptive E70/E71 trajectory taxonomy, with no language judge or new inference."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from native_request_precondition_report import metrics


def outcome(row):
    m = metrics(row)
    return next(k for k in ['to_goal', 'to_competitor', 'to_other', 'no_transfer'] if m[k])


def path(row):
    events = []
    for h in row['history']:
        if not h['legal'] or not h.get('executed'):
            events.append('rejected:'+h['command'].split()[0]); continue
        if h.get('stochastic_failure'):
            events.append('native_failed:'+h['event_type']); continue
        if h['source_item_give']:
            events.append(outcome(row)); continue
        ids = h.get('target_node_ids', [])
        name = h['event_type']
        if name in ['RemoveObjectEvent', 'EquipObjectEvent', 'WearEvent', 'WieldEvent', 'DropObjectEvent', 'EatEvent', 'DrinkEvent', 'GiveObjectEvent']:
            name += '/source' if ids and ids[0] == row['goal_item_id'] else '/other'
        events.append(name)
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--case-lines', type=Path, required=True)
    args = ap.parse_args(); rows = []; lookup = {}; cells = defaultdict(list)
    for folder in args.runs:
        assert (folder/'runtime.json').exists()
        for r in map(json.loads, (folder/'episodes.jsonl').open()):
            key = r['case_id'], r['seed'], r['persona'], r['condition']
            assert key not in lookup; lookup[key] = r; rows.append(r)
            cells[r['persona']+'/'+r['condition']].append(r)
    summaries = {}
    for cell, group in cells.items():
        counts = Counter(); sequences = Counter(); no_give = Counter(); worlds = defaultdict(set)
        event_episodes = Counter(); event_steps = Counter(); first_events = Counter(); failed_events = Counter()
        for r in group:
            m = metrics(r); o = outcome(r); events = path(r)
            counts[o] += 1; worlds[o].add(r['case_id'])
            sequences[' > '.join(events)] += 1
            legal_events = [h['event_type'] for h in r['history'] if h['legal'] and h.get('executed') and not h.get('stochastic_failure')]
            event_steps.update(legal_events)
            event_episodes.update(set(legal_events))
            failed_events.update(h['event_type'] for h in r['history'] if h.get('stochastic_failure'))
            if events: first_events[events[0]] += 1
            if o == 'no_transfer':
                category = ('source_consumed' if m['source_consumed'] else 'source_dropped' if m['source_drop'] else
                            'removed_without_give' if m['source_remove'] else
                            'still_equipped_without_remove' if r['state'] == 'equipped' and r['final_item_equipped'] else
                            'other_no_give')
                no_give[category] += 1
            stance = (r['conversation'] or {}).get('stance')
            if stance:
                counts['stance_'+stance] += 1
                counts['stance_'+stance+'/'+o] += 1
            if r.get('update'):
                for action in r['update'].get('priority_actions', []):
                    if action.startswith('remove '):
                        counts['plan_mentions_remove'] += 1
                        counts['plan_mentions_remove/'+('removed' if m['source_remove'] else 'not_removed')] += 1
                        break
        summaries[cell] = {'episodes': len(group), 'counts': dict(counts),
                           'distinct_graphs_by_outcome': {k: len(v) for k, v in worlds.items()},
                           'no_selected_give_categories': dict(no_give),
                           'legal_event_episode_counts': dict(event_episodes),
                           'legal_event_step_counts': dict(event_steps),
                           'first_event_counts': dict(first_events),
                           'native_failed_event_counts': dict(failed_events),
                           'most_common_paths': sequences.most_common(12)}
    transitions = {}; examples = {}
    for suffix in ['mechanics', 'staged']:
        for direction in ['aligned', 'divert']:
            for persona in ['firm', 'agreeable']:
                base = 'equipped_'+direction; treatment = base+'_'+suffix
                name = persona+'/'+direction+'/'+suffix; counter = Counter(); samples = defaultdict(list)
                for key in sorted(lookup):
                    cid, seed, p, cond = key
                    if p != persona or cond != base: continue
                    a, b = lookup[key], lookup[cid, seed, p, treatment]
                    transition = outcome(a)+' -> '+outcome(b); counter[transition] += 1
                    if len(samples[transition]) < 3:
                        samples[transition].append({'case_id': cid, 'seed': seed,
                                                   'baseline': path(a), 'treatment': path(b)})
                transitions[name] = dict(counter); examples[name] = dict(samples)
    args.case_lines.parent.mkdir(exist_ok=True, parents=True)
    with args.case_lines.open('w') as f:
        for r in rows:
            record = {k: r[k] for k in ['case_id', 'seed', 'persona', 'condition', 'goal_item_id', 'goal_recipient_id', 'competitor_id']}
            record.update(outcome=outcome(r), path=path(r), stance=(r['conversation'] or {}).get('stance'),
                          commands=[h['command'] for h in r['history']],
                          reasons=[h['choice']['reason'] for h in r['history']], update=r.get('update'))
            f.write(json.dumps(record, ensure_ascii=False)+'\n')
    result = {'status': 'COMPLETE', 'analysis': 'DESCRIPTIVE, no additional model calls or revised primary metric',
              'episodes': len(rows), 'cells': summaries, 'paired_transitions': transitions,
              'deterministic_examples_per_transition': examples, 'all_case_summaries': str(args.case_lines),
              'scope': ['Stance is model self-description including conditional acceptance, not an external truth label.',
                        'Lexical plan remove counts do not certify semantic correctness or a causal mediator.',
                        'RewardEvent concerns XP, never selected-item ownership; inherited failed flag includes deterministic no-XP failure.',
                        'No-give categories follow consumed > dropped > removed > still-equipped precedence; raw traces preserve overlaps.',
                        'Examples chosen by case_id then seed within each outcome transition, never to optimize a narrative.']}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'episodes': len(rows), 'cells': len(cells)}))


if __name__ == '__main__': main()
