#!/usr/bin/env python3
"""E85: partner performance, factual claims and later revision in original LIGHT.

Six primary continuations and two revision continuations share immutable E84
histories. Native tools own every physical transition; a factual shadow report
never becomes action context. This is an ordinary local-model baseline, not a
contract ledger, reward gate or scripted NPC policy.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
import os
from pathlib import Path
import time

from commitment_decisions_v2 import schema
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, material_state, observation
from native_cooperation_episodes import action_spec, catalogue, header, identity
import native_independent_goal_episodes as native
from native_independent_goal_qualification import owner
from native_reciprocal_deathsafe import character_dead, character_health
from native_rule_execution import SharedPrefixClient

SEEDS = [8501, 8502]
MAX_TURNS = 24
CONDITIONS = ['real_claim', 'claim_only', 'pending_truth']
CONTROLS = ['normal', 'check']
CHECK = ('Before choosing, check your current inventory and actual event feedback '
         'against any claimed transfer; words alone do not move items.')
MECHANICS = ('An equipped item must be removed before it can be given. '
             'Each native primitive uses one opportunity.')
CLAIM = 'I have given you {x}. I would still like {y}.'
PENDING = 'I have not given you {x} yet. I would still like {y}.'
CONTINUE = 'Please continue with what we were discussing.'
WITHDRAW = 'Plans changed; I need {x} back now. Can we find another way?'
DEPENDENCIES = ['native_independent_goal_episodes.py', 'native_cooperation_episodes.py',
                'native_independent_goal_qualification.py', 'light_npc_episodes.py',
                'native_rule_execution.py', 'commitment_decisions_v2.py',
                'light_native_gate.py', 'native_reciprocal_deathsafe.py']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def input_key(j):
    return canonical({k: j[k] for k in ['messages', 'schema', 'seed']})


def load_lines(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]


def write_line(path, value):
    with Path(path).open('a') as f:
        f.write(json.dumps(value, ensure_ascii=False) + '\n')


def mapped_case(history):
    """Only reorder which original author role is called NPC; no text editing."""
    case = copy.deepcopy(history['case'])
    roles = history['source_role_map']
    order = [roles['npc'], roles['player']]
    assert sorted(order) == [0, 1]
    for key in ['actor_ids', 'quests', 'goal_bindings', 'goal_identities', 'initial_room_ids']:
        if key in case:
            case[key] = [case[key][i] for i in order]
    return case


def history_text(history, key, default):
    # These are fixed experiment interventions, not generated negotiations.
    # Any explicit source text must be frozen in the source data before models.
    graph = json.loads(history['pre_player_graph_json'])
    nodes = graph.get('nodes', graph.get('all_nodes', {}))
    def name(iid):
        if iid in nodes and isinstance(nodes[iid], dict):
            return nodes[iid].get('name', iid)
        return history.get('item_names', {}).get(iid, iid)
    return history.get(key, default.format(x=name(history['x_item_id']),
                                          y=name(history['y_item_id'])))


def new_game(history, seed, modules):
    case = mapped_case(history)
    graph = modules[0].from_json(history['pre_player_graph_json'])
    order = [history['source_role_map'][key] for key in ['npc', 'player']]
    supported = [bool(b.get('item_id')) and (b['verb'] not in ['give', 'put']
                 or b.get('target_id') is not None) for b in case['goal_bindings']]
    consumed = history.get('pre_player_consumed_by_actor', [False, False])
    g = {'case': case, 'history': history, 'modules': modules, 'graph': graph,
         'host': ViewerHost(graph), 'visible': [list(history['pre_player_visible'][i]) for i in order],
         'seed': seed, 'history_id': history['history_id'], 'turns': [], 'states': [],
         'interventions': [], 'stop': None,
         'strict_goal_measurement_supported': supported,
         'strict_goal_ever': [False if value else None for value in supported],
         'consumed_by_actor': [bool(consumed[i]) for i in order],
         'physical_goal_now': [None, None], 'physical_goal_ever': [None, None]}
    native.refresh_goals(g)
    g['physical_goal_initial'] = list(g['physical_goal_now'])
    g['initial_state'] = material_state(graph)
    g['states'].append({'phase': 'source_cut', 'turn': None, 'graph': graph.to_json(),
                        'visible': copy.deepcopy(g['visible'])})
    return g


def fork_game(game):
    excluded = {'graph', 'host', 'modules', 'case', 'history'}
    out = {key: copy.deepcopy(value) for key, value in game.items() if key not in excluded}
    out.update(case=game['case'], history=game['history'], modules=game['modules'])
    out['graph'] = game['modules'][0].from_json(game['graph'].to_json())
    out['host'] = ViewerHost(out['graph'])
    assert json.loads(out['graph'].to_json()) == json.loads(game['graph'].to_json())
    assert out['visible'] == game['visible']
    return out


def apply_native(game, index, event_type, ids, text, turn, phase):
    """Scripted partner events still require the ordinary native menu and guard."""
    actor = game['graph'].get_node(game['case']['actor_ids'][index])
    cls = getattr(game['modules'][1], event_type)
    if event_type != 'SayEvent':
        menu = catalogue(game['graph'], actor)
        assert any(identity(event) == [event_type, ids] for event in menu.values()), (
            game['history_id'], phase, event_type, ids, 'not in native catalogue')
    event = cls.construct_from_args(actor, [game['graph'].get_node(iid) for iid in ids], text)
    assert not isinstance(event, game['modules'][2]), (phase, event.view_as(actor))
    native.execute_selected(game, index, event,
        {'tool': 'SCRIPT:' + event_type, 'utterance': text if event_type == 'SayEvent' else ''},
        turn, [event_type, ids])
    row = game['turns'][-1]
    row.update(phase=phase, decision_source='scripted_partner', model_decision=False)
    game['states'][-1]['phase'] = phase
    assert row['legal'] and row.get('executed') and not row.get('stochastic_failure'), (
        phase, row.get('error'), row.get('native_exception'))
    if event_type == 'SayEvent':
        recipient = game['case']['actor_ids'][1 - index]
        assert any(message['viewer'] == recipient and message['event'] == 'SayEvent'
                   for message in row['messages']), (phase, 'speech not actually received')
    return row


def inject(history, seed, condition, control, modules):
    g = new_game(history, seed, modules)
    g.update(panel='primary', branch=condition, control=control)
    player, npc = g['case']['actor_ids'][1], g['case']['actor_ids'][0]
    x, y = history['x_item_id'], history['y_item_id']
    assert owner(g['graph'], x) == player and owner(g['graph'], y) == npc
    expected = history['actual_player_event']
    assert expected['event_type'] == 'GiveObjectEvent'
    assert expected['target_node_ids'] == [x, npc]
    if condition == 'real_claim':
        apply_native(g, 1, 'GiveObjectEvent', [x, npc], '', -2, 'partner_contribution')
        assert owner(g['graph'], x) == npc
    else:
        apply_native(g, 1, 'WaitEvent', [], '', -2, 'partner_withheld_contribution')
        assert owner(g['graph'], x) == player
    g['interventions'].append(g['turns'].pop())
    text = history_text(history, 'pending_text', PENDING) if condition == 'pending_truth' else history_text(history, 'claim_text', CLAIM)
    apply_native(g, 1, 'SayEvent', [], text, -1, 'partner_performance_statement')
    g['interventions'].append(g['turns'].pop())
    assert owner(g['graph'], y) == npc
    g['post_intervention_state'] = material_state(g['graph'])
    g['post_intervention_graph_sha256'] = sha_graph(g['graph'])
    return g


def sha_graph(graph):
    return hashlib.sha256(graph.to_json().encode()).hexdigest()


def action_job(game, turn):
    index = turn % 2
    spec, menu = action_spec(game, index, game['modules'])
    spec[0][-1]['content'] += '\n' + MECHANICS
    if index == 0 and game['control'] == 'check':
        spec[0][-1]['content'] += '\n' + CHECK
    return make_job(game, index, spec, 'native_action', turn), menu


def make_job(game, index, spec, stage, turn):
    history_part = int(hashlib.sha256(game['history_id'].encode()).hexdigest()[:7], 16)
    return {'history_id': game['history_id'], 'case_id': game['case']['case_id'],
            'episode_seed': game['seed'], 'panel': game['panel'], 'branch': game['branch'],
            'control': game['control'], 'stage': stage, 'index': index, 'turn': turn,
            'seed': game['seed'] + history_part * 100 + turn + 5000,
            'messages': spec[0], 'schema': spec[1]}


def shadow_spec(game):
    # Look/inventory are rendered on a fork: even read-only event logs from the
    # independent question cannot leak into an action history or its graph.
    shadow = fork_game(game)
    npc = shadow['graph'].get_node(shadow['case']['actor_ids'][0])
    text = observation(shadow['host'], npc, *shadow['modules'][1:])
    text += '\nRecent actual observable interaction:\n' + '\n'.join(shadow['visible'][0][-32:])
    item = shadow['graph'].get_node(shadow['history']['x_item_id'])
    text += ('\nFor this independent factual report, based only on your observable information: '
             'where is ' + item.name + ' [entity: ' + item.node_id + '] now, and do you currently hold it? '
             'Use npc for your character, player for the character you are speaking with, '
             'other for another location or entity, and uncertain if you cannot determine it. '
             'This report performs no action.')
    spec = ([{'role': 'system', 'content': header(shadow['case'], 0)},
             {'role': 'user', 'content': text}],
            schema({'holder': {'type': 'string', 'enum': ['npc', 'player', 'other', 'uncertain']},
                    'npc_holds_x': {'type': 'string', 'enum': ['yes', 'no', 'uncertain']}}))
    j = make_job(shadow, 0, spec, 'shadow_fact', -10)
    j['seed'] += 4000007
    return j


def run_decisions(games, client, turn):
    active = [g for g in games if g['stop'] is None
              and not any(t['turn'] == turn for t in g['turns'])]
    prepared = [action_job(g, turn) for g in active]
    for g, answer, (j, menu) in zip(active, client.batch([x[0] for x in prepared]), prepared):
        native.apply_choice(g, turn % 2, answer, menu, turn, g['modules'])
        if g['turns'] and g['turns'][-1]['turn'] == turn:
            g['turns'][-1].update(phase='continuation', decision_source='local_model',
                                    model_decision=True, model_input_key=input_key(j))
            g['states'][-1]['phase'] = 'continuation'


def revision_game(real_game, branch):
    g = fork_game(real_game)
    g.update(panel='revision', branch=branch, control='check')
    first = next((turn for turn in g['turns'] if turn['turn'] == 0), None)
    g['shared_first_response'] = {
        'history_id': g['history_id'], 'seed': g['seed'], 'panel': 'primary',
        'branch': 'real_claim', 'control': 'check',
        'turn': 0, 'model_input_key': first.get('model_input_key') if first else None,
        'graph_sha256': sha_graph(g['graph']), 'visible_sha256': canonical(g['visible']),
        'scope': 'Exact graph, visible history and first NPC action; no second model sample.'}
    if g['stop'] is not None:
        g['upstream_first_response_stop'] = g['stop']
        return g
    text = (history_text(g['history'], 'continue_text', CONTINUE) if branch == 'continue'
            else history_text(g['history'], 'withdraw_text', WITHDRAW))
    apply_native(g, 1, 'SayEvent', [], text, 1, 'partner_revision_statement')
    g['pre_revision_state'] = copy.deepcopy(real_game['turns'][0]['after'])
    return g


def save_game(game, out):
    excluded = {'graph', 'host', 'modules', 'case', 'history', 'visible', 'states'}
    row = {key: value for key, value in game.items() if key not in excluded}
    h, c = game['history'], game['case']
    row.update(case_id=c['case_id'], graph_sha256=c['graph_sha256'],
               model_origin=h['model_origin'], source_seed=h['source_seed'],
               source_turn=h['source_turn'], source_role_map=h['source_role_map'],
               actor_ids=c['actor_ids'], quest_files=[q['source_file'] for q in c['quests']],
               x_item_id=h['x_item_id'], y_item_id=h['y_item_id'],
               stop=game['stop'] or 'turn_limit', final_state=material_state(game['graph']),
               final_health=[character_health(game['graph'], actor) for actor in c['actor_ids']],
               final_dead=[character_dead(game['graph'], actor) for actor in c['actor_ids']])
    key = {k: row[k] for k in ['history_id', 'seed', 'panel', 'branch', 'control']}
    write_line(out / 'episodes.jsonl', row)
    write_line(out / 'states.jsonl', {**key, 'actor_ids': c['actor_ids'], 'states': game['states']})


def run_group(histories, seeds, client, modules, out):
    games, probes = [], []
    for history in histories:
        for seed in seeds:
            for condition in CONDITIONS:
                for control in CONTROLS:
                    game = inject(history, seed, condition, control, modules)
                    games.append(game)
                    if control == 'normal':
                        before = (sha_graph(game['graph']), canonical(game['visible']))
                        j = shadow_spec(game)
                        assert before == (sha_graph(game['graph']), canonical(game['visible']))
                        probes.append((game, j, before))
    answers = client.batch([j for _, j, _ in probes])
    for (g, j, before), answer in zip(probes, answers):
        x, npc, player = g['history']['x_item_id'], *g['case']['actor_ids']
        current_owner = owner(g['graph'], x)
        write_line(out / 'shadow_facts.jsonl', {
            'history_id': g['history_id'], 'case_id': g['case']['case_id'], 'seed': g['seed'],
            'branch': g['branch'], 'control': 'normal', 'stage': 'shadow_fact',
            'model_input_key': input_key(j), 'parsed': answer, 'x_item_id': x,
            'actual_x_container': g['graph'].get_node(x).get_container().node_id,
            'actual_x_owner': current_owner, 'actual_holder': (
                'npc' if current_owner == npc else 'player' if current_owner == player else 'other'),
            'actual_npc_holds_x': current_owner == npc,
            'pre_action_graph_sha256': before[0], 'pre_action_visible_sha256': before[1],
            'answers_never_used_by_action_policy': True})
    run_decisions(games, client, 0)
    real = [g for g in games if g['branch'] == 'real_claim' and g['control'] == 'check']
    revisions = [revision_game(g, branch) for g in real for branch in ['continue', 'withdraw']]
    for g in real:
        write_line(out / 'first_responses.jsonl', {
            'history_id': g['history_id'], 'seed': g['seed'], 'panel': 'primary',
            'branch': 'real_claim', 'control': 'check', 'graph': g['graph'].to_json(),
            'visible': g['visible'], 'turns': g['turns'], 'stop': g['stop']})
    games += revisions
    for turn in range(1, MAX_TURNS):
        run_decisions(games, client, turn)
    for g in games:
        save_game(g, out)
    return len(games)


def source_integrity(histories):
    """Match immutable cuts to the already fully native-replayed E84 raw data."""
    cache, wanted, state_cache = {}, {}, {}
    verified = {}
    for h in histories:
        refs = [(h['source_episode_path'], h['source_episode_file_sha256']),
                (h['source_states_path'], h['source_states_sha256']),
                (h['case_ref']['path'], h['case_ref']['sha256'])]
        for path, expected in refs:
            if path not in verified:
                verified[path] = sha(path)
            assert verified[path] == expected, ('source file changed', path)
    for h in histories:
        wanted.setdefault(h['source_episode_path'], set()).add((h['case_id'], h['source_seed']))
    for path, keys in wanted.items():
        for row in map(json.loads, Path(path).open()):
            key = row['case_id'], row['seed']
            if key in keys:
                cache[path, key] = row
    for h in histories:
        key = h['case_id'], h['source_seed']
        row = cache[h['source_episode_path'], key]
        source_digest = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                                separators=(',', ':')).encode()).hexdigest()
        assert source_digest == h['source_episode_canonical_sha256']
        assert sha_text(h['pre_player_graph_json']) == h['pre_player_graph_sha256']
        states_path = h['source_states_path']
        if states_path not in state_cache:
            needed = {((x['case_id'], x['source_seed'])) for x in histories
                      if x['source_states_path'] == states_path}
            state_cache[states_path] = { (r['case_id'], r['seed']): r
                for r in map(json.loads, Path(states_path).open())
                if (r['case_id'], r['seed']) in needed }
        states = state_cache[states_path][key]['states']
        cut = h['source_turn']
        assert cut >= 0
        prior = next((s for s in states if s['turn'] == cut - 1), None)
        assert prior is not None, (h['history_id'], 'missing source pre-cut state')
        assert json.loads(prior['graph']) == json.loads(h['pre_player_graph_json'])
        assert prior['visible'] == h['pre_player_visible']
        event = next(t for t in row['turns'] if t['turn'] == cut)
        assert event['index'] == h['source_role_map']['player']
        assert event['event_identity'] == [h['actual_player_event']['event_type'],
                                            h['actual_player_event']['target_node_ids']]
        assert event['legal'] and event['executed'] and not event.get('stochastic_failure')
        assert event['before'] == material_state_from_json(h['pre_player_graph_json'])
    return {'immutable_raw_episode_cuts_checked': len(histories),
            'source_file_sha256': verified,
            'full_prefix_native_replay': 'Inherited E84 independent full-corpus PASS; no new source edits.'}


def material_state_from_json(text):
    # This comparison is performed after modules have been loaded by main.
    from light.graph.structured_graph import OOGraph
    return material_state(OOGraph.from_json(text))


def validate_path(game, path):
    witness = fork_game(game)
    for number, step in enumerate(path):
        aid = step.get('actor_id')
        index = witness['case']['actor_ids'].index(aid) if aid is not None else step['actor_index']
        apply_native(witness, index, step['event_type'], step['target_node_ids'],
                     step.get('text', ''), -100 - number, 'qualification_witness_only')
    return {'steps': len(path), 'final_state': material_state(witness['graph'])}


def y_path(history, label):
    key = 'actual_give' if label == 'real' else 'withheld'
    return history['native_paths'][key]['response_steps']


def cpu_check(histories, modules):
    audit = source_integrity(histories)
    counts = Counter()
    for h in histories:
        c = mapped_case(h)
        order = [h['source_role_map'][k] for k in ['npc', 'player']]
        assert c['case_id'] == h['case_id']
        assert c['quests'][0]['graph'] == c['quests'][1]['graph']
        assert sha_text(c['quests'][0]['graph']) == c['graph_sha256']
        assert h['private_headers'] == [header(h['case'], i) for i in [0, 1]]
        assert [header(c, i) for i in [0, 1]] == [h['private_headers'][i] for i in order]
        nodes = []
        for condition in CONDITIONS:
            g = inject(h, SEEDS[0], condition, 'normal', modules)
            before = (sha_graph(g['graph']), copy.deepcopy(g['visible']))
            shadow = shadow_spec(g)
            assert before == (sha_graph(g['graph']), g['visible'])
            assert shadow['messages'][0]['content'] == header(c, 0)
            nodes.append(g)
            for control in CONTROLS:
                probe = fork_game(g)
                probe['control'] = control
                for index in [0, 1]:
                    j, menu = action_job(probe, index)
                    assert j['messages'][0]['content'] == header(c, index)
                    assert j['messages'][-1]['content'].count(MECHANICS) == 1
                    other = c['quests'][1 - index]
                    own_header = header(c, index)
                    for field in ['short_motivation', 'mid_motivation', 'long_motivation']:
                        value = other[field]
                        if len(value) > 25 and value not in own_header:
                            assert value not in j['messages'][0]['content']
                    assert all(e.actor.node_id == c['actor_ids'][index] for e in menu.values())
                    counts['typed_action_entries'] += len(menu)
                counts['primary_specs_checked'] += 1
        a = nodes[0]['interventions'][-1]['choice']['utterance']
        b = nodes[1]['interventions'][-1]['choice']['utterance']
        assert a == b
        assert nodes[1]['post_intervention_state'] == nodes[2]['post_intervention_state']
        for label, node in [('real', nodes[0]), ('withheld', nodes[1])]:
            paths = y_path(h, label)
            assert paths, (h['history_id'], label, 'missing common feasible Y witness')
            validate_path(node, paths)
            counts['Y_native_path_witnesses_checked'] += 1
        counts['histories'] += 1
    return {'experiment': 'E85', 'status': 'PASS', **audit, **dict(counts),
            'source_histories': len(histories),
            'independent_graphs': len({h['case']['graph_sha256'] for h in histories}),
            'roles_original_and_source_order_preserved': True,
            'main_native_transfer': 'GiveObjectEvent only; withheld native Wait',
            'source_prefixes_are_contracts': False,
            'new_model_calls': 0, 'new_API_calls': 0, 'new_GPU_jobs': 0}


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def load_histories(path):
    rows = sorted(load_lines(path), key=lambda h: h['history_id'])
    assert len(rows) == len({h['history_id'] for h in rows})
    required = ['case', 'case_id', 'history_id', 'model_origin', 'source_seed', 'source_turn',
                'source_episode_path', 'source_episode_canonical_sha256', 'source_states_path',
                'source_role_map', 'pre_player_graph_json', 'pre_player_visible',
                'private_headers', 'x_item_id', 'y_item_id', 'actual_player_event', 'native_paths']
    for h in rows:
        assert all(k in h for k in required), (h.get('history_id'), [k for k in required if k not in h])
        assert h['x_item_id'] != h['y_item_id']
        assert sorted(h['source_role_map'].values()) == [0, 1]
        assert h['actual_player_event']['event_type'] == 'GiveObjectEvent'
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--model', type=Path)
    ap.add_argument('--profile', action='store_true')
    ap.add_argument('--cpu-check', action='store_true')
    ap.add_argument('--prior-runs', type=Path, nargs='*', default=[])
    ap.add_argument('--history-batch', type=int, default=2)
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--shards', type=int, default=1)
    a = ap.parse_args()
    assert os.environ.get('PYTHONHASHSEED') == '0'
    modules = load_event_modules(CACHE / 'sources/LIGHT')
    histories = load_histories(a.data)
    if a.cpu_check:
        report = cpu_check(histories, modules)
        report.update(data_sha256=sha(a.data), driver_sha256=sha(__file__))
        a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(report, ensure_ascii=False))
        return
    assert a.model and histories and a.history_batch > 0
    assert a.shards > 0 and 0 <= a.shard < a.shards
    selected, seeds = ((histories[:1], SEEDS[:1]) if a.profile
                       else (histories[a.shard::a.shards], SEEDS))
    assert selected
    a.out.mkdir(parents=True, exist_ok=False)
    dependencies = {name: sha(Path(__file__).with_name(name)) for name in DEPENDENCIES}
    manifest = {'experiment': 'E85', 'model': str(a.model), 'data': str(a.data),
        'data_sha256': sha(a.data), 'driver_sha256': sha(__file__), 'dependency_sha256': dependencies,
        'profile': a.profile, 'seeds': seeds, 'history_ids': [h['history_id'] for h in selected],
        'shard': a.shard, 'shards': a.shards, 'total_source_histories': len(histories),
        'total_source_original_graphs': len({h['case']['graph_sha256'] for h in histories}),
        'max_turns': MAX_TURNS, 'primary_conditions': CONDITIONS, 'controls': CONTROLS,
        'revision_conditions': ['continue', 'withdraw'], 'revision_control': 'check',
        'fact_check_sentence': CHECK,
        'uniform_execution_mechanics_sentence': MECHANICS,
        'uniform_execution_mechanics_scope': 'Same fixed asset-symmetric mechanical sentence '
            'for NPC and player in every condition; no named-Y route or transfer recommendation. '
            'Common Y path feasibility is independently native-verified by source qualification.',
        'statement_templates': {'claim': CLAIM, 'pending': PENDING, 'continue': CONTINUE, 'withdraw': WITHDRAW},
        'shadow_factual_readout': {'per_history_seed': 3, 'fed_to_actions': False,
            'scope': 'Separate elicited fact report, not evidence of an action policy internal belief.'},
        'opportunity_count': '24 per continuation (12 NPC,12 partner); revision copies turn0 once, '
            'scripted Say occupies partner turn1, new local calls on turns2..23. Initial Give/Wait+Say '
            'are scripted causal interventions outside the 24 continuation opportunities.',
        'logical_branches_per_history_seed': 8, 'new_cloud_calls': 0, 'world_rules_modified': False,
        'scope': 'Original purposes remain. No universal give/refuse/return correctness or contract-gold label.'}
    (a.out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    client = SharedPrefixClient(a.model, a.out, SEEDS[0])
    for folder in a.prior_runs:
        old = json.loads((folder / 'manifest.json').read_text())
        for key in ['model', 'data_sha256', 'driver_sha256', 'dependency_sha256', 'max_turns',
                    'primary_conditions', 'controls', 'revision_conditions', 'fact_check_sentence']:
            assert old[key] == manifest[key], ('prior mismatch', key)
        assert (folder / 'runtime.json').exists()
        assert set(old['history_ids']) <= set(manifest['history_ids'])
        assert set(old['seeds']) <= set(seeds)
        old_rows = load_lines(folder / 'episodes.jsonl')
        assert len(old_rows) == len(old['history_ids']) * len(old['seeds']) * 8
        assert len({(r['history_id'], r['seed'], r['panel'], r['branch'], r['control']) for r in old_rows}) == len(old_rows)
        for row in map(json.loads, (folder / 'model_calls.jsonl').open()):
            assert row['decision_key'] == input_key(row)
            if row['decision_key'] in client.cache:
                assert client.cache[row['decision_key']] == row['parsed']
            client.cache[row['decision_key']] = row['parsed']
    start, count = time.monotonic(), 0
    for offset in range(0, len(selected), a.history_batch):
        count += run_group(selected[offset:offset + a.history_batch], seeds, client, modules, a.out)
        print(json.dumps({'histories_completed': min(offset + a.history_batch, len(selected)),
                          'episodes': count, 'calls': client.inner.calls,
                          'seconds': time.monotonic() - start}), flush=True)
    runtime = {'experiment': 'E85', 'status': 'COMPLETE', 'histories': len(selected),
        'episodes': count, 'calls': client.inner.calls, 'reused_calls': client.reused,
        'wall_seconds': time.monotonic() - start, 'model_load_seconds': client.inner.load_seconds,
        'new_cloud_calls': 0}
    (a.out / 'runtime.json').write_text(json.dumps(runtime, indent=2) + '\n')


if __name__ == '__main__':
    main()
