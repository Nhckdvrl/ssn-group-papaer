#!/usr/bin/env python3
"""E75: original retrieval tasks, coherent persona and symmetric path support."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import time

from native_rule_execution import configure, SharedPrefixClient, policy
from native_matched_task_execution import decision_key
from light_native_gate import parse_event
from light_npc_episodes import ViewerHost, execute, chosen_command
import native_request_precondition_execution as prior
from native_owned_container_qualification import event_id

SEEDS = [7501, 7502, 7503]
CONDITIONS = {state+'_'+support:(state,support) for state in ['ready','retrieval']
              for support in ['baseline','paths']}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bases_for(rows):
    result = []
    for row in rows:
        for condition,(state,support) in CONDITIONS.items():
            case = copy.deepcopy(row['case']); case['quest']['graph'] = row['states'][state]
            case['request_item_id'] = case['item_id']
            for seed in SEEDS:
                for persona in ['firm','agreeable']:
                    prefix = [] if state == 'ready' else [row['retrieve_command']]
                    paths = [prefix+[case['goal_command']],prefix+[case['request_command']]]
                    if random.Random(seed+int(case['case_id'][:7],16)).randrange(2):
                        paths.reverse()
                    result.append({'case':case,'state':state,'support':support,'condition':condition,
                        'seed':seed,'persona':persona,'sampling_seed':seed+int(case['case_id'][:7],16)*10,
                        'control':'none','interface':'direct','retrieve_command':row['retrieve_command'],
                        'native_goal_identity':row['native_goal_identity'],'paths':paths,
                        'in_prior_E50_pool':row['in_prior_E50_pool']})
    return result


def spec(game, stage, modules, graph=None, history=None):
    messages,schema = prior.spec(game,stage,modules,graph,history)
    g = graph if graph is not None else modules[0].from_json(game['case']['quest']['graph'])
    item = g.get_node(game['case']['item_id']); parent = item.get_container()
    location = 'carried by you' if parent.node_id == game['case']['actor_id'] else 'in '+parent.get_prefix_view()
    messages[-1]['content'] += ('\nCurrent physical location of the selected task item '+item.get_prefix_view()
                               +': '+location+'. Equipped: '+str(bool(item.get_prop('equipped'))).lower()+'.')
    if stage == 'exec' and game['support'] == 'paths':
        messages[-1]['content'] += ('\nTwo hypothetical command sequences from this episode\'s INITIAL state '
            '(neither has been executed by this record): '+json.dumps(game['paths'],ensure_ascii=False)
            +'\nChoose your next actual command in the CURRENT world.')
    return messages,schema


def run_group(rows,client,modules,out):
    games = bases_for(rows)
    jobs = [policy.base.job(g['case'],g['persona'],'conv',spec(g,'conv',modules),g['sampling_seed'])
            | {'state':g['state'],'support':g['support']} for g in games]
    for g,response in zip(games,client.batch(jobs)):
        g.update(conversation=response,graph=modules[0].from_json(g['case']['quest']['graph']),
                 history=[],goal_executed=False,first_source_recipient=None,
                 protocol_error='invalid_conversation' if response is None else None,done=response is None)
    for step in range(8):
        active = [g for g in games if not g['done']]
        if not active:
            break
        jobs = [policy.base.job(g['case'],g['persona'],'exec',spec(g,'exec',modules,g['graph'],g['history']),
                               g['sampling_seed']+10+step,None,step)
                | {'state':g['state'],'support':g['support']} for g in active]
        for g,response in zip(active,client.batch(jobs)):
            if response is None:
                g['done'],g['protocol_error'] = True,'invalid_exec_json'
                continue
            c = g['case']; graph = g['graph']; actor = graph.get_node(c['actor_id'])
            command = chosen_command(response)
            parsed = parse_event(graph,actor,command,*modules[1:]); ident = event_id(parsed,modules)
            target_ids = list(ident[1]) if ident else []
            matches_goal = bool(ident and [ident[0],target_ids] == g['native_goal_identity'])
            random.seed(g['sampling_seed']+100+step)
            r = execute(ViewerHost(graph),actor,command,*modules[1:])
            success = r['legal'] and r.get('executed') and not r.get('stochastic_failure')
            source_give = bool(success and r['event_type']=='GiveObjectEvent' and target_ids[0]==c['item_id'])
            if success and matches_goal:
                g['goal_executed'] = True
            if source_give:
                g['first_source_recipient'] = target_ids[1]
                assert r['before'][c['item_id']]['container'] == c['actor_id']
                assert r['after'][c['item_id']]['container'] == target_ids[1]
            r.update(choice=response,step=step,target_node_ids=target_ids,
                     matches_bound_source_goal=matches_goal,source_item_give=source_give)
            g['history'].append(r)
            g['done'] = g['goal_executed'] or source_give or bool(actor.get_prop('dead'))
    with (out/'episodes.jsonl').open('a') as handle:
        for g in games:
            c = g['case']
            row = {k:v for k,v in g.items() if k not in ['case','graph','done','sampling_seed','control','interface']}
            row.update(case_id=c['case_id'],source_graph_sha256=c['graph_sha256'],
                       goal_kind=c['goal_kind'],goal_command=c['goal_command'],request_command=c['request_command'],
                       goal_item_id=c['item_id'],actor_id=c['actor_id'],requester_id=c['requester_id'],
                       goal_recipient_id=c['original_recipient'],steps=len(g['history']))
            handle.write(json.dumps(row,ensure_ascii=False)+'\n')
    return len(games)


def cpu_check(rows,modules):
    checked = 0
    games = bases_for(rows)
    for g in games:
        if g['support'] != 'baseline':
            continue
        g['conversation'] = {'reply':'I will consider the request.','stance':'negotiate'}
        graph = modules[0].from_json(g['case']['quest']['graph'])
        alternative = {**g,'support':'paths','condition':g['state']+'_paths'}
        assert spec(g,'conv',modules) == spec(alternative,'conv',modules)
        a,sa = spec(g,'exec',modules,graph,[]); b,sb = spec(alternative,'exec',modules,graph,[])
        assert sa == sb and a[0] == b[0]
        assert b[-1]['content'].startswith(a[-1]['content'])
        assert policy.TRAITS[g['persona']] in a[0]['content']
        assert g['case']['quest']['persona'] in a[0]['content']
        assert g['case']['goal_command'] in a[-1]['content']
        menu = policy.base.legal_commands(graph,graph.get_node(g['case']['actor_id']))
        if g['state']=='retrieval':
            assert g['retrieve_command'] in menu
            assert g['case']['goal_command'] not in menu and g['case']['request_command'] not in menu
        else:
            assert g['case']['goal_command'] in menu and g['case']['request_command'] in menu
        checked += 1
    return {'status':'PASS','worlds':len(rows),'paired_input_checks':checked,
            'planned_execution_branches_per_model':len(games),'model_calls':0}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--model',type=Path)
    ap.add_argument('--prior-runs',type=Path,nargs='*',default=[])
    ap.add_argument('--shard',type=int,default=0);ap.add_argument('--shards',type=int,default=1)
    ap.add_argument('--cpu-check',action='store_true');ap.add_argument('--profile',action='store_true')
    args=ap.parse_args();configure();assert os.environ.get('PYTHONHASHSEED')=='0'
    rows=list(map(json.loads,args.data.open()));assert len(rows)==102
    modules=policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    if args.cpu_check:
        r=cpu_check(rows,modules);r['script_sha256']=sha(Path(__file__));r['data_sha256']=sha(args.data)
        args.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));return
    assert args.model
    selected=rows[:1] if args.profile else rows[args.shard::args.shards]
    args.out.mkdir(parents=True,exist_ok=False)
    manifest={'experiment':'E75','model':str(args.model),'profile':args.profile,'shard':args.shard,'shards':args.shards,
        'case_ids':[r['case']['case_id'] for r in selected],'conditions':CONDITIONS,'seeds':SEEDS,
        'personas':policy.TRAITS,'script_sha256':sha(Path(__file__)),'data_sha256':sha(args.data),
        'prior_renderer_sha256':sha(Path(prior.__file__)),'max_actions':8,
        'termination':'Bound authored goal, first source-item Give, death, protocol failure or eight actions.',
        'rules_modified':False,'scripted_agent_actions':0,'new_cloud_calls':0}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    client=SharedPrefixClient(args.model,args.out,7501)
    for folder in args.prior_runs:
        assert (folder/'runtime.json').exists()
        assert json.loads((folder/'manifest.json').read_text())['model']==str(args.model)
        for r in map(json.loads,(folder/'model_calls.jsonl').open()):
            client.cache.setdefault(decision_key(r),r['parsed'])
    start=time.monotonic();count=0
    for chunk in [selected[:1]]+[selected[i:i+4] for i in range(1,len(selected),4)]:
        count+=run_group(chunk,client,modules,args.out)
        print(json.dumps({'episodes':count,'calls':client.inner.calls,'reused':client.reused,
                          'seconds':time.monotonic()-start}),flush=True)
    assert count==len(selected)*24
    r={'worlds':len(selected),'episodes':count,'calls':client.inner.calls,'reused_calls':client.reused,
       'wall_seconds':time.monotonic()-start,'model_load_seconds':client.inner.load_seconds,'new_cloud_calls':0}
    (args.out/'runtime.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)


if __name__=='__main__':main()
