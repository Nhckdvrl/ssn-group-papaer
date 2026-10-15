#!/usr/bin/env python3
"""E72 changes candidates only, sharing E70 dialogue and native trajectory engine."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import time
from native_rule_execution import configure, SharedPrefixClient, policy
from light_native_gate import parse_event
from light_npc_episodes import material_state
import native_request_precondition_execution as base
from native_matched_task_execution import decision_key

CONDITIONS = {direction+'_'+arm: ('equipped', direction, 'none', 'direct')
              for direction in ['aligned', 'divert'] for arm in ['valid_candidates', 'goal_candidates']}
DIRECTIVE = 'Choose your next game command from the candidates below. The native engine returns the actual result.'
ORIGINAL_SPEC = base.spec


def spec(game, stage, modules, graph=None, history=None):
    messages, schema = ORIGINAL_SPEC(game, stage, modules, graph, history)
    if stage != 'exec': return messages, schema
    actor = graph.get_node(game['case']['actor_id'])
    current = policy.base.legal_commands(graph, actor)
    candidates = sorted(set(current + ([game['case']['goal_command'], game['case']['request_command']]
                                      if game['condition'].endswith('goal_candidates') else [])))
    old = 'Choose your next legal game action.\n'+'\n'.join(current)
    assert messages[-1]['content'].count(old) == 1
    messages[-1]['content'] = messages[-1]['content'].replace(old, DIRECTIVE+'\n'+'\n'.join(candidates))
    schema = copy.deepcopy(schema); schema['properties']['action']['enum'] = candidates+['say']
    return messages, schema


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', type=Path)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--prior-runs', type=Path, nargs='*', default=[])
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--shards', type=int, default=1)
    ap.add_argument('--cpu-check', action='store_true')
    args = ap.parse_args(); configure(); base.CONDITIONS = CONDITIONS; base.spec = spec
    rows = list(map(json.loads, args.data.open())); assert len(rows) == 117
    modules = policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    if args.cpu_check:
        witnesses = []
        for row in rows:
            for direction in ['aligned', 'divert']:
                c = {**row['case'], **row['requests'][direction]}
                graph = modules[0].from_json(row['states']['equipped']); actor = graph.get_node(c['actor_id'])
                before = material_state(graph)
                e = parse_event(graph, actor, c['request_command'], *modules[1:])
                assert isinstance(e, modules[2])
                feedback = e.view_as(actor); assert 'remove' in feedback.lower()
                assert before == material_state(graph)
                witnesses.append({'case_id': c['case_id'], 'direction': direction, 'command': c['request_command'],
                                  'native_feedback': feedback, 'physical_state_unchanged': True})
        checks = 0
        for g in base.bases_for(rows):
            if not g['condition'].endswith('valid_candidates'): continue
            g['conversation'] = {'reply': 'I will consider the request.', 'stance': 'negotiate'}
            graph = modules[0].from_json(g['case']['quest']['graph'])
            a, sa = spec(g, 'exec', modules, graph, [])
            other = {**g, 'condition': g['condition'].replace('valid_candidates', 'goal_candidates')}
            b, sb = spec(other, 'exec', modules, graph, [])
            assert a[0] == b[0]
            current = policy.base.legal_commands(graph, graph.get_node(g['case']['actor_id']))
            expanded = sorted(set(current+[g['case']['goal_command'],g['case']['request_command']]))
            assert a[-1]['content'].replace(DIRECTIVE+'\n'+'\n'.join(current), 'CANDIDATES') == b[-1]['content'].replace(DIRECTIVE+'\n'+'\n'.join(expanded), 'CANDIDATES')
            assert set(sb['properties']['action']['enum']) == set(sa['properties']['action']['enum'])|{g['case']['goal_command'],g['case']['request_command']}
            checks += 1
        result = {'status': 'PASS', 'worlds': 117, 'native_feedback_witnesses': witnesses,
                  'paired_input_checks': checks, 'model_calls': 0}
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n'); print({'checks': checks, 'witnesses': len(witnesses)}); return
    assert args.model and args.prior_runs
    for folder in args.prior_runs:
        assert (folder/'runtime.json').exists()
        m = json.loads((folder/'manifest.json').read_text()); assert m['model'] == str(args.model)
    selected = rows[args.shard::args.shards]
    cached = {}
    for folder in args.prior_runs:
        for call in map(json.loads, (folder/'model_calls.jsonl').open()):
            if call['stage'] == 'conv': cached.setdefault(decision_key(call), call['parsed'])
    for g in base.bases_for(selected):
        conv = policy.base.job(g['case'], g['persona'], 'conv', spec(g, 'conv', modules), g['sampling_seed'])
        assert decision_key(conv) in cached, ('missing_exact_dialogue', g['case']['case_id'], g['seed'], g['persona'])
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {'experiment': 'E72', 'model': str(args.model), 'shard': args.shard, 'shards': args.shards,
                'case_ids': [r['case']['case_id'] for r in selected], 'conditions': CONDITIONS,
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'base_execution_sha256': hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(),
                'data_sha256': hashlib.sha256(args.data.read_bytes()).hexdigest(),
                'prior_runs': list(map(str, args.prior_runs)), 'new_cloud_calls': 0,
                'directive': DIRECTIVE, 'rules_modified': False, 'exact_dialogue_preflight_passed': True}
    (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    client = SharedPrefixClient(args.model, args.out, 7001)
    client.cache.update(cached)
    start = time.monotonic(); count = 0
    for group in [selected[:1]]+[selected[i:i+6] for i in range(1, len(selected), 6)]:
        count += base.run_group(group, client, modules, args.out)
        print(json.dumps({'episodes': count, 'calls': client.inner.calls, 'reused': client.reused,
                          'wall_seconds': time.monotonic()-start}), flush=True)
    assert count == len(selected)*24
    assert all(c['stage'] == 'exec' for c in map(json.loads,(args.out/'model_calls.jsonl').open()))
    runtime = {'episodes': count, 'calls': client.inner.calls, 'reused_calls': client.reused,
               'wall_seconds': time.monotonic()-start, 'model_load_seconds': client.inner.load_seconds,
               'new_cloud_calls': 0}
    (args.out/'runtime.json').write_text(json.dumps(runtime, indent=2)+'\n'); print(json.dumps(runtime), flush=True)


if __name__ == '__main__': main()
