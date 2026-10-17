#!/usr/bin/env python3
"""POST-HOC E69 structured stance/plan readout; no language judge or new calls."""
import argparse
import json
from pathlib import Path
import numpy as np
from native_rule_cross_report import summarize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    sources = {r['case']['case_id']: r for r in
               map(json.loads, (args.data/'paired_tasks.jsonl').open())}
    lookup = {}
    for folder in args.runs:
        assert (folder/'runtime.json').exists()
        for row in map(json.loads, (folder/'episodes.jsonl').open()):
            if row['panel'] == 'matched':
                key = row['case_id'], row['seed'], row['persona'], row['task_condition']
                assert key not in lookup
                lookup[key] = row
    expected = {(cid, seed, persona, task) for cid in sources
                for seed in [6901, 6902, 6903] for persona in ['firm', 'agreeable']
                for task in ['equip', 'duty_give']}
    assert set(lookup) == expected
    fields = ['stance_accept', 'stance_decline', 'stance_negotiate',
              'plan_contains_task', 'plan_starts_task', 'plan_contains_request',
              'task_without_listed_task', 'task_listed_but_not_executed']
    values = {}
    for key, row in lookup.items():
        source = sources[row['case_id']]
        stance = (row['conversation'] or {}).get('stance')
        plan = (row['update'] or {}).get('priority_actions', [])
        task = row['goal_command']
        request = source['requests']['goal_item']['command']
        # All task/request/plan commands use the native canonical action menu.
        included = task in plan
        values[key] = [float(stance == name) for name in ['accept', 'decline', 'negotiate']] + [
            float(included), float(bool(plan) and plan[0] == task), float(request in plan),
            float(row['goal_executed'] and not included),
            float(included and not row['goal_executed'])]
    cells, differences = {}, {}
    for task in ['equip', 'duty_give']:
        for persona in ['firm', 'agreeable']:
            matrix = [np.mean([values[cid, seed, persona, task]
                              for seed in [6901, 6902, 6903]], axis=0)
                      for cid in sorted(sources)]
            cells[persona+'/'+task] = summarize(matrix, fields)
        matrix = [np.mean([np.asarray(values[cid, seed, 'agreeable', task]) -
                           np.asarray(values[cid, seed, 'firm', task])
                           for seed in [6901, 6902, 6903]], axis=0)
                  for cid in sorted(sources)]
        differences[task] = summarize(matrix, fields)
    result = {'status': 'COMPLETE', 'design': 'POST-HOC structured-output description, added after seeing Gemma main outcomes.',
              'worlds': len(sources), 'episodes': len(lookup), 'cells': cells,
              'A_minus_F': differences, 'new_model_calls': 0,
              'scope': ['Stance is the generated structured field, not a semantic or unconditional-commitment label.',
                        'Plan inclusion is exact canonical command membership, not full executable-plan feasibility.',
                        'Direct goal information remains visible to execution. These counts do not identify mediation or a neural mechanism.']}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'worlds': len(sources), 'episodes': len(lookup), 'new_model_calls': 0}))


if __name__ == '__main__':
    main()
