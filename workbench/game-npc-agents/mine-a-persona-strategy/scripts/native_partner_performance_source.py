#!/usr/bin/env python3
"""E85 CPU source qualification from all completed E84 native histories.

No model calls or world edits. Primary cuts are original successful direct
Give events, with both original role directions considered separately. A
counterfactual native witness checks response feasibility; it is not an NPC
policy, an agreement annotation or evidence of mutual benefit.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from light_native_gate import load_event_modules
from light_npc_episodes import CACHE
from native_cooperation_episodes import header
from native_independent_goal_episodes import binding
from native_independent_goal_qualification import Witness, owner

WB = Path(__file__).resolve().parents[1]
SOURCE = CACHE / 'runs/e84_native_qualification/cross_snapshots.jsonl'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def lines(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s]


def good(turn):
    return bool(turn.get('legal') and turn.get('executed') and
                not turn.get('stochastic_failure') and not turn.get('native_exception'))


def native_paths(case, pregraph, npc, incoming, modules):
    qs = [binding(case, i) for i in range(2)]
    player = 1 - npc
    out = {}
    for arm in ['actual_give', 'withheld']:
        w = Witness(pregraph, qs, modules)
        incoming_ok = True
        if arm == 'actual_give':
            incoming_ok = w.run(case['actor_ids'][player], incoming[0], incoming[1],
                                'original_player_direct_Give_X')
        received_x = owner(w.graph, qs[npc]['item_id']) == case['actor_ids'][npc]
        before_response = len(w.steps)
        response_ok = bool(incoming_ok and w.help(player, 'give'))
        response = list(w.steps[before_response:])
        y_acquired = owner(w.graph, qs[player]['item_id']) == case['actor_ids'][player]
        # A finite next-goal witness is descriptive only. Get/Steal acquisition
        # is physically realized by receipt, not an original Get/Steal event.
        before_goal = len(w.steps)
        next_goal_ok = w.goal(player) if response_ok else False
        out[arm] = {'incoming_native_success': incoming_ok,
                    'npc_received_X': received_x,
                    'response_native_success': response_ok,
                    'player_received_Y': y_acquired,
                    'response_steps': response,
                    'next_original_goal_witness': w.steps[before_goal:],
                    'next_original_goal_strict_or_acquisition_found': next_goal_ok,
                    'status_after_witness': w.status()}
    return out


def summarize(rows):
    return {'histories': len(rows), 'source_pairs': len({r['case_id'] for r in rows}),
            'source_graphs': len({r['graph_sha256'] for r in rows}),
            'source_episodes': len({(r['model_origin'], r['case_id'], r['source_seed']) for r in rows}),
            'by_source_model': dict(Counter(r['model_origin'] for r in rows)),
            'by_original_npc_index': dict(Counter(str(r['source_role_map']['npc']) for r in rows))}


def summarize_events(rows):
    out=summarize(rows)
    out['events']=out.pop('histories')
    out['episode_role_histories']=len({(r['model_origin'],r['case_id'],r['source_seed'],
                                      r['source_role_map']['npc']) for r in rows})
    return out


def auxiliary_drops(episode, case, npc, model):
    """Trace actual Drop then uninterrupted source-item Get, never infer receipt."""
    player, item = 1-npc, case['goal_bindings'][npc]['item_id']
    records, pending = [], None
    for t in episode['turns']:
        if not good(t) or not t['event_identity'][1] or t['event_identity'][1][0] != item:
            continue
        if t['before'][item]['container'] == t['after'][item]['container']:
            continue
        if t['index'] == player and t['event_type'] == 'DropObjectEvent':
            pending={'model_origin':model,'case_id':case['case_id'],
                'graph_sha256':case['graph_sha256'],'source_seed':episode['seed'],
                'source_role_map':{'npc':npc,'player':player},
                'source_turn':t['turn'],'x_item_id':item,
                'dropped_to':t['after'][item]['container'],'actual_NPC_Get_turn':None}
            records.append(pending)
        else:
            if (pending is not None and t['index']==npc and t['event_type']=='GetObjectEvent'
                    and t['before'][item]['container']==pending['dropped_to']
                    and t['after'][item]['container']==case['actor_ids'][npc]):
                pending['actual_NPC_Get_turn']=t['turn']
            # Other custody-changing actions invalidate attribution to an old
            # player Drop (e.g. NPC Drop and later re-Get of its own item).
            pending=None
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=WB/'results/E85_source_qualification.json')
    ap.add_argument('--cache-out', type=Path, default=CACHE/'runs/e85_partner_performance_source')
    args = ap.parse_args()
    args.cache_out.mkdir(parents=True, exist_ok=True)
    modules = load_event_modules(CACHE/'sources/LIGHT')
    cases = {c['case_id']: c for c in lines(SOURCE)}
    source_hashes = {str(SOURCE): sha(SOURCE), str(Path(__file__).resolve()): sha(__file__)}
    selected, inventory, mechanical, all_give, drops = [], [], [], [], []
    for model in ['gemma', '32b']:
        folder = CACHE/f'runs/e84_{model}_full'
        ep_path, state_path = folder/'episodes.jsonl', folder/'states.jsonl'
        source_hashes.update({str(p):sha(p) for p in [ep_path,state_path,folder/'manifest.json']})
        state_rows = {(r['case_id'],r['seed']):r for r in lines(state_path)}
        for episode in lines(ep_path):
            c = cases[episode['case_id']]
            states = {s['turn']:s for s in state_rows[(c['case_id'],episode['seed'])]['states']}
            assert episode['stop'] == 'turn_limit' and len(episode['turns']) == 32
            for npc in range(2):
                drop_records=auxiliary_drops(episode,c,npc,model)
                drops.extend(drop_records)
                player = 1-npc
                x, y = [c['goal_bindings'][i]['item_id'] for i in [npc,player]]
                trail, picked = [], None
                prior_strict = [False if s else None for s in episode['strict_goal_measurement_supported']]
                prior_ever = list(episode['physical_goal_initial'])
                prior_now = list(prior_ever)
                for t in episode['turns']:
                    if (good(t) and t['index'] == player and t['event_type'] == 'GiveObjectEvent'
                            and t['event_identity'][1] == [x,c['actor_ids'][npc]]):
                        record = {'case_id':c['case_id'],'graph_sha256':c['graph_sha256'],
                                  'model_origin':model,'source_seed':episode['seed'],
                                  'source_turn':t['turn'],'source_role_map':{'npc':npc,'player':player},
                                  'x_item_id':x,'y_item_id':y,
                                  'player_goal_prior_strict':prior_strict[player],
                                  'player_goal_prior_physical_ever':prior_ever[player],
                                  'player_goal_prior_physical_now':prior_now[player],
                                  'npc_Y_directly_held':t['before'].get(y,{}).get('container') == c['actor_ids'][npc]}
                        all_give.append(record)
                        reasons=[]
                        if not record['npc_Y_directly_held']:
                            reasons.append('NPC_not_directly_holding_Y_before_incoming')
                        if prior_strict[player] is None and prior_ever[player] is None:
                            reasons.append('player_authored_atomic_outcome_not_measurable')
                        if prior_ever[player] is None or prior_now[player] is None:
                            reasons.append('player_goal_has_no_defined_literal_physical_outcome')
                        if prior_strict[player] or prior_ever[player]:
                            reasons.append('player_authored_atomic_outcome_already_ever_attained')
                        if not reasons:
                            mechanical.append(dict(record))
                            pre=states[t['turn']-1]
                            assert hashlib.sha256(pre['graph'].encode()).hexdigest() == t['graph_before_sha256']
                            paths=native_paths(c,pre['graph'],npc,t['event_identity'],modules)
                            record['native_paths']=paths
                            if not all(a['response_native_success'] and a['player_received_Y'] for a in paths.values()):
                                reasons.append('Y_response_native_path_not_found_in_both_arms')
                            if not paths['actual_give']['incoming_native_success'] or not paths['actual_give']['npc_received_X']:
                                reasons.append('original_incoming_Give_replay_did_not_receive_X')
                            if not reasons and picked is None:
                                hid=digest({'model':model,'case':c['case_id'],'seed':episode['seed'],
                                            'npc':npc,'cut':t['turn']})[:24]
                                picked={**record,'history_id':hid,'case':c,
                                    'case_ref':{'path':str(SOURCE),'sha256':sha(SOURCE),'case_id':c['case_id']},
                                    'source_episode_path':str(ep_path),
                                    'source_episode_file_sha256':sha(ep_path),
                                    'source_episode_canonical_sha256':digest(episode),
                                    'source_states_path':str(state_path),'source_states_sha256':sha(state_path),
                                    'pre_player_graph_json':pre['graph'],
                                    'pre_player_graph_sha256':t['graph_before_sha256'],
                                    'pre_player_visible':pre['visible'],
                                    'private_headers':[header(c,i) for i in range(2)],
                                    'actual_player_event':{'event_type':t['event_type'],
                                        'target_node_ids':t['event_identity'][1],
                                        'event_identity':t['event_identity'],'command':t['command']},
                                    'source_boundary':{
                                        'agreement_or_fulfilled_contract_not_annotated':True,
                                        'original_goal_not_full_private_motive':True,
                                        'NPC_goal_prior_strict':prior_strict[npc],
                                        'NPC_goal_prior_physical_ever':prior_ever[npc],
                                        'NPC_goal_prior_physical_now':prior_now[npc],
                                        'source_player_goal_verb':c['goal_bindings'][player]['verb'],
                                        'source_NPC_goal_verb':c['goal_bindings'][npc]['verb']}}
                        record['exclusion_reasons']=reasons
                        trail.append(record)
                    prior_strict=t['strict_goal_ever']
                    prior_ever=t['physical_goal_ever']
                    prior_now=t['physical_goal_now']
                if picked is not None:
                    selected.append(picked)
                inventory.append({'model_origin':model,'case_id':c['case_id'],
                    'graph_sha256':c['graph_sha256'],'source_seed':episode['seed'],
                    'source_role_map':{'npc':npc,'player':player},'direct_Give_candidates':trail,
                    'auxiliary_Drop_records':drop_records,
                    'selected_history_id':picked['history_id'] if picked else None,
                    'exclusion_reasons':([] if picked else sorted({q for r in trail for q in r['exclusion_reasons']})
                                         if trail else ['no_original_successful_player_Give_of_NPC_bound_X'])})
    selected.sort(key=lambda r:(r['model_origin'],r['case_id'],r['source_seed'],r['source_role_map']['npc']))
    snapshot_path=args.cache_out/'snapshots.jsonl'
    inv_path=args.cache_out/'all_episode_direction_inventory.jsonl'
    for path,rows in [(snapshot_path,selected),(inv_path,inventory)]:
        path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    report={'experiment':'E85','status':'CPU_SOURCE_QUALIFICATION_COMPLETE','new_model_calls':0,
        'new_cloud_calls':0,'source_scope':{'models':2,'episodes':128,'episode_role_directions':256,
                                        'source_pairs':32,'source_graphs':23},
        'primary_definition':'Earliest qualifying original successful direct Give per source episode and original NPC direction; Y is still directly held by NPC, player literal physical outcome is explicitly False both now and ever (initial true excluded), no prior strict attainment, and Remove/retrieve/Give Y native witness succeeds in both actual-Give and withheld states. Event-only Drop/Remove and unbound outcomes are not unmet material requests. No agreement, welfare or NPC-policy gold.',
        'Drop_scope':'Auxiliary only; no scripted NPC Get is receipt or primary fulfillment.',
        'direct_Give_events':summarize_events(all_give),
        'mechanical_pre_native_events':summarize_events(mechanical),
        'selected_primary':summarize(selected),
        'selected_by_original_npc_index':{str(i):summarize([r for r in selected if r['source_role_map']['npc']==i]) for i in range(2)},
        'selected_histories':[{k:r[k] for k in ['history_id','model_origin','case_id','graph_sha256','source_seed','source_turn','source_role_map','x_item_id','y_item_id','source_boundary']} for r in selected],
        'excluded_episode_directions_by_reason':dict(Counter(q for r in inventory if not r['selected_history_id'] for q in r['exclusion_reasons'])),
        'excluded_episode_directions_total':sum(not r['selected_history_id'] for r in inventory),
        'exclusive_first_exclusion_reason':dict(Counter(r['exclusion_reasons'][0] for r in inventory if not r['selected_history_id'])),
        'exclusion_reason_scope':'The full reasons may overlap; exclusive_first_exclusion_reason partitions the 238 excluded episode-role directions without duplicating them.',
        'auxiliary_Drop_only_not_primary':{
            'all_original_player_Drop_X_events':summarize_events(drops),
            'followed_by_actual_uninterrupted_NPC_Get':summarize_events([r for r in drops if r['actual_NPC_Get_turn'] is not None]),
            'without_actual_uninterrupted_NPC_Get':summarize_events([r for r in drops if r['actual_NPC_Get_turn'] is None]),
            'interpretation':'Actual source events only; Drop is floor availability, not NPC receipt. No scripted NPC Get and no contribution to primary N.'},
        'purpose_and_measurement_boundaries':{
            'NPC_prior_physical_ever_true_histories':sum(r['source_boundary']['NPC_goal_prior_physical_ever'] is True for r in selected),
            'NPC_prior_physical_now_true_histories':sum(r['source_boundary']['NPC_goal_prior_physical_now'] is True for r in selected),
            'player_original_goal_verbs':dict(Counter(r['case']['goal_bindings'][r['source_role_map']['player']]['verb'] for r in selected)),
            'Y_response_does_not_immediately_realize_player_goal_histories':[
                {'history_id':r['history_id'],'case_id':r['case_id'],'model_origin':r['model_origin'],
                 'source_seed':r['source_seed']} for r in selected
                if not r['native_paths']['actual_give']['next_original_goal_strict_or_acquisition_found']],
            'interpretation':'All 18 permit NPC Give Y in both physical branches. In the three 649ee Put-fruit histories, the pouch target is X now held by NPC after real Give, so a Y transfer alone is not the original Put completion. This is retained as a real remaining coordination issue, not filtered or called irrational. Three NPC source goals were already physically attained historically; receipt is not always new quest progress.'},
        'all_source_pairs':[{ 'case_id':cid,'graph_sha256':c['graph_sha256'],
            'selected_history_count':sum(r['case_id']==cid for r in selected)} for cid,c in sorted(cases.items())],
        'snapshots':{'path':str(snapshot_path),'sha256':sha(snapshot_path)},
        'full_inventory':{'path':str(inv_path),'sha256':sha(inv_path)},
        'source_sha256':source_hashes,'rebuild':{'script':str(Path(__file__).resolve()),
            'command':'env PYTHONHASHSEED=0 PYTHONPATH=/home/xiang/.cache/game-npc-research/deps OPENBLAS_NUM_THREADS=1 /home/xiang/miniconda3/envs/fgvd/bin/python '+str(Path(__file__).resolve())}}
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['selected_primary','selected_by_original_npc_index','excluded_episode_directions_by_reason','snapshots']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
