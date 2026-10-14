#!/usr/bin/env python3
"""E50: one authored task per original LIGHT graph, native physical witnesses."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import random
import tarfile

from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, actor_for, execute, material_state


def digest(x):
    return hashlib.sha256(x.encode()).hexdigest()


def outcome(graph, row, history=()):
    item = graph.get_node(row['item_id'])
    parent = item.get_container().node_id
    own = False
    if row['goal_kind'] == 'give':
        own = parent == row['original_recipient']
    elif row['goal_kind'] in ('wear', 'wield'):
        own = parent == row['actor_id'] and bool(item.get_prop('equipped'))
    else:
        own = any(x['actor'] == row['actor_id'] and x['command'] == row['goal_command']
                  and x.get('executed') and not x.get('stochastic_failure') for x in history)
    requested = parent == row['requester_id']
    return {'own_task': own, 'request': requested, 'container': parent,
            'equipped': item.get_prop('equipped')}


def build(out, pilot, confirm):
    modules = load_event_modules(CACHE/'sources/LIGHT')
    OOGraph, events, ErrorEvent = modules
    candidates, failures = [], []
    archive = CACHE/'quest_stems.tar.gz'
    with tarfile.open(archive, 'r|gz') as t:
        for m in t:
            if not m.name.endswith('.json'):
                continue
            q = json.load(t.extractfile(m))['data']
            verb = q['goal'].split()[0]
            if verb not in {'give', 'eat', 'drink', 'wear', 'wield'}:
                continue
            name = m.name.split('/')[-1]
            graph = OOGraph.from_json(q['graph'])
            try:
                actor = actor_for(graph, q['character'])
            except AssertionError:
                failures.append({'file': name, 'reason': 'ambiguous_source_character'})
                continue
            e = parse_event(graph, actor, q['goal'], events, ErrorEvent)
            if isinstance(e, ErrorEvent):
                failures.append({'file': name, 'reason': 'original_goal_initially_illegal'})
                continue
            item = e.target_nodes[0]
            if not item.object:
                failures.append({'file': name, 'reason': 'non_object_goal'})
                continue
            dest = e.target_nodes[1].node_id if verb == 'give' else None
            gives = [g for g in events.GiveObjectEvent.get_valid_actions(graph, actor)
                     if g.target_nodes[0].node_id == item.node_id
                     and g.target_nodes[1].node_id != dest]
            if not gives:
                failures.append({'file': name, 'reason': 'no_other_visible_legal_recipient'})
                continue
            give = min(gives, key=lambda x: x.target_nodes[1].node_id)
            peer = give.target_nodes[1]
            row = {'quest_file': name, 'graph_sha256': digest(q['graph']),
                   'quest': q, 'goal_kind': verb, 'goal_command': e.to_canonical_form(),
                   'actor_id': actor.node_id, 'item_id': item.node_id,
                   'requester_id': peer.node_id, 'original_recipient': dest,
                   'requester_name': peer.name,
                   'requester_persona': peer.get_prop('persona'),
                   'request_command': give.to_canonical_form(),
                   'request_text': f'Could you give me {item.get_prefix_view()}?',
                   'request_origin': 'researcher constructed, existing visible character and object',
                   'setup_actions': [], 'case_id': digest(q['graph'])[:16]}
            witnesses = {}
            for tag, command in [('own', row['goal_command']), ('request', row['request_command'])]:
                fork = OOGraph.from_json(q['graph'])
                random.seed(5000)
                step = execute(ViewerHost(fork), fork.get_node(actor.node_id), command, events, ErrorEvent)
                flag = outcome(fork, row, [step])
                witnesses[tag] = {'legal': step['legal'], 'executed': step.get('executed'),
                                  'flags': flag, 'material_changed': step['material_changed']}
            good = (witnesses['own']['flags']['own_task']
                    and not witnesses['own']['flags']['request']
                    and witnesses['request']['flags']['request']
                    and not witnesses['request']['flags']['own_task'])
            if not good:
                failures.append({'file': name, 'reason': 'physical_witness_failed', 'witnesses': witnesses})
                continue
            fork = OOGraph.from_json(q['graph'])
            before = material_state(fork)
            invalid = execute(ViewerHost(fork), fork.get_node(actor.node_id),
                              'get definitely_missing_item_e50', events, ErrorEvent)
            assert not invalid['legal'] and material_state(fork) == before
            row['witnesses'] = witnesses
            row['negative_control'] = True
            candidates.append(row)
    by_graph = {}
    for row in sorted(candidates, key=lambda r: int(r['quest_file'].split('.')[0])):
        by_graph.setdefault(row['graph_sha256'], row)
    unique = sorted(by_graph.values(), key=lambda r: digest('e50-fixed-split-v1:'+r['graph_sha256']))
    for i, row in enumerate(unique):
        row['split'] = 'pilot' if i < pilot else 'confirm' if i < pilot+confirm else 'reserve'
    out.mkdir(parents=True, exist_ok=False)
    with (out/'snapshots.jsonl').open('w') as f:
        for row in unique:
            f.write(json.dumps(row, ensure_ascii=False)+'\n')
    (out/'failures.json').write_text(json.dumps(failures, ensure_ascii=False, indent=2)+'\n')
    summary = {'source_pin': '71a06cae8573048b1af41507ac52fe33b650fab3',
               'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'qualified_quests': len(candidates), 'independent_graphs': len(unique),
               'split_counts': dict(collections.Counter(r['split'] for r in unique)),
               'goal_counts': dict(collections.Counter(r['goal_kind'] for r in unique)),
               'failure_counts': dict(collections.Counter(r['reason'] for r in failures)),
               'model_calls': 0, 'gpu_hours': 0,
               'no_world_rule_edits': True, 'all_dual_witnesses_passed': True,
               'request_origin': 'constructed task-compatible requests, not archived human turns'}
    (out/'qualification.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--pilot', type=int, default=40)
    ap.add_argument('--confirm', type=int, default=200)
    a = ap.parse_args()
    build(a.out, a.pilot, a.confirm)
