import argparse,hashlib,json,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from circa_pair_data import prepare,prompt,CATEGORIES
from run_circa_instruction import STRICT

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--shard',type=int,required=True);a=ap.parse_args();assert 0<=a.shard<4 and not a.output.exists()
rows,pairs,audit=prepare(a.root);rows=[r for r in rows if int(r['question_group'],16)%4==a.shard]
asset=a.root/'models/flan-t5-xl';tok=AutoTokenizer.from_pretrained(asset,local_files_only=True,use_fast=False)
choices=[tok.encode(str(x),add_special_tokens=False) for x in range(1,9)];assert all(len(x)==1 for x in choices);choices=[x[0] for x in choices]
inputs={}
for cond in ['original','strict']:
    for order in [0,1]:
        texts=[(STRICT if cond=='strict' else '')+prompt(r,order) for r in rows]
        ids=[tok.encode(s,add_special_tokens=True) for s in texts]
        inputs[cond+'/'+str(order)]=(texts,ids)
a.output.mkdir(parents=True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
model=AutoModelForSeq2SeqLM.from_pretrained(asset,local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
started=time.monotonic()
@torch.inference_mode()
def read(ids):
    logits=model(input_ids=torch.tensor([ids],device=model.device),decoder_input_ids=torch.tensor([[model.config.decoder_start_token_id]],device=model.device),use_cache=False).logits[0,-1].float()
    z=logits[choices]
    return {'ordered_probs':z.softmax(-1).cpu().tolist(),'choice_logits':z.cpu().tolist(),
            'support_mass':float((z.logsumexp(-1)-logits.logsumexp(-1)).exp()),'global_argmax_is_candidate':int(logits.argmax()) in choices}
controls=[]
for key,(_,ids) in inputs.items():
    for n in [0,len(rows)-1]:
        x,y=read(ids[n]),read(ids[n]);delta=max(abs(u-v) for u,v in zip(x['ordered_probs'],y['ordered_probs']))
        controls.append({'condition':key,'index':n,'delta':delta,'pass':delta<1e-6})
(a.output/'numerical-control.json').write_text(json.dumps(controls));assert all(c['pass'] for c in controls)
with (a.output/'predictions.jsonl').open('w') as f:
    for key,(texts,ids) in inputs.items():
        cond,order=key.split('/');order=int(order);options=CATEGORIES if order==0 else list(reversed(CATEGORIES))
        for i,(r,text,inp) in enumerate(zip(rows,texts,ids)):
            z=read(inp);record={**r,**z,'condition':cond,'order':order,'interface':'native-encoder',
                'choice_probs':dict(zip(options,z['ordered_probs'])),
                'readout_prompt_sha256':hashlib.sha256(text.encode()).hexdigest()}
            f.write(json.dumps(record,ensure_ascii=False)+'\n');f.flush()
        print(json.dumps({'done':key,'n':len(rows)}),flush=True)
config={'task':'flan_circa_native_control','model':'google/flan-t5-xl','revision':'7d6315df2c2fb742f0f5b556879d730926ca9001',
        'shard':a.shard,'n_shards':4,'dtype':'float32','batch_size':1,'n':4*len(rows),'n_items':len(rows),
        'source_audit':audit,'numerical_gate_pass':True,'complete':True,'wall_seconds':time.monotonic()-started,
        'add_special_tokens':True,'decoder_start_token_id':model.config.decoder_start_token_id,
        'input_token_hashes':{k:hashlib.sha256(json.dumps(ids).encode()).hexdigest() for k,(_,ids) in inputs.items()},
        'item_ids':[r['id'] for r in rows],'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(a.output/'config.json').write_text(json.dumps(config,indent=2));print(json.dumps({'complete':True,'n':config['n']}),flush=True)
