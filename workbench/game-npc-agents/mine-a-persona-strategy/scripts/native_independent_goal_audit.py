#!/usr/bin/env python3
"""CPU-only E84 native trajectories and exact input audit; no inference.

Run with the existing fgvd environment and PYTHONHASHSEED=0. Supply profile
before full in --runs. Duplicate logical episodes must be exactly identical.
Atomic events, material outcomes and authored narrative purposes stay separate.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import random

import numpy as np

from native_cooperation_report import canonical_sha, decision_key, job_key, key, success, cost_ledger

SEEDS = [8401, 8402]
SPEECH = {'SayEvent', 'TellEvent', 'WhisperEvent', 'ShoutEvent'}
CONSUME = {'EatEvent', 'DrinkEvent', 'IngestEvent'}
BOOTSTRAPS, BOOTSTRAP_SEED = 4000, 8484


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_runs(folders, profile):
    info, rows, origins, calls, jobs, hashes = {}, {}, {}, {}, {}, {}
    duplicates, costs = [], Counter()
    folders = list(dict.fromkeys(folders))
    folders.sort(key=lambda f: not json.loads((f/'manifest.json').read_text())['profile'])
    for folder in folders:
        m = json.loads((folder/'manifest.json').read_text())
        r = json.loads((folder/'runtime.json').read_text())
        assert m['experiment'] == 'E84' and m['max_turns'] == 32
        assert not m['world_modified'] and m['new_cloud_calls'] == r['new_cloud_calls'] == 0
        assert set(m['seeds']) <= set(SEEDS)
        if profile:
            assert m['profile']
        if info:
            first = next(iter(info.values()))[0]
            for field in ['model', 'data_sha256', 'driver_sha256', 'dependency_sha256', 'max_turns']:
                assert m[field] == first[field], ('Manifest mismatch', field)
        info[folder] = m, r
        for name in ['manifest.json', 'runtime.json', 'episodes.jsonl', 'states.jsonl']:
            hashes[str(folder/name)] = sha(folder/name)
        local = set()
        for row in map(json.loads, (folder/'episodes.jsonl').open()):
            k = key(row)
            assert k not in local
            local.add(k)
            if k in rows:
                exact = row == rows[k]
                duplicates.append({'key':list(k), 'exact':exact,
                    'primary_path':str(origins[k]/'episodes.jsonl'),
                    'duplicate_path':str(folder/'episodes.jsonl')})
                assert exact, ('Nonexact duplicate; do not select a version by outcome', k)
            else:
                rows[k], origins[k] = row, folder
        assert local == {(cid, seed) for cid in m['case_ids'] for seed in m['seeds']}
        assert len(local) == r['episodes']
        nc = nr = 0
        for name in ['model_calls.jsonl', 'reused_calls.jsonl']:
            path = folder/name
            if not path.exists():
                assert name == 'reused_calls.jsonl'
                continue
            hashes[str(path)] = sha(path)
            for rec in map(json.loads, path.open()):
                jk = job_key(rec)
                if jk in jobs:
                    assert jobs[jk] == rec['decision_key']
                jobs[jk] = rec['decision_key']
                if name == 'reused_calls.jsonl':
                    nr += 1
                    costs['reused_calls'] += 1
                else:
                    assert decision_key(rec) == rec['decision_key']
                    if rec['decision_key'] in calls:
                        assert all(calls[rec['decision_key']][f] == rec[f]
                                   for f in ['messages', 'schema', 'seed', 'parsed'])
                    calls[rec['decision_key']] = rec
                    nc += 1
                    costs.update(calls=1, prompt_tokens=rec['prompt_tokens'],
                        completion_tokens=rec['completion_tokens'], parse_errors=int(bool(rec['parse_error'])))
        assert (nc, nr) == (r['calls'], r['reused_calls'])
    return rows, origins, calls, jobs, hashes, info, duplicates, costs


def ultimate_owner(state, item, actors):
    seen = set()
    while item in state and item not in seen:
        seen.add(item)
        parent = state[item]['container']
        if parent in actors or parent in [None, 'VOID'] or parent not in state:
            return parent
        if state[parent]['container'] in [None, 'VOID']:
            return parent  # a room beneath VOID is not consumed material
        item = parent
    return None


def literal_physical(case, i, state, consumed):
    b, actor = case['goal_bindings'][i], case['actor_ids'][i]
    item, target, verb = b.get('item_id'), b.get('target_id'), b['verb']
    if not item or item not in state:
        return None
    current = state[item]
    if verb in ['get', 'steal']:
        return ultimate_owner(state, item, case['actor_ids']) == actor
    if verb in ['give', 'put']:
        return current['container'] == target if target is not None else None
    if verb in ['wear', 'wield']:
        return current['container'] == actor and current.get('equipped') == verb
    if verb in ['eat', 'drink']:
        return consumed[i] and current['container'] == 'VOID'
    return None


def readback(row, case):
    assert row['graph_sha256'] == case['graph_sha256']
    assert row['quest_files'] == [q['source_file'] for q in case['quests']]
    actors = case['actor_ids']
    strict = [False if x else None for x in row['strict_goal_measurement_supported']]
    consumed = [False, False]
    initial = [literal_physical(case, i, row['initial_state'], consumed) for i in [0, 1]]
    ever = list(initial)
    current = row['initial_state']
    assert row['physical_goal_initial'] == initial
    assert len(row['turns']) <= 32
    assert [t['turn'] for t in row['turns']] == list(range(len(row['turns'])))
    if row['stop'] == 'turn_limit':
        assert len(row['turns']) == 32
    events, errors, speeches, flows, goal_events = Counter(), [], [], [], []
    turns = ([row['opening']] if row.get('opening') else []) + row['turns']
    for t in turns:
        i = t['index']
        assert t['actor'] == actors[i]
        assert t['turn'] == -1 and i == 1 or t['turn'] >= 0 and i == t['turn'] % 2
        assert t['before'] == current
        assert t['material_changed'] == (t['before'] != t['after'])
        event, ids = t['event_identity']
        assert event == t['event_type']
        ok = success(t)
        events[(str(i), event, 'successful' if ok else 'rejected_or_failed')] += 1
        if ok and t['original_goal_current_identity'] == t['event_identity']:
            strict[i] = True
        if ok and event in CONSUME:
            assert ids and t['before'][ids[0]]['container'] == actors[i]
            assert t['after'][ids[0]]['container'] == 'VOID'
            if ids[0] == case['goal_bindings'][i]['item_id']:
                consumed[i] = True
        if ok and event in ['GiveObjectEvent', 'GetObjectEvent', 'StealObjectEvent', 'DropObjectEvent', 'PutObjectInEvent']:
            item = ids[0]
            before, after = t['before'][item]['container'], t['after'][item]['container']
            assert before != after
            if event == 'GiveObjectEvent':
                assert before == actors[i] and after == ids[1]
            elif event in ['GetObjectEvent', 'StealObjectEvent']:
                assert before == ids[1] and after == actors[i]
            flows.append({'turn':t['turn'], 'index':i, 'event':event, 'item_id':item,
                'from':before, 'to':after, 'matches_own_bound_item':item == case['goal_bindings'][i]['item_id']})
        if ok and event in SPEECH:
            speeches.append({'turn':t['turn'], 'index':i, 'actor_id':actors[i],
                'event':event, 'target_ids':ids, 'utterance':t['choice']['utterance']})
        if t.get('error') or t.get('native_exception'):
            errors.append({'turn':t['turn'], 'index':i, 'error':t.get('error'),
                'native_exception':t.get('native_exception')})
        if ids and ids[0] in [b.get('item_id') for b in case['goal_bindings']]:
            goal_events.append({'turn':t['turn'], 'index':i, 'identity':t['event_identity'],
                'successful':ok, 'before_parent':t['before'][ids[0]]['container'],
                'after_parent':t['after'][ids[0]]['container'],
                'equipped_after':t['after'][ids[0]].get('equipped')})
        now = [literal_physical(case, j, t['after'], consumed) for j in [0, 1]]
        ever = [True if value is True else old if old is not None else value for old, value in zip(ever, now)]
        assert strict == t['strict_goal_ever']
        assert now == t['physical_goal_now'] and ever == t['physical_goal_ever']
        current = t['after']
    assert current == row['final_state']
    assert strict == row['strict_goal_ever'] and ever == row['physical_goal_ever']
    now = [literal_physical(case, i, current, consumed) for i in [0, 1]]
    assert now == row['physical_goal_now']
    m = {}
    for i in [0, 1]:
        prefix = 'role_'+str(i)+'_'
        for field, values in [('strict_event_ever',strict), ('physical_initial',initial),
                              ('physical_ever',ever), ('physical_final',now)]:
            m[prefix+field] = None if values[i] is None else int(values[i])
        m[prefix+'new_physical_ever_among_initially_false'] = int(bool(ever[i])) if initial[i] is False else None
        m[prefix+'atomic_event_or_acquisition_ever'] = (None if strict[i] is None else int(bool(strict[i] or (
            case['goal_bindings'][i]['verb'] in ['get', 'steal'] and ever[i]))))
        for event, label in [('GiveObjectEvent','give_count'), ('StealObjectEvent','steal_count'),
                             ('GetObjectEvent','get_count')]:
            m[prefix+label] = sum(1 for f in flows if f['index'] == i and f['event'] == event)
        m[prefix+'actual_speech_count'] = sum(s['index'] == i for s in speeches)
        m[prefix+'native_rejections'] = sum(t['index']==i and not t['legal'] for t in turns)
        m[prefix+'stochastic_failures'] = sum(t['index']==i and bool(t.get('stochastic_failure')) for t in turns)
    combined = [m['role_'+str(i)+'_atomic_event_or_acquisition_ever'] for i in [0, 1]]
    m['both_atomic_events_or_acquisition_ever'] = None if None in combined else int(all(combined))
    m['actual_bidirectional_Give'] = int(all(any(f['event']=='GiveObjectEvent' and f['index']==i
        and f['to']==actors[1-i] for f in flows) for i in [0, 1]))
    return m, {'case_id':row['case_id'], 'seed':row['seed'], 'graph_sha256':row['graph_sha256'],
        'quest_files':row['quest_files'], 'goal_verbs':[b['verb'] for b in case['goal_bindings']],
        'metrics':m, 'goal_item_events':goal_events, 'actual_material_flows':flows,
        'actual_speech':speeches, 'native_errors':errors, 'raw_event_counts':{'/'.join(k):v for k,v in events.items()},
        'stop':row['stop'], 'final_health':row['final_health'], 'final_dead':row['final_dead']}


def native_and_inputs(rows, origins, cases, calls, jobs, modules, do_replay):
    import native_independent_goal_episodes as driver
    from commitment_decisions_v2 import schema
    from light_npc_episodes import material_state, observation
    count, byte_differences, seen = Counter(), [], set()
    for folder in dict.fromkeys(origins.values()):
        for stored in map(json.loads, (folder/'states.jsonl').open()):
            k = stored['case_id'], stored['seed']
            if k not in rows or origins[k] != folder:
                continue
            assert k not in seen
            seen.add(k)
            row, case = rows[k], cases[k[0]]
            turns = ([row['opening']] if row.get('opening') else []) + row['turns']
            assert len(stored['states']) == len(turns)
            game = driver.new_game(case, k[1], modules)
            visible = [[], []]
            assert material_state(game['graph']) == row['initial_state']
            for t, saved in zip(turns, stored['states']):
                i, aid = t['index'], case['actor_ids'][t['index']]
                assert saved['turn'] == t['turn']
                assert material_state(modules[0].from_json(saved['graph'])) == t['after']
                stage = 'player_opening' if t['turn'] == -1 else 'native_action'
                rec = calls[jobs[(k[0], k[1], stage, i, t['turn'])]]
                assert rec['messages'][0]['content'] == driver.header(case, i)
                if stage == 'player_opening':
                    assert rec['parsed'] == {'utterance':t['choice']['utterance']}
                else:
                    assert rec['parsed'] == t['choice']
                if do_replay:
                    if stage == 'player_opening':
                        actor = game['graph'].get_node(aid)
                        text = observation(game['host'], actor, *modules[1:])
                        text += '\nBegin a brief spoken interaction with '+case['quests'][0]['character']+(
                            ' about what you want to accomplish. You may propose cooperation or ask for help as appropriate. '
                            'This opening sends speech only; actual actions follow separately.')
                        spec = ([{'role':'system', 'content':driver.header(case,1)}, {'role':'user','content':text}],
                            schema({'utterance':{'type':'string','maxLength':500}}))
                        menu = {}
                    else:
                        spec, menu = driver.action_spec(game, i, modules)
                    rebuilt = driver.job(game, i, spec, stage, t['turn'])
                    assert decision_key(rebuilt) == rec['decision_key'], ('Input key differs', k, t['turn'])
                    assert spec[0] == rec['messages'] and spec[1] == rec['schema']
                    count['exact_complete_model_inputs_checked'] += 1
                    actor = game['graph'].get_node(aid)
                    if t['choice']['tool'] == 'SAY':
                        e = modules[1].SayEvent.construct_from_args(actor, [], t['choice']['utterance'])
                    else:
                        chosen = menu[t['choice']['tool']]
                        payload = t['choice']['utterance'] if type(chosen).__name__ in SPEECH else chosen.text_content
                        e = type(chosen).construct_from_args(actor, chosen.target_nodes, payload)
                    assert driver.identity(e) == t['event_identity']
                    expected, reason = driver.goal_event(game['graph'], driver.binding(case,i), modules)
                    assert (driver.identity(expected) if expected is not None else None) == t['original_goal_current_identity']
                    assert reason == t['original_goal_current_unavailable_reason']
                    before = game['graph'].to_json()
                    if hashlib.sha256(before.encode()).hexdigest() != t['graph_before_sha256']:
                        byte_differences.append({'case_id':k[0], 'seed':k[1], 'turn':t['turn']})
                    assert material_state(game['graph']) == t['before']
                    start = len(game['host'].messages)
                    random.seed(k[1]+int(k[0][:7],16)*100+t['turn']+1000)
                    if isinstance(e, modules[2]):
                        assert not t['legal'] and not t['executed'] and e.view_as(actor) == t['error']
                    else:
                        assert t['legal']
                        try:
                            e.execute(game['host'])
                            assert bool(e.executed) == t['executed']
                            assert bool(getattr(e,'failed',False)) == t.get('stochastic_failure',False)
                        except Exception as exc:
                            assert type(exc).__name__+': '+str(exc) == t.get('native_exception')
                    assert game['host'].messages[start:] == t['messages']
                    assert json.loads(game['graph'].to_json()) == json.loads(saved['graph'])
                    count['original_typed_native_events_replayed'] += 1
                for j, peer_id in enumerate(case['actor_ids']):
                    texts = [m['text'] for m in t['messages'] if m['viewer'] == peer_id]
                    if j == i:
                        texts.insert(0, 'Your actual tool attempt: '+t['command'])
                        if t.get('native_exception'): texts.append('Native error: '+t['native_exception'])
                        elif t.get('error'): texts.append('Native rejection: '+t['error'])
                        elif not t.get('executed'): texts.append('Native tool did not record execution.')
                    visible[j].extend(texts)
                assert saved['visible'] == visible
                game['visible'] = [list(v) for v in visible]
                count['full_graph_and_visible_history_snapshots_checked'] += 1
            if row['stop'] == 'protocol_error':
                failure = row['protocol_failure']
                stage = 'player_opening' if failure['turn'] == -1 else 'native_action'
                jk = k[0], k[1], stage, failure['actor_index'], failure['turn']
                rec = calls[jobs[jk]]
                assert rec['parsed'] == failure['parsed']
                if do_replay:
                    if stage == 'player_opening':
                        actor = game['graph'].get_node(case['actor_ids'][1])
                        text = observation(game['host'], actor, *modules[1:])
                        text += '\nBegin a brief spoken interaction with '+case['quests'][0]['character']+(
                            ' about what you want to accomplish. You may propose cooperation or ask for help as appropriate. '
                            'This opening sends speech only; actual actions follow separately.')
                        spec = ([{'role':'system','content':driver.header(case,1)}, {'role':'user','content':text}],
                            schema({'utterance':{'type':'string','maxLength':500}}))
                    else:
                        spec, _ = driver.action_spec(game,failure['actor_index'],modules)
                    rebuilt = driver.job(game,failure['actor_index'],spec,stage,failure['turn'])
                    assert decision_key(rebuilt) == rec['decision_key']
                    assert spec[0] == rec['messages'] and spec[1] == rec['schema']
                    count['exact_failed_model_inputs_checked'] += 1
                count['retained_protocol_failure_records'] += 1
            if do_replay:
                assert material_state(game['graph']) == row['final_state']
                count['whole_episodes_replayed'] += 1
            count['whole_saved_sequences_checked'] += 1
    assert seen == set(rows)
    return {'status':'PASS', **dict(count), 'typed_replay_requested':do_replay,
        'before_graph_byte_sha_differences':byte_differences, 'new_model_calls':0, 'new_API_calls':0}


def aggregate(rows, metrics, profile):
    fields = sorted(set(f for m in metrics.values() for f in m))
    grouped = defaultdict(list)
    for k, m in metrics.items():
        grouped[rows[k]['graph_sha256']].append(m)
    estimates = {}
    for f in fields:
        eligible = [float(m[f]) for m in metrics.values() if m.get(f) is not None]
        means = [float(np.mean([m[f] for m in mm if m.get(f) is not None]))
                 for mm in grouped.values() if any(m.get(f) is not None for m in mm)]
        ci = None
        if not profile and means:
            rng = np.random.default_rng(BOOTSTRAP_SEED)
            v = np.asarray(means)
            bs = v[rng.integers(0,len(v),size=(BOOTSTRAPS,len(v)))].mean(axis=1)
            ci = [float(x) for x in np.quantile(bs,[.025,.975])]
        estimates[f] = {'raw_sum':sum(eligible),'eligible_episodes':len(eligible),
            'eligible_graphs':len(means),'graph_mean':float(np.mean(means)) if means else None,
            'graph_cluster_95CI':ci}
    return estimates


def completed_cost_ledger(info, costs, hashes):
    """Final occupied slot ends at the recorded launcher exit, not JSON write."""
    result = cost_ledger(info, costs, hashes)
    result['launch_to_runtime_mtime_GPU_hours'] = result['observed_occupied_GPU_slot_hours']
    for entry in result['per_run']:
        entry['launch_to_runtime_mtime_seconds'] = entry['observed_occupied_slot_seconds']
        path = Path(entry['run']).parent/(Path(entry['run']).name+'_launch.json')
        launch = json.loads(path.read_text()) if path.exists() else {}
        end = launch.get('end_epoch')
        if end is not None:
            assert launch['exit_code'] == 0
            assert end >= entry['original_runtime_mtime_epoch']
            seconds = end-launch['start_epoch']
            assert abs(seconds/3600-launch['occupied_gpu_hours']) < 1e-9
            entry.update(launcher_end_epoch=end, launcher_exit_code=launch['exit_code'],
                         observed_occupied_slot_seconds=seconds)
        else:
            entry.update(launcher_end_epoch=None, launcher_exit_code=None,
                         observed_occupied_slot_seconds=None)
    timed = [e for e in result['per_run'] if e['observed_occupied_slot_seconds'] is not None]
    result['observed_occupied_GPU_slot_hours'] = sum(e['observed_occupied_slot_seconds'] for e in timed)/3600
    result['observed_slot_runs'] = len(timed)
    result['scope'] = ('Final occupied slots use launcher start_epoch→end_epoch and include process shutdown; '
        'launch→original runtime mtime is retained separately as a lower observation. Runtime load/run sub-timers '
        'remain separate. All supplied profile/full costs counted once; exact duplicate episodes add no samples.')
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--profile', action='store_true')
    ap.add_argument('--verify-replay', action='store_true')
    a = ap.parse_args()
    assert os.environ.get('PYTHONHASHSEED') == '0'
    from light_native_gate import load_event_modules
    from light_npc_episodes import CACHE
    import native_independent_goal_episodes as driver
    modules = load_event_modules(CACHE/'sources/LIGHT')
    rows, origins, calls, jobs, hashes, info, duplicates, costs = load_runs(a.runs,a.profile)
    manifest = next(iter(info.values()))[0]
    assert sha(driver.__file__) == manifest['driver_sha256']
    for name, expected in manifest['dependency_sha256'].items():
        assert sha(Path(driver.__file__).with_name(name)) == expected
    source = Path(manifest['data'])
    assert sha(source) == manifest['data_sha256']
    cases = {c['case_id']:c for c in driver.load_cases(source,modules)}
    if not a.profile:
        assert set(rows) == {(cid,s) for cid in cases for s in SEEDS}
    details, metrics, stops, events = [], {}, Counter(), Counter()
    for k, row in sorted(rows.items()):
        m, detail = readback(row,cases[k[0]])
        metrics[k] = m
        details.append(detail)
        stops[row['stop']] += 1
        events.update(detail['raw_event_counts'])
    audit = native_and_inputs(rows,origins,cases,calls,jobs,modules,a.verify_replay)
    cost = completed_cost_ledger(info,costs,hashes)
    cache = CACHE/'runs/e84_independent_goal_readback'
    cache.mkdir(exist_ok=True)
    raw = cache/(a.out.stem+'_episodes.jsonl')
    raw.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in details))
    compact = [{k:d[k] for k in ['case_id','seed','graph_sha256','quest_files','goal_verbs','metrics','stop','final_health','final_dead']}
               for d in details]
    result = {'experiment':'E84','status':'PROFILE_TECHNICAL_ONLY' if a.profile else 'COMPLETE',
        'model':manifest['model'],'data':str(source),'data_sha256':sha(source),
        'driver_sha256':manifest['driver_sha256'],'report_sha256':sha(__file__),
        'source_sha256':hashes,'primary_episode_sources_ordered':[str(f/'episodes.jsonl') for f in info],
        'source_pairs':len({k[0] for k in rows}),'original_graphs':len({r['graph_sha256'] for r in rows.values()}),
        'episodes':len(rows),'duplicate_episode_records':duplicates,
        'measurement':{'strict_event':'Current native goal with frozen authored item/target binding, same actor, legal successful event; no name rebinding.',
            'physical':'Recursive possession for Get/Steal; exact Give/Put destination; exact wear/wield mode; own bound consumption into VOID. Drop/Remove have only strict events.',
            'initial':'Physical predicates already true in source are explicitly separate; not evidence of newly induced cooperation.',
            'joint':'Both original atomic events or, for Get/Steal only, material acquisition. Not agreement, complete purpose, mutual benefit or cooperation success.',
            'unknown':'Unbound/nonimplemented predicates remain null and leave that metric denominator; all episodes remain.',
            'bootstrap':None if a.profile else {'draws':BOOTSTRAPS,'seed':BOOTSTRAP_SEED,'unit':'original graph','within_graph':'mean over original pairs and fixed seeds'}},
        'independent_full_state_and_input_audit':audit,'estimates':aggregate(rows,metrics,a.profile),
        'raw_counts':{'stop':dict(stops),'native_events':dict(events),
            'native_error_events':sum(len(d['native_errors']) for d in details),
            'episodes_with_any_actor_death':sum(any(d['final_dead']) for d in details)},
        'cost':cost,'episodes_readback':compact,
        'full_actual_interactions':{'path':str(raw),'sha256':sha(raw),'episodes':len(details)},
        'scope':'Both roles use this model. Profile is one technical case, not a population result. Original quests are independent annotations on the same original graph. No uniform cooperation label.',
        'report_new_model_calls':0,'report_new_API_calls':0}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'out':str(a.out),'status':result['status'],'audit':audit,'episodes':len(rows),'cost':cost},ensure_ascii=False))


if __name__ == '__main__':
    main()
