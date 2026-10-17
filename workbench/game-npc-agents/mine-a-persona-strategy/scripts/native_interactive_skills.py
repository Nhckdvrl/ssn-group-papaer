#!/usr/bin/env python3
"""Bound, visible-affordance LIGHT skills for an already selected outcome.

These helpers never select a social outcome, execute on the live graph, steal,
move an actor, or bundle two primitives into a single game opportunity. The
caller executes only path[0], lets the other character act, then replans.
"""
import random

from light_native_gate import parse_event
from light_npc_episodes import ViewerHost, execute
from native_owned_container_qualification import event_id

GOAL_EVENTS = {'GiveObjectEvent', 'WearEvent', 'WieldEvent', 'EatEvent', 'DrinkEvent'}


def _identity(event, modules):
    value = event_id(event, modules)
    return [value[0], list(value[1])] if value is not None else None


def snapshot_target_identity(case, modules):
    """Return JSON-friendly initial ``goal``/``request`` event+entity bindings.

    Store the result as case['native_target_identities'] to reuse it. The
    initial case graph, not a later same-name substitute item, defines both
    bindings. This function leaves the case and its graph unchanged.
    """
    graph = modules[0].from_json(case['quest']['graph'])
    actor = graph.get_node(case['actor_id'])
    assert actor is not None and not actor.get_prop('dead')
    result = {}
    for target, command in [('goal', case['goal_command']), ('request', case['request_command'])]:
        identity = _identity(parse_event(graph, actor, command, *modules[1:]), modules)
        assert identity is not None, (target, command)
        assert identity[1] and identity[1][0] == case['item_id'], (target, identity)
        result[target] = identity
    assert result['goal'][0] in GOAL_EVENTS
    assert result['request'] == ['GiveObjectEvent', [case['item_id'], case['requester_id']]]
    return result


def _candidates(graph, actor, identity, modules):
    """Only native, currently public legal-menu affordances; exact ID reparse."""
    event_type, ids = identity
    cls = getattr(modules[1], event_type)
    for command in sorted({event.to_canonical_form() for event in cls.get_valid_actions(graph, actor)
                           if _identity(event, modules) == [event_type, list(ids)]}):
        parsed = parse_event(graph, actor, command, *modules[1:])
        if _identity(parsed, modules) == [event_type, list(ids)]:
            yield command


def _apply_checked(graph, case, command, expected, modules):
    """Validate actual native effects on a disposable fork; no synthetic edits."""
    actor = graph.get_node(case['actor_id'])
    parsed = parse_event(graph, actor, command, *modules[1:])
    if _identity(parsed, modules) != expected:
        return False
    row = execute(ViewerHost(graph), actor, command, *modules[1:])
    if not (row['legal'] and row.get('executed') and not row.get('stochastic_failure')
            and row['material_changed']):
        return False
    source = case['item_id']
    before, after = row['before'][source], row['after'][source]
    kind, ids = expected
    if kind == 'GetObjectEvent':
        return before['container'] == ids[1] and after['container'] == case['actor_id']
    if kind == 'RemoveObjectEvent':
        return (before['container'] == after['container'] == case['actor_id']
                and bool(before.get('equipped')) and not after.get('equipped'))
    if kind == 'GiveObjectEvent':
        return before['container'] == case['actor_id'] and after['container'] == ids[1]
    if kind in ['WearEvent', 'WieldEvent']:
        mode = {'WearEvent': 'wear', 'WieldEvent': 'wield'}[kind]
        return after['container'] == case['actor_id'] and after.get('equipped') == mode
    if kind in ['EatEvent', 'DrinkEvent']:
        return before['container'] == case['actor_id'] and after['container'] == 'VOID'
    raise AssertionError(('Unallowed skill event', expected))


def native_short_path(graph, case, target, modules):
    """Return a verified 1–2 primitive path for ``goal``/``request``, or None.

    Only a source-item Get or Remove can precede the exact initial bound
    event. Affordances come from the same upstream get_valid_actions used by
    the existing legal-command menu. No hidden inventory search or private
    partner goal is used. Already-achieved refers to the *current* physical
    state; historical ever-goal flags belong to the caller's event log.
    """
    assert target in ['goal', 'request']
    rng_state = random.getstate()
    try:
        bindings = case.get('native_target_identities') or snapshot_target_identity(case, modules)
        expected = [bindings[target][0], list(bindings[target][1])]
        assert expected[1][0] == case['item_id']
        initial_json = graph.to_json()
        fork = modules[0].from_json(initial_json)
        actor, item = fork.get_node(case['actor_id']), fork.get_node(case['item_id'])
        if actor is None or actor.get_prop('dead') or item is None:
            return None
        parent = item.get_container()
        if parent is None or parent.node_id == 'VOID' or (parent.agent and parent.node_id != actor.node_id):
            return None
        if (expected[0] in ['WearEvent', 'WieldEvent'] and parent.node_id == actor.node_id
                and item.get_prop('equipped') == {'WearEvent': 'wear', 'WieldEvent': 'wield'}[expected[0]]):
            return None
        for command in _candidates(fork, actor, expected, modules):
            check = modules[0].from_json(initial_json)
            if _apply_checked(check, case, command, expected, modules):
                return [command]
        prerequisites = []
        for cls in [modules[1].GetObjectEvent, modules[1].RemoveObjectEvent]:
            for event in cls.get_valid_actions(fork, actor):
                identity = _identity(event, modules)
                if identity[1] and identity[1][0] == case['item_id']:
                    prerequisites.append((event.to_canonical_form(), identity))
        for first, identity in sorted(prerequisites):
            branch = modules[0].from_json(initial_json)
            if not _apply_checked(branch, case, first, identity, modules):
                continue
            actor = branch.get_node(case['actor_id'])
            branch_json = branch.to_json()
            for last in _candidates(branch, actor, expected, modules):
                check = modules[0].from_json(branch_json)
                if _apply_checked(check, case, last, expected, modules):
                    return [first, last]
        return None
    finally:
        random.setstate(rng_state)
