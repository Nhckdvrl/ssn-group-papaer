#!/usr/bin/env python3
"""E58 coherent role packages: traits, value priorities and their original combination."""
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

ORIGINAL = dict(base.PERSONAS)
PACKAGES = {}
for direction, text in ORIGINAL.items():
    first, second = text.split('. ', 1)
    PACKAGES['full_' + direction] = text
    PACKAGES['traits_' + direction] = first + '.'
    PACKAGES['priority_' + direction] = second
GROUNDING = ('Dialogue expresses intentions, and no physical game action has occurred yet; '
             'only actually executed game events can mark either task as completed, so record '
             'intentions separately from performed actions.')


def run(cases, seed, client, modules, out):
    bases = [{'case': c, 'persona': p, 'sampling_seed': seed + int(c['case_id'][:7], 16) * 10}
             for c in cases for p in PACKAGES]
    jobs = [base.job(b['case'], b['persona'], 'expression',
        (base.pack_messages(b['case'], b['persona'], 'Introduce yourself and say what you value in two sentences.'),
         base.schema({'self_description': {'type': 'string'}})), b['sampling_seed'] + 2) for b in bases]
    expressions = client.batch(jobs)
    with (out / 'expression.jsonl').open('a') as f:
        for b, answer in zip(bases, expressions):
            f.write(json.dumps({'case_id': b['case']['case_id'], 'persona': b['persona'],
                                'seed': seed, 'expression': answer, 'separate_session': True}, ensure_ascii=False) + '\n')
    answers = client.batch([base.job(b['case'], b['persona'], 'conv', base.conv_spec(b['case'], b['persona'], modules),
                                    b['sampling_seed']) for b in bases])
    for b, answer in zip(bases, answers): b['conversation'] = answer
    jobs, slots = [], []
    for b in bases:
        if b['conversation'] is None: continue
        messages, structure = base.update_spec(b['case'], b['persona'], b['conversation'], modules)
        messages[-1]['content'] += '\n' + GROUNDING
        jobs.append(base.job(b['case'], b['persona'], 'update', (messages, structure), b['sampling_seed'] + 1)); slots.append(b)
    for b, answer in zip(slots, client.batch(jobs) if jobs else []): b['update'] = answer
    with (out / 'stage_outputs.jsonl').open('a') as f:
        for b in bases:
            f.write(json.dumps({**{k: v for k, v in b.items() if k != 'case'},
                               'case_id': b['case']['case_id'], 'seed': seed}, ensure_ascii=False) + '\n')
    games = []
    for b in bases:
        for kind in ['direct', 'plan_grounded']:
            error = None
            if kind == 'plan_grounded':
                if b['conversation'] is None: error = 'invalid_conversation'
                elif b.get('update') is None: error = 'invalid_update'
            games.append({**b, 'condition': kind, 'graph': modules[0].from_json(b['case']['quest']['graph']),
                          'history': [], 'done': bool(error), 'protocol_error': error})
    for step in range(6):
        active = [g for g in games if not g['done']]
        if not active: break
        jobs = [base.job(g['case'], g['persona'], 'exec',
                    base.exec_spec(g['case'], g['persona'], g.get('update') or {},
                                   '11' if g['condition'] == 'plan_grounded' else '00', g['graph'], g['history'], modules),
                    g['sampling_seed'] + 10 + step, None, step) | {'condition': g['condition']} for g in active]
        for g, answer in zip(active, client.batch(jobs)):
            if answer is None: g['done'], g['protocol_error'] = True, 'invalid_exec_json'; continue
            command = 'say ' + answer['utterance'] if answer['action'] == 'say' else answer['action'].replace('<SOMETHING>', answer['utterance'])
            random.seed(g['sampling_seed'] + 100 + step)
            row = execute(ViewerHost(g['graph']), g['graph'].get_node(g['case']['actor_id']), command, *modules[1:])
            row['choice'] = answer; g['history'].append(row)
            flags = outcome(g['graph'], g['case'], g['history'])
            g['done'] = bool(flags['own_task'] or flags['request'] or g['graph'].get_node(g['case']['item_id']).get_container().node_id != g['case']['actor_id'])
    with (out / 'branches.jsonl').open('a') as f:
        for g in games:
            flags = outcome(g['graph'], g['case'], g['history']); assert not (flags['own_task'] and flags['request'])
            f.write(json.dumps({'case_id': g['case']['case_id'], 'graph_sha256': g['case']['graph_sha256'],
                'persona': g['persona'], 'seed': seed, 'condition': g['condition'], 'goal_kind': g['case']['goal_kind'],
                'conversation': g['conversation'], 'update': g.get('update'), 'history': g['history'],
                'flags': flags, 'steps': len(g['history']), 'protocol_error': g['protocol_error']}, ensure_ascii=False) + '\n')
    return len(games)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=5801); a = ap.parse_args()
    cases = list(map(json.loads, a.dataset.read_text().splitlines()))
    assert len(cases) == len({c['graph_sha256'] for c in cases}) == 200
    # Process-local configuration shared by every stage, never rewrite a running helper file.
    base.PERSONAS.clear(); base.PERSONAS.update(PACKAGES)
    a.out.mkdir(parents=True, exist_ok=False)
    manifest = {'arguments': {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()},
        'case_ids': [c['case_id'] for c in cases], 'personas': PACKAGES, 'conditions': ['direct', 'plan_grounded'],
        'dataset_sha256': hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'helpers_sha256': {n: hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                           for n in ['commitment_decisions_v2.py', 'commitment_snapshots.py', 'light_npc_episodes.py']},
        'all_stages_coherent': True, 'previous_package_dialogue_reused': False,
        'world_modified': False, 'cloud_calls': 0, 'grounding': GROUNDING}
    (a.out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
    modules = load_event_modules(CACHE / 'sources/LIGHT'); client = base.BatchClient(a.model, a.out, a.seed)
    start = time.monotonic(); count = 0
    for cs in [cases[:1]] + [cases[i:i+10] for i in range(1, len(cases), 10)]:
        count += run(cs, a.seed, client, modules, a.out)
        print(json.dumps({'branches': count, 'calls': client.calls, 'wall_seconds': time.monotonic()-start}), flush=True)
    assert count == 2400
    (a.out / 'runtime.json').write_text(json.dumps({'graphs': 200, 'branches': count, 'calls': client.calls,
        'wall_seconds': time.monotonic()-start, 'model_load_seconds': client.load_seconds, 'cloud_calls': 0}, indent=2) + '\n')


if __name__ == '__main__': main()
