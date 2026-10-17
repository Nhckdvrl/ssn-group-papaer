#!/usr/bin/env python3
"""E84 CPU witnesses in unchanged authored LIGHT graphs. No model or new world.

Source qualification is separate from character motives and mutual benefit.
Every primitive uses the same original typed constructor/guard as E81. The
finite witness search reports what it found; no witness is not impossibility.
"""
import argparse
from collections import Counter
import hashlib
import json
import random
from pathlib import Path
import time

from light_native_gate import load_event_modules, parse_event
from light_npc_episodes import CACHE, ViewerHost, material_state
from native_cooperation_episodes import identity, header
from cooperation_source_inventory import EVENT

WB = Path(__file__).resolve().parents[1]
SEED = 8401


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canonical_sha(g):
    return hashlib.sha256(json.dumps(json.loads(g.to_json()), sort_keys=True).encode()).hexdigest()


def load_lines(p):
    return [json.loads(s) for s in Path(p).read_text().splitlines() if s]


def owner(g, item_id):
    n = g.get_node(item_id) if item_id else None
    seen = set()
    while n is not None and n.node_id not in seen:
        seen.add(n.node_id)
        if n.agent:
            return n.node_id
        if n.room:
            return None
        n = n.get_container()
    return None


def listed(g, actor, event_type, ids, modules):
    """E81's ordinary tool boundary: enumerate first, then native guard.

    Some upstream constructors assume that target lookup already checked
    visibility/ownership; a hand-bound ID is not a licence to bypass lookup.
    """
    cls = getattr(modules[1], event_type)
    return any(identity(e) == [event_type, ids] for e in cls.get_valid_actions(g, actor))


def goal_event(g, q, modules):
    actor = g.get_node(q['actor_id'])
    if actor is None or actor.get_prop('dead'):
        return None, 'actor_dead_or_absent'
    iid, tid, verb = q['item_id'], q['target_id'], q['verb']
    initial = q['initial_native_identity']
    if verb in EVENT and iid:
        item = g.get_node(iid)
        if item is None:
            return None, 'bound_item_absent'
        targets = [iid]
        if verb == 'get':
            # "get X" has an implicit current source container. An explicit
            # authored "from Y" retains its source binding instead.
            container = tid if ' from ' in q['goal'] else item.get_container().node_id
            targets.append(container)
        elif verb in ['give', 'put']:
            if tid is None:
                return None, 'target_not_uniquely_bound'
            targets.append(tid)
        elif verb == 'steal':
            targets.append(tid or q['item_owner_agent_id'])
        cls = getattr(modules[1], EVENT[verb])
    elif initial:
        cls = getattr(modules[1], initial[0])
        targets = initial[1]
    else:
        try:
            e = parse_event(g, actor, q['goal'], *modules[1:])
        except Exception as exc:
            return None, 'native_parse_exception:' + type(exc).__name__
        if isinstance(e, modules[2]):
            return None, e.view_as(actor)
        return (e, None) if listed(g, actor, type(e).__name__, identity(e)[1], modules) else (None, 'not_in_original_native_action_catalogue')
    nodes = [g.get_node(n) for n in targets]
    if any(n is None for n in nodes):
        return None, 'bound_target_absent'
    if not listed(g, actor, cls.__name__, targets, modules):
        return None, 'not_in_original_native_action_catalogue'
    try:
        e = cls.construct_from_args(actor, nodes, '')
    except Exception as exc:
        return None, 'native_guard_exception:' + type(exc).__name__ + ':' + str(exc)
    return (None, e.view_as(actor)) if isinstance(e, modules[2]) else (e, None)


class Witness:
    def __init__(self, graph_json, quests, modules):
        self.modules, self.quests = modules, quests
        self.graph = modules[0].from_json(graph_json)
        self.host = ViewerHost(self.graph)
        self.steps, self.strict = [], [False, False]
        self.ever = [False, False]
        self.update()

    def physical(self, q):
        iid, aid, verb, tid = q['item_id'], q['actor_id'], q['verb'], q['target_id']
        item = self.graph.get_node(iid) if iid else None
        if item is None:
            return None
        parent = item.get_container().node_id if item.get_container() else None
        if verb in ['get', 'steal']:
            return owner(self.graph, iid) == aid
        if verb in ['give', 'put']:
            return parent == tid if tid is not None else None
        if verb in ['wear', 'wield']:
            return parent == aid and item.get_prop('equipped') == verb
        if verb in ['eat', 'drink']:
            return parent == 'VOID' and any(s.get('successful') and s['actor_id'] == aid
                and s['event_type'] in ['EatEvent', 'DrinkEvent', 'IngestEvent']
                and s['target_node_ids'] and s['target_node_ids'][0] == iid for s in self.steps)
        # Remove/Drop/Hit/Hug/Follow strict events are not replaced by a
        # convenient final-state heuristic or a narrative completion flag.
        return None

    def update(self):
        for i, q in enumerate(self.quests):
            self.ever[i] |= bool(self.physical(q))

    def status(self):
        physical = [self.physical(q) for q in self.quests]
        # Only Get/Steal acquisition can be accomplished by another actor's
        # transfer without executing the original authored event.
        realized = [self.strict[i] or (q['verb'] in ['get', 'steal'] and self.ever[i])
                    for i, q in enumerate(self.quests)]
        return {'strict_goal_ever': list(self.strict), 'physical_ever': list(self.ever),
                'physical_final': physical, 'strict_or_acquisition_ever': realized,
                'both_strict_or_acquisition_ever': all(realized)}

    def run(self, aid, event_type, ids, purpose):
        g, m = self.graph, self.modules
        before, before_hash = material_state(g), canonical_sha(g)
        row = {'actor_id': aid, 'event_type': event_type, 'target_node_ids': ids,
               'purpose': purpose, 'seed': SEED + len(self.steps), 'graph_before_sha256': before_hash}
        actor, nodes = g.get_node(aid), [g.get_node(n) for n in ids]
        if actor is None or any(n is None for n in nodes):
            row.update(legal=False, error='actor_or_bound_target_absent')
            self.steps.append(row)
            return False
        matches = []
        for i, q in enumerate(self.quests):
            goal, _ = goal_event(g, q, m)
            if q['actor_id'] == aid and goal is not None and identity(goal) == [event_type, ids]:
                matches.append(i)
        try:
            if not listed(g, actor, event_type, ids, m):
                row.update(legal=False, error='not_in_original_native_action_catalogue')
            else:
                e = getattr(m[1], event_type).construct_from_args(actor, nodes, '')
                row['legal'] = not isinstance(e, m[2])
                if not row['legal']:
                    row['error'] = e.view_as(actor)
            if row['legal']:
                assert identity(e) == [event_type, ids]
                row['command'] = e.to_canonical_form()
                random.seed(row['seed'])
                e.execute(self.host)
                row.update(executed=bool(e.executed), stochastic_failure=bool(getattr(e, 'failed', False)))
                row['successful'] = row['executed'] and not row['stochastic_failure']
                if row['successful']:
                    for i in matches:
                        self.strict[i] = True
        except Exception as exc:
            row.update(native_exception=type(exc).__name__ + ':' + str(exc), successful=False)
        after = material_state(g)
        row['graph_after_sha256'] = canonical_sha(g)
        row['material_delta'] = {n: {'before': before.get(n), 'after': after.get(n)}
                                 for n in set(before) | set(after) if before.get(n) != after.get(n)}
        if not row.get('legal'):
            assert row['graph_after_sha256'] == before_hash
        self.steps.append(row)
        self.update()
        return bool(row.get('successful'))

    def goal(self, index):
        q = self.quests[index]
        if self.strict[index] or q['verb'] in ['get', 'steal'] and self.ever[index]:
            return True
        e, error = goal_event(self.graph, q, self.modules)
        if e is None:
            self.steps.append({'actor_id': q['actor_id'], 'event_type': None, 'purpose': 'original_goal',
                               'legal': False, 'error': error, 'goal_index': index})
            return False
        return self.run(q['actor_id'], type(e).__name__, identity(e)[1], 'original_goal_'+str(index))

    def help(self, index, mode='give'):
        q, other = self.quests[index], self.quests[1-index]
        iid, recipient, provider = q['item_id'], q['actor_id'], other['actor_id']
        if not iid or owner(self.graph, iid) == recipient:
            return False
        if owner(self.graph, iid) != provider:
            return False
        item = self.graph.get_node(iid)
        # Traverse only the real source ownership chain, never an invented bag.
        while item.get_container().node_id != provider:
            parent = item.get_container().node_id
            if not self.run(provider, 'GetObjectEvent', [iid, parent], 'retrieve_own_nested_asset'):
                return False
        if item.get_prop('equipped'):
            if not self.run(provider, 'RemoveObjectEvent', [iid], 'remove_before_transfer'):
                return False
        if mode == 'give':
            return self.run(provider, 'GiveObjectEvent', [iid, recipient], 'peer_give_existing_goal_item')
        if not self.run(provider, 'DropObjectEvent', [iid], 'peer_release_existing_goal_item'):
            return False
        parent = item.get_container().node_id
        return self.run(recipient, 'GetObjectEvent', [iid, parent], 'recipient_get_released_item')

    def export(self):
        return {'steps': self.steps, 'status': self.status(),
                'final_material_state': material_state(self.graph),
                'final_graph_sha256': canonical_sha(self.graph)}


def initial_status(gtext, qs, modules):
    w = Witness(gtext, qs, modules)
    out = []
    for q in qs:
        e, error = goal_event(w.graph, q, modules)
        out.append({'typed_legal': e is not None, 'identity': identity(e) if e else None,
                    'native_error': error, 'physical_initial': w.physical(q)})
    return out


def qualify(c, gtext, modules):
    qs = [c['quest_a'], c['quest_b']]
    out = {k: c[k] for k in ['candidate_id', 'graph_sha256', 'relationship_types']}
    out['initial_goals'] = initial_status(gtext, qs, modules)
    out['directions'] = []
    for i, q in enumerate(qs):
        if not q['item_id'] or q['item_owner_agent_id'] != qs[1-i]['actor_id']:
            continue
        direction = {'recipient_index': i, 'item_id': q['item_id'], 'methods': {}, 'solo_alternatives': {}}
        for mode in ['give', 'drop_get']:
            w = Witness(gtext, qs, modules)
            w.help(i, mode)
            acquired = owner(w.graph, q['item_id']) == q['actor_id']
            if acquired:
                w.goal(i)
            direction['methods'][mode] = {'acquired': acquired, 'goal_realized': w.status()['strict_or_acquisition_ever'][i],
                                          'witness': w.export()}
        source = modules[0].from_json(gtext)
        parent = source.get_node(q['item_id']).get_container().node_id
        for event_type, ids in [('GetObjectEvent', [q['item_id'], parent]),
                                ('StealObjectEvent', [q['item_id'], qs[1-i]['actor_id']])]:
            w = Witness(gtext, qs, modules)
            w.run(q['actor_id'], event_type, ids, 'unilateral_initial_alternative')
            direction['solo_alternatives'][event_type] = {'acquired': owner(w.graph, q['item_id']) == q['actor_id'],
                                                         'witness': w.export()}
        out['directions'].append(direction)
    plans = [['g0', 'g1', 'h0', 'h1', 'g0', 'g1'], ['h0', 'h1', 'g0', 'g1'],
             ['h1', 'h0', 'g1', 'g0'], ['h0', 'g0', 'h1', 'g1'], ['h1', 'g1', 'h0', 'g0']]
    out['joint_witnesses'] = []
    for plan in plans:
        w = Witness(gtext, qs, modules)
        for task in plan:
            (w.goal if task[0] == 'g' else w.help)(int(task[1]))
        out['joint_witnesses'].append({'plan': plan, 'witness': w.export()})
    out['joint_found'] = any(x['witness']['status']['both_strict_or_acquisition_ever'] for x in out['joint_witnesses'])
    out['qualification'] = ('NATIVE_JOINT_ATOMIC_OR_ACQUISITION_WITNESS' if out['joint_found']
                            else 'NO_JOINT_WITNESS_IN_REGISTERED_NATIVE_PATHS_NOT_IMPOSSIBILITY')
    return out


def snapshot(c, result, graph_json):
    qs = [c['quest_a'], c['quest_b']]
    case = {'case_id': c['candidate_id'], 'graph_sha256': c['graph_sha256'],
            'actor_ids': [q['actor_id'] for q in qs],
            'quests': [{**q['quest'], 'source_file': q['file'], 'graph': graph_json} for q in qs],
            'goal_identities': [q['initial_native_identity'] for q in qs],
            'goal_bindings': [{k: q.get(k) for k in ['actor_id', 'goal', 'file', 'verb', 'item_id', 'target_id', 'initial_native_identity',
                'item_owner_agent_id', 'initial_item_parent_id', 'item_initial_equipped']} for q in qs],
            'relationship_types': c['relationship_types'], 'qualification': result,
            'scope': 'Original independently authored purposes, not a mutual-benefit gold label or proof cooperation is necessary.'}
    # Reuse the actual E81 private-role header without its single-source score.
    case['private_header_sha256'] = [hashlib.sha256(header(case, i).encode()).hexdigest() for i in [0, 1]]
    return case


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=CACHE/'runs/e84_independent_goal_source')
    ap.add_argument('--out', type=Path, default=CACHE/'runs/e84_native_qualification')
    ap.add_argument('--report', type=Path, default=WB/'results/E84_native_qualification.json')
    ap.add_argument('--prior-attempt', type=Path)
    a = ap.parse_args(); a.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    modules = load_event_modules(CACHE/'sources/LIGHT')
    graphs = {r['graph_sha256']: r['graph_json'] for r in load_lines(a.source/'graphs.jsonl')}
    quests = {r['file']: r for r in load_lines(a.source/'quests.jsonl')}
    candidates = load_lines(a.source/'candidates.jsonl')
    pairs = load_lines(a.source/'co_present_pairs.jsonl')
    cross = [c for c in candidates if 'cross_directly_held_distinct_goal_items' in c['relationship_types']]
    cross_ids = {c['candidate_id'] for c in cross}
    ordered = cross + [c for c in candidates if c['candidate_id'] not in cross_ids]
    results, cross_cases = [], []
    raw_path = a.out/'candidate_witnesses.jsonl'
    with raw_path.open('w') as raw:
        for c in ordered:
            result = qualify(c, graphs[c['graph_sha256']], modules)
            results.append(result);raw.write(json.dumps(result, ensure_ascii=False)+'\n');raw.flush()
            if c['candidate_id'] in cross_ids:
                cross_cases.append(snapshot(c, result, graphs[c['graph_sha256']]))
                if len(cross_cases) == len(cross):
                    file = a.out/'cross_snapshots.jsonl'
                    file.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in cross_cases))
                    count = sum(r['qualification']['joint_found'] for r in cross_cases)
                    progress = {'status': 'CROSS_COMPLETE', 'source_pairs': len(cross_cases),
                        'source_graphs': len({r['graph_sha256'] for r in cross_cases}),
                        'joint_witness_pairs': count, 'dataset': str(file), 'dataset_sha256': sha(file),
                        'all_source_pairs_retained': True, 'model_calls': 0}
                    (a.out/'cross_summary.json').write_text(json.dumps(progress, indent=2)+'\n')
                    print(json.dumps(progress), flush=True)
    # Every same-graph pair is checked for a partner's *authored* single action
    # enabling a previously blocked goal; no word filter or arbitrary help menu.
    activation = a.out/'authored_action_activations.jsonl'
    activation_counts = Counter(); activation_worlds = set()
    initial_cache = {}
    def initial(q):
        if q['file'] not in initial_cache:
            w = Witness(graphs[q['graph_sha256']], [q, q], modules)
            e, error = goal_event(w.graph, q, modules)
            initial_cache[q['file']] = {'legal': e is not None, 'physical': w.physical(q), 'error': error}
        return initial_cache[q['file']]
    with activation.open('w') as f:
        for pair in pairs:
            qs = [quests[pair['quest_a_file']], quests[pair['quest_b_file']]]
            for i in [0, 1]:
                if initial(qs[i])['legal'] or initial(qs[i])['physical']:
                    activation_counts['recipient_goal_initially_ready'] += 1;continue
                if not initial(qs[1-i])['legal']:
                    activation_counts['partner_authored_goal_initially_blocked'] += 1;continue
                w = Witness(graphs[pair['graph_sha256']], qs, modules)
                helper_success = w.goal(1-i)
                after, error = goal_event(w.graph, qs[i], modules)
                acquired = qs[i]['verb'] in ['get', 'steal'] and bool(w.physical(qs[i]))
                row = {'candidate_id': pair['candidate_id'], 'graph_sha256': pair['graph_sha256'],
                    'quest_files': [q['file'] for q in qs], 'recipient_index': i,
                    'helper_success': helper_success, 'recipient_goal_now_typed_legal': after is not None,
                    'recipient_acquired_without_strict_event': acquired, 'native_error_after': error}
                if helper_success and (after is not None or acquired):
                    w.goal(i);row['witness'] = w.export()
                    activation_counts['native_action_enabled_strict_or_acquisition'] += 1
                    activation_worlds.add(pair['graph_sha256'])
                else:
                    activation_counts['no_activation_observed'] += 1
                    row['helper_witness'] = w.export()
                f.write(json.dumps(row, ensure_ascii=False)+'\n')
    relation_counts = {}
    for rel in sorted({x for c in candidates for x in c['relationship_types']}):
        subset = [r for r in results if rel in r['relationship_types']]
        qualified = [r for r in subset if r['joint_found']]
        relation_counts[rel] = {'candidate_pairs': len(subset), 'candidate_graphs': len({r['graph_sha256'] for r in subset}),
            'joint_witness_pairs': len(qualified), 'joint_witness_graphs': len({r['graph_sha256'] for r in qualified})}
    report = {'experiment': 'E84', 'status': 'COMPLETE_CPU_NATIVE_QUALIFICATION',
        'script_sha256': sha(__file__), 'source_summary': str(a.source/'summary.json'),
        'source_counts': json.loads((a.source/'summary.json').read_text())['counts'],
        'source_hashes': {str(a.source/name): sha(a.source/name) for name in
            ['graphs.jsonl', 'quests.jsonl', 'candidates.jsonl', 'co_present_pairs.jsonl', 'binding_alternatives.jsonl']},
        'native_seed': SEED, 'relation_counts': relation_counts,
        'authored_action_activation': {**dict(activation_counts), 'enabled_graphs': len(activation_worlds)},
        'cross_summary': json.loads((a.out/'cross_summary.json').read_text()),
        'raw_assets': {str(p): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in
            [raw_path, activation, a.out/'cross_snapshots.jsonl']},
        'scope': ['No source graph, asset, reward, persona, motivation, timeline or goal edited.',
            'Joint original atomic events or material acquisition are not complete private purpose, mutual benefit, necessity of cooperation or a contract.',
            'The five fixed native schedules verify concrete existing paths; no witness is not an impossibility proof.',
            'Get/Steal by actual peer transfer and strict original Get/Steal events are separate fields.',
            'Initial native text bindings and source surface ambiguities remain in the source assets; typed execution never rebinds similarly named targets.'],
        'model_calls': 0, 'cloud_calls': 0, 'GPU_hours': 0, 'wall_seconds': time.monotonic()-started}
    if a.prior_attempt:
        report['invalid_constructor_only_attempt'] = {'path': str(a.prior_attempt), 'sha256': sha(a.prior_attempt),
            'status': 'INVALID_MEASUREMENT_AND_ABORTED',
            'reason': 'The earlier qualifier used constructors without original action enumeration. Constructors alone allow targets that are outside the actual native tool catalogue. No model experiment used that output.'}
    a.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    (a.out/'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': report['status'], 'relation_counts': relation_counts,
        'authored_action_activation': report['authored_action_activation'], 'wall_seconds': report['wall_seconds']}), flush=True)


if __name__ == '__main__':
    main()
