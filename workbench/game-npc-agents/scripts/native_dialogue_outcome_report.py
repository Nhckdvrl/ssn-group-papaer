#!/usr/bin/env python3
"""E77: graph-paired dialogue crossover and externally assigned outcomes.

No model calls. Original E75 diagonals and every source dialogue are checked
against the complete original records before any contrast is calculated.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np

from native_dialogue_outcome_execution import CONDITIONS, donor
from native_retrieval_execution import SEEDS
from native_retrieval_report import metrics as original_metrics, validate
from native_rule_cross_report import summarize

PERSONAS = ['firm', 'agreeable']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_key(row):
    return tuple(row[k] for k in ['case_id', 'seed', 'persona', 'condition'])


def metrics(row, target=None):
    values = original_metrics(row)
    physical_goal = False
    source = row['goal_item_id']
    for h in row['history']:
        if not (h['legal'] and h.get('executed') and not h.get('stochastic_failure')):
            continue
        ids = h['target_node_ids']
        if not ids or ids[0] != source:
            continue
        before, after = h['before'][source], h['after'][source]
        if row['goal_kind'] in ['eat', 'drink'] and h['event_type'] in ['EatEvent', 'DrinkEvent', 'IngestEvent']:
            assert before['container'] == row['actor_id'] and after['container'] == 'VOID'
            physical_goal = True
        elif row['goal_kind'] == 'wear' and h['event_type'] == 'WearEvent':
            assert after['container'] == row['actor_id'] and after['equipped']
            physical_goal = True
        elif row['goal_kind'] == 'give' and h['event_type'] == 'GiveObjectEvent':
            assert before['container'] == row['actor_id'] and after['container'] == ids[1]
            physical_goal |= ids[1] == row['goal_recipient_id']
    assert not values['goal'] or physical_goal
    decisive = values['goal'] + values['request'] + values['other_source_give']
    assert decisive in [0, 1]
    physical_decisive = float(physical_goal) + values['request'] + values['other_source_give']
    assert physical_decisive in [0, 1]
    # All E77 starts are the original floor state. Any bound use must have
    # passed the exact source-item Get; this is checked, not assumed in plots.
    assert not decisive or values['retrieved']
    values.update(
        noninitiation=1-values['retrieved'],
        retrieved_without_decisive=values['retrieved'] * values['no_decisive_event'],
        no_get_without_decisive=(1-values['retrieved']) * values['no_decisive_event'],
        get_then_goal=values['retrieved'] * values['goal'],
        get_then_request=values['retrieved'] * values['request'],
        get_then_other_source_give=values['retrieved'] * values['other_source_give'],
        otherasset=values['other_item_give'],
        native_errors=float(values['invalid_attempts']),
        physical_goal=float(physical_goal),
        physical_goal_without_bound_event=float(physical_goal and not values['goal']),
        physical_no_decisive_event=1-physical_decisive,
        physical_retrieved_without_decisive=values['retrieved']*(1-physical_decisive),
        physical_no_get_without_decisive=(1-values['retrieved'])*(1-physical_decisive),
    )
    assert (values['goal'] + values['request'] + values['other_source_give']
            + values['retrieved_without_decisive'] + values['no_get_without_decisive']) == 1
    if target is not None:
        assert target in ['goal', 'request']
        values.update(assigned_success=values[target], wronguse=decisive-values[target])
        physical_assigned = float(physical_goal) if target == 'goal' else values['request']
        values.update(physical_assigned_success=physical_assigned,
                      physical_wronguse=physical_decisive-physical_assigned)
    return values


def load_rows(folders, experiment, model=None):
    rows, manifests, runtimes, hashes, calls = {}, [], [], {}, Counter()
    duplicate_records = 0
    for folder in dict.fromkeys(folders):
        manifest = json.loads((folder/'manifest.json').read_text())
        runtime = json.loads((folder/'runtime.json').read_text())
        assert manifest['experiment'] == experiment
        if model is None:
            model = manifest['model']
        assert manifest['model'] == model
        manifests.append(manifest)
        runtimes.append(runtime)
        path = folder/'episodes.jsonl'
        hashes[str(path)] = sha(path)
        for row in map(json.loads, path.open()):
            if experiment == 'E75' and row['condition'] != 'retrieval_baseline':
                continue
            key = row_key(row)
            if key in rows:
                assert rows[key] == row, ('Non-identical duplicate episode', key)
                duplicate_records += 1
            else:
                rows[key] = row
        if experiment == 'E77':
            count = 0
            path = folder/'model_calls.jsonl'
            hashes[str(path)] = sha(path)
            for row in map(json.loads, path.open()):
                assert row['stage'] == 'exec'
                calls.update(calls=1, parse_errors=int(bool(row['parse_error'])),
                             prompt_tokens=row['prompt_tokens'], completion_tokens=row['completion_tokens'])
                count += 1
            assert count == runtime['calls']
            assert runtime['new_conversation_calls'] == runtime['new_cloud_calls'] == 0
    return rows, model, manifests, runtimes, hashes, calls, duplicate_records


def analyze(runs, references, data, out):
    sources = {r['case']['case_id']: r for r in map(json.loads, data.open())}
    assert len(sources) == 102
    rows, model, manifests, runtimes, hashes, calls, duplicate_records = load_rows(runs, 'E77')
    old, _, _, _, reference_hashes, _, _ = load_rows(references, 'E75', model)
    hashes.update(reference_hashes)
    hashes[str(data)] = sha(data)
    assert all(m['data_sha256'] == sha(data) and m['seeds'] == SEEDS for m in manifests)
    expected = {(cid, seed, p, c) for cid in sources for seed in SEEDS
                for p in PERSONAS for c in CONDITIONS}
    expected_old = {(cid, seed, p, 'retrieval_baseline') for cid in sources
                    for seed in SEEDS for p in PERSONAS}
    assert set(rows) == expected and len(rows) == 2448
    assert set(old) == expected_old and len(old) == 612
    validation, new_validation = Counter(), Counter()
    exact_dialogues = exact_diagonals = 0
    new_metadata = {'condition', 'conv_persona', 'assigned_outcome'}
    for key, row in rows.items():
        cid, seed, p, condition = key
        source, target = CONDITIONS[condition]
        source = source or donor(cid, seed)
        assert row['conv_persona'] == source and row['assigned_outcome'] == target
        ref = old[cid, seed, source, 'retrieval_baseline']
        assert row['conversation'] == ref['conversation']
        assert row['native_goal_identity'] == sources[cid]['native_goal_identity']
        assert row['state'] == 'retrieval' and row['support'] == 'baseline'
        assert row['goal_item_id'] == sources[cid]['case']['item_id']
        case = sources[cid]['case']
        for field in ['actor_id', 'requester_id', 'goal_kind', 'goal_command', 'request_command']:
            assert row[field] == case[field], (key, field)
        assert row['source_graph_sha256'] == case['graph_sha256']
        assert row['goal_recipient_id'] == case['original_recipient']
        exact_dialogues += 1
        checked = validate(row, sources[cid])
        validation.update(checked)
        if target is None and source == p:
            diagonal = old[cid, seed, p, 'retrieval_baseline']
            assert ({k: v for k, v in row.items() if k not in new_metadata}
                    == {k: v for k, v in diagonal.items() if k not in new_metadata}), key
            exact_diagonals += 1
        else:
            new_validation.update(checked)
    assert exact_diagonals == 612 and exact_dialogues == 2448
    values = {key: metrics(row) for key, row in rows.items()}
    fields = list(next(iter(values.values())))
    physical_extras = [rows[key] for key, value in values.items()
                       if value['physical_goal_without_bound_event']]
    groups = {'all': sorted(sources),
              'source_give': sorted(cid for cid, r in sources.items() if r['case']['goal_kind'] == 'give'),
              'source_use': sorted(cid for cid, r in sources.items() if r['case']['goal_kind'] != 'give')}
    groups.update({'kind_'+kind: sorted(cid for cid, r in sources.items() if r['case']['goal_kind'] == kind)
                   for kind in ['wear', 'eat', 'drink']})
    output = {}
    for group, cids in groups.items():
        def estimate(value_fn, use_fields=fields):
            matrix = [np.mean([[value_fn(cid, seed)[f] for f in use_fields] for seed in SEEDS], axis=0)
                      for cid in cids]
            return summarize(matrix, use_fields)

        def contrast(terms):
            return estimate(lambda cid, seed: {f: sum(w*values[cid, seed, p, c][f]
                                                     for w, p, c in terms) for f in fields})

        cells_a, contrasts_a = {}, {}
        for c in PERSONAS:
            for p in PERSONAS:
                cells_a['conv_'+c+'/exec_'+p] = contrast([(1, p, 'dialogue_'+c)])
            contrasts_a['exec_A_minus_F/given_C_'+c] = contrast([
                (1, 'agreeable', 'dialogue_'+c), (-1, 'firm', 'dialogue_'+c)])
        for p in PERSONAS:
            contrasts_a['C_A_minus_F/given_exec_'+p] = contrast([
                (1, p, 'dialogue_agreeable'), (-1, p, 'dialogue_firm')])
        contrasts_a['exec_x_C'] = contrast([
            (1, 'agreeable', 'dialogue_agreeable'), (-1, 'firm', 'dialogue_agreeable'),
            (-1, 'agreeable', 'dialogue_firm'), (1, 'firm', 'dialogue_firm')])
        contrasts_a['average_exec_A_minus_F'] = contrast([
            (0.5, 'agreeable', 'dialogue_'+c) for c in PERSONAS]
            + [(-0.5, 'firm', 'dialogue_'+c) for c in PERSONAS])
        contrasts_a['average_C_A_minus_F'] = contrast([
            (0.5, p, 'dialogue_agreeable') for p in PERSONAS]
            + [(-0.5, p, 'dialogue_firm') for p in PERSONAS])
        contrasts_a['coherent_A_minus_F'] = contrast([
            (1, 'agreeable', 'dialogue_agreeable'), (-1, 'firm', 'dialogue_firm')])

        def b_value(cid, seed, p, target, assigned):
            condition = 'assigned_'+target if assigned else 'dialogue_'+donor(cid, seed)
            return metrics(rows[cid, seed, p, condition], target)

        b_fields = fields + ['assigned_success', 'wronguse', 'physical_assigned_success', 'physical_wronguse']

        def b_estimate(terms, target):
            return estimate(lambda cid, seed: {f: sum(w*b_value(cid, seed, p, target, assigned)[f]
                                                      for w, p, assigned in terms) for f in b_fields}, b_fields)

        assigned_cells, free_cells, contrasts_b = {}, {}, {}
        for target in ['goal', 'request']:
            for p in PERSONAS:
                assigned_cells[p+'/assigned_'+target] = b_estimate([(1, p, True)], target)
                free_cells[p+'/matched_to_'+target] = b_estimate([(1, p, False)], target)
                contrasts_b[p+'/assigned_minus_free/'+target] = b_estimate(
                    [(1, p, True), (-1, p, False)], target)
            contrasts_b['A_minus_F/assigned_'+target] = b_estimate(
                [(1, 'agreeable', True), (-1, 'firm', True)], target)
            contrasts_b['A_minus_F/matched_free/'+target] = b_estimate(
                [(1, 'agreeable', False), (-1, 'firm', False)], target)
            contrasts_b['persona_x_assignment/'+target] = b_estimate([
                (1, 'agreeable', True), (-1, 'firm', True),
                (-1, 'agreeable', False), (1, 'firm', False)], target)
        counts = Counter(donor(cid, seed) for cid in cids for seed in SEEDS)
        output[group] = {'worlds': len(cids), 'world_seed_donors': dict(counts),
                         'panel_A': {'cells': cells_a, 'contrasts': contrasts_a},
                         'panel_B': {'assigned_cells': assigned_cells, 'matched_free_cells': free_cells,
                                     'contrasts': contrasts_b}}
    result = {'status': 'COMPLETE', 'experiment': 'E77', 'model': model, 'worlds': len(sources),
              'logical_execution_records': len(rows), 'old_diagonal_records_exactly_reused': exact_diagonals,
              'new_logical_execution_branches': len(rows)-exact_diagonals,
              'duplicate_profile_records_verified': duplicate_records,
              'exact_source_conversations_verified': exact_dialogues,
              'seeds': SEEDS, 'groups': output, 'actual_calls_in_supplied_runs': dict(calls),
              'native_validation_all_records': dict(validation),
              'native_validation_new_logical_branches': dict(new_validation),
              'physical_flag_mismatches': 0,
              'physical_task_consequence_without_registered_event_records': len(physical_extras),
              'physical_secondary_extra_records_by_goal_kind': dict(Counter(r['goal_kind'] for r in physical_extras)),
              'physical_secondary_extra_records_by_condition': dict(Counter(r['condition'] for r in physical_extras)),
              'supplied_run_load_and_inference_gpu_hours': sum(
                  r['wall_seconds']+r['model_load_seconds'] for r in runtimes)/3600,
              'source_sha256': hashes,
              'scope': [
                  'Every original source graph and all three seeds retained; seeds averaged within graph before 4000 paired graph bootstrap draws.',
                  'Panel A interventions change only the current execution trait header conditional on an exact donor dialogue; they are stage interventions, not coherent whole-persona changes.',
                  'Panel B donor is preassigned by a fixed world-seed hash shared across traits and outcomes; matched free branches use exactly the same dialogue.',
                  'Outcome assignment changes intended priorities and is not a proof of fixed latent ability, observed prior intention, or orthogonal mediation.',
                  'Assigned success means the assigned outcome was the first decisive source-item use under the unchanged original stopping rule.',
                  'No-decisive-event, no source Get, and source Get without a decisive event are reported separately; no causal effect is inferred by conditioning on successful Get.',
                  'Wrong use is any first decisive source-item outcome other than the assigned one; it is defined only in target-aligned Panel B comparisons.',
                  'The preregistered exact bound event remains primary. Physical-outcome sensitivity additionally counts successful source-item Ingest/Eat/Drink with actor-to-VOID state change, Wear with the equipped flag, and Give with recipient custody; it does not relabel the primary.',
                  'Intervals are pointwise, not simultaneous; the small Wear/Eat/Drink groups are all reported.',
                  'Old diagonals and profile duplicates are exact reuses, not additional independent samples.'
              ]}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['status', 'model', 'worlds', 'logical_execution_records',
                                           'new_logical_execution_branches', 'actual_calls_in_supplied_runs',
                                           'native_validation_all_records']}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--references', type=Path, nargs='+', required=True)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    analyze(a.runs, a.references, a.data, a.out)


if __name__ == '__main__':
    main()
