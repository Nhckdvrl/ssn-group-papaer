#!/usr/bin/env python3
"""E80: real local player interaction, common decisions, two native executors."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import time

from native_rule_execution import configure, SharedPrefixClient, policy
from light_native_gate import parse_event
from light_npc_episodes import ViewerHost, execute, observation, legal_commands, chosen_command, material_state
from native_owned_container_qualification import event_id
from native_reciprocal_deathsafe import character_health, character_dead
from native_interactive_skills import snapshot_target_identity, native_short_path

SEEDS = [8001, 8002, 8003]
BACKENDS = ['model_steps', 'native_skill']
ALIASES = {'PURSUE_AUTHORED_OUTCOME': 'goal', 'FULFILL_REQUEST': 'request'}
COMMUNICATION = ('Only a selected say, tell, or whisper command transmits utterance to the other character. '
                 'For a non-speech command set utterance to the empty string. '
                 'Speech is not a completed physical action. Use actual feedback and visible state. '
                 'You may negotiate, refuse, change your proposal, or act. Keep speech brief.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cases(data, modules):
    rows = list(map(json.loads, data.open()))
    assert len(rows) == 200
    cases = []
    for row in rows:
        case = copy.deepcopy(row['case'])
        request = row['requests']['goal_item']
        case['request_command'] = request['command']
        case['request_text'] = request['request_text']
        assert request['item_id'] == case['item_id']
        case['native_target_identities'] = snapshot_target_identity(case, modules)
        cases.append(case)
    assert len({c['graph_sha256'] for c in cases}) == 200
    return cases


def profile_cases(cases):
    # Source-only deterministic coverage, chosen before any model output.
    return [next(c for c in cases if c['goal_kind'] == 'give'),
            next(c for c in cases if c['goal_kind'] != 'give')]


def npc_header(case, persona):
    return policy.base.header(case, persona) + '\n' + COMMUNICATION


def player_header(case):
    return (f"You control {case['requester_name']} as a simulated player in a LIGHT fantasy game.\n"
            f"Your character persona: {case['requester_persona']}\n"
            f"Your starting request to the other character was: {case['request_text']}\n"
            'For this interaction, seek the requested item using the visible world and available legal actions. '
            'This request objective is assigned for this simulation; it is not a private quest of the other character. '
            'You can ask questions, respond to proposals, trade your existing items, or choose other available actions. '
            'Do not invent possessions, completed transfers, or knowledge of someone else\'s private motivations. '
            + COMMUNICATION)


def outcome_text(case, target):
    if target == 'goal':
        return 'Realize your original authored outcome: ' + case['goal_command']
    return 'Transfer the requested source item to ' + case['requester_name'] + ': ' + case['request_command']


def view_context(game, role, modules):
    case, graph = game['case'], game['graph']
    aid = case['actor_id'] if role == 'npc' else case['requester_id']
    actor = graph.get_node(aid)
    text = observation(game['host'], actor, *modules[1:])
    text += '\nRecent actual observable interaction:\n' + '\n'.join(game['visible'][role][-24:])
    blocking = actor.get_blocking()
    if blocking:
        text += '\nActual status: You are already blocking ' + blocking.get_prefix_view() + '.'
    if role == 'npc':
        text += '\nOriginal authored task: ' + case['goal_command']
        text += '\nActual historical task event executed: ' + str(game['goal_bound_ever'])
        text += '\nActual historical source transfer by you to requester: ' + str(game['npc_give_request_ever'])
    return text, legal_commands(graph, actor)


def action_schema(menu):
    return policy.base.schema({
        'action': {'type': 'string', 'enum': sorted(set(menu + ['say']))},
        'utterance': {'type': 'string', 'maxLength': 400}})


def selector_spec(game, modules):
    text, menu = view_context(game, 'npc', modules)
    paths = {target: native_short_path(game['graph'], game['case'], target, modules)
             for target in ['goal', 'request']}
    options = []
    for alias, target in ALIASES.items():
        if paths[target]:
            options.append(alias)
            text += '\nOptional attainable outcome ' + alias + ': ' + outcome_text(game['case'], target) + '.'
    text += ('\nChoose a native action, actual speech, or one optional outcome. '
             'An outcome selection expresses what to work toward now; it does not record a completed action. '
             'You may revise your choice at your next turn after seeing what actually happens.\nNative commands:\n'
             + '\n'.join(menu))
    return ([{'role': 'system', 'content': npc_header(game['case'], game['persona'])},
             {'role': 'user', 'content': text}], action_schema(menu + options)), paths


def primitive_spec(game, target, modules):
    text, menu = view_context(game, 'npc', modules)
    text += ('\nThe outcome you just selected to work toward is: ' + outcome_text(game['case'], target)
             + '.\nChoose exactly one actual next native action in the current state. '
             'This outcome has not been marked complete by the selection.\nNative commands:\n' + '\n'.join(menu))
    return ([{'role': 'system', 'content': npc_header(game['case'], game['persona'])},
             {'role': 'user', 'content': text}], action_schema(menu))


def player_spec(game, modules):
    text, menu = view_context(game, 'player', modules)
    text += '\nChoose your next actual game action or speech.\nNative commands:\n' + '\n'.join(menu)
    return ([{'role': 'system', 'content': player_header(game['case'])},
             {'role': 'user', 'content': text}], action_schema(menu))


def make_job(game, stage, spec, turn):
    case = game['case']
    offset = {'npc_choice': 0, 'npc_primitive': 1, 'player': 2}[stage]
    return {'case_id': case['case_id'], 'persona': game['persona'], 'backend': game['backend'],
            'episode_seed': game['seed'], 'stage': stage, 'turn': turn,
            'seed': game['seed'] + int(case['case_id'][:7], 16)*1000 + (turn+1)*10 + offset,
            'messages': spec[0], 'schema': spec[1]}


def physical_goal(case, row):
    sid, aid = case['item_id'], case['actor_id']
    if (row['role'] != 'npc' or not row['legal'] or not row.get('executed')
            or row.get('stochastic_failure') or not row['target_node_ids']
            or row['target_node_ids'][0] != sid):
        return False
    before, after = row['before'][sid], row['after'][sid]
    if case['goal_kind'] in ['eat', 'drink']:
        return (row['event_type'] in ['EatEvent', 'DrinkEvent', 'IngestEvent']
                and before['container'] == aid and after['container'] == 'VOID')
    if case['goal_kind'] in ['wear', 'wield']:
        return (row['event_type'] == {'wear': 'WearEvent', 'wield': 'WieldEvent'}[case['goal_kind']]
                and after['container'] == aid and after.get('equipped') == case['goal_kind'])
    return (row['event_type'] == 'GiveObjectEvent'
            and after['container'] == case['original_recipient'])


def apply(game, role, command, decision, turn, modules, target=None, path_length=0, lower=None):
    case, graph = game['case'], game['graph']
    aid = case['actor_id'] if role == 'npc' else case['requester_id']
    actor = graph.get_node(aid)
    parsed = parse_event(graph, actor, command, *modules[1:])
    ident = event_id(parsed, modules)
    identity = [ident[0], list(ident[1])] if ident else None
    random.seed(game['seed'] + int(case['case_id'][:7], 16)*1000 + turn + 1000)
    row = execute(game['host'], actor, command, *modules[1:])
    success = row['legal'] and row.get('executed') and not row.get('stochastic_failure')
    bound = bool(role == 'npc' and success and identity == case['native_target_identities']['goal'])
    given = bool(role == 'npc' and success and identity == case['native_target_identities']['request'])
    row.update(role=role, turn=turn, decision=decision, selected_target=target,
               path_length=path_length, lower_decision=lower,
               target_node_ids=identity[1] if identity else [],
               matches_bound_goal=bound, source_give_to_requester=given)
    game['goal_bound_ever'] |= bound
    game['goal_physical_ever'] |= physical_goal(case, row)
    game['npc_give_request_ever'] |= given
    game['turns'].append(row)
    for view_role, viewer in [('npc', case['actor_id']), ('player', case['requester_id'])]:
        seen = [m['text'] for m in row['messages'] if m['viewer'] == viewer]
        if view_role == role:
            seen.insert(0, 'Your attempted command: ' + command)
            if row.get('error'):
                seen.append('Native rejection: ' + row['error'])
        game['visible'][view_role].extend(seen)
    if any(character_dead(graph, a) for a in [case['actor_id'], case['requester_id']]):
        game['stop'] = 'character_death'


def run_group(cases, client, modules, out):
    games = []
    for case in cases:
        for seed in SEEDS:
            for persona in ['firm', 'agreeable']:
                for backend in BACKENDS:
                    graph = modules[0].from_json(case['quest']['graph'])
                    game = {'case': case, 'seed': seed, 'persona': persona, 'backend': backend,
                            'graph': graph, 'host': ViewerHost(graph), 'visible': {'npc': [], 'player': []},
                            'goal_bound_ever': False, 'goal_physical_ever': False, 'npc_give_request_ever': False,
                            'turns': [], 'stop': None, 'protocol_error': None, 'initial_state': material_state(graph)}
                    apply(game, 'player', 'say '+case['request_text'], {'opening': True}, -1, modules)
                    game['opening'] = game['turns'].pop()
                    games.append(game)
    for turn in range(16):
        active = [g for g in games if g['stop'] is None]
        if not active:
            break
        if turn % 2:
            jobs = [make_job(g, 'player', player_spec(g, modules), turn) for g in active]
            for g, answer in zip(active, client.batch(jobs)):
                if answer is None:
                    g['stop'], g['protocol_error'] = 'protocol_error', 'invalid_player_json'
                else:
                    apply(g, 'player', chosen_command(answer), answer, turn, modules)
            continue
        prepared = [selector_spec(g, modules) for g in active]
        jobs = [make_job(g, 'npc_choice', spec, turn) for g, (spec, paths) in zip(active, prepared)]
        answers = client.batch(jobs)
        pending = []
        for game, answer, (_, paths) in zip(active, answers, prepared):
            if answer is None:
                game['stop'], game['protocol_error'] = 'protocol_error', 'invalid_npc_choice_json'
                continue
            target = ALIASES.get(answer['action'])
            if target is None:
                apply(game, 'npc', chosen_command(answer), answer, turn, modules)
                continue
            path = paths[target]
            assert path and len(path) in [1, 2]
            if len(path) == 1 or game['backend'] == 'native_skill':
                apply(game, 'npc', path[0], answer, turn, modules, target, len(path))
            else:
                pending.append((game, answer, target, path))
        if pending:
            jobs = [make_job(g, 'npc_primitive', primitive_spec(g, target, modules), turn)
                    for g, answer, target, path in pending]
            for (game, answer, target, path), lower in zip(pending, client.batch(jobs)):
                if lower is None:
                    game['stop'], game['protocol_error'] = 'protocol_error', 'invalid_npc_primitive_json'
                else:
                    apply(game, 'npc', chosen_command(lower), answer, turn, modules, target, len(path), lower)
    with (out/'episodes.jsonl').open('a') as handle:
        for game in games:
            case = game['case']
            row = {k: v for k, v in game.items() if k not in ['case', 'graph', 'host', 'visible']}
            row.update(case_id=case['case_id'], graph_sha256=case['graph_sha256'], goal_kind=case['goal_kind'],
                       goal_item_id=case['item_id'], actor_id=case['actor_id'], requester_id=case['requester_id'],
                       goal_recipient_id=case['original_recipient'], goal_command=case['goal_command'],
                       request_command=case['request_command'], native_target_identities=case['native_target_identities'],
                       final_state=material_state(game['graph']), stop=game['stop'] or 'turn_limit',
                       final_health=[character_health(game['graph'], a) for a in [case['actor_id'], case['requester_id']]],
                       final_dead=[character_dead(game['graph'], a) for a in [case['actor_id'], case['requester_id']]])
            handle.write(json.dumps(row, ensure_ascii=False)+'\n')
    return len(games)


def cpu_check(cases, modules):
    checks = 0
    for case in cases:
        graph = modules[0].from_json(case['quest']['graph'])
        game = {'case': case, 'persona': 'firm', 'backend': 'model_steps', 'seed': SEEDS[0],
                'graph': graph, 'host': ViewerHost(graph), 'visible': {'npc': [], 'player': []},
                'goal_bound_ever': False, 'npc_give_request_ever': False}
        before = graph.to_json()
        a, paths = selector_spec(game, modules)
        b, paths2 = selector_spec({**game, 'backend': 'native_skill'}, modules)
        assert a == b and paths == paths2
        assert all(len(path) == 1 for path in paths.values())
        assert npc_header(case, 'firm') == a[0][0]['content']
        p, sch = player_spec(game, modules)
        assert p[0]['content'] == player_header(case)
        assert 'Original authored task:' not in p[-1]['content']
        for field in ['short_motivation', 'mid_motivation', 'long_motivation']:
            value = case['quest'][field]
            if len(value.strip()) > 25 and value not in case['requester_persona']:
                assert value not in json.dumps(p), (case['case_id'], field)
        assert graph.to_json() == before
        checks += 1
    return {'status': 'PASS', 'worlds': len(cases), 'paired_selector_checks': checks,
            'player_private_goal_leak_checks': checks, 'initial_one_step_targets': checks*2,
            'planned_full_episodes_per_model': len(cases)*12, 'model_calls': 0, 'cloud_calls': 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--profile', action='store_true')
    ap.add_argument('--cpu-check', action='store_true')
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--shards', type=int, default=1)
    ap.add_argument('--prior-runs', type=Path, nargs='*', default=[])
    args = ap.parse_args()
    configure()
    assert os.environ.get('PYTHONHASHSEED') == '0'
    modules = policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    cases = load_cases(args.data, modules)
    if args.cpu_check:
        result = cpu_check(cases, modules)
        result.update(driver_sha256=sha(Path(__file__)), data_sha256=sha(args.data),
                      skills_sha256=sha(Path(__file__).with_name('native_interactive_skills.py')))
        args.out.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result)); return
    assert args.model
    selected = profile_cases(cases) if args.profile else cases[args.shard::args.shards]
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {'experiment': 'E80', 'model': str(args.model), 'profile': args.profile,
                'shard': args.shard, 'shards': args.shards, 'source': str(args.data),
                'source_sha256': sha(args.data), 'case_ids': [c['case_id'] for c in selected],
                'seeds': SEEDS, 'personas': policy.TRAITS, 'backends': BACKENDS,
                'max_turns': 16, 'initial_request_is_free_common_stimulus': True,
                'driver_sha256': sha(Path(__file__)),
                'skills_sha256': sha(Path(__file__).with_name('native_interactive_skills.py')),
                'rules_modified': False, 'new_cloud_calls': 0,
                'scope': 'Common strong selector; skill realizes only an independently selected target, one native primitive per opportunity. Models include both NPC and player.'}
    (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    client = SharedPrefixClient(args.model, args.out, SEEDS[0])
    for folder in args.prior_runs:
        assert (folder/'runtime.json').exists()
        old = json.loads((folder/'manifest.json').read_text())
        assert old['model'] == str(args.model) and old['driver_sha256'] == manifest['driver_sha256']
        for row in map(json.loads, (folder/'model_calls.jsonl').open()):
            client.cache.setdefault(row['decision_key'], row['parsed'])
    start = time.monotonic(); count = 0
    for group in [selected[:1]] + [selected[i:i+4] for i in range(1, len(selected), 4)]:
        count += run_group(group, client, modules, args.out)
        print(json.dumps({'episodes': count, 'calls': client.inner.calls, 'reused': client.reused,
                          'seconds': time.monotonic()-start}), flush=True)
    assert count == len(selected)*12
    runtime = {'worlds': len(selected), 'episodes': count, 'calls': client.inner.calls,
               'reused_calls': client.reused, 'wall_seconds': time.monotonic()-start,
               'model_load_seconds': client.inner.load_seconds, 'new_cloud_calls': 0}
    (args.out/'runtime.json').write_text(json.dumps(runtime, indent=2)+'\n')
    print(json.dumps(runtime), flush=True)


if __name__ == '__main__':
    main()
