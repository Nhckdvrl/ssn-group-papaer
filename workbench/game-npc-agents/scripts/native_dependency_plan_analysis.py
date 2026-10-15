#!/usr/bin/env python3
"""POST-HOC E63 native plan feasibility vs actual execution, no semantic judge."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import numpy as np
from commitment_behavior_report import estimate
from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, execute


def analyze(row, source, modules):
    case = source['case']; graph = modules[0].from_json(case['quest']['graph'])
    actor = graph.get_node(case['actor_id'])
    goal = parse_event(graph, actor, case['goal_command'], *modules[1:])
    assert not isinstance(goal, modules[2])
    goal_canonical = goal.to_canonical_form()
    plan = (row.get('update') or {}).get('priority_actions', [])
    planned_goal = False; planned_request = False; initial_rejections = 0
    for command in plan:
        event = parse_event(graph, actor, command, *modules[1:])
        if isinstance(event, modules[2]):
            initial_rejections += 1; continue
        planned_goal |= event.to_canonical_form() == goal_canonical
        planned_request |= (type(event).__name__ == 'GiveObjectEvent'
            and event.target_nodes[0].node_id == row['request_item_id']
            and event.target_nodes[1].node_id == case['requester_id'])
    replay_goal = False; replay_rejections = 0; stochastic = 0; actions = []
    for step, command in enumerate(plan):
        event = parse_event(graph, actor, command, *modules[1:])
        current_goal = parse_event(graph, actor, case['goal_command'], *modules[1:])
        is_goal = (not isinstance(event, modules[2]) and not isinstance(current_goal, modules[2])
                   and event.to_canonical_form() == current_goal.to_canonical_form())
        random.seed(row['seed'] + int(row['case_id'][:7], 16)*10 + 100 + step)
        result = execute(ViewerHost(graph), actor, command, *modules[1:])
        success = result['legal'] and result.get('executed') and not result.get('stochastic_failure')
        replay_goal |= bool(is_goal and success)
        replay_rejections += not result['legal']; stochastic += bool(result.get('stochastic_failure'))
        actions.append({k: result.get(k) for k in ['command', 'legal', 'executed', 'stochastic_failure', 'event_type']})
    observed = bool(row['goal_executed'])
    values = {'planned_original_goal': float(planned_goal), 'planned_requested_transfer': float(planned_request),
        'actual_goal': float(observed), 'actual_request': float(row['request_given']),
        'planned_goal_but_no_actual_goal': float(planned_goal and not observed),
        'replay_goal_executed': float(replay_goal),
        'replay_goal_but_no_actual_goal': float(replay_goal and not observed),
        'initial_plan_has_illegal_action': float(initial_rejections > 0),
        'sequential_plan_has_illegal_action': float(replay_rejections > 0),
        'sequential_plan_stochastic_failure': float(stochastic > 0),
        'actual_all_actions_without_material_change': float(bool(row['history']) and all(not h['material_changed'] for h in row['history'])),
        'protocol_error': float(bool(row['protocol_error']))}
    return values, actions


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--directories', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True); ap.add_argument('--partial', action='store_true')
    a = ap.parse_args(); manifests = [json.loads((d/'manifest.json').read_text()) for d in a.directories]
    ref = manifests[0]
    for m in manifests:
        for key in ['dataset_sha256', 'script_sha256', 'personas', 'rules']: assert m[key] == ref[key]
        assert m['arguments']['model'] == ref['arguments']['model']
    sources = {r['case']['case_id']: r for r in map(json.loads, Path(ref['arguments']['dataset']).read_text().splitlines())}
    rows = []
    for d in a.directories:
        if not a.partial:
            assert (d/'runtime.json').exists() or (d/'interrupted_runtime.json').exists()
            if (d/'interrupted_runtime.json').exists():
                ck = json.loads((d/'interrupted_runtime.json').read_text())
                assert hashlib.sha256((d/'episodes.jsonl').read_bytes()).hexdigest() == ck['episodes_sha256']
        rows.extend(map(json.loads, (d/'episodes.jsonl').read_text().splitlines()))
    keys = [(r['case_id'], r['seed'], r['persona'], r['rule'], r['mode']) for r in rows]
    assert len(keys) == len(set(keys))
    if not a.partial:
        expected = {(cid, s, p, rule, mode) for cid, source in sources.items()
                    for s in ref['arguments']['seeds'] for p in ref['personas']
                    for rule in ref['rules'] for mode in source['requests']}
        assert set(keys) == expected
    modules = load_event_modules(CACHE/'sources/LIGHT'); results = []; groups = defaultdict(list)
    for row in rows:
        values, replay = analyze(row, sources[row['case_id']], modules)
        key = tuple(row[k] for k in ['case_id', 'seed', 'persona', 'rule', 'mode'])
        verb = row['goal_kind']
        results.append({'key': key, 'source_goal_verb': verb, 'values': values, 'plan_replay': replay})
        groups[(row['mode'], row['rule'], row['persona'], 'all')].append((row['case_id'], values))
        groups[(row['mode'], row['rule'], row['persona'], verb)].append((row['case_id'], values))
    cells = {}
    for key, pairs in groups.items():
        points = defaultdict(list)
        for cid, values in pairs: points[cid].append(values)
        cells['/'.join(key)] = {f: estimate([np.mean([v[f] for v in vs]) for vs in points.values()])
                                for f in pairs[0][1]}
    a.out.mkdir(parents=True, exist_ok=False)
    (a.out/'plan_replays.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in results))
    report = {'analysis': 'POST-HOC', 'status': 'PARTIAL' if a.partial else 'COMPLETE',
        'worlds': len({r['case_id'] for r in rows}), 'episodes': len(rows), 'cells': cells,
        'source_goal_verbs': dict(Counter(r['goal_kind'] for r in rows)),
        'model_calls': 0, 'gpu_hours': 0, 'world_modified': False,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': ['Plan commands are native actions, not semantic labels on reasons or intentions.',
          'Replay executes listed priorities in order; the actual policy is free to revise its choice each step.',
          'A feasible listed plan followed by nonexecution is not proof of a circuit or capability failure.',
          'Rows with protocol errors remain; source verb strata are exploratory and not randomized.']}
    (a.out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['analysis', 'status', 'worlds', 'episodes', 'source_goal_verbs', 'model_calls']}))


if __name__ == '__main__': main()
