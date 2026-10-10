"""Source-equivalent code aliases separate rule use from label-group use.

Balanced and segregated views preserve every item/source/class/order token.
Only alias assignment changes. All queries use valid aliases of their source.
"""
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
from e58_factorization import make_contexts
from e67_prefix import HEAD, INSTRUCTION
from e71_relational import fields, queries

SCOPE = ('Each source uses one classification rule. Its two codes are interchangeable '
         'identifiers, not different classification rules. The final class depends on '
         'the item and source, not on which of its codes is used.\n')
LABELS = ['toxic', 'safe']


def contexts(n, seed):
    ctxs = make_contexts('confirmation', n, seed)
    rng = np.random.default_rng(seed+860)
    for c in ctxs:
        c.update(names=['Alice', 'Bob'], codes=rng.permutation(['Left','Right','Up','Down']).tolist(),
                 alias_permutation=rng.integers(2,size=2).tolist())
        qs = []
        for seen in (False, True):
            for s in (0, 1):
                for k in (0, 1):
                    base = next(q for q in c['queries'] if q['source']==s and q['kind']==k)
                    ds = [d for d in c['demos'] if d['source']==s and d['kind']==k]
                    word = ds[int(rng.integers(4))]['word'] if seen else base['word']
                    for alias in (0, 1):
                        qs.append(dict(base,word=word,alias=alias,code=2*s+alias,seen=seen,
                                       matched=alias==(k^c['alias_permutation'][s])))
                    balanced = rng.permutation([0,0,1,1]) if not seen else None
                    if not seen:
                        for d,a in zip(ds,balanced):
                            d['balanced_code'] = 2*s+int(a)
                            d['segregated_code'] = 2*s+(k^c['alias_permutation'][s])
        c['queries'] = qs
        assert len(qs)==16
        demo_words = {d['word'] for d in c['demos']}
        assert all((q['word'] in demo_words)==q['seen'] for q in qs)
        for s in (0,1):
            for a in (0,1):
                for support in ('balanced','segregated'):
                    assert sum(d[support+'_code']==2*s+a for d in c['demos'])==4
                for k in (0,1):
                    assert sum(d['source']==s and d['kind']==k and d['balanced_code']==2*s+a for d in c['demos'])==2
    return ctxs


def encode(tok,c,support,layout,instruction=False):
    enc = lambda s:tok.encode(s,add_special_tokens=False)
    ownership = ''.join(f'Source {c["names"][s]} has codes {c["codes"][2*s]} and {c["codes"][2*s+1]}.\n'
                        for s in (0,1))
    ids = enc(HEAD+SCOPE+ownership+'\n'+(INSTRUCTION if instruction else ''))
    sites = {k:[] for k in ('source','tag','prefix','label')}
    for d in c['demos']:
        block,st = fields(tok,d,c,support,layout)
        for k,v in st.items():
            sites[k].append(len(ids)+v)
        ids += block
        sites['label'].append(len(ids))
        ids += enc(' '+LABELS[d['label']])+enc('\n\n')
    return ids,sites


def hashes():
    return {n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
            for n in ['e86_aliases.py','e58_factorization.py','e71_relational.py','e67_prefix.py']}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--n',type=int,default=16)
    ap.add_argument('--seed',type=int,default=86001)
    ap.add_argument('--preflight-only',action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    torch.set_num_threads(6)
    source_hashes = hashes()
    dest = Path(a.out)
    dest.mkdir(parents=True,exist_ok=True)
    ctxs = contexts(a.n,a.seed)
    tok = AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    tokens = [tok.encode(' '+x,add_special_tokens=False) for x in ctxs[0]['names']+ctxs[0]['codes']+LABELS+['Mark']]
    assert all(len(x)==1 for x in tokens) and len({x[0] for x in tokens})==len(tokens)
    for c in ctxs:
        for instruction in (False,True):
            seqs = [encode(tok,c,support,layout,instruction) for support in ('balanced','segregated') for layout in (0,1)]
            assert all(st==seqs[0][1] and len(ids)==len(seqs[0][0]) and Counter(ids)==Counter(seqs[0][0]) for ids,st in seqs)
    preflight = dict(args=vars(a),source_hashes=source_hashes,n_contexts=len(ctxs),
                     checks='scope, ownership, balanced counts, equal multisets/sites/lengths, unseen/seen passed')
    (dest/'preflight.json').write_text(json.dumps(preflight,indent=2))
    (dest/'example.json').write_text(json.dumps({support+str(layout):tok.decode(encode(tok,ctxs[0],support,layout)[0])
                                               for support in ('balanced','segregated') for layout in (0,1)},indent=2))
    if a.preflight_only:
        print(json.dumps(preflight),flush=True)
        return
    torch.manual_seed(0)
    model = AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.float32,
                                               device_map='cuda',attn_implementation='eager').eval()
    label_ids = [tok.encode(' '+x,add_special_tokens=False)[0] for x in LABELS]
    errors = dict(noop=0.,full_forward=0.,row_sum=0.,masked_mass=0.)
    def error(name,value):
        errors[name] = max(errors[name],float(value))
    def score(cache,c,layout,plen,audit):
        ids,mask,pos = queries(tok,c,'balanced',layout,plen)
        cp = copy.deepcopy(cache)
        cp.batch_repeat_interleave(16)
        out = model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=cp,
                    use_cache=True,logits_to_keep=1,output_attentions=audit)
        z = out.logits[:,-1].float()
        if audit:
            causal = torch.arange(plen+ids.shape[1],device='cuda')[None,:] <= plen+torch.arange(ids.shape[1],device='cuda')[:,None]
            forbidden = ~(causal[None,None]&mask[:,None,None,:].bool())
            valid = mask[:,None,plen:].bool()
            for p in out.attentions:
                error('masked_mass',(p*forbidden*valid[...,None]).sum(-1).max())
                error('row_sum',((p.sum(-1)-1)*valid).abs().max())
        return (z[:,label_ids[1]]-z[:,label_ids[0]]).cpu().numpy()
    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in ctxs))
    with (dest/'behavior.jsonl').open('w') as stream,torch.inference_mode():
        for ci,c in enumerate(ctxs):
            scores = {}
            for support in ('balanced','segregated'):
                for layout in (0,1):
                    for instruction in (False,True):
                        seq,sites = encode(tok,c,support,layout,instruction)
                        cache = model(input_ids=torch.tensor([seq],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
                        key = f'{support}.D{layout}.'+('instruction' if instruction else 'native')
                        scores[key] = score(cache,c,layout,len(seq),ci<2)
                        if ci<2:
                            error('noop',np.abs(scores[key]-score(copy.deepcopy(cache),c,layout,len(seq),False)).max())
                            for qi,q in enumerate(c['queries']):
                                full = seq+fields(tok,q,c,support,layout)[0]
                                z = model(input_ids=torch.tensor([full],device='cuda'),logits_to_keep=1).logits[0,-1].float()
                                error('full_forward',abs(float(z[label_ids[1]]-z[label_ids[0]])-scores[key][qi]))
            assert max(errors.values())<=.01 and errors['masked_mass']<=1e-7 and errors['row_sum']<=2e-5,errors
            assert len(scores)==8 and all(np.isfinite(v).all() for v in scores.values())
            stream.write(json.dumps(dict(context=ci,scores={k:list(map(float,v)) for k,v in scores.items()},
                                         signs=[2*q['label']-1 for q in c['queries']],
                                         matched=[q['matched'] for q in c['queries']]))+'\n')
            stream.flush()
            if ci%4==0:
                print(json.dumps(dict(context=ci,elapsed_s=round(time.time()-t0,1),control=errors)),flush=True)
    assert hashes()==source_hashes
    run = dict(args=vars(a),seconds=time.time()-t0,control=errors,source_hashes=source_hashes,
               config_sha256=hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
               git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
               torch=torch.__version__,transformers=transformers.__version__,host=platform.node(),gpu=torch.cuda.get_device_name())
    (dest/'run.json').write_text(json.dumps(run,indent=2))
    print(json.dumps(run),flush=True)


if __name__=='__main__':
    main()
