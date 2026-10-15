#!/usr/bin/env python3
"""E70 full native source pool: authored Give, third party, paired equip state."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import tarfile
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, actor_for, execute


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def native(graph, actor_id, command, modules):
    result = execute(ViewerHost(graph), graph.get_node(actor_id), command, *modules[1:])
    assert result['legal'] and result.get('executed') and not result.get('stochastic_failure')
    return {k: result.get(k) for k in ['command', 'legal', 'executed', 'stochastic_failure']}


def qualify(quest, filename, modules):
    graph = modules[0].from_json(quest['graph'])
    try:
        actor = actor_for(graph, quest['character'])
    except AssertionError:
        return None, 'ambiguous_actor'
    if actor.get_prop('dead'):
        return None, 'dead_actor'
    actor_id = actor.node_id
    goal = parse_event(graph, actor, quest['goal'].strip().lower(), *modules[1:])
    origin_equipped = False
    ready_setup = []
    if isinstance(goal, modules[2]):
        # Some authored Give goals naturally start with their item equipped.
        recovered = None
        for event in sorted(modules[1].RemoveObjectEvent.get_valid_actions(graph, actor),
                            key=lambda e: e.target_nodes[0].node_id):
            fork = modules[0].from_json(quest['graph'])
            witness = native(fork, actor_id, event.to_canonical_form(), modules)
            candidate = parse_event(fork, fork.get_node(actor_id), quest['goal'].strip().lower(), *modules[1:])
            if (not isinstance(candidate, modules[2]) and type(candidate).__name__ == 'GiveObjectEvent'
                    and candidate.target_nodes[0].node_id == event.target_nodes[0].node_id):
                recovered = fork, candidate, witness
                break
        if recovered is None:
            return None, 'goal_not_ready_after_one_native_remove'
        graph, goal, witness = recovered
        ready_setup = [witness]
        origin_equipped = True
    if type(goal).__name__ != 'GiveObjectEvent':
        return None, 'goal_not_give_event'
    item, recipient = goal.target_nodes
    if recipient.get_prop('dead'):
        return None, 'dead_goal_recipient'
    others = sorted([e for e in modules[1].GiveObjectEvent.get_valid_actions(graph, graph.get_node(actor_id))
                     if e.target_nodes[0].node_id == item.node_id
                     and e.target_nodes[1].node_id not in [recipient.node_id, actor_id]
                     and not e.target_nodes[1].get_prop('dead')],
                    key=lambda e: e.target_nodes[1].node_id)
    if not others:
        return None, 'no_other_living_recipient'
    other = others[0].target_nodes[1]
    ready_json = graph.to_json()
    equipped_setup = []
    if origin_equipped:
        equipped = modules[0].from_json(quest['graph'])
    else:
        equipped = None
        equip_options = []
        for cls in [modules[1].WearEvent, modules[1].WieldEvent]:
            equip_options += [e for e in cls.get_valid_actions(graph, graph.get_node(actor_id))
                              if e.target_nodes[0].node_id == item.node_id]
        for event in equip_options:
            fork = modules[0].from_json(ready_json)
            result = execute(ViewerHost(fork), fork.get_node(actor_id), event.to_canonical_form(), *modules[1:])
            if result['legal'] and result.get('executed') and fork.get_node(item.node_id).get_prop('equipped'):
                equipped = fork
                equipped_setup = [{k: result.get(k) for k in ['command', 'legal', 'executed', 'stochastic_failure']}]
                break
        if equipped is None:
            return None, 'no_legal_same_item_equip'
    removes = [e for e in modules[1].RemoveObjectEvent.get_valid_actions(equipped, equipped.get_node(actor_id))
               if e.target_nodes[0].node_id == item.node_id]
    if not removes:
        return None, 'no_native_remove'
    remove = removes[0].to_canonical_form()
    goal_command = goal.to_canonical_form()
    requests = {}
    for direction, target_id in [('aligned', recipient.node_id), ('divert', other.node_id)]:
        event = next(e for e in modules[1].GiveObjectEvent.get_valid_actions(graph, graph.get_node(actor_id))
                     if [n.node_id for n in e.target_nodes] == [item.node_id, target_id])
        target = graph.get_node(target_id)
        requests[direction] = {'requester_id': target_id, 'requester_name': target.name,
                               'requester_persona': target.get_prop('persona'),
                               'request_command': event.to_canonical_form(),
                               'request_text': 'Could you give me '+item.get_prefix_view()+'?'}
    states = {'ready': ready_json, 'equipped': equipped.to_json()}
    witnesses = []
    for label, state in states.items():
        for direction, request in requests.items():
            fork = modules[0].from_json(state)
            parsed = parse_event(fork, fork.get_node(actor_id), request['request_command'], *modules[1:])
            if label == 'equipped' and not isinstance(parsed, modules[2]):
                return None, 'equipped_command_rebinds_to_alternative'
            if label == 'ready' and (isinstance(parsed, modules[2]) or
                    [n.node_id for n in parsed.target_nodes] != [item.node_id, request['requester_id']]):
                return None, 'ready_command_not_unique_target'

            actions = ([] if label == 'ready' else [remove])+[request['request_command']]
            events = [native(fork, actor_id, command, modules) for command in actions]
            if fork.get_node(item.node_id).get_container().node_id != request['requester_id']:
                return None, 'path_not_bound_item_transfer'
            witnesses.append({'state': label, 'direction': direction, 'events': events,
                              'final_item_container': request['requester_id']})
    source_sha = sha(quest['graph'])
    case = {'quest_file': filename, 'graph_sha256': source_sha, 'case_id': source_sha[:16],
            'quest': copy.deepcopy(quest), 'goal_kind': 'give', 'goal_command': goal_command,
            'actor_id': actor_id, 'item_id': item.node_id, 'original_recipient': recipient.node_id}
    return {'case': case, 'requests': requests, 'competitor_id': other.node_id,
            'states': states, 'state_sha256': {key: sha(value) for key, value in states.items()},
            'source_initially_equipped': origin_equipped,
            'setup_from_source': {'ready': ready_setup, 'equipped': equipped_setup},
            'remove_command': remove, 'native_witnesses': witnesses,
            'state_scope': 'Legal Equip/Remove also updates native equipment stats; rules and source goals unchanged.'}, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    args = ap.parse_args()
    modules = load_event_modules(CACHE/'sources/LIGHT')
    counts = Counter()
    candidates = []
    source = CACHE/'quest_stems.tar.gz'
    with tarfile.open(source, 'r|gz') as archive:
        for member in archive:
            if not member.name.endswith('.json'):
                continue
            quest = json.load(archive.extractfile(member))['data']
            counts['source_quests'] += 1
            if quest['goal'].split()[0].lower() != 'give':
                continue
            counts['give_quests'] += 1
            row, reason = qualify(quest, member.name.split('/')[-1], modules)
            counts[reason or 'qualified_quests'] += 1
            if row:
                candidates.append(row)
    unique = {}
    for row in sorted(candidates, key=lambda r: int(r['case']['quest_file'].split('.')[0])):
        unique.setdefault(row['case']['graph_sha256'], row)
    rows = sorted(unique.values(), key=lambda r: sha('e70-fixed-pool:'+r['case']['graph_sha256']))
    prior_path = CACHE/'runs/e50_native_snapshots_v1/snapshots.jsonl'
    prior = {r['graph_sha256'] for r in map(json.loads, prior_path.open())}
    for row in rows:
        row['source_pool'] = 'prior_E50_pool' if row['case']['graph_sha256'] in prior else 'outside_prior_E50_pool'
    args.out.mkdir(parents=True, exist_ok=False)
    dataset = args.out/'snapshots.jsonl'
    dataset.write_text(''.join(json.dumps(row, ensure_ascii=False)+'\n' for row in rows))
    report = {'status': 'COMPLETE', 'counts': dict(counts), 'independent_source_graphs': len(rows),
              'source_pool': dict(Counter(row['source_pool'] for row in rows)),
              'source_initial_equipment': dict(Counter(str(row['source_initially_equipped']) for row in rows)),
              'native_path_witnesses': sum(len(row['native_witnesses']) for row in rows),
              'data': str(dataset), 'data_sha256': sha(dataset.read_text()),
              'archive_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'model_calls': 0, 'gpu_hours': 0, 'rules_modified': False,
              'scope': 'All eligible authored Give graphs; request/state interventions are explicit. Source-pool novelty is not proof of no prior model exposure.'}
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
