import argparse,hashlib,json,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from speaker_listener_data import prepare,inputs,parse,tokenizer_path

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--model',type=Path,required=True)
ap.add_argument('--model-id',required=True);ap.add_argument('--revision',required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
rows,audit=prepare(a.root);tok=AutoTokenizer.from_pretrained(tokenizer_path(a.root,a.model.name),local_files_only=True)
texts,ids,fp=inputs(tok,rows)
pre=json.loads((Path(__file__).resolve().parents[1]/'results/E49-source-preflight.json').read_text())
assert pre['gate_pass'] and audit==pre['source_audit'] and fp==pre['models'][a.model.name]['input_token_sha256']
sha=lambda name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
assert sha('speaker_listener_data.py')==pre['helper_sha256']
torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
started=time.monotonic()
model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').eval().to('cuda')
eos=model.generation_config.eos_token_id;eos=[eos] if isinstance(eos,int) else eos or []
@torch.inference_mode()
def read(inp,r):
    z=model.generate(input_ids=torch.tensor([inp],device='cuda'),attention_mask=torch.ones((1,len(inp)),device='cuda',dtype=torch.long),
        do_sample=False,max_new_tokens=64,pad_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True,use_cache=True)
    generated=z.sequences[0,len(inp):].tolist();raw=tok.decode(generated,skip_special_tokens=True)
    return dict(raw_text=raw,generated_ids=generated,prediction=parse(raw,r['task']),
        generated_token_logprobs=[float(s[0].float().log_softmax(-1)[t]) for s,t in zip(z.scores,generated)],
        terminated_by_eos=bool(generated and generated[-1] in eos),n_output_tokens=len(generated))

controls=[]
for task in ['listener','speaker']:
    indices=[i for i,r in enumerate(rows) if r['task']==task]
    for i in [indices[0],indices[-1]]:
        x,y=read(ids[i],rows[i]),read(ids[i],rows[i])
        repeat=max([abs(u-v) for u,v in zip(x['generated_token_logprobs'],y['generated_token_logprobs'])] or [0])
        with torch.inference_mode():
            seq=ids[i]+x['generated_ids']
            logits=model(input_ids=torch.tensor([seq],device='cuda'),attention_mask=torch.ones((1,len(seq)),device='cuda',dtype=torch.long)).logits[0].float()
            independent=[float(logits[len(ids[i])+j-1].log_softmax(-1)[t]) for j,t in enumerate(x['generated_ids'])]
        delta=max([abs(u-v) for u,v in zip(x['generated_token_logprobs'],independent)] or [0])
        controls.append(dict(id=rows[i]['id'],same_generated_ids=x['generated_ids']==y['generated_ids'],repeat_lp_delta=repeat,
            independent_full_lp_delta=delta,pass_gate=x['generated_ids']==y['generated_ids'] and repeat<.001 and delta<.001))
        del logits
(a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert all(z['pass_gate'] for z in controls)
config=dict(model=a.model_id,revision=a.revision,n=len(rows),dtype='float32',batch_size=1,max_new_tokens=64,do_sample=False,
    source_audit=audit,input_token_sha256=fp,numerical_gate_pass=True,tokenizer=str(tokenizer_path(a.root,a.model.name)),
    script_sha256=sha('run_speaker_listener.py'),helper_sha256=sha('speaker_listener_data.py'))
(a.output/'config.json').write_text(json.dumps(config,indent=2))
with (a.output/'predictions.jsonl').open('w') as f:
    for i,(r,t,inp) in enumerate(zip(rows,texts,ids)):
        out={k:v for k,v in r.items() if k not in ['prompt','human_norm']}
        out.update(read(inp,r),readout_prompt_sha256=hashlib.sha256(t.encode()).hexdigest())
        f.write(json.dumps(out,ensure_ascii=False)+'\n');f.flush()
        if i%40==0:print(json.dumps({'done':i+1,'total':len(rows)}),flush=True)
config.update(complete=True,wall_seconds=time.monotonic()-started);(a.output/'config.json').write_text(json.dumps(config,indent=2))
print(json.dumps({'complete':True,'n':len(rows)}),flush=True)
