#!/usr/bin/env python3
"""E57: local two-character native interaction, authored goals and irreversible food."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
from commitment_decisions_v2 import BatchClient, PERSONAS, schema
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, execute, observation, legal_commands, chosen_command, material_state


def identity(case, index, persona):
    q = case['quests'][index]
    text = (f"You are {q['character']} in a native LIGHT game.\nCharacter persona: {q['persona']}\n"
            f"Short motivation: {q['short_motivation']}\nMid motivation: {q['mid_motivation']}\n"
            f"Long motivation: {q['long_motivation']}\nAuthored immediate goal action: {q['goal']}\n")
    if index == 0: text += 'Character disposition: ' + PERSONAS[persona] + '\n'
    return text + ('Choose for this character using the current visible game state, your motivations and social relationships. '
        'You may speak, negotiate or execute a physical action. Use native feedback to distinguish speech from actual execution. '
        'Private reasons are not spoken to the other character; only a selected speech command transmits your utterance.')


def visible_context(g, index, modules):
    actor = g['graph'].get_node(g['case']['actor_ids'][index]); host = g['host']
    view = observation(host, actor, *modules[1:]); menu = legal_commands(g['graph'], actor)
    history = g['visible'][index]
    text = view + '\nActually executed original goal event for you: ' + str(g['goal_done'][index])
    text += '\nRecent observable interaction:\n' + '\n'.join(history[-16:])
    text += '\nLegal game commands:\n' + '\n'.join(menu) + '\nChoose your next legal game action.'
    return text, menu


def apply(g, index, command, choice, turn, modules):
    case = g['case']; graph = g['graph']; actor = graph.get_node(case['actor_ids'][index])
    goal = parse_event(graph, actor, case['quests'][index]['goal'], *modules[1:])
    chosen = parse_event(graph, actor, command, *modules[1:])
    goal_match = (not isinstance(goal, modules[2]) and not isinstance(chosen, modules[2])
                  and goal.to_canonical_form() == chosen.to_canonical_form())
    food_match = (not isinstance(chosen, modules[2]) and type(chosen).__name__ in ['EatEvent', 'DrinkEvent']
                  and chosen.target_nodes[0].node_id == case['item_id'])
    random.seed(g['seed'] + int(case['case_id'][:7], 16) * 100 + turn)
    row = execute(g['host'], actor, command, *modules[1:])
    row.update(index=index, turn=turn, choice=choice, matches_original_goal=goal_match)
    success = row.get('legal') and row.get('executed') and not row.get('stochastic_failure')
    if goal_match and success: g['goal_done'][index] = True
    if food_match and success: g['consumer'] = index
    for i, aid in enumerate(case['actor_ids']):
        received = [m['text'] for m in row['messages'] if m['viewer'] == aid]
        if i == index:
            received.insert(0, 'Your executed command: ' + command)
            if not row['legal']: received.append(row.get('error', 'Native event rejected'))
        g['visible'][i].extend(received)
    g['turns'].append(row)
    if g['consumer'] is not None: g['stop'] = 'target_consumed'
    elif any(graph.get_node(aid).get_prop('dead') for aid in case['actor_ids']): g['stop'] = 'character_death'


def run_group(cases, client, modules, out, seeds):
    openings = {}; jobs = []
    for c in cases:
        for seed in seeds:
            graph = modules[0].from_json(c['quests'][0]['graph'])
            partner = graph.get_node(c['actor_ids'][1])
            view = observation(ViewerHost(graph), partner, *modules[1:])
            messages = [{'role': 'system', 'content': identity(c, 1, 'firm')},
                {'role': 'user', 'content': view + '\nStart a brief conversation with ' + c['quests'][0]['character']
                    + ' about your immediate motivation. You may ask, explain, negotiate or refuse. This initial turn is a native spoken utterance; no physical action is selected yet.'}]
            jobs.append({'case_id': c['case_id'], 'persona': 'partner', 'stage': 'opening', 'seed': seed + int(c['case_id'][:7], 16),
                         'messages': messages, 'schema': schema({'utterance': {'type': 'string'}})})
    for j, answer in zip(jobs, client.batch(jobs)): openings[j['case_id'], j['seed']] = answer
    games = []
    for c in cases:
        for seed in seeds:
            opening = openings[c['case_id'], seed + int(c['case_id'][:7], 16)]
            for p in PERSONAS:
                graph = modules[0].from_json(c['quests'][0]['graph'])
                g = {'case': c, 'persona': p, 'seed': seed, 'graph': graph, 'host': ViewerHost(graph),
                     'visible': [[], []], 'goal_done': [False, False], 'turns': [], 'consumer': None, 'stop': None,
                     'protocol_error': None, 'opening': opening, 'initial_state': material_state(graph)}
                if opening is None: g['stop'], g['protocol_error'] = 'protocol_error', 'invalid_opening_json'
                else: apply(g, 1, 'say ' + opening['utterance'], opening, -1, modules)
                games.append(g)
    # Twelve turns per character; no navigation frames, no unrelated NPC inference.
    for turn in range(24):
        index = turn % 2; active = [g for g in games if g['stop'] is None]
        if not active: break
        jobs = []
        for g in active:
            text, menu = visible_context(g, index, modules)
            jobs.append({'case_id': g['case']['case_id'], 'persona': g['persona'], 'stage': 'native_action',
                'acting_index': index, 'turn': turn, 'episode_seed': g['seed'],
                'seed': g['seed'] + int(g['case']['case_id'][:7], 16) * 100 + turn + 2000,
                'messages': [{'role': 'system', 'content': identity(g['case'], index, g['persona'])},
                             {'role': 'user', 'content': text}],
                'schema': schema({'action': {'type': 'string', 'enum': menu + ['say']},
                                  'utterance': {'type': 'string'}, 'reason': {'type': 'string'}})})
        for g, answer in zip(active, client.batch(jobs)):
            if answer is None: g['stop'], g['protocol_error'] = 'protocol_error', 'invalid_action_json'
            else: apply(g, index, chosen_command(answer), answer, turn, modules)
    with (out / 'episodes.jsonl').open('a') as f:
        for g in games:
            row = {k: v for k, v in g.items() if k not in ['case', 'graph', 'host', 'visible']}
            row.update(case_id=g['case']['case_id'], graph_sha256=g['case']['graph_sha256'],
                       stop=g['stop'] or 'turn_limit', final_state=material_state(g['graph']))
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return len(games)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seeds', type=int, nargs='+', default=[5701, 5702, 5703])
    ap.add_argument('--shard', type=int, default=0); ap.add_argument('--shards', type=int, default=1)
    a = ap.parse_args(); all_cases = list(map(json.loads, a.dataset.read_text().splitlines()))
    assert len({c['graph_sha256'] for c in all_cases}) == len(all_cases) == 39
    cases = [c for i, c in enumerate(all_cases) if i % a.shards == a.shard]
    a.out.mkdir(parents=True, exist_ok=False)
    manifest = {'arguments': {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()},
        'case_ids': [c['case_id'] for c in cases], 'dataset_sha256': hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'personas': PERSONAS,
        'max_action_turns': 24, 'world_modified': False, 'npc_cloud_calls': 0,
        'partner': 'same local model, original authored persona and private motivations; no focal disposition intervention',
        'opening_scope': 'native Say shared by focal persona pair; speech-only generation instruction is absent from action context',
        'endpoint_scope': 'irreversible consumption of the specified native food, character death, or 24 action turns'}
    (a.out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
    modules = load_event_modules(CACHE / 'sources/LIGHT'); client = BatchClient(a.model, a.out, a.seeds[0])
    start = time.monotonic(); count = 0
    # First full native scene reports measured cost before broadening the batch.
    groups = [cases[:1]] + [cases[i:i+6] for i in range(1, len(cases), 6)]
    for cs in groups:
        if not cs: continue
        count += run_group(cs, client, modules, a.out, a.seeds)
        print(json.dumps({'episodes': count, 'calls': client.calls, 'wall_seconds': time.monotonic()-start}), flush=True)
    assert count == len(cases) * len(a.seeds) * 2
    (a.out / 'runtime.json').write_text(json.dumps({'graphs': len(cases), 'episodes': count, 'calls': client.calls,
        'wall_seconds': time.monotonic()-start, 'model_load_seconds': client.load_seconds, 'npc_cloud_calls': 0}, indent=2) + '\n')


if __name__ == '__main__': main()
