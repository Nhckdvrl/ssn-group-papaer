"""E55 full original candidates, independent numerical gate, no participant fields."""
import argparse
import json
import math
import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from noisy_parent_data import prepare, fingerprint, tokenizer_path, sha, specs


def main():
    ap=argparse.ArgumentParser()
    for name in ['root','model','output']:ap.add_argument('--'+name,type=Path,required=True)
    for name in ['model-id','revision']:ap.add_argument('--'+name,required=True)
    a=ap.parse_args();assert not a.output.exists()
    m=next(m for m in specs(a.root) if m['id']==a.model_id);assert m['sha']==a.revision
    marker=json.loads((a.model/'DOWNLOAD_COMPLETE.json').read_text())
    assert marker['model']==a.model_id and marker['revision']==a.revision
    tok=AutoTokenizer.from_pretrained(tokenizer_path(a.root,a.model.name),local_files_only=True)
    rows,audit,nulls=prepare(a.root,tok)
    pre=json.loads((Path(__file__).resolve().parents[1]/'results/E55-source-preflight.json').read_text())
    assert pre['gate_pass'] and pre['models']==specs(a.root)
    check=pre['audits'][a.model.name]
    assert check['source_audit']==audit and check['input_sha256']==fingerprint(rows,nulls)
    helper=Path(__file__).with_name('noisy_parent_data.py')
    assert pre['helper_sha256']==sha(helper)
    a.output.mkdir(parents=True)
    (a.output/'input-plans.json').write_text(json.dumps({'rows':rows,'nulls':nulls}))
    torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    start=time.monotonic()
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,
        torch_dtype=torch.float32,attn_implementation='eager',device_map={'':0},weights_only=True).eval()

    @torch.inference_mode()
    def read(plan,independent=False):
        begin=len(plan['prefix_ids']);scores={'full':[],'content':[]}
        sequences=plan['full_ids'];width=max(map(len,sequences))
        if not independent:
            x=torch.full((2,width),tok.pad_token_id or tok.eos_token_id,device=model.device,dtype=torch.long)
            mask=torch.zeros_like(x)
            for i,z in enumerate(sequences):x[i,:len(z)]=torch.tensor(z,device=model.device);mask[i,:len(z)]=1
            h=model.model(input_ids=x,attention_mask=mask,use_cache=False).last_hidden_state
        for i,z in enumerate(sequences):
            content=plan['content_ids'][i];assert z[:len(content)]==content
            inp=torch.tensor([z],device=model.device)
            if independent:logits=model(input_ids=inp,use_cache=False).logits[0,begin-1:len(z)-1].float()
            else:logits=model.lm_head(h[i,begin-1:len(z)-1]).float()
            lp=logits.log_softmax(-1).gather(-1,inp[0,begin:,None]).flatten()
            scores['full'].append(float(lp.sum()));scores['content'].append(float(lp[:len(content)-begin].sum()))
        out={}
        for key,lp in scores.items():
            z=float(np.logaddexp.reduce(lp))
            out[key]={'logprobs':lp,'conditional_probs':np.exp(np.array(lp)-z).tolist(),
                'candidate_mass':math.exp(z),'argmax':int(np.argmax(lp))}
        return out

    controls=[]
    for interface in ['bare','common-chat']:
        for instruction in ['default','literal']:
            group=[r for r in rows if r['interface']==interface and r['instruction']==instruction]
            for r in [group[0],group[-1]]:
                x,y,z=read(r['plan']),read(r['plan']),read(r['plan'],True)
                repeat=max(abs(u-v) for k in x for u,v in zip(x[k]['logprobs'],y[k]['logprobs']))
                delta=max(abs(u-v) for k in x for u,v in zip(x[k]['logprobs'],z[k]['logprobs']))
                prob=max(abs(u-v) for k in x for u,v in zip(x[k]['conditional_probs'],z[k]['conditional_probs']))
                same=all(x[k]['argmax']==z[k]['argmax'] for k in x)
                controls.append({'id':r['id'],'repeat_delta':repeat,'independent_lp_delta':delta,
                    'prob_delta':prob,'argmax_agrees':same,'pass':repeat<1e-6 and delta<.001 and prob<.001 and same})
    (a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2))
    assert all(c['pass'] for c in controls),'E55 numerical gate: zero experiment predictions'
    config={'model':a.model_id,'revision':a.revision,'n':len(rows),'source_audit':audit,
        'input_sha256':fingerprint(rows,nulls),'helper_sha256':sha(helper),'script_sha256':sha(Path(__file__)),
        'dtype':'float32','attention':'eager','candidate_batch_size':2,'tf32':False,'numerical_gate_pass':True,
        'null_readout':{k:read(p) for k,p in nulls.items()},'primary':'full period-completed candidate, no EOS'}
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    with (a.output/'predictions.jsonl').open('w') as f:
        for i,r in enumerate(rows):
            f.write(json.dumps({**r,**read(r['plan'])})+'\n');f.flush()
            if i%50==0:print(json.dumps({'done':i+1,'n':len(rows)}),flush=True)
    config.update(complete=True,wall_seconds=time.monotonic()-start)
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    print(json.dumps({'complete':True,'n':len(rows)}),flush=True)


if __name__=='__main__':main()
