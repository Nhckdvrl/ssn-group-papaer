#!/usr/bin/env python3
"""E64 source sensitivity: authored bilateral Give goals, without LLM calls."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import tarfile
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, actor_for, ViewerHost, execute


def sha(text): return hashlib.sha256(text.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args(); a.out.mkdir(parents=True, exist_ok=False)
    groups, issues = defaultdict(list), Counter()
    with tarfile.open(CACHE / 'quest_stems.tar.gz') as archive:
        for member in archive:
            if member.isfile() and member.name.endswith('.json'):
                q = json.load(archive.extractfile(member))['data']
                q['source_file'] = member.name.rsplit('/', 1)[-1]
                groups[sha(q['graph'])].append(q)
    modules = load_event_modules(CACHE / 'sources/LIGHT'); pairs = []
    for gh, quests in sorted(groups.items()):
        graph = modules[0].from_json(quests[0]['graph']); entries = []
        for q in quests:
            if not q['goal'].startswith('give '): continue
            try: actor = actor_for(graph, q['character'])
            except AssertionError:
                issues['ambiguous_actor'] += 1; continue
            event = parse_event(graph, actor, q['goal'], *modules[1:])
            if isinstance(event, modules[2]):
                issues['goal_not_initially_legal'] += 1; continue
            assert type(event).__name__ == 'GiveObjectEvent'
            item, recipient = event.target_nodes
            if item.get_container().node_id != actor.node_id:
                issues['not_directly_owned'] += 1; continue
            entries.append((q, actor.node_id, item.node_id, recipient.node_id))
        for q0, a0, t0, r0 in entries:
            for q1, a1, t1, r1 in entries:
                if a0 >= a1 or a0 != r1 or a1 != r0 or t0 == t1: continue
                g = modules[0].from_json(q0['graph']); commands = []
                for q, aid in [(q0, a0), (q1, a1)]:
                    result = execute(ViewerHost(g), g.get_node(aid), q['goal'], *modules[1:])
                    if not result['legal'] or not result.get('executed'): break
                    commands.append(result['command'])
                if len(commands) != 2:
                    issues['sequential_execution_failed'] += 1; continue
                assert g.get_node(t0).get_container().node_id == a1
                assert g.get_node(t1).get_container().node_id == a0
                cid = sha(gh + '|' + q0['source_file'] + '|' + q1['source_file'])[:20]
                pairs.append({'case_id': cid, 'graph_sha256': gh, 'quests': [q0, q1],
                    'actor_ids': [a0, a1], 'outgoing_item_ids': [t0, t1],
                    'native_goal_execution_witness': commands})
    selected = {}
    for row in sorted(pairs, key=lambda r: r['case_id']): selected.setdefault(row['graph_sha256'], row)
    rows = sorted(selected.values(), key=lambda r: r['case_id'])
    dataset = a.out / 'snapshots.jsonl'
    dataset.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    summary = {'source_graphs': len(groups), 'eligible_pairs': len(pairs), 'independent_worlds': len(rows),
        'source_issues': dict(issues), 'native_goal_actions_witnessed': 2 * len(rows),
        'archive_sha256': hashlib.sha256((CACHE / 'quest_stems.tar.gz').read_bytes()).hexdigest(),
        'dataset_sha256': hashlib.sha256(dataset.read_bytes()).hexdigest(),
        'model_calls': 0, 'gpu_hours': 0, 'world_modified': False, 'raw': str(a.out),
        'scope': 'Coverage diagnostic only; both source immediate goals prescribe giving, not a costly negotiation cohort.',
        'selection': 'minimum pair SHA per source world, before any new model outcomes'}
    (a.out / 'qualification.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__': main()
