#!/usr/bin/env python3
"""E84 CPU derived numbers; no inference or modifications to frozen execution.

Only completed runs are accepted. Exact profile/full duplicates count once as
logical outcomes; all actual calls and load time remain in the cost ledger.
Use --profile for the completed technical episode, never a partial full queue.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

from native_independent_goal_audit import load_runs
from native_cooperation_report import cost_ledger

SEEDS = [8401, 8402]
BOOTSTRAPS, BOOTSTRAP_SEED = 4000, 8484
_WEIGHTS = {}
SPEECH = {'SayEvent', 'TellEvent', 'WhisperEvent', 'ShoutEvent'}
CONSUME = {'EatEvent', 'DrinkEvent', 'IngestEvent'}
EVENTS = {'get':'GetObjectEvent', 'steal':'StealObjectEvent',
          'give':'GiveObjectEvent', 'put':'PutObjectInEvent',
          'eat':'EatEvent', 'drink':'DrinkEvent', 'wear':'WearEvent',
          'wield':'WieldEvent', 'drop':'DropObjectEvent', 'remove':'RemoveObjectEvent'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def successful(t):
    return bool(t['legal'] and t.get('executed') and not t.get('stochastic_failure'))


def owner(state, item, actors):
    """Current ultimate native owner, including existing held containers."""
    seen = set()
    while item in state:
        assert item not in seen, ('Cyclic native containment', item)
        seen.add(item)
        if item in actors:
            return item
        parent = state[item]['container']
        if parent in [None, 'VOID'] or parent not in state:
            return parent
        item = parent
    return None


def physical(case, index, state, consumed):
    b = case['goal_bindings'][index]
    item, target, verb = b.get('item_id'), b.get('target_id'), b['verb']
    if not item or item not in state:
        return None
    actor, current = case['actor_ids'][index], state[item]
    if verb in ['get', 'steal']:
        return owner(state, item, case['actor_ids']) == actor
    if verb in ['give', 'put']:
        return current['container'] == target if target is not None else None
    if verb in ['wear', 'wield']:
        return current['container'] == actor and current.get('equipped') == verb
    if verb in ['eat', 'drink']:
        return bool(consumed[index] and current['container'] == 'VOID')
    return None  # Drop/Remove require actual actor events, no state substitute.


def strict_identity(case, index, state):
    b = case['goal_bindings'][index]
    item, target, verb = b.get('item_id'), b.get('target_id'), b['verb']
    if not item or verb not in EVENTS or verb in ['give', 'put'] and target is None:
        return None
    ids = [item]
    if verb == 'get':
        ids.append(target if ' from ' in case['quests'][index]['goal'] else state[item]['container'])
    elif verb == 'steal':
        ids.append(target or b.get('item_owner_agent_id'))
    elif verb in ['give', 'put']:
        ids.append(target)
    return [EVENTS[verb], ids] if None not in ids else None


def read_episode(row, case):
    assert row['graph_sha256'] == case['graph_sha256']
    assert row['quest_files'] == [q['source_file'] for q in case['quests']]
    actors = case['actor_ids']
    supported = [bool(b.get('item_id')) and (b['verb'] not in ['give', 'put']
                  or b.get('target_id') is not None) for b in case['goal_bindings']]
    assert supported == row['strict_goal_measurement_supported']
    strict = [False if known else None for known in supported]
    consumed = [False, False]
    initial = [physical(case, i, row['initial_state'], consumed) for i in range(2)]
    ever, current = list(initial), row['initial_state']
    first_strict = [None, None]
    first_material = [-1 if v is True else None for v in initial]
    counts, events, errors = Counter(), Counter(), Counter()
    flows = []
    assert row['physical_goal_initial'] == initial
    assert [t['turn'] for t in row['turns']] == list(range(len(row['turns'])))
    assert len(row['turns']) <= 32
    if row['stop'] == 'turn_limit':
        assert len(row['turns']) == 32
    for t in ([row['opening']] if row.get('opening') else []) + row['turns']:
        i, actor = t['index'], actors[t['index']]
        prefix = 'role_' + str(i) + '_'
        assert t['actor'] == actor and (t['turn'] == -1 and i == 1 or t['turn'] >= 0 and i == t['turn'] % 2)
        assert t['before'] == current
        assert t['material_changed'] == (t['before'] != t['after'])
        event, ids = t['event_identity']
        assert event == t['event_type']
        ok = successful(t)
        events[(str(i), event, 'successful' if ok else 'rejected_or_failed')] += 1
        counts[prefix+'action_opportunities'] += int(t['turn'] >= 0)
        counts[prefix+'native_rejections'] += int(not t['legal'])
        counts[prefix+'stochastic_failures'] += int(bool(t.get('stochastic_failure')))
        counts[prefix+'native_exceptions'] += int(bool(t.get('native_exception')))
        counts[prefix+'legal_not_recorded_executed'] += int(t['legal'] and not t.get('executed'))
        if t.get('error') or t.get('native_exception'):
            errors[prefix + str(t.get('error') or t['native_exception'])] += 1
        if ok:
            expected = strict_identity(case, i, t['before'])
            if t['original_goal_current_identity'] is not None:
                assert t['original_goal_current_identity'] == expected
            if supported[i] and expected == t['event_identity']:
                strict[i] = True
                if first_strict[i] is None:
                    first_strict[i] = t['turn']
            counts[prefix+'successful_material_actions'] += int(t['material_changed'])
            for cls, label in [('GiveObjectEvent','give_count'), ('StealObjectEvent','steal_count'),
                    ('GetObjectEvent','get_count'), ('PutObjectInEvent','put_count'),
                    ('DropObjectEvent','drop_count'), ('RemoveObjectEvent','remove_count'),
                    ('HitEvent','hit_count'), ('BlockEvent','block_count'), ('WaitEvent','wait_count')]:
                counts[prefix+label] += int(event == cls)
            counts[prefix+'consume_count'] += int(event in CONSUME)
            counts[prefix+'actual_speech_count'] += int(event in SPEECH)
            if event in CONSUME:
                assert ids and t['before'][ids[0]]['container'] == actor
                assert t['after'][ids[0]]['container'] == 'VOID'
                if ids[0] == case['goal_bindings'][i]['item_id']:
                    consumed[i] = True
            if event in ['GiveObjectEvent','GetObjectEvent','StealObjectEvent','PutObjectInEvent','DropObjectEvent']:
                item = ids[0]
                before, after = t['before'][item]['container'], t['after'][item]['container']
                assert before != after
                if event == 'GiveObjectEvent':
                    assert before == actor and after == ids[1]
                    counts[prefix+'give_peer_count'] += int(after == actors[1-i])
                    counts[prefix+'give_other_asset_count'] += int(item not in [b.get('item_id') for b in case['goal_bindings']])
                elif event in ['GetObjectEvent','StealObjectEvent']:
                    assert before == ids[1] and after == actor
                flows.append({'turn':t['turn'],'index':i,'event':event,'item_id':item,'from':before,'to':after})
        now = [physical(case, j, t['after'], consumed) for j in range(2)]
        for j, value in enumerate(now):
            if value is True:
                ever[j] = True
                if first_material[j] is None:
                    first_material[j] = t['turn']
            elif ever[j] is None and value is not None:
                ever[j] = False
        assert strict == t['strict_goal_ever']
        assert now == t['physical_goal_now'] and ever == t['physical_goal_ever']
        current = t['after']
    assert current == row['final_state']
    final = [physical(case, i, current, consumed) for i in range(2)]
    assert strict == row['strict_goal_ever'] and ever == row['physical_goal_ever'] and final == row['physical_goal_now']
    metric = {}
    for i in range(2):
        p = 'role_'+str(i)+'_'
        for name, values in [('strict_event_ever',strict),('physical_initial',initial),('physical_ever',ever),('physical_final',final)]:
            metric[p+name] = int(values[i]) if values[i] is not None else None
        metric[p+'new_physical_ever_among_initially_false'] = int(bool(ever[i])) if initial[i] is False else None
        metric[p+'atomic_event_or_acquisition_ever'] = (None if strict[i] is None else int(bool(strict[i] or (
            case['goal_bindings'][i]['verb'] in ['get','steal'] and ever[i]))))
        for label in ['action_opportunities','native_rejections','stochastic_failures','native_exceptions',
                'legal_not_recorded_executed','successful_material_actions','give_count','steal_count','get_count',
                'put_count','drop_count','remove_count','consume_count','actual_speech_count','give_peer_count',
                'give_other_asset_count','hit_count','block_count','wait_count']:
            metric[p+label] = counts[p+label]
        metric[p+'dead_final'] = int(row['final_dead'][i])
        metric[p+'protocol_failure'] = int(row.get('protocol_failure',{}).get('actor_index') == i)
    for label, values in [('strict_events_ever',strict),('physical_initial',initial),('physical_ever',ever),('physical_final',final)]:
        metric['both_'+label] = None if None in values else int(all(values))
    metric['both_new_physical_among_both_initially_false'] = int(all(ever)) if initial == [False,False] else None
    combined = [metric['role_'+str(i)+'_atomic_event_or_acquisition_ever'] for i in range(2)]
    metric['both_atomic_events_or_acquisition_ever'] = None if None in combined else int(all(combined))
    metric['actual_bidirectional_Give'] = int(all(any(f['event']=='GiveObjectEvent' and f['index']==i
        and f['to']==actors[1-i] for f in flows) for i in range(2)))
    return {'case_id':row['case_id'],'seed':row['seed'],'graph_sha256':row['graph_sha256'],
        'goal_verbs':[b['verb'] for b in case['goal_bindings']],'metrics':metric,
        'first_strict_turn':first_strict,'first_physical_turn':first_material,
        'stop':row['stop'],'final_health':row['final_health'],'final_dead':row['final_dead'],
        'raw_event_counts':{'/'.join(k):v for k,v in events.items()},'native_errors':dict(errors)}


def estimate(observations, profile):
    """Mean seeds within pair, then pairs within graph; equal graph weight."""
    known = [(g,c,s,float(v)) for g,c,s,v in observations if v is not None]
    pairs = defaultdict(list)
    for graph, case, seed, value in known:
        pairs[graph,case].append(value)
    graphs = defaultdict(list)
    for (graph,case), values in pairs.items():
        graphs[graph].append(float(np.mean(values)))
    values = np.asarray([np.mean(graphs[g]) for g in sorted(graphs)], dtype=float)
    result = {'mean':float(values.mean()) if len(values) else None,
        'known_logical_episodes':len(known),'excluded_or_unknown_logical_episodes':len(observations)-len(known),
        'raw_sum':float(sum(x[3] for x in known)), 'independent_graphs':len(values),'pairs':len(pairs)}
    if not profile and len(values):
        n = len(values)
        if n not in _WEIGHTS:
            rng = np.random.default_rng(BOOTSTRAP_SEED)
            _WEIGHTS[n] = rng.multinomial(n,np.full(n,1/n),size=BOOTSTRAPS)/n
        result['graph_bootstrap_95'] = list(map(float,np.quantile(_WEIGHTS[n]@values,[.025,.975])))
    return result


def aggregate(details, profile):
    fields = sorted({f for d in details for f in d['metrics']})
    overall = {f:estimate([(d['graph_sha256'],d['case_id'],d['seed'],d['metrics'][f]) for d in details],profile) for f in fields}
    by_goal = {}
    core = ['strict_event_ever','physical_initial','physical_ever','physical_final',
            'new_physical_ever_among_initially_false','atomic_event_or_acquisition_ever',
            'give_count','steal_count','put_count','consume_count','native_rejections','protocol_failure','dead_final']
    for i in range(2):
        for verb in sorted({d['goal_verbs'][i] for d in details}):
            group=[d for d in details if d['goal_verbs'][i]==verb]
            by_goal['role_'+str(i)+'_'+verb]={f:estimate([(d['graph_sha256'],d['case_id'],d['seed'],d['metrics']['role_'+str(i)+'_'+f]) for d in group],profile) for f in core}
    first = {}
    for i in range(2):
        for label in ['strict','physical']:
            support = 'strict_event_ever' if label=='strict' else 'physical_ever'
            hist=Counter(); unknown=unreached=0
            for d in details:
                value=d['first_'+label+'_turn'][i]
                if d['metrics']['role_'+str(i)+'_'+support] is None:unknown+=1
                elif value is None:unreached+=1
                else:hist[str(value)]+=1
            first['role_'+str(i)+'_'+label]={'first_turn_counts':dict(sorted(hist.items(),key=lambda x:int(x[0]))),
                'unreached_known':unreached,'unknown':unknown,'initial_true_turn_code':-1}
    return overall, by_goal, first


def denominators(details, cases):
    result = {}
    for i in range(2):
        counts = Counter()
        for d in details:
            p = 'role_'+str(i)+'_'
            counts['strict_supported'] += d['metrics'][p+'strict_event_ever'] is not None
            counts['strict_unknown_binding'] += d['metrics'][p+'strict_event_ever'] is None
            initial = d['metrics'][p+'physical_initial']
            counts['physical_initial_true'] += initial == 1
            counts['physical_initial_false_new_attainment_denominator'] += initial == 0
            if initial is None:
                b = cases[d['case_id']]['goal_bindings'][i]
                if not b.get('item_id'):
                    counts['physical_unknown_item_binding'] += 1
                elif b['verb'] in ['give','put'] and b.get('target_id') is None:
                    counts['physical_unknown_target_binding'] += 1
                else:
                    counts['physical_not_defined_for_actor_event_goal'] += 1
        result['role_'+str(i)] = dict(counts)
    result['both_new_physical'] = {
        'both_initially_false':sum(all(d['metrics']['role_'+str(i)+'_physical_initial']==0 for i in range(2)) for d in details),
        'at_least_one_initially_true':sum(any(d['metrics']['role_'+str(i)+'_physical_initial']==1 for i in range(2)) for d in details),
        'at_least_one_material_unknown_or_event_only':sum(any(d['metrics']['role_'+str(i)+'_physical_initial'] is None for i in range(2)) for d in details),
        'scope':'Exclusion categories may overlap; initial truth is not unsupported measurement.'}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',type=Path,nargs='+',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--profile',action='store_true')
    args=parser.parse_args()
    rows, origins, calls, jobs, hashes, info, duplicates, costs=load_runs(args.runs,args.profile)
    manifest=next(iter(info.values()))[0]
    source=Path(manifest['data']);assert sha(source)==manifest['data_sha256']
    cases={r['case_id']:r for r in map(json.loads,source.open())}
    if not args.profile:
        assert any(not m['profile'] for m,_ in info.values())
        assert set(rows)=={(cid,s) for cid in cases for s in SEEDS}, 'Full cohort not complete; no partial result reported'
    details=[read_episode(row,cases[k[0]]) for k,row in sorted(rows.items())]
    overall, by_goal, first=aggregate(details,args.profile)
    event_counts, errors, stops=Counter(),Counter(),Counter()
    for d in details:
        event_counts.update(d['raw_event_counts']);errors.update(d['native_errors']);stops[d['stop']]+=1
    cache=source.parent.parent/'e84_independent_goal_numeric_readback'
    cache.mkdir(exist_ok=True)
    detail_file=cache/(args.out.stem+'_episodes.jsonl')
    detail_file.write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in details))
    output={'experiment':'E84','status':'PROFILE_TECHNICAL_ONLY' if args.profile else 'COMPLETE',
        'model':manifest['model'],'scope':'Whole model configuration controls both original roles. Roles, pairs and seeds from one original graph are not independent NPC treatment effects.',
        'source_data':str(source),'data_sha256':sha(source),'driver_sha256':manifest['driver_sha256'],
        'report_sha256':sha(Path(__file__)),'loader_sha256':sha(Path(__file__).with_name('native_independent_goal_audit.py')),
        'source_sha256':hashes,'pairs':len({k[0] for k in rows}),'independent_graphs':len({r['graph_sha256'] for r in rows.values()}),
        'logical_episodes':len(rows),'seeds':sorted({k[1] for k in rows}), 'exact_duplicate_episode_records':duplicates,
        'measurement':{'strict_event':'Successful native actor/class/target IDs match the source-bound original event; implicit Get uses current source parent. No receipt is relabeled as Steal/Get event.',
            'material':'Get/Steal recursive ownership; Give/Put exact parent; Wear/Wield exact mode; Eat/Drink same actor consumes bound item into VOID. Drop/Remove have no substituted state label.',
            'initial':'Initial true is reported explicitly. Newly reached only has initially-false measurable episodes in its denominator; None is never failure.',
            'first_turn':'-1 is already true at initial state; 0..31 are actual alternating primitive opportunities. Histograms are raw logical counts, not independent-sample estimates.',
            'weighting':'Within pair average fixed seeds, within original graph average pair values, then equal weight per measurable original graph. Unknown observations and denominators are explicit for every metric.',
            'bootstrap':None if args.profile else {'draws':BOOTSTRAPS,'seed':BOOTSTRAP_SEED,'unit':'original graph','kind':'pointwise percentile interval'},
            'both':'Co-occurring atomic events/material states are not cooperation success, welfare, agreement fulfillment or complete private purposes.'},
        'measurement_denominators':denominators(details,cases),
        'overall':overall,'by_role_goal_verb':by_goal,'first_attainment':first,
        'raw_counts':{'events':dict(event_counts),'native_errors':dict(errors),'stop':dict(stops)},
        'cost':cost_ledger(info,costs,hashes),
        'numeric_episode_readback':{'path':str(detail_file),'sha256':sha(detail_file),'episodes':len(details),
            'scope':'Compact per-logical-episode metrics/milestones; complete speech, states and inputs remain in original raw artifacts.'},
        'report_new_model_calls':0,'report_new_API_calls':0,'report_new_GPU_jobs':0}
    args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'out':str(args.out),'status':output['status'],'logical_episodes':len(rows),
        'graphs':output['independent_graphs'],'actual_calls':costs['calls'],'exact_duplicates':len(duplicates)},ensure_ascii=False))


if __name__=='__main__':
    main()
