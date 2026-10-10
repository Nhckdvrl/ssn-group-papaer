"""Native name-key and mapping-label interventions with crossed query cues."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from e71_relational import contexts, encode, fields, queries


def variants(c):
    out = {}
    for name,n,m in [('base',False,False),('N',True,False),('M',False,True),('NM',True,True)]:
        v = copy.deepcopy(c)
        if n:
            v['names'] = list(reversed(v['names']))
        if m:
            v['orientation'] ^= 1
            for d in v['demos']:
                d['label'] ^= 1
        out[name] = v
    return out


def hashes():
    names = ['e85_cue_paths.py','e71_relational.py','e58_factorization.py','e67_prefix.py']
    return {n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in names}


def patch_cache(base,name,mapping,sites,use_name,use_mapping):
    dst = copy.deepcopy(base)
    for b,n,m,d in zip(base.layers,name.layers,mapping.layers,dst.layers):
        if use_name:
            d.keys[:,:,sites['source'],:] = n.keys[:,:,sites['source'],:]
        if use_mapping:
            d.keys[:,:,sites['label'],:] = m.keys[:,:,sites['label'],:]
            d.values[:,:,sites['label'],:] = m.values[:,:,sites['label'],:]
        allowed_k = torch.zeros(b.keys.shape[-2],dtype=torch.bool,device=b.keys.device)
        allowed_v = allowed_k.clone()
        if use_name:
            allowed_k[sites['source']] = True
            assert torch.equal(d.keys[:,:,sites['source'],:],n.keys[:,:,sites['source'],:])
        if use_mapping:
            allowed_k[sites['label']] = True
            allowed_v[sites['label']] = True
            assert torch.equal(d.keys[:,:,sites['label'],:],m.keys[:,:,sites['label'],:])
            assert torch.equal(d.values[:,:,sites['label'],:],m.values[:,:,sites['label'],:])
        assert torch.equal(d.keys[:,:,~allowed_k,:],b.keys[:,:,~allowed_k,:])
        assert torch.equal(d.values[:,:,~allowed_v,:],b.values[:,:,~allowed_v,:])
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--n',type=int,default=32)
    ap.add_argument('--seed',type=int,default=85001)
    ap.add_argument('--preflight-only',action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    torch.set_num_threads(6)
    source_hashes = hashes()
    dest = Path(a.out)
    dest.mkdir(parents=True,exist_ok=True)
    ctxs = contexts('confirmation',a.n,a.seed)
    assert all(len(c['queries']) == 8 for c in ctxs)
    tok = AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    labels = ['toxic','safe']
    label_ids = [tok.encode(' '+x,add_special_tokens=False)[0] for x in labels]
    assert all(len(tok.encode(' '+x,add_special_tokens=False)) == 1
               for x in ctxs[0]['names']+ctxs[0]['codes']+labels+['Mark'])
    for c in ctxs:
        vv = variants(c)
        for layout in (0,1):
            seq = {name:encode(tok,v,labels,'linked',layout) for name,v in vv.items()}
            for name in seq:
                assert seq[name][1:] == seq['base'][1:]
                assert Counter(seq[name][0]) == Counter(seq['base'][0])
            st = seq['base'][1]
            assert len(set(st['source'])) == len(set(st['label'])) == 16
            assert not set(st['source']) & set(st['label'])
    preflight = dict(args=vars(a),source_hashes=source_hashes,layout_and_variant_checks='passed',n_contexts=len(ctxs))
    (dest/'preflight.json').write_text(json.dumps(preflight,indent=2))
    if a.preflight_only:
        print(json.dumps(preflight),flush=True)
        return
    torch.manual_seed(0)
    model = AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.float32,
                                                device_map='cuda',attn_implementation='eager').eval()
    errors = dict(noop=0.,full_forward=0.,row_sum=0.,masked_mass=0.)

    def error(name,value):
        errors[name] = max(errors[name],float(value))

    def prefix(c,layout,instruction=False):
        seq,st,_ = encode(tok,c,labels,'linked',layout,instruction)
        out = model(input_ids=torch.tensor([seq],device='cuda'),use_cache=True,logits_to_keep=1)
        return out.past_key_values,st,len(seq),seq

    def score(cache,c,layout,plen,audit=False):
        ids,mask,pos = queries(tok,c,'linked',layout,plen)
        cp = copy.deepcopy(cache)
        cp.batch_repeat_interleave(len(c['queries']))
        out = model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=cp,
                    use_cache=True,logits_to_keep=1,output_attentions=audit)
        z = out.logits[:,-1].float()
        if audit:
            width = ids.shape[1]
            causal = torch.arange(plen+width,device='cuda')[None,:] <= plen+torch.arange(width,device='cuda')[:,None]
            forbidden = ~(causal[None,None] & mask[:,None,None,:].bool())
            valid = mask[:,None,plen:].bool()
            for p in out.attentions:
                error('masked_mass',(p*forbidden*valid[...,None]).sum(-1).max())
                error('row_sum',((p.sum(-1)-1)*valid).abs().max())
        return (z[:,label_ids[1]]-z[:,label_ids[0]]).cpu().numpy()

    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in ctxs))
    with (dest/'behavior.jsonl').open('w') as stream,torch.inference_mode():
        for ci,c in enumerate(ctxs):
            vv,scores = variants(c),{}
            for layout in (0,1):
                caches,seqs,sites,lengths = {},{},{},{}
                for name,v in vv.items():
                    caches[name],sites[name],lengths[name],seqs[name] = prefix(v,layout)
                    key = f'D{layout}.full_{name}'
                    scores[key] = score(caches[name],c,layout,lengths[name],ci<2)
                    if ci<2:
                        for qi,q in enumerate(c['queries']):
                            full_ids = seqs[name]+fields(tok,q,c,'linked',layout)[0]
                            z = model(input_ids=torch.tensor([full_ids],device='cuda'),logits_to_keep=1).logits[0,-1].float()
                            error('full_forward',abs(float(z[label_ids[1]]-z[label_ids[0]])-scores[key][qi]))
                st,pl = sites['base'],lengths['base']
                assert all(sites[n] == st and lengths[n] == pl for n in vv)
                for name,n,m in [('name_K',True,False),('label_KV',False,True),('joint',True,True)]:
                    patched = patch_cache(caches['base'],caches['N'],caches['M'],st,n,m)
                    scores[f'D{layout}.{name}'] = score(patched,c,layout,pl,ci<2)
                noop = patch_cache(caches['base'],caches['base'],caches['base'],st,True,True)
                scores[f'D{layout}.noop'] = score(noop,c,layout,pl,ci<2)
                error('noop',abs(scores[f'D{layout}.noop']-scores[f'D{layout}.full_base']).max())
                cache,_,pl,_ = prefix(c,layout,True)
                scores[f'D{layout}.instruction'] = score(cache,c,layout,pl,ci<2)
            assert max(errors.values()) <= .01,errors
            assert errors['masked_mass'] <= 1e-7 and errors['row_sum'] <= 2e-5
            assert all(np.isfinite(v).all() for v in scores.values())
            stream.write(json.dumps(dict(context=ci,signs=[2*q['label']-1 for q in c['queries']],
                                         scores={k:list(map(float,v)) for k,v in scores.items()}))+'\n')
            stream.flush()
            if ci%4 == 0:
                print(json.dumps(dict(context=ci,elapsed_s=round(time.time()-t0,1),control=errors)),flush=True)
    assert hashes() == source_hashes
    run = dict(args=vars(a),seconds=time.time()-t0,control=errors,source_hashes=source_hashes,
               config_sha256=hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
               git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
               torch=torch.__version__,transformers=transformers.__version__,host=platform.node(),
               gpu=torch.cuda.get_device_name(),n_layers=len(model.model.layers),
               cache_slice_verification='Exact on every layer, context, intervention; other slices unchanged.')
    (dest/'run.json').write_text(json.dumps(run,indent=2))
    print(json.dumps(run),flush=True)


if __name__ == '__main__':
    main()
