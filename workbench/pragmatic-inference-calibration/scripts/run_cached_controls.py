#!/usr/bin/env python3
"""E68 controls only, exact E67 source text and existing E28 native rendering."""
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from run_canonical_stage import fixed_controls
from run_native_readout import next_logits


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--model',choices=['Qwen3-8B','Qwen3-14B'],required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists();a.output.mkdir()
    start=time.monotonic();path=a.root/'models'/a.model
    marker=json.loads((path/'DOWNLOAD_COMPLETE.json').read_text())
    tok=AutoTokenizer.from_pretrained(path,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    labels=[tok.encode(t,add_special_tokens=False) for t in ['1','2']]
    assert all(len(x)==1 for x in labels);labels=[x[0] for x in labels]
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.set_num_threads(4)
    model=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,torch_dtype=torch.float32,
                                            device_map={'':0},weights_only=True,attn_implementation='eager').eval()
    rows=fixed_controls(a.root);records=[];gates=[];inputs={}
    @torch.inference_mode()
    def read(xs):
        inp=tok.pad({'input_ids':xs,'attention_mask':[[1]*len(x) for x in xs]},padding=True,return_tensors='pt').to(model.device)
        z=next_logits(model,inp);t=z[:,labels]
        return [dict(label_probs=p,support_mass=m,global_top_token_id=top) for p,m,top in
                zip(t.softmax(-1).cpu().tolist(),(t.logsumexp(-1)-z.logsumexp(-1)).exp().cpu().tolist(),z.argmax(-1).cpu().tolist())]
    for c in ['parent','format']:
        text=[tok.apply_chat_template([{'role':'system','content':r['system_prompt']},
              {'role':'user','content':r['prompt']+('\nReply with only 1 or 2.' if c=='format' else '')}],
              tokenize=False,add_generation_prompt=True,enable_thinking=False) for r in rows]
        xs=[tok.encode(t,add_special_tokens=False) for t in text]
        inputs[c]=hashlib.sha256(json.dumps(xs).encode()).hexdigest()
        batch=read(xs[:8]);error=max(abs(x-y) for j in [0,7] for x,y in zip(batch[j]['label_probs'],read([xs[j]])[0]['label_probs']))
        gates.append(dict(condition=c,batch_error=error,passed=error<.001));assert error<.001
        for offset in range(0,len(rows),8):
            for r,t,v in zip(rows[offset:offset+8],text[offset:offset+8],read(xs[offset:offset+8])):
                rec={k:x for k,x in r.items() if k not in ['prompt','system_prompt']}
                rec.update(v,condition=c,p_true=v['label_probs'][int(r['true_label'])-1],prompt_sha256=hashlib.sha256(t.encode()).hexdigest())
                records.append(rec)
    raw=a.output/'predictions.jsonl';raw.write_text(''.join(json.dumps(r)+'\n' for r in records))
    summary={}
    for c in ['parent','format']:
        rr=[r for r in records if r['condition']==c]
        pairs={(r['item_id'],r['state'],r['true_label']):r for r in rr}
        difference=[abs(pairs[i,s,'1']['p_true']-pairs[i,s,'2']['p_true']) for i,s,o in pairs if o=='1']
        accuracy=float(np.mean([(r['p_true']>.5)==r['expected_true'] for r in rr]))
        mass=float(np.mean([r['support_mass'] for r in rr]));median=float(np.median(difference))
        summary[c]=dict(n=len(rr),accuracy=accuracy,mean_mass=mass,median_order_difference=median,
                        gate_pass=accuracy>=.9 and mass>=.8 and median<=.15)
    cfg=dict(model=marker['model'],revision=marker['revision'],complete=True,wall_seconds=time.monotonic()-start,
             source_control_sha256=sha(Path(__file__).with_name('run_canonical_stage.py')),script_sha256=sha(Path(__file__)),
             input_token_hashes=inputs,raw_sha256=sha(raw),numerical_control=gates,summary=summary)
    (a.output/'config.json').write_text(json.dumps(cfg,indent=2))
    print(json.dumps(cfg),flush=True)


if __name__=='__main__':main()
