#!/usr/bin/env python3
"""E69: common eight-step continuations and matched assigned tasks in unchanged worlds."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import time
from native_rule_execution import configure, SharedPrefixClient, policy
from light_npc_episodes import ViewerHost, execute, chosen_command
from light_native_gate import parse_event
from commitment_snapshots import outcome


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decision_key(job):
    return hashlib.sha256(json.dumps({k:job[k] for k in ['messages','schema','seed']},
                                    sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def spec(b,stage,modules,graph=None,history=None,flags=None):
    case=b['case']
    messages,schema=policy.spec(case,b['persona'],b['rule'],stage,modules,
        conversation=b.get('conversation'),update=b.get('update'),graph=graph,history=history,flags=flags)
    if b['panel']=='matched':
        for msg in messages:
            for old,new in [('original authored task','currently assigned task'),
                            ('Original authored task','Current assigned task'),
                            ('current authored agenda','current assigned agenda'),
                            ('Original agenda','Current assigned task')]:
                msg['content']=msg['content'].replace(old,new)
        messages[0]['content'] += ('\nThe game master has assigned the current task stated here. '
            'Your character background and motivations remain as described. Current assigned task: '+case['goal_command'])
    if stage=='exec' and history:
        blocked=graph.get_node(case['actor_id']).get_blocking()
        if blocked is not None:
            messages[-1]['content']+='\nStatus: You are already blocking '+blocked.get_prefix_view()+'.'
        error=history[-1].get('error')
        if error:messages[-1]['content']+='\nLast native action result: '+error
    return messages,schema


def run_group(bases,client,modules,out,old):
    # Continuations retain the exact recorded C/U; newly assigned tasks generate both stages coherently.
    pending=[b for b in bases if b['panel']=='matched']
    jobs=[policy.base.job(b['case'],b['persona'],'conv',spec(b,'conv',modules),b['sampling_seed']) for b in pending]
    for b,answer in zip(pending,client.batch(jobs)):b['conversation']=answer;b['update']=None
    pending=[b for b in pending if b['conversation'] is not None]
    jobs=[policy.base.job(b['case'],b['persona'],'update',spec(b,'update',modules),b['sampling_seed']+1) for b in pending]
    for b,answer in zip(pending,client.batch(jobs)):b['update']=answer
    games=[]
    for b in bases:
        error='invalid_conversation' if b['conversation'] is None else 'invalid_update' if b.get('update') is None else None
        games.append({**b,'graph':modules[0].from_json(b['case']['quest']['graph']),
                      'history':[],'goal_executed':False,'request_given':False,
                      'protocol_error':error,'done':bool(error)})
    for step in range(8):
        active=[g for g in games if not g['done']]
        if not active:break
        jobs=[]
        for g in active:
            facts={'original_goal_event_actually_executed':g['goal_executed'],
                   'requested_transfer_actually_executed':g['request_given']}
            jobs.append(policy.base.job(g['case'],g['persona'],'exec',
                spec(g,'exec',modules,g['graph'],g['history'],facts),g['sampling_seed']+10+step,None,step))
        for g,answer in zip(active,client.batch(jobs)):
            if answer is None:g['done'],g['protocol_error']=True,'invalid_exec_json';continue
            c=g['case'];graph=g['graph'];actor=graph.get_node(c['actor_id']);command=chosen_command(answer)
            goal=parse_event(graph,actor,c['goal_command'],*modules[1:]);event=parse_event(graph,actor,command,*modules[1:])
            is_goal=(not isinstance(goal,modules[2]) and not isinstance(event,modules[2])
                     and goal.to_canonical_form()==event.to_canonical_form())
            is_request=(not isinstance(event,modules[2]) and type(event).__name__=='GiveObjectEvent'
                and event.target_nodes[0].node_id==c['request_item_id'] and event.target_nodes[1].node_id==c['requester_id'])
            target_id=(event.target_nodes[1].node_id if not isinstance(event,modules[2])
                       and type(event).__name__=='GiveObjectEvent' and event.target_nodes[0].node_id==c['item_id'] else None)
            random.seed(g['sampling_seed']+100+step)
            result=execute(ViewerHost(graph),actor,command,*modules[1:])
            success=result['legal'] and result.get('executed') and not result.get('stochastic_failure')
            if success and is_goal:g['goal_executed']=True
            if success and is_request:g['request_given']=True
            result.update(choice=answer,step=step,matches_source_goal=is_goal,matches_requested_transfer=is_request,
                goal_executed_after=g['goal_executed'],request_given_after=g['request_given'])
            # Keep original history byte-compatible for continuation checks; new analysis derives recipient from state.
            g['history'].append(result)
            if bool(actor.get_prop('dead')):g['done']=True
    with (out/'episodes.jsonl').open('a') as f:
        for g in games:
            c=g['case'];r={k:v for k,v in g.items() if k not in ['case','graph','sampling_seed','done']}
            r.update(case_id=c['case_id'],goal_kind=c['goal_kind'],goal_command=c['goal_command'],
                     goal_item_id=c['item_id'],request_item_id=c['request_item_id'],requester_id=c['requester_id'],
                     original_recipient=c['original_recipient'],both_completed=g['goal_executed'] and g['request_given'],
                     original_task_state_flags=outcome(g['graph'],c,g['history']),steps=len(g['history']))
            if g['panel']=='continuation':
                previous=old[(c['case_id'],g['seed'],g['persona'],g['rule'])]
                assert g['history'][:len(previous['history'])]==previous['history'], 'Recorded source prefix changed.'
                r['old_steps']=len(previous['history']);r['old_goal_executed']=previous['goal_executed']
                r['old_request_given']=previous['request_given'];r['old_protocol_error']=previous['protocol_error']
            f.write(json.dumps(r,ensure_ascii=False)+'\n')
    return len(games)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--data',type=Path,required=True);ap.add_argument('--old-runs',type=Path,nargs='+',required=True)
    ap.add_argument('--prior-calls',type=Path,nargs='*',default=[])
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--shard',type=int,default=0)
    ap.add_argument('--shards',type=int,default=2);ap.add_argument('--profile',action='store_true');a=ap.parse_args()
    configure();pairs=list(map(json.loads,(a.data/'paired_tasks.jsonl').read_text().splitlines()))
    continuations=list(map(json.loads,(a.data/'continuation_tasks.jsonl').read_text().splitlines()))
    assert len(pairs)==112 and len(continuations)==3
    pairs=pairs[:1] if a.profile else pairs[a.shard::a.shards]
    continuations=[] if a.profile else continuations[a.shard::a.shards]
    old={};old_calls=list(a.prior_calls)
    for d in a.old_runs:
        assert (d/'runtime.json').exists();old_calls.append(d/'model_calls.jsonl')
        for line in (d/'episodes.jsonl').open():
            r=json.loads(line)
            if r['mode']=='goal_item' and r['upstream_rule']==r['exec_rule']:
                old[(r['case_id'],r['seed'],r['persona'],r['upstream_rule'])]=r
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'experiment':'E69','model':str(a.model),'shard':a.shard,'shards':a.shards,'profile':a.profile,
        'paired_worlds':[r['case']['case_id'] for r in pairs],
        'continuation_worlds':[r['case']['case_id'] for r in continuations],
        'paired_seeds':[6901,6902,6903],'continuation_seeds':[6801,6802,6803],
        'personas':policy.TRAITS,'max_steps':8,'task_stop':False,'world_modified':False,'cloud_calls':0,
        'driver_sha256':sha(Path(__file__)),'dataset_sha256':{n:sha(a.data/(n+'.jsonl')) for n in ['paired_tasks','continuation_tasks']},
        'old_runs':list(map(str,a.old_runs)),'prior_calls':list(map(str,a.prior_calls))}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    modules=policy.load_event_modules(policy.CACHE/'sources/LIGHT');client=SharedPrefixClient(a.model,a.out,6901)
    preload_start=time.monotonic()
    for path in old_calls:
        for line in path.open():
            r=json.loads(line);client.cache.setdefault(decision_key(r),r['parsed'])
    client.inner.load_seconds += time.monotonic()-preload_start
    start=time.monotonic();count=0
    for panel,rows in [('continuation',continuations),('matched',pairs)]:
        for group in [rows[:1]]+[rows[i:i+6] for i in range(1,len(rows),6)]:
            bases=[]
            for row in group:
                for task in (['source'] if panel=='continuation' else ['equip','duty_give']):
                    c=copy.deepcopy(row['case']);req=row['requests']['goal_item']
                    c.update(request_text=req['request_text'],request_command=req['command'],request_item_id=req['item_id'])
                    if panel=='matched':
                        c['goal_command']=row['tasks'][task];c['goal_kind']=c['goal_command'].split()[0]
                        c['quest']['goal']=c['goal_command'];c['original_recipient']=row['duty_recipient_id'] if task=='duty_give' else None
                    for seed in ([6801,6802,6803] if panel=='continuation' else [6901,6902,6903]):
                        for persona in ['firm','agreeable']:
                            for rule in (['generic_priority','negative_only'] if panel=='continuation' else ['generic_priority']):
                                b={'panel':panel,'task_condition':task,'case':c,'seed':seed,'persona':persona,'rule':rule,
                                   'source_goal_kind':row['case']['goal_kind'],'source_split':row.get('split','reserve'),
                                   'sampling_seed':seed+int(c['case_id'][:7],16)*10}
                                if panel=='continuation':
                                    prior=old[(c['case_id'],seed,persona,rule)]
                                    b.update(conversation=prior['conversation'],update=prior['update'])
                                bases.append(b)
            count+=run_group(bases,client,modules,a.out,old)
            print(json.dumps({'panel':panel,'episodes':count,'calls':client.inner.calls,'reused':client.reused,
                              'wall_seconds':time.monotonic()-start}),flush=True)
    assert count==12*(len(pairs)+len(continuations))
    runtime={'episodes':count,'calls':client.inner.calls,'reused_calls':client.reused,
             'wall_seconds':time.monotonic()-start,'model_load_seconds':client.inner.load_seconds,'cloud_calls':0}
    (a.out/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n');print(json.dumps(runtime),flush=True)


if __name__=='__main__':main()
