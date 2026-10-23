#!/usr/bin/env python3
"""Read-only D-E10--13 run/attempt ledger, retaining the earlier D-E01--09 ledger."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path


def load(path):return json.loads(path.read_text())
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def record_file(path,root):
    digest=hashlib.sha256();usage=Counter();finish=Counter();models=Counter();n=returned=unknown=0
    with path.open('rb') as f:
        for line in f:
            digest.update(line);r=json.loads(line);n+=1;returned+=r.get('response') is not None
            finish[str(r.get('finish_reason'))]+=1;models[str(r.get('model',r.get('owner','unspecified')))]+=1
            u=r.get('usage') or {}
            for key in ['prompt_tokens','completion_tokens']:
                if u.get(key) is None:unknown+=1
                else:usage[key]+=u[key]
    meta_path=path.parent/'metadata.json';meta=load(meta_path) if meta_path.exists() else {}
    return dict(path=str(path.relative_to(root)),sha256=digest.hexdigest(),records=n,returned_records=returned,
        known_usage=dict(usage),missing_usage_fields=unknown,finish_reasons=dict(finish),labels=dict(models),
        process_complete=meta.get('complete'),process_wall_s=meta.get('wall_s'),metadata_sha256=sha(meta_path) if meta_path.exists() else None,
        checkpoint=meta.get('checkpoint',(meta.get('args') or {}).get('checkpoint')),
        adapter=meta.get('adapter',(meta.get('args') or {}).get('adapter')))


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    root=a.asset_root;results=Path(__file__).resolve().parent.parent/'results'
    historical_file=results/'D-RESIDENCY-TOTALS.json';historical=load(historical_file)
    studies={};known_generation=known_forward=known_seconds=training_seconds=0;usage=Counter();training_ok=[];training_failed=[];unknown_durations=[]
    for exp in ['D-E10','D-E11','D-E12','D-E13']:
        run=root/'runs'/exp
        terminal=load(run/('judges/status.json' if exp=='D-E11' else 'finish_status.json'))
        if not terminal.get('complete'):raise ValueError('Registered study still open: '+exp)
        files=sorted(run.rglob('responses.jsonl'))
        if exp=='D-E11':files+=sorted(run.glob('*/raw.jsonl'))
        assert len(files)==len(set(files))
        records=[record_file(f,root) for f in files]
        unknown_durations.extend(x['path'] for x in records if x['process_wall_s'] is None)
        generated=sum(x['returned_records'] for x in records);known_generation+=generated
        seconds=sum(x['process_wall_s'] for x in records if x['process_wall_s'] is not None);known_seconds+=seconds
        exp_usage=Counter()
        for x in records:exp_usage.update(x['known_usage'])
        usage.update(exp_usage)
        training=[]
        for file in sorted(run.glob('train*/metadata.json')):
            m=load(file);v=dict(path=str(file.relative_to(root)),sha256=sha(file),complete=m.get('complete'),error=m.get('error'),
                completed_steps=m.get('completed_steps'),seen_examples=m.get('seen_examples'),forward_tokens=m.get('seen_forward_tokens'),
                target_tokens=m.get('planned_target_tokens') if m.get('complete') else None,wall_s=m.get('wall_s'),
                final_checkpoint=m.get('final_checkpoint'),extra_alignment_forwards=(m.get('alignment_check') or {}).get('extra_forwards'))
            val=file.parent/'validation.jsonl';v['validation_sequence_evaluations']=sum(len(json.loads(x).get('rows',[])) for x in val.read_text().splitlines()) if val.exists() else 0
            training.append(v);(training_ok if v['complete'] else training_failed).append(v)
            if v['wall_s'] is not None:training_seconds+=v['wall_s']
            else:unknown_durations.append(v['path'])
        forwards=[]
        for file in sorted(run.glob('likelihood/scores.jsonl')):
            meta=load(file.parent/'metadata.json');n=sum(1 for _ in file.open());known_forward+=n;known_seconds+=meta.get('wall_s',0)
            forwards.append(dict(path=str(file.relative_to(root)),sha256=sha(file),rows=n,wall_s=meta.get('wall_s'),complete=meta.get('complete')))
        studies[exp]=dict(execution_terminal=True,scientific_scope='Use experiment card and research report; terminal is not a full-validity or growth-success claim',
            returned_generation_records=generated,known_generation_usage=dict(exp_usage),generation_process_seconds=seconds,
            generation_files=records,training_attempts=training,source_target_forward_runs=forwards)
    assert studies['D-E11']['returned_generation_records']==2146
    assert studies['D-E12']['returned_generation_records']==283 and studies['D-E13']['returned_generation_records']==231
    d10=load(results/'D-E10-summary.json')
    assert studies['D-E10']['returned_generation_records']==d10['judgment_attempts']+sum(x['recorded_generation_attempts'] for x in d10['systems'].values())
    result=dict(as_of=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),model_calls_by_this_script=0,
        historical_D_E01_to_D_E09=dict(path=historical_file.name,sha256=sha(historical_file),totals=historical),
        learning_and_interaction_studies=studies,
        totals=dict(recorded_local_generation_responses=historical['local_generations_recorded']+known_generation,
            source_target_forward_rows=historical['source_target_forward_rows']+known_forward,
            successful_training_runs=len(training_ok),failed_training_startups=len(training_failed),
            successful_optimization_steps=sum(x['completed_steps'] for x in training_ok),
            training_sequence_exposures=sum(x['seen_examples'] for x in training_ok),
            training_forward_tokens=sum(x['forward_tokens'] for x in training_ok),
            training_target_tokens=sum(x['target_tokens'] for x in training_ok),
            training_validation_sequence_evaluations=sum(x['validation_sequence_evaluations'] for x in training_ok+training_failed),
            known_training_gpu_process_hours=training_seconds/3600,
            known_total_gpu_process_hours=historical['gpu_process_hours']+(known_seconds+training_seconds)/3600,
            historical_step_plan_recorded_attempts=historical['step_plan_recorded_attempts'],new_step_plan_attempts=0,
            historical_step_plan_recorded_usage=historical['step_plan_recorded_usage'],D_E10_to_D_E13_known_generation_usage=dict(usage)),
        process_duration_unknown_paths=unknown_durations,
        unrecorded_or_uncertain=[
            dict(scope='D-E01--09',local_inflight_upper_bound=historical['unpersisted_local_source_interruption_upper_bound'],api_inflight_upper_bound=historical['unpersisted_api_calibration_upper_bound']),
            dict(scope='D-E10 failed training startups',detail='Zero optimization steps recorded; wall duration not recorded. Do not impute it as zero.'),
            dict(scope='D-E11 initial GPU interruption',detail='21 returned records saved; OOM and in-flight generation count/token usage not fully recorded. Exact total is unknown.'),
            dict(scope='D-E11 judge source-audit interruption',possible_inflight_requests=2,detail='18 returned records saved before stop; in-flight replies/tokens unknown, process wall fully charged.')],
        units='Generation responses count one returned record per model input, not low-level batched generate() invocations or independent scientific samples. Includes invalid/source-disqualified outputs and uniform recoveries. NLL forwards, training exposures, and validation visits are separate. Process wall includes model load/import; controller waits, API wall, and archive CPU time are not added. Known cost is incomplete where startup duration is unavailable.')
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['totals'],ensure_ascii=False,indent=2))


if __name__=='__main__':main()
