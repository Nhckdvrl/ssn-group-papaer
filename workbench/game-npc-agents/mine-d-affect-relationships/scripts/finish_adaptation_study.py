#!/usr/bin/env python3
"""Wait for all registered runs, compute shared-consumer readouts, save and sync results."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from run_adaptation_pipeline import SYSTEMS,Q8,read,write


def load(path):
    try:return json.loads(path.read_text())
    except (FileNotFoundError,json.JSONDecodeError):return {}


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--sync-main',action='store_true');a=p.parse_args()
    root=Path(a.asset_root);runs=root/'runs/D-E10';status_path=runs/'finish_status.json';scripts=Path(__file__).resolve().parent
    status=dict(complete=False,phase='waiting_for_full_registered_results',error=None)
    def save():
        status['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        status_path.write_text(json.dumps(status,indent=2)+'\n')
    save()
    try:
        while True:
            all_meta=[load(runs/('system_'+s)/'metadata.json') for s in SYSTEMS]
            judge=load(runs/'judges/queue_status.json')
            if judge.get('error') or any(m.get('error') for m in all_meta):raise RuntimeError('A registered system or judge stopped; no survivor-only summary')
            for mode in ['update','multitask']:
                training=load(runs/('train_'+mode+'_v2/metadata.json'))
                if training.get('error') or training.get('stop_reason'):raise RuntimeError('Training did not finish; retain incomplete state')
            if all(m.get('complete') for m in all_meta) and judge.get('complete'):break
            time.sleep(30)
        gpu=os.environ.get('CUDA_VISIBLE_DEVICES','0').split(',')[0]
        while int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())>=1024:time.sleep(30)
        status['phase']='fixed_consumer_likelihood';save()
        tasks=[];refs=[]
        for system in SYSTEMS:
            for r in read(runs/('system_'+system)/'actor_tasks.jsonl'):
                tasks.append(dict(r,trajectory_id=r['episode_id'],after_updates=1,condition=system))
        for r in read(root/'data/evaluation_D-E10/references.jsonl'):
            refs.extend(dict(question_id=k,target=v) for k,v in r['responses'].items())
        data=root/'data/evaluation_D-E10';write(data/'likelihood_tasks.jsonl',tasks);write(data/'likelihood_references.jsonl',refs)
        cmd=[sys.executable,str(scripts/'score_role_likelihood.py'),'--tasks',str(data/'likelihood_tasks.jsonl'),
            '--references',str(data/'likelihood_references.jsonl'),'--checkpoint',Q8,'--revision',Path(Q8).name,
            '--model','qwen3_8b_fixed_readout','--out',str(runs/'likelihood')]
        with (root/'logs/D-E10-fixed-likelihood.log').open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
        status['phase']='aggregate';save();results=scripts.parent/'results'
        subprocess.run([sys.executable,str(scripts/'summarize_adaptation_study.py'),'--asset-root',str(root),'--out',str(results)],check=True)
        status['phase']='results_saved_pending_scientific_case_review'
        if a.sync_main:
            repo=scripts.parents[3]
            branch=subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()
            if branch!='main':raise RuntimeError('Results saved; current branch changed, will not alter it')
            files=[str((results/name).relative_to(repo)) for name in ['D-E10-summary.json','D-E10-RUN-REPORT.md']]
            subprocess.run(['git','add','--',*files],cwd=repo,check=True)
            subprocess.run(['git','diff','--cached','--check','--',*files],cwd=repo,check=True)
            subprocess.run(['git','commit','--only','-m','保存人物适应SFT与后续互动全量读数，保留评价范围和待审阅状态','--',*files],cwd=repo,check=True)
            subprocess.run(['git','push','origin','main'],cwd=repo,check=True)
            status['result_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
        status['complete']=True
    except BaseException as error:
        status['error']=repr(error);raise
    finally:save()


if __name__=='__main__':main()
