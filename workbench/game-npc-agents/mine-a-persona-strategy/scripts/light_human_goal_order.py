"""E31 original human/NPC goal ordering; native physics, bounded witnesses."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import random
import re
import tarfile
import time

from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, actor_for, execute, legal_commands, material_state


def norm(text):
    return re.sub(r"^(the|a|an) ", "", text.strip().lower())


def run_path(pair, quests, commands, seed, modules):
    OOGraph, events, ErrorEvent = modules
    q = [quests[pair['quest_file']], quests[pair['npc_file']]]
    assert q[0]['graph'] == q[1]['graph']
    graph = OOGraph.from_json(q[0]['graph'])
    actors = [actor_for(graph, x['character']) for x in q]
    host = ViewerHost(graph)
    random.seed(seed)
    attempts, successful = [False, False], [False, False]
    rows = []
    for index, command in commands:
        goal = parse_event(graph, actors[index], q[index]['goal'], events, ErrorEvent)
        chosen = parse_event(graph, actors[index], command, events, ErrorEvent)
        match = (not isinstance(goal, ErrorEvent) and not isinstance(chosen, ErrorEvent)
                 and goal.to_canonical_form() == chosen.to_canonical_form())
        row = execute(host, actors[index], command, events, ErrorEvent)
        row['matches_original_goal'] = match
        if match and row.get('executed'):
            attempts[index] = True
            if not row.get('stochastic_failure'):
                successful[index] = True
        rows.append(row)
    return graph, actors, rows, attempts, successful, random.getstate()


def bounded_witness(pair, quests, common_names, seed, modules, max_states):
    queue = deque([[]]); seen = set(); expanded = 0
    while queue and expanded < max_states:
        path = queue.popleft()
        graph, actors, rows, attempts, successful, rng = run_path(pair, quests, path, seed, modules)
        key = (json.dumps(material_state(graph), sort_keys=True), tuple(successful), rng)
        if key in seen:
            continue
        seen.add(key); expanded += 1
        if all(successful):
            return {'found': True, 'path': path, 'rows': rows, 'expanded': expanded}
        if len(path) >= 4:
            continue
        q = [quests[pair['quest_file']], quests[pair['npc_file']]]
        for index, actor in enumerate(actors):
            options = {q[index]['goal']}
            options.update(c for c in legal_commands(graph, actor)
                           if c.partition(' ')[0] in {'get', 'drop', 'give', 'steal'}
                           and any(re.search(r'(?<!\w)' + re.escape(n) + r'(?!\w)',
                                             c.lower()) for n in common_names))
            for command in sorted(options):
                event = parse_event(graph, actor, command, modules[1], modules[2])
                if not isinstance(event, modules[2]):
                    queue.append(path + [(index, command)])
    return {'found': False, 'expanded': expanded, 'states_cap_hit': bool(queue),
            'scope': 'No witness within four actions/cap and fixed stochastic seed; not impossibility.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--max-states', type=int, default=500)
    ap.add_argument('--seeds', type=int, nargs='+', default=[3101, 3102, 3103])
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    joins = json.loads((CACHE/'light_npc_human_join.json').read_text())
    demos = json.loads((CACHE/'light_quests_human_demos.json').read_text())
    pairs = [{**row, 'npc_file': npc['file']} for row in joins for npc in row['npc_goals']]
    if args.limit:
        pairs = pairs[:args.limit]
    needed = {p[k] for p in pairs for k in ['quest_file', 'npc_file']}; quests = {}
    with tarfile.open(CACHE/'quest_stems.tar.gz', 'r|gz') as archive:
        for member in archive:
            name = member.name.split('/')[-1]
            if name in needed:
                quests[name] = json.load(archive.extractfile(member))['data']
    modules = load_event_modules(CACHE/'sources/LIGHT')
    results = []
    for pair in pairs:
        q = [quests[pair['quest_file']], quests[pair['npc_file']]]
        graph, actors, _, _, _, _ = run_path(pair, quests, [], args.seeds[0], modules)
        common = sorted({norm(o.name) for o in graph.objects.values()
                         if all(re.search(r'(?<!\w)' + re.escape(norm(o.name)) + r'(?!\w)',
                                          x['goal'].lower()) for x in q)})
        row = {'demo_index': pair['demo_index'], 'quest_files': [pair['quest_file'], pair['npc_file']],
               'actors': [x['character'] for x in q], 'goals': [x['goal'] for x in q],
               'motivations': [x['short_motivation'] for x in q], 'common_object_names': common,
               'human_actions': [d for d in demos[pair['demo_index']]['dialogue'] if d['type'] == 'action'],
               'orders': [], 'witnesses': []}
        for seed in args.seeds:
            for order in [(0, 1), (1, 0)]:
                _, _, steps, attempts, success, _ = run_path(
                    pair, quests, [(i, q[i]['goal']) for i in order], seed, modules)
                row['orders'].append({'seed': seed, 'order': order, 'steps': steps,
                                      'goal_events_executed': attempts, 'successful_goal_events': success})
            if common:
                row['witnesses'].append({'seed': seed, **bounded_witness(
                    pair, quests, common, seed, modules, args.max_states)})
        results.append(row)
        with (args.out/'cases.jsonl').open('a') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    summary = {'pairs': len(results), 'strict_human_joins': len(joins),
               'common_object_pairs': sum(bool(r['common_object_names']) for r in results),
               'pairs_with_joint_witness': sum(any(w['found'] for w in r['witnesses']) for r in results),
               'seeds': args.seeds, 'max_actions': 4, 'max_states': args.max_states,
               'wall_seconds': time.monotonic()-started, 'cloud_calls': 0, 'gpu_hours': 0,
               'input_sha256': {n: hashlib.sha256((CACHE/n).read_bytes()).hexdigest()
                                for n in ['light_npc_human_join.json', 'quest_stems.tar.gz']},
               'scope': 'Native event/physical qualification; no abstract utility or original RL score reproduction.'}
    (args.out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
