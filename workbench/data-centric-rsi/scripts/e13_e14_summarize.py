"""Aggregate the eight frozen terminal evaluations; reject missing/failed runs."""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
from e12_validate_eval import validate_results, BENCHMARKS


def read(p): return json.loads(p.read_text())


def summarize(results, state_path):
    state = read(state_path)
    assert state['status'] == 'eight_evaluations_completed'
    assert len(state['runs']) == 8 and not state['judge_cleanup']['remaining']
    cleanup_audit = read(results/'E13_E14_descendant_cleanup.json')
    guard_rows = {r['name']:r for entries in cleanup_audit['nodes'].values() for r in entries}
    assert len(guard_rows)==9 and all(r['cleanup_complete'] and not r['active_pids'] for r in guard_rows.values())
    old = read(results / 'E12_seed17_static_utility_summary.json')
    parents = {'init':old['arms']['base']['scores'], 'used':old['arms']['icons_exact']['scores']}
    actions = ('replay', 'fresh_selected', 'fresh_law', 'source_only_fresh')
    schedule = {}
    for line in (results/'E13_E14_closeout_schedule.jsonl').read_text().splitlines():
        record = json.loads(line)
        for row in record['active']:
            if record['status'] == 'operational_retry_schedule_reconstruction':
                schedule[row['name']] = row
            else:
                schedule.setdefault(row['name'], row)
    rows = []
    for parent in ('init','used'):
        for action in actions:
            experiment = 'E14' if action == 'source_only_fresh' else 'E13'
            name = f'{parent}_{action}_s29'; prefix = f'{experiment}_{name}'
            worker = next(r for r in state['runs'] if r['name'] == name)
            assert worker['status'] == 'completed' and worker['returncode'] == 0
            assert worker.get('validation_accepted') or worker.get('ssh_returncode') == 0
            scores = validate_results(read(results/f'{prefix}_raw_results.json'))
            saved = read(results/f'{prefix}_validated_scores.json')
            assert math.isclose(scores['accuracy_percent'], saved['accuracy_percent'], rel_tol=0, abs_tol=1e-12)
            assert set(scores['benchmarks']) == set(saved['benchmarks'])
            for benchmark, row in scores['benchmarks'].items():
                other = saved['benchmarks'][benchmark]
                assert row['field'] == other['field']
                assert all(math.isclose(row[k], other[k], rel_tol=0, abs_tol=1e-12) for k in ('raw', 'max', 'normalized'))
            manifest = read(results/f'{prefix}_eval_manifest.json')
            assert set(manifest['benchmarks']) == set(BENCHMARKS)
            assert manifest['judge_model'] == 'Qwen3.5-27B' and manifest['api_nproc'] == 4 and manifest['mode'] == 'all'
            assert manifest['source_git_sha'] == '24eea1526492c00cee421f5db0793789e00aabb2'
            vector = {b:100*scores['benchmarks'][b]['normalized'] for b in BENCHMARKS}
            start = dt.datetime.fromisoformat(schedule[name]['submitted_utc'])
            end = max(dt.datetime.fromisoformat(worker['finished_utc']), dt.datetime.fromisoformat(guard_rows[name]['all_descendants_exited_utc']))
            rows.append({'experiment':experiment,'parent':parent,'action':action,'name':name,
                         'mean_percent':scores['accuracy_percent'], 'task_percent':vector,
                         'gain_over_parent_pp':scores['accuracy_percent']-parents[parent]['accuracy_percent'],
                         'task_gain_over_parent_pp':{b:vector[b]-100*parents[parent]['benchmarks'][b]['normalized'] for b in BENCHMARKS},
                         'source_prefix':prefix,'node':schedule[name]['node'],'gpu':manifest['gpu'],
                         'eval_process_wrapper_seconds':worker['eval_wrapper_seconds'],
                         'scheduled_worker_wall_seconds':(end-start).total_seconds(),
                         'cleanup_complete':not worker['cleanup']['remaining'] and guard_rows[name]['cleanup_complete']})
    assert all(r['cleanup_complete'] for r in rows)
    lookup = {(r['parent'],r['action']):r for r in rows}
    contrasts = {}
    for a,b in (('fresh_selected','fresh_law'),('fresh_selected','replay'),('fresh_law','replay'),('source_only_fresh','fresh_law')):
        key = f'{a}_minus_{b}'
        contrasts[key] = {p:{'mean_pp':lookup[p,a]['mean_percent']-lookup[p,b]['mean_percent'],
                            'task_pp':{t:lookup[p,a]['task_percent'][t]-lookup[p,b]['task_percent'][t] for t in BENCHMARKS}} for p in parents}
        contrasts[key]['used_minus_init_interaction_pp'] = contrasts[key]['used']['mean_pp']-contrasts[key]['init']['mean_pp']
    training = {'E13':32131.095, 'E14':7490.509}
    cost = {e:{'train_queue_wrapper_seconds':training[e],
               'eval_process_wrapper_seconds':sum(r['eval_process_wrapper_seconds'] for r in rows if r['experiment']==e),
               'eval_scheduled_worker_seconds':sum(r['scheduled_worker_wall_seconds'] for r in rows if r['experiment']==e)} for e in training}
    for c in cost.values():
        c['train_plus_scheduled_eval_A100_hours']=(c['train_queue_wrapper_seconds']+c['eval_scheduled_worker_seconds'])/3600
    failed = read(results/'E14_judge_startup_failure_audit.json')['correction']
    return {'experiment':'E13/E14 original seed29 terminal closeout','generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'status':'all_eight_terminal_evaluations_validated','seed':29,'rows':rows,'prewritten_and_descriptive_contrasts':contrasts,
            'cost':cost,'judge_recovery_launch_to_cleanup_seconds':(dt.datetime.fromisoformat(guard_rows['judge']['all_descendants_exited_utc'])-dt.datetime.fromisoformat(state['judge']['started_utc'])).total_seconds(),
            'original_token_only_judge_cleanup_seconds':state['judge_launch_to_cleanup_seconds'],
            'prior_failed_judge_launch_to_shutdown_log_seconds':failed['launch_to_engine_shutdown_log_seconds'],
            'cost_scope':'A100 scheduled-worker wall includes CPU/import/checksum/SSH and up to one guard polling interval at teardown; sum across parallel branches, not kernel-active time. Judge recovery includes loading and waits. Old failed judge final resource-teardown time unknown; its log span is not an exact active-GPU allocation or a proved upper bound. Copy and staging costs recorded separately.',
            'failed_prelaunch_eval_attempt':{'name':'used_fresh_law_s29','GPU_inference_started':False,'CPU_preflight_wall_seconds':None,'note':'Original card-idle rejection before launch is preserved; CPU/hash/SSH time for that rejected reservation not fully metered, excluded from successful GPU-worker wall totals.'},
            'API_paid_requests':0,'scientific_claim_upgrade':False,'train_seed_CI':None,
            'limitations':['One paired train seed, no training variance estimate; task/episode samples are not independent training replicates.',
                           'Existing eight public benchmarks were already observed in E12; this is not fresh private confirmation.',
                           'E13 exact source/label matching retains 46 shared anchors; text-only refresh has lower coverage.',
                           'E14 changes label quantity, anchor retention and content jointly; not a label-length causal intervention.',
                           'Concurrent eval requests and node deployment differ from E12; same judge weights, version and fixed scoring protocol, not bit-identical inference.',
                           'No new seeds or experiments were added; null differences do not establish equivalence.']}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results',type=Path,required=True);p.add_argument('--state',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();result=summarize(a.results,a.state)
    with a.out.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({r['name']:r['mean_percent'] for r in result['rows']},indent=2))
