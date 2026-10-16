#!/usr/bin/env python3
"""E80: source-bound, full-interaction CPU readback and graph-paired estimates.

No model, API, semantic judge, or game rule modification is used. Example:
  env PYTHONHASHSEED=0 PYTHONPATH=/home/xiang/.cache/game-npc-research/deps \
    /home/xiang/miniconda3/envs/fgvd/bin/python \
    workbench/game-npc-agents/scripts/native_interactive_report.py \
    --runs RUN1 RUN2 --out REPORT.json [--profile] [--verify-replay]

Pass the profile directory with full runs to resolve cached decisions and
deduplicate identical episodes, or use --call-runs for decision provenance only.
All point estimates average the three seeds within graph before resampling.
Historical goal and transfer events are not mutually exclusive here.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import random

import numpy as np

PERSONAS = ['firm', 'agreeable']
BACKENDS = ['model_steps', 'native_skill']
SEEDS = [8001, 8002, 8003]
ALIASES = {'PURSUE_AUTHORED_OUTCOME': 'goal', 'FULFILL_REQUEST': 'request'}
SPEECH = {'SayEvent', 'TellEvent', 'WhisperEvent'}
CONSUME = {'EatEvent', 'DrinkEvent', 'IngestEvent'}
BOOTSTRAP_SEED = 8080
BOOTSTRAPS = 4000
_BOOTSTRAP_WEIGHTS = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_key(row):
    return tuple(row[k] for k in ['case_id', 'seed', 'persona', 'backend'])


def job_key(job):
    return tuple(job[k] for k in ['case_id', 'episode_seed', 'persona', 'backend', 'stage', 'turn'])


def decision_key(job):
    return hashlib.sha256(json.dumps({k: job[k] for k in ['messages', 'schema', 'seed']},
                                   sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def success(turn):
    return bool(turn['legal'] and turn.get('executed') and not turn.get('stochastic_failure'))


def owner(state, item, character_ids):
    """Ultimate known container, preserving direct possession as a separate field."""
    seen = set()
    node = item
    while node in state:
        assert node not in seen, ('Cyclic native containment', item)
        seen.add(node)
        parent = state[node]['container']
        if parent in character_ids or parent in [None, 'VOID']:
            return parent
        if parent not in state:
            return parent
        node = parent
    return node


def health_dead(state, actor):
    if actor not in state:
        assert actor + '__dead__' in state, ('Missing character without native corpse', actor)
        return 0, True
    return state[actor].get('health'), bool(state[actor].get('dead'))


def event_readback(row, turn):
    """Recompute ID-bound facts from the successful event AND material transition."""
    sid, aid, bid = row['goal_item_id'], row['actor_id'], row['requester_id']
    ids = turn['target_node_ids']
    legal = success(turn)
    is_npc = turn['role'] == 'npc'
    actor = aid if is_npc else bid
    assert turn['actor'] == actor
    event = turn['event_type']
    has_source = bool(legal and ids and ids[0] == sid)
    before, after = turn['before'][sid], turn['after'][sid]
    identity = [event, ids]
    bound = bool(is_npc and legal and identity == row['native_target_identities']['goal'])
    request = bool(is_npc and legal and identity == ['GiveObjectEvent', [sid, bid]])
    given = bool(legal and event == 'GiveObjectEvent')
    if given:
        assert len(ids) == 2
        assert turn['before'][ids[0]]['container'] == actor
        assert turn['after'][ids[0]]['container'] == ids[1]
    if has_source and event == 'GetObjectEvent':
        assert len(ids) == 2 and before['container'] == ids[1]
        assert after['container'] == actor
    if has_source and event == 'StealObjectEvent':
        assert len(ids) == 2 and before['container'] == ids[1]
        assert after['container'] == actor
    consume = bool(has_source and event in CONSUME)
    if consume:
        assert before['container'] == actor and after['container'] == 'VOID'
    equip = bool(has_source and event in ['WearEvent', 'WieldEvent', 'EquipObjectEvent'])
    if equip:
        expected = {'WearEvent': 'wear', 'WieldEvent': 'wield', 'EquipObjectEvent': 'equip'}[event]
        assert before['container'] == after['container'] == actor
        assert after.get('equipped') == expected
    physical = False
    if is_npc and has_source:
        if row['goal_kind'] in ['eat', 'drink']:
            physical = consume
        elif row['goal_kind'] in ['wear', 'wield']:
            physical = bool(equip and after.get('equipped') == row['goal_kind'])
        elif row['goal_kind'] == 'give':
            physical = bool(given and ids[1] == row['goal_recipient_id'])
        else:
            raise AssertionError(('Unknown goal kind', row['goal_kind']))
    assert not bound or physical, ('Bound goal lacks physical consequence', row_key(row), turn['turn'])
    assert turn['matches_bound_goal'] == bound
    assert turn['source_give_to_requester'] == request
    return {'bound': bound, 'physical': physical, 'request': request,
            'source': has_source, 'give': given, 'consume': consume, 'equip': equip}


def metrics(row, case):
    aid, bid, sid = row['actor_id'], row['requester_id'], row['goal_item_id']
    assert (aid, bid, sid) == (case['actor_id'], case['requester_id'], case['item_id'])
    assert row['goal_kind'] == case['goal_kind'] and row['goal_recipient_id'] == case['original_recipient']
    assert row['graph_sha256'] == case['graph_sha256']
    assert row['native_target_identities'] == case['native_target_identities']
    assert row['goal_command'] == case['goal_command'] and row['request_command'] == case['request_command']
    assert row['initial_state'] == case['initial_state']
    opening = row['opening']
    assert opening['role'] == 'player' and opening['turn'] == -1
    assert opening['actor'] == bid and opening['command'] == 'say ' + case['request_text']
    assert success(opening) and opening['event_type'] == 'SayEvent'
    assert opening['before'] == opening['after'] == row['initial_state']
    assert any(m['viewer'] == aid for m in opening['messages']), 'Opening request not delivered to NPC'
    turns = row['turns']
    assert len(turns) <= 16
    assert [h['turn'] for h in turns] == list(range(len(turns)))
    assert all(h['role'] == ('npc' if i % 2 == 0 else 'player') for i, h in enumerate(turns))
    current = opening['after']
    flags = []
    for h in turns:
        assert h['before'] == current, ('Discontinuous material trace', row_key(row), h['turn'])
        assert h['material_changed'] == (h['before'] != h['after'])
        flags.append(event_readback(row, h))
        current = h['after']
        selected = ALIASES.get(h['decision']['action'])
        assert h['selected_target'] == selected
        if selected:
            assert h['role'] == 'npc' and h['path_length'] in [1, 2]
            assert bool(h['lower_decision']) == (row['backend'] == 'model_steps' and h['path_length'] == 2)
        else:
            assert h['path_length'] == 0 and h['lower_decision'] is None
    assert current == row['final_state']
    bound = any(f['bound'] for f in flags)
    physical = any(f['physical'] for f in flags)
    request = any(f['request'] for f in flags)
    assert row['goal_bound_ever'] == bound and row['goal_physical_ever'] == physical
    assert row['npc_give_request_ever'] == request
    final_health, final_dead, initial_health = [], [], []
    for actor in [aid, bid]:
        hp, dead = health_dead(row['final_state'], actor)
        final_health.append(hp); final_dead.append(dead)
        initial_health.append(health_dead(row['initial_state'], actor)[0])
    assert row['final_health'] == final_health and row['final_dead'] == final_dead
    assert row['stop'] in ['turn_limit', 'character_death', 'protocol_error']
    if row['stop'] == 'turn_limit':
        assert len(turns) == 16 and not row['protocol_error'] and not any(final_dead)
    elif row['stop'] == 'character_death':
        assert any(final_dead) and not row['protocol_error']
    else:
        assert row['protocol_error'] and len(turns) < 16
    source_final = row['final_state'][sid]
    own = owner(row['final_state'], sid, [aid, bid, row['goal_recipient_id']])
    value = {
        'npc_goal_bound_ever': float(bound), 'npc_goal_physical_ever': float(physical),
        'npc_goal_physical_without_bound_ever': float(physical and not bound),
        'npc_source_give_requester_ever': float(request),
        'both_goal_physical_and_npc_request_ever': float(physical and request),
        'neither_goal_physical_nor_npc_request_ever': float(not physical and not request),
        'final_source_direct_npc': float(source_final['container'] == aid),
        'final_source_direct_requester': float(source_final['container'] == bid),
        'final_source_ultimate_npc': float(own == aid),
        'final_source_ultimate_requester': float(own == bid),
        'final_source_ultimate_original_recipient': float(row['goal_kind'] == 'give'
            and own == row['goal_recipient_id']),
        'final_source_VOID': float(source_final['container'] == 'VOID'),
        'final_source_any_equipped': float(bool(source_final.get('equipped'))),
        'final_source_npc_any_equipped': float(bool(source_final.get('equipped')) and source_final['container'] == aid),
        'final_source_npc_goal_mode_equipped': float(row['goal_kind'] in ['wear', 'wield']
            and source_final['container'] == aid and source_final.get('equipped') == row['goal_kind']),
        'npc_goal_physical_ever_but_source_final_requester': float(physical and own == bid),
        'npc_goal_physical_ever_but_source_not_final_npc': float(physical and own != aid),
        'npc_source_give_requester_ever_but_source_not_final_requester': float(request and own != bid),
        'npc_final_health': float(final_health[0]), 'player_final_health': float(final_health[1]),
        'npc_health_change': float(final_health[0] - initial_health[0]),
        'player_health_change': float(final_health[1] - initial_health[1]),
        'npc_dead': float(final_dead[0]), 'player_dead': float(final_dead[1]),
        'either_dead': float(any(final_dead)), 'protocol_error': float(bool(row['protocol_error'])),
        'total_action_opportunities_executed': float(len(turns)),
    }
    index = defaultdict(list)
    for h, f in zip(turns, flags):
        role, event = h['role'], h['event_type']
        valid = success(h)
        for name, cond in {
            'source_get': f['source'] and event == 'GetObjectEvent',
            'source_steal': f['source'] and event == 'StealObjectEvent',
            'source_consume': f['consume'], 'source_any_equipped': f['equip'],
            'source_drop': f['source'] and event == 'DropObjectEvent',
            'source_remove': f['source'] and event == 'RemoveObjectEvent',
            'source_give': f['source'] and f['give'],
            'other_asset_give': f['give'] and h['target_node_ids'][0] != sid,
            'give_other_party': f['give'] and h['target_node_ids'][1] == (bid if role == 'npc' else aid),
            'other_asset_give_other_party': f['give'] and h['target_node_ids'][0] != sid
                and h['target_node_ids'][1] == (bid if role == 'npc' else aid),
            'source_give_other_party': f['source'] and f['give']
                and h['target_node_ids'][1] == (bid if role == 'npc' else aid),
            'speech': valid and event in SPEECH,
            'examine': valid and event == 'ExamineEvent',
            'emote': valid and event == 'EmoteEvent',
            'block': valid and event == 'BlockEvent',
            'attack': valid and event == 'HitEvent',
            'native_error': not h['legal'],
            'native_failed_flag': bool(h.get('stochastic_failure')),
            'no_material_change': valid and not h['material_changed'],
            'consequence_choice': bool(h['selected_target']),
            'goal_choice': h['selected_target'] == 'goal',
            'request_choice': h['selected_target'] == 'request',
            'two_step_choice': h['path_length'] == 2,
            'skill_trigger': row['backend'] == 'native_skill' and h['path_length'] == 2,
            'lower_model_choice': h['lower_decision'] is not None,
            'one_step_consequence_choice': h['path_length'] == 1,
            'selected_goal_realized_same_opportunity': h['selected_target'] == 'goal' and f['physical'],
            'selected_request_realized_same_opportunity': h['selected_target'] == 'request' and f['request'],
            'non_speech_unused_utterance': bool((h['lower_decision'] or h['decision']).get('utterance'))
                and event not in SPEECH,
        }.items():
            if cond:
                index[role + '_' + name].append(h['turn'])
        if f['physical']:
            index['goal'].append(h['turn'])
        if f['request']:
            index['request'].append(h['turn'])
    bases = ['source_get', 'source_steal', 'source_consume', 'source_any_equipped', 'source_drop',
             'source_remove', 'source_give', 'other_asset_give', 'give_other_party',
             'other_asset_give_other_party', 'source_give_other_party', 'speech', 'examine', 'emote',
             'block', 'attack', 'native_error', 'native_failed_flag', 'no_material_change',
             'consequence_choice', 'goal_choice', 'request_choice', 'two_step_choice', 'skill_trigger',
             'lower_model_choice', 'one_step_consequence_choice', 'selected_goal_realized_same_opportunity',
             'selected_request_realized_same_opportunity', 'non_speech_unused_utterance']
    for role in ['npc', 'player']:
        value[role + '_opportunities_executed'] = float(sum(h['role'] == role for h in turns))
        for name in bases:
            value[role + '_' + name + '_count'] = float(len(index[role + '_' + name]))
            value[role + '_' + name + '_ever'] = float(bool(index[role + '_' + name]))
    value['bidirectional_any_item_give_ever'] = float(bool(index['npc_give_other_party'] and index['player_give_other_party']))
    value['source_any_equipped_ever'] = float(bool(index['npc_source_any_equipped'] or index['player_source_any_equipped']))
    value['source_any_consumed_ever'] = float(bool(index['npc_source_consume'] or index['player_source_consume']))
    value['player_get_or_steal_source_ever'] = float(bool(index['player_source_get'] or index['player_source_steal']))
    requester_ever = any(owner(h['after'], sid, [aid, bid, row['goal_recipient_id']]) == bid for h in turns)
    value['requester_ever_ultimate_source_possession'] = float(requester_ever)
    value['requester_ever_source_without_npc_source_give'] = float(requester_ever and not request)
    value['final_requester_source_without_npc_source_give'] = float(own == bid and not request)
    value['npc_goal_then_npc_request_ever'] = float(bool(index['goal'] and index['request']
        and any(g < b for g in index['goal'] for b in index['request'])))
    value['npc_request_then_goal_ever'] = float(bool(index['goal'] and index['request']
        and any(b < g for g in index['goal'] for b in index['request'])))
    value['first_npc_choice_goal'] = float(bool(turns and turns[0]['selected_target'] == 'goal'))
    value['first_npc_choice_request'] = float(bool(turns and turns[0]['selected_target'] == 'request'))
    value['first_npc_physical_goal'] = float(bool(flags and flags[0]['physical']))
    value['first_npc_give_requester'] = float(bool(flags and flags[0]['request']))
    return value


def load_sources(path, modules):
    from light_native_gate import parse_event
    from light_npc_episodes import material_state
    from native_owned_container_qualification import event_id
    rows = list(map(json.loads, path.open()))
    assert len(rows) == 200
    cases = {}
    for source in rows:
        case = dict(source['case'])
        request = source['requests']['goal_item']
        case.update(request_command=request['command'], request_text=request['request_text'])
        graph = modules[0].from_json(case['quest']['graph'])
        actor = graph.get_node(case['actor_id'])
        identities = {}
        for target, command in [('goal', case['goal_command']), ('request', case['request_command'])]:
            ident = event_id(parse_event(graph, actor, command, *modules[1:]), modules)
            assert ident and ident[1][0] == case['item_id']
            identities[target] = [ident[0], list(ident[1])]
        assert identities['request'] == ['GiveObjectEvent', [case['item_id'], case['requester_id']]]
        case.update(native_target_identities=identities, initial_state=material_state(graph))
        assert case['initial_state'][case['item_id']]['container'] == case['actor_id']
        assert case['case_id'] not in cases
        cases[case['case_id']] = case
    assert len({c['graph_sha256'] for c in cases.values()}) == 200
    return cases


def read_runs(folders, call_folders, profile):
    rows, manifests, runtimes, hashes = {}, [], [], {}
    duplicate_episodes = 0
    for folder in dict.fromkeys(folders):
        manifest = json.loads((folder / 'manifest.json').read_text())
        runtime = json.loads((folder / 'runtime.json').read_text())
        assert manifest['experiment'] == 'E80'
        if profile:
            assert manifest['profile']
        manifests.append(manifest); runtimes.append(runtime)
        path = folder / 'episodes.jsonl'
        hashes[str(path)] = sha(path)
        count = 0
        for row in map(json.loads, path.open()):
            k = row_key(row)
            if k in rows:
                assert rows[k] == row, ('Non-identical profile/full duplicate', k)
                duplicate_episodes += 1
            else:
                rows[k] = row
            count += 1
        assert count == runtime['episodes'] == len(manifest['case_ids']) * 12
    first = manifests[0]
    for key in ['model', 'source_sha256', 'seeds', 'personas', 'backends', 'max_turns',
                'driver_sha256', 'skills_sha256', 'rules_modified', 'new_cloud_calls']:
        assert all(m[key] == first[key] for m in manifests), key
    assert set(first['personas']) == set(PERSONAS) and first['seeds'] == SEEDS
    assert first['backends'] == BACKENDS and first['max_turns'] == 16
    assert not first['rules_modified'] and first['new_cloud_calls'] == 0
    calls, job_keys, totals, reused_totals = {}, {}, Counter(), 0
    call_runtimes, call_manifests = [], []
    for folder in dict.fromkeys([*folders, *call_folders]):
        manifest = json.loads((folder / 'manifest.json').read_text())
        runtime = json.loads((folder / 'runtime.json').read_text())
        for field in ['model', 'source_sha256', 'driver_sha256', 'skills_sha256']:
            assert manifest[field] == first[field]
        call_manifests.append(manifest); call_runtimes.append(runtime)
        count = 0
        for name in ['model_calls.jsonl', 'reused_calls.jsonl']:
            path = folder / name
            if not path.exists():
                assert name == 'reused_calls.jsonl'
                continue
            hashes[str(path)] = sha(path)
            for record in map(json.loads, path.open()):
                jk = job_key(record)
                if jk in job_keys:
                    assert job_keys[jk] == record['decision_key'], ('Different same-job decisions', jk)
                job_keys[jk] = record['decision_key']
                if name == 'model_calls.jsonl':
                    assert decision_key(record) == record['decision_key']
                    if record['decision_key'] in calls:
                        old = calls[record['decision_key']]
                        assert all(record[f] == old[f] for f in ['messages', 'schema', 'seed', 'parsed'])
                    else:
                        calls[record['decision_key']] = record
                    count += 1
                    totals.update(calls=1, prompt_tokens=record['prompt_tokens'],
                                  completion_tokens=record['completion_tokens'],
                                  parse_errors=int(bool(record['parse_error'])))
                else:
                    reused_totals += 1
        assert count == runtime['calls']
        assert runtime['new_cloud_calls'] == 0
    assert all(k in calls for k in job_keys.values()), 'Supply cached profile dependencies via --call-runs'
    return rows, manifests, runtimes, hashes, duplicate_episodes, calls, job_keys, dict(totals), reused_totals, call_runtimes


def audit_decisions(rows, cases, calls, job_keys):
    from native_interactive_execution import player_header, npc_header, configure
    configure()
    audit = Counter()
    for k, row in rows.items():
        cid, seed, persona, backend = k
        case = cases[cid]
        for turn in row['turns']:
            stage = 'npc_choice' if turn['role'] == 'npc' else 'player'
            jk = (cid, seed, persona, backend, stage, turn['turn'])
            record = calls[job_keys[jk]]
            assert record['parsed'] == turn['decision']
            assert record['messages'][0]['content'] == (npc_header(case, persona)
                if turn['role'] == 'npc' else player_header(case))
            assert 'backend' not in record['messages'][0]['content'].lower()
            if turn['lower_decision'] is not None:
                lower = calls[job_keys[(cid, seed, persona, backend, 'npc_primitive', turn['turn'])]]
                assert lower['parsed'] == turn['lower_decision']
                assert lower['messages'][0]['content'] == npc_header(case, persona)
                audit['lower_decisions_resolved'] += 1
            audit['recorded_turn_decisions_resolved'] += 1
        if row['protocol_error']:
            t = len(row['turns'])
            stage = {'invalid_player_json': 'player', 'invalid_npc_choice_json': 'npc_choice',
                     'invalid_npc_primitive_json': 'npc_primitive'}[row['protocol_error']]
            assert calls[job_keys[(cid, seed, persona, backend, stage, t)]]['parsed'] is None
            audit['protocol_failure_decisions_resolved'] += 1
    for cid, seed, persona, _ in rows:
        left, right = (cid, seed, persona, BACKENDS[0]), (cid, seed, persona, BACKENDS[1])
        if _ != BACKENDS[0]:
            continue
        assert left in rows and right in rows
        jl = (cid, seed, persona, BACKENDS[0], 'npc_choice', 0)
        jr = (cid, seed, persona, BACKENDS[1], 'npc_choice', 0)
        assert job_keys[jl] == job_keys[jr], ('Initial policy input differs by backend', cid)
        a, b = rows[left], rows[right]
        assert a['opening'] == b['opening']
        assert a['turns'][:1] == b['turns'][:1], ('First one-step action differs by backend', cid)
        audit['paired_common_initial_input_and_action_checks'] += 1
    # Visible speech may later legitimately disclose motivations. This is a
    # structural header check, not a ban on private text becoming public speech.
    for record in calls.values():
        case = cases[record['case_id']]
        if record['stage'] == 'player':
            assert record['messages'][0]['content'] == player_header(case)
            assert 'Original authored task:' not in record['messages'][0]['content']
            for field in ['short_motivation', 'mid_motivation', 'long_motivation']:
                value = case['quest'][field].strip()
                if len(value) > 25 and value not in case['requester_persona']:
                    assert value not in record['messages'][0]['content']
            audit['player_header_private_goal_checks'] += 1
    return dict(audit)


def verify_replay(rows, cases, calls, job_keys, modules):
    """Re-execute every supplied episode on CPU and reconstruct exact input keys.

    This checks driver serialization/privacy plumbing, not model causal content.
    It intentionally uses the pinned driver's public-view/spec functions and
    the original native engine; independent outcome counting is above.
    """
    import native_interactive_execution as driver
    from light_npc_episodes import ViewerHost, execute, material_state, chosen_command
    from light_native_gate import parse_event
    from native_owned_container_qualification import event_id
    audit = Counter()
    for key, row in rows.items():
        case = cases[row['case_id']]
        graph = modules[0].from_json(case['quest']['graph'])
        game = {'case': case, 'seed': row['seed'], 'persona': row['persona'], 'backend': row['backend'],
                'graph': graph, 'host': ViewerHost(graph), 'visible': {'npc': [], 'player': []},
                'goal_bound_ever': False, 'goal_physical_ever': False, 'npc_give_request_ever': False}

        def check_job(stage, spec, turn):
            job = driver.make_job(game, stage, spec, turn)
            expected = job_keys[(*key, stage, turn)]
            assert decision_key(job) == expected, ('Reconstructed input mismatch', key, stage, turn)
            record = calls[expected]
            assert job['messages'] == record['messages'] and job['schema'] == record['schema']
            audit['exact_input_reconstructions'] += 1
            return record['parsed']

        for turn in [row['opening'], *row['turns']]:
            if turn['turn'] >= 0:
                if turn['role'] == 'player':
                    answer = check_job('player', driver.player_spec(game, modules), turn['turn'])
                    assert chosen_command(answer) == turn['command']
                else:
                    spec, paths = driver.selector_spec(game, modules)
                    answer = check_job('npc_choice', spec, turn['turn'])
                    target = ALIASES.get(answer['action'])
                    if target:
                        assert paths[target] and len(paths[target]) == turn['path_length']
                        if len(paths[target]) == 1 or row['backend'] == 'native_skill':
                            assert paths[target][0] == turn['command']
                        else:
                            lower = check_job('npc_primitive', driver.primitive_spec(game, target, modules), turn['turn'])
                            assert chosen_command(lower) == turn['command']
                    else:
                        assert chosen_command(answer) == turn['command']
            actor = graph.get_node(row['actor_id'] if turn['role'] == 'npc' else row['requester_id'])
            parsed = parse_event(graph, actor, turn['command'], *modules[1:])
            ident = event_id(parsed, modules)
            assert (list(ident[1]) if ident else []) == turn['target_node_ids']
            random.seed(row['seed'] + int(row['case_id'][:7], 16)*1000 + turn['turn'] + 1000)
            actual = execute(game['host'], actor, turn['command'], *modules[1:])
            for field in actual:
                assert actual[field] == turn[field], ('Native replay differs', key, turn['turn'], field)
            f = event_readback(row, turn)
            game['goal_bound_ever'] |= f['bound']; game['goal_physical_ever'] |= f['physical']
            game['npc_give_request_ever'] |= f['request']
            for role, viewer in [('npc', row['actor_id']), ('player', row['requester_id'])]:
                seen = [m['text'] for m in actual['messages'] if m['viewer'] == viewer]
                if role == turn['role']:
                    seen.insert(0, 'Your attempted command: ' + turn['command'])
                    if actual.get('error'):
                        seen.append('Native rejection: ' + actual['error'])
                game['visible'][role].extend(seen)
            audit['native_events_replayed_including_opening'] += 1
        if row['protocol_error']:
            t = len(row['turns'])
            if row['protocol_error'] == 'invalid_player_json':
                assert check_job('player', driver.player_spec(game, modules), t) is None
            else:
                spec, paths = driver.selector_spec(game, modules)
                answer = check_job('npc_choice', spec, t)
                if row['protocol_error'] == 'invalid_npc_choice_json':
                    assert answer is None
                else:
                    target = ALIASES[answer['action']]
                    assert len(paths[target]) == 2
                    assert check_job('npc_primitive', driver.primitive_spec(game, target, modules), t) is None
        assert material_state(graph) == row['final_state']
        audit['entire_episodes_replayed'] += 1
    return {'status': 'PASS', **dict(audit), 'model_calls': 0, 'API_calls': 0}


def summarize(matrix, fields):
    x = np.asarray(matrix, dtype=float)
    assert x.ndim == 2 and len(x)
    if len(x) not in _BOOTSTRAP_WEIGHTS:
        rng = np.random.default_rng(BOOTSTRAP_SEED)
        _BOOTSTRAP_WEIGHTS[len(x)] = rng.multinomial(len(x), np.full(len(x), 1/len(x)), size=BOOTSTRAPS)/len(x)
    weights = _BOOTSTRAP_WEIGHTS[len(x)]
    low, high = np.quantile(weights @ x, [.025, .975], axis=0)
    means = x.mean(axis=0)
    return {field: {'mean': float(means[i]), 'graph_bootstrap_95': [float(low[i]), float(high[i])],
                    'independent_graphs': len(x)} for i, field in enumerate(fields)}


def raw_counts(rows):
    counts = Counter(episodes=len(rows))
    event_counts = Counter(); errors = Counter(); stops = Counter(); final_modes = Counter()
    for row in rows:
        stops[row['stop']] += 1
        final_modes[str(row['final_state'][row['goal_item_id']].get('equipped'))] += 1
        for h in row['turns']:
            event_counts[(h['role'], h['event_type'], 'successful' if success(h) else 'rejected_or_failed')] += 1
            if h.get('error'):
                errors[h['role'] + ': ' + h['error']] += 1
    return {'episodes': counts['episodes'], 'stop': dict(stops), 'final_source_equipped_mode': dict(final_modes),
            'event_counts': {'/'.join(k): v for k, v in sorted(event_counts.items())},
            'native_error_texts': dict(errors)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--call-runs', type=Path, nargs='*', default=[])
    ap.add_argument('--source', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--profile', action='store_true', help='Report only the two source-selected profile worlds.')
    ap.add_argument('--verify-replay', action='store_true', help='CPU replay all supplied episodes and exact inputs.')
    args = ap.parse_args()
    if args.verify_replay:
        assert os.environ.get('PYTHONHASHSEED') == '0', 'Exact native view reconstruction needs the driver PYTHONHASHSEED=0.'
    from light_native_gate import load_event_modules
    from light_npc_episodes import CACHE
    loaded = read_runs(args.runs, args.call_runs, args.profile)
    rows, manifests, runtimes, hashes, duplicate_episodes, calls, job_keys, costs, reused, call_runtimes = loaded
    assert manifests[0]['driver_sha256'] == sha(Path(__file__).with_name('native_interactive_execution.py'))
    assert manifests[0]['skills_sha256'] == sha(Path(__file__).with_name('native_interactive_skills.py'))
    source = args.source or Path(manifests[0]['source'])
    assert sha(source) == manifests[0]['source_sha256']
    hashes[str(source)] = sha(source)
    modules = load_event_modules(CACHE / 'sources/LIGHT')
    cases = load_sources(source, modules)
    if args.profile:
        ids = [next(cid for cid, c in cases.items() if c['goal_kind'] == kind)
               for kind in ['give', next(c['goal_kind'] for c in cases.values() if c['goal_kind'] != 'give')]]
    else:
        ids = list(cases)
    expected = {(cid, seed, persona, backend) for cid in ids for seed in SEEDS
                for persona in PERSONAS for backend in BACKENDS}
    assert set(rows) == expected, ('Incomplete or unexpected factorial', len(rows), len(expected))
    data = {k: metrics(row, cases[row['case_id']]) for k, row in rows.items()}
    fields = list(next(iter(data.values())))
    arrays = {k: np.asarray([value[f] for f in fields]) for k, value in data.items()}
    decision_audit = audit_decisions(rows, cases, calls, job_keys)
    replay = verify_replay(rows, cases, calls, job_keys, modules) if args.verify_replay else {'status': 'NOT_REQUESTED'}
    groups = {'all': ids, 'Give': [cid for cid in ids if cases[cid]['goal_kind'] == 'give'],
              'nonGive': [cid for cid in ids if cases[cid]['goal_kind'] != 'give']}
    groups.update({kind: [cid for cid in ids if cases[cid]['goal_kind'] == kind]
                   for kind in sorted({cases[cid]['goal_kind'] for cid in ids})})
    cells, contrasts, raw = {}, {}, {}
    graph_vectors = {(cid, persona, backend): np.mean([arrays[cid, seed, persona, backend] for seed in SEEDS], axis=0)
                     for cid in ids for persona in PERSONAS for backend in BACKENDS}

    def graph_vector(cid, persona, backend):
        return graph_vectors[cid, persona, backend]

    for group, cids in groups.items():
        if not cids:
            continue
        for persona in PERSONAS:
            for backend in BACKENDS:
                key = '/'.join([group, persona, backend])
                matrix = [graph_vector(cid, persona, backend) for cid in cids]
                cells[key] = summarize(matrix, fields)
                selected_rows = [rows[cid, seed, persona, backend] for cid in cids for seed in SEEDS]
                raw[key] = raw_counts(selected_rows)
                raw[key]['metric_sums'] = {f: float(sum(data[row_key(r)][f] for r in selected_rows)) for f in fields}
        for persona in PERSONAS:
            contrasts[f'{group}/{persona}/native_skill_minus_model_steps'] = summarize(
                [graph_vector(cid, persona, 'native_skill') - graph_vector(cid, persona, 'model_steps') for cid in cids], fields)
        for backend in BACKENDS:
            contrasts[f'{group}/{backend}/agreeable_minus_firm'] = summarize(
                [graph_vector(cid, 'agreeable', backend) - graph_vector(cid, 'firm', backend) for cid in cids], fields)
        contrasts[f'{group}/backend_x_trait_interaction'] = summarize(
            [graph_vector(cid, 'agreeable', 'native_skill') - graph_vector(cid, 'agreeable', 'model_steps')
             - graph_vector(cid, 'firm', 'native_skill') + graph_vector(cid, 'firm', 'model_steps') for cid in cids], fields)
    profile_ids = [next(cid for cid, c in cases.items() if c['goal_kind'] == 'give'),
                   next(cid for cid, c in cases.items() if c['goal_kind'] != 'give')]
    result = {
        'status': 'COMPLETE_PROFILE_CPU_READBACK' if args.profile else 'COMPLETE',
        'experiment': 'E80', 'model': manifests[0]['model'], 'worlds': len(ids), 'episodes': len(rows),
        'seeds': SEEDS, 'personas': PERSONAS, 'backends': BACKENDS,
        'group_worlds': {k: len(v) for k, v in groups.items()}, 'profile_case_ids_in_source_order': profile_ids,
        'duplicate_identical_episode_records_excluded': duplicate_episodes,
        'physical_episode_records_read': len(rows) + duplicate_episodes,
        'metrics': fields, 'cells': cells, 'contrasts': contrasts, 'raw_counts': raw,
        'decision_input_audit': decision_audit, 'CPU_native_replay': replay,
        'costs': {**costs, 'unique_decision_keys': len(calls), 'unique_job_keys': len(job_keys),
                  'reused_call_records_read': reused, 'new_cloud_calls': 0,
                  'supplied_run_GPU_hours_including_profiles': sum(r['wall_seconds'] + r['model_load_seconds']
                                                               for r in call_runtimes)/3600},
        'episode_runtimes': runtimes, 'cost_runtimes_including_call_dependencies': call_runtimes,
        'source_sha256': hashes, 'report_script_sha256': sha(Path(__file__)),
        'pinned_driver_sha256': manifests[0]['driver_sha256'], 'pinned_skills_sha256': manifests[0]['skills_sha256'],
        'definitions': {
            'unit': 'Three seeds averaged within source graph; 4000 paired graph-bootstrap pointwise 95% intervals.',
            'contrast_orientation': 'Backend is native_skill minus model_steps; trait is agreeable minus firm; interaction is the difference of backend contrasts.',
            'successful_native_event': 'legal and executed and not stochastic_failure; exact initial source entity ID plus actual before/after effects.',
            'npc_goal_bound_ever': 'Successful NPC event with the exact native event type and target IDs bound in the original source initial graph.',
            'npc_goal_physical_ever': 'Bound source Give to authored recipient, exact wear/wield equipped mode by NPC, or actual NPC Eat/Drink/Ingest consumption of bound source.',
            'equipment': 'Any successful Wear/Wield/Equip and final equipped mode are also reported separately. Generic equip mode is not silently equated to wear/wield.',
            'ever_vs_final': 'Goal, NPC source Give, player Get/Steal, equipment/consumption are historical events; final direct and ultimate possession are separate. They may co-occur.',
            'speech': 'Only successful native Say/Tell/Whisper events transmit utterance. Opening common request is excluded from the 8+8 action/count metrics.',
            'skills': 'Only already selected two-primitive outcomes trigger the executor contrast. Every primitive uses one opportunity and the player may act between them.',
            'triggered_subsets': 'Two-step choices and realized choices are post-treatment descriptions, not separate causal effect estimates or independent samples.',
            'costs': 'All physically incurred calls in supplied distinct directories count once; identical profile/full episodes and repeated decision inputs are separately deduplicated.',
        },
        'scope': [
            'All source worlds and all configured seeds retained, including zero-player-asset worlds, rejected actions, deaths and protocol failures.',
            'Both arms share a strong high-level outcome/native-action/speech selector. This is a closed-loop configuration comparison, not a raw-model-vs-scaffold contrast.',
            'Model identity includes both NPC and simulated player; there are no human experience, private welfare, mutual benefit or full quest completion claims.',
            'Original authored atomic goal and assigned player request can conflict; obtaining the item by player Get/Steal is not NPC voluntary compliance.',
            'Already exposed same-engine worlds are not a new-world or human-player generalization test.',
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'experiment', 'model', 'worlds', 'episodes', 'group_worlds',
                                           'duplicate_identical_episode_records_excluded', 'decision_input_audit',
                                           'CPU_native_replay', 'costs']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
