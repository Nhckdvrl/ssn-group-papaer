#!/usr/bin/env python3
"""E57: pair only authored characters/quests in exactly identical native worlds."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import tarfile
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, actor_for


def sha(data): return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args(); a.out.mkdir(exist_ok=False, parents=True)
    groups = defaultdict(list)
    with tarfile.open(CACHE / 'quest_stems.tar.gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.json'): continue
            q = json.load(archive.extractfile(member))['data']; q['source_file'] = member.name.rsplit('/', 1)[-1]
            groups[sha(q['graph'].encode())].append(q)
    modules = load_event_modules(CACHE / 'sources/LIGHT'); pairs = []; issues = []
    for gh, quests in sorted(groups.items()):
        native = json.loads(quests[0]['graph'])
        objects = {i: n for i, n in native['nodes'].items() if n.get('object') and (n.get('food') or n.get('drink'))}
        for q0 in quests:
            verb, _, noun = q0['goal'].partition(' ')
            if verb not in ['eat', 'drink']: continue
            targets = [i for i, n in objects.items() if noun.lower().strip() in
                       [n['name'].lower(), *(v.lower() for v in n.get('names', []))]]
            if len(targets) != 1:
                issues.append({'source_file': q0['source_file'], 'goal': q0['goal'], 'reason': 'consumption noun has no unique native edible object'})
                continue
            target = targets[0]; name = objects[target]['name']
            for q1 in quests:
                if q1['character'] == q0['character']: continue
                if not re.search(r'(?<!\w)' + re.escape(name.lower()) + r'(?!\w)', q1['goal'].lower()): continue
                graph = modules[0].from_json(q0['graph'])
                try: actors = [actor_for(graph, q['character']) for q in [q0, q1]]
                except AssertionError as e:
                    issues.append({'files': [q0['source_file'], q1['source_file']], 'reason': 'source actor cannot be uniquely bound', 'error': str(e)})
                    continue
                if actors[0].get_room() != actors[1].get_room():
                    issues.append({'files': [q0['source_file'], q1['source_file']], 'reason': 'actors initially in different rooms'})
                    continue
                events = [parse_event(graph, actor, q['goal'], *modules[1:]) for actor, q in zip(actors, [q0, q1])]
                cid = sha((gh + '|' + q0['source_file'] + '|' + q1['source_file']).encode())[:20]
                pairs.append({'case_id': cid, 'graph_sha256': gh, 'quests': [q0, q1],
                    'actor_ids': [x.node_id for x in actors], 'item_id': target,
                    'initial_holder': graph.get_node(target).get_container().node_id,
                    'initial_goal_parse': [None if isinstance(e, modules[2]) else e.to_canonical_form() for e in events],
                    'initial_goal_errors': [e.view_as(actor) if isinstance(e, modules[2]) else None for e, actor in zip(events, actors)],
                    'source_pair_scope': 'Two separately authored quests bound on an identical graph; not the original retrieval partner policy.'})
    selected = {}
    for row in sorted(pairs, key=lambda r: r['case_id']): selected.setdefault(row['graph_sha256'], row)
    chosen = sorted(selected.values(), key=lambda r: r['case_id'])
    for name, rows in [('all_pairs.jsonl', pairs), ('snapshots.jsonl', chosen)]:
        (a.out / name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    report = {'authored_quests': sum(map(len, groups.values())), 'source_graphs': len(groups),
        'eligible_pairs': len(pairs), 'selected_independent_graphs': len(chosen),
        'selection': 'one minimum-SHA case per exact source graph, before model outcomes',
        'pair_verbs': dict(Counter('/'.join(q['goal'].split()[0] for q in r['quests']) for r in chosen)),
        'holder_categories': dict(Counter('focal' if r['initial_holder'] == r['actor_ids'][0] else 'partner' if r['initial_holder'] == r['actor_ids'][1] else 'other' for r in chosen)),
        'initial_focal_goal_parseable': sum(r['initial_goal_parse'][0] is not None for r in chosen),
        'issues': issues, 'archive_sha256': sha((CACHE / 'quest_stems.tar.gz').read_bytes()),
        'dataset_sha256': sha((a.out / 'snapshots.jsonl').read_bytes()), 'world_modified': False,
        'gpu_hours': 0, 'model_calls': 0, 'raw_directory': str(a.out)}
    (a.out / 'inventory.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'issues'}))


if __name__ == '__main__': main()
