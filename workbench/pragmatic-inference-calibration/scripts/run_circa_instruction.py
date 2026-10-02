import argparse,hashlib,json,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from run_native_readout import next_logits
from iqap_data import common_model
from circa_pair_data import prepare,prompt,CATEGORIES
STRICT='Match both the yes/no direction and the strength or conditions of the answer; do not add or remove certainty or conditions.\n'
def strict_render(tok,row,order,interface):
    p=STRICT+prompt(row,order)
    return p if interface=='bare' else tok.apply_chat_template([{'role':'user','content':p}],tokenize=False,add_generation_prompt=True,enable_thinking=False)


def main():
    ap=argparse.ArgumentParser()
    for k in ['root','model','output']:ap.add_argument('--'+k,type=Path,required=True)
    for k in ['model-id','revision']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();assert not a.output.exists()
    rows,pairs,audit=prepare(a.root)
    tok=AutoTokenizer.from_pretrained(common_model(a.root,a.model.name),local_files_only=True)
    digit_ids=[tok.encode(str(x),add_special_tokens=False) for x in range(1,9)]
    assert all(len(x)==1 for x in digit_ids);digits=[x[0] for x in digit_ids]
    inputs={}
    for interface in ['bare','common-chat']:
        for order in [0,1]:
            texts=[strict_render(tok,r,order,interface) for r in rows]
            ids=[tok.encode(p,add_special_tokens=False) for p in texts]
            inputs[interface+'/'+str(order)]=(texts,ids)
    a.output.mkdir(parents=True)
    (a.output/'source-pairs.json').write_text(json.dumps(pairs,ensure_ascii=False))
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,
        torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
    started=time.monotonic()
    @torch.inference_mode()
    def read(ids):
        t=torch.tensor([ids],device=model.device)
        logits=next_logits(model,{'input_ids':t})[0]
        ls=logits[digits]
        return {'ordered_probs':ls.softmax(-1).cpu().tolist(),
                'choice_logits':ls.cpu().tolist(),
                'support_mass':float((ls.logsumexp(-1)-logits.logsumexp(-1)).exp()),
                'global_argmax_is_candidate':int(logits.argmax()) in digits}
    controls=[]
    for key,(_,ids) in inputs.items():
        for i in [0,len(rows)-1]:
            x,y=read(ids[i]),read(ids[i]);delta=max(abs(u-v) for u,v in zip(x['ordered_probs'],y['ordered_probs']))
            controls.append({'condition':key,'index':i,'single_repeat_delta':delta,'pass':delta<1e-6})
    (a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2));assert all(c['pass'] for c in controls)
    config={'task':'circa_bounded_strength_instruction_control','strict_instruction':STRICT,'model':a.model_id,'revision':a.revision,
        'dtype':'float32','batch_size':1,'tf32':False,'common_tokenizer':str(common_model(a.root,a.model.name)),
        'source_audit':audit,'numerical_gate_pass':True,
        'input_token_hashes':{k:hashlib.sha256(json.dumps(ids).encode()).hexdigest() for k,(_,ids) in inputs.items()},
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'data_helper_sha256':hashlib.sha256(Path(__file__).with_name('circa_pair_data.py').read_bytes()).hexdigest()}
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    with (a.output/'predictions.jsonl').open('w') as f:
        for key,(texts,ids) in inputs.items():
            interface,order=key.split('/');order=int(order)
            options=CATEGORIES if order==0 else list(reversed(CATEGORIES))
            for i,(r,p,input_ids) in enumerate(zip(rows,texts,ids)):
                z=read(input_ids)
                record={**r,**z,'interface':interface,'order':order,
                    'choice_probs':dict(zip(options,z['ordered_probs'])),
                    'readout_prompt_sha256':hashlib.sha256(p.encode()).hexdigest()}
                f.write(json.dumps(record,ensure_ascii=False)+'\n');f.flush()
                if i%100==0:print(json.dumps({'condition':key,'done':i+1,'total':len(rows)}),flush=True)
    config.update(complete=True,n=4*len(rows),wall_seconds=time.monotonic()-started)
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    print(json.dumps({'complete':True,'n':config['n']}),flush=True)

if __name__=='__main__':main()
