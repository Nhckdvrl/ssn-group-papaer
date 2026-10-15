#!/usr/bin/env python3
"""E73 fixed dialogue/native menu with genuine initial-state parser information."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from native_rule_execution import configure,SharedPrefixClient,policy
from native_matched_task_execution import decision_key
from light_native_gate import parse_event
from light_npc_episodes import material_state
import native_request_precondition_execution as base
import native_candidate_feedback_execution as proposal

CONDITIONS={d+'_initial_feedback':('equipped',d,'none','direct') for d in ['aligned','divert']}
FEEDBACK={}


def spec(g,stage,modules,graph=None,history=None):
    messages,schema=proposal.spec(g,stage,modules,graph,history)
    if stage=='exec':
        messages[-1]['content']+='\nNative mechanics check of the INITIAL state, before your current actions: '+FEEDBACK[g['case']['case_id']]
    return messages,schema


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',type=Path);ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--prior-runs',type=Path,nargs='*',default=[])
    ap.add_argument('--cpu-check',action='store_true');args=ap.parse_args()
    configure();base.CONDITIONS=CONDITIONS;base.spec=spec
    rows=list(map(json.loads,args.data.open()));assert len(rows)==117
    modules=policy.load_event_modules(policy.CACHE/'sources/LIGHT');witnesses=[]
    for row in rows:
        c=row['case'];g=modules[0].from_json(row['states']['equipped']);a=g.get_node(c['actor_id']);before=material_state(g)
        ev=parse_event(g,a,c['goal_command'],*modules[1:]);assert isinstance(ev,modules[2])
        text=ev.view_as(a);assert 'remove' in text.lower();FEEDBACK[c['case_id']]=text
        for d in ['aligned','divert']:
            other=parse_event(g,a,row['requests'][d]['request_command'],*modules[1:])
            assert isinstance(other,modules[2]) and other.view_as(a)==text
        assert before==material_state(g)
        witnesses.append({'case_id':c['case_id'],'native_feedback':text,'A_B_feedback_identical':True})
    if args.cpu_check:
        checks=0
        for g in base.bases_for(rows):
            g['conversation']={'reply':'I will consider the request.','stance':'negotiate'}
            graph=modules[0].from_json(g['case']['quest']['graph'])
            new,sn=spec(g,'exec',modules,graph,[]);old,so=proposal.spec(g,'exec',modules,graph,[])
            assert sn==so and new[0]==old[0]
            assert new[-1]['content']==old[-1]['content']+'\nNative mechanics check of the INITIAL state, before your current actions: '+FEEDBACK[g['case']['case_id']]
            checks+=1
        result={'status':'PASS','worlds':117,'paired_input_checks':checks,'native_feedback_witnesses':witnesses,'model_calls':0}
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print({'checks':checks,'witnesses':len(witnesses)});return
    assert args.model and args.prior_runs;cached={}
    for folder in args.prior_runs:
        assert (folder/'runtime.json').exists()
        assert json.loads((folder/'manifest.json').read_text())['model']==str(args.model)
        for call in map(json.loads,(folder/'model_calls.jsonl').open()):
            if call['stage']=='conv':cached.setdefault(decision_key(call),call['parsed'])
    for g in base.bases_for(rows):
        job=policy.base.job(g['case'],g['persona'],'conv',spec(g,'conv',modules),g['sampling_seed'])
        assert decision_key(job) in cached
    args.out.mkdir(parents=True,exist_ok=False)
    manifest={'experiment':'E73','model':str(args.model),'worlds':117,'conditions':CONDITIONS,
              'data_sha256':hashlib.sha256(args.data.read_bytes()).hexdigest(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'proposal_renderer_sha256':hashlib.sha256(Path(proposal.__file__).read_bytes()).hexdigest(),
              'feedback_sha256':hashlib.sha256(json.dumps(FEEDBACK,sort_keys=True).encode()).hexdigest(),
              'exact_dialogue_preflight_passed':True,'prior_runs':list(map(str,args.prior_runs)),
              'new_cloud_calls':0,'rules_modified':False,'scripted_agent_actions':0}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    client=SharedPrefixClient(args.model,args.out,7001);client.cache.update(cached);start=time.monotonic();count=0
    for group in [rows[:1]]+[rows[i:i+8] for i in range(1,len(rows),8)]:
        count+=base.run_group(group,client,modules,args.out)
        print(json.dumps({'episodes':count,'calls':client.inner.calls,'reused':client.reused,'wall_seconds':time.monotonic()-start}),flush=True)
    assert count==1404
    assert all(c['stage']=='exec' for c in map(json.loads,(args.out/'model_calls.jsonl').open()))
    runtime={'episodes':count,'calls':client.inner.calls,'reused_calls':client.reused,
             'wall_seconds':time.monotonic()-start,'model_load_seconds':client.inner.load_seconds,'new_cloud_calls':0}
    (args.out/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n');print(json.dumps(runtime),flush=True)


if __name__=='__main__':main()
