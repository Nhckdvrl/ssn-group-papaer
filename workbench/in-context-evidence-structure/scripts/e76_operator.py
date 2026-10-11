"""Owned +/-1 parameters with answer words available only at foreign labels."""
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


def contexts(n, seed, stage='discovery'):
    assert n % 8 == 0
    rng=np.random.default_rng(seed)
    values=[3,4,5,6] if stage=='discovery' else [23,24,25,26]
    names=['Alex','Sam','Chris','Dana'] if stage=='discovery' else ['Alice','Bob','Casey','Eli']
    designs=list(itertools.product([-1,1],values))*(n//8);rng.shuffle(designs)
    out=[]
    for ci,(b,q) in enumerate(designs):
        records=[{'source':s,'input':q+dx,'rep':r} for s in range(4) for dx in [-2,2] for r in range(2)]
        rng.shuffle(records)
        out.append({'context':ci,'q':q,'offsets':[b,-b,-b,b],'names':names,'records':records,
            'queries':[{'source':s,'input':q+dx} for s in range(4) for dx in [-2,0,2]],
            'candidates':[q-3,q-1,q+1,q+3]})
    assert all(sum(c['offsets'][0]==b and c['q']==q for c in out)==n//8 for b,q in itertools.product([-1,1],values))
    return out


def offsets(c, change):
    bs=c['offsets'].copy()
    for s in {'base':[],'scope_swap':[0,1],'owned_a':[0,2],'owned_b':[1,3],'foreign_swap':[2,3],'comp_a':[2],'comp_b':[3]}[change]:bs[s]*=-1
    return bs


def encode(tok,c,bs,instructed):
    text='Each named source adds either +1 or -1 to every input number. The choice is fixed separately for each source. Infer the requested source\'s choice from the records and apply it to the final input.\n'
    if instructed:text+='Use only the records from the requested source and the stated mapping constraint.\n'
    ids=tok.encode(text+'\n',add_special_tokens=False);sites=[]
    for r in c['records']:
        ids+=tok.encode(f'Input: {r["input"]}\nSource: {c["names"][r["source"]]}\nLabel:',add_special_tokens=False)
        value=tok.encode(' '+str(r['input']+bs[r['source']]),add_special_tokens=False)
        sites.append(len(ids)+len(value)-1);ids+=tok.encode(' '+str(r['input']+bs[r['source']])+'\n\n',add_special_tokens=False)
    return ids,sites


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--n',type=int,default=32);ap.add_argument('--seed',type=int,default=76001)
    ap.add_argument('--stage',choices=['discovery','confirmation'],default='discovery');a=ap.parse_args()
    t0=time.time();torch.set_num_threads(6);torch.manual_seed(0);d=Path(a.out);d.mkdir(parents=True,exist_ok=True)
    cs=contexts(a.n,a.seed,a.stage);tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.float32,device_map='cuda',attn_implementation='eager').eval()
    errors=[]
    space_ids=tok.encode(' ',add_special_tokens=False);assert len(space_ids)==1
    space_id=space_ids[0]
    def score(cache,c,plen,label_ids,common_prefix):
        qs=[tok.encode(f'Input: {q["input"]}\nSource: {c["names"][q["source"]]}\nLabel:',add_special_tokens=False)+common_prefix for q in c['queries']]
        w=max(map(len,qs));ids=torch.zeros((12,w),dtype=torch.long,device='cuda');mask=torch.zeros((12,plen+w),dtype=torch.long,device='cuda');mask[:,:plen]=1;pos=torch.zeros_like(ids)
        for j,q in enumerate(qs):
            ids[j,-len(q):]=torch.tensor(q,device='cuda');mask[j,-len(q):]=1;pos[j,-len(q):]=torch.arange(plen,plen+len(q),device='cuda')
        cc=copy.deepcopy(cache);cc.batch_repeat_interleave(12)
        v=model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=cc,use_cache=True,logits_to_keep=len(common_prefix)+1).logits.float().log_softmax(-1)
        common=sum(v[:,j,tokid] for j,tokid in enumerate(common_prefix))
        return (v[:,-1,label_ids]+common[:,None]).cpu().numpy()
    (d/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    with torch.inference_mode(),(d/'behavior.jsonl').open('w') as f:
        for c in cs:
            encoded=[tok.encode(' '+str(y),add_special_tokens=False) for y in c['candidates']]
            common_prefix=encoded[0][:-1]
            assert common_prefix and common_prefix[0]==space_id and all(x[:-1]==common_prefix for x in encoded),encoded
            label_ids=[x[-1] for x in encoded];assert len(set(label_ids))==4
            scores={};gold={}
            for instructed in [0,1]:
                variants={change:encode(tok,c,offsets(c,change),instructed) for change in ['base','scope_swap','owned_a','owned_b','foreign_swap','comp_a','comp_b']}
                original,sites=variants['base']
                for change,(ids,ss) in variants.items():
                    assert len(ids)==len(original) and ss==sites
                    if not change.startswith('comp_'):assert Counter(ids)==Counter(original)
                    bs=offsets(c,change)
                    for s in [0,1]:
                        target=c['q']+bs[s]
                        assert all(r['input']+bs[s]!=target for r in c['records'] if r['source']==s)
                        assert any(r['input']+bs[r['source']]==target for r in c['records'])
                        assert target not in [c['q'],c['q']-2,c['q']+2,1,-1]
                    prefix=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True).past_key_values
                    key=f'{instructed}.{change}';v=score(prefix,c,len(ids),label_ids,common_prefix);scores[key]=v.tolist()
                    gold[key]=[c['candidates'].index(q['input']+bs[q['source']]) for q in c['queries']]
                    if change=='base':
                        err=float(np.max(np.abs(score(prefix,c,len(ids),label_ids,common_prefix)-v)));errors.append(err);assert err<=.1,err
                del prefix
            pair=[c['candidates'].index(c['q']+c['offsets'][s]) for s in [0,1]]
            f.write(json.dumps({'context':c['context'],'q':c['q'],'pair':pair,'scores':scores,'gold':gold})+'\n');f.flush()
            if c['context']%4==0:print(c['context'],round(time.time()-t0,1),flush=True)
    run={'args':vars(a),'seconds':time.time()-t0,'sanity_max_error':max(errors),'torch':torch.__version__,'transformers':transformers.__version__,
        'host':platform.node(),'gpu':torch.cuda.get_device_name(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'config_sha256':hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    (d/'run.json').write_text(json.dumps(run,indent=2))


if __name__=='__main__':main()
