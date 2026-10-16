#!/usr/bin/env python3
"""E84: original independent character goals, open native interactions.

Reuse E81's ordinary original-role prompt, observations and typed native tools.
No role receives the other's private purpose, forced exchange, reward gate,
goal-selection macro or narrative-success judgement. Raw states permit an
independent readback; event and physical goal measures are kept separate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time

from commitment_decisions_v2 import schema
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, material_state, observation
from native_cooperation_episodes import action_spec, header, identity, job, SPEECH
from native_reciprocal_deathsafe import character_dead, character_health
from native_rule_execution import SharedPrefixClient
from native_independent_goal_qualification import goal_event, owner

SEEDS = [8401, 8402]
MAX_TURNS = 32


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(case, index):
    return {**case['goal_bindings'][index], 'actor_id': case['actor_ids'][index],
            'goal': case['quests'][index]['goal']}


def physical_goal(case, index, graph, state, consumed):
    """Literal authored atomic outcome; never a private-utility/welfare label."""
    b = case['goal_bindings'][index]
    verb, item, target = b['verb'], b.get('item_id'), b.get('target_id')
    if not item or item not in state:
        return None
    current, actor = state[item], case['actor_ids'][index]
    held = current['container'] == actor
    if verb in ['get', 'steal']:
        return owner(graph, item) == actor
    if verb in ['give', 'put']:
        return current['container'] == target if target is not None else None
    if verb in ['wear', 'wield']:
        return held and current.get('equipped') == verb
    if verb in ['eat', 'drink']:
        return bool(consumed[index] and current['container'] == 'VOID')
    # Drop/Remove are reported as actual actor events, not replaced by a
    # convenient room/equipment state somebody else may have produced.
    return None


def refresh_goals(game):
    state = material_state(game['graph'])
    for i in [0, 1]:
        value = physical_goal(game['case'], i, game['graph'], state, game['consumed_by_actor'])
        game['physical_goal_now'][i] = value
        if value is not None and game['physical_goal_ever'][i] is None:
            game['physical_goal_ever'][i] = False
        if value is True:
            game['physical_goal_ever'][i] = True


def execute_selected(game, index, event, choice, turn, attempted=None):
    from light.graph.events.base import ErrorEvent
    graph, case = game['graph'], game['case']
    actor = graph.get_node(case['actor_ids'][index])
    before, full_before = material_state(graph), graph.to_json()
    expected_event, expected_error = goal_event(graph, binding(case, index), game['modules'])
    expected_identity = identity(expected_event) if expected_event is not None else None
    start = len(game['host'].messages)
    random.seed(game['seed'] + int(case['case_id'][:7], 16)*100 + turn + 1000)
    row = {'actor': actor.node_id, 'index': index, 'turn': turn, 'choice': choice,
           'event_identity': identity(event), 'event_type': type(event).__name__,
           'command': event.to_canonical_form() or ('rejected tool '+choice['tool']),
           'before': before, 'graph_before_sha256': hashlib.sha256(full_before.encode()).hexdigest(),
           'legal': not isinstance(event, ErrorEvent),
           'original_goal_current_identity': expected_identity,
           'original_goal_current_unavailable_reason': expected_error}
    if attempted is not None:
        row['selected_identity'] = attempted
    if isinstance(event, ErrorEvent):
        row.update(executed=False, error=event.view_as(actor))
    else:
        try:
            event.execute(game['host'])
            row.update(executed=bool(event.executed),
                       stochastic_failure=bool(getattr(event, 'failed', False)))
        except Exception as exc:
            row.update(executed=False, native_exception=type(exc).__name__+': '+str(exc))
            game['stop'] = 'native_runtime_error'
    row.update(after=material_state(graph), messages=game['host'].messages[start:])
    row['material_changed'] = before != row['after']
    if row.get('executed') and not row.get('stochastic_failure'):
        if expected_identity is not None and row['event_identity'] == expected_identity:
            game['strict_goal_ever'][index] = True
        b = case['goal_bindings'][index]
        if (b['verb'] in ['eat', 'drink'] and b.get('item_id')
                and row['event_type'] in ['EatEvent', 'DrinkEvent', 'IngestEvent']
                and row['event_identity'][1] and row['event_identity'][1][0] == b['item_id']
                and row['after'][b['item_id']]['container'] == 'VOID'):
            game['consumed_by_actor'][index] = True
    refresh_goals(game)
    row.update(strict_goal_ever=list(game['strict_goal_ever']),
               physical_goal_ever=list(game['physical_goal_ever']),
               physical_goal_now=list(game['physical_goal_now']))
    game['turns'].append(row)
    for i, aid in enumerate(case['actor_ids']):
        seen = [m['text'] for m in row['messages'] if m['viewer'] == aid]
        if i == index:
            seen.insert(0, 'Your actual tool attempt: '+row['command'])
            if row.get('native_exception'):
                seen.append('Native error: '+row['native_exception'])
            elif row.get('error'):
                seen.append('Native rejection: '+row['error'])
            elif not row.get('executed'):
                seen.append('Native tool did not record execution.')
        game['visible'][i].extend(seen)
    game['states'].append({'turn': turn, 'graph': graph.to_json(),
                           'visible': [list(x) for x in game['visible']]})
    if any(character_dead(graph, a) for a in case['actor_ids']):
        game['stop'] = 'character_death'


def apply_choice(game, index, choice, menu, turn, modules):
    if (not isinstance(choice, dict) or set(choice) != {'tool', 'utterance'}
            or not isinstance(choice.get('utterance'), str)
            or choice.get('tool') not in ['SAY']+list(menu)):
        game['stop'] = 'protocol_error'
        game['protocol_failure'] = {'turn': turn, 'actor_index': index, 'parsed': choice}
        return
    actor = game['graph'].get_node(game['case']['actor_ids'][index])
    if choice['tool'] == 'SAY':
        event = modules[1].SayEvent.construct_from_args(actor, [], choice['utterance'])
        attempted = ['SayEvent', []]
    else:
        event = menu[choice['tool']]
        attempted = identity(event)
        payload = choice['utterance'] if type(event).__name__ in SPEECH else event.text_content
        event = type(event).construct_from_args(actor, event.target_nodes, payload)
    execute_selected(game, index, event, choice, turn, attempted)


def load_cases(path, modules):
    rows = [json.loads(x) for x in path.read_text().splitlines()]
    assert len(rows) == len({c['case_id'] for c in rows})
    for c in rows:
        assert c['quests'][0]['graph'] == c['quests'][1]['graph']
        assert hashlib.sha256(c['quests'][0]['graph'].encode()).hexdigest() == c['graph_sha256']
        graph = modules[0].from_json(c['quests'][0]['graph'])
        c['initial_room_ids'] = [graph.get_node(a).get_room().node_id for a in c['actor_ids']]
        assert len(c['goal_bindings']) == len(c['goal_identities']) == 2
    return sorted(rows, key=lambda c: c['case_id'])


def new_game(case, seed, modules):
    graph = modules[0].from_json(case['quests'][0]['graph'])
    measurable = [bool(b.get('item_id')) and (
        b['verb'] not in ['give', 'put'] or b.get('target_id') is not None)
        for b in case['goal_bindings']]
    g = {'case': case, 'seed': seed, 'graph': graph, 'host': ViewerHost(graph), 'modules': modules,
         'visible': [[], []], 'turns': [], 'states': [],
         'strict_goal_measurement_supported': measurable,
         'strict_goal_ever': [False if supported else None for supported in measurable],
         'consumed_by_actor': [False, False], 'physical_goal_now': [None, None],
         'physical_goal_ever': [None, None], 'stop': None, 'initial_state': material_state(graph)}
    refresh_goals(g)
    g['physical_goal_initial'] = list(g['physical_goal_now'])
    return g


def cpu_check(rows, modules):
    count = 0
    for c in rows:
        g = new_game(c, SEEDS[0], modules)
        original = g['graph'].to_json()
        for i in [0, 1]:
            (messages, structure), menu = action_spec(g, i, modules)
            assert messages[0]['content'] == header(c, i)
            for k in ['short_motivation', 'mid_motivation', 'long_motivation']:
                value = c['quests'][1-i][k]
                if len(value) > 25 and value not in header(c, i):
                    assert value not in json.dumps(messages, ensure_ascii=False)
            assert all(e.actor.node_id == c['actor_ids'][i] for e in menu.values())
            goal_event(g['graph'], binding(c, i), modules)
            count += len(menu)
        assert g['graph'].to_json() == original
    return {'status': 'PASS', 'pairs': len(rows), 'source_graphs': len({c['graph_sha256'] for c in rows}),
            'typed_tools': count, 'private_headers_checked': len(rows)*2,
            'driver_sha256': sha(Path(__file__)), 'new_model_calls': 0, 'new_cloud_calls': 0}


def run_group(cases, seeds, client, modules, out):
    games = [new_game(c, seed, modules) for c in cases for seed in seeds]
    jobs = []
    for g in games:
        actor = g['graph'].get_node(g['case']['actor_ids'][1])
        text = observation(g['host'], actor, *modules[1:])
        text += '\nBegin a brief spoken interaction with '+g['case']['quests'][0]['character']+(
            ' about what you want to accomplish. You may propose cooperation or ask for help as appropriate. '
            'This opening sends speech only; actual actions follow separately.')
        spec = ([{'role': 'system', 'content': header(g['case'], 1)},
                 {'role': 'user', 'content': text}],
                schema({'utterance': {'type': 'string', 'maxLength': 500}}))
        jobs.append(job(g, 1, spec, 'player_opening', -1))
    for g, answer in zip(games, client.batch(jobs)):
        if not isinstance(answer, dict) or not isinstance(answer.get('utterance'), str):
            g['stop'] = 'protocol_error'
            g['protocol_failure'] = {'turn': -1, 'actor_index': 1, 'parsed': answer}
        else:
            apply_choice(g, 1, {'tool': 'SAY', 'utterance': answer['utterance']}, {}, -1, modules)
            g['opening'] = g['turns'].pop() if g['turns'] else None
    for turn in range(MAX_TURNS):
        active = [g for g in games if g['stop'] is None]
        if not active:
            break
        index = turn % 2
        prepared = [action_spec(g, index, modules) for g in active]
        jobs = [job(g, index, spec, 'native_action', turn) for g, (spec, menu) in zip(active, prepared)]
        for g, answer, (_, menu) in zip(active, client.batch(jobs), prepared):
            apply_choice(g, index, answer, menu, turn, modules)
    with (out/'episodes.jsonl').open('a') as f, (out/'states.jsonl').open('a') as sf:
        for g in games:
            row = {k: v for k, v in g.items() if k not in ['case', 'graph', 'host', 'visible', 'states', 'modules']}
            row.update(case_id=g['case']['case_id'], graph_sha256=g['case']['graph_sha256'],
                       quest_files=[q['source_file'] for q in g['case']['quests']],
                       stop=g['stop'] or 'turn_limit', final_state=material_state(g['graph']),
                       final_health=[character_health(g['graph'], a) for a in g['case']['actor_ids']],
                       final_dead=[character_dead(g['graph'], a) for a in g['case']['actor_ids']])
            f.write(json.dumps(row, ensure_ascii=False)+'\n')
            sf.write(json.dumps({'case_id': g['case']['case_id'], 'seed': g['seed'],
                                  'states': g['states']}, ensure_ascii=False)+'\n')
    return len(games)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--profile', action='store_true')
    ap.add_argument('--cpu-check', action='store_true')
    ap.add_argument('--prior-runs', type=Path, nargs='*', default=[])
    a = ap.parse_args()
    assert os.environ.get('PYTHONHASHSEED') == '0'
    modules = load_event_modules(CACHE/'sources/LIGHT')
    rows = load_cases(a.data, modules)
    if a.cpu_check:
        r = cpu_check(rows, modules)
        r['data_sha256'] = sha(a.data)
        a.out.write_text(json.dumps(r, indent=2)+'\n')
        print(json.dumps(r))
        return
    assert a.model and rows
    selected, seeds = (rows[:1], SEEDS[:1]) if a.profile else (rows, SEEDS)
    a.out.mkdir(parents=True, exist_ok=False)
    dependency_files = ['native_cooperation_episodes.py', 'native_independent_goal_qualification.py',
                        'light_npc_episodes.py', 'native_rule_execution.py',
                        'commitment_decisions_v2.py', 'light_native_gate.py']
    dependencies = {name: sha(Path(__file__).with_name(name)) for name in dependency_files}
    manifest = {'experiment': 'E84', 'model': str(a.model), 'data': str(a.data),
                'data_sha256': sha(a.data), 'driver_sha256': sha(Path(__file__)),
                'shared_interface_sha256': sha(Path(__file__).with_name('native_cooperation_episodes.py')),
                'profile': a.profile, 'seeds': seeds, 'case_ids': [c['case_id'] for c in selected],
                'max_turns': MAX_TURNS, 'personas': 'both original authored',
                'dependency_sha256': dependencies,
                'new_cloud_calls': 0, 'world_modified': False,
                'scope': 'Original atomic outcomes are not total private utility, welfare or agreement-fulfillment labels.'}
    (a.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    client = SharedPrefixClient(a.model, a.out, SEEDS[0])
    for folder in a.prior_runs:
        old = json.loads((folder/'manifest.json').read_text())
        for key in ['driver_sha256', 'model', 'data_sha256', 'shared_interface_sha256', 'dependency_sha256', 'max_turns']:
            assert old[key] == manifest[key]
        assert (folder/'runtime.json').exists()
        assert set(old['case_ids']) <= set(manifest['case_ids']) and set(old['seeds']) <= set(seeds)
        recorded = [json.loads(x) for x in (folder/'episodes.jsonl').read_text().splitlines()]
        assert {(x['case_id'], x['seed']) for x in recorded} == {
            (c, s) for c in old['case_ids'] for s in old['seeds']}
        assert all(x['stop'] != 'turn_limit' or len(x['turns']) == MAX_TURNS for x in recorded)
        for row in map(json.loads, (folder/'model_calls.jsonl').open()):
            client.cache.setdefault(row['decision_key'], row['parsed'])
    start, count = time.monotonic(), 0
    for offset in range(0, len(selected), 8):
        count += run_group(selected[offset:offset+8], seeds, client, modules, a.out)
        print(json.dumps({'pairs_completed': min(offset+8, len(selected)), 'episodes': count,
                          'calls': client.inner.calls, 'seconds': time.monotonic()-start}), flush=True)
    (a.out/'runtime.json').write_text(json.dumps({'pairs': len(selected), 'episodes': count,
        'calls': client.inner.calls, 'reused_calls': client.reused,
        'wall_seconds': time.monotonic()-start, 'model_load_seconds': client.inner.load_seconds,
        'new_cloud_calls': 0}, indent=2)+'\n')


if __name__ == '__main__':
    main()
