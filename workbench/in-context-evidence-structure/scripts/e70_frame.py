"""Separate common context shift from item-dependent prefix-key changes."""
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
from transformers import AutoModelForCausalLM,AutoTokenizer
from transformers.models.qwen3.modeling_qwen3 import apply_rotary_pos_emb
from e58_factorization import make_contexts
from e59_mediation import patch
from e67_prefix import HEAD,encode,query_batch


def main():
    ap=argparse.ArgumentParser()
    for x in ['model','out','stage']:ap.add_argument('--'+x,required=True)
    for x in ['n','seed']:ap.add_argument('--'+x,type=int,required=True)
    ap.add_argument('--dtype',choices=['bfloat16','float32'],default='float32')
    ap.add_argument('--extract-frame-only',action='store_true')
    ap.add_argument('--frame-source')
    a=ap.parse_args();assert a.stage in ['discovery','confirmation']
    torch.set_num_threads(6);torch.manual_seed(0);t0=time.time();dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    ctxs=make_contexts(a.stage,a.n,a.seed);rng=np.random.default_rng(a.seed+91117)
    for c in ctxs:c['code_permutation']=int(rng.integers(2))
    labels=['yes','no'] if a.stage=='discovery' else ['toxic','safe']
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True);label_ids=[tok.encode(' '+x,add_special_tokens=False)[0] for x in labels]
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=getattr(torch,a.dtype),device_map='cuda',attn_implementation='eager').eval()
    state={'audit':False,'measure':False,'capture':False,'q':{},'mass_max':0.0};errs=[];ferrs=[];spreads=[];rounding=[]
    for li,layer in enumerate(model.model.layers):
        def hook(idx):
            def h(module,args,kwargs,output):
                if state['audit']:
                    mass=(output[1].float()*state['forbidden'][None,None]).sum(-1).max();state['mass_max']=max(state['mass_max'],float(mass))
                if state['measure']:
                    p=output[1][...,state['prefix_sites']].float();valid=state['qmask'][:,None,:]
                    p=p*valid[...,None];den=p.sum((1,2,3));valid_count=valid.sum((1,2))*p.shape[1]
                    src=state['match'][:,None,None,:]
                    state['attention'][idx]={'mass':(den/valid_count.clamp_min(1e-9)).cpu().tolist(),
                         'within_source':((p*src).sum((1,2,3))/den.clamp_min(1e-9)).cpu().tolist()}
                if state['capture']:
                    hs=kwargs.get('hidden_states',args[0] if args else None)
                    q=module.q_norm(module.q_proj(hs).view(*hs.shape[:-1],-1,module.head_dim)).transpose(1,2)
                    q,_=apply_rotary_pos_emb(q,q,*kwargs['position_embeddings']);state['q'][idx]=q.float().clone()
                return output
            return h
        layer.self_attn.register_forward_hook(hook(li),with_kwargs=True)

    def prefix(ctx,layout=1,mode='native',instruction=False):
        ids,st=encode(tok,ctx,labels,layout,instruction);pl=len(ids);kw={}
        if mode!='native':
            causal=torch.ones((pl,pl),dtype=torch.bool,device='cuda').tril()
            if mode=='blind':
                cols=torch.zeros(pl,dtype=torch.bool,device='cuda');cols[st['label']]=True
                forbidden=causal&cols[None,:]&~torch.eye(pl,dtype=torch.bool,device='cuda')
            elif mode=='isolated':
                owner=torch.full((pl,),-1,dtype=torch.long,device='cuda');start=len(tok.encode(HEAD,add_special_tokens=False))
                for j,end in enumerate(st['label']):end+=1+len(tok.encode('\n\n',add_special_tokens=False));owner[start:end]=j;start=end
                assert start==pl
                forbidden=causal&(owner[:,None]!=owner[None,:])&(owner[:,None]>=0)&(owner[None,:]>=0)
            else:assert mode=='full';forbidden=torch.zeros_like(causal)
            dtype=next(model.parameters()).dtype
            kw['attention_mask']=torch.zeros((pl,pl),dtype=dtype,device='cuda').masked_fill(~(causal&~forbidden),torch.finfo(dtype).min)[None,None]
            state.update(audit=mode!='full',forbidden=forbidden)
        out=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1,**kw);state['audit']=False
        return out.past_key_values,st,pl

    def score(c,ctx,q,pl,st,capture=False):
        ids,mask,pos,_=query_batch(tok,ctx,q,pl);cc=copy.deepcopy(c);cc.batch_repeat_interleave(len(ctx['queries']))
        state.update(measure=True,capture=capture,prefix_sites=st['prefix'],qmask=mask[:,pl:].float(),
                     match=torch.tensor([[x['source']==y['source'] for y in ctx['demos']] for x in ctx['queries']],device='cuda'),attention={})
        logits=model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=cc,use_cache=True,logits_to_keep=1).logits[:,-1].float()
        state.update(measure=False,capture=False)
        return (logits[:,label_ids[1]]-logits[:,label_ids[0]]).cpu().numpy(),state['attention']

    if a.extract_frame_only:
        frames=[];frame_errors=[]
        with torch.inference_mode():
            for ctx in ctxs:
                b,st,pl=prefix(ctx,mode='blind');i,_,_=prefix(ctx,mode='isolated')
                fc=copy.deepcopy(ctx)
                for x in fc['demos']:x['label']^=1
                bf,_,_=prefix(fc,mode='blind');nonlabel=[j for j in range(pl) if j not in st['label']]
                frame=[]
                for dst,src,fl in zip(b.layers,i.layers,bf.layers):
                    frame.append((dst.keys[:,:,st['prefix']].float()-src.keys[:,:,st['prefix']].float()).mean(2,keepdim=True).cpu().numpy())
                    frame_errors.append(float((dst.keys[:,:,nonlabel]-fl.keys[:,:,nonlabel]).float().abs().max()))
                frames.append(np.stack(frame))
        assert max(frame_errors)==0 and state['mass_max']==0
        mean=np.stack(frames).astype(np.float64).mean(0).astype(np.float32)
        np.save(dest/'frame.npy',mean)
        meta={'args':vars(a),'seconds':time.time()-t0,'label_blind_feature_error_max':max(frame_errors),
              'forbidden_attention_mass_max':state['mass_max'],'shape':list(mean.shape),
              'frame_sha256':hashlib.sha256((dest/'frame.npy').read_bytes()).hexdigest(),
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'config_sha256':hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
              'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
        (dest/'frame_metadata.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta),flush=True);return
    frozen=None
    if a.frame_source:
        frozen=torch.from_numpy(np.load(a.frame_source)).to(device='cuda',dtype=torch.float32)
        frame_meta=json.loads((Path(a.frame_source).parent/'frame_metadata.json').read_text())
        assert frame_meta['args']['stage']=='discovery' and frame_meta['label_blind_feature_error_max']==0
        assert frame_meta['config_sha256']==hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest()
    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in ctxs))
    with (dest/'behavior.jsonl').open('w') as f,torch.inference_mode():
        for ci,ctx in enumerate(ctxs):
            base,st,pl=prefix(ctx);field,_,_=prefix(ctx,0);full,_,_=prefix(ctx,mode='full');blind,_,_=prefix(ctx,mode='blind');iso,_,_=prefix(ctx,mode='isolated')
            fc=copy.deepcopy(ctx)
            for x in fc['demos']:x['label']^=1
            bf,_,_=prefix(fc,mode='blind');nonlabel=[i for i in range(pl) if i not in st['label']]
            for dst,src in zip(blind.layers,bf.layers):
                ferrs.extend([float((dst.keys[:,:,nonlabel]-src.keys[:,:,nonlabel]).float().abs().max()),float((dst.values[:,:,nonlabel]-src.values[:,:,nonlabel]).float().abs().max())])
            scores={};att={}
            for d,c in [(0,field),(1,base)]:
                for q in (0,1):scores[f'D{d}Q{q}'],att[f'D{d}Q{q}']=score(c,ctx,q,pl,st,capture=d==1 and q==1)
            v,_=score(full,ctx,1,pl,st);errs.append(float(abs(v-scores['D1Q1']).max()))
            variants={k:copy.deepcopy(base) for k in ['isolated','blind','common','centered','both','norm','negative_common']}
            if frozen is not None:variants['shared_frame']=copy.deepcopy(base)
            for li,(x,y) in enumerate(zip(iso.layers,blind.layers)):
                pos_=st['prefix'];i=x.keys[:,:,pos_].float();b=y.keys[:,:,pos_].float();delta=b-i;mean=delta.mean(2,keepdim=True)
                mats={'isolated':i,'blind':b,'common':i+mean,'centered':i+delta-mean,'both':b,
                      'norm':i*b.norm(dim=-1,keepdim=True)/i.norm(dim=-1,keepdim=True).clamp_min(1e-8),'negative_common':i-mean}
                if frozen is not None:mats['shared_frame']=i+frozen[li]
                for k,m in mats.items():variants[k].layers[li].keys[:,:,pos_]=m.to(x.keys.dtype)
                errs.append(float((variants['both'].layers[li].keys[:,:,pos_]-y.keys[:,:,pos_]).float().abs().max()))
                actual=variants['common'].layers[li].keys[:,:,pos_].float()-i
                rounding.append(float((actual-mean).square().mean().sqrt()))
                q=state['q'][li];actual=actual.repeat_interleave(q.shape[1]//actual.shape[1],dim=1)
                logits=q@actual.transpose(-1,-2)/(q.shape[-1]**.5)
                spreads.append(float((logits.max(-1).values-logits.min(-1).values).max()))
            for k,c in variants.items():scores[k],att[k]=score(c,ctx,1,pl,st)
            errs.append(float(abs(scores['blind']-scores['both']).max()))
            scores['noop'],_=score(patch(base,base,st['prefix'],'key'),ctx,1,pl,st);errs.append(float(abs(scores['noop']-scores['D1Q1']).max()))
            for layout in (0,1):
                c,s,p=prefix(ctx,layout,instruction=True);scores[f'D{layout}Q{layout}.instruction'],_=score(c,ctx,layout,p,s)
                pieces=[]
                for source in (0,1):
                    ind=[j for j,q in enumerate(ctx['queries']) if q['source']==source]
                    sc=dict(ctx,demos=[x for x in ctx['demos'] if x['source']==source],queries=[ctx['queries'][j] for j in ind])
                    c,s,p=prefix(sc,layout);v,_=score(c,sc,layout,p,s);pieces.extend(zip(ind,map(float,v)))
                scores[f'D{layout}Q{layout}.single']=[v for _,v in sorted(pieces)]
            assert max(ferrs)==0 and state['mass_max']==0,(ferrs,state['mass_max'])
            f.write(json.dumps({'context':ci,'signs':[2*q['label']-1 for q in ctx['queries']],
                   'scores':{k:list(map(float,v)) for k,v in scores.items()},'attention':att})+'\n');f.flush()
            if ci%4==0:print(ci,round(time.time()-t0,1),flush=True)
    run={'args':vars(a),'seconds':time.time()-t0,'sanity_max_error':max(errs),'nonlabel_flip_feature_error_max':max(ferrs),
         'forbidden_attention_mass_max':state['mass_max'],'fixedQ_common_relative_logit_spread_max':max(spreads),
         'common_writeback_rms_max':max(rounding),'torch':torch.__version__,'transformers':transformers.__version__,
         'host':platform.node(),'gpu':torch.cuda.get_device_name(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'config_sha256':hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
         'frame_sha256':hashlib.sha256(Path(a.frame_source).read_bytes()).hexdigest() if a.frame_source else None,
         'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    assert max(errs)<=.1 and max(spreads)<=.02,run
    (dest/'run.json').write_text(json.dumps(run,indent=2));print(json.dumps(run),flush=True)

if __name__=='__main__':main()
