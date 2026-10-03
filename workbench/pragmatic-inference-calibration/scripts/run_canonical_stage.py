#!/usr/bin/env python3
"""E67: canonical two conditions only, with fixed explicit stance controls."""
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from run_implicaturex import prepare
from run_native_readout import next_logits
from dense_stage_data import specs


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fixed_controls(root):
    audit=[json.loads(s) for s in (root/'data/E66-canonical-human-audit/items.jsonl').read_text().splitlines()]
    rng=np.random.default_rng(20261003)
    controls=[]
    for ph in sorted({r['phenomenon'] for r in audit}):
        rs=sorted([r for r in audit if r['phenomenon']==ph],key=lambda x:x['item_id'])
        for j in sorted(rng.choice(len(rs),8,replace=False)):
            r=rs[j]
            for affirm in [True,False]:
                stance='affirms' if affirm else 'rejects'
                for order in ['1','2']:
                    options='1: True\n2: False' if order=='1' else '1: False\n2: True'
                    prompt=('You will read an explicit statement about a claim. Decide whether the interpretation '
                            'of the statement is true or false. Pick its corresponding number.\n\nClaim: '+r['q']+
                            '\nStatement: The speaker explicitly '+stance+' this claim.'+
                            '\n\nInterpretation: The speaker affirms the claim.\n\nIs this interpretation true or false?\n\n'+
                            options+'\n\nAnswer: ')
                    controls.append(dict(item_id=r['item_id'],phenomenon=ph,state='affirm' if affirm else 'deny',
                                         true_label=order,false_label='2' if order=='1' else '1',
                                         prompt=prompt,system_prompt='You are an expert in pragmatic inference and in identifying the intended meaning of utterances.',
                                         kind='control',expected_true=affirm))
    assert len(controls)==128
    return controls


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--stage',choices=['SFT','DPO'],required=True)
    ap.add_argument('--shard',type=int,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    assert 0<=a.shard<4 and not a.output.exists()
    start=time.monotonic()
    a.output.mkdir(parents=True)
    m=next(x for x in specs(a.root) if x['stage']==a.stage)
    model_path=a.root/'models'/m['id'].split('/')[-1]
    common=a.root/'models/OLMo-2-1124-13B-SFT'
    marker=json.loads((model_path/'DOWNLOAD_COMPLETE.json').read_text())
    assert marker['model']==m['id'] and marker['revision']==m['sha']
    tok=AutoTokenizer.from_pretrained(common,local_files_only=True,padding_side='left')
    native=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
    assert tok.backend_tokenizer.to_str()==native.backend_tokenizer.to_str()
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    rows,audit=prepare(a.root)
    rows=[dict(r,kind='natural') for r in rows if r['state'] in ['baseline','cancel']]
    assert len(rows)==1084
    selected=set(sorted({r['item_id'] for r in rows})[a.shard::4])
    rows=[r for r in rows+fixed_controls(a.root) if r['item_id'] in selected]
    label_ids=[tok.encode(s,add_special_tokens=False) for s in ['1','2']]
    assert all(len(x)==1 for x in label_ids)
    label_ids=[x[0] for x in label_ids]
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.set_num_threads(4)
    model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,torch_dtype=torch.float32,
                                            device_map={'':0},attn_implementation='eager',weights_only=True).eval()
    def render(r,c):
        p=r['prompt']+('\nReply with only 1 or 2.' if c=='format' else '')
        return tok.apply_chat_template([{'role':'system','content':r['system_prompt']},{'role':'user','content':p}],
                                      tokenize=False,add_generation_prompt=True)
    @torch.inference_mode()
    def read(sequences):
        inp=tok.pad({'input_ids':sequences,'attention_mask':[[1]*len(x) for x in sequences]},padding=True,return_tensors='pt').to(model.device)
        logits=next_logits(model,inp)
        target=logits[:,label_ids]
        return [dict(label_probs=p,support_mass=mass,global_top_token_id=top,support_argmax_present=top in label_ids)
                for p,mass,top in zip(target.softmax(-1).cpu().tolist(),
                    (target.logsumexp(-1)-logits.logsumexp(-1)).exp().cpu().tolist(),logits.argmax(-1).cpu().tolist())]
    config=dict(model=m['id'],revision=m['sha'],stage=a.stage,shard=a.shard,n_shards=4,items=sorted(selected),
                n_rows=len(rows)*2,complete=False,dtype='float32',batch_size=8,attention='eager',tf32=False,
                source_audit=audit,common_tokenizer=str(common),script_sha256=sha(Path(__file__)),
                dependency_sha256={s:sha(Path(__file__).with_name(s)) for s in ['run_implicaturex.py','run_native_readout.py','dense_stage_data.py']},
                input_token_hashes={})
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    gates=[]
    with (a.output/'predictions.jsonl').open('w') as f:
        for c in ['parent','format']:
            text=[render(r,c) for r in rows]
            sequences=[tok.encode(t,add_special_tokens=False) for t in text]
            assert max(map(len,sequences))<4096
            config['input_token_hashes'][c]=hashlib.sha256(json.dumps(sequences).encode()).hexdigest()
            probe=sequences[:7]+sequences[-1:]
            many=read(probe)
            error=max(abs(x-y) for j in [0,7] for x,y in zip(read([probe[j]])[0]['label_probs'],many[j]['label_probs']))
            gates.append(dict(condition=c,first_last_batch_prob_delta=error,pass_gate=error<.001))
            (a.output/'numerical-control.json').write_text(json.dumps(gates,indent=2))
            assert error<.001,'Numerical padding gate failed'
            for offset in range(0,len(rows),8):
                result=read(sequences[offset:offset+8])
                for r,t,v in zip(rows[offset:offset+8],text[offset:offset+8],result):
                    rec={k:v for k,v in r.items() if k not in ['prompt','system_prompt']}
                    rec.update(v,condition=c,p_true=v['label_probs'][int(r['true_label'])-1],prompt_sha256=hashlib.sha256(t.encode()).hexdigest())
                    f.write(json.dumps(rec)+'\n')
                f.flush()
            print(json.dumps(dict(stage=a.stage,shard=a.shard,condition=c,n=len(rows))),flush=True)
    config.update(complete=True,numerical_gate_pass=True,wall_seconds=time.monotonic()-start,
                  output_sha256=sha(a.output/'predictions.jsonl'))
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    print(json.dumps(dict(done=a.stage,shard=a.shard,seconds=config['wall_seconds'])),flush=True)


if __name__=='__main__':
    main()
