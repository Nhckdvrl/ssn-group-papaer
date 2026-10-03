import argparse,hashlib,json,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from projection_data import parse_rating
from projection_budget_data import selected

ap=argparse.ArgumentParser()
for k in ['root','model','output']:ap.add_argument('--'+k,type=Path,required=True)
for k in ['model-id','revision']:ap.add_argument('--'+k,required=True)
a=ap.parse_args();assert not a.output.exists();cp=a.model.name
if cp.startswith('Mistral'):
    from projection_mistral_data import common_model,inputs
else:
    from iqap_data import common_model
    from projection_data import inputs
rows,audit=selected(a.root,cp)
pre=json.loads(Path('workbench/pragmatic-inference-calibration/results/E42-selected-preflight.json').read_text())[cp]
assert audit==pre['audit'];tok=AutoTokenizer.from_pretrained(common_model(a.root,cp),local_files_only=True)
plans=[]
for z in rows:
    old=z['original'];texts,ids,_=inputs(tok,[z['source']],old['interface'])
    assert hashlib.sha256(texts[0].encode()).hexdigest()==old['readout_prompt_sha256']
    plans.append(ids[0])
assert hashlib.sha256(json.dumps(plans).encode()).hexdigest()==pre['selected_input_token_sha256']
a.output.mkdir(parents=True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
started=time.monotonic()
@torch.inference_mode()
def read(ids):
    z=model.generate(input_ids=torch.tensor([ids],device=model.device),attention_mask=torch.ones((1,len(ids)),dtype=torch.long,device=model.device),
        do_sample=False,max_new_tokens=32,pad_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True,use_cache=True)
    generated=z.sequences[0,len(ids):].tolist();text=tok.decode(generated,skip_special_tokens=True)
    eos=model.generation_config.eos_token_id;eos=[eos] if isinstance(eos,int) else eos or []
    return {'raw_text':text,'generated_ids':generated,'rating':parse_rating(text),'terminated_by_eos':bool(generated and generated[-1] in eos),
        'generated_token_logprobs':[float(score[0].float().log_softmax(-1)[target]) for score,target in zip(z.scores,generated)]}
controls=[]
for i in sorted({0,len(rows)-1}):
    x,y=read(plans[i]),read(plans[i]);delta=max([abs(u-v) for u,v in zip(x['generated_token_logprobs'],y['generated_token_logprobs'])] or [0])
    controls.append({'index':i,'same_generated_ids':x['generated_ids']==y['generated_ids'],'token_lp_delta':delta,
        'pass':x['generated_ids']==y['generated_ids'] and delta<.001})
(a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert all(c['pass'] for c in controls)
config={'model':a.model_id,'revision':a.revision,'dtype':'float32','batch_size':1,'max_new_tokens':32,'do_sample':False,
    'selection_audit':audit,'input_token_sha256':pre['selected_input_token_sha256'],'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(a.output/'config.json').write_text(json.dumps(config,indent=2))
with (a.output/'predictions.jsonl').open('w') as f:
    for i,(r,ids) in enumerate(zip(rows,plans)):
        z=read(ids);old=r['original'];prefix_same=z['generated_ids'][:len(old['generated_ids'])]==old['generated_ids']
        out={**z,'id':old['id'],'interface':old['interface'],'selection':r['selection'],
            'original_rating':old['rating'],'original_generated_ids':old['generated_ids'],'prefix_ids_match':prefix_same,
            'readout_prompt_sha256':old['readout_prompt_sha256']}
        f.write(json.dumps(out,ensure_ascii=False)+'\n');f.flush();assert prefix_same,'Budget changed greedy prefix: isolate this model'
        if i%100==0:print(json.dumps({'done':i+1,'total':len(rows)}),flush=True)
config.update(complete=True,n=len(rows),wall_seconds=time.monotonic()-started)
(a.output/'config.json').write_text(json.dumps(config,indent=2));print(json.dumps({'complete':True,'n':len(rows)}),flush=True)
