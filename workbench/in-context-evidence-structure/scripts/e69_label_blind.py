"""Keep unlabeled context structure while preventing every label relay."""
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
from e58_factorization import make_contexts
from e59_mediation import patch
from e67_prefix import HEAD,encode,query_batch
from transformers import AutoModelForCausalLM,AutoTokenizer


def main():
    ap=argparse.ArgumentParser()
    for x in ['model','out','stage']:ap.add_argument('--'+x,required=True)
    for x in ['n','seed']:ap.add_argument('--'+x,type=int,required=True)
    a=ap.parse_args();assert a.stage in ['discovery','confirmation']
    torch.set_num_threads(6);torch.manual_seed(0);t0=time.time();dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    ctxs=make_contexts(a.stage,a.n,a.seed);rng=np.random.default_rng(a.seed+91117)
    for c in ctxs:c['code_permutation']=int(rng.integers(2))
    labels=['yes','no'] if a.stage=='discovery' else ['toxic','safe']
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True);label_ids=[tok.encode(' '+l,add_special_tokens=False)[0] for l in labels]
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.bfloat16,device_map='cuda',attn_implementation='eager').eval()
    state={'on':False,'blind_max_mass':0.0,'isolated_max_mass':0.0}
    def hook(module,args,kwargs,output):
        if state['on']:
            mass=(output[1].float()*state['forbidden'][None,None]).sum(-1).max()
            key=state['mode']+'_max_mass';state[key]=max(state[key],float(mass))
        return output
    for layer in model.model.layers:layer.self_attn.register_forward_hook(hook,with_kwargs=True)
    errors=[];feature_errors=[]

    def prefix(ctx,layout=1,mode='native',instruction=False):
        ids,st=encode(tok,ctx,labels,layout,instruction);plen=len(ids);kw={}
        if mode!='native':
            causal=torch.ones((plen,plen),dtype=torch.bool,device='cuda').tril()
            if mode=='blind':
                cols=torch.zeros(plen,dtype=torch.bool,device='cuda');cols[st['label']]=True
                forbidden=causal&cols[None,:]&~torch.eye(plen,dtype=torch.bool,device='cuda')
            elif mode=='isolated':
                header=len(tok.encode(HEAD,add_special_tokens=False));owner=torch.full((plen,),-1,dtype=torch.long,device='cuda');start=header
                for j,end in enumerate(st['label']):
                    end+=1+len(tok.encode('\n\n',add_special_tokens=False));owner[start:end]=j;start=end
                assert start==plen
                forbidden=causal&(owner[:,None]!=owner[None,:])&(owner[:,None]>=0)&(owner[None,:]>=0)
            else:
                assert mode=='full';forbidden=torch.zeros_like(causal)
            allow=causal&~forbidden;dtype=next(model.parameters()).dtype
            kw['attention_mask']=torch.zeros((plen,plen),dtype=dtype,device='cuda').masked_fill(~allow,torch.finfo(dtype).min)[None,None]
            state.update(on=mode!='full',forbidden=forbidden,mode=mode)
        out=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1,**kw);state['on']=False
        return out.past_key_values,st,plen

    def score(cache,ctx,q,plen):
        ids,mask,pos,_=query_batch(tok,ctx,q,plen);c=copy.deepcopy(cache);c.batch_repeat_interleave(len(ctx['queries']))
        logits=model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=c,use_cache=True,logits_to_keep=1).logits[:,-1].float()
        return (logits[:,label_ids[1]]-logits[:,label_ids[0]]).cpu().numpy()

    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in ctxs))
    with (dest/'behavior.jsonl').open('w') as f,torch.inference_mode():
        for ci,ctx in enumerate(ctxs):
            base,st,plen=prefix(ctx);field,_,_=prefix(ctx,0);full,_,_=prefix(ctx,mode='full')
            blind,_,_=prefix(ctx,mode='blind');isolated,_,_=prefix(ctx,mode='isolated')
            flipped=copy.deepcopy(ctx)
            for ex in flipped['demos']:ex['label']^=1
            blindflip,_,_=prefix(flipped,mode='blind')
            nonlabel=[j for j in range(plen) if j not in st['label']]
            for dst,src in zip(blind.layers,blindflip.layers):
                feature_errors.extend([float((dst.keys[:,:,nonlabel]-src.keys[:,:,nonlabel]).float().abs().max()),
                                       float((dst.values[:,:,nonlabel]-src.values[:,:,nonlabel]).float().abs().max())])
            scores={'D1Q1':score(base,ctx,1,plen),'D0Q0':score(field,ctx,0,plen),'fullmask':score(full,ctx,1,plen)}
            errors.append(float(abs(scores['D1Q1']-scores['fullmask']).max()))
            groups={'prefix':st['prefix'],'source':st['source'],'tag':st['tag'],
                    'source_tag_prefix':st['source']+st['tag']+st['prefix'],'all_nonlabel':nonlabel}
            for donor,c in [('blind',blind),('isolated',isolated)]:
                for site,positions in groups.items():
                    channels=['key','value','kv'] if site=='prefix' else ['kv']
                    for channel in channels:
                        patched=patch(base,c,positions,channel);scores[f'{donor}.{site}.{channel}']=score(patched,ctx,1,plen)
            noop=patch(base,base,st['prefix'],'kv');scores['noop']=score(noop,ctx,1,plen)
            errors.append(float(abs(scores['D1Q1']-scores['noop']).max()))
            for layout in (0,1):
                c,_,pl=prefix(ctx,layout,instruction=True);scores[f'D{layout}Q{layout}.instruction']=score(c,ctx,layout,pl)
                pieces=[]
                for source in (0,1):
                    indices=[j for j,q in enumerate(ctx['queries']) if q['source']==source]
                    sc=dict(ctx,demos=[x for x in ctx['demos'] if x['source']==source],queries=[ctx['queries'][j] for j in indices])
                    c,_,pl=prefix(sc,layout);pred=score(c,sc,layout,pl);pieces.extend(zip(indices,map(float,pred)))
                scores[f'D{layout}Q{layout}.single']=[v for _,v in sorted(pieces)]
            assert max(feature_errors)==0 and state['blind_max_mass']==0 and state['isolated_max_mass']==0,(feature_errors,state)
            f.write(json.dumps({'context':ci,'signs':[2*q['label']-1 for q in ctx['queries']],
                   'scores':{k:list(map(float,v)) for k,v in scores.items()}})+'\n');f.flush()
            if ci%4==0:print(ci,round(time.time()-t0,1),flush=True)
    run={'args':vars(a),'seconds':time.time()-t0,'sanity_max_error':max(errors),'nonlabel_flip_feature_error_max':max(feature_errors),
         'label_forbidden_attention_mass_max':state['blind_max_mass'],'cross_demo_attention_mass_max':state['isolated_max_mass'],
         'torch':torch.__version__,'transformers':transformers.__version__,'host':platform.node(),'gpu':torch.cuda.get_device_name(),
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'config_sha256':hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
         'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    assert max(errors)<=.1,run
    (dest/'run.json').write_text(json.dumps(run,indent=2));print(json.dumps(run),flush=True)

if __name__=='__main__':main()
