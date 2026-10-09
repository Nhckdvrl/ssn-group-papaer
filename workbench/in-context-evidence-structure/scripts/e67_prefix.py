"""Move the same source code between metadata and the answer prefix.

Labels, token counts, code counts, demonstration positions and answer positions
are invariant. Fully cross demonstration and query layout; patch native cache.
"""
import argparse
import copy
from collections import Counter
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
from e58_factorization import NAMES, make_contexts
from e59_mediation import patch

HEAD = 'Below are items and the labels that individual sources gave them. Labels have a prefix and an arbitrary final classification code.\n\n'
INSTRUCTION = 'Use only examples from the requested source; each source may use a different mapping.\n\n'
MARKER = 'Mark'


def fields(tok, example, ctx, layout):
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    code = NAMES[example['source'] ^ ctx['code_permutation']]
    tag, prefix = (code, MARKER) if layout == 0 else (MARKER, code)
    ids = enc(f'Item: {example["word"]}\nSource:')
    sites = {'source': len(ids)}
    ids += enc(' ' + NAMES[example['source']]) + enc('\nTag:')
    sites['tag'] = len(ids)
    ids += enc(' ' + tag) + enc('\nLabel:')
    sites['prediction'] = len(ids) - 1
    sites['prefix'] = len(ids)
    pref = enc(' ' + prefix)
    assert len(pref) == 1
    ids += pref
    return ids, sites, pref[0]


def encode(tok, ctx, labels, layout, instruction=False):
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    ids = enc(HEAD + (INSTRUCTION if instruction else ''))
    sites = {k: [] for k in ['source', 'tag', 'prediction', 'prefix', 'label']}
    for ex in ctx['demos']:
        block, st, _ = fields(tok, ex, ctx, layout)
        for k, p in st.items():
            sites[k].append(len(ids) + p)
        ids += block
        sites['label'].append(len(ids))
        label = enc(' ' + labels[ex['label']])
        assert len(label) == 1
        ids += label + enc('\n\n')
    return ids, sites


def query_batch(tok, ctx, qlayout, plen, prefix_present=True):
    parts = [fields(tok, q, ctx, qlayout) for q in ctx['queries']]
    seqs = [p[0] if prefix_present else p[0][:-1] for p in parts]
    width = max(map(len, seqs))
    ids = torch.zeros((len(seqs), width), dtype=torch.long, device='cuda')
    mask = torch.zeros((len(seqs), plen + width), dtype=torch.long, device='cuda')
    mask[:, :plen] = 1
    pos = torch.zeros_like(ids)
    for i, seq in enumerate(seqs):
        ids[i, -len(seq):] = torch.tensor(seq, device='cuda')
        mask[i, -len(seq):] = 1
        pos[i, -len(seq):] = torch.arange(plen, plen + len(seq), device='cuda')
    return ids, mask, pos, [p[2] for p in parts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--stage', choices=['discovery','confirmation'], required=True)
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--seed', type=int, required=True)
    a = ap.parse_args()
    torch.set_num_threads(6)
    torch.manual_seed(0)
    t0 = time.time()
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    contexts = make_contexts(a.stage,a.n,a.seed)
    rng=np.random.default_rng(a.seed+91117)
    for ctx in contexts:
        ctx['code_permutation']=int(rng.integers(2))
    labels=['yes','no'] if a.stage=='discovery' else ['toxic','safe']
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    tokens=[tok.encode(' '+v,add_special_tokens=False) for v in NAMES+[MARKER]+labels]
    assert all(len(v)==1 for v in tokens) and len({v[0] for v in tokens})==len(tokens)
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.bfloat16,
                                             device_map='cuda',attn_implementation='eager').eval()
    state={'on':False}
    for li, layer in enumerate(model.model.layers):
        def hook(layer_index):
            def h(module,args,kwargs,output):
                if state['on']:
                    probs=output[1]
                    weights=probs[...,state['label_sites']].float()
                    qmask=state['qmask'][:,None,:,None]
                    match=state['match'][:,None,None,:]
                    numerator=(weights*qmask*match).sum((1,2,3))
                    denominator=(weights*qmask).sum((1,2,3))
                    state['attention'][layer_index]={'requested_source':(numerator/denominator.clamp_min(1e-9)).cpu().tolist(),
                                                     'total_label_mass':denominator.cpu().tolist()}
                return output
            return h
        layer.self_attn.register_forward_hook(hook(li),with_kwargs=True)
    errors=[]

    def score(cache,ctx,qlayout,plen,label_sites,with_attention=True):
        ids,mask,pos,_=query_batch(tok,ctx,qlayout,plen)
        c=copy.deepcopy(cache)
        c.batch_repeat_interleave(len(ctx['queries']))
        state.update(on=with_attention, label_sites=label_sites,qmask=mask[:,plen:].float(),
                     match=torch.tensor([[q['source']==d['source'] for d in ctx['demos']] for q in ctx['queries']],device='cuda'),
                     attention={})
        logits=model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=c,
                     use_cache=True,logits_to_keep=1).logits[:,-1].float()
        state['on']=False
        label_ids=[t[0] for t in tokens[-2:]]
        return (logits[:,label_ids[1]]-logits[:,label_ids[0]]).cpu().numpy(),state['attention']

    def prefix_score(cache,ctx,qlayout,plen):
        ids,mask,pos,desired=query_batch(tok,ctx,qlayout,plen,False)
        c=copy.deepcopy(cache);c.batch_repeat_interleave(len(ctx['queries']))
        logits=model(input_ids=ids,attention_mask=mask,position_ids=pos,past_key_values=c,
                     use_cache=True,logits_to_keep=1).logits[:,-1].float()
        universe=[t[0] for t in tokens[:3]]
        lp=logits[:,universe].log_softmax(-1)
        choices=[universe.index(x) for x in desired]
        probs=lp.exp()[torch.arange(len(choices),device='cuda'),choices]
        correct=lp.argmax(-1)==torch.tensor(choices,device='cuda')
        return {'candidate_accuracy':correct.float().cpu().tolist(),'candidate_probability':probs.cpu().tolist()}

    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in contexts))
    with (dest/'behavior.jsonl').open('w') as f, torch.inference_mode():
        for ci,ctx in enumerate(contexts):
            state['on']=False
            caches={};sites={};sequences={}
            for d in (0,1):
                ids,st=encode(tok,ctx,labels,d)
                sequences[d]=ids;sites[d]=st
                caches[d]=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
            assert len(sequences[0])==len(sequences[1]) and sites[0]==sites[1]
            assert Counter(sequences[0])==Counter(sequences[1])
            plen=len(sequences[0]); st=sites[0]
            for q in ctx['queries']:
                a0,site0,_=fields(tok,q,ctx,0);a1,site1,_=fields(tok,q,ctx,1)
                assert len(a0)==len(a1) and Counter(a0)==Counter(a1) and site0==site1
            if ci==0:
                (dest/'layout.json').write_text(json.dumps({'prefix_length':plen,'sites':st,'D0':tok.decode(sequences[0]),'D1':tok.decode(sequences[1]),
                         'query0':tok.decode(fields(tok,ctx['queries'][0],ctx,0)[0]),'query1':tok.decode(fields(tok,ctx['queries'][0],ctx,1)[0])},indent=2))
            scores={};attn={};pref={}
            for d in (0,1):
                for q in (0,1):
                    key=f'D{d}Q{q}'
                    scores[key],attn[key]=score(caches[d],ctx,q,plen,st['label'])
                    pref[key]=prefix_score(caches[d],ctx,q,plen)
                    scores[key+'.noop'],_=score(caches[d],ctx,q,plen,st['label'],False)
                    errors.append(float(abs(scores[key]-scores[key+'.noop']).max()))
            for recipient,donor in [(0,1),(1,0)]:
                for channel in ('key','value','kv','full'):
                    c=copy.deepcopy(caches[donor]) if channel=='full' else patch(caches[recipient],caches[donor],st['label'],channel)
                    for q in (0,1):
                        key=f'D{recipient}Q{q}.label_{channel}'
                        scores[key],attn[key]=score(c,ctx,q,plen,st['label'])
                        if channel=='full':
                            errors.append(float(abs(scores[key]-scores[f'D{donor}Q{q}']).max()))
            for layout in (0,1):
                ids,st_ins=encode(tok,ctx,labels,layout,True)
                c=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
                scores[f'D{layout}Q{layout}.instruction'],_=score(c,ctx,layout,len(ids),st_ins['label'],False)
                single_scores=[]
                for source in (0,1):
                    indices=[j for j,q in enumerate(ctx['queries']) if q['source']==source]
                    sc=dict(ctx,demos=[x for x in ctx['demos'] if x['source']==source],queries=[ctx['queries'][j] for j in indices])
                    ids,sst=encode(tok,sc,labels,layout)
                    c=model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
                    s,_=score(c,sc,layout,len(ids),sst['label'],False)
                    single_scores.extend(zip(indices,map(float,s)))
                scores[f'D{layout}Q{layout}.single']=[v for _,v in sorted(single_scores)]
            f.write(json.dumps({'context':ci,'signs':[2*q['label']-1 for q in ctx['queries']],
                 'scores':{k:list(map(float,v)) for k,v in scores.items()},'attention':attn,'prefix':pref})+'\n');f.flush()
            if ci%4==0:print(ci,round(time.time()-t0,1),flush=True)
    run={'args':vars(a),'seconds':time.time()-t0,'sanity_max_error':max(errors),'torch':torch.__version__,'transformers':transformers.__version__,
         'host':platform.node(),'gpu':torch.cuda.get_device_name(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'config_sha256':hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
         'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    assert max(errors)<=.1,run
    (dest/'run.json').write_text(json.dumps(run,indent=2));print(json.dumps(run),flush=True)

if __name__=='__main__':main()
