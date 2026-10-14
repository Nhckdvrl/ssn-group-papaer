#!/usr/bin/env python3
"""E52: source-grounded object binding, token patch, full native action menu."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import time
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, execute, material_state, system_message

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--draws',type=int,default=32)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM,AutoModelForImageTextToText
    torch.set_num_threads(1)
    snap=json.loads((CACHE/'runs/e22_qwen35/snapshots.json').read_text())[0]
    assert snap['name']=='p14908_s2001_first1'
    contexts={k:snap['contexts'][k] for k in ['all_dialog','no_dialog','all_dialog_fact','all_dialog_binding']}
    assert contexts['all_dialog'].count('this worm for my hungry babies')==1
    contexts['corrected_self_speech']=contexts['all_dialog'].replace('this worm for my hungry babies','this nut for my hungry babies')
    tokenizer=AutoTokenizer.from_pretrained(str(a.model),local_files_only=True)
    extra=contexts['all_dialog_binding'][len(contexts['all_dialog']):]
    unrelated='\nReminder: I love flying high in the sky. '
    target_length=len(tokenizer(extra,add_special_tokens=False).input_ids)
    neutral_ids=tokenizer(unrelated*10,add_special_tokens=False).input_ids[:target_length]
    contexts['unrelated_reminder']=contexts['all_dialog']+tokenizer.decode(neutral_ids)
    sch=snap['original_action_schema']
    system=system_message(snap['quest'])+'\nChoose one game action using the choose_action tool. Return only its JSON arguments; reasoning must be one short sentence. Schema: '+json.dumps(sch)
    def render(context):
        messages=[{'role':'system','content':system},{'role':'user','content':context}]
        prompt=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
        return prompt+'{"action":',messages,prompt
    rendered={k:render(v) for k,v in contexts.items()}
    tokens={k:tokenizer(v[0],return_tensors='pt',add_special_tokens=False) for k,v in rendered.items()}
    target=tokens['all_dialog'].input_ids[0];donor=tokens['corrected_self_speech'].input_ids[0]
    assert target.shape==donor.shape
    changed=(target!=donor).nonzero().flatten().tolist();assert len(changed)==1,changed
    position=changed[0]
    trie={}
    for command in snap['menu']:
        node=trie
        for token in tokenizer(json.dumps(command,ensure_ascii=False),add_special_tokens=False).input_ids:
            node=node.setdefault(token,{})
        node[None]=True
    cfg=json.loads((a.model/'config.json').read_text())
    loader=AutoModelForImageTextToText if cfg['model_type']=='qwen3_5' else AutoModelForCausalLM
    t=time.monotonic()
    model=loader.from_pretrained(str(a.model),dtype=torch.bfloat16,device_map={'':'cuda:0'},
                                attn_implementation='sdpa',local_files_only=True).eval()
    layers=model.model.language_model.layers if cfg['model_type']=='qwen3_5' else model.model.layers
    assert len(layers)==64
    load_seconds=time.monotonic()-t
    captured={};last={}
    def capture(i):
        def fn(module,inputs,output):
            h=output[0] if isinstance(output,tuple) else output
            captured[i]=h[0,position].detach().clone()
            last[i]=h[0,-1].detach().float().cpu()
        return fn
    handles=[layer.register_forward_hook(capture(i)) for i,layer in enumerate(layers)]
    vectors={};tails={}
    for name in ['all_dialog','corrected_self_speech']:
        captured.clear();last.clear()
        with torch.inference_mode():model(**tokens[name].to('cuda:0'),use_cache=False,logits_to_keep=1)
        vectors[name]={i:h for i,h in captured.items()}
        tails[name]=torch.stack([last[i] for i in range(64)])
    for h in handles:h.remove()
    torch.save({'binding_token':{n:torch.stack([v[i].float().cpu() for i in range(64)]) for n,v in vectors.items()},
                'prompt_tail':tails},a.out/'residuals.pt')
    modules=load_event_modules(CACHE/'sources/LIGHT')
    conditions=[(k,k,None,None) for k in contexts]
    conditions += [(f'patch_correct_to_original_l{i}','all_dialog',i,'donor') for i in [0,15,31,47,63]]
    conditions += [('sham_l31','all_dialog',31,'sham'),('random_delta_l31','all_dialog',31,'random'),
                   ('patch_original_to_correct_l31','corrected_self_speech',31,'reverse')]
    manifest={'model':str(a.model),'source_snapshot':snap['name'],'independent_graphs':1,
              'draws':a.draws,'layers':[0,15,31,47,63],'changed_token_position':position,
              'target_token':tokenizer.decode([int(target[position])]),'donor_token':tokenizer.decode([int(donor[position])]),
              'conditions':[c[0] for c in conditions],'native_menu':snap['menu'],
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'cloud_calls':0,'generation':'full native command trie; JSON action field only, no reason selection',
              'contexts':contexts,'load_seconds':load_seconds,
              'original_base_prompt_hash_match':hashlib.sha256(rendered['all_dialog'][2].encode()).hexdigest()==snap['original_action_prompt_sha256']}
    (a.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    records=[];started=time.monotonic()
    for label,context,layer,kind in conditions:
        handle=None
        if layer is not None:
            v0=vectors['all_dialog'][layer];v1=vectors['corrected_self_speech'][layer]
            if kind=='random':
                generator=torch.Generator(device='cuda').manual_seed(520031)
                noise=torch.randn(v0.shape,device='cuda',generator=generator,dtype=torch.float32)
                delta=noise/noise.norm()*(v1.float()-v0.float()).norm()
            def patch(module,inputs,output):
                h=output[0] if isinstance(output,tuple) else output
                if h.shape[1]<=position:return output
                h=h.clone()
                if kind=='donor':h[0,position]=v1
                elif kind in ['sham','reverse']:h[0,position]=v0
                else:h[0,position]=(h[0,position].float()+delta).to(h.dtype)
                return (h,*output[1:]) if isinstance(output,tuple) else h
            handle=layers[layer].register_forward_hook(patch)
        input_args=tokens[context].to('cuda:0');prefix_length=input_args.input_ids.shape[1]
        def allowed(batch_index,ids):
            node=trie
            for token in ids[prefix_length:].tolist():node=node[token]
            return [tokenizer.eos_token_id] if None in node else list(node)
        for draw in range(a.draws):
            seed=520000+draw;torch.manual_seed(seed)
            t=time.monotonic()
            with torch.inference_mode():
                output=model.generate(**input_args,max_new_tokens=64,do_sample=True,temperature=.7,top_p=1.,top_k=0,
                    use_cache=True,prefix_allowed_tokens_fn=allowed,eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.eos_token_id)
            text=tokenizer.decode(output[0,prefix_length:],skip_special_tokens=True)
            command=json.loads(text);assert command in snap['menu']
            graph=modules[0].from_json(snap['graph']);assert material_state(graph)==snap['before']
            random.seed(seed)
            native=execute(ViewerHost(graph),graph.get_node(snap['actor_id']),command,*modules[1:])
            row={'condition':label,'draw':draw,'seed':seed,'command':command,'response_action_field':text,
                 'native':native,'seconds':time.monotonic()-t,'prompt_sha256':hashlib.sha256(rendered[context][0].encode()).hexdigest()}
            records.append(row)
            with (a.out/'calls.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
        if handle:handle.remove()
        print(json.dumps({'condition':label,'draws':a.draws,
                          'actions':dict(Counter(r['command'] for r in records if r['condition']==label)),
                          'seconds':time.monotonic()-started}),flush=True)
    table={label:dict(Counter(r['command'] for r in records if r['condition']==label)) for label,_,_,_ in conditions}
    paired={label:sum(r['command']!=records[r['draw']]['command'] for r in records if r['condition']==label) for label in table}
    runtime={'load_seconds':load_seconds,'wall_seconds':time.monotonic()-started,
             'generation_calls':len(records),'cloud_calls':0,'illegal_actions':sum(not r['native']['legal'] for r in records)}
    result={'manifest':manifest,'runtime':runtime,'actions':table,'paired_changed_from_baseline':paired,
            'sham_matches_baseline':paired['sham_l31']==0,'scope':'one native conflict snapshot; local causal diagnostic'}
    (a.out/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(runtime),flush=True)

if __name__=='__main__':main()
