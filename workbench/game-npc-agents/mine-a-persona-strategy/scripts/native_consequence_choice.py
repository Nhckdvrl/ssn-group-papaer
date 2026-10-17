#!/usr/bin/env python3
"""E74: independent physical forecasts and native-truth substitution in NPC choice.

No game rules or agent actions are changed. Hypothetical trials run on isolated
native graph forks; actual episodes continue to use the frozen E70 executor.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import time

from light_native_gate import parse_event
from light_npc_episodes import ViewerHost, execute, material_state
from native_rule_execution import configure, SharedPrefixClient, policy
from native_matched_task_execution import decision_key
import native_request_precondition_execution as base
import native_candidate_feedback_execution as proposal

PREDICTION_CONDITIONS = {
    'divert_no_information': ('equipped', 'divert', 'none', 'direct'),
    'divert_initial_feedback': ('equipped', 'divert', 'none', 'direct')}
EXECUTION_CONDITIONS = {
    'divert_self_forecast': ('equipped', 'divert', 'none', 'direct'),
    'divert_native_forecast': ('equipped', 'divert', 'none', 'direct')}
KINDS = ['initial', 'remove', 'give_A', 'remove_give_A', 'remove_give_B', 'examine', 'remove_drop']
OWNERS = ['self', 'authored_recipient', 'other_peer', 'room', 'other']
TRIALS = {}
FEEDBACK = {}
FORECASTS = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table_layout(case_id, seed):
    kinds = list(KINDS)
    random.Random(seed+int(case_id[:7], 16)*10+740).shuffle(kinds)
    return {f'q{i}': kind for i, kind in enumerate(kinds)}


def native_trials(row, modules):
    c = row['case']; initial = row['states']['equipped']
    graph = modules[0].from_json(initial); actor = graph.get_node(c['actor_id'])
    item = graph.get_node(c['item_id']); before = material_state(graph)
    error = parse_event(graph, actor, c['goal_command'], *modules[1:])
    assert isinstance(error, modules[2]) and 'remove' in error.view_as(actor).lower()
    feedback = error.view_as(actor)
    assert before == material_state(graph)
    examine = next(e.to_canonical_form() for e in modules[1].ExamineEvent.get_valid_actions(graph, actor)
                   if e.target_nodes and e.target_nodes[0].node_id == c['item_id'])
    removed = modules[0].from_json(initial)
    execute(ViewerHost(removed), removed.get_node(c['actor_id']), row['remove_command'], *modules[1:])
    drops = [e.to_canonical_form() for e in modules[1].DropObjectEvent.get_valid_actions(
        removed, removed.get_node(c['actor_id'])) if e.target_nodes[0].node_id == c['item_id']]
    drop = drops[0] if drops else 'drop '+item.name
    commands = {
        'initial': [], 'remove': [row['remove_command']],
        'give_A': [c['goal_command']],
        'remove_give_A': [row['remove_command'], c['goal_command']],
        'remove_give_B': [row['remove_command'], row['requests']['divert']['request_command']],
        'examine': [examine], 'remove_drop': [row['remove_command'], drop]}
    result = {}
    for kind, sequence in commands.items():
        g = modules[0].from_json(initial); a = g.get_node(c['actor_id'])
        events = []; goal_executed = False
        for command in sequence:
            ev = parse_event(g, a, command, *modules[1:])
            targets = [] if isinstance(ev, modules[2]) else [n.node_id for n in ev.target_nodes]
            r = execute(ViewerHost(g), a, command, *modules[1:])
            r['target_node_ids'] = targets; events.append(r)
            if (r['legal'] and r.get('executed') and not r.get('stochastic_failure')
                    and r['event_type'] == 'GiveObjectEvent'
                    and targets == [c['item_id'], c['original_recipient']]):
                goal_executed = True
        final = g.get_node(c['item_id']); parent = final.get_container().node_id
        labels = {c['actor_id']: 'self', c['original_recipient']: 'authored_recipient',
                  row['competitor_id']: 'other_peer', a.get_room().node_id: 'room'}
        truth = {'owner': labels.get(parent, 'other'), 'equipped': bool(final.get_prop('equipped')),
                 'authored_give_executed': goal_executed}
        result[kind] = {'commands': sequence, 'truth': truth, 'native_events': events}
    # These are inherited source eligibility properties, checked without an LLM.
    assert result['initial']['truth'] == result['examine']['truth']
    assert result['examine']['native_events'][0]['legal'] and result['examine']['native_events'][0]['executed']
    assert result['initial']['truth'] == result['give_A']['truth']
    assert result['remove']['truth'] == {'owner': 'self', 'equipped': False, 'authored_give_executed': False}
    assert result['remove_give_A']['truth'] == {'owner': 'authored_recipient', 'equipped': False, 'authored_give_executed': True}
    assert result['remove_give_B']['truth'] == {'owner': 'other_peer', 'equipped': False, 'authored_give_executed': False}
    assert material_state(graph) == before
    return result, feedback


def table_parts(game):
    cid = game['case']['case_id']; layout = table_layout(cid, game['seed'])
    commands = {q: TRIALS[cid][kind]['commands'] for q, kind in layout.items()}
    truth = {q: TRIALS[cid][kind]['truth'] for q, kind in layout.items()}
    return layout, commands, truth


def common_spec(game, stage, modules, graph=None, history=None):
    messages, schema = proposal.spec(game, stage, modules, graph, history)
    if stage == 'exec' and game['condition'] != 'divert_no_information':
        messages[-1]['content'] += ('\nNative mechanics check of the INITIAL state, before your current actions: '
                                    +FEEDBACK[game['case']['case_id']])
    return messages, schema


def forecast_context(game):
    c = game['case']; _, commands, truth = table_parts(game)
    text = ('\nHypothetical command sequences for the INITIAL state (each starts independently from that state): '
            +json.dumps(commands, ensure_ascii=False)
            +'\nOwner labels: self = you; authored_recipient = the recipient in your authored Give task; '
            +'other_peer = the other peer requesting this item; room = the current room; other = another container/owner.')
    return text, truth


def prediction_spec(game, modules):
    graph = modules[0].from_json(game['case']['quest']['graph'])
    messages, _ = common_spec(game, 'exec', modules, graph, [])
    assert proposal.DIRECTIVE in messages[-1]['content']
    messages[-1]['content'] = messages[-1]['content'].replace(
        proposal.DIRECTIVE, 'Current engine candidate commands, for reference:')
    context, truth = forecast_context(game)
    messages[-1]['content'] += (context+'\nPredict only physical outcomes if the listed commands are attempted in order. '
        'An invalid command leaves the physical state unchanged. No hypothetical command has actually executed. '
        'For each sequence report the selected item owner and equipped status at the end, and whether the original '
        'authored Give event has actually occurred within that sequence. Do not choose what you want to do, '
        'and do not substitute speech, intentions or promises for a physical event.')
    item_schema = policy.base.schema({'owner': {'type': 'string', 'enum': OWNERS},
                  'equipped': {'type': 'boolean'}, 'authored_give_executed': {'type': 'boolean'}})
    return messages, policy.base.schema({q: copy.deepcopy(item_schema) for q in truth})


def execution_spec(game, stage, modules, graph=None, history=None):
    messages, schema = common_spec(game, stage, modules, graph, history)
    if stage != 'exec':
        return messages, schema
    context, truth = forecast_context(game)
    cid = game['case']['case_id']
    predicted = FORECASTS[cid, game['seed'], game['persona']]
    record = truth if game['condition'] == 'divert_native_forecast' else predicted
    if record is not None:
        record = {q: {field: record[q][field] for field in truth[q]} for q in truth}
    messages[-1]['content'] += (context+'\nHypothetical physical-outcome record for the INITIAL state only '
        '(not a record of actions you have executed): '+json.dumps(record, ensure_ascii=False)
        +'\nContinue choosing your next command in the actual current world.')
    return messages, schema


def restore_cache(folders, model):
    cache = {}; hashes = {}
    for folder in folders:
        assert (folder/'runtime.json').exists()
        assert json.loads((folder/'manifest.json').read_text())['model'] == str(model)
        for row in map(json.loads, (folder/'model_calls.jsonl').open()):
            cache.setdefault(decision_key(row), row['parsed'])
        hashes[str(folder/'model_calls.jsonl')] = sha(folder/'model_calls.jsonl')
    return cache, hashes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--model', type=Path); ap.add_argument('--prior-runs', type=Path, nargs='*', default=[])
    ap.add_argument('--shard', type=int, default=0); ap.add_argument('--shards', type=int, default=1)
    ap.add_argument('--profile', action='store_true'); ap.add_argument('--cpu-check', action='store_true')
    args = ap.parse_args(); configure()
    assert os.environ.get('PYTHONHASHSEED') == '0', 'Match the frozen E70 native-view ordering with PYTHONHASHSEED=0.'
    rows = list(map(json.loads, args.data.open())); assert len(rows) == 117
    selected = rows[:1] if args.profile else rows[args.shard::args.shards]
    modules = policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    for row in selected:
        cid = row['case']['case_id']; TRIALS[cid], FEEDBACK[cid] = native_trials(row, modules)
    base.CONDITIONS = PREDICTION_CONDITIONS
    if args.cpu_check:
        checks = 0
        for game in base.bases_for(selected):
            game['conversation'] = {'reply': 'I will consider the request.', 'stance': 'negotiate'}
            m, s = prediction_spec(game, modules); layout, _, truth = table_parts(game)
            assert len(layout) == 7 and set(s['properties']) == set(layout)
            assert policy.TRAITS[game['persona']] in m[0]['content']
            assert game['case']['goal_command'] in m[-1]['content']
            assert proposal.DIRECTIVE not in m[-1]['content']
            FORECASTS[game['case']['case_id'], game['seed'], game['persona']] = {
                q: dict(reversed(list(v.items()))) for q, v in reversed(list(truth.items()))}
            a = {**game, 'condition': 'divert_self_forecast'}
            b = {**game, 'condition': 'divert_native_forecast'}
            graph = modules[0].from_json(game['case']['quest']['graph'])
            assert execution_spec(a, 'exec', modules, graph, []) == execution_spec(b, 'exec', modules, graph, [])
            checks += 1
        args.out.parent.mkdir(parents=True, exist_ok=True)
        raw = policy.CACHE/'runs/e74_native_counterfactuals.json'
        raw.write_text(json.dumps(TRIALS, ensure_ascii=False)+'\n')
        summary = {'status': 'PASS', 'worlds': len(selected), 'native_sequences': len(selected)*7,
                   'paired_input_checks': checks, 'source_sha256': sha(args.data), 'model_calls': 0,
                   'raw_witnesses': str(raw), 'raw_sha256': sha(raw),
                   'trial_truth_patterns': {kind: sorted({json.dumps(TRIALS[cid][kind]['truth'], sort_keys=True)
                                           for cid in TRIALS}) for kind in KINDS}}
        args.out.write_text(json.dumps(summary, indent=2)+'\n'); print(json.dumps(summary), flush=True)
        return
    assert args.model and args.prior_runs
    cached, cache_hashes = restore_cache(args.prior_runs, args.model)
    for game in base.bases_for(selected):
        conv = policy.base.job(game['case'], game['persona'], 'conv',
                               common_spec(game, 'conv', modules), game['sampling_seed'])
        assert decision_key(conv) in cached
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {'experiment': 'E74', 'model': str(args.model), 'worlds': len(selected),
                'case_ids': [r['case']['case_id'] for r in selected], 'seeds': base.SEEDS,
                'profile': args.profile, 'shard': args.shard, 'shards': args.shards,
                'script_sha256': sha(Path(__file__)), 'base_sha256': sha(Path(base.__file__)),
                'proposal_renderer_sha256': sha(Path(proposal.__file__)), 'data_sha256': sha(args.data),
                'prediction_conditions': PREDICTION_CONDITIONS, 'execution_conditions': EXECUTION_CONDITIONS,
                'prior_call_sha256': cache_hashes, 'new_cloud_calls': 0, 'rules_modified': False,
                'scripted_agent_actions': 0, 'exact_dialogue_preflight_passed': True}
    (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    client = SharedPrefixClient(args.model, args.out, 7001); client.cache.update(cached)
    started = time.monotonic(); predictions = 0
    for chunk in [selected[:1]]+[selected[i:i+6] for i in range(1, len(selected), 6)]:
        games = base.bases_for(chunk)
        for game in games:
            conv = policy.base.job(game['case'], game['persona'], 'conv',
                                   common_spec(game, 'conv', modules), game['sampling_seed'])
            game['conversation'] = cached[decision_key(conv)]
            assert game['conversation'] is not None
        jobs = [policy.base.job(game['case'], game['persona'], 'effects', prediction_spec(game, modules),
                               game['sampling_seed']+500) | {'information': game['condition'], 'logical_seed': game['seed']}
                for game in games]
        with (args.out/'predictions.jsonl').open('a') as handle:
            for game, response in zip(games, client.batch(jobs)):
                layout, commands, truth = table_parts(game)
                r = {'case_id': game['case']['case_id'], 'persona': game['persona'], 'seed': game['seed'],
                     'information': game['condition'], 'conversation': game['conversation'], 'layout': layout,
                     'commands': commands, 'truth': truth, 'prediction': response}
                handle.write(json.dumps(r, ensure_ascii=False)+'\n'); predictions += 1
                if game['condition'] == 'divert_initial_feedback':
                    FORECASTS[game['case']['case_id'], game['seed'], game['persona']] = response
        print(json.dumps({'phase': 'prediction', 'contexts': predictions, 'calls': client.inner.calls,
                          'seconds': time.monotonic()-started}), flush=True)
    prediction_calls = client.inner.calls
    base.CONDITIONS = EXECUTION_CONDITIONS; base.spec = execution_spec
    episodes = 0
    for chunk in [selected[:1]]+[selected[i:i+6] for i in range(1, len(selected), 6)]:
        episodes += base.run_group(chunk, client, modules, args.out)
        print(json.dumps({'phase': 'execution', 'episodes': episodes, 'calls': client.inner.calls,
                          'seconds': time.monotonic()-started}), flush=True)
    assert predictions == episodes == len(selected)*12
    runtime = {'worlds': len(selected), 'prediction_contexts': predictions, 'episodes': episodes,
               'calls': client.inner.calls, 'prediction_calls': prediction_calls,
               'new_execution_calls': client.inner.calls-prediction_calls, 'reused_calls': client.reused,
               'wall_seconds': time.monotonic()-started, 'model_load_seconds': client.inner.load_seconds,
               'new_cloud_calls': 0}
    (args.out/'runtime.json').write_text(json.dumps(runtime, indent=2)+'\n'); print(json.dumps(runtime), flush=True)


if __name__ == '__main__':
    main()
