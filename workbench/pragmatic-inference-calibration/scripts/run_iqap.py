"""E33 source four-way graded meaning readout, all candidates evaluated separately."""
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from iqap_data import prepare, prompt, sequences, common_model, fingerprint, CATEGORIES, TARGETS

def main():
    ap=argparse.ArgumentParser()
    for k in ['root','model','output']:ap.add_argument('--'+k,type=Path,required=True)
    for k in ['model-id','revision']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args()
    assert not a.output.exists()
    rows, data_sha=prepare(a.root)
    common=common_model(a.root,a.model.name)
    tok=AutoTokenizer.from_pretrained(common,local_files_only=True)
    plans={i:[sequences(tok,prompt(r),i) for r in rows] for i in ['bare','common-chat']}
    nulls={i:sequences(tok,prompt({'Question':'[not provided]','Answer':'[not provided]'}),i) for i in plans}
    # Full CPU prefix preflight happens before GPU loading. Actual IDs stored externally.
    a.output.mkdir(parents=True)
    (a.output/'input-plans.json').write_text(json.dumps(plans))
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,
        torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
    started=time.monotonic()
    @torch.inference_mode()
    def read(plan):
        out=[]
        # Primary single sequence: no cross-item or candidate padding/batch changes.
        for ids, end in zip(plan['ids'],plan['content_ends']):
            inp=torch.tensor([ids],device=model.device)
            h=model.model(input_ids=inp,use_cache=False).last_hidden_state
            logits=model.lm_head(h[0,plan['first']-1:len(ids)-1]).float()
            labels=inp[0,plan['first']:]
            lp=logits.log_softmax(-1).gather(1,labels[:,None]).flatten()
            out.append({'full_logprob':float(lp.sum()),
                'content_logprob':float(lp[:end-plan['first']].sum()),
                'content_tokens':end-plan['first'],
                'suffix_tokens':len(ids)-end})
        return out
    controls=[]
    for interface, ps in plans.items():
        for index in [0,149]:
            one,repeat=read(ps[index]),read(ps[index])
            delta=max(abs(x[k]-y[k]) for x,y in zip(one,repeat) for k in ['full_logprob','content_logprob'])
            controls.append({'interface':interface,'index':index,'single_repeat_max_delta':delta,'pass':delta<1e-6})
    (a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2))
    assert all(c['pass'] for c in controls), 'Single-sequence repeat gate failed'
    null_results={i:read(p) for i,p in nulls.items()}
    config={'task':'iqap_graded_interpretation','model':a.model_id,'revision':a.revision,
        'dtype':'float32','tf32':False,'batch_size':1,'numerical_gate_pass':True,
        'data_sha256':data_sha,'split':'DEVELOPMENT','n_source_items':150,
        'categories':CATEGORIES,'targets':TARGETS,'common_tokenizer':str(common),
        'input_token_hashes':{i:fingerprint(ps) for i,ps in plans.items()},
        'primary':'normalized full interpretation sequence likelihood including terminal suffix',
        'secondary':'content-only sequence likelihood; fixed null lexical prior diagnostic',
        'source_url':'https://compprag.christopherpotts.net/iqap.html',
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'data_helper_sha256':hashlib.sha256(Path(__file__).with_name('iqap_data.py').read_bytes()).hexdigest(),
        'null_readout':null_results}
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    with (a.output/'predictions.jsonl').open('w') as f:
        for interface, ps in plans.items():
            for n,(r,p) in enumerate(zip(rows,ps)):
                scores=read(p)
                z={'item':r['Item'],'classification':r['Classification'],'source':r['Source'],
                    'question':r['Question'],'answer':r['Answer'],'removed_prefix':r['Prefix'],
                    'human_counts':[int(r[k]) for k in CATEGORIES],
                    'interface':interface,'prompt_sha256':p['prompt_sha256'],'choice_scores':scores}
                for key in ['full_logprob','content_logprob']:
                    lp=np.array([s[key] for s in scores]);prob=np.exp(lp-lp.max());prob/=prob.sum()
                    z[key+'_normalized']=prob.tolist()
                f.write(json.dumps(z,ensure_ascii=False)+'\n');f.flush()
                if n%25==0:print(json.dumps({'interface':interface,'done':n+1,'total':150}),flush=True)
    config.update(complete=True,n=300,wall_seconds=time.monotonic()-started)
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    print(json.dumps({'complete':True,'n':300}),flush=True)

if __name__=='__main__':main()
