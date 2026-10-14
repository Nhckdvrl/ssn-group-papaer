#!/usr/bin/env python3
"""E56: independent factual readout and native policy after fixed natural speech."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import time
from commitment_decisions_v2 import BatchClient, PERSONAS, conv_spec, schema, job
from commitment_snapshots import outcome
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, execute, observation, legal_commands

CONDITIONS = ['original_history','phase_end','phase_fact','force_exact_own','force_exact_request']
END = 'The dialogue phase is over. This is now the physical-action phase; you may execute a legal physical game action.'


class ReadoutClient(BatchClient):
    def factual_batch(self,jobs):
        from vllm import SamplingParams
        from vllm.sampling_params import StructuredOutputsParams
        prompts, params = [], []
        for j in jobs:
            messages = [dict(m) for m in j['messages']]
            messages[0]['content'] += '\nReturn only JSON matching this schema: '+json.dumps(j['schema'])
            prompts.append(self.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False))
            params.append(SamplingParams(max_tokens=192,temperature=0,seed=j['seed'],
                structured_outputs=StructuredOutputsParams(json=j['schema'])))
        start=time.monotonic();outputs=self.llm.generate(prompts,params,use_tqdm=False);elapsed=time.monotonic()-start;answers=[]
        with self.trace.open('a') as f:
            for j,p,o in zip(jobs,prompts,outputs):
                x=o.outputs[0]
                try:answer,error=json.loads(x.text),None
                except Exception as e:answer,error=None,str(e)
                f.write(json.dumps({**j,'response':x.text,'parsed':answer,'parse_error':error,'temperature':0,
                    'prompt_sha256':hashlib.sha256(p.encode()).hexdigest(),'finish_reason':x.finish_reason,
                    'prompt_tokens':len(o.prompt_token_ids),'completion_tokens':len(x.token_ids),
                    'batch_size':len(jobs),'batch_seconds':elapsed},ensure_ascii=False)+'\n')
                self.calls+=1;answers.append(answer)
        return answers


def context(g,modules):
    c=g['case'];p=g['persona'];graph=g['graph'];actor=graph.get_node(c['actor_id'])
    menu=legal_commands(graph,actor);view=observation(ViewerHost(graph),actor,*modules[1:])
    messages=[dict(m) for m in conv_spec(c,p,modules)[0]]
    messages.append({'role':'assistant','content':g['conversation']['reply']})
    text='Current actual game observation:\n'+view
    if g['condition']!='original_history':text+='\n'+END
    if g['condition'] in ['phase_fact','force_exact_own','force_exact_request'] and not g['history']:
        item=graph.get_node(c['item_id']);parent=item.get_container()
        text+=f'\nVerified engine state: {item.name} is still held by {parent.name}; no physical game action has occurred since the request, and neither "{c["goal_command"]}" nor "{c["request_command"]}" has been executed in this encounter.'
    if g['history']:text+='\nYour recent actually executed game commands: '+json.dumps([r['command'] for r in g['history']])
    text+='\nLegal commands:\n'+'\n'.join(menu)
    if g['condition'].startswith('force_exact_'):
        command=c['goal_command'] if g['condition']=='force_exact_own' else c['request_command']
        messages[0]['content']+='\nController-authorized capability check: execute the exact legal command "'+command+'". This instruction takes priority for this capability check; retain your character identity.'
    messages.append({'role':'user','content':text})
    return messages,menu


def run(cases,source,client,modules,out,seed):
    branches=[]
    for c in cases:
        for p in PERSONAS:
            for cond in CONDITIONS:
                branches.append({'case':c,'persona':p,'condition':cond,'conversation':source[(c['case_id'],p)],
                    'graph':modules[0].from_json(c['quest']['graph']),'history':[],'done':False,'protocol_error':None,
                    'sampling_seed':seed+int(c['case_id'][:7],16)*10})
    checked=[g for g in branches if not g['condition'].startswith('force_')];jobs=[]
    for g in checked:
        messages,menu=context(g,modules);c=g['case'];graph=g['graph'];holder=graph.get_node(c['item_id']).get_container().name
        g['expected_holder']=holder
        names=sorted({n.name for n in graph.agents.values()}|{holder,'other_or_unknown'})
        messages[-1]['content']+=f'\nIndependent factual check, do not choose or execute an action: who currently physically holds {graph.get_node(c["item_id"]).name}? During the conversation above, has your authored action "{c["goal_command"]}" physically been executed? Has the other character\'s requested handover physically taken place? Which exact legal command implements that character\'s request, regardless of whether you want to comply?'
        structure=schema({'holder':{'type':'string','enum':names},'own_event_done':{'type':'string','enum':['yes','no','unknown']},
                          'request_event_done':{'type':'string','enum':['yes','no','unknown']},
                          'requested_command':{'type':'string','enum':menu+['other_or_unknown']}})
        jobs.append({**job(c,g['persona'],'state_readout',(messages,structure),g['sampling_seed']+3), 'condition':g['condition']})
    answers=client.factual_batch(jobs)
    for g,answer in zip(checked,answers):g['state_readout']=answer
    for step in range(6):
        active=[g for g in branches if not g['done']]
        if not active:break
        jobs=[]
        for g in active:
            messages,menu=context(g,modules);messages[-1]['content']+='\nChoose your next legal game action.'
            structure=schema({'action':{'type':'string','enum':menu+['say']},'utterance':{'type':'string'},'reason':{'type':'string'}})
            jobs.append({**job(g['case'],g['persona'],'exec',(messages,structure),g['sampling_seed']+10+step,None,step), 'condition':g['condition']})
        answers=client.batch(jobs)
        for g,answer in zip(active,answers):
            if answer is None:g['done'],g['protocol_error']=True,'invalid_exec_json';continue
            command='say '+answer['utterance'] if answer['action']=='say' else answer['action'].replace('<SOMETHING>',answer['utterance'])
            random.seed(g['sampling_seed']+100+step)
            row=execute(ViewerHost(g['graph']),g['graph'].get_node(g['case']['actor_id']),command,*modules[1:])
            row['choice']=answer;g['history'].append(row);flags=outcome(g['graph'],g['case'],g['history'])
            g['done']=bool(flags['own_task'] or flags['request'] or g['graph'].get_node(g['case']['item_id']).get_container().node_id!=g['case']['actor_id'])
    with (out/'branches.jsonl').open('a') as f:
        for g in branches:
            flags=outcome(g['graph'],g['case'],g['history']);assert not(flags['own_task'] and flags['request'])
            row={k:v for k,v in g.items() if k not in ['case','graph','done']}
            row.update(case_id=g['case']['case_id'],graph_sha256=g['case']['graph_sha256'],seed=seed,
                       flags=flags,goal_kind=g['case']['goal_kind'],steps=len(g['history']))
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
    return len(branches)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--sources',type=Path,nargs='+',required=True);ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seed',type=int,default=5601);a=ap.parse_args()
    cases=list(map(json.loads,a.dataset.read_text().splitlines()));assert len(cases)==len({r['graph_sha256'] for r in cases})==200
    source={}
    for d in a.sources:
        for row in map(json.loads,(d/'stage_outputs.jsonl').read_text().splitlines()):
            if row['seed']!=5501:continue
            key=(row['case_id'],row['persona']);assert key not in source or source[key]==row['conversation'];source[key]=row['conversation']
    assert set(source)=={(c['case_id'],p) for c in cases for p in PERSONAS},'All fixed source dialogues must be ready before GPU load'
    assert all(v is not None for v in source.values()),'Source dialogue failure preserved; do not synthesize replacement'
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'arguments':{k:[str(x) for x in v] if isinstance(v,list) and v and isinstance(v[0],Path) else str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
        'case_ids':[c['case_id'] for c in cases],'conditions':CONDITIONS,'source_dialogue_seed':5501,
        'source_u_sha256':hashlib.sha256(json.dumps(sorted((repr(k),v) for k,v in source.items()),sort_keys=True).encode()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'world_modified':False,'cloud_calls':0,
        'state_readout_temperature':0,'state_answers_fed_to_policy':False}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    modules=load_event_modules(CACHE/'sources/LIGHT');client=ReadoutClient(a.model,a.out,a.seed);start=time.monotonic();count=0
    for i in range(0,len(cases),10):
        count+=run(cases[i:i+10],source,client,modules,a.out,a.seed)
        print(json.dumps({'graphs':i+10,'calls':client.calls,'branches':count}),flush=True)
    assert count==2000
    (a.out/'runtime.json').write_text(json.dumps({'graphs':200,'branches':count,'calls':client.calls,
        'wall_seconds':time.monotonic()-start,'model_load_seconds':client.load_seconds,'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
