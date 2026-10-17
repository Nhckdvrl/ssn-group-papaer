#!/usr/bin/env python3
"""E85 CPU-only derived reporting, fixed before model outcome inspection.

Completed-run interface: 8-branch queues only; exact profile reuse counts
once. Contrasts preserve each source history and seed before original-graph
aggregation. Transfer, return, use, authored atomic outcomes and speech are
separate observations, never one universal cooperation/utility score.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

SEEDS = (8501, 8502)
FACT_BRANCHES = ('real_claim', 'claim_only', 'pending_truth')
CONTROLS = ('normal', 'check')
CONDITIONS = tuple(('primary', b, c) for b in FACT_BRANCHES for c in CONTROLS) + (
    ('revision', 'continue', 'check'), ('revision', 'withdraw', 'check'))
BOOTSTRAPS, BOOTSTRAP_SEED = 4000, 8585
SPEECH = {'SayEvent', 'TellEvent', 'WhisperEvent', 'ShoutEvent'}
CONSUME = {'EatEvent', 'DrinkEvent', 'IngestEvent'}
EVENTS = {'get':'GetObjectEvent', 'steal':'StealObjectEvent',
    'give':'GiveObjectEvent', 'put':'PutObjectInEvent', 'eat':'EatEvent',
    'drink':'DrinkEvent', 'wear':'WearEvent', 'wield':'WieldEvent',
    'drop':'DropObjectEvent', 'remove':'RemoveObjectEvent'}
_WEIGHTS = {}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def episode_key(row):
    return (row['history_id'], row['seed'], row['panel'], row['branch'], row['control'])


def successful(turn):
    # Legacy field records native event.failed, including deterministic Reward
    # failures; no claim that all flagged failures are stochastic.
    return bool(turn['legal'] and turn.get('executed') and not turn.get('stochastic_failure'))


def ultimate_owner(state, item, actors):
    seen = set()
    node = item
    while node in state:
        assert node not in seen, ('Cyclic containment', item)
        seen.add(node)
        parent = state[node]['container']
        if parent in actors or parent in [None, 'VOID'] or parent not in state:
            # A room may itself sit under VOID; this does not mean an object
            # on the floor was consumed. Only direct item->VOID is consumed.
            return parent if node == item or parent in actors else node
        node = parent
    return None


def physical_goal(binding, actor, state, actors, consumed):
    item, target, verb = binding.get('item_id'), binding.get('target_id'), binding['verb']
    if not item or item not in state:
        return None
    current = state[item]
    if verb in ['get', 'steal']:
        return ultimate_owner(state, item, actors) == actor
    if verb in ['give', 'put']:
        return current['container'] == target if target is not None else None
    if verb in ['wear', 'wield']:
        return current['container'] == actor and current.get('equipped') == verb
    if verb in ['eat', 'drink']:
        return bool(consumed and current['container'] == 'VOID')
    return None


def strict_goal_identity(binding, quest, state):
    item, target, verb = binding.get('item_id'), binding.get('target_id'), binding['verb']
    if not item or verb not in EVENTS or verb in ['give', 'put'] and target is None:
        return None
    ids = [item]
    if verb == 'get':
        ids.append(target if ' from ' in quest['goal'] else state[item]['container'])
    elif verb == 'steal':
        ids.append(target or binding.get('item_owner_agent_id'))
    elif verb in ['give', 'put']:
        ids.append(target)
    return [EVENTS[verb], ids] if None not in ids else None


def mapped_case(history):
    order = [history['source_role_map'][k] for k in ['npc','player']]
    assert sorted(order) == [0,1]
    return {**history['case'], **{key:[history['case'][key][i] for i in order]
        for key in ['actor_ids','quests','goal_bindings','goal_identities']}}


def load_lines(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]


def load_runs(folders, profile):
    info, rows, shadows, origins, hashes, duplicates = {}, {}, {}, {}, {}, []
    calls, jobs, costs = {}, {}, Counter()
    folders = list(dict.fromkeys(folders))
    folders.sort(key=lambda p:not json.loads((p/'manifest.json').read_text())['profile'])
    for folder in folders:
        manifest = json.loads((folder/'manifest.json').read_text())
        runtime = json.loads((folder/'runtime.json').read_text())
        assert manifest['experiment'] == runtime['experiment'] == 'E85'
        assert runtime['status'] == 'COMPLETE' and manifest['max_turns'] == 24
        assert not manifest['world_rules_modified'] and manifest['new_cloud_calls'] == runtime['new_cloud_calls'] == 0
        assert tuple(manifest['primary_conditions']) == FACT_BRANCHES
        assert tuple(manifest['controls']) == CONTROLS
        assert manifest['revision_conditions'] == ['continue','withdraw']
        assert manifest['logical_branches_per_history_seed'] == 8
        assert set(manifest['seeds']) <= set(SEEDS)
        if profile:
            assert manifest['profile']
        if info:
            first = next(iter(info.values()))[0]
            for field in ['model','data_sha256','driver_sha256','dependency_sha256','max_turns',
                    'primary_conditions','controls','revision_conditions','fact_check_sentence','statement_templates']:
                assert manifest[field] == first[field], ('Manifest mismatch',field)
        info[folder] = manifest,runtime
        for name in ['manifest.json','runtime.json','episodes.jsonl','states.jsonl','shadow_facts.jsonl','first_responses.jsonl']:
            path = folder/name
            assert path.exists(),('Missing complete artifact',path)
            hashes[str(path)] = sha(path)
        local = set()
        for row in load_lines(folder/'episodes.jsonl'):
            k = episode_key(row)
            assert k not in local
            local.add(k)
            if k in rows:
                exact = row == rows[k]
                duplicates.append({'key':list(k),'exact':exact,'primary_path':str(origins[k]),'duplicate_path':str(folder)})
                assert exact,('Nonexact logical duplicate; no outcome selection',k)
            else:
                rows[k],origins[k] = row,folder
        expected = {(h,s,*c) for h in manifest['history_ids'] for s in manifest['seeds'] for c in CONDITIONS}
        assert local == expected and len(local) == runtime['episodes']
        local_shadow = set()
        for shadow in load_lines(folder/'shadow_facts.jsonl'):
            k = shadow['history_id'],shadow['seed'],shadow['branch']
            assert k not in local_shadow
            local_shadow.add(k)
            if k in shadows:
                assert shadows[k] == shadow,('Nonexact duplicate shadow',k)
            else:
                shadows[k] = shadow
        assert local_shadow == {(h,s,b) for h in manifest['history_ids'] for s in manifest['seeds'] for b in FACT_BRANCHES}
        nc = nr = 0
        for name in ['model_calls.jsonl','reused_calls.jsonl']:
            path = folder/name
            if not path.exists():
                assert name == 'reused_calls.jsonl'
                continue
            hashes[str(path)] = sha(path)
            for rec in load_lines(path):
                key = tuple(rec[k] for k in ['history_id','episode_seed','panel','branch','control','stage','index','turn'])
                if key in jobs:
                    assert jobs[key] == rec['decision_key']
                jobs[key] = rec['decision_key']
                if name == 'reused_calls.jsonl':
                    nr += 1;costs['reused_calls'] += 1
                else:
                    assert canonical_sha({k:rec[k] for k in ['messages','schema','seed']}) == rec['decision_key']
                    if rec['decision_key'] in calls:
                        assert all(rec[k] == calls[rec['decision_key']][k] for k in ['messages','schema','seed','parsed'])
                    calls[rec['decision_key']] = rec
                    nc += 1
                    costs.update(calls=1,prompt_tokens=rec['prompt_tokens'],completion_tokens=rec['completion_tokens'],
                        parse_errors=int(bool(rec['parse_error'])))
        assert (nc,nr) == (runtime['calls'],runtime['reused_calls'])
    return rows,shadows,info,hashes,duplicates,costs,calls


def load_cost_only(folders,reference,hashes,calls):
    """Retain every actual legacy request/launch, excluding all old outcomes.

    A failed run need not have runtime.json. Its absence is not a zero load/run
    timer. Legacy profiles and partial runs supply exact cached inputs only;
    faithful complete recovered trajectories exclusively define the estimand.
    """
    info,costs,excluded,actual_origins = {},Counter(),[],defaultdict(list)
    for folder in dict.fromkeys(folders):
        manifest_path = folder/'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        assert manifest['experiment'] == 'E85'
        for field in ['model','data_sha256','max_turns','primary_conditions','controls','revision_conditions',
                'fact_check_sentence','statement_templates']:
            assert manifest[field] == reference[field],('Legacy scientific configuration differs',field,folder)
        assert not manifest['world_rules_modified'] and manifest['new_cloud_calls'] == 0
        runtime_path = folder/'runtime.json'
        runtime = json.loads(runtime_path.read_text()) if runtime_path.exists() else None
        info[folder] = manifest,runtime
        for name in ['manifest.json','runtime.json','episodes.jsonl','states.jsonl','shadow_facts.jsonl',
                'first_responses.jsonl','failure.json','failure_summary.json','partial_runtime.json']:
            path = folder/name
            if path.exists():hashes[str(path)] = sha(path)
        nc=nr=0
        for name in ['model_calls.jsonl','reused_calls.jsonl']:
            path = folder/name
            if not path.exists():continue
            hashes[str(path)] = sha(path)
            with path.open() as f:
                for line in f:
                    if not line.strip():continue
                    rec = json.loads(line)
                    if name == 'reused_calls.jsonl':
                        nr += 1;costs['reused_calls'] += 1
                    else:
                        assert canonical_sha({k:rec[k] for k in ['messages','schema','seed']}) == rec['decision_key']
                        if rec['decision_key'] in calls:
                            assert all(rec[k] == calls[rec['decision_key']][k] for k in ['messages','schema','seed','parsed'])
                        calls[rec['decision_key']] = rec
                        actual_origins[rec['decision_key']].append(str(path))
                        nc += 1
                        costs.update(calls=1,prompt_tokens=rec['prompt_tokens'],completion_tokens=rec['completion_tokens'],
                            parse_errors=int(bool(rec['parse_error'])))
        if runtime is not None:
            assert runtime['new_cloud_calls'] == 0
            assert (nc,nr) == (runtime['calls'],runtime['reused_calls'])
        # Only count retained rows here; do not inspect their outcomes or add N.
        episode_path = folder/'episodes.jsonl'
        retained = sum(bool(line.strip()) for line in episode_path.open()) if episode_path.exists() else 0
        excluded.append({'run':str(folder),'runtime_present':runtime is not None,'recorded_model_calls':nc,
            'reused_calls':nr,'legacy_episode_records_not_in_estimand':retained,
            'scope':'Legacy pre-faithful-restore outcomes excluded as a whole; actual calls, tokens, occupied launch and exact cache entries retained.'})
    return info,costs,excluded,actual_origins


def cache_lineage(info,calls,legacy_origins):
    counts=Counter();sources=Counter()
    for folder in info:
        path=folder/'reused_calls.jsonl'
        if not path.exists():continue
        with path.open() as f:
            for line in f:
                if not line.strip():continue
                rec=json.loads(line);key=rec['decision_key']
                assert key in calls,('Reused result lacks an actual recorded input/response',path,key)
                counts['reused_request_records'] += 1
                if key in legacy_origins:
                    counts['reused_records_with_legacy_actual_input'] += 1
                    for origin in sorted(set(legacy_origins[key])):sources[origin]+=1
                else:
                    counts['reused_records_with_only_faithful_run_actual_input'] += 1
    return {**dict(counts),'legacy_actual_input_sources':dict(sources),
        'scope':'Every cached decision key resolves to an actual messages/schema/seed hash and retained response. A reused record is not another inference call or independent sample; multiple sources for one hash are listed, not silently deduplicated actual costs.'}


def build_cost_ledger(info,costs,hashes):
    entries=[]
    for folder,(manifest,runtime) in info.items():
        call_path=folder/'model_calls.jsonl';reuse_path=folder/'reused_calls.jsonl'
        call_count=sum(bool(x.strip()) for x in call_path.open()) if call_path.exists() else 0
        reused=sum(bool(x.strip()) for x in reuse_path.open()) if reuse_path.exists() else 0
        entry={'run':str(folder),'profile':manifest['profile'],'runtime_present':runtime is not None,
            'calls':call_count,'reused_calls':reused,'outcomes_used':bool(manifest.get('_report_outcomes_used')),
            'call_count_scope':'Complete serialized model_calls.jsonl response records.',
            'aborted_inflight_unserialized_generation':('UNKNOWN_POSSIBLE' if runtime is None else 'completed_run_marker'),
            'runtime_load_seconds':runtime.get('model_load_seconds') if runtime else None,
            'runtime_run_seconds':runtime.get('wall_seconds') if runtime else None}
        entry['runtime_model_load_plus_run_seconds']=(entry['runtime_load_seconds']+entry['runtime_run_seconds']
            if entry['runtime_load_seconds'] is not None and entry['runtime_run_seconds'] is not None else None)
        path=folder.parent/(folder.name+'_launch.json')
        if path.exists():
            launch=json.loads(path.read_text());hashes[str(path)]=sha(path)
            for field in ['driver_sha256','data_sha256']:assert launch[field]==manifest[field]
            start=launch['start_epoch'];end=launch.get('end_epoch')
            fallback=(folder/'runtime.json').stat().st_mtime if runtime is not None else None
            endpoint=end if end is not None else fallback
            entry.update(launch_metadata=str(path),host=launch['host'],gpu=launch['gpu'],
                pid=launch.get('pid'),launch_epoch=start,wrapper_end_epoch=end,
                wrapper_exit_code=launch.get('exit_code'),original_runtime_mtime_epoch=fallback,
                observed_occupied_slot_endpoint=('wrapper_observed_child_exit' if end is not None
                    else 'runtime_file_mtime_fallback' if fallback is not None else None),
                observed_occupied_slot_seconds=endpoint-start if endpoint is not None else None)
            if endpoint is not None:assert endpoint>=start
            if entry['runtime_model_load_plus_run_seconds'] is not None and endpoint is not None:
                assert endpoint-start>=entry['runtime_model_load_plus_run_seconds']-2
        else:
            entry.update(launch_metadata=None,observed_occupied_slot_endpoint=None,observed_occupied_slot_seconds=None)
        entries.append(entry)
    loads=[x['runtime_load_seconds'] for x in entries if x['runtime_load_seconds'] is not None]
    runs=[x['runtime_run_seconds'] for x in entries if x['runtime_run_seconds'] is not None]
    timed=[x for x in entries if x['observed_occupied_slot_seconds'] is not None]
    return {**costs,'sum_known_model_load_seconds':sum(loads),'sum_known_run_loop_wall_seconds':sum(runs),
        'unknown_model_load_timer_runs':len(entries)-len(loads),'unknown_run_loop_timer_runs':len(entries)-len(runs),
        'known_runtime_model_load_plus_run_GPU_hours':sum(x['runtime_model_load_plus_run_seconds'] for x in entries
            if x['runtime_model_load_plus_run_seconds'] is not None)/3600,
        'observed_occupied_GPU_slot_hours':sum(x['observed_occupied_slot_seconds'] for x in timed)/3600,
        'observed_slot_runs':len(timed),'total_runs':len(entries),
        'unknown_occupied_slot_runs':len(entries)-len(timed),
        'wrapper_exit_observed_runs':sum(x['observed_occupied_slot_endpoint']=='wrapper_observed_child_exit' for x in timed),
        'runtime_mtime_fallback_runs':sum(x['observed_occupied_slot_endpoint']=='runtime_file_mtime_fallback' for x in timed),
        'per_run':entries,'new_cloud_calls':0,
        'scope':'Count each supplied launch and complete serialized model-call response record once, including legacy profiles, failed partial queues and faithful recovery. Calls/tokens are recorded responses; aborted workers may have in-flight generations that never returned or were never serialized, whose count/tokens are unknown and not estimated. Wrapper occupied slots include that work. Reused cache records add no inference cost or N. Occupied GPU-slot intervals prefer wrapper start_epoch to observed child exit end_epoch, including loading/CPU waits/teardown; runtime mtime is an explicitly weaker fallback only. Runtime wall_seconds covers the execution loop, not GPU-active or inference-only time. Missing aborted-run load/run sub-timers remain unknown; observed occupied slots and recorded tokens are still counted.'}


def compatibility_summary(info,legacy_info,hashes):
    overlays=[m.get('compatibility_overlay') for m,_ in info.values()]
    if not any(overlays):return None
    assert all(overlays),'Faithful and pre-restoration outcomes must not be mixed'
    first=overlays[0]
    for overlay in overlays:
        for key in ['overlay_sha256','frozen_driver_sha256','operative_loader']:
            assert overlay[key]==first[key]
        for partial in overlay['partial_runs']:
            folder=Path(partial['path'])
            assert folder in legacy_info,('Declared partial launch omitted from costs',folder)
            assert sha(folder/'manifest.json')==partial['manifest_sha256']
            assert sha(folder/'model_calls.jsonl')==partial['model_calls_sha256']
            assert sum(bool(x.strip()) for x in (folder/'model_calls.jsonl').open())==partial['calls']
    freeze_path=Path(__file__).resolve().parents[1]/'results/E85_compatibility_freeze.json'
    freeze=json.loads(freeze_path.read_text())
    assert freeze['overlay_sha256']==first['overlay_sha256']
    assert freeze['base_driver_sha256']==first['frozen_driver_sha256']
    audit_path=Path(freeze['cpu_audit_path'])
    assert sha(audit_path)==freeze['cpu_audit_sha256']
    audit=json.loads(audit_path.read_text())
    restored={e['history_id'] for e in audit['compatibility_events'] if e['kind']=='source_scalar_restoration'}
    for path in [freeze_path,audit_path,Path(first['overlay_path'])]:hashes[str(path)]=sha(path)
    return {'overlay_sha256':first['overlay_sha256'],'frozen_driver_sha256':first['frozen_driver_sha256'],
        'operative_loader':first['operative_loader'],'freeze_path':str(freeze_path),'freeze_sha256':sha(freeze_path),
        'sourcecut_full_JSON_exact_after_restoration':audit['sourcecuts_full_JSON_exact'],
        'sourcecut_histories_requiring_original_scalar_restoration':len(restored),
        'sourcecut_legacy_full_JSON_exact':len(audit['source_checks'])-len(restored),
        'old_profiles_exact_CPU_episode_replays':freeze['old_profiles_exact_episodes_and_states'],
        'partial_outcomes_used':False,
        'scope':'Environment/source restoration audit, not NPC failure evidence. Preserve original attack/xp/reward_xp scalars omitted by legacy loading and deepcopy only after failed exact JSON roundtrip. Frozen scientific settings remain; all legacy outcomes are excluded, while exact input caches and all actual costs are retained.'}


def source_X_possession(histories):
    """Descriptive POST-HOC prior-state context from already completed E84.

    A new source-cut branch is not the beginning of the character's history.
    Preserve earlier possession/receipts without declaring any promise met.
    """
    requests=defaultdict(list)
    for history in histories.values():requests[Path(history['source_episode_path'])].append(history)
    output={}
    for path,group in requests.items():
        file_sha=sha(path)
        for h in group:assert file_sha==h['source_episode_file_sha256']
        selected={(h['case_id'],h['source_seed']):[] for h in group}
        with path.open() as f:
            for line in f:
                if not line.strip():continue
                row=json.loads(line);key=(row['case_id'],row['seed'])
                if key in selected:selected[key].append(row)
        for h in group:
            candidates=selected[h['case_id'],h['source_seed']]
            assert len(candidates)==1
            source=candidates[0]
            # Source inventory uses compact canonical JSON; decision-cache keys
            # deliberately retain the frozen client's default separators.
            source_sha=hashlib.sha256(json.dumps(source,sort_keys=True,ensure_ascii=False,
                separators=(',',':')).encode()).hexdigest()
            assert source_sha==h['source_episode_canonical_sha256']
            actors=mapped_case(h)['actor_ids'];npc=actors[0];x=h['x_item_id']
            prior_initial=ultimate_owner(source['initial_state'],x,actors)==npc
            events=([source['opening']] if source.get('opening') else [])+[
                t for t in source['turns'] if t['turn']<h['source_turn']]
            receipts=[];ever=prior_initial
            for t in events:
                before=ultimate_owner(t['before'],x,actors);after=ultimate_owner(t['after'],x,actors)
                ever=ever or after==npc
                if before!=npc and after==npc:
                    receipts.append({'source_turn':t['turn'],'event_identity':t['event_identity'],
                        'actor_id':t['actor'],'actor_role':'npc' if t['actor']==npc else 'player',
                        'native_result_success':successful(t)})
            output[h['history_id']]={'X_possessed_in_original_episode_initial_state':prior_initial,
                'X_possession_observed_before_source_cut':ever,'prior_X_receipt_events':receipts,
                'source_episode_path':str(path),'source_episode_canonical_sha256':h['source_episode_canonical_sha256'],
                'scope':'Observed prior possession is not a completed promise or full original purpose.'}
    return output


def receipt_Y_order(row,ownership_events,prior):
    """POST-HOC descriptive timing; do not add inferential contrasts or filter."""
    npc,player=row['actor_ids'];x,y=row['x_item_id'],row['y_item_id']
    receipts=[e for e in ownership_events if e['item_id']==x and e['owner_before']!=npc and e['owner_after']==npc]
    first_X=receipts[0] if receipts else None
    Y_gives=[t for t in row['turns'] if t['index']==0 and successful(t)
        and t['event_identity']==['GiveObjectEvent',[y,player]]]
    first_Y=Y_gives[0] if Y_gives else None
    if first_Y is None:category='no_NPC_Give_Y_observed'
    elif first_X is None:category='NPC_Give_Y_without_X_receipt_since_cut'
    elif first_X['turn']<first_Y['turn']:category='X_receipt_before_NPC_Give_Y'
    elif first_X['turn']>first_Y['turn']:category='NPC_Give_Y_before_X_receipt'
    else:category='same_native_event'
    def kind(e):
        if e is None:return None
        event=e['event_identity'][0]
        if e['index']==1 and event=='GiveObjectEvent':
            return 'scripted_player_Give' if e['turn']<0 else 'responsive_player_Give'
        if e['index']==0 and event=='GetObjectEvent':return 'NPC_Get'
        if e['index']==0 and event=='StealObjectEvent':return 'NPC_Steal'
        return ('NPC_' if e['index']==0 else 'player_')+event
    return {'category':category,'first_X_receipt_since_cut':first_X,
        'first_X_receipt_source_kind':kind(first_X),'all_X_receipts_since_cut':receipts,
        'first_NPC_Give_Y_turn':first_Y['turn'] if first_Y else None,
        'X_ever_received_since_cut_before_first_Give_Y':(any(e['turn']<first_Y['turn'] for e in receipts) if first_Y else None),
        'NPC_currently_holds_X_before_first_Give_Y':(ultimate_owner(first_Y['before'],x,row['actor_ids'])==npc if first_Y else None),
        'no_X_receipt_since_source_cut':not receipts,
        'no_X_possession_seen_in_source_prefix_or_continuation':not prior['X_possession_observed_before_source_cut'] and not receipts,
        'prior_source_context':prior,
        'scope':'Descriptive POST-HOC event order, including initial scripted native Give. NPC Get/Steal is acquisition, not player fulfillment. No_Y remains in the full denominator. No significance test, new condition or cooperation-correctness label.'}


def read_episode(row, history,prior):
    case = mapped_case(history)
    actors,bindings,quests = case['actor_ids'],case['goal_bindings'],case['quests']
    assert row['actor_ids'] == actors and row['quest_files'] == [q['source_file'] for q in quests]
    for field in ['history_id','case_id','graph_sha256','model_origin','source_seed','source_turn','source_role_map','x_item_id','y_item_id']:
        assert row[field] == history[field]
    supported = [bool(b.get('item_id')) and (b['verb'] not in ['give','put'] or b.get('target_id') is not None) for b in bindings]
    assert supported == row['strict_goal_measurement_supported']
    strict = [False if x else None for x in supported]
    order = [history['source_role_map'][k] for k in ['npc','player']]
    consumed = [bool(history.get('pre_player_consumed_by_actor',[False,False])[i]) for i in order]
    def goals(state):
        return [physical_goal(b,a,state,actors,used) for b,a,used in zip(bindings,actors,consumed)]
    source_initial = goals(row['initial_state'])
    assert source_initial == row['physical_goal_initial']
    ever = list(source_initial)
    current = row['initial_state']
    counts,events,failed_flags,errors = Counter(),Counter(),Counter(),Counter()
    flows,speeches,milestones = [],[],{}
    item_events=[];ownership_events=[]
    first_strict = [None,None]
    x,y = row['x_item_id'],row['y_item_id']
    assert len(row['interventions']) == 2
    assert [t['turn'] for t in row['interventions']] == [-2,-1]
    turns = row['turns']
    assert [t['turn'] for t in turns] == list(range(len(turns)))
    assert len(turns) <= 24
    if row['stop'] == 'turn_limit':
        assert len(turns) == 24
    after_intervention = None
    perturn_goals = {}
    for t in row['interventions'] + turns:
        turn,index = t['turn'],t['index']
        actor,prefix = actors[index],('npc_' if index == 0 else 'player_')
        assert t['actor'] == actor and t['before'] == current
        assert index == (1 if turn < 0 else turn%2)
        assert t['material_changed'] == (t['before'] != t['after'])
        event,ids = t['event_identity']
        assert event == t['event_type']
        ok = successful(t)
        for item in [x,y]:
            before_owner=ultimate_owner(t['before'],item,actors);after_owner=ultimate_owner(t['after'],item,actors)
            if before_owner!=after_owner:
                ownership_events.append({'turn':turn,'index':index,'actor_id':actor,'item_id':item,
                    'event_identity':t['event_identity'],'owner_before':before_owner,'owner_after':after_owner,
                    'native_result_success':ok,'decision_source':t.get('decision_source'),
                    'phase':'intervention' if turn<0 else 'continuation'})
        phase = 'intervention' if turn < 0 else 'continuation'
        events[(phase,str(index),event,'successful' if ok else 'rejected_or_failed')] += 1
        if t.get('stochastic_failure'):
            failed_flags[(phase,str(index),event)] += 1
        if t.get('error') or t.get('native_exception'):
            errors[(phase,str(index),str(t.get('error') or t['native_exception']))] += 1
        if ok:
            expected = strict_goal_identity(bindings[index],quests[index],t['before'])
            if t.get('original_goal_current_identity') is not None:
                assert t['original_goal_current_identity'] == expected
            if supported[index] and expected == t['event_identity']:
                strict[index] = True
                if first_strict[index] is None:first_strict[index] = turn
            if event in CONSUME and ids and ids[0] == bindings[index].get('item_id'):
                assert t['after'][ids[0]]['container'] == 'VOID'
                consumed[index] = True
            if event in ['GiveObjectEvent','GetObjectEvent','StealObjectEvent','DropObjectEvent','PutObjectInEvent']:
                item = ids[0]
                before,after = t['before'][item]['container'],t['after'][item]['container']
                assert before != after
                flows.append({'turn':turn,'index':index,'event':event,'item_id':item,
                    'from':before,'to':after,'owner_before':ultimate_owner(t['before'],item,actors),
                    'owner_after':ultimate_owner(t['after'],item,actors),'phase':phase})
            if event in SPEECH:
                heard = [m['text'] for m in t.get('messages',[]) if m['viewer'] == actors[1-index] and m['event'] == event]
                speeches.append({'turn':turn,'index':index,'event':event,'target_ids':ids,
                    'utterance':t['choice']['utterance'],'peer_received_messages':heard,'phase':phase})
            if turn >= 0 and ids and ids[0] in [x,y]:
                item_events.append({'turn':turn,'index':index,'event':event,'item_id':ids[0],
                    'target_ids':ids,'before_parent':t['before'][ids[0]]['container'],
                    'after_parent':t['after'][ids[0]]['container'],
                    'equipped_after':t['after'][ids[0]].get('equipped')})
        if turn >= 0:
            counts[prefix+'opportunities_recorded'] += 1
            counts[prefix+'local_model_choices_recorded'] += int(t.get('model_decision') is True)
            counts[prefix+'native_rejections'] += int(not t['legal'])
            counts[prefix+'native_failed_flags'] += int(bool(t.get('stochastic_failure')))
            counts[prefix+'native_exceptions'] += int(bool(t.get('native_exception')))
            counts[prefix+'legal_unexecuted'] += int(t['legal'] and not t.get('executed'))
            counts[prefix+'non_speech_payloads_not_sent'] += int(event not in SPEECH and bool(t['choice'].get('utterance')))
            if ok:
                counts[prefix+'actual_speech_count'] += int(event in SPEECH)
                counts[prefix+'peer_heard_speech_count'] += int(event in SPEECH and bool(heard))
                counts[prefix+'successful_material_actions'] += int(t['material_changed'])
                for cls,label in [('GiveObjectEvent','give'),('StealObjectEvent','steal'),('GetObjectEvent','get'),
                        ('PutObjectInEvent','put'),('DropObjectEvent','drop'),('RemoveObjectEvent','remove'),
                        ('BlockEvent','block'),('WaitEvent','wait')]:
                    counts[prefix+label+'_count'] += int(event == cls)
                for item,label in [(x,'X'),(y,'Y')]:
                    if ids and ids[0] == item:
                        for cls,action in [('GiveObjectEvent','give'),('DropObjectEvent','drop'),('PutObjectInEvent','put'),
                                ('RemoveObjectEvent','remove')]:
                            counts[prefix+action+'_'+label+'_count'] += int(event == cls)
                        counts[prefix+'consume_'+label+'_count'] += int(event in CONSUME)
                        counts[prefix+'equip_'+label+'_count'] += int(event in ['WearEvent','WieldEvent','EquipObjectEvent'])
                        counts[prefix+'give_'+label+'_to_peer_count'] += int(event == 'GiveObjectEvent' and ids[1] == actors[1-index])
        now = goals(t['after'])
        ever = [True if v is True else old if old is not None else v for old,v in zip(ever,now)]
        assert strict == t['strict_goal_ever'] and now == t['physical_goal_now'] and ever == t['physical_goal_ever']
        current = t['after']
        if turn == -1:
            after_intervention = list(now)
            assert current == row['post_intervention_state']
        elif turn >= 0:
            perturn_goals[turn] = list(now)
    assert current == row['final_state']
    assert strict == row['strict_goal_ever'] and goals(current) == row['physical_goal_now'] and ever == row['physical_goal_ever']
    assert after_intervention is not None
    revision = row['panel'] == 'revision'
    request_delivered = any(t['turn'] == 1 and t.get('phase') == 'partner_revision_statement' and successful(t) for t in turns)
    branchpoint = row.get('pre_revision_state') if revision else row['post_intervention_state']
    branchpoint_goals = (goals(branchpoint) if branchpoint is not None else [None,None])
    # For consume goals the source item is the delivered X; none is already
    # consumed at the post-intervention cut. Retain the explicit source flags.
    if revision and 0 in perturn_goals:branchpoint_goals = perturn_goals[0]
    eligible_turns = [t for t in turns if t['turn'] >= (2 if revision else 0)]
    metric = dict(counts)
    for prefix in ['npc_','player_']:
        for label in ['opportunities_recorded','local_model_choices_recorded','native_rejections','native_failed_flags',
                'native_exceptions','legal_unexecuted','non_speech_payloads_not_sent','actual_speech_count',
                'peer_heard_speech_count','successful_material_actions','give_count','steal_count','get_count',
                'put_count','drop_count','remove_count','block_count','wait_count']:
            metric.setdefault(prefix+label,0)
        for label in ['X','Y']:
            for action in ['give','drop','put','remove','consume','equip','give_to_peer']:
                field = prefix+action+'_'+label+'_count' if action != 'give_to_peer' else prefix+'give_'+label+'_to_peer_count'
                metric.setdefault(field,0)
    for index,prefix in enumerate(['npc_','player_']):
        for label,values in [('goal_physical_source_cut',source_initial),('goal_physical_post_intervention',after_intervention),
                ('goal_physical_ever_since_cut',ever),('goal_physical_final',goals(current)),('goal_physical_branchpoint',branchpoint_goals),
                ('goal_strict_event_ever_since_cut',strict)]:
            metric[prefix+label] = None if values[index] is None else int(values[index])
        eligible_values = [perturn_goals[t['turn']][index] for t in eligible_turns]
        metric[prefix+'goal_new_physical_after_branchpoint'] = (int(any(v is True for v in eligible_values))
            if branchpoint_goals[index] is False and (not revision or request_delivered) else None)
        metric[prefix+'dead_final'] = int(row['final_dead'][index])
        metric[prefix+'protocol_failure'] = int(row.get('protocol_failure',{}).get('actor_index') == index)
    for item,label in [(x,'X'),(y,'Y')]:
        for index,role in enumerate(['npc','player']):
            start = row['post_intervention_state']
            held_states = [(t['turn'],ultimate_owner(t['after'],item,actors) == actors[index]) for t in turns]
            start_held = ultimate_owner(start,item,actors) == actors[index]
            metric[role+'_holds_'+label+'_post_intervention'] = int(start_held)
            metric[role+'_holds_'+label+'_ever_continuation'] = int(start_held or any(v for _,v in held_states))
            metric[role+'_holds_'+label+'_branchpoint'] = (int(ultimate_owner(branchpoint,item,actors) == actors[index])
                if branchpoint is not None else None)
            metric[role+'_holds_'+label+'_final'] = int(ultimate_owner(current,item,actors) == actors[index])
            milestones[role+'_first_holds_'+label] = -1 if start_held else next((t for t,v in held_states if v),None)
    metric['npc_gave_Y_to_player'] = int(metric['npc_give_Y_to_peer_count'] > 0)
    metric['npc_gave_X_to_player'] = int(metric['npc_give_X_to_peer_count'] > 0)
    metric['X_NPC_to_player_ownership_change'] = int(any(f['turn'] >= 0 and f['item_id'] == x
        and f['owner_before'] == actors[0] and f['owner_after'] == actors[1] for f in flows))
    metric['npc_consumed_X'] = int(metric['npc_consume_X_count'] > 0)
    metric['npc_equipped_X'] = int(metric['npc_equip_X_count'] > 0)
    metric['npc_put_X'] = int(metric['npc_put_X_count'] > 0)
    metric['X_directly_VOID_at_branchpoint'] = (int(branchpoint[x]['container'] == 'VOID') if branchpoint is not None else None)
    metric['X_directly_VOID_final'] = int(current[x]['container'] == 'VOID')
    metric['X_equipped_at_branchpoint'] = (int(bool(branchpoint[x].get('equipped'))) if branchpoint is not None else None)
    metric['npc_X_equipped_at_branchpoint'] = (int(ultimate_owner(branchpoint,x,actors)==actors[0]
        and bool(branchpoint[x].get('equipped'))) if branchpoint is not None else None)
    metric['protocol_failure_episode'] = int(bool(row.get('protocol_failure')))
    metric['revision_request_delivered'] = int(request_delivered) if revision else None
    first=next((t for t in turns if t['turn']==0),None)
    metric['first_NPC_event_recorded']=int(first is not None)
    metric['first_NPC_protocol_failure']=int(row.get('protocol_failure',{}).get('turn')==0)
    for label,item in [('X',x),('Y',y)]:
        for action,classes in [('give',{'GiveObjectEvent'}),('consume',CONSUME),
                ('equip',{'WearEvent','WieldEvent','EquipObjectEvent'}),('put',{'PutObjectInEvent'}),
                ('drop',{'DropObjectEvent'}),('remove',{'RemoveObjectEvent'})]:
            metric['first_NPC_'+action+'_'+label]=int(first is not None and successful(first)
                and first['event_type'] in classes and first['event_identity'][1] and first['event_identity'][1][0]==item)
            milestones['npc_first_'+action+'_'+label]=next((e['turn'] for e in item_events
                if e['index']==0 and e['event'] in classes and e['item_id']==item),None)
        metric['first_NPC_gave_'+label+'_to_player']=int(first is not None and successful(first)
            and first['event_identity']==['GiveObjectEvent',[item,actors[1]]])
    metric['first_NPC_actual_speech']=int(first is not None and successful(first) and first['event_type'] in SPEECH)
    metric['first_NPC_peer_heard_speech']=int(any(s['turn']==0 and s['index']==0 and s['peer_received_messages'] for s in speeches))
    metric['first_NPC_original_goal_event']=int(first is not None and successful(first) and
        first.get('original_goal_current_identity') is not None and first['event_identity']==first['original_goal_current_identity'])
    for index,role in enumerate(['npc','player']):
        milestones[role+'_first_physical_goal_after_intervention']=(-1 if after_intervention[index] is True else
            next((t for t,v in perturn_goals.items() if v[index] is True),None))
        milestones[role+'_first_strict_original_event_since_cut']=first_strict[index]
    # The revision estimand concerns actions following the shared first response,
    # not a second use of the same turn0. It may be undefined after upstream stop.
    if revision:
        for label,item in [('X',x),('Y',y)]:
            for action,classes in [('give',{'GiveObjectEvent'}),('consume',CONSUME),('equip',{'WearEvent','WieldEvent','EquipObjectEvent'}),('put',{'PutObjectInEvent'})]:
                value = any(t['index'] == 0 and successful(t) and t['event_type'] in classes
                    and t['event_identity'][1] and t['event_identity'][1][0] == item for t in eligible_turns)
                metric['post_revision_npc_'+action+'_'+label] = int(value) if request_delivered else None
            metric['post_revision_npc_gave_'+label+'_to_player'] = (int(any(t['index'] == 0 and successful(t)
                and t['event_identity'] == ['GiveObjectEvent',[item,actors[1]]] for t in eligible_turns))
                if request_delivered else None)
        metric['post_revision_X_NPC_to_player_ownership_change']=(int(any(f['turn']>=2 and f['item_id']==x
            and f['owner_before']==actors[0] and f['owner_after']==actors[1] for f in flows)) if request_delivered else None)
    else:
        for label in ['X','Y']:
            for action in ['give','consume','equip','put']:
                metric['post_revision_npc_'+action+'_'+label] = None
            metric['post_revision_npc_gave_'+label+'_to_player'] = None
        metric['post_revision_X_NPC_to_player_ownership_change']=None
    return {**{k:row[k] for k in ['history_id','seed','panel','branch','control','graph_sha256','case_id',
                'model_origin','source_seed','source_turn','source_role_map','x_item_id','y_item_id']},
        'metrics':metric,'stop':row['stop'],'final_dead':row['final_dead'],'final_health':row['final_health'],
        'source_boundary':history['source_boundary'],'first_strict_turn':first_strict,'first_holding':milestones,
        'first_NPC_event':first['event_identity'] if first is not None else None,
        'branchpoint_item_state':({label:{'item_id':item,'direct_parent':branchpoint[item]['container'],
            'ultimate_owner':ultimate_owner(branchpoint,item,actors),'equipped':branchpoint[item].get('equipped'),
            'directly_VOID':branchpoint[item]['container']=='VOID'} for label,item in [('X',x),('Y',y)]}
            if branchpoint is not None else None),
        'goal_verbs':[b['verb'] for b in bindings],'flows':flows,'speeches':speeches,'item_uses':item_events,
        'ownership_events':ownership_events,'POST_HOC_X_receipt_and_Y_order':receipt_Y_order(row,ownership_events,prior),
        'event_counts':{'/'.join(k):v for k,v in events.items()},
        'native_failed_flags_by_event':{'/'.join(k):v for k,v in failed_flags.items()},
        'native_errors':{'/'.join(k):v for k,v in errors.items()}}


def estimate(observations, profile=False):
    """Each tuple: original graph, source history, new episode seed, value.

    Average seeds within each history, histories within graph, then equally
    weight the measurable original graphs. Unknowns are not failures.
    """
    known = [(g,h,s,float(v)) for g,h,s,v in observations if v is not None]
    histories = defaultdict(list)
    for graph, history, seed, value in known:
        histories[graph,history].append(value)
    graphs = defaultdict(list)
    for (graph,history), values in histories.items():
        graphs[graph].append(float(np.mean(values)))
    values = np.asarray([np.mean(graphs[g]) for g in sorted(graphs)], dtype=float)
    result = {'mean':float(values.mean()) if len(values) else None,
        'known_history_seed_pairs':len(known), 'unknown_history_seed_pairs':len(observations)-len(known),
        'histories':len(histories), 'independent_graphs':len(values),
        'raw_sum':float(sum(x[3] for x in known))}
    if len(values) and not profile:
        n = len(values)
        if n not in _WEIGHTS:
            rng = np.random.default_rng(BOOTSTRAP_SEED)
            _WEIGHTS[n] = rng.multinomial(n,np.full(n,1/n),size=BOOTSTRAPS)/n
        result['graph_bootstrap_95'] = list(map(float,np.quantile(_WEIGHTS[n]@values,[.025,.975])))
    return result


def condition_label(condition):
    return '/'.join(condition)


def aggregate(details, profile=False):
    """Derive every predeclared pairing from the same complete episode set."""
    index = {episode_key(d):d for d in details}
    assert len(index) == len(details)
    history_seeds = sorted({(d['history_id'],d['seed']) for d in details})
    fields = sorted({f for d in details for f in d['metrics']})
    groups = {}
    for condition in CONDITIONS:
        subset = [index[(h,s,*condition)] for h,s in history_seeds]
        groups[condition_label(condition)] = {f:estimate([
            (d['graph_sha256'],d['history_id'],d['seed'],d['metrics'][f]) for d in subset],profile) for f in fields}
    specifications = []
    for control in CONTROLS:
        specifications += [
            ('real_claim_minus_claim_only/'+control, ('primary','real_claim',control), ('primary','claim_only',control)),
            ('claim_only_minus_pending_truth/'+control, ('primary','claim_only',control), ('primary','pending_truth',control))]
    for branch in FACT_BRANCHES:
        specifications.append(('check_minus_normal/'+branch,('primary',branch,'check'),('primary',branch,'normal')))
    specifications.append(('withdraw_minus_continue',('revision','withdraw','check'),('revision','continue','check')))
    contrasts = {}
    for name, treatment, reference in specifications:
        metrics = {}
        for field in fields:
            observations = []
            for h,s in history_seeds:
                t,r = index[(h,s,*treatment)],index[(h,s,*reference)]
                assert t['graph_sha256'] == r['graph_sha256']
                tv,rv = t['metrics'][field],r['metrics'][field]
                observations.append((t['graph_sha256'],h,s,None if tv is None or rv is None else tv-rv))
            metrics[field] = estimate(observations,profile)
        contrasts[name] = {'treatment':condition_label(treatment), 'reference':condition_label(reference),
            'estimand':'Paired outcome difference; no universal correctness or utility interpretation.', 'metrics':metrics}
    return groups, contrasts


def verify_common_prefixes(rows):
    counts = Counter()
    for history,seed in sorted({k[:2] for k in rows}):
        real = rows[history,seed,'primary','real_claim','check']
        first = next((t for t in real['turns'] if t['turn'] == 0),None)
        for branch in ['continue','withdraw']:
            revision = rows[history,seed,'revision',branch,'check']
            assert revision['initial_state'] == real['initial_state']
            assert revision['interventions'] == real['interventions']
            assert revision['post_intervention_state'] == real['post_intervention_state']
            other = next((t for t in revision['turns'] if t['turn'] == 0),None)
            assert other == first,('Revision first response differs',history,seed,branch)
            ref = revision['shared_first_response']
            assert ref['history_id'] == history and ref['seed'] == seed
            assert ref['model_input_key'] == (first.get('model_input_key') if first else None)
            counts['exact_first_response_pairs'] += int(first is not None)
            counts['upstream_stopped_before_first_response_pairs'] += int(first is None)
        assert rows[history,seed,'revision','continue','check']['shared_first_response'] == rows[
            history,seed,'revision','withdraw','check']['shared_first_response']
        for control in CONTROLS:
            true,claim,pending = [rows[history,seed,'primary',b,control] for b in FACT_BRANCHES]
            assert true['initial_state'] == claim['initial_state'] == pending['initial_state']
            assert true['interventions'][1]['choice']['utterance'] == claim['interventions'][1]['choice']['utterance']
            assert claim['post_intervention_state'] == pending['post_intervention_state']
            counts['matched_same_claim_changed_fact_pairs'] += 1
            counts['matched_same_physical_changed_claim_pairs'] += 1
    return dict(counts)


def shadow_report(shadows,rows,profile):
    details = []
    for (history,seed,branch),record in sorted(shadows.items()):
        row = rows[history,seed,'primary',branch,'normal']
        state,actors,item = row['post_intervention_state'],row['actor_ids'],row['x_item_id']
        actual_owner = ultimate_owner(state,item,actors)
        actual_holder = 'npc' if actual_owner == actors[0] else 'player' if actual_owner == actors[1] else 'other'
        assert record['answers_never_used_by_action_policy']
        assert record['actual_holder'] == actual_holder and record['actual_npc_holds_x'] == (actual_holder == 'npc')
        assert record['actual_x_container'] == state[item]['container']
        parsed = record['parsed']
        valid = isinstance(parsed,dict) and set(parsed) == {'holder','npc_holds_x'}
        holder = parsed.get('holder') if isinstance(parsed,dict) else None
        holds = parsed.get('npc_holds_x') if isinstance(parsed,dict) else None
        valid = valid and holder in ['npc','player','other','uncertain'] and holds in ['yes','no','uncertain']
        metrics = {'valid_structured_answer':int(valid),
            'elicited_holder_correct':int(holder == actual_holder),
            'elicited_npc_holds_X_correct':int(holds == ('yes' if actual_holder == 'npc' else 'no')),
            'elicited_holder_uncertain':int(holder == 'uncertain'),
            'elicited_npc_holds_X_uncertain':int(holds == 'uncertain'),
            'elicited_answer_consistent':(int((holder == 'npc') == (holds == 'yes'))
                if holder in ['npc','player','other'] and holds in ['yes','no'] else None)}
        details.append({'history_id':history,'seed':seed,'branch':branch,'graph_sha256':row['graph_sha256'],
            'actual_holder':actual_holder,'parsed':parsed,'metrics':metrics,'model_input_key':record['model_input_key']})
    index = {(d['history_id'],d['seed'],d['branch']):d for d in details}
    groups = {branch:{field:estimate([(d['graph_sha256'],d['history_id'],d['seed'],d['metrics'][field])
        for d in details if d['branch'] == branch],profile) for field in details[0]['metrics']} for branch in FACT_BRANCHES}
    contrasts = {}
    for treatment,reference in [('real_claim','claim_only'),('claim_only','pending_truth')]:
        values = {}
        for field in details[0]['metrics']:
            observations = []
            for h,s in sorted({(d['history_id'],d['seed']) for d in details}):
                t,r = index[h,s,treatment],index[h,s,reference]
                tv,rv = t['metrics'][field],r['metrics'][field]
                observations.append((t['graph_sha256'],h,s,None if tv is None or rv is None else tv-rv))
            values[field] = estimate(observations,profile)
        contrasts[treatment+'_minus_'+reference] = values
    return {'logical_reports':len(details),'groups':groups,'paired_contrasts':contrasts,
        'scope':'Separate elicited factual reports, never fed to action history. Correctness is relative to actual native ownership; not action-policy internal belief, mediation or a causal explanation of actions.'},details


def milestone_report(details):
    output={}
    for condition in CONDITIONS:
        subset=[d for d in details if (d['panel'],d['branch'],d['control'])==condition]
        events=Counter('NO_EVENT:'+d['stop'] if d['first_NPC_event'] is None else d['first_NPC_event'][0] for d in subset)
        milestones={}
        for field in sorted({key for d in subset for key in d['first_holding']}):
            def known(d):
                role=field.split('_',1)[0]
                if field.endswith('_first_physical_goal_after_intervention'):
                    return d['metrics'][role+'_goal_physical_post_intervention'] is not None
                if field.endswith('_first_strict_original_event_since_cut'):
                    return d['metrics'][role+'_goal_strict_event_ever_since_cut'] is not None
                return True
            eligible=[d for d in subset if known(d)]
            hist=Counter(str(d['first_holding'][field]) for d in eligible if d['first_holding'][field] is not None)
            milestones[field]={'first_turn_counts':dict(hist),
                'not_observed_known':sum(d['first_holding'][field] is None for d in eligible),
                'unknown_or_undefined':len(subset)-len(eligible)}
        output[condition_label(condition)]={'logical_branches':len(subset),'first_NPC_native_event_counts':dict(events),
            'first_milestones':milestones,'scope':'Raw logical-branch histograms, not independent samples or a latency-adjusted success score; -1 means already true after scripted transfer and statement.'}
    return output


def posthoc_order_report(details):
    groups={}
    for condition in CONDITIONS:
        subset=[d for d in details if (d['panel'],d['branch'],d['control'])==condition]
        categories=Counter();sources=Counter();before=Counter();current=Counter();prior=Counter()
        for d in subset:
            o=d['POST_HOC_X_receipt_and_Y_order']
            categories[o['category']]+=1
            sources[str(o['first_X_receipt_source_kind'])]+=1
            before[str(o['X_ever_received_since_cut_before_first_Give_Y'])]+=1
            current[str(o['NPC_currently_holds_X_before_first_Give_Y'])]+=1
            prior[str(o['prior_source_context']['X_possession_observed_before_source_cut'])]+=1
        groups[condition_label(condition)]={'logical_branches':len(subset),'event_order_counts':dict(categories),
            'first_X_receipt_source_kind_counts':dict(sources),
            'received_X_before_first_Y_Give_counts':dict(before),'holds_X_at_first_Y_Give_counts':dict(current),
            'prior_source_X_possession_counts':dict(prior)}
    return {'status':'DESCRIPTIVE_POST_HOC','groups':groups,
        'scope':'All logical branches, with no NPC Give Y retained as its own category. Counts are not independent graphs, no added CI/significance or subgroup filtering. Final primary contrasts are initial-treatment ITT: a responsive player can later actually Give X in claim_only/pending_truth, and NPC can acquire it independently. Actual receipt does not establish full promise fulfillment or utility.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',type=Path,nargs='+',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--profile',action='store_true')
    parser.add_argument('--cost-only-runs',type=Path,nargs='*',default=[],
        help='Retain legacy complete profiles/aborted partial launches and exact input cache costs; exclude all their outcomes.')
    args = parser.parse_args()
    assert not set(args.runs)&set(args.cost_only_runs),'A launch must not be costed twice'
    rows,shadows,info,hashes,duplicates,costs,calls = load_runs(args.runs,args.profile)
    manifest = next(iter(info.values()))[0]
    legacy_info,legacy_costs,excluded_legacy,legacy_origins=load_cost_only(args.cost_only_runs,manifest,hashes,calls)
    costs.update(legacy_costs)
    lineage=cache_lineage(info,calls,legacy_origins)
    restoration=compatibility_summary(info,legacy_info,hashes)
    source = Path(manifest['data'])
    assert sha(source) == manifest['data_sha256']
    histories = {h['history_id']:h for h in load_lines(source)}
    if not args.profile:
        assert any(not m['profile'] for m,_ in info.values())
        assert set(rows) == {(h,s,*c) for h in histories for s in SEEDS for c in CONDITIONS}, 'Full cohort not complete; no partial report'
    prefix_checks = verify_common_prefixes(rows)
    prior_X=source_X_possession(histories)
    details = [read_episode(row,histories[key[0]],prior_X[key[0]]) for key,row in sorted(rows.items())]
    groups,contrasts = aggregate(details,args.profile)
    shadow,shadow_details = shadow_report(shadows,rows,args.profile)
    cache = source.parent.parent/'e85_partner_performance_readback'
    cache.mkdir(exist_ok=True)
    detail_file = cache/(args.out.stem+'_episodes.jsonl')
    detail_file.write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in details))
    shadow_file = cache/(args.out.stem+'_shadow_facts.jsonl')
    shadow_file.write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in shadow_details))
    event_counts,failed_flags,errors,stops,origins = Counter(),Counter(),Counter(),Counter(),Counter()
    for d in details:
        condition = condition_label((d['panel'],d['branch'],d['control']))
        event_counts.update({condition+'/'+k:v for k,v in d['event_counts'].items()})
        failed_flags.update({condition+'/'+k:v for k,v in d['native_failed_flags_by_event'].items()})
        errors.update({condition+'/'+k:v for k,v in d['native_errors'].items()})
        stops[condition+'/'+d['stop']] += 1
    selected = {d['history_id'] for d in details}
    for history in selected:origins[histories[history]['model_origin']] += 1
    cost_info={folder:({**m,'_report_outcomes_used':True},r) for folder,(m,r) in info.items()}
    cost_info.update({folder:({**m,'_report_outcomes_used':False},r) for folder,(m,r) in legacy_info.items()})
    cost = build_cost_ledger(cost_info,costs,hashes)
    source_index=[{'history_id':hid,'graph_sha256':histories[hid]['graph_sha256'],
        'case_id':histories[hid]['case_id'],'source_role_map':histories[hid]['source_role_map'],
        'model_origin':histories[hid]['model_origin'],'source_seed':histories[hid]['source_seed'],
        'source_turn':histories[hid]['source_turn'],'x_item_id':histories[hid]['x_item_id'],'y_item_id':histories[hid]['y_item_id'],
        'original_goal_verbs':[b['verb'] for b in mapped_case(histories[hid])['goal_bindings']],
        'original_goal_sources':[q['source_file'] for q in mapped_case(histories[hid])['quests']],
        'source_boundary':histories[hid]['source_boundary']} for hid in sorted(selected)]
    purpose_index={}
    for hid in sorted(selected):
        h=histories[hid];case=mapped_case(h)
        for index,role in enumerate(['npc','player']):
            q=case['quests'][index];key=q['source_file']
            if key not in purpose_index:
                purpose_index[key]={'source_file':key,'character':q['character'],'graph_sha256':h['graph_sha256'],
                    'authored_goal':q['goal'],'goal_verb':case['goal_bindings'][index]['verb'],
                    'short_motivation':q.get('short_motivation'),'mid_motivation':q.get('mid_motivation'),
                    'long_motivation':q.get('long_motivation'),'observed_roles':[]}
            if role not in purpose_index[key]['observed_roles']:purpose_index[key]['observed_roles'].append(role)
    result = {'experiment':'E85','status':'PROFILE_TECHNICAL_ONLY' if args.profile else 'COMPLETE',
        'model':manifest['model'],'source_data':str(source),'data_sha256':sha(source),
        'driver_sha256':manifest['driver_sha256'],'report_sha256':sha(__file__),'source_sha256':hashes,
        'histories':len(selected),'source_pairs':len({histories[h]['case_id'] for h in selected}),
        'independent_graphs':len({histories[h]['graph_sha256'] for h in selected}),
        'logical_branches':len(rows),'seeds':sorted({k[1] for k in rows}),
        'source_history_model_origins':dict(origins),'exact_duplicate_episode_records':duplicates,
        'source_history_index':source_index,'excluded_legacy_outcomes':excluded_legacy,'input_cache_lineage':lineage,
        'source_role_purpose_index':{'roles':list(purpose_index.values()),
            'scope':'Deduplicated original atomic goal and motivations needed to interpret physical outcomes; no graph, full persona, timeline or dialogue is copied. These author texts do not certify that higher purposes have native completion flags or a single correct cooperative response.'},
        'source_and_fork_compatibility':restoration,
        'revision_fork_item_states':[{'history_id':d['history_id'],'seed':d['seed'],'graph_sha256':d['graph_sha256'],
            'first_NPC_event':d['first_NPC_event'],'item_state':d['branchpoint_item_state'],
            'player_already_holds_X_at_fork':d['metrics']['player_holds_X_branchpoint'],
            'scope':'Common first response/fork state, identical for withdraw and continue; not a post-hoc subgroup or correctness label.'}
            for d in details if d['panel']=='revision' and d['branch']=='continue'],
        'scope':'This model controls both original roles after fixed player interventions. Source history/model-origin/role/seed are nested under original graph, not independent NPC treatment effects. Each conditional continuation remains a distinct observed branch.',
        'measurement':{
            'primary_contrasts':'Within history/new seed: real_claim minus claim_only changes native contribution under identical claim; claim_only minus pending_truth changes claim under identical physical material state; check minus normal is the ordinary factual-instruction control.',
            'dynamic_ITT':'Terminal outcomes estimate the initial-treatment ITT under responsive continuation, not permanent withholding: claim_only/pending_truth players may later actually Give X, and NPC may Get/Steal X. The predeclared first NPC response precedes those later actions; event-order readback is descriptive POST-HOC, not mediation evidence.',
            'secondary':'withdraw minus continue begins with the exact same real_claim/check first NPC response and state; post_revision metrics count only new events on turns>=2 after actual request. Fork-time X/Y owner, already-returned-to-player status, equipped state and direct VOID state are explicit. Shared turn0 returns are not withdrawal-induced returns. A revision request expresses changed player preference; no external proof makes it obligatory or the original plan infeasible.',
            'weighting':'Average fixed seeds within source history, histories within original graph, then equally weight measurable original graphs; differences are paired before averaging. Every metric reports unknown exclusions and eligible history/graph counts.',
            'bootstrap':None if args.profile else {'draws':BOOTSTRAPS,'seed':BOOTSTRAP_SEED,'unit':'original graph','kind':'pointwise percentile'},
            'original_goal':'Strict successful actor/class/item/target event and literal material outcome are separate. Original atomic goal is not full private purpose or welfare. Source historical prior flags are retained in cached readback.',
            'initial_and_intervention':'Source-cut, scripted-contribution post-intervention, branchpoint and final states are distinct. A player Give may itself satisfy NPC Get/Steal possession; this is not an NPC continuation choice. New physical attainment excludes branchpoint-true/undefined observations explicitly.',
            'X_interpretation':'X names the item actually transferred by the player, not a gold label of useful contribution or completed promise. Source original Give/Put/other goals and purposes remain; original motives are referenced, never replaced by this transfer. The cohort is an exploratory nine-original-graph queue, not a large independent population.',
            'flows':'NPC Give Y, player possession, NPC Give X, consumption, equipment, Put and ownership changes are separate. X_NPC_to_player_ownership_change includes player Steal; it is not necessarily voluntary return. No transfer/return is universally correct cooperation.',
            'speech':'Only successful native speech with actual peer-visible messages is delivered dialogue. Non-speech utterance payloads are counted separately and never treated as promises. Full utterances/flows remain in cache, not semantic gold.',
            'failure':'Protocol/death/native rejection/exception and unknowns remain. Legacy driver stochastic_failure records event.failed, not exclusively random failures; event-type composition is explicit.',
            'first_holding':'-1 denotes already held after scripted intervention; 0..23 are continuation turn IDs, and null is never observed. Full source episodes, graphs and all raw histories remain in cache.'},
        'exact_pairing_checks':prefix_checks,'groups':groups,'paired_contrasts':contrasts,'shadow_fact_report':shadow,
        'first_response_and_milestones':milestone_report(details),
        'POST_HOC_X_receipt_and_Y_order':posthoc_order_report(details),
        'raw_counts':{'events':dict(event_counts),'native_failed_flags_by_event':dict(failed_flags),
            'native_errors':dict(errors),'stop':dict(stops),
            'scope':'Logical-branch record counts include copied common first responses and intervention prefixes; they are not independent samples or additional model calls.'},'cost':cost,
        'episode_readback':{'path':str(detail_file),'sha256':sha(detail_file),'logical_branches':len(details),
            'scope':'Complete derived native flows, actually received speech and source/branch provenance; raw graph and complete input artifacts remain in original run folders.'},
        'shadow_readback':{'path':str(shadow_file),'sha256':sha(shadow_file),'logical_reports':len(shadow_details)},
        'report_new_model_calls':0,'report_new_API_calls':0,'report_new_GPU_jobs':0}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'out':str(args.out),'status':result['status'],'logical_branches':len(rows),
        'histories':len(selected),'independent_graphs':result['independent_graphs'],
        'recorded_calls':costs['calls'],'exact_duplicates':len(duplicates)},ensure_ascii=False))


if __name__ == '__main__':
    main()
