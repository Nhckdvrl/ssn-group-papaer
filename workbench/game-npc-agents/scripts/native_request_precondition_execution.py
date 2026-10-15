#!/usr/bin/env python3
"""E70 native goal/request alignment and legal preconditions, fixed nine cells."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import time
from native_rule_execution import configure, SharedPrefixClient, policy
from light_native_gate import parse_event
from light_npc_episodes import ViewerHost, execute, chosen_command

MECHANICS = ('Equipped items remain in your inventory. To give an equipped item, first use its legal remove command '
             'to unequip it; then use give. Removing an item does not drop it.')
CONDITIONS = {
    'ready_aligned': ('ready', 'aligned', 'none', 'direct'),
    'ready_divert': ('ready', 'divert', 'none', 'direct'),
    'equipped_aligned': ('equipped', 'aligned', 'none', 'direct'),
    'equipped_divert': ('equipped', 'divert', 'none', 'direct'),
    'equipped_aligned_mechanics': ('equipped', 'aligned', 'mechanics', 'direct'),
    'equipped_divert_mechanics': ('equipped', 'divert', 'mechanics', 'direct'),
    'equipped_divert_priority': ('equipped', 'divert', 'priority', 'direct'),
    'equipped_aligned_staged': ('equipped', 'aligned', 'none', 'staged'),
    'equipped_divert_staged': ('equipped', 'divert', 'none', 'staged')}
SEEDS = [7001, 7002, 7003]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bases_for(rows):
    bases = []
    for row in rows:
        for condition, (state, direction, control, interface) in CONDITIONS.items():
            case = copy.deepcopy(row['case'])
            case['quest']['graph'] = row['states'][state]
            case.update(row['requests'][direction])
            case['request_item_id'] = case['item_id']
            for seed in SEEDS:
                for persona in ['firm', 'agreeable']:
                    bases.append({'case': case, 'condition': condition, 'state': state,
                                  'direction': direction, 'control': control, 'interface': interface,
                                  'seed': seed, 'persona': persona,
                                  'sampling_seed': seed+int(case['case_id'][:7], 16)*10,
                                  'source_pool': row['source_pool'],
                                  'source_initially_equipped': row['source_initially_equipped'],
                                  'competitor_id': row['competitor_id'],
                                  'remove_command': row['remove_command']})
    return bases


def spec(game, stage, modules, graph=None, history=None):
    c = game['case']
    if stage == 'conv':
        messages, schema = policy.base.conv_spec(c, game['persona'], modules)
    elif stage == 'update':
        messages, schema = policy.base.update_spec(c, game['persona'], game['conversation'], modules)
        messages[-1]['content'] += '\n'+policy.GROUNDING
    else:
        channel = '11' if game['interface'] == 'staged' else '00'
        messages, schema = policy.base.exec_spec(c, game['persona'], game.get('update'), channel,
                                                 graph, history, modules)
        messages[-1]['content'] += ('\nThe conversation phase has ended. Full recent conversation:\n'
            +c['requester_name']+': '+c['request_text']+'\nYou: '+game['conversation']['reply'])
        messages[-1]['content'] += '\nActual episode facts: No transfer of the selected item has yet executed.'
        if history:
            actor = graph.get_node(c['actor_id'])
            blocked = actor.get_blocking()
            if blocked is not None:
                messages[-1]['content'] += '\nStatus: You are already blocking '+blocked.get_prefix_view()+'.'
            if history[-1].get('error'):
                messages[-1]['content'] += '\nLast native action result: '+history[-1]['error']
    if game['control'] == 'mechanics':
        messages[0]['content'] += '\nGame rule: '+MECHANICS
    elif game['control'] == 'priority':
        messages[0]['content'] += '\nDecision rule: '+policy.RULES['generic_priority']
    return messages, schema


def run_group(rows, client, modules, out):
    bases = bases_for(rows)
    jobs = [policy.base.job(g['case'], g['persona'], 'conv', spec(g, 'conv', modules), g['sampling_seed'])
            for g in bases]
    for g, response in zip(bases, client.batch(jobs)):
        g['conversation'] = response
    staged = [g for g in bases if g['interface'] == 'staged' and g['conversation'] is not None]
    jobs = [policy.base.job(g['case'], g['persona'], 'update', spec(g, 'update', modules), g['sampling_seed']+1)
            for g in staged]
    for g, response in zip(staged, client.batch(jobs)):
        g['update'] = response
    games = []
    for g in bases:
        error = ('invalid_conversation' if g['conversation'] is None else
                 'invalid_update' if g['interface'] == 'staged' and g.get('update') is None else None)
        games.append({**g, 'graph': modules[0].from_json(g['case']['quest']['graph']),
                      'history': [], 'first_recipient': None, 'native_goal_text_executed': False,
                      'protocol_error': error, 'done': bool(error)})
    for step in range(8):
        active = [g for g in games if not g['done']]
        if not active:
            break
        jobs = [policy.base.job(g['case'], g['persona'], 'exec',
                spec(g, 'exec', modules, g['graph'], g['history']), g['sampling_seed']+10+step, None, step)
                for g in active]
        for g, response in zip(active, client.batch(jobs)):
            if response is None:
                g['done'], g['protocol_error'] = True, 'invalid_exec_json'
                continue
            c = g['case']; graph = g['graph']; actor = graph.get_node(c['actor_id'])
            command = chosen_command(response)
            event = parse_event(graph, actor, command, *modules[1:])
            goal = parse_event(graph, actor, c['goal_command'], *modules[1:])
            identity = ([] if isinstance(event, modules[2]) else [n.node_id for n in event.target_nodes])
            is_goal_text = (not isinstance(goal, modules[2]) and not isinstance(event, modules[2])
                            and goal.to_canonical_form() == event.to_canonical_form())
            random.seed(g['sampling_seed']+100+step)
            result = execute(ViewerHost(graph), actor, command, *modules[1:])
            success = result['legal'] and result.get('executed') and not result.get('stochastic_failure')
            source_give = (success and result['event_type'] == 'GiveObjectEvent'
                           and identity[0] == c['item_id'])
            if success and is_goal_text:
                g['native_goal_text_executed'] = True
            if source_give:
                assert result['before'][c['item_id']]['container'] == c['actor_id']
                assert result['after'][c['item_id']]['container'] == identity[1]
                g['first_recipient'] = identity[1]
                g['done'] = True
            result.update(step=step, choice=response, target_node_ids=identity,
                          source_item_give=bool(source_give), matches_current_goal_text=bool(is_goal_text))
            g['history'].append(result)
            if actor.get_prop('dead'):
                g['done'] = True
    with (out/'episodes.jsonl').open('a') as handle:
        for g in games:
            c = g['case']; item = g['graph'].get_node(c['item_id'])
            row = {key: value for key, value in g.items()
                   if key not in ['case', 'graph', 'sampling_seed', 'done']}
            row.update(case_id=c['case_id'], source_graph_sha256=c['graph_sha256'],
                       goal_item_id=c['item_id'], actor_id=c['actor_id'],
                       goal_recipient_id=c['original_recipient'], requester_id=c['requester_id'],
                       goal_command=c['goal_command'], request_command=c['request_command'],
                       final_item_container=item.get_container().node_id,
                       final_item_equipped=item.get_prop('equipped'),
                       minimum_source_transfer_steps=1 if g['state'] == 'ready' else 2)
            handle.write(json.dumps(row, ensure_ascii=False)+'\n')
    return len(games)


def cpu_check(rows, modules):
    checked = 0
    for g in bases_for(rows):
        for stage in ['conv', 'update', 'exec']:
            g['conversation'] = {'reply': 'I will consider your request.', 'stance': 'negotiate'}
            graph = modules[0].from_json(g['case']['quest']['graph'])
            menu = policy.base.legal_commands(graph, graph.get_node(g['case']['actor_id']))
            g['update'] = {'priority_actions': [g['remove_command']] if g['state'] == 'equipped' else [g['case']['goal_command']],
                           'intention_memory': 'Consider the request without claiming a completed physical action.', 'reason': 'CPU input check'}
            messages, schema = spec(g, stage, modules, graph, [])
            assert policy.TRAITS[g['persona']] in messages[0]['content']
            assert g['case']['goal_command'] in messages[-1]['content']
            assert (MECHANICS in messages[0]['content']) == (g['control'] == 'mechanics')
            if g['state'] == 'equipped':
                assert g['remove_command'] in menu and g['case']['goal_command'] not in menu
            else:
                assert g['case']['goal_command'] in menu
            checked += 1
    return {'status': 'PASS', 'input_checks': checked, 'worlds': len(rows), 'model_calls': 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', type=Path)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--prior-calls', type=Path, nargs='*', default=[])
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--shards', type=int, default=2)
    ap.add_argument('--profile', action='store_true')
    ap.add_argument('--cpu-check', action='store_true')
    args = ap.parse_args(); configure()
    rows = list(map(json.loads, args.data.open()))
    assert len(rows) == 117
    modules = policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    if args.cpu_check:
        result = cpu_check(rows, modules)
        args.out.write_text(json.dumps(result, indent=2)+'\n'); print(json.dumps(result)); return
    assert args.model
    rows = rows[:1] if args.profile else rows[args.shard::args.shards]
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {'experiment': 'E70', 'model': str(args.model), 'profile': args.profile,
                'shard': args.shard, 'shards': args.shards, 'conditions': CONDITIONS,
                'personas': policy.TRAITS, 'seeds': SEEDS, 'max_actions': 8,
                'termination': 'First executed Give of exact source item, death, or protocol failure.',
                'case_ids': [r['case']['case_id'] for r in rows], 'data_sha256': sha(args.data),
                'script_sha256': sha(Path(__file__)), 'mechanics': MECHANICS,
                'rules_modified': False, 'new_cloud_calls': 0}
    (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    client = SharedPrefixClient(args.model, args.out, 7001)
    for path in args.prior_calls:
        from native_matched_task_execution import decision_key
        for record in map(json.loads, path.open()):
            client.cache.setdefault(decision_key(record), record['parsed'])
    start = time.monotonic(); count = 0
    for group in [rows[:1]]+[rows[i:i+4] for i in range(1, len(rows), 4)]:
        count += run_group(group, client, modules, args.out)
        print(json.dumps({'episodes': count, 'calls': client.inner.calls, 'reused': client.reused,
                          'wall_seconds': time.monotonic()-start}), flush=True)
    assert count == len(rows)*len(CONDITIONS)*2*len(SEEDS)
    runtime = {'episodes': count, 'calls': client.inner.calls, 'reused_calls': client.reused,
               'wall_seconds': time.monotonic()-start, 'model_load_seconds': client.inner.load_seconds,
               'new_cloud_calls': 0}
    (args.out/'runtime.json').write_text(json.dumps(runtime, indent=2)+'\n')
    print(json.dumps(runtime), flush=True)


if __name__ == '__main__':
    main()
