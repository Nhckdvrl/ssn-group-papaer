#!/usr/bin/env python3
"""Native character metrics for complete D-E11 cohorts; no API or future reference."""
import argparse
from collections import defaultdict
import copy
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from run_adaptation_pipeline import Q32,read,write

SYSTEMS=['base','update_sft','multitask_sft']
METRICS=['PF','SSF','MDB','PUF','MQ','CR']
INVALID_TRACKER_METRICS={'PF','SSF','MDB'}


def qualify_after_source_audit(tasks):
    """Do not rerun corrected inputs: retain original tasks but invalidate wrong-time metrics."""
    tasks=copy.deepcopy(tasks)
    for task in tasks:
        if task['metric'] in INVALID_TRACKER_METRICS:
            task['unscored_reason']='Source-time audit: scene-end hidden tracker is labeled scene-start in upstream PF/SSF/MDB inputs; no corrected-input rerun in this study'
    return tasks


def selected_score(task,raw):
    # A well-formed answer to an invalid source view cannot enter scientific scores.
    return parse_native_score(raw['response']) if raw and not task.get('unscored_reason') else None


def has_character_state(view):
    """PES requires an observed initial profile or a persisted profile history."""
    return bool(view.get('initial_profile')) or any(x.get('profile') for x in view.get('profile_history',[]))


def parse_native_score(text):
    text=text.strip()
    if text.startswith('```'):text=text.split('\n',1)[-1].rsplit('```',1)[0].strip()
    try:value,end=json.JSONDecoder().raw_decode(text)
    except ValueError:return None
    if not isinstance(value,dict):return None
    for key in ['merits','demerits']:
        if not isinstance(value.get(key),list):return None
        for item in value[key]:
            if not isinstance(item,dict):return None
            x=item.get('points')
            if type(x) not in [int,float] or not math.isfinite(x) or not 1<=abs(x)<=10:return None
    points=lambda key:sum(abs(x['points']) for x in value[key])
    return dict(score=min(100,max(0,50+points('merits')-points('demerits'))),details=value)


def prepare(root):
    evaluation=root/'vendor/EvolvingWorld/evaluation';sys.path.insert(0,str(evaluation))
    import data_loader as dl
    import prompts
    selected=json.loads((root/'data/native_D-E11/snapshots.json').read_text())
    tasks=[]
    for system in SYSTEMS:
        for item in selected:
            index=item['source_index'];book=item['input']['book_name']
            folder=root/'runs/D-E11'/system/('snapshot_'+str(index))
            if not (folder/'meta.json').exists():continue  # Budget-stopped, unattempted book remains missing in aggregation.
            data=dl.load_sample_data(str(folder),snapshot=item['input'])
            scenes=data['all_scenes']['scenes'];summaries={s['scene_index']:dl.format_interactions(s['interactions']) for s in scenes}
            def add(metric,user,scope,role=None):
                name=f'{system}/{index}/{scope}/{metric}'
                system_prompt=prompts.build_cross_scene_character_system_prompt(metric) if metric=='PES' else prompts.build_per_scene_system_prompt(metric)
                task=dict(task_id=name,system=system,book_name=book,snapshot_index=index,metric=metric,role=role,repeat=False,
                          messages=[dict(role='system',content=system_prompt),dict(role='user',content=user)])
                tasks.append(task);return task
            for scene in scenes:
                si=scene['scene_index']
                view=dl.build_per_scene_slice(scene,data['all_scenes'],data['character_dynamic'],data['world_dynamic'],
                    prev_scene_summary=summaries.get(si-1,''),initial_states=data['initial_states'])
                for metric in METRICS:add(metric,prompts.build_per_scene_user_prompt(metric,view),'scene'+str(si))
            eligible=[]
            names={name for scene in scenes for name in scene.get('involved_characters',[]) if name!='Environment'}
            for name in sorted(names):
                view=dl.build_cross_scene_character_slice(name,data['character_dynamic'],data['all_scenes'],summaries,
                                                         initial_states=data['initial_states'])
                if view['num_scenes_participated']>=2:
                    task=add('PES',prompts.build_cross_scene_character_user_prompt('PES',view),
                             'character-'+hashlib.sha256(name.encode()).hexdigest()[:16],name)
                    if has_character_state(view):eligible.append(task)
                    else:task['unscored_reason']='No initial or persisted character profile; do not ask the judge to invent one'
            if eligible:
                repeated=copy.deepcopy(min(eligible,key=lambda x:hashlib.sha256(('D-E11-repeat|'+x['role']).encode()).hexdigest()))
                repeated['repeat']=True;repeated['task_id']+='__repeat';tasks.append(repeated)
    return tasks


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--sync-main',action='store_true')
    p.add_argument('--resume-after-source-audit',action='store_true');a=p.parse_args()
    root=Path(a.asset_root);out=root/'runs/D-E11/judges'
    if a.resume_after_source_audit:
        if not (out/'SOURCE_INPUT_INTERRUPTION.json').exists():raise ValueError('Documented source interruption required')
        if (out/'status_before_source_audit.json').exists():raise FileExistsError('Already resumed; inspect rather than duplicate')
        old=json.loads((out/'status.json').read_text())
        if not old.get('error') or old.get('complete'):raise ValueError('Original coordinator must be terminal before resume')
        (out/'status_before_source_audit.json').write_bytes((out/'status.json').read_bytes())
        (out/'runner_source_qualified.py').write_bytes(Path(__file__).read_bytes())
    else:
        out.mkdir(exist_ok=False);(out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
    status=dict(complete=False,error=None,phase='waiting',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():(out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    def load(path):
        try:return json.loads(path.read_text())
        except (FileNotFoundError,json.JSONDecodeError):return {}
    save()
    try:
        while True:
            generation=load(root/'runs/D-E11/queue_status.json');earlier=load(root/'runs/D-E10/finish_status.json')
            if generation.get('error') or earlier.get('error'):raise RuntimeError('Registered upstream run stopped')
            if generation.get('complete') and earlier.get('complete'):break
            time.sleep(30)
        gpu=os.environ.get('CUDA_VISIBLE_DEVICES','0').split(',')[0]
        while int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())>=1024:time.sleep(30)
        from run_native_rollouts import REVISION,digest
        vendor=root/'vendor/EvolvingWorld'
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=vendor,text=True).strip()!=REVISION:raise ValueError('Upstream judge revision changed')
        status['vendor_revision']=REVISION
        status['upstream_hashes']={name:digest(vendor/'evaluation'/name) for name in ['prompts.py','data_loader.py']}
        tasks=prepare(root)
        if a.resume_after_source_audit:
            if tasks!=read(out/'all_tasks.jsonl'):raise ValueError('Original native tasks changed')
            tasks=qualify_after_source_audit(tasks);write(out/'qualified_tasks.jsonl',tasks)
            status['source_qualification']=json.loads((out/'SOURCE_INPUT_INTERRUPTION.json').read_text())
        else:write(out/'all_tasks.jsonl',tasks)
        status['phase']='judge';save()
        from transformers import AutoTokenizer
        from cache_local_weights import resolve_local_checkpoint
        tok=AutoTokenizer.from_pretrained(resolve_local_checkpoint(Q32)[0],local_files_only=True)
        eligible=[];excluded=[]
        for t in tasks:
            if t.get('unscored_reason'):
                excluded.append(dict(task_id=t['task_id'],reason=t['unscored_reason']));continue
            n=len(tok.apply_chat_template(t['messages'],tokenize=True,add_generation_prompt=True,enable_thinking=False))
            if n+2048>32768:excluded.append(dict(task_id=t['task_id'],input_tokens=n,reason='No truncation; insufficient recovery space'))
            else:eligible.append(t)
        prefix='qualified_' if a.resume_after_source_audit else ''
        write(out/(prefix+'unscored_tasks.jsonl'),excluded);write(out/(prefix+'first_tasks.jsonl'),eligible)
        scoring_errors=[]
        def invoke(file,name,limit):
            used=sum(json.loads(q.read_text()).get('wall_s',0) for q in out.glob('*/metadata.json'))
            if used>=4*3600:
                scoring_errors.append(dict(stage=name,error='Registered D-E11 judge budget exhausted'));return {}
            cmd=[sys.executable,str(Path(__file__).with_name('run_local_text.py')),'--tasks',str(file),'--checkpoint',Q32,
                 '--revision',Path(Q32).name,'--model','qwen3_32b_native_judge','--out',str(out/name),
                 '--max-tokens',str(limit),'--batch-size','2','--max-seconds',str(4*3600-used)]
            with (out/(name+'.log')).open('x') as f:process=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
            if process.returncode:scoring_errors.append(dict(stage=name,returncode=process.returncode,error='Registered worker stopped; preserve completed rows and missing coverage, no automatic retry'))
            file=out/name/'responses.jsonl'
            return {r['task_id']:r for r in read(file)} if file.exists() else {}
        first={r['task_id']:r for r in read(out/'first/responses.jsonl')} if a.resume_after_source_audit else {}
        pending=[t for t in eligible if t['task_id'] not in first]
        if pending:
            file=out/('first_remaining_tasks.jsonl' if a.resume_after_source_audit else 'first_tasks.jsonl')
            if a.resume_after_source_audit:write(file,pending)
            first.update(invoke(file,'first_remaining' if a.resume_after_source_audit else 'first',1024))
        bad=[t for t in eligible if t['task_id'] in first and parse_native_score(first[t['task_id']]['response']) is None];second={}
        if bad and not scoring_errors:
            write(out/'recovery_tasks.jsonl',bad);second=invoke(out/'recovery_tasks.jsonl','recovery',2048)
        selected=[]
        for t in tasks:
            raw=second.get(t['task_id'],first.get(t['task_id']));score=selected_score(t,raw)
            selected.append(dict(**{k:t[k] for k in ['task_id','system','book_name','snapshot_index','metric','role','repeat']},
                                 valid=score is not None,result=score,selected_attempt=2 if t['task_id'] in second else 1 if raw else 0,
                                 unscored_reason=t.get('unscored_reason') or ('No completed response within registered execution' if raw is None else None)))
        write(out/'selected.jsonl',selected)
        books=sorted({t['input']['book_name'] for t in json.loads((root/'data/native_D-E11/snapshots.json').read_text())})
        result=dict(experiment='D-E11',status='AUTOMATED-AGGREGATION-PENDING-CASE-REVIEW',n_books=6,systems={},
                    scope='Short generated native trajectories, six publisher-OOD books, one seed, fixed 8B world. Official character rubric subset; PES sees full generated transcripts, not teacher summaries. Not player study or validated growth accuracy.')
        result['generation_coordinator']=load(root/'runs/D-E11/queue_status.json')
        result['source_qualification']=status.get('source_qualification')
        result['scoring_errors']=scoring_errors
        result['planned_judgments']=len(tasks);result['source_and_context_eligible_judgments']=len(eligible)
        result['valid_judgments']=sum(r['valid'] for r in selected)
        result['judge_process_seconds']=sum(load(q).get('wall_s',0) for q in out.glob('*/metadata.json'))
        result['judge_saved_response_records']=sum(len(read(q)) for q in out.glob('*/responses.jsonl'))
        result['all_generation_cohorts_processed']=all(load(root/'runs/D-E11'/s/'metadata.json').get('complete') for s in SYSTEMS)
        if not result['all_generation_cohorts_processed']:result['status']='PARTIAL-GENERATION-COVERAGE-PENDING-CASE-REVIEW'
        if a.resume_after_source_audit:result['status']='SOURCE-QUALIFIED-PARTIAL-COVERAGE-PENDING-CASE-REVIEW'
        result['interrupted_runs']=[]
        for folder in sorted((root/'runs/D-E11').glob('*_interrupted*')):
            meta=load(folder/'metadata.json')
            result['interrupted_runs'].append(dict(path=str(folder),wall_s=meta.get('wall_s'),
                saved_raw_records=len(read(folder/'raw.jsonl')) if (folder/'raw.jsonl').exists() else 0,
                interruption=load(folder/'INTERRUPTION.json')))
        for system in SYSTEMS:
            meta=load(root/'runs/D-E11'/system/'metadata.json');bybook={}
            realized=meta['processed_snapshots'];all_ok=len(realized)==6 and all(x['stop_reason']!='error' for x in realized)
            for book in books:
                bybook[book]={}
                for metric in METRICS+['PES']:
                    rows=[r for r in selected if r['system']==system and r['book_name']==book and r['metric']==metric and not r['repeat']]
                    bybook[book][metric]=statistics.mean(r['result']['score'] for r in rows) if rows and all(r['valid'] for r in rows) else None
            values={k:statistics.mean(bybook[b][k] for b in books) if all_ok and all(bybook[b][k] is not None for b in books) else None for k in METRICS+['PES']}
            primary={r['task_id']:r for r in selected if r['system']==system and not r['repeat']}
            noise=[]
            for row in selected:
                if row['system']==system and row['repeat'] and row['valid']:
                    initial=primary.get(row['task_id'].removesuffix('__repeat'))
                    if initial and initial['valid']:noise.append(abs(initial['result']['score']-row['result']['score']))
            result['systems'][system]=dict(execution=meta,by_book=bybook,macro_metrics=values,n_repeat_pairs=len(noise),
                                          repeat_mean_absolute_difference=statistics.mean(noise) if noise else None)
        import numpy as np
        draws=np.random.default_rng(173).integers(0,6,(10000,6))
        for system in SYSTEMS:
            comparisons={}
            for metric in METRICS+['PES']:
                values=[result['systems'][s]['macro_metrics'][metric] for s in [system,'base']]
                if all(v is not None for v in values):
                    delta=np.array([result['systems'][system]['by_book'][b][metric]-result['systems']['base']['by_book'][b][metric] for b in books])
                    comparisons[metric]=dict(mean=float(delta.mean()),ci95=np.quantile(delta[draws].mean(1),[.025,.975]).tolist())
            result['systems'][system]['paired_vs_base']=comparisons
        destination=Path(__file__).resolve().parent.parent/'results';name='D-E11-summary.json'
        (destination/name).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        status['phase']='saved_pending_case_review'
        if a.sync_main:
            repo=Path(__file__).resolve().parents[4];file=str((destination/name).relative_to(repo))
            if subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()!='main':raise RuntimeError('Branch changed; results saved')
            subprocess.run(['git','add','--',file],cwd=repo,check=True)
            subprocess.run(['git','commit','--only','-m','保存原生连续互动的完整覆盖和分项读数，等待科研案例审阅','--',file],cwd=repo,check=True)
            subprocess.run(['git','push','origin','main'],cwd=repo,check=True)
        status['all_eligible_judgments_completed']=all(t['task_id'] in first for t in eligible)
        status['scoring_errors']=scoring_errors
        status['complete']=True  # Registered execution terminated and evidence saved, not all metrics scientifically valid.
    except BaseException as e:
        status['error']=repr(e);raise
    finally:
        status['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()


if __name__=='__main__':main()
