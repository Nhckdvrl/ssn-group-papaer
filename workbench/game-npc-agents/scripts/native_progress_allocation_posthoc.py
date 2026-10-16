#!/usr/bin/env python3
"""POST-HOC, zero-model readback of E73/E75/E76 progress and source-item outcomes.

Run with the existing fgvd Python (numpy). No model calls. Optional CPU-only
native forks verify consumption-equivalent commands; historical scores unchanged.
Counts use successful native events and exact target node IDs, never utterances.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

DEFAULT_RUNS = Path('/home/xiang/.cache/game-npc-research/runs')
PERSONAS = ['firm', 'agreeable']
BOOTSTRAPS = 4000
BOOTSTRAP_SEED = 760073
SPEECH = {'TellEvent', 'SayEvent', 'WhisperEvent'}
NONMATERIAL = SPEECH | {'EmoteEvent', 'PointEvent', 'ExamineEvent', 'HugEvent'}
FIELDS = [
    'pre_success', 'pre_first_action', 'goal', 'request_distinct', 'other_source_give',
    'registered_terminal', 'pre_no_terminal', 'no_pre_no_terminal',
    'terminal_without_pre', 'request_including_aligned_goal',
    'other_item_give', 'other_item_give_requester', 'source_drop', 'source_consume',
    'any_speech', 'any_emote', 'any_examine', 'any_point', 'any_nonmaterial',
    'only_successful_nonmaterial', 'any_block', 'any_rejection_or_failed',
    'no_pre_other_item_give', 'no_pre_other_item_give_requester',
    'no_pre_any_speech', 'no_pre_any_emote', 'no_pre_any_examine',
    'no_pre_only_successful_nonmaterial', 'no_pre_any_block',
    'pre_no_terminal_source_drop', 'pre_no_terminal_source_consume',
    'pre_no_terminal_source_still_carried', 'source_consumed_without_bound_goal',
    'physical_goal_secondary', 'physical_registered_terminal_secondary',
    'pre_no_physical_terminal_secondary', 'no_pre_source_material_change',
    'source_drop_then_source_get', 'source_get_then_later_source_drop',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def success(h):
    return bool(h['legal'] and h.get('executed') and not h.get('stochastic_failure'))


def profile(events, history, source):
    """Mutually exclusive trace profile; precedence is stated, not a moral label."""
    if any(h['event_type'] == 'GiveObjectEvent' and h['target_node_ids'][0] != source for h in events):
        return 'other_item_give_present'
    if any(h.get('material_changed') for h in events):
        return 'other_material_event_present'
    if events and len(events) == len(history) and all(not h.get('material_changed') for h in events):
        return 'only_successful_nonmaterial_events'
    if any(h['event_type'] in NONMATERIAL for h in events):
        return 'nonmaterial_plus_rejected_or_failed_attempts'
    if history:
        return 'other_or_only_rejected_failed_attempts'
    return 'empty_history'


def readback(r, experiment):
    item, actor = r['goal_item_id'], r['actor_id']
    hs = r['history']; good = [h for h in hs if success(h)]
    pre_type = 'RemoveObjectEvent' if experiment == 'E73' else 'GetObjectEvent'
    required = r['state'] in ['equipped', 'retrieval']
    pre_indices = []
    gives = []
    native_goal = r.get('native_goal_identity')
    goal_events = []
    source_drops = []; source_consumes = []; source_gets = []; source_atomic_path = []
    if hs:
        initial = hs[0]['before'][item]
        if r['state'] == 'equipped':
            assert initial['container'] == actor and initial['equipped']
        elif r['state'] == 'retrieval':
            assert initial['container'] != actor and not initial['equipped']
        else:
            assert r['state'] == 'ready' and initial['container'] == actor and not initial['equipped']
    for i, h in enumerate(hs):
        if not success(h):
            continue
        targets = h['target_node_ids']; typ = h['event_type']
        if targets and targets[0] == item and typ in ['RemoveObjectEvent', 'GetObjectEvent',
                'GiveObjectEvent', 'DropObjectEvent', 'WearEvent', 'EquipObjectEvent',
                'WieldEvent', 'EatEvent', 'DrinkEvent', 'IngestEvent']:
            source_atomic_path.append(typ)
        if typ == 'GetObjectEvent' and targets and targets[0] == item:
            source_gets.append(i)
        if typ == pre_type and targets and targets[0] == item:
            if typ == 'RemoveObjectEvent':
                assert h['before'][item]['equipped'] and not h['after'][item]['equipped']
            else:
                assert h['before'][item]['container'] == targets[1]
                assert h['after'][item]['container'] == actor
            pre_indices.append(i)
        if typ == 'GiveObjectEvent' and targets and targets[0] == item:
            assert h['before'][item]['container'] == actor
            assert h['after'][item]['container'] == targets[1]
            gives.append((i, targets[1]))
        if native_goal is not None and [typ, targets] == native_goal:
            goal_events.append(i)
            if r['goal_kind'] == 'wear':
                assert h['after'][item]['equipped']
            elif r['goal_kind'] in ['eat', 'drink']:
                assert h['after'][item]['container'] == 'VOID'
        if typ == 'DropObjectEvent' and targets and targets[0] == item:
            assert h['before'][item]['container'] == actor and h['after'][item]['container'] != actor
            source_drops.append(i)
        if typ in ['EatEvent', 'DrinkEvent', 'IngestEvent'] and targets and targets[0] == item:
            assert h['before'][item]['container'] == actor and h['after'][item]['container'] == 'VOID'
            source_consumes.append(i)
    assert len(gives) <= 1
    receiver = gives[0][1] if gives else None
    recorded = r['first_recipient'] if experiment == 'E73' else r['first_source_recipient']
    assert receiver == recorded
    if experiment == 'E73':
        goal = receiver == r['goal_recipient_id']
        goal_events = [gives[0][0]] if goal else []
        kind = 'give'
    else:
        goal = bool(goal_events)
        assert goal == r['goal_executed']
        kind = r['goal_kind']
    # Aligned E73 requester IS authored A. Do not count one event twice.
    request_all = receiver is not None and receiver == r['requester_id']
    request = request_all and not goal
    other = receiver is not None and not goal and not request
    terminal = bool(goal or request or other)
    assert sum([goal, request, other, not terminal]) == 1
    pre = bool(pre_indices)
    physical_goal = goal or (kind in ['eat', 'drink'] and bool(source_consumes))
    physical_terminal = physical_goal or request or other
    if required:
        assert not terminal or (pre and min(pre_indices) < (goal_events[0] if goal else gives[0][0]))
    other_gives = [h for h in good if h['event_type'] == 'GiveObjectEvent' and h['target_node_ids'][0] != item]
    has_speech = any(h['event_type'] in SPEECH for h in good)
    has_emote = any(h['event_type'] == 'EmoteEvent' for h in good)
    has_examine = any(h['event_type'] == 'ExamineEvent' for h in good)
    only_nonmaterial = bool(good and len(good) == len(hs) and all(not h.get('material_changed') for h in good))
    requester_other = any(h['target_node_ids'][1] == r['requester_id'] for h in other_gives)
    block = any(h['event_type'] == 'BlockEvent' for h in good)
    values = dict(zip(FIELDS, [
        pre, bool(pre_indices and pre_indices[0] == 0), goal, request, other, terminal,
        pre and not terminal, not pre and not terminal, terminal and not pre,
        request_all, bool(other_gives), requester_other, bool(source_drops), bool(source_consumes),
        has_speech, has_emote, has_examine, any(h['event_type'] == 'PointEvent' for h in good),
        any(h['event_type'] in NONMATERIAL for h in good), only_nonmaterial, block,
        any(not success(h) for h in hs),
        not pre and bool(other_gives), not pre and requester_other,
        not pre and has_speech, not pre and has_emote, not pre and has_examine,
        not pre and only_nonmaterial, not pre and block,
        pre and not terminal and bool(source_drops), pre and not terminal and bool(source_consumes),
        pre and not terminal and bool(hs and hs[-1]['after'][item]['container'] == actor),
        bool(source_consumes) and not goal,
        physical_goal, physical_terminal, pre and not physical_terminal,
        not pre and any(h['before'][item] != h['after'][item] for h in good),
        any(d < g for d in source_drops for g in source_gets),
        any(g < d for g in source_gets for d in source_drops),
    ]))
    assert len(values) == len(FIELDS)
    # Exact accounting per trace, valid only where pre is actually required.
    if required:
        assert int(pre) == int(goal) + int(request) + int(other) + int(pre and not terminal)
    return {
        'case_id': r['case_id'], 'seed': r['seed'], 'persona': r['persona'],
        'condition': r['condition'], 'state': r['state'], 'goal_kind': kind,
        'pre_required': required, 'values': {k: int(v) for k, v in values.items()},
        'no_pre_profile': profile(good, hs, item) if not pre else None,
        'pre_no_terminal_profile': profile(good, hs, item) if pre and not terminal else None,
        'no_pre_event_types': Counter(h['event_type'] for h in good) if not pre else Counter(),
        'pre_no_terminal_event_types': Counter(h['event_type'] for h in good) if pre and not terminal else Counter(),
        'source_atomic_path': ' -> '.join(source_atomic_path) or 'NO_SOURCE_PHYSICAL_EVENT',
        'consumption_equivalent_witness': ({'case_id': r['case_id'], 'seed': r['seed'],
            'persona': r['persona'], 'condition': r['condition'], 'goal_kind': kind,
            'goal_command': r['goal_command'], 'goal_item_id': item,
            'actual_commands': [hs[i]['command'] for i in source_consumes],
            'actual_event_classes': [hs[i]['event_type'] for i in source_consumes],
            'actor_health_before_after': [[hs[i]['before'][actor].get('health'),
                                          hs[i]['after'][actor].get('health')] for i in source_consumes],
            'physical_consumption_occurred': True, 'bound_goal_event_occurred': False}
            if source_consumes and not goal and kind in ['eat', 'drink'] else None),
        'native_source_event_counts': Counter(successful_pre=len(pre_indices), source_give=len(gives),
                                              bound_goal=len(goal_events), source_drop=len(source_drops),
                                              source_consume=len(source_consumes)),
    }


def check_consumption_equivalence(args, cases):
    """Read source facts and, if requested, compare four real native forks."""
    from light_native_gate import load_event_modules
    from light_npc_episodes import ViewerHost, execute, material_state
    source = args.runs_root.parents[0] / 'sources/LIGHT'
    modules = load_event_modules(source)
    _, events, _ = modules
    assert events.EatEvent.execute is events.IngestEvent.execute
    assert events.DrinkEvent.execute is events.IngestEvent.execute
    data = args.runs_root / 'e75_native_retrieval_qualification/snapshots.jsonl'
    snapshots = {r['case']['case_id']: r for r in map(json.loads, data.open())}
    witnesses = []
    for cid in sorted(cases):
        src = snapshots[cid]; c = src['case']; branches = []
        for command in [c['goal_command'], 'ingest ' + c['goal_command'].split(' ', 1)[1]]:
            graph = modules[0].from_json(src['states']['ready'])
            actor = graph.get_node(c['actor_id']); item = graph.get_node(c['item_id'])
            before = material_state(graph); food_energy = item.get_prop('food_energy')
            native = execute(ViewerHost(graph), actor, command, *modules[1:])
            assert success(native) and native['after'][c['item_id']]['container'] == 'VOID'
            branches.append({'command': command, 'event_class': native['event_type'],
                'success': True, 'food_energy': food_energy,
                'health_before': before[c['actor_id']].get('health'),
                'health_after': native['after'][c['actor_id']].get('health'),
                'item_after': native['after'][c['item_id']],
                'physical_state': material_state(graph), 'graph_json': json.loads(graph.to_json())})
        assert branches[0]['physical_state'] == branches[1]['physical_state']
        assert branches[0]['graph_json'] == branches[1]['graph_json']
        for b in branches:
            del b['physical_state']; del b['graph_json']
        witnesses.append({'case_id': cid, 'branches': branches,
                          'all_material_state_equal': True, 'entire_serialized_graph_equal': True})
    return {'status': 'PASS', 'model_calls': 0, 'cpu_control_forks': len(witnesses) * 2,
        'source_commit': subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip(),
        'source_sha256': {str(source / f): sha(source / f) for f in [
            'light/graph/events/graph_events.py', 'light/graph/events/all_events_list.py']},
        'source_facts': ['graph_events.py:3041-3162 IngestEvent.execute moves the held food/drink to VOID, marks deletion and applies food_energy to health.',
            'graph_events.py:3165-3202 EatEvent and DrinkEvent inherit the same execute method; they narrow can_ingest to food or drink and change names/messages.',
            'all_events_list.py:72-74 exposes all three event classes as legal commands.',
            'The historical episode harness matches exact event class and source IDs. Physical equivalence does not rewrite that stored primary score.',
            'Native quest XP/completion service is not loaded by this event host; no full quest-completion flag is inferred from this CPU check.'],
        'interpretation': 'For these exact authored eat/drink items, ingest realizes the same physical consumption goal; absence of the bound event is not failure to consume.',
        'witnesses': witnesses}


def interval(point, draws, scale=100.0):
    finite = np.asarray(draws)[np.isfinite(draws)]
    return {'estimate': float(point * scale) if np.isfinite(point) else None,
            'ci95': [float(x * scale) for x in np.quantile(finite, [.025, .975])] if len(finite) else None,
            'defined_bootstraps': int(len(finite))}


def division(n, d):
    n, d = np.asarray(n, dtype=float), np.asarray(d, dtype=float)
    return np.divide(n, d, out=np.full_like(n, np.nan, dtype=float), where=d != 0)


def group_report(rows):
    cids = sorted({r['case_id'] for r in rows})
    conditions = sorted({r['condition'] for r in rows})
    lookup = {(r['case_id'], r['seed'], r['persona'], r['condition']): r for r in rows}
    assert len(lookup) == len(rows)
    seeds = sorted({r['seed'] for r in rows}); assert len(seeds) == 3
    indices = np.random.default_rng(BOOTSTRAP_SEED).integers(0, len(cids), (BOOTSTRAPS, len(cids)))
    arrays = {}; cells = {}; contrasts = {}
    for cond in conditions:
        for persona in PERSONAS:
            selected = [lookup[c, s, persona, cond] for c in cids for s in seeds]
            requireds = {r['pre_required'] for r in selected}; assert len(requireds) == 1
            required = requireds.pop()
            # Three seeds summarized within graph; complete fixed grid => pooled
            # rates and mean graph rates agree. Bootstrap is paired by graph.
            a = np.asarray([[sum(lookup[c, s, persona, cond]['values'][f] for s in seeds)
                             for f in FIELDS] for c in cids], dtype=float)
            arrays[persona, cond] = a
            total = a.sum(axis=0); draws = a[indices].sum(axis=1); n = len(selected)
            def ratio(name, numerator, denominator):
                i, j = FIELDS.index(numerator), FIELDS.index(denominator)
                out = interval(division(total[i], total[j]), division(draws[:, i], draws[:, j]))
                out.update(numerator=int(total[i]), denominator=int(total[j]))
                return name, out
            conditional = {}
            if required:
                conditional.update([
                    ratio('goal_given_successful_pre', 'goal', 'pre_success'),
                    ratio('request_given_successful_pre', 'request_distinct', 'pre_success'),
                    ratio('other_source_give_given_successful_pre', 'other_source_give', 'pre_success'),
                    ratio('no_terminal_given_successful_pre', 'pre_no_terminal', 'pre_success'),
                ])
            no_pre = n - total[FIELDS.index('pre_success')]
            no_pre_draws = n - draws[:, FIELDS.index('pre_success')]
            for f in (['other_item_give', 'other_item_give_requester', 'any_speech', 'any_emote',
                      'any_examine', 'only_successful_nonmaterial', 'any_block']
                      if required else []):
                i = FIELDS.index('no_pre_' + f)
                stat = interval(division(total[i], no_pre), division(draws[:, i], no_pre_draws))
                stat.update(numerator=int(total[i]), denominator=int(no_pre))
                conditional[f + '_given_no_successful_pre'] = stat
            cell = {'episodes': n, 'worlds': len(cids), 'pre_required': required,
                    'counts': {f: int(x) for f, x in zip(FIELDS, total)},
                    'rates_percent': {f: interval(total[i] / n, draws[:, i] / n) for i, f in enumerate(FIELDS)},
                    'conditional_rates_percent': conditional,
                    'no_pre_exclusive_profile': dict(sum((Counter({r['no_pre_profile']: 1}) for r in selected
                                                        if r['no_pre_profile'] is not None), Counter())),
                    'pre_no_terminal_exclusive_profile': dict(sum((Counter({r['pre_no_terminal_profile']: 1}) for r in selected
                                                               if r['pre_no_terminal_profile'] is not None), Counter())),
                    'no_pre_successful_event_counts': dict(sum((r['no_pre_event_types'] for r in selected), Counter())),
                    'pre_no_terminal_successful_event_counts': dict(sum((r['pre_no_terminal_event_types'] for r in selected), Counter())),
                    'pre_no_terminal_atomic_source_paths': dict(Counter(r['source_atomic_path'] for r in selected if r['values']['pre_no_terminal'])),
                    'no_pre_atomic_source_paths': dict(Counter(r['source_atomic_path'] for r in selected if not r['values']['pre_success'])),
                    'pre_accounting_residual_count': int(total[FIELDS.index('pre_success')] - sum(total[FIELDS.index(f)]
                                                        for f in ['goal', 'request_distinct', 'other_source_give', 'pre_no_terminal'])) if required else None,
                    'ready_note': None if required else 'Source item available in initial execution state; successful Get/Remove event rate is not mobilization and conditional-on-pre rates are inapplicable.'}
            assert cell['pre_accounting_residual_count'] in [None, 0]
            cells[persona + '/' + cond] = cell
        af = arrays['agreeable', cond] - arrays['firm', cond]
        out = {f: interval(af[:, i].sum() / (len(cids) * 3), af[indices, i].sum(axis=1) / (len(cids) * 3))
               for i, f in enumerate(FIELDS)}
        if cells['firm/' + cond]['pre_required']:
            delta = {f: int(af[:, i].sum()) for i, f in enumerate(FIELDS)}
            assert delta['goal'] == delta['pre_success'] - delta['request_distinct'] - delta['other_source_give'] - delta['pre_no_terminal']
        contrasts['A_minus_F/' + cond] = {'unconditional_pp': out,
            'conditional_rates_note': 'Persona-specific successful-pre subsets differ; q_A/q_B are descriptive selected-subset rates, not causal allocation effects.'}
    return {'worlds': len(cids), 'seeds': seeds, 'cells': cells, 'contrasts': contrasts}, arrays, cids, indices


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs-root', type=Path, default=DEFAULT_RUNS)
    ap.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[1] / 'results/E73_E76_progress_allocation_POST_HOC.json')
    ap.add_argument('--verify-consumption-semantics', action='store_true',
                    help='CPU-only native forks require the existing LIGHT dependency overlay')
    args = ap.parse_args(); all_rows = {}; hashes = {}; physics = Counter()
    for experiment, names in [('E73', ['e73_{m}']), ('E75', ['e75_{m}_s0', 'e75_{m}_s1']), ('E76', ['e76_{m}'])]:
        for model in ['gemma', '32b']:
            raw = []; compact = []
            for pattern in names:
                folder = args.runs_root / pattern.format(m=model)
                assert (folder / 'runtime.json').exists()
                manifest = json.loads((folder / 'manifest.json').read_text())
                assert manifest['experiment'] == experiment and not manifest.get('profile')
                for fn in ['episodes.jsonl', 'manifest.json', 'runtime.json']:
                    hashes[str(folder / fn)] = sha(folder / fn)
                for r in map(json.loads, (folder / 'episodes.jsonl').open()):
                    compact.append(readback(r, experiment))
                    physics['episodes'] += 1
                    physics.update(compact[-1]['native_source_event_counts'])
                    if experiment == 'E76':
                        raw.append((r['case_id'], r['seed'], r['persona'], r['conversation']))
            all_rows[experiment, model] = compact
            if experiment == 'E76':
                conv = {}
                for shard in ['s0', 's1']:
                    for r in map(json.loads, (args.runs_root / f'e75_{model}_{shard}' / 'episodes.jsonl').open()):
                        if r['condition'] == 'retrieval_baseline':
                            conv[r['case_id'], r['seed'], r['persona']] = r['conversation']
                assert len(raw) == 612
                for cid, seed, persona, conversation in raw:
                    assert conversation == conv[cid, seed, persona]
                    physics['E76_exact_retrieval_conversations'] += 1
    output = {}; internals = {}
    for (experiment, model), rows in all_rows.items():
        assert len(rows) == {'E73': 1404, 'E75': 2448, 'E76': 612}[experiment]
        groups = {'all': rows}
        if experiment != 'E73':
            groups.update(source_give=[r for r in rows if r['goal_kind'] == 'give'],
                          source_use=[r for r in rows if r['goal_kind'] != 'give'])
            groups.update({'kind_' + k: [r for r in rows if r['goal_kind'] == k] for k in ['wear', 'eat', 'drink']})
        out = {}
        for group, values in groups.items():
            result, arrays, cids, indices = group_report(values)
            out[group] = result
            internals[experiment, model, group] = arrays, cids, indices
        output[experiment + '/' + model] = out
    # Compare P(outcome | actual Get) to ready outcomes, with paired graph
    # resampling. This is descriptive; conditioning changes the selected set.
    conditional_vs_ready = {}
    for model in ['gemma', '32b']:
        for group in output['E75/' + model]:
            a75, c75, ix = internals['E75', model, group]
            a76, c76, _ = internals['E76', model, group]; assert c75 == c76
            result = {}
            for support in ['baseline', 'paths']:
                for persona in PERSONAS:
                    src = a75[persona, 'retrieval_' + support]
                    for reference in ['E75_ready_same_support', 'E76_ready_frozen_retrieval_dialogue']:
                        ref = a75[persona, 'ready_' + support] if reference.startswith('E75') else a76[persona, 'ready_frozen_dialogue']
                        out = {}
                        for f in ['goal', 'request_distinct', 'other_source_give', 'pre_no_terminal']:
                            num = src[:, FIELDS.index(f)]; den = src[:, FIELDS.index('pre_success')]
                            ref_count = ref[:, FIELDS.index(f)] if f != 'pre_no_terminal' else 3 - ref[:, FIELDS.index('registered_terminal')]
                            point = division(num.sum(), den.sum()) - ref_count.sum() / (len(c75) * 3)
                            draws = division(num[ix].sum(axis=1), den[ix].sum(axis=1)) - ref_count[ix].sum(axis=1) / (len(c75) * 3)
                            out[f] = interval(point, draws)
                        result[persona + '/' + support + '/' + reference] = out
            conditional_vs_ready[model + '/' + group] = result
    consumption_witnesses = []
    for (experiment, model), rows in all_rows.items():
        consumption_witnesses.extend({'experiment': experiment, 'model': model, **r['consumption_equivalent_witness']}
            for r in rows if r['consumption_equivalent_witness'])
    semantics = check_consumption_equivalence(args, {r['case_id'] for r in consumption_witnesses}) if args.verify_consumption_semantics else None
    result = {'status': 'COMPLETE_POST_HOC', 'analysis': 'E73-E76 source-bound progress and allocation',
              'model_calls': 0, 'gpu_hours': 0, 'verified_counts': dict(physics),
              'bootstrap': {'samples': BOOTSTRAPS, 'seed': BOOTSTRAP_SEED, 'unit': 'source graph, with all three seeds and persona pairs retained',
                            'conditional_estimator': 'ratio of pooled within-graph counts; cluster-bootstrap the numerator and denominator together',
                            'intervals': 'pointwise percentile 95%; undefined zero-denominator draws excluded and counted'},
              'definitions': {
                  'successful_event': 'legal AND executed AND NOT stochastic_failure; no command attempt or prose counts',
                  'pre_success': 'At least one successful exact-source Remove (E73) or Get (E75/E76), independently state-checked',
                  'goal': 'E73 first exact-source Give to authored A; E75/E76 exact native goal event class and bound target IDs',
                  'request_distinct': 'First exact-source Give to requester, excluding a goal event; aligned E73 requester==A counted only as goal',
                  'other_source_give': 'First exact-source Give to neither authored goal nor distinct requester',
                  'registered_terminal': 'Mutually exclusive goal OR request_distinct OR other_source_give under original stopping protocol',
                  'pre_no_terminal': 'Successful source pre but no registered terminal by original horizon; may hold/drop/consume or perform other legal acts, so not automatically R_hold',
                  'no_pre_no_terminal': 'No successful source pre and no registered terminal, not necessarily physical inactivity',
                  'identity_where_pre_required': 'P(pre)=P(goal)+P(request_distinct)+P(other_source_give)+P(pre_no_terminal)',
                  'resolved_identity': 'P(registered_terminal)=P(goal)+P(request_distinct)+P(other_source_give), a separate quantity from P(pre)',
                  'ready': 'Prerequisite externally satisfied in initial execution state. Actual source Get/Remove events are not a ready-state mobilization measure.',
                  'physical_goal_secondary': 'Original bound goal OR successful exact-source consumption for authored eat/drink goals; historical bound-event primary unchanged.',
                  'no_pre_source_material_change': 'No successful required pre, but some successful event changed the source item state; unlike vague no-source-progress, the definition checks direct Drop and other paths.',
                  'trace_profile_precedence': 'other-item Give present > other material event present > only successful nonmaterial > nonmaterial plus failures > other/failures > empty',
              },
              'scope': ['Accounting identities organize outcomes but do not identify a latent two-stage policy or causal mediation.',
                        'Conditioning on successful pre selects a persona-dependent subset; conditional equality/difference versus ready is descriptive.',
                        'Action costs, custody, menus, dialogue grounding and goal value are not separated by this readback.',
                        'Legal emote/speech/negotiation during a static requester interaction is not automatically inability or pathology.',
                        'Aligned E73 goal and request refer to one recipient; they are never treated as independent successes.',
                        'E76 setup Get was performed only to initialize the counterfactual world, never counted as a chosen NPC action.',
                        'All source graphs/seeds retained; no re-run, API, threshold, new outcome protocol or human state change.'],
              'results': output, 'conditional_minus_ready_unconditional_pp': conditional_vs_ready,
              'consumption_equivalent_witnesses': consumption_witnesses,
              'consumption_semantics_cpu_check': semantics,
              'source_sha256': hashes, 'script_sha256': sha(Path(__file__))}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'verified_counts': dict(physics), 'out': str(args.out)}))


if __name__ == '__main__':
    main()
