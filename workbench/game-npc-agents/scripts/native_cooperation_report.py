#!/usr/bin/env python3
"""E81 CPU readback of two authored LIGHT roles and their actual interaction.

No models, API calls, semantic labels, world changes or new experimental arms.
Example (the existing fgvd environment supplies numpy and LIGHT dependencies):
  env PYTHONHASHSEED=0 PYTHONPATH=/home/xiang/.cache/game-npc-research/deps \
    /home/xiang/miniconda3/envs/fgvd/bin/python \
    workbench/game-npc-agents/scripts/native_cooperation_report.py \
    --runs RUN --profile --verify-replay --out REPORT.json

For full results include the profile and all complete full shards in --runs.
Only exact duplicate episode records may be merged. Get/Steal event identity,
receipt through somebody else's Give, equipment mode, and consumption are
reported separately. Neither two authored goals nor two transfers define
negotiation success, private utility, or a mutually beneficial outcome.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path

import numpy as np

SEEDS = [8101, 8102]
SPEECH = {'SayEvent', 'TellEvent', 'WhisperEvent', 'ShoutEvent'}
CONSUME = {'EatEvent', 'DrinkEvent', 'IngestEvent'}
EQUIP = {'WearEvent': 'wear', 'WieldEvent': 'wield', 'EquipObjectEvent': 'equip'}
BOOTSTRAPS = 4000
BOOTSTRAP_SEED = 8181
_WEIGHTS = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def key(row):
    return row['case_id'], row['seed']


def job_key(row):
    return tuple(row[k] for k in ['case_id', 'episode_seed', 'stage', 'index', 'turn'])


def decision_key(row):
    return canonical_sha({k: row[k] for k in ['messages', 'schema', 'seed']})


def success(turn):
    return bool(turn['legal'] and turn.get('executed') and not turn.get('stochastic_failure'))


def owner(state, item, actors):
    seen = set()
    node = item
    while node in state:
        assert node not in seen, ('Cyclic native containment', item)
        seen.add(node)
        parent = state[node]['container']
        if parent in [None,'VOID'] and node != item:
            # Rooms themselves live under VOID in LIGHT. A source in a room
            # (or in a table in that room) has not been consumed into VOID.
            return node
        if parent in actors or parent in [None, 'VOID'] or parent not in state:
            return parent
        node = parent
    return node


def health_dead(state, actor):
    if actor not in state:
        assert actor+'__dead__' in state, ('Missing character without corpse', actor)
        return 0, True
    return state[actor].get('health'), bool(state[actor].get('dead'))


def load_runs(folders, profile):
    folders = list(dict.fromkeys(folders))
    info = {}
    for folder in folders:
        m = json.loads((folder/'manifest.json').read_text())
        r = json.loads((folder/'runtime.json').read_text())
        assert m['experiment'] == 'E81' and m['seeds'] == SEEDS
        assert m['max_turns'] == 32 and not m['world_modified'] and m['new_cloud_calls'] == 0
        assert r['new_cloud_calls'] == 0
        info[folder] = m, r
    folders = [f for f in folders if info[f][0]['profile']]+[f for f in folders if not info[f][0]['profile']]
    if profile:
        assert all(info[f][0]['profile'] for f in folders)
    first = info[folders[0]][0]
    for m, _ in info.values():
        for field in ['model', 'data', 'data_sha256', 'driver_sha256', 'seeds', 'max_turns', 'tools']:
            assert m[field] == first[field], ('Manifest mismatch', field)
    rows, origins, calls, jobs, hashes = {}, {}, {}, {}, {}
    duplicates = []
    costs = Counter()
    runtimes = []
    for folder in folders:
        m, r = info[folder]
        runtimes.append(r)
        for name in ['manifest.json', 'runtime.json', 'episodes.jsonl', 'states.jsonl']:
            hashes[str(folder/name)] = sha(folder/name)
        local = set()
        for row in map(json.loads, (folder/'episodes.jsonl').open()):
            k = key(row)
            assert k not in local and k[0] in m['case_ids'] and k[1] in SEEDS
            local.add(k)
            if k in rows:
                exact = row == rows[k]
                duplicates.append({'key':list(k),'exact':exact,
                    'primary_path':str(origins[k]/'episodes.jsonl'),
                    'duplicate_path':str(folder/'episodes.jsonl'),
                    'primary_canonical_sha256':canonical_sha(rows[k]),
                    'duplicate_canonical_sha256':canonical_sha(row)})
                assert exact, ('Nonexact profile/full record: preserve both and audit before merging', k)
            else:
                rows[k] = row; origins[k] = folder
        assert len(local) == len(m['case_ids'])*len(SEEDS) == r['episodes']
        local_calls = local_reuses = 0
        for name in ['model_calls.jsonl', 'reused_calls.jsonl']:
            path = folder/name
            if not path.exists():
                assert name == 'reused_calls.jsonl'; continue
            hashes[str(path)] = sha(path)
            for record in map(json.loads, path.open()):
                jk = job_key(record)
                if jk in jobs:
                    assert jobs[jk] == record['decision_key']
                jobs[jk] = record['decision_key']
                if name == 'model_calls.jsonl':
                    assert decision_key(record) == record['decision_key']
                    if record['decision_key'] in calls:
                        old = calls[record['decision_key']]
                        assert all(old[f] == record[f] for f in ['messages','schema','seed','parsed'])
                    else:
                        calls[record['decision_key']] = record
                    costs.update(calls=1,prompt_tokens=record['prompt_tokens'],
                        completion_tokens=record['completion_tokens'],parse_errors=int(bool(record['parse_error'])))
                    local_calls += 1
                else:
                    costs['reused_calls'] += 1; local_reuses += 1
        assert local_calls == r['calls'] and local_reuses == r['reused_calls']
    return rows, origins, calls, jobs, hashes, info, duplicates, dict(costs), runtimes


def readback(row, case):
    """Independently count ID-bound successful events and material consequences."""
    actors, sid = case['actor_ids'], case['source_item_id']
    kind = case['player_goal_kind']
    assert row['graph_sha256'] == case['graph_sha256']
    assert row['quest_files'] == [q['source_file'] for q in case['quests']]
    goals = case['goal_identities']
    strict = [False, False]
    suffixes = ['all_asset_give_count','other_asset_give_count','give_peer_count',
        'other_asset_give_peer_count','source_give_count','source_get_ever','source_steal_ever',
        'source_consume_ever','source_any_equipped_ever','turns','native_rejections',
        'stochastic_failures','native_exceptions','not_recorded_executed_legal',
        'successful_material_actions','successful_hit_count','successful_block_count',
        'successful_wait_count','actual_speech_count','unused_non_speech_payloads']
    m = Counter({role+'_'+suffix:0 for role in ['giver','receiver'] for suffix in suffixes})
    m['giver_source_give_receiver_ever'] = m['receiver_source_return_giver_ever'] = 0
    m['episodes'] = 1
    speech = []
    flows = []
    source_events = []
    errors = []
    initial = row['initial_state']
    current = initial
    acquired = bool(initial[sid]['container'] == actors[1])
    receiver_physical = False
    receiver_any_equipped = False
    receiver_strict_mode = False
    receiver_driver_physical = False
    milestones = {}
    opening = row.get('opening')
    turns = row['turns']
    assert len(turns) <= 32 and [h['turn'] for h in turns] == list(range(len(turns)))
    if opening is not None:
        assert opening['turn'] == -1 and opening['index'] == 1 and opening['actor'] == actors[1]
        assert opening['event_type'] in ['SayEvent','ErrorEvent']
    ordered = ([opening] if opening else [])+turns
    for h in ordered:
        index = h['index']; actor = actors[index]; role = 'giver' if index == 0 else 'receiver'
        assert index in [0,1] and actor == h['actor']
        if h['turn'] >= 0:
            assert index == h['turn'] % 2
        assert h['before'] == current, ('Discontinuous states', key(row), h['turn'])
        assert h['material_changed'] == (h['before'] != h['after'])
        event, ids = h['event_identity']
        assert event == h['event_type']
        ok = success(h)
        if ok:
            strict[index] |= h['event_identity'] == goals[index]
        before, after = h['before'][sid], h['after'][sid]
        source = bool(ok and ids and ids[0] == sid)
        if ok and event in ['GiveObjectEvent','GetObjectEvent','StealObjectEvent','DropObjectEvent','PutObjectInEvent']:
            item = ids[0]
            assert h['before'][item]['container'] != h['after'][item]['container'], (key(row),h['turn'],event)
            if event == 'GiveObjectEvent':
                assert len(ids)==2 and h['before'][item]['container'] == actor
                assert h['after'][item]['container'] == ids[1]
                m[role+'_all_asset_give_count'] += 1
                m[role+'_other_asset_give_count'] += item != sid
                if ids[1] == actors[1-index]:
                    m[role+'_give_peer_count'] += 1
                    m[role+'_other_asset_give_peer_count'] += item != sid
                flows.append({'turn':h['turn'],'actor':actor,'item_id':item,'recipient_id':ids[1],
                    'source_item':item == sid,'before_parent':h['before'][item]['container'],
                    'after_parent':h['after'][item]['container']})
            elif event in ['GetObjectEvent','StealObjectEvent']:
                assert len(ids)==2 and h['before'][item]['container'] == ids[1]
                assert h['after'][item]['container'] == actor
        if source:
            source_events.append({'turn':h['turn'],'index':index,'event':event,'ids':ids,
                'before_parent':before['container'],'after_parent':after['container'],
                'equipped_after':after.get('equipped')})
            if event == 'GiveObjectEvent':
                m[role+'_source_give_count'] += 1
                if index==0 and ids[1]==actors[1]:
                    m['giver_source_give_receiver_ever'] = 1
                    milestones.setdefault('giver_source_give_receiver',h['turn'])
                if index==1 and ids[1]==actors[0]:
                    m['receiver_source_return_giver_ever'] = 1
            if event == 'GetObjectEvent': m[role+'_source_get_ever'] = 1
            if event == 'StealObjectEvent': m[role+'_source_steal_ever'] = 1
            if event in CONSUME:
                assert before['container'] == actor and after['container'] == 'VOID'
                m[role+'_source_consume_ever'] = 1
                if index==1 and kind in ['eat','drink']:
                    receiver_physical = receiver_driver_physical = True
                    milestones.setdefault('receiver_original_physical',h['turn'])
            if event in EQUIP:
                assert before['container'] == after['container'] == actor
                assert after.get('equipped') == EQUIP[event]
                m[role+'_source_any_equipped_ever'] = 1
        held = after['container'] == actors[1]
        if held:
            acquired = True
            milestones.setdefault('receiver_acquisition',h['turn'])
        if held and after.get('equipped'):
            receiver_any_equipped = True
        if held and after.get('equipped') == kind and kind in ['wear','wield']:
            receiver_strict_mode = receiver_physical = True
            milestones.setdefault('receiver_original_physical',h['turn'])
        if kind in ['get','steal']:
            receiver_physical |= held
            receiver_driver_physical |= held
            if held: milestones.setdefault('receiver_original_physical',h['turn'])
        elif kind in ['wear','wield']:
            receiver_driver_physical |= bool(held and after.get('equipped'))
        elif kind == 'put':
            placed = after['container'] == case['receiver_goal_identity'][1][1]
            receiver_physical |= placed; receiver_driver_physical |= placed
            if placed: milestones.setdefault('receiver_original_physical',h['turn'])
        current = h['after']
        if h['turn'] >= 0:
            m[role+'_turns'] += 1
        m['native_attempts_including_opening'] += 1
        m[role+'_native_rejections'] += not h['legal']
        m[role+'_stochastic_failures'] += bool(h.get('stochastic_failure'))
        m[role+'_native_exceptions'] += bool(h.get('native_exception'))
        m[role+'_not_recorded_executed_legal'] += bool(h['legal'] and not h.get('executed'))
        m[role+'_successful_material_actions'] += bool(ok and h['material_changed'])
        m[role+'_successful_hit_count'] += bool(ok and event=='HitEvent')
        m[role+'_successful_block_count'] += bool(ok and event=='BlockEvent')
        m[role+'_successful_wait_count'] += bool(ok and event=='WaitEvent')
        if event in SPEECH and ok:
            speech.append({'turn':h['turn'],'index':index,'event':event,'ids':ids,
                           'utterance':h['choice']['utterance'],
                           'viewers':[v['viewer'] for v in h['messages']]})
            m[role+'_actual_speech_count'] += 1
        elif event not in SPEECH and h['choice'].get('utterance'):
            m[role+'_unused_non_speech_payloads'] += 1
        if h.get('error') or h.get('native_exception'):
            errors.append({'turn':h['turn'],'index':index,'identity':h['event_identity'],
                'error':h.get('error'),'native_exception':h.get('native_exception')})
    assert current == row['final_state']
    assert strict == row['strict_goal_ever']
    assert acquired == row['receiver_acquired_ever']
    assert receiver_driver_physical == row['receiver_physical_goal_ever']
    assert bool(m['giver_source_give_receiver_ever']) == strict[0]
    final = row['final_state']
    hp_dead = [health_dead(final,a) for a in actors]
    assert [x[0] for x in hp_dead] == row['final_health']
    assert [x[1] for x in hp_dead] == row['final_dead']
    if row['stop'] == 'turn_limit': assert len(turns)==32 and not any(row['final_dead'])
    elif row['stop'] == 'character_death': assert any(row['final_dead'])
    else: assert row['stop'] in ['protocol_error','native_runtime_error']
    m.update(giver_strict_goal_ever=int(strict[0]),receiver_strict_goal_ever=int(strict[1]),
        receiver_acquired_ever=int(acquired),receiver_original_physical_ever=int(receiver_physical),
        receiver_driver_broad_physical_ever=int(receiver_driver_physical),
        receiver_source_any_equipped_ever=int(receiver_any_equipped),
        receiver_source_authored_equipment_mode_ever=int(receiver_strict_mode),
        giver_and_receiver_original_physical_ever=int(strict[0] and receiver_physical),
        both_strict_event_identities_ever=int(all(strict)),
        bidirectional_any_asset_give_ever=int(bool(m['giver_give_peer_count'] and m['receiver_give_peer_count'])),
        giver_other_asset_give_peer_ever=int(bool(m['giver_other_asset_give_peer_count'])),
        receiver_other_asset_give_peer_ever=int(bool(m['receiver_other_asset_give_peer_count'])),
        receiver_acquired_without_giver_source_give=int(acquired and not strict[0]),
        giver_gave_but_receiver_original_physical_absent=int(strict[0] and not receiver_physical),
        receiver_physical_without_giver_source_give=int(receiver_physical and not strict[0]),
        protocol_failure=int(row['stop']=='protocol_error'),
        native_runtime_stop=int(row['stop']=='native_runtime_error'),
        any_character_death=int(any(row['final_dead'])))
    sid_final = final[sid]
    parent = sid_final['container']; ultimate = owner(final,sid,actors)
    for i, role in enumerate(['giver','receiver']):
        m[role+'_final_source_direct_held'] = int(parent==actors[i])
        m[role+'_final_source_owned_including_containers'] = int(ultimate==actors[i])
        m[role+'_final_source_any_equipped'] = int(parent==actors[i] and bool(sid_final.get('equipped')))
        m[role+'_final_source_authored_equipment_mode'] = int(parent==actors[i] and kind in ['wear','wield'] and sid_final.get('equipped')==kind)
        m[role+'_death'] = int(hp_dead[i][1])
        m[role+'_final_hp'] = float(hp_dead[i][0])
        m[role+'_hp_change'] = float(hp_dead[i][0]-health_dead(initial,actors[i])[0])
        m[role+'_source_give_ever'] = int(bool(m[role+'_source_give_count']))
    m['source_final_VOID'] = int(parent=='VOID')
    m['source_final_other_owner_or_room'] = int(ultimate not in [*actors,'VOID'])
    assert m['giver_final_source_owned_including_containers']+m['receiver_final_source_owned_including_containers']+m['source_final_VOID']+m['source_final_other_owner_or_room']==1
    if kind in ['get','steal']:
        final_goal = parent == actors[1]
    elif kind in ['eat','drink']:
        final_goal = bool(m['receiver_source_consume_ever'] and parent=='VOID')
    elif kind in ['wear','wield']:
        final_goal = parent==actors[1] and sid_final.get('equipped')==kind
    else:
        final_goal = parent == case['receiver_goal_identity'][1][1]
    m['receiver_original_physical_final'] = int(final_goal)
    m['giver_gave_and_receiver_original_physical_final'] = int(strict[0] and final_goal)
    return dict(m), {'case_id':row['case_id'],'seed':row['seed'],'graph_sha256':row['graph_sha256'],
        'receiver_kind':kind,'task_family':case['task_family'],'metrics':dict(m),
        'first_milestones':milestones,'final_source_direct_parent':parent,
        'final_source_ultimate_owner':ultimate,'final_source_equipped_mode':sid_final.get('equipped'),
        'source_events':source_events,'all_actual_give_flows':flows,'actual_speech':speech,
        'native_errors':errors,'stop':row['stop']}


def audit_inputs(rows,cases,calls,jobs):
    import native_cooperation_episodes as driver
    audit = Counter()
    for k,row in rows.items():
        case = cases[k[0]]
        for h in ([row['opening']] if row.get('opening') else [])+row['turns']:
            stage = 'player_opening' if h['turn']==-1 else 'native_action'
            jk=(k[0],k[1],stage,h['index'],h['turn'])
            record=calls[jobs[jk]]
            parsed=record['parsed']
            assert parsed is not None
            if stage=='player_opening': assert parsed == {'utterance':h['choice']['utterance']}
            else: assert parsed == h['choice']
            assert record['messages'][0]['content']==driver.header(case,h['index'])
            own_header=record['messages'][0]['content']
            peer=case['quests'][1-h['index']]
            for field in ['short_motivation','mid_motivation','long_motivation']:
                text=peer[field]
                if len(text)>25 and text not in driver.header(case,h['index']):
                    assert text not in own_header
            audit['executed_or_rejected_decisions_resolved']+=1
            audit['own_author_header_checks']+=1
            if h['event_type'] in SPEECH and success(h):
                assert h['choice']['utterance']
                audit['actual_native_speech_selections']+=1
            elif h['event_type'] not in SPEECH and h['choice'].get('utterance'):
                audit['non_speech_payload_not_sent_as_speech']+=1
        if row['stop']=='protocol_error':
            t=len(row['turns']);index=t%2
            stage='native_action'
            if row.get('opening') is None: t,index,stage=-1,1,'player_opening'
            assert calls[jobs[(k[0],k[1],stage,index,t)]]['parsed'] is None
            audit['protocol_failure_decisions_resolved']+=1
    return {'status':'PASS',**dict(audit),
        'scope':'Own header and recorded decision provenance. Public native speech may legitimately disclose a private purpose; it is not prohibited by a string-leak filter.'}


def states_and_replay(rows,origins,cases,calls,jobs,modules,do_replay):
    """Full saved-state continuity always; exact typed native replay if requested."""
    import native_cooperation_episodes as driver
    from commitment_decisions_v2 import schema
    from light_npc_episodes import ViewerHost,material_state,observation
    counts=Counter();seen=set();byte_sha_differences=[]
    for folder in dict.fromkeys(origins.values()):
        for stored in map(json.loads,(folder/'states.jsonl').open()):
            k=stored['case_id'],stored['seed']
            if k not in rows or origins[k]!=folder:continue
            assert k not in seen;seen.add(k)
            row,case=rows[k],cases[k[0]]
            steps=([row['opening']] if row.get('opening') else [])+row['turns']
            assert len(stored['states'])==len(steps)
            visible=[[],[]]
            previous_graph=case['quests'][0]['graph']
            initial_graph=modules[0].from_json(previous_graph)
            assert material_state(initial_graph)==row['initial_state']
            game={'case':case,'seed':k[1],'graph':initial_graph,'host':ViewerHost(initial_graph),
                'visible':[[],[]],'turns':[],'states':[],'strict_goal_ever':[False,False],
                'stop':None,'receiver_acquired_ever':False,'receiver_physical_goal_ever':False}
            for h,state in zip(steps,stored['states']):
                assert state['turn']==h['turn']
                graph=modules[0].from_json(state['graph'])
                assert material_state(graph)==h['after'],('Saved fullgraph/material disagreement',k,h['turn'])
                for index,aid in enumerate(case['actor_ids']):
                    observed=[v['text'] for v in h['messages'] if v['viewer']==aid]
                    if index==h['index']:
                        observed.insert(0,'Your actual tool attempt: '+h['command'])
                        if h.get('native_exception'):observed.append('Native error: '+h['native_exception'])
                        elif h.get('error'):observed.append('Native rejection: '+h['error'])
                        elif not h.get('executed'):observed.append('Native tool did not record execution.')
                    visible[index].extend(observed)
                assert state['visible']==visible,('Private/public visible history differs',k,h['turn'])
                counts['full_graph_material_and_visible_snapshots_checked']+=1
                if do_replay:
                    if h['turn']==-1:
                        actor=game['graph'].get_node(case['actor_ids'][1])
                        text=observation(game['host'],actor,*modules[1:])
                        text+='\nBegin a brief spoken interaction with '+case['quests'][0]['character']+(
                            ' about what you want to accomplish. You may propose cooperation or ask for help as appropriate. '
                            'This opening sends speech only; actual actions follow separately.')
                        spec=([{'role':'system','content':driver.header(case,1)}, {'role':'user','content':text}],
                            schema({'utterance':{'type':'string','maxLength':500}}))
                        menu={};stage='player_opening'
                    else:
                        spec,menu=driver.action_spec(game,h['index'],modules);stage='native_action'
                    job=driver.job(game,h['index'],spec,stage,h['turn'])
                    expected=jobs[(k[0],k[1],stage,h['index'],h['turn'])]
                    assert decision_key(job)==expected,('Reconstructed full input differs',k,h['turn'])
                    assert calls[expected]['messages']==spec[0] and calls[expected]['schema']==spec[1]
                    counts['exact_model_input_keys_reconstructed']+=1
                    before_string=game['graph'].to_json()
                    if hashlib.sha256(before_string.encode()).hexdigest()!=h['graph_before_sha256']:
                        # JSON ordering does not change the physical graph. Preserve
                        # byte discrepancy; full canonical before/after checked below.
                        byte_sha_differences.append({'case_id':k[0],'seed':k[1],'turn':h['turn']})
                    driver.apply_choice(game,h['index'],h['choice'],menu,h['turn'],modules)
                    actual=game['turns'][-1]
                    for field in set(h)|set(actual):
                        if field=='graph_before_sha256':continue
                        assert actual.get(field)==h.get(field),('Typed native replay differs',k,h['turn'],field)
                    assert json.loads(game['graph'].to_json())==json.loads(state['graph']),('Full typed graph differs',k,h['turn'])
                    assert game['visible']==state['visible']
                    counts['native_typed_events_replayed_including_opening']+=1
                previous_graph=state['graph']
            if do_replay:
                assert material_state(game['graph'])==row['final_state']
                counts['entire_episodes_replayed']+=1
            counts['entire_saved_state_sequences_checked']+=1
    assert seen==set(rows)
    return {'status':'PASS',**dict(counts),'typed_native_replay_requested':do_replay,
        'graph_before_byte_sha_differences':byte_sha_differences,'new_model_calls':0,'new_API_calls':0}


def estimates(matrix,fields):
    x=np.asarray(matrix,dtype=float)
    assert x.ndim==2 and len(x)
    n=len(x)
    if n not in _WEIGHTS:
        rng=np.random.default_rng(BOOTSTRAP_SEED)
        _WEIGHTS[n]=rng.multinomial(n,np.full(n,1/n),size=BOOTSTRAPS)/n
    low,high=np.quantile(_WEIGHTS[n]@x,[.025,.975],axis=0)
    mean=x.mean(axis=0)
    return {f:{'mean':float(mean[i]),'graph_bootstrap_95':[float(low[i]),float(high[i])],
        'independent_graphs':n} for i,f in enumerate(fields)}


def aggregate(rows,metrics,cases,profile):
    fields=sorted({f for m in metrics.values() for f in m if f!='episodes'})
    groups={'all':list(cases)}
    for family in ['acquisition','use_or_put']:
        groups[family]=[cid for cid,c in cases.items() if c['task_family']==family]
    for kind in sorted({c['player_goal_kind'] for c in cases.values()}):
        groups['receiver_'+kind]=[cid for cid,c in cases.items() if c['player_goal_kind']==kind]
    for label,held in [('source_initially_NPC_held',True),('source_initially_not_NPC_held',False)]:
        groups[label]=[cid for cid,c in cases.items() if c['source_initially_held_by_npc']==held]
    result={}
    for label,ids in groups.items():
        ids=[cid for cid in ids if (cid,SEEDS[0]) in rows]
        if not ids:continue
        keys=[(cid,s) for cid in ids for s in SEEDS]
        matrix=[[sum(metrics[(cid,s)].get(f,0) for s in SEEDS)/len(SEEDS) for f in fields] for cid in ids]
        raw={f:sum(metrics[k].get(f,0) for k in keys) for f in fields}
        if profile:
            summary={f:{'mean':raw[f]/len(keys),'raw_sum':raw[f]} for f in fields}
        else:
            summary=estimates(matrix,fields)
            for f in fields:summary[f]['raw_sum']=raw[f]
        result[label]={'independent_graphs':len(ids),'episodes':len(keys),'metrics':summary,
            'seed_specific':{str(s):{f:sum(metrics[(cid,s)].get(f,0) for cid in ids)/len(ids) for f in fields} for s in SEEDS}}
    return result


def cost_ledger(info, costs, hashes):
    """Preserve runtime sub-timers and the separately observed occupied slots.

    The parent launch timestamp to the original runtime-file mtime includes
    imports, model loading, monitoring pauses and inference. It is not an
    inference-only timer, and parallel workers still consume separate slots.
    """
    ledger=[]
    for folder,(manifest,runtime) in info.items():
        path=folder.parent/(folder.name+'_launch.json')
        entry={'run':str(folder),'profile':manifest['profile'],
            'calls':runtime['calls'],'reused_calls':runtime['reused_calls'],
            'runtime_load_seconds':runtime['model_load_seconds'],
            'runtime_run_seconds':runtime['wall_seconds'],
            'runtime_model_load_plus_run_seconds':runtime['model_load_seconds']+runtime['wall_seconds']}
        if path.exists():
            launch=json.loads(path.read_text());hashes[str(path)]=sha(path)
            for field in ['driver_sha256','data_sha256']:
                assert launch[field]==manifest[field]
            finished=(folder/'runtime.json').stat().st_mtime
            seconds=finished-launch['start_epoch']
            assert seconds>=entry['runtime_model_load_plus_run_seconds']-2, ('Slot clock/timer discrepancy',folder,seconds)
            entry.update(launch_metadata=str(path),host=launch['host'],gpu=launch['gpu'],pid=launch['pid'],
                launch_epoch=launch['start_epoch'],original_runtime_mtime_epoch=finished,
                observed_occupied_slot_seconds=seconds,
                monitoring_resume=launch.get('monitoring_resume'))
        else:
            entry.update(launch_metadata=None,observed_occupied_slot_seconds=None)
        ledger.append(entry)
    timed=[x for x in ledger if x['observed_occupied_slot_seconds'] is not None]
    return {**costs,'sum_inference_wall_seconds':sum(x['runtime_run_seconds'] for x in ledger),
        'sum_model_load_seconds':sum(x['runtime_load_seconds'] for x in ledger),
        'runtime_model_load_plus_run_GPU_hours':sum(x['runtime_model_load_plus_run_seconds'] for x in ledger)/3600,
        'observed_occupied_GPU_slot_hours':sum(x['observed_occupied_slot_seconds'] for x in timed)/3600,
        'observed_slot_runs':len(timed),'total_runs':len(ledger),'per_run':ledger,'new_cloud_calls':0,
        'scope':'Costs include every supplied profile/full run once; duplicate outcomes add no samples. Runtime load+run sub-timers are separate from launch→original runtime mtime slot observations, which include import, loading, pauses and inference. No unobserved timings are imputed.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runs',nargs='+',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--profile',action='store_true')
    ap.add_argument('--verify-replay',action='store_true');a=ap.parse_args()
    assert os.environ.get('PYTHONHASHSEED')=='0'
    from light_native_gate import load_event_modules
    from light_npc_episodes import CACHE
    import native_cooperation_episodes as driver
    modules=load_event_modules(CACHE/'sources/LIGHT')
    rows,origins,calls,jobs,hashes,info,duplicates,costs,runtimes=load_runs(a.runs,a.profile)
    manifest=next(iter(info.values()))[0]
    source=Path(manifest['data'])
    assert sha(source)==manifest['data_sha256']
    assert sha(Path(driver.__file__))==manifest['driver_sha256']
    all_cases=driver.load_cases(source);cases={c['case_id']:c for c in all_cases}
    if not a.profile:
        assert set(rows)=={(c['case_id'],s) for c in all_cases for s in SEEDS}
    assert len(rows)==len({row['graph_sha256'] for row in rows.values()})*len(SEEDS)
    data={};details=[]
    raw_events=Counter();errors=Counter();stops=Counter();final_modes=Counter()
    for k,row in sorted(rows.items()):
        data[k],detail=readback(row,cases[k[0]]);details.append(detail)
        stops[row['stop']]+=1
        final_modes[str(row['final_state'][cases[k[0]]['source_item_id']].get('equipped'))]+=1
        for h in ([row['opening']] if row.get('opening') else [])+row['turns']:
            role='giver' if h['index']==0 else 'receiver'
            raw_events[(role,h['event_type'],'successful' if success(h) else 'rejected_or_failed')]+=1
            if h.get('error'):errors[role+': '+h['error']]+=1
            if h.get('native_exception'):errors[role+': '+h['native_exception']]+=1
    audit=audit_inputs(rows,cases,calls,jobs)
    replay=states_and_replay(rows,origins,cases,calls,jobs,modules,a.verify_replay)
    groups=aggregate(rows,data,cases,a.profile)
    cost=cost_ledger(info,costs,hashes)
    result={'experiment':'E81','status':'PROFILE_TECHNICAL_ONLY' if a.profile else 'COMPLETE',
        'model':manifest['model'],'data':str(source),'data_sha256':sha(source),
        'driver_sha256':manifest['driver_sha256'],'report_sha256':sha(Path(__file__)),
        'source_sha256':hashes,'primary_episode_sources_ordered':[str(f/'episodes.jsonl') for f in info],
        'independent_graphs':len(rows)//len(SEEDS),'episodes':len(rows),'seeds':SEEDS,
        'source_goal_binding':{
            'receiver_goal_kind_graphs':dict(Counter(cases[cid]['player_goal_kind'] for cid in {k[0] for k in rows})),
            'receiver_initial_native_identity_unavailable_graphs':sum(cases[cid]['goal_identities'][1] is None for cid in {k[0] for k in rows}),
            'source_initially_NPC_held_graphs':sum(cases[cid]['source_initially_held_by_npc'] for cid in {k[0] for k in rows}),
            'player_initial_direct_Get_possible_graphs':sum(cases[cid]['player_can_initially_get_source_without_npc'] for cid in {k[0] for k in rows})},
        'duplicate_episode_records':duplicates,
        'scope':('Two profile worlds test plumbing and cost only; no population estimate.' if a.profile else
            'All 126 source graphs; two seeds averaged within original graph; pointwise graph-cluster bootstrap intervals. Both roles use this model.'),
        'measurement':{
            'strict_goal':'Successful recorded native class and exact target-node IDs equal original bound identity.',
            'receiver_original_physical':'Get/Steal: actual direct possession; eat/drink: receiver consumes exact source into VOID; wear/wield: source held with original mode; Put: exact original destination.',
            'driver_broad_physical':'Also preserves the driver field, which counts any equipped mode on wear/wield tasks. Strict-mode and any-equipment measures are reported independently.',
            'giver_source_give':'Actual successful Give by original authored giver to original receiver with exact source ID; player Get/Steal is distinct.',
            'not_claimed':'Original atomic goals are not all private purposes. Co-occurring outcomes or bidirectional flows do not establish negotiation success, mutual utility or human player value.',
            'bootstrap':None if a.profile else {'draws':BOOTSTRAPS,'seed':BOOTSTRAP_SEED,'unit':'original graph','within_graph':'mean of fixed two seeds'}},
        'input_audit':audit,'full_state_and_native_replay_audit':replay,'groups':groups,
        'raw_counts':{'stop':dict(stops),'events':{'/'.join(k):v for k,v in sorted(raw_events.items())},
            'native_errors':dict(errors),'final_source_equipped_modes':dict(final_modes)},
        'cost':cost,
        'episodes_readback':details,'report_new_model_calls':0,'report_new_API_calls':0}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'out':str(a.out),'status':result['status'],'graphs':result['independent_graphs'],
        'episodes':len(rows),'replay':replay,'cost':result['cost']},ensure_ascii=False))


if __name__=='__main__':main()
