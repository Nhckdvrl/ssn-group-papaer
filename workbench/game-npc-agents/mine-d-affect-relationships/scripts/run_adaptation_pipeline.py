#!/usr/bin/env python3
"""Run a frozen D-E10 system: completed experience -> state -> motivation -> role turns."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from adaptation_protocol import decode_state,decode_motivation,motivation_messages,actor_messages

Q8='/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218'
Q32='/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137'
SYSTEMS=['base','update_sft','multitask_sft','strong32','released','full_evidence','frozen']


def read(path):return [json.loads(l) for l in Path(path).read_text().splitlines()]
def write(path,rows):
    with Path(path).open('x') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--system',choices=SYSTEMS,required=True)
    p.add_argument('--max-hours',type=float,default=2.5);a=p.parse_args();root=Path(a.asset_root)
    data=root/'data/evaluation_D-E10';out=root/'runs/D-E10'/('system_'+a.system);out.mkdir(parents=True,exist_ok=False)
    episodes=read(data/'episodes.jsonl');refs={r['episode_id']:r for r in read(data/'references.jsonl')}
    byid={e['episode_id']:e for e in episodes};base=Q32 if a.system=='strong32' else Q8
    training=None
    if a.system in ['update_sft','multitask_sft']:
        name='update' if a.system=='update_sft' else 'multitask';train=root/'runs/D-E10'/('train_'+name+'_v2')
        training=json.loads((train/'metadata.json').read_text())
        if not training.get('complete'):raise ValueError('Training not complete; no partial-checkpoint substitution')
        adapter=train/'final'
    else:adapter=None
    meta=dict(experiment='D-E10',system=a.system,started_utc=now(),complete=False,
        episode_sha256=sha(data/'episodes.jsonl'),references_sha256=sha(data/'references.jsonl'),
        runner_sha256=sha(__file__),protocol_sha256=sha(Path(__file__).with_name('adaptation_protocol.py')),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        base_checkpoint=base,adapter=str(adapter) if adapter else None,max_hours=a.max_hours)
    (out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
    (out/'protocol_source.py').write_bytes(Path(__file__).with_name('adaptation_protocol.py').read_bytes())
    start=time.monotonic()
    def save():(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    save()
    stages=[]
    def run_stage(tasks,name,cap,recovery,validator):
        if time.monotonic()-start>=a.max_hours*3600:raise TimeoutError('Registered system budget reached before stage')
        path=out/(name+'_tasks.jsonl');write(path,tasks)
        use_adapter=adapter if a.system=='multitask_sft' or name=='update' else None
        def invoke(taskpath,folder,limit):
            cmd=[sys.executable,str(Path(__file__).with_name('run_local_text.py')),'--tasks',str(taskpath),
                '--checkpoint',base,'--revision',Path(base).name,'--model',a.system,'--out',str(folder),
                '--max-tokens',str(limit),'--batch-size','4','--max-seconds',str(max(1,a.max_hours*3600-(time.monotonic()-start)))]
            if use_adapter:cmd+=['--adapter',str(use_adapter)]
            with (out/(folder.name+'.log')).open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
            stages.append(str(folder))
            return {r['task_id']:r for r in read(folder/'responses.jsonl')}
        first=invoke(path,out/name,cap)
        bad=[t for t in tasks if first[t['task_id']]['finish_reason']!='stop' or validator(first[t['task_id']],t) is None]
        extra={}
        if bad:
            if time.monotonic()-start>=a.max_hours*3600:raise TimeoutError('Registered system budget reached before recovery')
            recover_path=out/(name+'_recovery_tasks.jsonl');write(recover_path,bad)
            extra=invoke(recover_path,out/(name+'_recovery'),recovery)
        selected=[]
        for t in tasks:
            uid=t['task_id'];r=extra.get(uid,first[uid]);v=validator(r,t)
            good=r['finish_reason']=='stop' and v is not None
            selected.append(dict(record=r,value=v if good else None,valid=good,selected_attempt=2 if uid in extra else 1))
        return selected
    try:
        states={};state_records=[]
        if a.system in ['released','frozen','full_evidence']:
            for e in episodes:
                states[e['episode_id']]=refs[e['episode_id']]['state'] if a.system=='released' else e['before_state']
                state_records.append(dict(episode_id=e['episode_id'],state=states[e['episode_id']],valid=True,source=a.system))
        else:
            tasks=[dict(task_id=e['episode_id']+'/update',episode_id=e['episode_id'],book_name=e['book'],role=e['role'],messages=e['update_input']) for e in episodes]
            selected=run_stage(tasks,'update',4096,8192,lambda r,t:decode_state(r['response'],byid[t['episode_id']]['before_state']))
            for r in selected:
                eid=r['record']['episode_id'];states[eid]=r['value'] or byid[eid]['before_state']
                state_records.append(dict(episode_id=eid,state=states[eid],valid=r['valid'],selected_attempt=r['selected_attempt'],carried_previous=not r['valid']))
        write(out/'states.jsonl',state_records)
        motivations={};mot_records=[]
        if a.system=='released':
            for e in episodes:
                eid=e['episode_id'];motivations[eid]=refs[eid]['motivation'];mot_records.append(dict(episode_id=eid,motivation=motivations[eid],valid=True,source='published'))
        else:
            tasks=[dict(task_id=e['episode_id']+'/motivation',episode_id=e['episode_id'],book_name=e['book'],role=e['role'],
                messages=motivation_messages(e,states[e['episode_id']],a.system=='full_evidence')) for e in episodes]
            selected=run_stage(tasks,'motivation',1024,2048,lambda r,t:decode_motivation(r['response']))
            for r in selected:
                eid=r['record']['episode_id'];motivations[eid]=r['value'] or ''
                mot_records.append(dict(episode_id=eid,motivation=motivations[eid],valid=r['valid'],selected_attempt=r['selected_attempt']))
        write(out/'motivations.jsonl',mot_records)
        tasks=[]
        for e in episodes:
            eid=e['episode_id']
            for q in e['queries']:
                tasks.append(dict(task_id=q['question_id']+'/'+a.system,question_id=q['question_id'],episode_id=eid,
                    system=a.system,book_name=e['book'],role=e['role'],preselected_review=e['preselected_review'],
                    messages=actor_messages(e,q,states[eid],motivations[eid],a.system=='full_evidence')))
        selected=run_stage(tasks,'actor',768,1536,lambda r,t:r['response'].strip() or None)
        outputs=[]
        for item in selected:
            r=item['record'];outputs.append(dict(r,valid=item['valid'],selected_attempt=item['selected_attempt']))
        write(out/'outputs.jsonl',outputs)
        meta.update(complete=True,n_episodes=len(episodes),n_outputs=len(outputs),valid_outputs=sum(r['valid'] for r in outputs),
                    valid_states=sum(r['valid'] for r in state_records),valid_motivations=sum(r['valid'] for r in mot_records))
    except BaseException as error:
        meta['error']=repr(error);raise
    finally:
        meta.update(finished_utc=now(),wall_s=time.monotonic()-start,completed_generation_runs=stages)
        all_runs=[f.parent for f in out.glob('*/metadata.json')]
        meta['all_generation_runs']=[str(s) for s in all_runs]
        meta['recorded_generation_attempts']=sum(len(read(s/'responses.jsonl')) for s in all_runs if (s/'responses.jsonl').exists())
        meta['gpu_process_hours']=sum(json.loads((s/'metadata.json').read_text()).get('wall_s',0) for s in all_runs)/3600
        save()


if __name__=='__main__':main()
