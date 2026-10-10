"""Source-conditioned copy/complement: equal source label bags, variable queries."""
import argparse
import copy
from collections import Counter
import hashlib
import itertools
import json
import platform
import subprocess
import time
from pathlib import Path
import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer


def contexts(n,seed):
    assert n%8==0
    rng=np.random.default_rng(seed);designs=list(itertools.product([-1,1],repeat=3))*(n//8);rng.shuffle(designs)
    out=[]
    for ci,(aa,ac,ad) in enumerate(designs):
        rs=[{'source':s,'input':x,'rep':r} for s in range(4) for x in [2,7] for r in range(2)];rng.shuffle(rs)
        out.append({'context':ci,'theta':[aa,-aa,ac,ad],'names':['Alex','Sam','Chris','Dana'],'records':rs})
    assert all(sum((c['theta'][0],c['theta'][2],c['theta'][3])==p for c in out)==n//8 for p in itertools.product([-1,1],repeat=3))
    return out


def function(x,theta):return x if theta==1 else 9-x


def theta(c,change):
    t=c['theta'].copy()
    for s in {'base':[],'owned_a':[0],'owned_b':[1],'foreign_swap':[2,3]}[change]:t[s]*=-1
    return t


def encode(tok,c,t,mode,single_source=None):
    text='Each named source follows one of two fixed rules: copy the input number, or subtract the input number from 9. Infer the requested source\'s rule from its records and apply it to the final input.\n'
    if mode.endswith('instruction'):text+='Use only the records from the requested source and the stated mapping constraint.\n'
    if mode=='direct':
        for s in range(4):text+=f'{c["names"][s]} always '+('copies the input number' if t[s]==1 else 'subtracts the input number from 9')+'.\n'
    ids=tok.encode(text+'\n',add_special_tokens=False);sites=[]
    for r in c['records']:
        if single_source is not None and r['source']!=single_source:continue
        ids+=tok.encode(f'Input: {r["input"]}\nSource: {c["names"][r["source"]]}\nLabel:',add_special_tokens=False)
        sites.append(len(ids)+1);ids+=tok.encode(' '+str(function(r['input'],t[r['source']]))+'\n\n',add_special_tokens=False)
    return ids,sites


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--n',type=int,default=32);ap.add_argument('--seed',type=int,default=77001);a=ap.parse_args()
    t0=time.time();torch.set_num_threads(6);torch.manual_seed(0);d=Path(a.out);d.mkdir(parents=True,exist_ok=True)
    cs=contexts(a.n,a.seed);tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    enc=[tok.encode(' '+str(y),add_special_tokens=False) for y in range(10)];space=tok.encode(' ',add_special_tokens=False)
    assert len(space)==1 and all(len(e)==2 and e[0]==space[0] for e in enc)
    labels=[e[-1] for e in enc]
    model,loading=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.float32,device_map='cuda',attn_implementation='eager',output_loading_info=True)
    model.eval();assert not loading.get('missing_keys') and not loading.get('unexpected_keys') and not loading.get('mismatched_keys'),loading
    errors=[]
    def score(cache,c,plen,sources):
        qs=[tok.encode(f'Input: {x}\nSource: {c["names"][s]}\nLabel:',add_special_tokens=False)+space for s in sources for x in range(10)]
        nb=len(qs);w=max(map(len,qs));ids=torch.zeros((nb,w),dtype=torch.long,device='cuda');mask=torch.zeros((nb,plen+w),dtype=torch.long,device='cuda');mask[:,:plen]=1;pos=torch.zeros_like(ids)
        for j,q in enumerate(qs):ids[j,-len(q):]=torch.tensor(q,device='cuda');mask[j,-len(q):]=1;pos[j,-len(q):]=torch.arange(plen,plen+len(q),device='cuda')
        cc=copy.deepcopy(cache);cc.batch_repeat_interleave(nb)
        v=model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=cc,use_cache=True,logits_to_keep=2).logits.float().log_softmax(-1)
        return (v[:,-1,labels]+v[:,-2,space[0],None]).cpu().numpy()
    (d/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    with torch.inference_mode(),(d/'behavior.jsonl').open('w') as f:
        for c in cs:
            scores={};golds={};computed={}
            for mode in ['mixed','mixed_instruction','single','single_instruction','direct']:
                for change in ['base','owned_a','owned_b','foreign_swap']:
                    t=theta(c,change);arrays=[]
                    for sources in [[0],[1]] if mode.startswith('single') else [[0,1]]:
                        ss=sources[0] if mode.startswith('single') else None
                        ids,sites=encode(tok,c,t,mode,ss)
                        original,original_sites=encode(tok,c,theta(c,'base'),mode,ss)
                        assert sites==original_sites and len(ids)==len(original)
                        if mode!='direct':assert Counter(ids)==Counter(original)
                        signature=(tuple(ids),tuple(sources))
                        if signature not in computed:
                            prefix=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True).past_key_values
                            v=score(prefix,c,len(ids),sources);computed[signature]=v
                            if change=='base':
                                e=float(np.max(np.abs(score(prefix,c,len(ids),sources)-v)));errors.append(e);assert e<=.1,e
                            del prefix
                        arrays.append(computed[signature])
                    key=mode+'.'+change;scores[key]=np.concatenate(arrays).tolist()
                    golds[key]=[function(x,t[s]) for s in [0,1] for x in range(10)]
            f.write(json.dumps({'context':c['context'],'theta':c['theta'],'scores':scores,'gold':golds})+'\n');f.flush()
            if c['context']%4==0:print(c['context'],round(time.time()-t0,1),flush=True)
    run={'args':vars(a),'seconds':time.time()-t0,'sanity_max_error':max(errors),'torch':torch.__version__,'transformers':transformers.__version__,
        'host':platform.node(),'gpu':torch.cuda.get_device_name(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'config_sha256':hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    (d/'run.json').write_text(json.dumps(run,indent=2))


if __name__=='__main__':main()
