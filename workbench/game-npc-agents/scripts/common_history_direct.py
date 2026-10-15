#!/usr/bin/env python3
"""E61: same observed prior speech, direct native policy, coherent identities."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
import commitment_decisions_v2 as base
from common_commitment_native import load_sources, cpu_replay
from commitment_snapshots import outcome
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, execute


def direct_spec(case, persona, speech, graph, history, modules):
    messages, structure = base.exec_spec(case, persona, {}, '00', graph, history, modules)
    marker = '\nChoose your next legal game action.'
    recording = ('\nRecorded prior speech from this encounter, before the recent game actions: '
                 + json.dumps(speech, ensure_ascii=False)
                 + '\nThe conversation phase is over. Speech itself executed no physical game action; '
                   'the current game observation and subsequent action feedback describe actual events.')
    assert messages[-1]['content'].count(marker) == 1
    messages[-1]['content'] = messages[-1]['content'].replace(marker, recording + marker)
    return messages, structure


def run_group(cases, rows, client, modules, out, seed):
    games = [{'case': c, 'persona': p, 'conversation': rows[c['case_id'], p]['fixed_conversation'],
              'graph': modules[0].from_json(c['quest']['graph']), 'history': [],
              'done': False, 'protocol_error': None} for c in cases for p in base.PERSONAS]
    for step in range(6):
        active = [g for g in games if not g['done']]
        if not active:
            break
        jobs = [base.job(g['case'], g['persona'], 'exec',
                    direct_spec(g['case'], g['persona'], g['conversation']['reply'],
                                g['graph'], g['history'], modules),
                    seed + int(g['case']['case_id'][:7], 16) * 10 + 10 + step, '00', step)
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
                'persona': g['persona'], 'seed': seed, 'condition': 'common_history_direct',
                'goal_kind': g['case']['goal_kind'], 'conversation': g['conversation'],
                'history': g['history'], 'flags': flags, 'steps': len(g['history']),
                'protocol_error': g['protocol_error']}, ensure_ascii=False) + '\n')
    return len(games)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=5801)
    args = ap.parse_args()
    manifest, cases, rows, natural, controls = load_sources(args.source)
    modules = load_event_modules(CACHE / 'sources/LIGHT')
    replay = cpu_replay(cases, controls, modules)
    assert replay['passed'] and args.seed == 5801
    args.out.mkdir(parents=True, exist_ok=False)
    report = {'source_manifest': manifest, 'source': str(args.source), 'natural_source': str(natural),
        'source_records_sha256': hashlib.sha256((args.source / 'records.jsonl').read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helpers_sha256': {n: hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                          for n in ['common_commitment_native.py', 'commitment_decisions_v2.py', 'commitment_snapshots.py']},
        'case_ids': [c['case_id'] for c in cases], 'all_stages_coherent': True,
        'updated_plan_or_memory_fed_to_policy': False, 'factual_answers_fed_to_policy': False,
        'world_modified': False, 'cloud_calls': 0, 'new_writer_calls': 0, 'seed': args.seed}
    (args.out / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (args.out / 'cpu_replay.json').write_text(json.dumps(replay, ensure_ascii=False, indent=2) + '\n')
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
    client = base.BatchClient(Path(manifest['arguments']['model']), args.out, args.seed)
    start = time.monotonic()
    count = 0
    for cs in [cases[:1]] + [cases[i:i+10] for i in range(1, len(cases), 10)]:
        count += run_group(cs, rows, client, modules, args.out, args.seed)
        print(json.dumps({'branches': count, 'calls': client.calls,
                          'wall_seconds': time.monotonic()-start}), flush=True)
    assert count == 400
    (args.out / 'runtime.json').write_text(json.dumps({'graphs': 200, 'branches': count,
        'calls': client.calls, 'wall_seconds': time.monotonic()-start,
        'model_load_seconds': client.load_seconds, 'cloud_calls': 0}, indent=2) + '\n')


if __name__ == '__main__':
    main()
