#!/usr/bin/env python3
"""E71 authored goal with no solicitation/dialogue; same native E70 states."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time
from native_rule_execution import configure, SharedPrefixClient, policy
from light_native_gate import parse_event
from light_npc_episodes import ViewerHost, execute, chosen_command
from native_request_precondition_execution import SEEDS


def spec(game, graph, history, modules):
    c = game['case']; actor = graph.get_node(c['actor_id'])
    view = policy.base.observation(ViewerHost(graph), actor, *modules[1:])
    menu = policy.base.legal_commands(graph, actor)
    text = view+'\nOriginal authored task: '+c['goal_command']+'\nCurrent agenda: '+c['goal_command']
    if history:
        text += '\nRecent actions: '+json.dumps([h['command'] for h in history])
    text += '\nChoose your next legal game action.\n'+'\n'.join(menu)
    text += '\nActual episode facts: No transfer of the selected item has yet executed.'
    if history:
        blocked = actor.get_blocking()
        if blocked is not None:
            text += '\nStatus: You are already blocking '+blocked.get_prefix_view()+'.'
        if history[-1].get('error'):
            text += '\nLast native action result: '+history[-1]['error']
    schema = policy.base.schema({'action': {'type': 'string', 'enum': menu+['say']},
                                 'utterance': {'type': 'string'}, 'reason': {'type': 'string'}})
    return policy.base.pack_messages(c, game['persona'], text), schema


def games_for(rows, modules):
    games = []
    for row in rows:
        for state in ['ready', 'equipped']:
            c = {**row['case'], 'quest': {**row['case']['quest'], 'graph': row['states'][state]}}
            for seed in SEEDS:
                for p in ['firm', 'agreeable']:
                    games.append({'case': c, 'persona': p, 'seed': seed, 'state': state,
                                  'condition': state+'_unsolicited', 'direction': 'unsolicited',
                                  'control': 'none', 'interface': 'direct', 'conversation': None,
                                  'competitor_id': row['competitor_id'],
                                  'sampling_seed': seed+int(c['case_id'][:7], 16)*10,
                                  'graph': modules[0].from_json(c['quest']['graph']),
                                  'history': [], 'first_recipient': None,
                                  'native_goal_text_executed': False, 'protocol_error': None, 'done': False})
    return games


def run_group(rows, client, modules, out):
    games = games_for(rows, modules)
    for step in range(8):
        active = [g for g in games if not g['done']]
        if not active:
            break
        jobs = [policy.base.job(g['case'], g['persona'], 'exec', spec(g, g['graph'], g['history'], modules),
                                g['sampling_seed']+10+step, None, step) for g in active]
        for g, response in zip(active, client.batch(jobs)):
            if response is None:
                g['done'], g['protocol_error'] = True, 'invalid_exec_json'; continue
            c = g['case']; actor = g['graph'].get_node(c['actor_id']); command = chosen_command(response)
            event = parse_event(g['graph'], actor, command, *modules[1:])
            goal = parse_event(g['graph'], actor, c['goal_command'], *modules[1:])
            ids = [] if isinstance(event, modules[2]) else [n.node_id for n in event.target_nodes]
            is_goal = (not isinstance(event, modules[2]) and not isinstance(goal, modules[2])
                       and event.to_canonical_form() == goal.to_canonical_form())
            random.seed(g['sampling_seed']+100+step)
            result = execute(ViewerHost(g['graph']), actor, command, *modules[1:])
            success = result['legal'] and result.get('executed') and not result.get('stochastic_failure')
            source_give = success and result['event_type'] == 'GiveObjectEvent' and ids[0] == c['item_id']
            if success and is_goal:
                g['native_goal_text_executed'] = True
            if source_give:
                assert result['before'][c['item_id']]['container'] == c['actor_id']
                assert result['after'][c['item_id']]['container'] == ids[1]
                g['first_recipient'], g['done'] = ids[1], True
            result.update(step=step, choice=response, target_node_ids=ids, source_item_give=bool(source_give),
                          matches_current_goal_text=bool(is_goal))
            g['history'].append(result)
            if actor.get_prop('dead'):
                g['done'] = True
    with (out/'episodes.jsonl').open('a') as handle:
        for g in games:
            c = g['case']; item = g['graph'].get_node(c['item_id'])
            row = {k: v for k, v in g.items() if k not in ['case', 'graph', 'sampling_seed', 'done']}
            row.update(case_id=c['case_id'], source_graph_sha256=c['graph_sha256'],
                       goal_item_id=c['item_id'], actor_id=c['actor_id'], goal_recipient_id=c['original_recipient'],
                       requester_id=None, goal_command=c['goal_command'], request_command=None,
                       minimum_source_transfer_steps=1 if g['state'] == 'ready' else 2,
                       final_item_container=item.get_container().node_id, final_item_equipped=item.get_prop('equipped'))
            handle.write(json.dumps(row, ensure_ascii=False)+'\n')
    return len(games)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--model', type=Path)
    ap.add_argument('--data', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--cpu-check', action='store_true'); args = ap.parse_args(); configure()
    rows = list(map(json.loads, args.data.open())); assert len(rows) == 117
    modules = policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    if args.cpu_check:
        count = 0
        for row in rows:
            # Rendering has no dependence on seed; check all distinct state/persona inputs once.
            for g in [g for g in games_for([row], modules) if g['seed'] == SEEDS[0]]:
                messages, schema = spec(g, g['graph'], [], modules)
                assert policy.TRAITS[g['persona']] in messages[0]['content']
                assert g['case']['goal_command'] in messages[-1]['content']
                assert 'Recent request from' not in messages[-1]['content'] and 'Full recent conversation' not in messages[-1]['content']
                count += 1
        result = {'status': 'PASS', 'distinct_input_checks': count, 'worlds': 117, 'model_calls': 0}
        args.out.write_text(json.dumps(result, indent=2)+'\n'); print(result); return
    assert args.model; args.out.mkdir(parents=True, exist_ok=False)
    manifest = {'experiment': 'E71', 'model': str(args.model), 'seeds': SEEDS, 'worlds': 117,
                'source_data_sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'termination': 'First executed exact-source-item Give, death, protocol failure, or eight actions.',
                'dialogue': 'No external solicitation or generated conversation/update.',
                'rules_modified': False, 'new_cloud_calls': 0}
    (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    client = SharedPrefixClient(args.model, args.out, 7001); start = time.monotonic(); count = 0
    for group in [rows[:1]]+[rows[i:i+8] for i in range(1, len(rows), 8)]:
        count += run_group(group, client, modules, args.out)
        print(json.dumps({'episodes': count, 'calls': client.inner.calls, 'wall_seconds': time.monotonic()-start}), flush=True)
    assert count == 1404
    runtime = {'episodes': count, 'calls': client.inner.calls, 'reused_calls': client.reused,
               'wall_seconds': time.monotonic()-start, 'model_load_seconds': client.inner.load_seconds, 'new_cloud_calls': 0}
    (args.out/'runtime.json').write_text(json.dumps(runtime, indent=2)+'\n'); print(json.dumps(runtime), flush=True)


if __name__ == '__main__':
    main()
