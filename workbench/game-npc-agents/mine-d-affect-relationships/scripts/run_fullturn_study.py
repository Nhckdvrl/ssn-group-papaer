#!/usr/bin/env python3
"""D-E12 complete-dialogue baseline, followed by the unchanged D-E10 readouts."""
import argparse
from collections import defaultdict
import datetime
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from run_adaptation_pipeline import Q8,Q32,read,write
from score_adaptation_quality import prepare,parse_score,DIMENSIONS
from summarize_adaptation_study import aggregate_primary


def load(path):
    try:return json.loads(path.read_text())
    except (FileNotFoundError,json.JSONDecodeError):return {}


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--sync-main',action='store_true');a=p.parse_args()
    root=Path(a.asset_root);run=root/'runs/D-E12';run.mkdir(exist_ok=False);scripts=Path(__file__).resolve().parent
    status=dict(complete=False,error=None,phase='waiting_for_training_gpu',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        status['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        (run/'finish_status.json').write_text(json.dumps(status,indent=2)+'\n')
    def idle():
        gpu=os.environ.get('CUDA_VISIBLE_DEVICES','3').split(',')[0]
        return int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())<1024
    def invoke(command,log,timeout=None):
        with (root/'logs'/log).open('x') as f:subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=timeout)
    save();(run/'coordinator_source.py').write_bytes(Path(__file__).read_bytes())
    try:
        while not idle():time.sleep(30)
        status['phase']='training';save();train=run/'train_multitask_fullturn'
        invoke([sys.executable,str(scripts/'train_adaptation_sft.py'),'--data',str(root/'data/training_D-E12'),
            '--checkpoint',Q8,'--mode','multitask','--out',str(train),'--max-hours','24'],'D-E12-training.log')
        if not load(train/'metadata.json').get('complete'):raise RuntimeError('Complete final training checkpoint required')
        # The already registered D-E11 judge gets the GPU before new D-E12 inference.
        status['phase']='yielding_gpu_to_registered_native_judge';save()
        while True:
            native=load(root/'runs/D-E11/judges/status.json')
            if native.get('complete') or native.get('error'):break
            time.sleep(30)
        while not idle():time.sleep(30)
        start=time.monotonic()
        def remaining():
            value=4*3600-(time.monotonic()-start)
            if value<=0:raise TimeoutError('Registered D-E12 inference budget exhausted')
            return value
        status['phase']='state_motivation_actor';save()
        invoke([sys.executable,str(scripts/'run_adaptation_pipeline.py'),'--asset-root',str(root),
            '--system','multitask_sft','--experiment','D-E12','--training-run',str(train),
            '--max-hours',str(min(2.5,remaining()/3600))],'D-E12-pipeline.log',remaining())
        status['phase']='blind_judge';save();judge=run/'judge';judge.mkdir()
        tasks=prepare(root,'multitask_sft',judge,runs_root=run)
        def score(file,name,cap):
            invoke([sys.executable,str(scripts/'run_local_text.py'),'--tasks',str(file),'--checkpoint',Q32,
                '--revision',Path(Q32).name,'--model','qwen3_32b_judge','--out',str(judge/name),
                '--max-tokens',str(cap),'--batch-size','2','--max-seconds',str(remaining())],
                'D-E12-judge-'+name+'.log',remaining())
            return {r['task_id']:r for r in read(judge/name/'responses.jsonl')}
        first=score(judge/'tasks.jsonl','first',1024)
        bad=[t for t in tasks if parse_score(first[t['task_id']]['response']) is None];second={}
        if bad:
            write(judge/'recovery_tasks.jsonl',bad);second=score(judge/'recovery_tasks.jsonl','recovery',2048)
        selected=[]
        for t in tasks:
            raw=second.get(t['task_id'],first[t['task_id']]);value=parse_score(raw['response'])
            selected.append(dict(**{k:t[k] for k in ['task_id','question_id','episode_id','book_name','role','system','repeat']},
                valid=value is not None,result=value,selected_attempt=2 if t['task_id'] in second else 1,finish_reason=raw['finish_reason']))
        write(judge/'selected.jsonl',selected)
        status['phase']='fixed_consumer_likelihood';save()
        actor=[dict(r,trajectory_id=r['episode_id'],after_updates=1,condition='fullturn_sft') for r in read(run/'system_multitask_sft/actor_tasks.jsonl')]
        refs=[dict(question_id=k,target=v) for r in read(root/'data/evaluation_D-E10/references.jsonl') for k,v in r['responses'].items()]
        write(run/'likelihood_tasks.jsonl',actor);write(run/'likelihood_references.jsonl',refs)
        invoke([sys.executable,str(scripts/'score_role_likelihood.py'),'--tasks',str(run/'likelihood_tasks.jsonl'),
            '--references',str(run/'likelihood_references.jsonl'),'--checkpoint',Q8,'--revision',Path(Q8).name,
            '--model','qwen3_8b_fixed_readout','--out',str(run/'likelihood')],'D-E12-likelihood.log',remaining())
        status['phase']='aggregate';save()
        primary=[r for r in selected if not r['repeat']];books=sorted({r['book_name'] for r in primary})
        good,bybook,metrics=aggregate_primary(primary,books,87)
        noise=[statistics.mean(abs(r['result']['scores'][k]-good[r['question_id']][k]) for k in DIMENSIONS)
            for r in selected if r['repeat'] and r['valid'] and r['question_id'] in good]
        old=json.loads((scripts.parent/'results/D-E10-summary.json').read_text())
        result=dict(experiment='D-E12',status='AUTOMATED-RESULTS-PENDING-SCIENTIFIC-REVIEW',n_books=6,n_episodes=47,n_queries=87,
            interpretation='Post-D-E10 exploratory full-conversation supervision baseline. Same held-out source cohort, already observed; not independent confirmation or a new algorithm.',
            training=load(train/'metadata.json'),pipeline=load(run/'system_multitask_sft/metadata.json'),
            valid_primary=len(good),dimensions=metrics,by_book=bybook,macro_quality=statistics.mean(metrics.values()) if metrics else None,
            repeat_pairs=len(noise),repeat_mean_absolute_difference=statistics.mean(noise) if noise else None,
            inference_wall_s=time.monotonic()-start,paired_vs={})
        import numpy as np
        draws=np.random.default_rng(173).integers(0,6,(10000,6))
        if metrics:
            current=np.array([statistics.mean(bybook[b].values()) for b in books])
            for name,values in old['systems'].items():
                baseline=np.array([statistics.mean(values['by_book'][b].values()) for b in books])
                delta=current-baseline;result['paired_vs'][name]=dict(mean=float(delta.mean()),ci95=np.quantile(delta[draws].mean(1),[.025,.975]).tolist())
        nll=read(run/'likelihood/scores.jsonl');perrole=defaultdict(list)
        for row in nll:perrole[row['book_name'],row['trajectory_id']].append(row['mean_target_nll'])
        result['fixed_consumer_nll']=statistics.mean(statistics.mean(statistics.mean(v) for (b,_),v in perrole.items() if b==book) for book in books)
        for label,file in [('validation',train/'validation.jsonl')]:
            result[label]=[{k:v for k,v in row.items() if k!='rows'} for row in read(file)]
        result['manifest']=load(root/'data/training_D-E12/manifest.json')
        destination=scripts.parent/'results';(destination/'D-E12-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        lines=['# D-E12：完整对话监督的自动汇总','',
            '执行完成；同一已观察D-E10 cohort的探索性后续，尚待完整人物链审阅，不是独立确认或新方法证明。','',
            f"87个后续context；有效正式评分{len(good)}/87；六作品宏均{result['macro_quality']}。",'',
            '| 参照 | 本路径减参照，均分差 | 六作品配对95%区间 |','|---|---:|---|']
        for name,value in result['paired_vs'].items():lines.append(f"| {name} | {value['mean']:+.3f} | {value['ci95']} |")
        lines+=['','完整训练监督、逐任务验证、成本及分项见[D-E12-summary.json](D-E12-summary.json)。评分不是成长准确率；更短或更长均不自动等于更好。']
        (destination/'D-E12-RUN-REPORT.md').write_text('\n'.join(lines)+'\n')
        if a.sync_main:
            repo=scripts.parents[3];files=[str((destination/f).relative_to(repo)) for f in ['D-E12-summary.json','D-E12-RUN-REPORT.md']]
            if subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()!='main':raise RuntimeError('Branch changed; results saved')
            subprocess.run(['git','add','--',*files],cwd=repo,check=True)
            subprocess.run(['git','commit','--only','-m','保存完整对话监督的同预算基线结果，保留探索性比较范围','--',*files],cwd=repo,check=True)
            subprocess.run(['git','push','origin','main'],cwd=repo,check=True)
        status['complete']=True;status['phase']='results_saved_pending_case_review'
    except BaseException as error:
        status['error']=repr(error);raise
    finally:save()


if __name__=='__main__':main()
