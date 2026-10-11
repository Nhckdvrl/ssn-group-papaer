"""Counterfactual prefix-state history with native label evidence kept fixed."""
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path
import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from e58_factorization import make_contexts
from e59_mediation import patch
from e67_prefix import HEAD, encode, query_batch


def main():
    ap=argparse.ArgumentParser()
    for arg in ['model','out','stage']:ap.add_argument('--'+arg,required=True)
    for arg in ['n','seed']:ap.add_argument('--'+arg,type=int,required=True)
    a=ap.parse_args();assert a.stage in ['discovery','confirmation']
    torch.set_num_threads(6);torch.manual_seed(0);t0=time.time();dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    ctxs=make_contexts(a.stage,a.n,a.seed);rng=np.random.default_rng(a.seed+91117)
    for c in ctxs:c['code_permutation']=int(rng.integers(2))
    labels=['yes','no'] if a.stage=='discovery' else ['toxic','safe']
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    label_ids=[tok.encode(' '+l,add_special_tokens=False)[0] for l in labels]
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.bfloat16,device_map='cuda',attn_implementation='eager').eval()
    state={'isolating':False,'max_mass':0.0}
    def hook(module,args,kwargs,output):
        if state['isolating']:
            mass=(output[1].float()*state['forbidden'][None,None]).sum(-1).max()
            state['max_mass']=max(state['max_mass'],float(mass))
        return output
    for layer in model.model.layers:layer.self_attn.register_forward_hook(hook,with_kwargs=True)
    errors=[];feature_errors=[]

    def prefix(ctx,layout,mode='native'):
        ids,sites=encode(tok,ctx,labels,layout);plen=len(ids)
        kw={}
        if mode!='native':
            header=len(tok.encode(HEAD,add_special_tokens=False));owner=torch.full((plen,),-1,dtype=torch.long,device='cuda');start=header
            for j,end in enumerate(sites['label']):
                end+=1+len(tok.encode('\n\n',add_special_tokens=False));owner[start:end]=j;start=end
            assert start==plen and int((owner<0).sum())==header
            causal=torch.ones((plen,plen),dtype=torch.bool,device='cuda').tril()
            other=(owner[:,None]!=owner[None,:])&(owner[None,:]>=0)&(owner[:,None]>=0)
            state['forbidden']=other&causal
            allow=causal if mode=='full' else causal&~other
            dtype=next(model.parameters()).dtype
            mask=torch.zeros((plen,plen),dtype=dtype,device='cuda').masked_fill(~allow,torch.finfo(dtype).min)[None,None]
            kw['attention_mask']=mask
            state['isolating']=mode=='isolated'
        out=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1,**kw)
        state['isolating']=False
        return out.past_key_values,sites,plen

    def score(cache,ctx,q,plen):
        ids,mask,pos,_=query_batch(tok,ctx,q,plen);c=copy.deepcopy(cache);c.batch_repeat_interleave(len(ctx['queries']))
        logits=model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=c,use_cache=True,logits_to_keep=1).logits[:,-1].float()
        return (logits[:,label_ids[1]]-logits[:,label_ids[0]]).cpu().numpy()

    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in ctxs))
    with (dest/'behavior.jsonl').open('w') as f,torch.inference_mode():
        for ci,ctx in enumerate(ctxs):
            c0,st0,plen=prefix(ctx,0);c1,st1,pl1=prefix(ctx,1);assert plen==pl1 and st0==st1
            isolated,st,pl=prefix(ctx,1,'isolated');full,_,_=prefix(ctx,1,'full')
            flipped=copy.deepcopy(ctx)
            for ex in flipped['demos']:ex['label']^=1
            fc,_,_=prefix(flipped,1);fi,_,_=prefix(flipped,1,'isolated')
            for base,donor,positions in [(c1,fc,[st1['prefix'][0]]),(isolated,fi,st1['prefix'])]:
                for dst,src in zip(base.layers,donor.layers):
                    feature_errors.extend([float((dst.keys[:,:,positions]-src.keys[:,:,positions]).float().abs().max()),
                                           float((dst.values[:,:,positions]-src.values[:,:,positions]).float().abs().max())])
            scores={}
            for name,c in [('D0',c0),('D1',c1),('fullmask',full),('rule_flip',fc),('all_isolated',isolated)]:
                for q in (0,1):scores[name+f'Q{q}']=score(c,ctx,q,plen)
            for q in (0,1):errors.append(float(abs(scores[f'D1Q{q}']-scores[f'fullmaskQ{q}']).max()))
            for site in ['prefix','tag','source','label']:
                channels=['key','value','kv'] if site=='prefix' else ['kv']
                for channel in channels:
                    c=patch(c1,isolated,st1[site],channel)
                    scores[f'D1Q1.isolated_{site}_{channel}']=score(c,ctx,1,plen)
            for channel in ['key','value','kv']:
                c=patch(c1,fc,st1['prefix'],channel)
                scores[f'D1Q1.flip_prefix_{channel}']=score(c,ctx,1,plen)
            groups={'prefix':st1['prefix'],'tag':st1['tag'],'prefix_tag':st1['prefix']+st1['tag'],
                    'prefix_tag_label':st1['prefix']+st1['tag']+st1['label'],'full':list(range(plen))}
            for site,positions in groups.items():
                channels=['key','value','kv'] if site=='prefix' else ['kv']
                for channel in channels:
                    c=patch(c0,c1,positions,channel)
                    for q in (0,1):
                        key=f'D0Q{q}.D1_{site}_{channel}';scores[key]=score(c,ctx,q,plen)
                        if site=='full':errors.append(float(abs(scores[key]-scores[f'D1Q{q}']).max()))
            c=patch(c1,c1,st1['prefix'],'kv');scores['noop']=score(c,ctx,1,plen)
            errors.append(float(abs(scores['noop']-scores['D1Q1']).max()))
            for layout in (0,1):
                ids,sst=encode(tok,ctx,labels,layout,True);c=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
                scores[f'D{layout}Q{layout}.instruction']=score(c,ctx,layout,len(ids))
                pieces=[]
                for source in (0,1):
                    indices=[j for j,q in enumerate(ctx['queries']) if q['source']==source]
                    sc=dict(ctx,demos=[d for d in ctx['demos'] if d['source']==source],queries=[ctx['queries'][j] for j in indices])
                    ids,_=encode(tok,sc,labels,layout);c=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
                    pred=score(c,sc,layout,len(ids));pieces.extend(zip(indices,map(float,pred)))
                scores[f'D{layout}Q{layout}.single']=[v for _,v in sorted(pieces)]
            assert max(feature_errors)==0 and state['max_mass']==0,(feature_errors,state)
            f.write(json.dumps({'context':ci,'signs':[2*q['label']-1 for q in ctx['queries']],
                'scores':{k:list(map(float,v)) for k,v in scores.items()}})+'\n');f.flush()
            if ci%4==0:print(ci,round(time.time()-t0,1),flush=True)
    run={'args':vars(a),'seconds':time.time()-t0,'sanity_max_error':max(errors),'causal_feature_error_max':max(feature_errors),
         'cross_demo_attention_mass_max':state['max_mass'],'torch':torch.__version__,'transformers':transformers.__version__,
         'host':platform.node(),'gpu':torch.cuda.get_device_name(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'config_sha256':hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
         'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    assert max(errors)<=.1,run
    (dest/'run.json').write_text(json.dumps(run,indent=2));print(json.dumps(run),flush=True)

if __name__=='__main__':main()
