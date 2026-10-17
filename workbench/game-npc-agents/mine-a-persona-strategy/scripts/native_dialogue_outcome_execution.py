#!/usr/bin/env python3
"""E77: exact dialogue crossover and symmetric outcome instructions, native actions."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import time

import native_retrieval_execution as base
from native_rule_execution import configure, SharedPrefixClient, policy
from native_matched_task_execution import decision_key

ORIGINAL_SPEC = base.spec
ORIGINAL_BASES = base.bases_for
CONDITIONS = {
    'dialogue_firm': ('firm', None),
    'dialogue_agreeable': ('agreeable', None),
    'assigned_goal': (None, 'goal'),
    'assigned_request': (None, 'request'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def donor(case_id, seed):
    bit = hashlib.sha256(f'E77-donor:{case_id}:{seed}'.encode()).digest()[0] % 2
    return ['firm', 'agreeable'][bit]


def bases(rows):
    games = ORIGINAL_BASES(rows)
    for g in games:
        source, target = CONDITIONS[g['condition']]
        g['conv_persona'] = source or donor(g['case']['case_id'], g['seed'])
        g['assigned_outcome'] = target
    return games


def target_text(game, modules):
    c = game['case']
    graph = modules[0].from_json(c['quest']['graph'])
    item = graph.get_node(c['item_id']).get_prefix_view()
    if game['assigned_outcome'] == 'request' or c['goal_kind'] == 'give':
        recipient = c['requester_id'] if game['assigned_outcome'] == 'request' else c['original_recipient']
        peer = graph.get_node(recipient).get_prefix_view()
        return f'{item} has been transferred from you to {peer}.'
    return {
        'wear': f'You are wearing {item}.',
        'eat': f'You have consumed {item} as food.',
        'drink': f'You have consumed {item} as a drink.',
    }[c['goal_kind']]


def spec(game, stage, modules, graph=None, history=None):
    source = game
    if stage == 'conv':
        source = {**game, 'persona': game['conv_persona']}
    messages, schema = ORIGINAL_SPEC(source, stage, modules, graph, history)
    if stage == 'exec' and game['assigned_outcome'] is not None:
        messages[-1]['content'] += (
            '\nFor this continuation, work toward this assigned physical outcome: '
            + target_text(game, modules)
            + ' This statement specifies a target; it does not record a completed action.'
        )
    return messages, schema


def load_cache(folders, model=None):
    cache, hashes = {}, {}
    for folder in folders:
        assert (folder / 'runtime.json').exists()
        manifest = json.loads((folder / 'manifest.json').read_text())
        if model is not None:
            assert manifest['model'] == str(model)
        path = folder / 'model_calls.jsonl'
        for r in map(json.loads, path.open()):
            cache.setdefault(decision_key(r), r['parsed'])
        hashes[str(path)] = sha(path)
    return cache, hashes


def cpu_check(rows, modules, cache):
    checked, diagonals, outcomes = 0, 0, 0
    balanced = {'firm': 0, 'agreeable': 0}
    for r in rows:
        for seed in base.SEEDS:
            balanced[donor(r['case']['case_id'], seed)] += 1
    for g in bases(rows):
        conv_job = policy.base.job(g['case'], g['persona'], 'conv', spec(g, 'conv', modules), g['sampling_seed'])
        key = decision_key(conv_job)
        assert key in cache and cache[key] is not None
        original = {**g, 'persona': g['conv_persona']}
        assert spec(g, 'conv', modules) == ORIGINAL_SPEC(original, 'conv', modules)
        g['conversation'] = cache[key]
        graph = modules[0].from_json(g['case']['quest']['graph'])
        m, schema = spec(g, 'exec', modules, graph, [])
        m0, schema0 = ORIGINAL_SPEC(g, 'exec', modules, graph, [])
        assert schema == schema0 and m[0] == m0[0]
        assert policy.TRAITS[g['persona']] in m[0]['content']
        assert g['case']['quest']['persona'] in m[0]['content']
        assert g['conversation']['reply'] in m[-1]['content']
        if g['assigned_outcome'] is None:
            assert m == m0
            if g['conv_persona'] == g['persona']:
                first = policy.base.job(g['case'], g['persona'], 'exec', (m, schema), g['sampling_seed']+10, None, 0)
                assert decision_key(first) in cache
                diagonals += 1
        else:
            assert m[-1]['content'].startswith(m0[-1]['content'])
            assert 'get ' not in target_text(g, modules).lower()
            assert 'remove ' not in target_text(g, modules).lower()
            outcomes += 1
        checked += 1
    return {'status': 'PASS', 'worlds': len(rows), 'input_checks': checked,
            'exact_old_diagonal_first_steps': diagonals, 'outcome_only_checks': outcomes,
            'balanced_donor_world_seed_counts': balanced, 'model_calls': 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--prior-runs', type=Path, nargs='+', required=True)
    ap.add_argument('--profile', action='store_true')
    ap.add_argument('--cpu-check', action='store_true')
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--shards', type=int, default=1)
    a = ap.parse_args()
    configure()
    assert os.environ.get('PYTHONHASHSEED') == '0'
    rows = list(map(json.loads, a.data.open()))
    assert len(rows) == 102
    base.CONDITIONS = {c: ('retrieval', 'baseline') for c in CONDITIONS}
    base.bases_for, base.spec = bases, spec
    modules = policy.load_event_modules(policy.CACHE / 'sources/LIGHT')
    cache, hashes = load_cache(a.prior_runs, a.model)
    controls = cpu_check(rows, modules, cache)
    if a.cpu_check:
        controls.update(script_sha256=sha(Path(__file__)), data_sha256=sha(a.data))
        a.out.write_text(json.dumps(controls, indent=2)+'\n')
        print(json.dumps(controls))
        return
    assert a.model is not None
    selected = rows[:1] if a.profile else rows[a.shard::a.shards]
    a.out.mkdir(parents=True, exist_ok=False)
    (a.out / 'model_calls.jsonl').touch()
    manifest = {'experiment': 'E77', 'model': str(a.model), 'profile': a.profile,
        'shard': a.shard, 'shards': a.shards, 'worlds': len(selected),
        'case_ids': [r['case']['case_id'] for r in selected], 'seeds': base.SEEDS,
        'conditions': CONDITIONS, 'state': 'original_retrieval',
        'donor_rule': 'SHA256(E77-donor:case_id:seed) first byte parity; shared across exec traits.',
        'all_input_controls': controls, 'data_sha256': sha(a.data),
        'script_sha256': sha(Path(__file__)), 'base_driver_sha256': sha(Path(base.__file__)),
        'prior_renderer_sha256': sha(Path(base.prior.__file__)),
        'prior_model_calls_sha256': hashes, 'personas': policy.TRAITS,
        'rules_modified': False, 'new_cloud_calls': 0, 'scripted_agent_actions': 0,
        'stage_intervention_not_full_persona_change': True,
        'assigned_outcomes_are_external_instructions_not_observed_choices': True,
        'max_actions': 8}
    (a.out / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    client = SharedPrefixClient(a.model, a.out, 7501)
    client.cache.update(cache)
    started, count = time.monotonic(), 0
    for chunk in [selected[:1]] + [selected[i:i+4] for i in range(1, len(selected), 4)]:
        count += base.run_group(chunk, client, modules, a.out)
        print(json.dumps({'episodes': count, 'calls': client.inner.calls, 'reused': client.reused,
                         'seconds': time.monotonic()-started}), flush=True)
    assert count == len(selected) * 24
    assert all(r['stage'] == 'exec' for r in map(json.loads, (a.out / 'model_calls.jsonl').open()))
    runtime = {'worlds': len(selected), 'episodes': count, 'calls': client.inner.calls,
        'reused_calls': client.reused, 'new_conversation_calls': 0,
        'wall_seconds': time.monotonic()-started, 'model_load_seconds': client.inner.load_seconds,
        'new_cloud_calls': 0}
    (a.out / 'runtime.json').write_text(json.dumps(runtime, indent=2)+'\n')
    print(json.dumps(runtime), flush=True)


if __name__ == '__main__':
    main()
