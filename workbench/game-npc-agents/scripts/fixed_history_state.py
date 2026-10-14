#!/usr/bin/env python3
"""E59: coherent persona, identical future statement and zero native transfers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from commitment_decisions_v2 import PERSONAS, update_spec, schema, job
from native_state_readout import ReadoutClient
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE
from native_persona_components import GROUNDING


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seed',type=int,default=5801);a=ap.parse_args()
    cases=list(map(json.loads,a.dataset.read_text().splitlines()));assert len(cases)==len({c['graph_sha256'] for c in cases})==200
    assert (a.source/'runtime.json').exists(),'Freeze the complete E58 natural comparison before this run'
    natural={}
    for row in map(json.loads,(a.source/'stage_outputs.jsonl').read_text().splitlines()):
        if row['persona'].startswith('full_'):
            key=(row['case_id'],row['persona'].removeprefix('full_'));assert key not in natural;natural[key]=row
    assert set(natural)=={(c['case_id'],p) for c in cases for p in PERSONAS}
    source_manifest=json.loads((a.source/'manifest.json').read_text())
    assert source_manifest['arguments']['model']==str(a.model)
    assert source_manifest['dataset_sha256']==hashlib.sha256(a.dataset.read_bytes()).hexdigest()
    assert all(source_manifest['personas']['full_'+p]==v for p,v in PERSONAS.items())
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'arguments':{k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
        'case_ids':[c['case_id'] for c in cases],'personas':dict(PERSONAS),
        'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'natural_source_sha256':hashlib.sha256((a.source/'stage_outputs.jsonl').read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'grounding':GROUNDING,'world_modified':False,'physical_actions_before_writer':0,
        'fixed_history_has_persona_description':False,'factual_answers_fed_to_writer':False,
        'cloud_calls':0,'conditions':['natural_frozen_E58','fixed_future']}
    (a.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (a.out/'natural_comparison.jsonl').write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for k,v in sorted(natural.items())))
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    modules=load_event_modules(CACHE/'sources/LIGHT');client=ReadoutClient(a.model,a.out,a.seed);start=time.monotonic();count=0
    for i in range(0,len(cases),10):
        jobs=[];slots=[];facts=[]
        for c in cases[i:i+10]:
            graph=modules[0].from_json(c['quest']['graph']);item=graph.get_node(c['item_id']);holder=item.get_container().name
            assert item.get_container().node_id==c['actor_id']
            future={'stance':'accept','reply':f'I will hand {item.name} to {c["requester_name"]} next.',
                    'reason':'Experimentally fixed neutral future statement, no physical action selected.'}
            for p in PERSONAS:
                seed=a.seed+int(c['case_id'][:7],16)*10
                messages,structure=update_spec(c,p,future,modules);messages[-1]['content']+='\n'+GROUNDING
                jobs.append(job(c,p,'fixed_history_update',(messages,structure),seed+1))
                fm=[dict(m) for m in messages]
                fm[-1]['content']+='\nIndependent factual question: who currently physically holds '+item.name+'? Has the specific physical game command "'+c['request_command']+'" been executed in this encounter? Do not select an action.'
                names=sorted({n.name for n in graph.agents.values()}|{holder,'other_or_unknown'})
                fact_structure=schema({'holder':{'type':'string','enum':names},
                                       'give_executed':{'type':'string','enum':['yes','no','unknown']}})
                facts.append(job(c,p,'fixed_history_factual',(fm,fact_structure),seed+3))
                slots.append({'case_id':c['case_id'],'graph_sha256':c['graph_sha256'],'persona':p,'seed':a.seed,
                              'fixed_conversation':future,'expected_holder':holder,'expected_give_executed':'no',
                              'request_command':c['request_command'],'goal_command':c['goal_command']})
        outputs=client.batch(jobs);answers=client.factual_batch(facts)
        with (a.out/'records.jsonl').open('a') as f:
            for row,output,answer in zip(slots,outputs,answers):
                f.write(json.dumps({**row,'update':output,'factual_readout':answer},ensure_ascii=False)+'\n');count+=1
        print(json.dumps({'graphs':i+10,'records':count,'calls':client.calls,'wall_seconds':time.monotonic()-start}),flush=True)
    assert count==400
    (a.out/'runtime.json').write_text(json.dumps({'graphs':200,'records':count,'calls':client.calls,
        'wall_seconds':time.monotonic()-start,'model_load_seconds':client.load_seconds,'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
