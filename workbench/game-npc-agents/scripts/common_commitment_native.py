#!/usr/bin/env python3
"""E60: native execution of complete E59 fixed-utterance plans; no new writer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time

import commitment_decisions_v2 as base
from commitment_snapshots import outcome
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, execute


def load_sources(source):
    manifest = json.loads((source / 'manifest.json').read_text())
    assert (source / 'runtime.json').exists(), 'Complete and freeze all source rows first'
    rows = list(map(json.loads, (source / 'records.jsonl').read_text().splitlines()))
    cases = list(map(json.loads, Path(manifest['arguments']['dataset']).read_text().splitlines()))
    assert len(cases) == len({c['graph_sha256'] for c in cases}) == 200
    assert manifest['dataset_sha256'] == hashlib.sha256(Path(manifest['arguments']['dataset']).read_bytes()).hexdigest()
    lookup = {(r['case_id'], r['persona']): r for r in rows}
    assert len(lookup) == len(rows) == 400
    assert set(lookup) == {(c['case_id'], p) for c in cases for p in base.PERSONAS}
    assert all(r['update'] is not None for r in rows), 'Preserve source failures; never invent plans'
    assert manifest['personas'] == base.PERSONAS
    natural = Path(manifest['arguments']['source'])
    assert (natural / 'runtime.json').exists()
    controls = [r for r in map(json.loads, (natural / 'branches.jsonl').read_text().splitlines())
                if r['persona'].startswith('full_') and r['condition'] == 'plan_grounded']
    assert len(controls) == 400
    return manifest, cases, lookup, natural, controls


def cpu_replay(cases, controls, modules):
    by_id = {c['case_id']: c for c in cases}
    failures = []
    for original in controls:
        case = by_id[original['case_id']]
        graph = modules[0].from_json(case['quest']['graph'])
        history = []
        for step, past in enumerate(original['history']):
            random.seed(original['seed'] + int(case['case_id'][:7], 16) * 10 + 100 + step)
            row = execute(ViewerHost(graph), graph.get_node(case['actor_id']), past['command'], *modules[1:])
            row['choice'] = past['choice']
            history.append(row)
        actual = outcome(graph, case, history)
        if actual != original['flags']:
            failures.append({'case_id': case['case_id'], 'persona': original['persona'],
                             'expected': original['flags'], 'actual': actual})
    return {'branches': len(controls), 'mismatches': failures, 'passed': not failures,
            'new_model_calls': 0, 'world_rules_modified': False}


def run_group(cases, rows, client, modules, out, seed):
    games = []
    for case in cases:
        for persona in base.PERSONAS:
            row = rows[case['case_id'], persona]
            games.append({'case': case, 'persona': persona, 'update': row['update'],
                          'fixed_conversation': row['fixed_conversation'],
                          'graph': modules[0].from_json(case['quest']['graph']),
                          'history': [], 'done': False, 'protocol_error': None})
    for step in range(6):
        active = [g for g in games if not g['done']]
        if not active:
            break
        jobs = [base.job(g['case'], g['persona'], 'exec',
                    base.exec_spec(g['case'], g['persona'], g['update'], '11',
                                   g['graph'], g['history'], modules),
                    seed + int(g['case']['case_id'][:7], 16) * 10 + 10 + step, '11', step)
                for g in active]
        for g, answer in zip(active, client.batch(jobs)):
            if answer is None:
                g['done'], g['protocol_error'] = True, 'invalid_exec_json'
                continue
            command = ('say ' + answer['utterance'] if answer['action'] == 'say'
                       else answer['action'].replace('<SOMETHING>', answer['utterance']))
            random.seed(seed + int(g['case']['case_id'][:7], 16) * 10 + 100 + step)
            row = execute(ViewerHost(g['graph']), g['graph'].get_node(g['case']['actor_id']), command, *modules[1:])
            row['choice'] = answer
            g['history'].append(row)
            flags = outcome(g['graph'], g['case'], g['history'])
            g['done'] = bool(flags['own_task'] or flags['request']
                or g['graph'].get_node(g['case']['item_id']).get_container().node_id != g['case']['actor_id'])
    with (out / 'branches.jsonl').open('a') as f:
        for g in games:
            flags = outcome(g['graph'], g['case'], g['history'])
            assert not (flags['own_task'] and flags['request'])
            f.write(json.dumps({'case_id': g['case']['case_id'], 'graph_sha256': g['case']['graph_sha256'],
                'persona': g['persona'], 'seed': seed, 'condition': 'fixed_future_plan',
                'goal_kind': g['case']['goal_kind'], 'conversation': g['fixed_conversation'],
                'update': g['update'], 'history': g['history'], 'flags': flags,
                'steps': len(g['history']), 'protocol_error': g['protocol_error']}, ensure_ascii=False) + '\n')
    return len(games)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=5801)
    ap.add_argument('--cpu-check', action='store_true')
    args = ap.parse_args()
    manifest, cases, rows, natural, controls = load_sources(args.source)
    modules = load_event_modules(CACHE / 'sources/LIGHT')
    replay = cpu_replay(cases, controls, modules)
    if args.cpu_check:
        args.out.write_text(json.dumps(replay, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(replay, ensure_ascii=False))
        return
    assert replay['passed'], 'Stop on adapter mismatch; never fix game rules or filter cases'
    assert args.seed == 5801, 'Registered comparison pairs the E58 execution seed'
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'cpu_replay.json').write_text(json.dumps(replay, ensure_ascii=False, indent=2) + '\n')
    new_manifest = {'source': str(args.source), 'natural_source': str(natural), 'source_manifest': manifest,
        'source_records_sha256': hashlib.sha256((args.source / 'records.jsonl').read_bytes()).hexdigest(),
        'natural_branches_sha256': hashlib.sha256((natural / 'branches.jsonl').read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helper_sha256': {n: hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                          for n in ['commitment_decisions_v2.py', 'commitment_snapshots.py', 'light_npc_episodes.py']},
        'case_ids': [c['case_id'] for c in cases], 'seed': args.seed, 'conditions': ['fixed_future_plan'],
        'max_steps': 6, 'all_stages_coherent': True, 'world_modified': False,
        'factual_answers_fed_to_policy': False, 'text_labels_fed_to_policy': False,
        'cloud_calls': 0, 'new_writer_calls': 0}
    (args.out / 'manifest.json').write_text(json.dumps(new_manifest, ensure_ascii=False, indent=2) + '\n')
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
    client = base.BatchClient(Path(manifest['arguments']['model']), args.out, args.seed)
    start = time.monotonic()
    count = 0
    for cs in [cases[:1]] + [cases[i:i+10] for i in range(1, len(cases), 10)]:
        count += run_group(cs, rows, client, modules, args.out, args.seed)
        print(json.dumps({'branches': count, 'calls': client.calls, 'wall_seconds': time.monotonic()-start}), flush=True)
    assert count == 400
    (args.out / 'runtime.json').write_text(json.dumps({'graphs': 200, 'branches': count,
        'calls': client.calls, 'wall_seconds': time.monotonic()-start,
        'model_load_seconds': client.load_seconds, 'cloud_calls': 0}, indent=2) + '\n')


if __name__ == '__main__':
    main()
