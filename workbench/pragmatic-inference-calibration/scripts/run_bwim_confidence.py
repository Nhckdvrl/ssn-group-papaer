import argparse,hashlib,json,time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from bwim_data import prepare,SYSTEM,user_prompt,render,add_user,parse
from commitment_data import common_model

ap=argparse.ArgumentParser()
for k in ['root','model','output']:ap.add_argument('--'+k,type=Path,required=True)
for k in ['model-id','revision','seeds']:ap.add_argument('--'+k,required=True)
a=ap.parse_args();assert not a.output.exists();seeds=[int(x) for x in a.seeds.split(',')];assert seeds in [[0,2],[1,3]]
episodes,audit=prepare(a.root);pre=json.loads(Path('workbench/pragmatic-inference-calibration/results/E44-bwim-source-preflight.json').read_text())
assert pre['gate_pass'] and pre['audit']==audit
tok=AutoTokenizer.from_pretrained(common_model(a.root,a.model.name),local_files_only=True)
a.output.mkdir(parents=True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
limit=model.config.max_position_embeddings;eos=model.generation_config.eos_token_id;eos=[eos] if isinstance(eos,int) else eos or []
assert pre['models'][a.model.name]['gold_history_max_input_tokens']+512<=limit
config={'model':a.model_id,'revision':a.revision,'dtype':'float32','batch_size':1,'seeds':seeds,'n':80,
    'source_audit':audit,'max_new_tokens':512,'max_context_tokens':limit,'do_sample':False,'thinking':False,
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'helper_sha256':hashlib.sha256(Path(__file__).with_name('bwim_data.py').read_bytes()).hexdigest()}
(a.output/'config.json').write_text(json.dumps(config,indent=2));controls=[];started=time.monotonic()
@torch.inference_mode()
def read(ids):
    assert len(ids)+512<=limit,'Full history exceeds checkpoint context; do not truncate'
    z=model.generate(input_ids=torch.tensor([ids],device=model.device),attention_mask=torch.ones((1,len(ids)),dtype=torch.long,device=model.device),
        do_sample=False,max_new_tokens=512,pad_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True,use_cache=True)
    generated=z.sequences[0,len(ids):].tolist();text=tok.decode(generated,skip_special_tokens=True)
    return {'raw_text':text,'generated_ids':generated,'generated_token_logprobs':[float(score[0].float().log_softmax(-1)[target]) for score,target in zip(z.scores,generated)],
        'terminated_by_eos':bool(generated and generated[-1] in eos),'n_input_tokens':len(ids)}
def repeated(ids,z,seed,trial):
    other=read(ids);same=z['generated_ids']==other['generated_ids']
    delta=max([abs(u-v) for u,v in zip(z['generated_token_logprobs'],other['generated_token_logprobs'])] or [0])
    controls.append({'seed':seed,'trial':trial,'same_generated_ids':same,'token_lp_delta':delta,'pass':same and delta<.001})
    (a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert controls[-1]['pass']

with (a.output/'predictions.jsonl').open('w') as f:
    for seed in seeds:
        messages=[{'role':'system','content':SYSTEM}]
        for i,r in enumerate(episodes[seed]):
            add_user(messages,user_prompt(r,i in [0,20]));text,ids=render(tok,messages)
            z=read(ids)
            if i in [0,39]:repeated(ids,z,seed,i)
            parsed=parse(z['raw_text']);available=parsed is not None and z['terminated_by_eos']
            correct=parsed is not None and parsed['blocks']==r['gold_blocks']
            pragmatic=parsed is not None and parsed['blocks']==r['pragmatic_blocks']
            out={**r,**z,'parsed':parsed,'available':available,'correct':correct,'pragmatic_choice':pragmatic,
                'messages':messages,'input_sha256':hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                'prompt_sha256':hashlib.sha256(text.encode()).hexdigest()}
            f.write(json.dumps(out,ensure_ascii=False)+'\n');f.flush()
            # Retain the actual model answer, including malformed/prose outputs. Never replace it with gold.
            messages.append({'role':'assistant','content':z['raw_text']})
            built=(';'.join(','.join(map(str,b)) for b in parsed['blocks']) if parsed else 'unparseable response')
            add_user(messages,'FEEDBACK:'+str(correct)+'; the structure you built = '+built+'; the correct structure = '+r['target_structure']+';')
            print(json.dumps({'seed':seed,'trial':i+1,'available':available,'correct':correct,'input_tokens':len(ids)}),flush=True)
config.update(complete=True,numerical_gate_pass=all(c['pass'] for c in controls),wall_seconds=time.monotonic()-started,
    peak_gpu_memory_bytes=torch.cuda.max_memory_allocated())
(a.output/'config.json').write_text(json.dumps(config,indent=2));print(json.dumps({'complete':True,'n':80}),flush=True)
