#!/usr/bin/env python3
"""E69 complete paired-world outcomes, including observed post-stop continuations."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from native_rule_cross_report import summarize


def metrics(r,source):
    history=r['history']
    valid=[h for h in history if h['legal'] and h.get('executed') and not h.get('stochastic_failure')]
    goals=[h['step'] for h in valid if h['matches_source_goal']]
    requests=[h['step'] for h in valid if h['matches_requested_transfer']]
    item=r['goal_item_id']
    gives=[h for h in valid if h['event_type']=='GiveObjectEvent'
           and h['before'][item]['container']==h['actor'] and h['after'][item]['container']!=h['actor']]
    receiver=gives[0]['after'][item]['container'] if gives else None
    duty=source.get('duty_recipient_id');final=r['original_task_state_flags']
    actor=history[0]['actor'] if history else None
    final_goal=(final['container']==r['original_recipient'] if r['goal_kind']=='give' else
                final['container']==actor and final['equipped']==r['goal_kind'])
    first=history[0] if history else None
    v={'goal':float(r['goal_executed']),'request':float(r['request_given']),
       'both':float(r['both_completed']),
       'first_step_goal':float(bool(first in valid and first and first['matches_source_goal'])),
       'first_step_request':float(bool(first in valid and first and first['matches_requested_transfer'])),
       'any_target_give':float(bool(gives)),
       'first_target_give_to_duty':float(bool(receiver is not None and receiver==duty)),
       'first_target_give_to_requester':float(bool(receiver is not None and receiver==r['requester_id'])),
       'first_target_give_to_other':float(bool(receiver is not None and receiver not in [duty,r['requester_id']])),
       'request_before_goal':float(bool(requests and (not goals or requests[0]<goals[0]))),
       'goal_then_request':float(bool(goals and requests and goals[0]<requests[0])),
       'final_goal_holds':float(bool(final_goal)),
       'final_request_holds':float(final['container']==r['requester_id']),
       'protocol_error':float(bool(r['protocol_error'])),
       'native_rejections':float(sum(not h['legal'] for h in history)),
       'repeat_block_errors':float(sum('already blocking' in h.get('error','').lower() for h in history)),
       'steps':float(len(history))}
    if r['panel']=='matched':
        original=source['case']['goal_command']
        authored=[h for h in valid if h['command']==original]
        v.update(authored_atomic_event=float(bool(authored)),
                 assigned_and_authored_events=float(bool(r['goal_executed'] and authored)))
    if r['panel']=='continuation':
        v.update(old_goal=float(r['old_goal_executed']),old_request=float(r['old_request_given']),
                 added_request=float(r['request_given'] and not r['old_request_given']),
                 give_after_old_stop=float(any(h['step']>=r['old_steps'] and h['matches_requested_transfer'] for h in valid)))
    return v


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--data',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();pairs={r['case']['case_id']:r for r in map(json.loads,(a.data/'paired_tasks.jsonl').read_text().splitlines())}
    cont={r['case']['case_id']:r for r in map(json.loads,(a.data/'continuation_tasks.jsonl').read_text().splitlines())}
    rows=[];manifests=[];runtimes=[];calls=Counter()
    for d in a.runs:
        assert (d/'runtime.json').exists()
        manifests.append(json.loads((d/'manifest.json').read_text()));runtimes.append(json.loads((d/'runtime.json').read_text()))
        rows.extend(map(json.loads,(d/'episodes.jsonl').read_text().splitlines()))
        for line in (d/'model_calls.jsonl').open():
            r=json.loads(line);calls.update(count=1,parse_errors=int(bool(r['parse_error'])),prompt_tokens=r['prompt_tokens'],completion_tokens=r['completion_tokens'])
    assert all(m['driver_sha256']==manifests[0]['driver_sha256'] and m['dataset_sha256']==manifests[0]['dataset_sha256']
               and m['model']==manifests[0]['model'] for m in manifests)
    lookup={(r['panel'],r['case_id'],r['seed'],r['persona'],r['task_condition'],r['rule']):r for r in rows}
    expected={('matched',cid,s,p,t,'generic_priority') for cid in pairs for s in [6901,6902,6903] for p in ['firm','agreeable'] for t in ['equip','duty_give']}
    expected|={('continuation',cid,s,p,'source',rule) for cid in cont for s in [6801,6802,6803] for p in ['firm','agreeable'] for rule in ['generic_priority','negative_only']}
    assert len(lookup)==len(rows)==1380 and set(lookup)==expected
    values={k:metrics(r,pairs[k[1]] if k[0]=='matched' else cont[k[1]]) for k,r in lookup.items()}
    cells={};contrasts={}
    def estimate(keys,terms,seeds):
        fields=list(values[('matched' if seeds[0]==6901 else 'continuation',keys[0],seeds[0],*terms[0][1])])
        matrix=[]
        for cid in keys:
            matrix.append(np.mean([[sum(w*values[(panel,cid,s,*condition)][f] for w,condition in terms) for f in fields] for s in seeds],axis=0))
        return summarize(matrix,fields)
    panel='matched';seeds=[6901,6902,6903]
    for scope in ['all','source_give','source_equip','confirm','reserve']:
        ids=sorted(cid for cid,row in pairs.items() if scope=='all' or
                   (scope=='source_give' and row['case']['goal_kind']=='give') or
                   (scope=='source_equip' and row['case']['goal_kind'] in ['wear','wield']) or scope==row['split'])
        for p in ['firm','agreeable']:
            for task in ['equip','duty_give']:
                condition=(p,task,'generic_priority');cells[f'{scope}/{p}/{task}']=estimate(ids,[(1,condition)],seeds)
        for task in ['equip','duty_give']:
            contrasts[f'{scope}/A_minus_F/{task}']=estimate(ids,[(1,('agreeable',task,'generic_priority')),(-1,('firm',task,'generic_priority'))],seeds)
        contrasts[f'{scope}/persona_x_task']=estimate(ids,[(1,('agreeable','duty_give','generic_priority')),(-1,('firm','duty_give','generic_priority')),(-1,('agreeable','equip','generic_priority')),(1,('firm','equip','generic_priority'))],seeds)
    panel='continuation';seeds=[6801,6802,6803];continuation_cells={}
    for p in ['firm','agreeable']:
        for rule in ['generic_priority','negative_only']:
            condition=(p,'source',rule)
            continuation_cells[p+'/'+rule]=estimate(sorted(cont),[(1,condition)],seeds)
    examples=[]
    for k,r in sorted(lookup.items()):
        if r['panel']=='continuation':
            examples.append({key:r[key] for key in ['case_id','seed','persona','rule','goal_command','old_steps','old_goal_executed','old_request_given','goal_executed','request_given','both_completed']} |
                {'history':[{'command':h['command'],'legal':h['legal'],'goal':h['goal_executed_after'],'request':h['request_given_after']} for h in r['history']]})
    assert calls['count']==sum(r['calls'] for r in runtimes)
    report={'status':'COMPLETE','experiment':'E69','model':manifests[0]['model'],'episodes':len(rows),
            'matched_worlds':len(pairs),'continuation_worlds':len(cont),'cells':cells,'contrasts':contrasts,
            'continuation_cells':continuation_cells,'continuation_trajectories':examples,
            'calls':dict(calls),'reused_calls':sum(r['reused_calls'] for r in runtimes),
            'runtime_gpu_hours':sum(r['wall_seconds']+r['model_load_seconds'] for r in runtimes)/3600,
            'runtimes':runtimes,'native_errors':dict(Counter(h.get('error','') for r in rows for h in r['history'] if not h['legal'])),
            'native_stochastic_failures':sum(bool(h.get('stochastic_failure')) for r in rows for h in r['history']),
            'scope':['Matched assigned tasks in known source worlds; not 112 new held-out worlds.',
                     'Three seeds averaged within graph; 4000 paired graph bootstrap resamples; pointwise intervals.',
                     'Task interaction does not separately identify lexical priming or utility preferences.',
                     'Continuation 3-world panel diagnoses cited cases; no population-frequency inference.',
                     'Executed intermediate event and final physical state are distinct.'],
            'source_sha256':{str(d/'episodes.jsonl'):hashlib.sha256((d/'episodes.jsonl').read_bytes()).hexdigest() for d in a.runs}}
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','experiment','episodes','matched_worlds','calls','runtime_gpu_hours']}))


if __name__=='__main__':main()
