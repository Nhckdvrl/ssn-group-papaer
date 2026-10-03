"""E46 frozen original goals, four disjoint shards per matched checkpoint."""
import argparse,hashlib,json,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from commitment_qwen14_data import prepare,inputs,parse,common_model,selected,GROUPS

ap=argparse.ArgumentParser()
for k in ['root','model','output']:ap.add_argument('--'+k,type=Path,required=True)
for k in ['model-id','revision']:ap.add_argument('--'+k,required=True)
ap.add_argument('--group',choices=GROUPS,required=True);a=ap.parse_args();assert not a.output.exists()
allrows,audit=prepare(a.root);rows=selected(allrows,a.group)
pre=json.loads(Path('workbench/pragmatic-inference-calibration/results/E46-source-preflight.json').read_text())
assert pre['gate_pass'] and pre['audit']==audit
tok=AutoTokenizer.from_pretrained(common_model(a.root,a.model.name),local_files_only=True)
prepared={k:inputs(tok,rows,k,a.model.name) for k in ['bare','common-chat']}
assert all(v[2]==pre['models'][a.model.name]['groups'][a.group][k] for k,v in prepared.items())
a.output.mkdir(parents=True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
started=time.monotonic();eos=model.generation_config.eos_token_id;eos=[eos] if isinstance(eos,int) else eos or []
@torch.inference_mode()
def read(ids,row):
    z=model.generate(input_ids=torch.tensor([ids],device=model.device),attention_mask=torch.ones((1,len(ids)),dtype=torch.long,device=model.device),
        do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True,use_cache=True)
    generated=z.sequences[0,len(ids):].tolist();text=tok.decode(generated,skip_special_tokens=True);pred=parse(text,row)
    return {'raw_text':text,'generated_ids':generated,
        'generated_token_logprobs':[float(score[0].float().log_softmax(-1)[target]) for score,target in zip(z.scores,generated)],
        'prediction':pred,'invalid':pred is None,'terminated_by_eos':bool(generated and generated[-1] in eos),'n_output_tokens':len(generated)}
controls=[]
for interface,(_,ids,_) in prepared.items():
    for i in [0,len(rows)-1]:
        x,y=read(ids[i],rows[i]),read(ids[i],rows[i]);same=x['generated_ids']==y['generated_ids']
        delta=max([abs(u-v) for u,v in zip(x['generated_token_logprobs'],y['generated_token_logprobs'])] or [0])
        controls.append({'interface':interface,'id':rows[i]['id'],'same_generated_ids':same,'token_lp_delta':delta,'pass':same and delta<.001})
(a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert all(c['pass'] for c in controls)
sha=lambda name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
config={'task':'crossed_truth_commitment_original_experiment_2','group':a.group,'model':a.model_id,'revision':a.revision,
    'dtype':'float32','batch_size':1,'source_audit':audit,'input_token_hashes':{k:v[2] for k,v in prepared.items()},
    'full_input_token_hashes':pre['models'][a.model.name]['full'],'numerical_gate_pass':True,'do_sample':False,'max_new_tokens':16,
    'thinking':False,'n':2*len(rows),'common_tokenizer':str(common_model(a.root,a.model.name)),
    'script_sha256':sha('run_commitment_qwen14.py'),'helper_sha256':sha('commitment_qwen14_data.py'),
    'original_dependency_sha256':sha('commitment_data.py')}
(a.output/'config.json').write_text(json.dumps(config,indent=2))
with (a.output/'predictions.jsonl').open('w') as f:
    for interface,(texts,ids,_) in prepared.items():
        for i,(r,text,inp) in enumerate(zip(rows,texts,ids)):
            out={k:v for k,v in r.items() if k not in ['prompt','story','facts','human_values']}
            out.update(read(inp,r),interface=interface,readout_prompt_sha256=hashlib.sha256(text.encode()).hexdigest())
            f.write(json.dumps(out,ensure_ascii=False)+'\n');f.flush()
            if i%16==0:print(json.dumps({'interface':interface,'done':i+1,'total':len(rows)}),flush=True)
config.update(complete=True,wall_seconds=time.monotonic()-started);(a.output/'config.json').write_text(json.dumps(config,indent=2))
print(json.dumps({'complete':True,'n':config['n']}),flush=True)
