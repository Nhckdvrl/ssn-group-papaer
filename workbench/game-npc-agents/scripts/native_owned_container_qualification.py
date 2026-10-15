#!/usr/bin/env python3
"""E75: preserve authored tasks and ultimate ownership, vary a native Get prerequisite."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import tarfile

from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, actor_for, execute


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_id(event, modules):
    if isinstance(event, modules[2]):
        return None
    return type(event).__name__, tuple(n.node_id for n in event.target_nodes)


def stats(graph, actor_id):
    row = json.loads(graph.to_json())['nodes'][actor_id]
    return {k: row.get(k) for k in ['health', 'food_energy', 'energy', 'attack', 'defense',
                                   'dexterity', 'strength', 'damage', 'dead', 'speed', 'aggression']}


def ultimate_owner(item):
    seen = set()
    while item is not None and not item.agent and not item.room:
        assert item.node_id not in seen
        seen.add(item.node_id)
        item = item.get_container()
    return item.node_id if item is not None else None


def run(graph, actor_id, command, modules):
    actor = graph.get_node(actor_id)
    parsed = parse_event(graph, actor, command, *modules[1:])
    ident = event_id(parsed, modules)
    result = execute(ViewerHost(graph), actor, command, *modules[1:])
    result['target_node_ids'] = list(ident[1]) if ident else []
    return result


def success(row):
    return row['legal'] and row.get('executed') and not row.get('stochastic_failure')


def qualify(case, modules):
    g = modules[0].from_json(case['quest']['graph'])
    aid, iid = case['actor_id'], case['item_id']
    actor, item = g.get_node(aid), g.get_node(iid)
    if actor.get_prop('dead') or g.get_node(case['requester_id']).get_prop('dead'):
        return None, 'dead_actor_or_requester'
    if item.get_container().node_id != aid or item.get_prop('equipped'):
        return None, 'source_item_not_directly_carried_unequipped'
    goal = parse_event(g, actor, case['goal_command'], *modules[1:])
    request = parse_event(g, actor, case['request_command'], *modules[1:])
    goal_id, request_id = event_id(goal, modules), event_id(request, modules)
    if not goal_id or not request_id or goal_id[1][0] != iid or request_id[1][0] != iid:
        return None, 'source_use_not_exact_item'
    candidates = [e for e in modules[1].PutObjectInEvent.get_valid_actions(g, actor)
                  if e.target_nodes[0].node_id == iid and e.target_nodes[1].node_id != iid
                  and e.target_nodes[1].object and e.target_nodes[1].get_container().node_id == aid]
    if not candidates:
        return None, 'no_native_owned_container_put_candidate'
    failures = Counter()
    original_stats = stats(g, aid)
    for put in sorted(candidates, key=lambda e: e.target_nodes[1].node_id):
        stored = modules[0].from_json(case['quest']['graph'])
        result = run(stored, aid, put.to_canonical_form(), modules)
        if not success(result):
            failures['put_rejected'] += 1
            continue
        bag_id = put.target_nodes[1].node_id
        obj = stored.get_node(iid)
        if obj.get_container().node_id != bag_id or ultimate_owner(obj) != aid:
            failures['ownership_not_preserved'] += 1
            continue
        if stats(stored, aid) != original_stats or obj.get_prop('equipped'):
            failures['physical_stats_or_equipment_changed'] += 1
            continue
        if any(event_id(parse_event(stored, stored.get_node(aid), command, *modules[1:]), modules)
               for command in [case['goal_command'], case['request_command']]):
            failures['direct_use_still_legal_or_rebinds'] += 1
            continue
        retrieves = [e for e in modules[1].GetObjectEvent.get_valid_actions(stored, stored.get_node(aid))
                     if [n.node_id for n in e.target_nodes] == [iid, bag_id]]
        if not retrieves:
            failures['no_native_get'] += 1
            continue
        retrieve = min(e.to_canonical_form() for e in retrieves)
        witnesses = {}
        for state_name, state in [('ready', case['quest']['graph']), ('stored', stored.to_json())]:
            for target, command, expected in [('goal', case['goal_command'], goal_id),
                                               ('request', case['request_command'], request_id)]:
                fork = modules[0].from_json(state)
                records = []
                if state_name == 'stored':
                    records.append(run(fork, aid, retrieve, modules))
                    assert success(records[-1]) and fork.get_node(iid).get_container().node_id == aid
                    assert stats(fork, aid) == original_stats
                parsed = parse_event(fork, fork.get_node(aid), command, *modules[1:])
                assert event_id(parsed, modules) == expected
                records.append(run(fork, aid, command, modules))
                assert success(records[-1])
                if target == 'request':
                    assert fork.get_node(iid).get_container().node_id == case['requester_id']
                witnesses[state_name+'/'+target] = records
        return {'case': copy.deepcopy(case), 'states': {'ready': case['quest']['graph'], 'stored': stored.to_json()},
                'container_id': bag_id, 'container_name': put.target_nodes[1].get_prefix_view(),
                'retrieve_command': retrieve, 'setup_event': result, 'native_witnesses': witnesses,
                'native_goal_identity': [goal_id[0], list(goal_id[1])],
                'native_request_identity': [request_id[0], list(request_id[1])],
                'source_actor_physical_stats': original_stats,
                'ultimate_source_item_owner_in_both_states': aid,
                'qualification_container_attempts': dict(failures)}, None
    return None, 'owned_container_candidates_failed:'+json.dumps(dict(failures), sort_keys=True)


def retrieval_case(quest, filename, modules):
    source = modules[0].from_json(quest['graph'])
    try:
        actor = actor_for(source, quest['character'])
    except AssertionError:
        return None, 'ambiguous_actor'
    aid = actor.node_id
    if actor.get_prop('dead'):
        return None, 'dead_actor'
    goal_text = quest['goal'].strip().lower()
    if event_id(parse_event(source, actor, goal_text, *modules[1:]), modules):
        return None, 'original_goal_already_executable'
    failures = Counter()
    for candidate in sorted(modules[1].GetObjectEvent.get_valid_actions(source, actor),
                            key=lambda e: tuple(n.node_id for n in e.target_nodes)):
        ready = modules[0].from_json(quest['graph'])
        get_command = candidate.to_canonical_form()
        setup = run(ready, aid, get_command, modules)
        expected_get = [n.node_id for n in candidate.target_nodes]
        if not success(setup) or setup['target_node_ids'] != expected_get:
            failures['get_rejected_or_rebound'] += 1
            continue
        iid = candidate.target_nodes[0].node_id
        goal = parse_event(ready, ready.get_node(aid), goal_text, *modules[1:])
        gid = event_id(goal, modules)
        if not gid or gid[1][0] != iid:
            failures['goal_not_enabled_for_retrieved_item'] += 1
            continue
        if stats(ready, aid) != stats(source, aid) or ready.get_node(iid).get_prop('equipped'):
            failures['get_changes_actor_stats_or_equipment'] += 1
            continue
        original_recipient = gid[1][1] if gid[0] == 'GiveObjectEvent' else None
        gives = [e for e in modules[1].GiveObjectEvent.get_valid_actions(ready, ready.get_node(aid))
                 if e.target_nodes[0].node_id == iid and e.target_nodes[1].node_id not in [aid, original_recipient]
                 and not e.target_nodes[1].get_prop('dead')]
        if not gives:
            failures['no_other_living_requester'] += 1
            continue
        req = min(gives, key=lambda e: e.target_nodes[1].node_id)
        request_command = req.to_canonical_form()
        if event_id(parse_event(source, actor, request_command, *modules[1:]), modules):
            failures['initial_request_legal_or_rebinds'] += 1
            continue
        goal_command = goal.to_canonical_form()
        witnesses = {}; witness_failure = None
        for state_name, state in [('ready', ready.to_json()), ('retrieval', quest['graph'])]:
            for target, command, expected in [('goal', goal_command, gid),
                                               ('request', request_command, event_id(req, modules))]:
                fork = modules[0].from_json(state); records = []
                if state_name == 'retrieval':
                    records.append(run(fork, aid, get_command, modules))
                    if (not success(records[-1]) or records[-1]['target_node_ids'] != expected_get
                            or fork.get_node(iid).get_container().node_id != aid):
                        witness_failure = 'get_witness_failed_or_rebound'
                        break
                if event_id(parse_event(fork, fork.get_node(aid), command, *modules[1:]), modules) != expected:
                    witness_failure = 'goal_request_witness_rebound'
                    break
                records.append(run(fork, aid, command, modules))
                if not success(records[-1]):
                    witness_failure = 'goal_request_execution_failed'
                    break
                if target == 'request' and fork.get_node(iid).get_container().node_id != req.target_nodes[1].node_id:
                    witness_failure = 'request_wrong_final_owner'
                    break
                witnesses[state_name+'/'+target] = records
            if witness_failure:
                break
        if witness_failure:
            failures[witness_failure] += 1
            continue
        graph_sha = hashlib.sha256(quest['graph'].encode()).hexdigest()
        peer = req.target_nodes[1]; item = ready.get_node(iid)
        case = {'quest_file': filename, 'quest': copy.deepcopy(quest), 'graph_sha256': graph_sha,
                'case_id': graph_sha[:16], 'actor_id': aid, 'item_id': iid,
                'goal_kind': goal_text.split()[0], 'goal_command': goal_command,
                'original_recipient': original_recipient,
                'requester_id': peer.node_id, 'requester_name': peer.name,
                'requester_persona': peer.get_prop('persona'), 'request_command': request_command,
                'request_text': 'Could you give me '+item.get_prefix_view()+'?'}
        return {'case':case, 'states':{'ready':ready.to_json(),'retrieval':quest['graph']},
                'retrieve_command':get_command, 'source_container_id':candidate.target_nodes[1].node_id,
                'source_container_name':candidate.target_nodes[1].get_prefix_view(),
                'setup_event':setup, 'native_witnesses':witnesses,
                'native_goal_identity':[gid[0],list(gid[1])],
                'native_request_identity':[type(req).__name__,[n.node_id for n in req.target_nodes]],
                'source_actor_physical_stats':stats(source,aid),
                'qualification_get_attempts':dict(failures)}, None
    return None, 'no_one_get_goal_and_request_path:'+json.dumps(dict(failures), sort_keys=True)


def build_retrieval(args, modules):
    archive = CACHE/'quest_stems.tar.gz'
    candidates, failures, counts = [], [], Counter()
    with tarfile.open(archive, 'r|gz') as handle:
        for member in handle:
            if not member.name.endswith('.json'):
                continue
            quest = json.load(handle.extractfile(member))['data']
            kind = quest['goal'].strip().lower().split()[0]
            if kind not in ['give','wear','wield','eat','drink']:
                continue
            counts[kind+'/source_quests'] += 1
            row, reason = retrieval_case(quest, member.name.split('/')[-1], modules)
            if row:
                candidates.append(row)
                counts[kind+'/eligible_quests'] += 1
            else:
                failures.append({'quest_file':member.name,'goal_kind':kind,'reason':reason})
    unique = {}
    for row in sorted(candidates, key=lambda r:int(r['case']['quest_file'].split('.')[0])):
        unique.setdefault(row['case']['graph_sha256'],row)
    rows = sorted(unique.values(), key=lambda r:hashlib.sha256(('e75-native-get:'+r['case']['graph_sha256']).encode()).hexdigest())
    prior = {r['graph_sha256'] for r in map(json.loads,args.data.open())}
    for row in rows:
        row['in_prior_E50_pool'] = row['case']['graph_sha256'] in prior
    args.out.mkdir(parents=True,exist_ok=False); path=args.out/'snapshots.jsonl'
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    raw_failures = args.out/'qualification_failures.json'
    raw_failures.write_text(json.dumps(failures,ensure_ascii=False,indent=2)+'\n')
    report = {'status':'COMPLETE','counts':dict(counts),'qualified_worlds':len(rows),
              'qualified_goal_counts':dict(Counter(r['case']['goal_kind'] for r in rows)),
              'source_prior_overlap':dict(Counter(str(r['in_prior_E50_pool']) for r in rows)),
              'failure_counts':dict(Counter(r['reason'].split(':')[0] for r in failures)),
              'failures':str(raw_failures),'failures_sha256':digest(raw_failures),
              'data':str(path),'data_sha256':digest(path),'native_path_witnesses':len(rows)*4,
              'archive_sha256':digest(archive),'script_sha256':digest(Path(__file__)),
              'model_calls':0,'gpu_hours':0,'rules_modified':False,
              'scope':['Retrieval is the original authored initial state; ready is produced by one legal native Get.',
                       'Source task and motivations unchanged; resource custody, menus and sequence length vary.',
                       'Prior E50 overlap alone is not a complete prior-model-exposure audit.']}
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--retrieval', action='store_true')
    args = ap.parse_args()
    cases = list(map(json.loads, args.data.open()))
    assert len(cases) == len({c['graph_sha256'] for c in cases}) == 360
    modules = load_event_modules(CACHE/'sources/LIGHT')
    if args.retrieval:
        build_retrieval(args, modules)
        return
    rows, exclusions, counts = [], [], Counter()
    for case in cases:
        row, reason = qualify(case, modules)
        counts[case['goal_kind']+'/source'] += 1
        if row:
            rows.append(row)
            counts[case['goal_kind']+'/qualified'] += 1
        else:
            exclusions.append({'case_id': case['case_id'], 'goal_kind': case['goal_kind'], 'reason': reason})
    args.out.mkdir(parents=True, exist_ok=False)
    path = args.out/'snapshots.jsonl'
    path.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
    report = {'status':'COMPLETE', 'source_worlds':len(cases), 'qualified_worlds':len(rows),
              'counts':dict(counts), 'exclusions':exclusions,
              'source_split_counts':dict(Counter(r['case']['split'] for r in rows)),
              'native_path_witnesses':len(rows)*4, 'data':str(path), 'data_sha256':digest(path),
              'source_data_sha256':digest(args.data), 'script_sha256':digest(Path(__file__)),
              'model_calls':0, 'gpu_hours':0, 'rules_modified':False,
              'scope':['All native-eligible graphs retained; no behavioral selection.',
                       'Stored state is a legal counterfactual with the original ultimate owner; not an authored initial state.',
                       'Same previously exposed source pool; no heldout claim.']}
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'exclusions'}))


if __name__ == '__main__':
    main()
