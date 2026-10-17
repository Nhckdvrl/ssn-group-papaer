#!/usr/bin/env python3
"""E69 adaptive post-completion notices; preserve all recorded pre-completion decisions."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import native_matched_task_execution as core

NOTICES={
    'completion_notice':'Your current assigned task has been completed. Decide what to do next using your authored motivations and the visible request.',
    'mechanics_fact':'An equipped item must be removed before it can be given to another character. Removing it is a legal game action when available.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--data',type=Path,required=True);ap.add_argument('--old-runs',type=Path,nargs='+',required=True)
    ap.add_argument('--base-runs',type=Path,nargs='+',required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();core.configure()
    sources=list(map(json.loads,(a.data/'continuation_tasks.jsonl').read_text().splitlines()));assert len(sources)==3
    old={};traces=[]
    for d in a.old_runs:
        assert (d/'runtime.json').exists();traces.append(d/'model_calls.jsonl')
        for r in map(json.loads,(d/'episodes.jsonl').read_text().splitlines()):
            if r['mode']=='goal_item' and r['upstream_rule']==r['exec_rule']:
                old[(r['case_id'],r['seed'],r['persona'],r['upstream_rule'])]=r
    baseline={}
    for d in a.base_runs:
        assert (d/'runtime.json').exists();traces.append(d/'model_calls.jsonl')
        for r in map(json.loads,(d/'episodes.jsonl').read_text().splitlines()):
            if r['panel']=='continuation':baseline[r['case_id'],r['seed'],r['persona'],r['rule']]=r
    assert len(baseline)==36
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'experiment':'E69','adaptive_after':'Panel A yielded zero joint events in 72 model trajectories.',
              'controls':NOTICES,'intervention':'Only after the native goal event has already executed.',
              'model':str(a.model),'worlds':3,'expected_episodes':72,'base_runs':list(map(str,a.base_runs)),
              'script_sha256':core.sha(Path(__file__)),'core_sha256':core.sha(Path(core.__file__)),
              'world_modified':False,'cloud_calls':0}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=core.policy.load_event_modules(core.policy.CACHE/'sources/LIGHT')
    client=core.SharedPrefixClient(a.model,a.out,6801);preload=time.monotonic()
    for path in traces:
        for r in map(json.loads,path.open()):client.cache.setdefault(core.decision_key(r),r['parsed'])
    client.inner.load_seconds+=time.monotonic()-preload
    original_spec=core.spec
    def controlled_spec(b,stage,modules,graph=None,history=None,flags=None):
        messages,schema=original_spec(b,stage,modules,graph,history,flags)
        if stage=='exec' and flags['original_goal_event_actually_executed']:
            messages[-1]['content']+='\n'+NOTICES[b['control']]
        return messages,schema
    core.spec=controlled_spec
    count=0;start=time.monotonic()
    for source in sources:
        c={**source['case']};req=source['requests']['goal_item']
        c.update(request_text=req['request_text'],request_command=req['command'],request_item_id=req['item_id'])
        bases=[]
        for seed in [6801,6802,6803]:
            for p in ['firm','agreeable']:
                for rule in ['generic_priority','negative_only']:
                    prior=old[c['case_id'],seed,p,rule]
                    for control in NOTICES:
                        bases.append({'panel':'continuation','task_condition':'source','control':control,
                            'case':c,'seed':seed,'persona':p,'rule':rule,'source_goal_kind':c['goal_kind'],
                            'source_split':'reserve','sampling_seed':seed+int(c['case_id'][:7],16)*10,
                            'conversation':prior['conversation'],'update':prior['update']})
        count+=core.run_group(bases,client,modules,a.out,old)
        print(json.dumps({'episodes':count,'calls':client.inner.calls,'wall_seconds':time.monotonic()-start}),flush=True)
    rows=list(map(json.loads,(a.out/'episodes.jsonl').read_text().splitlines()));assert count==len(rows)==72
    for r in rows:
        base=baseline[r['case_id'],r['seed'],r['persona'],r['rule']]
        assert r['goal_executed']==base['goal_executed']
        first_goal=next((h['step'] for h in base['history'] if h['goal_executed_after']),8)
        assert r['history'][:first_goal+1]==base['history'][:first_goal+1]
    runtime={'episodes':count,'calls':client.inner.calls,'reused_calls':client.reused,
             'wall_seconds':time.monotonic()-start,'model_load_seconds':client.inner.load_seconds,
             'pre_goal_histories_identical':True,'cloud_calls':0}
    (a.out/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n');print(json.dumps(runtime),flush=True)


if __name__=='__main__':main()
