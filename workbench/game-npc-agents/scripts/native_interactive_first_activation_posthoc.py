#!/usr/bin/env python3
"""POST-HOC E80 first common two-step choice, using completed raw runs only.

Design fixed after both two-world profiles and before full results completed.
The all-world E80 endpoints are unchanged. This is a conditional same-prefix
implementation readback, not a cross-persona capability or human-value test.
No model/API call, new world, or live-game modification occurs.

  env PYTHONHASHSEED=0 PYTHONPATH=/home/xiang/.cache/game-npc-research/deps \
    OPENBLAS_NUM_THREADS=1 /home/xiang/miniconda3/envs/fgvd/bin/python \
    workbench/game-npc-agents/scripts/native_interactive_first_activation_posthoc.py \
    --runs MODEL_RUNS_AND_PROFILES... --out REPORT.json [--profile]
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import random

import numpy as np

from native_interactive_report import (
    ALIASES, BACKENDS, PERSONAS, SEEDS, SPEECH, decision_key, event_readback,
    load_sources, read_runs, sha, success,
)

BOOTSTRAPS = 4000
BOOTSTRAP_SEED = 808001
PROJECTION = ['actor', 'role', 'turn', 'command', 'event_type', 'target_node_ids',
              'legal', 'executed', 'stochastic_failure', 'error', 'before', 'after',
              'messages', 'material_changed']
CATEGORIES = ['expected_prerequisite_success', 'expected_prerequisite_failed',
              'other_legal_speech', 'other_legal_action', 'other_rejected_or_failed',
              'protocol_failure_no_primitive']


def native_projection(turn):
    # Explicitly exclude lower-decision metadata and the implementation arm.
    return {field: turn.get(field) for field in PROJECTION}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def add_visible(visible, turn, row):
    for role, viewer in [('npc', row['actor_id']), ('player', row['requester_id'])]:
        seen = [m['text'] for m in turn['messages'] if m['viewer'] == viewer]
        if role == turn['role']:
            seen.insert(0, 'Your attempted command: ' + turn['command'])
            if turn.get('error'):
                seen.append('Native rejection: ' + turn['error'])
        visible[role].extend(seen)


def expected_success(turn, expected):
    if not success(turn) or [turn['event_type'], turn['target_node_ids']] != expected:
        return False
    sid = expected[1][0]
    before, after = turn['before'][sid], turn['after'][sid]
    if expected[0] == 'GetObjectEvent':
        assert len(expected[1]) == 2 and before['container'] == expected[1][1]
        assert after['container'] == turn['actor']
    else:
        assert expected == ['RemoveObjectEvent', [sid]]
        assert before['container'] == after['container'] == turn['actor']
        assert before.get('equipped') and not after.get('equipped')
    return True


def classify(turn, expected):
    identity = [turn['event_type'], turn['target_node_ids']]
    if identity == expected:
        return 'expected_prerequisite_success' if expected_success(turn, expected) else 'expected_prerequisite_failed'
    if success(turn):
        return 'other_legal_speech' if turn['event_type'] in SPEECH else 'other_legal_action'
    return 'other_rejected_or_failed'


def replay_prefix_and_witness(case, row, prefix, selected, expected_before, modules):
    """CPU-native witness from the original graph, without editing any world."""
    from light_native_gate import parse_event
    from light_npc_episodes import ViewerHost, execute, material_state
    from native_owned_container_qualification import event_id
    from native_interactive_skills import native_short_path
    graph = modules[0].from_json(case['quest']['graph'])
    host = ViewerHost(graph)
    for turn in [row['opening'], *prefix]:
        actor = graph.get_node(turn['actor'])
        ident = event_id(parse_event(graph, actor, turn['command'], *modules[1:]), modules)
        assert (list(ident[1]) if ident else []) == turn['target_node_ids']
        random.seed(row['seed'] + int(row['case_id'][:7], 16)*1000 + turn['turn'] + 1000)
        actual = execute(host, actor, turn['command'], *modules[1:])
        for field in actual:
            assert actual[field] == turn[field], ('Prefix replay differs', row['case_id'], turn['turn'], field)
    assert material_state(graph) == expected_before
    original_json = graph.to_json()
    path = native_short_path(graph, case, selected, modules)
    assert path and len(path) == 2 and graph.to_json() == original_json
    witnesses = []
    fork = modules[0].from_json(original_json)
    for command in path:
        actor = fork.get_node(case['actor_id'])
        ident = event_id(parse_event(fork, actor, command, *modules[1:]), modules)
        assert ident is not None
        identity = [ident[0], list(ident[1])]
        actual = execute(ViewerHost(fork), actor, command, *modules[1:])
        assert success(actual) and actual['material_changed']
        actual['target_node_ids'] = identity[1]
        witnesses.append({'command': command, 'identity': identity,
                          'source_before': actual['before'][case['item_id']],
                          'source_after': actual['after'][case['item_id']]})
        if len(witnesses) == 1:
            assert identity[0] in ['GetObjectEvent', 'RemoveObjectEvent'] and identity[1][0] == case['item_id']
            assert expected_success(actual, identity)
    assert witnesses[1]['identity'] == case['native_target_identities'][selected]
    assert graph.to_json() == original_json
    return path, witnesses


def pair_readback(case, left, right, calls, jobs, modules):
    assert left['backend'] == 'model_steps' and right['backend'] == 'native_skill'
    assert left['initial_state'] == right['initial_state'] == case['initial_state']
    assert native_projection(left['opening']) == native_projection(right['opening'])
    visible = [{'npc': [], 'player': []}, {'npc': [], 'player': []}]
    add_visible(visible[0], left['opening'], left)
    add_visible(visible[1], right['opening'], right)
    record = {'case_id': case['case_id'], 'graph_sha256': case['graph_sha256'],
              'goal_kind': case['goal_kind'], 'persona': left['persona'], 'seed': left['seed'],
              'activated': False, 'common_prefix_native_turns': 0,
              'common_prefix_including_opening_checks': 1}
    max_turns = max(len(left['turns']), len(right['turns']))
    for i in range(max_turns):
        assert i < len(right['turns']), ('Pre-activation skill stop diverges', record)
        a = left['turns'][i] if i < len(left['turns']) else None
        b = right['turns'][i]
        if a is None:
            # A failed lower JSON has no executed turn, but the shared
            # high-level two-step choice still defines this first activation.
            assert left['protocol_error'] == 'invalid_npc_primitive_json' and i == len(left['turns'])
            assert b['role'] == 'npc' and b['path_length'] == 2
        before = a['before'] if a else left['final_state']
        assert before == b['before'] and visible[0] == visible[1]
        assert b['turn'] == i
        if a:
            assert a['role'] == b['role'] and a['turn'] == i
        stage = 'npc_choice' if b['role'] == 'npc' else 'player'
        jk = lambda backend: (case['case_id'], left['seed'], left['persona'], backend, stage, i)
        assert jobs[jk('model_steps')] == jobs[jk('native_skill')], ('Pre-activation policy input diverges', record, i)
        common_key = jobs[jk('model_steps')]
        assert b['decision'] == calls[common_key]['parsed']
        if a:
            assert a['decision'] == b['decision']
            assert a['selected_target'] == b['selected_target'] and a['path_length'] == b['path_length']
        if b['path_length'] == 2:
            assert b['role'] == 'npc' and b['selected_target'] in ['goal', 'request']
            assert ALIASES[b['decision']['action']] == b['selected_target']
            assert (a is None or a['lower_decision'] is not None) and b['lower_decision'] is None
            path, witness = replay_prefix_and_witness(case, left, left['turns'][:i],
                b['selected_target'], before, modules)
            expected = witness[0]['identity']
            assert b['command'] == path[0] and expected_success(b, expected)
            lower_job = (case['case_id'], left['seed'], left['persona'], 'model_steps', 'npc_primitive', i)
            lower = calls[jobs[lower_job]]
            assert (a['lower_decision'] if a else None) == lower['parsed']
            from light_npc_episodes import chosen_command
            if a:
                assert chosen_command(lower['parsed']) == a['command']
            category = classify(a, expected) if a else 'protocol_failure_no_primitive'
            record.update(activated=True, activation_turn=i, selected_target=b['selected_target'],
                common_selector_decision_key=common_key, common_before_state_sha256=digest(before),
                common_visible_history_sha256=digest(visible[0]), native_two_primitive_witness=witness,
                model_lower_decision_key=jobs[lower_job], model_primitive_command=a['command'] if a else None,
                model_primitive_identity=[a['event_type'], a['target_node_ids']] if a else None,
                model_primitive_category=category,
                model_command_equals_witness=bool(a and a['command'] == path[0]),
                model_identity_equals_witness=bool(a and [a['event_type'], a['target_node_ids']] == expected),
                model_expected_prerequisite_success=bool(a and expected_success(a, expected)),
                model_primitive_legal=bool(a and a['legal']), model_primitive_executed=bool(a and a.get('executed')),
                model_primitive_failed_flag=bool(a and a.get('stochastic_failure')), model_primitive_error=a.get('error') if a else None,
                model_protocol_failure_no_primitive=(a is None),
                skill_primitive_command=b['command'], skill_primitive_identity=[b['event_type'], b['target_node_ids']],
                skill_expected_prerequisite_success=expected_success(b, expected),
                model_source_after=(a['after'] if a else before)[case['item_id']], skill_source_after=b['after'][case['item_id']])
            # These suffix outcomes follow a genuine same-state fork but also
            # include new player responses and later freely revised choices.
            for backend, episode in [('model_steps', left), ('native_skill', right)]:
                suffix = [event_readback(episode, h) for h in episode['turns'][i:]]
                record[backend + '_selected_outcome_ever_after_activation'] = any(
                    f['physical'] if b['selected_target'] == 'goal' else f['request'] for f in suffix)
                record[backend + '_remaining_native_turns_including_activation'] = len(episode['turns']) - i
            return record
        assert a is not None
        assert native_projection(a) == native_projection(b), ('Native prefix diverges before activation', record, i)
        add_visible(visible[0], a, left); add_visible(visible[1], b, right)
        record['common_prefix_native_turns'] += 1
        record['common_prefix_including_opening_checks'] += 1
    assert left['stop'] == right['stop'] and left['protocol_error'] == right['protocol_error']
    assert left['final_state'] == right['final_state']
    if left['protocol_error']:
        i = len(left['turns'])
        stage = {'invalid_player_json': 'player', 'invalid_npc_choice_json': 'npc_choice'}[left['protocol_error']]
        lkey = jobs[(case['case_id'], left['seed'], left['persona'], 'model_steps', stage, i)]
        rkey = jobs[(case['case_id'], left['seed'], left['persona'], 'native_skill', stage, i)]
        assert lkey == rkey and calls[lkey]['parsed'] is None
    record['unactivated_common_stop'] = left['stop']
    return record


def summarize(records, graph_ids):
    """Conditional pair rates with source-graph cluster bootstrap, including zero-trigger graphs."""
    per_graph = {cid: Counter() for cid in graph_ids}
    for r in records:
        counts = per_graph[r['case_id']]
        counts['eligible_pairs'] += 1
        counts['active_pairs'] += int(r['activated'])
        if not r['activated']:
            continue
        counts['model_expected_prerequisite_success'] += r['model_expected_prerequisite_success']
        counts['skill_expected_prerequisite_success'] += r['skill_expected_prerequisite_success']
        counts['skill_minus_model_expected_prerequisite_success'] += (
            r['skill_expected_prerequisite_success'] - r['model_expected_prerequisite_success'])
        counts['model_identity_equals_witness'] += r['model_identity_equals_witness']
        counts['model_command_equals_witness'] += r['model_command_equals_witness']
        for category in CATEGORIES:
            counts['model_' + category] += r['model_primitive_category'] == category
        for target in ['goal', 'request']:
            counts['selected_target_' + target] += r['selected_target'] == target
        for event in ['GetObjectEvent', 'RemoveObjectEvent']:
            counts['expected_' + event] += r['native_two_primitive_witness'][0]['identity'][0] == event
        for backend in BACKENDS:
            counts[backend + '_selected_outcome_ever_after_activation'] += r[backend + '_selected_outcome_ever_after_activation']
    fixed_fields = {'eligible_pairs', 'active_pairs', 'model_expected_prerequisite_success',
                    'skill_expected_prerequisite_success', 'skill_minus_model_expected_prerequisite_success',
                    'model_identity_equals_witness', 'model_command_equals_witness',
                    'selected_target_goal', 'selected_target_request', 'expected_GetObjectEvent',
                    'expected_RemoveObjectEvent', 'model_steps_selected_outcome_ever_after_activation',
                    'native_skill_selected_outcome_ever_after_activation'}
    fields = sorted(fixed_fields | {'model_' + c for c in CATEGORIES})
    matrix = np.asarray([[per_graph[cid][f] for f in fields] for cid in graph_ids], dtype=float)
    totals = matrix.sum(axis=0)
    where = {f: i for i, f in enumerate(fields)}
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    weights = rng.multinomial(len(graph_ids), np.full(len(graph_ids), 1/len(graph_ids)), size=BOOTSTRAPS)
    sampled = weights @ matrix
    active_index = where['active_pairs']
    defined = sampled[:, active_index] > 0
    active = totals[active_index]
    conditional = {}
    for f in fields:
        if f in ['active_pairs', 'eligible_pairs']:
            continue
        point = float(totals[where[f]] / active) if active else None
        ci = (list(map(float, np.quantile(sampled[defined, where[f]] / sampled[defined, active_index], [.025, .975])))
              if active and defined.any() else None)
        conditional[f] = {'conditional_pair_rate': point, 'graph_cluster_95': ci}
    activation = sampled[:, active_index] / sampled[:, where['eligible_pairs']]
    return {'eligible_graphs': len(graph_ids), 'active_graphs': sum(v['active_pairs'] > 0 for v in per_graph.values()),
            'counts': {f: int(totals[where[f]]) for f in fields},
            'active_pair_fraction': float(active / totals[where['eligible_pairs']]),
            'active_pair_fraction_graph_cluster_95': list(map(float, np.quantile(activation, [.025, .975]))),
            'conditional_rates': conditional, 'bootstrap_replicates': BOOTSTRAPS,
            'bootstrap_replicates_without_any_activation': int((~defined).sum())}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--call-runs', type=Path, nargs='*', default=[])
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--profile', action='store_true')
    args = ap.parse_args()
    assert os.environ.get('PYTHONHASHSEED') == '0', 'Native prefix replay requires the driver PYTHONHASHSEED=0.'
    by_model = defaultdict(list); call_model = defaultdict(list)
    for folder in dict.fromkeys(args.runs):
        by_model[json.loads((folder / 'manifest.json').read_text())['model']].append(folder)
    for folder in dict.fromkeys(args.call_runs):
        call_model[json.loads((folder / 'manifest.json').read_text())['model']].append(folder)
    from light_native_gate import load_event_modules
    from light_npc_episodes import CACHE
    modules = load_event_modules(CACHE / 'sources/LIGHT')
    first_manifest = json.loads((args.runs[0] / 'manifest.json').read_text())
    source = Path(first_manifest['source'])
    assert sha(source) == first_manifest['source_sha256']
    cases = load_sources(source, modules)
    profile = [next(cid for cid, c in cases.items() if c['goal_kind'] == 'give'),
               next(cid for cid, c in cases.items() if c['goal_kind'] != 'give')]
    ids = profile if args.profile else list(cases)
    models = {}; hashes = {str(source): sha(source)}
    for model, folders in by_model.items():
        loaded = read_runs(folders, call_model[model], args.profile)
        rows, manifests, runtimes, model_hashes, duplicates, calls, jobs, costs, reused, call_runtimes = loaded
        assert all(m['source_sha256'] == first_manifest['source_sha256'] for m in manifests)
        expected = {(cid, seed, persona, backend) for cid in ids for seed in SEEDS
                    for persona in PERSONAS for backend in BACKENDS}
        assert set(rows) == expected
        hashes.update(model_hashes)
        pairs = []
        for cid in ids:
            for persona in PERSONAS:
                for seed in SEEDS:
                    left, right = [rows[cid, seed, persona, backend] for backend in BACKENDS]
                    pairs.append(pair_readback(cases[cid], left, right, calls, jobs, modules))
        groups = {'all': ids, 'Give': [cid for cid in ids if cases[cid]['goal_kind'] == 'give'],
                  'nonGive': [cid for cid in ids if cases[cid]['goal_kind'] != 'give']}
        groups.update({kind: [cid for cid in ids if cases[cid]['goal_kind'] == kind]
                       for kind in sorted({cases[cid]['goal_kind'] for cid in ids})})
        summaries = {}
        for group, cids in groups.items():
            if not cids:
                continue
            for persona in ['pooled_traits', *PERSONAS]:
                subset = [r for r in pairs if r['case_id'] in cids
                          and (persona == 'pooled_traits' or r['persona'] == persona)]
                summaries[group + '/' + persona] = summarize(subset, cids)
        models[model] = {'worlds': len(ids), 'episodes': len(rows), 'backend_pairs': len(pairs),
            'identical_profile_full_episode_records_excluded': duplicates,
            'pre_activation_invariant': {'status': 'PASS', 'all_pairs_checked': len(pairs),
                'prefix_native_events_compared_including_opening': sum(r['common_prefix_including_opening_checks'] for r in pairs),
                'first_common_two_step_pairs': sum(r['activated'] for r in pairs),
                'activated_graphs': len({r['case_id'] for r in pairs if r['activated']}),
                'native_witnesses_verified': sum(r['activated'] for r in pairs)},
            'summaries': summaries, 'pair_readback': pairs}
    result = {'status': 'PROFILE_TOOL_CHECK_ONLY_POST_HOC' if args.profile else 'COMPLETE_POST_HOC',
        'experiment': 'E80', 'analysis': 'first_common_two_step_activation', 'model_calls': 0, 'API_calls': 0,
        'design_timing': 'Added after both two-world profiles, before full E80 results completed. Not an original preregistered primary endpoint.',
        'fixed_readback': [
            'Retain every preassigned source graph, seed and persona; pair model_steps/native_skill by exact source/seed/persona.',
            'Before first len2 alias, compare actual material states, native events, viewer-visible history, selector/player input keys and parsed high-level choices. Ignore lower-decision metadata.',
            'At first common len2 choice verify same selected target and a native two-primitive fork witness; expected first primitive is source Get or Remove.',
            'Read actual model lower action and physical success against that witness; distinguish other legal speech/action from rejections/failed flags.',
            'Skill and model primitive use the same original game opportunity. Subsequent freely revised choices/player responses are descriptive suffix outcomes.',
            'Cluster bootstrap source graphs with all seed/trait pairs retained. Conditional rates use active-pair counts as denominators; zero-trigger graphs remain in resampling.',
            'Do not substitute conditional activation results for all-world main endpoints, compare personas as latent ability, or equate later realized targets with primitive implementation quality.',
        ],
        'models': models, 'source_sha256': hashes, 'script_sha256': sha(Path(__file__)),
        'metric_dependency_sha256': sha(Path(__file__).with_name('native_interactive_report.py'))}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'models': {model: value['pre_activation_invariant']
                                                            for model, value in models.items()}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
