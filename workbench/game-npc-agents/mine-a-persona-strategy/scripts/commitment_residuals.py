#!/usr/bin/env python3
"""E50 matched-context stage residuals; no generation or causal claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

from commitment_decisions_v2 import PERSONAS, conv_spec, update_spec, exec_spec
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--split',default='pilot')
    ap.add_argument('--limit',type=int,default=40)
    ap.add_argument('--readout',choices=['native','common'],default='native')
    a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM,AutoModelForImageTextToText
    torch.set_num_threads(1)
    config=json.loads((a.model/'config.json').read_text())
    loader=AutoModelForImageTextToText if config['model_type'] in ('qwen3_5','gemma3') else AutoModelForCausalLM
    start=time.monotonic()
    model=loader.from_pretrained(str(a.model),dtype=torch.bfloat16,device_map={'':'cuda:0'},
                                local_files_only=True,attn_implementation='sdpa').eval()
    tokenizer=AutoTokenizer.from_pretrained(str(a.model),local_files_only=True)
    if config['model_type']=='qwen3_5': decoder=model.model.language_model
    elif config['model_type']=='gemma3': decoder=model.language_model.model
    else: decoder=model.model
    layers=decoder.layers
    load_seconds=time.monotonic()-start
    modules=load_event_modules(CACHE/'sources/LIGHT')
    rows=[json.loads(x) for x in a.dataset.read_text().splitlines()]
    rows=[r for r in rows if r['split']==a.split][:a.limit]
    tensors=[];metadata=[];hidden={}
    def hook(index):
        def capture(module,inputs,output):
            h=output[0] if isinstance(output,tuple) else output
            hidden[index]=h[0,-1].detach().float().cpu()
        return capture
    handles=[layer.register_forward_hook(hook(i)) for i,layer in enumerate(layers)]
    start=time.monotonic()
    for row in rows:
        # Fixed social acceptance and conflicting intents are identical under P/P'.
        # This avoids subtracting two different generated conversations or plans.
        u={'reply':'Yes, I can give that item to you.','stance':'accept'}
        update={'priority_actions':[row['goal_command']],
                'intention_memory':f"I agreed to {row['request_command']}.",'reason':'Fixed conflict context.'}
        for stage in ('conv','update','exec'):
            for p in PERSONAS:
                if stage=='conv':messages,sch=conv_spec(row,p,modules)
                elif stage=='update':messages,sch=update_spec(row,p,u,modules)
                else:
                    graph=modules[0].from_json(row['quest']['graph'])
                    messages,sch=exec_spec(row,p,update,'11',graph,[],modules)
                if a.readout=='common':
                    graph=modules[0].from_json(row['quest']['graph'])
                    from light_npc_episodes import legal_commands
                    menu=legal_commands(graph,graph.get_node(row['actor_id']))
                    messages=[dict(m) for m in messages]
                    messages[-1]['content']+='\nFor a separate diagnostic check, report the concrete legal action you intend next. Do not execute it. Output only an action JSON.\n'+'\n'.join(menu)
                    sch={'type':'object','properties':{'action':{'type':'string','enum':menu}},
                         'required':['action'],'additionalProperties':False}
                messages=[dict(m) for m in messages]
                messages[0]['content']+='\nReturn only JSON matching this schema: '+json.dumps(sch)
                text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,
                                                   enable_thinking=False)
                # Two positions: input boundary and standardized generation prefix.
                prefix={'conv':'{"reply":"','update':'{"priority_actions":["','exec':'{"action":"'}[stage]
                if a.readout=='common':prefix='{"action":"'
                for location,tail in [('input_boundary',''),('generation_prefix',prefix)]:
                    prompt=text+tail
                    ids=tokenizer(prompt,return_tensors='pt',add_special_tokens=False).to('cuda:0')
                    hidden.clear()
                    with torch.inference_mode(): decoder(**ids,use_cache=False)
                    assert len(hidden)==len(layers)
                    tensors.append(torch.stack([hidden[i] for i in range(len(layers))]))
                    metadata.append({'case_id':row['case_id'],'graph_sha256':row['graph_sha256'],
                      'goal_kind':row['goal_kind'],'stage':stage,'persona':p,'location':location,
                      'input_tokens':ids.input_ids.shape[-1],
                      'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                      'messages':messages,'forced_prefix':tail})
        if len(metadata)%120==0:
            print(json.dumps({'graphs':len(metadata)//12,'forward_calls':len(metadata),
                              'wall_seconds':time.monotonic()-start}),flush=True)
    for h in handles:h.remove()
    tensor=torch.stack(tensors)
    torch.save(tensor,a.out/'residuals.pt')
    (a.out/'prompts.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in metadata)+'\n')
    manifest={'model':str(a.model),'load_seconds':load_seconds,'forward_seconds':time.monotonic()-start,
      'graphs':len(rows),'forward_calls':len(metadata),'shape':list(tensor.shape),
      'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'personas':PERSONAS,'fixed_conversation':u,'cloud_calls':0,'generation_calls':0,
      'readout':a.readout,
      'claim_scope':'matched-context representational contrast; requires causal intervention for mechanism'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest),flush=True)


if __name__=='__main__':main()
