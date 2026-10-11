"""E118: criterion identity versus shared sentiment gain under independent output conventions.
Uses E91 namespace task and CTA-style causal path isolation.
"""
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np

from e56_query_adapter import HEAD, contexts, pools

WORDS = {"shared": ["no", "yes"], "far": ["pass", "flag"]}


def interval(values):
    v = np.asarray(values, dtype=float)
    draws = np.random.default_rng(910).integers(len(v), size=(10000, len(v)))
    return {"mean": float(v.mean()), "ci95": np.quantile(v[draws].mean(1), [.025, .975]).tolist(),
            "n_contexts": len(v)}


WORLDS = ['origin', 'service_negative', 'food_positive', 'food_negative']


def analyze(dest):
    from e109_reconstruction_audit import summarize
    rows=[json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    cs=[json.loads(x) for x in (dest/'contexts.jsonl').read_text().splitlines()]
    f=np.array([r['gold'] for r in rows]);ss=np.array([c['service_gold'] for c in cs])
    p=np.array([-1 if c['reverse'] else 1 for c in cs])[:,None]
    assert np.all(f.sum(1)==0) and np.all(ss.sum(1)==0) and np.all((f*ss).sum(1)==0)
    z={k:np.array([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    assert len(z)==33 and len(rows)==json.loads((dest/'run.json').read_text())['args']['n']
    features={k:{'bias':(v*p).mean(1),'food':(v*f).mean(1),'service':(v*ss).mean(1),
                 'food_service':(v*f*ss*p).mean(1)} for k,v in z.items()}
    out={'n_contexts':len(rows),'feature_responses':{k:{t:interval(x) for t,x in v.items()} for k,v in features.items()},
         'accuracy':{},'code_effects':{},'criterion_feature_alignment':{},'reconstruction':{},'within_control':{}}
    for k,v in z.items():
        g=f
        if k.startswith('single_B_'):
            w=k[len('single_B_'):];g=(ss if w.startswith('service') or w=='origin' else f)*(-1 if w.endswith('negative') else 1)
        out['accuracy'][k]=interval(((v>0)==(g>0)).mean(1))
    for mode in ['native','gate','label','label_gate','edge','edge_gate','far_label']:
        def condition(w):
            if w=='origin' and mode not in ['native','gate','far_label']:
                return 'origin_'+('gate' if mode.endswith('gate') else 'native')
            return w+'_'+mode
        effects={}
        for task,positive,negative in [('service','origin','service_negative'),('food','food_positive','food_negative')]:
            effects[task]={t:.5*(features[condition(positive)][t]-features[condition(negative)][t]) for t in ['bias','food','service','food_service']}
        out['code_effects'][mode]={task:{t:interval(x) for t,x in v.items()} for task,v in effects.items()}
        aligned=.5*(effects['food']['food']-effects['food']['service']+effects['service']['service']-effects['service']['food'])
        out['criterion_feature_alignment'][mode]=interval(aligned)
    for mode in ['native','gate']:
        base=z['origin_'+mode]
        target=np.stack([z[w+'_'+('label_gate' if mode=='gate' else 'label')]-base for w in WORLDS[1:]],1)
        pred=np.stack([z[w+'_'+('edge_gate' if mode=='gate' else 'edge')]-base for w in WORLDS[1:]],1)
        out['reconstruction'][mode]={'coefficient':1,'fit':False,'raw':summarize(target,pred)}
    for mode in ['label','edge']:
        out['within_control'][mode]={t:interval(features['within_'+mode][t]-features['origin_native'][t]) for t in ['bias','food','service','food_service']}
    # Whole four-point response and all channels retained, no fitted feature probe.
    out['single_A_by_polarity']={str(reverse):interval(((z['single_A'][np.array([c['reverse']==reverse for c in cs])]>0)==(f[np.array([c['reverse']==reverse for c in cs])]>0)).mean(1)) for reverse in [False,True]}
    (dest/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
    print('criterion-feature alignment',out['criterion_feature_alignment'],flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/tmp/ices_models/Llama-3.1-8B")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed", type=int, default=118001)
    ap.add_argument("--materials", choices=['discovery','validation'], default='discovery')
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--analyze-only", action="store_true")
    args = ap.parse_args()
    dest = Path(args.out)
    if args.analyze_only:
        analyze(dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    assert not (dest / "behavior.jsonl").exists()
    rng = np.random.default_rng(args.seed)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda t: tok.encode(t, add_special_tokens=False)
    word_ids = {k: [enc(" "+w) for w in v] for k, v in WORDS.items()}
    assert all(len(i) == 1 for pair in word_ids.values() for i in pair)
    label_ids = [x[0] for x in word_ids["shared"]]

    from itertools import product
    positive=['excellent','great','wonderful','superb','pleasant','fantastic','lovely','delightful']
    negative=['terrible','poor','awful','horrible','unpleasant','dreadful','bad','disappointing']
    templates=['The food was {f}, and the service was {s}.',
               'The food was {f}; the service was {s}.',
               'The food was {f}, while the service was {s}.']
    if args.materials=='validation':
        positive=['good','amazing','enjoyable','splendid','satisfying','impressive','outstanding','exceptional']
        negative=['abysmal','lousy','appalling','unsatisfactory','atrocious','unacceptable','pathetic','miserable']
        templates=['The food seemed {f}, and the service seemed {s}.',
                   'The food was really {f}; the service was really {s}.',
                   'Overall, the food was {f}, whereas the service was {s}.']
    # Four cells share lexical instantiations. Shape matching is entirely CPU,
    # before any outputs, and holds non-comment tokens/boundaries fixed.
    from collections import defaultdict
    variants=[];all_by_template=defaultdict(list)
    for template,p,n in product(templates,positive,negative):
        cells={(f,g):template.format(f=p if f else n,s=p if g else n) for f,g in product([0,1],repeat=2)}
        all_by_template[template].append(cells)
        sigs=[]
        for text in cells.values():
            block=f"Comment: {text}\nAnnotator: Alex\nLabel:"
            annotation=tok(block,add_special_tokens=False,return_offsets_mapping=True)
            left=len('Comment: ');right=left+len(text)
            pos=tuple(i for i,(a,b) in enumerate(annotation['offset_mapping']) if a<right and b>left)
            outside=tuple((i,t) for i,t in enumerate(annotation['input_ids']) if i not in pos)
            sigs.append((len(annotation['input_ids']),pos,outside))
        if len(set(sigs))==1:variants.append((sigs[0],template,cells))
    from collections import defaultdict
    bins=defaultdict(list)
    for sig,template,cells in variants:bins[(sig,template)].append(cells)
    valid=[sig for sig,v in bins.items() if len(v)>=4]
    assert valid
    cs=[]
    for ci in range(args.n):
        key=valid[int(rng.integers(len(valid)))];sig,template=key;v=bins[key]
        pairs=[(i,j) for i in range(len(v)) for j in range(i+1,len(v)) if not set(v[i].values()).intersection(v[j].values())]
        assert pairs
        chosen=pairs[int(rng.integers(len(pairs)))];bvars=[v[j] for j in chosen]
        used=set(t for cells in bvars for t in cells.values());rest=[]
        for j in rng.permutation(len(all_by_template[template])):
            cells=all_by_template[template][j]
            if used.intersection(cells.values()):continue
            rest.append(cells);used.update(cells.values())
            if len(rest)==4:break
        assert len(rest)==4,'Insufficient disjoint lexical variants in CPU pool'
        avars=rest[:2];qvars=rest[2:]

        B=[];cross_map={};within_map={};service_negative_map={};food_negative_map={}
        for j,cells in enumerate(bvars):
            for (f,g),text in cells.items():
                B.append((text,1,g))
                cross_map[text]=cells[(g,f)]
                service_negative_map[text]=cells[(f,1-g)]
                food_negative_map[text]=cells[(1-g,f)]
                within_map[text]=bvars[1-j][(f,g)]
        # Different lexical variants can share concordant strings; ensure the
        # four changed discordant inputs are distinct before choosing a sample.
        discordant=[cells[k] for cells in bvars for k in [(0,1),(1,0)]]
        assert len(set(discordant))==4
        A=[(cells[(f,g)],0,f) for cells in avars for f,g in product([0,1],repeat=2)]
        q=[(cells[(f,g)],'positive' if f else 'negative') for cells in qvars for f,g in product([0,1],repeat=2)]
        raw_s=[1 if g else -1 for cells in qvars for f,g in product([0,1],repeat=2)]
        assert len(set(t for t,k in q))==8
        assert not set(t for t,k in q).intersection(t for t,r,y in A+B)
        reverse=bool(ci%2);demos=[(A+B)[j] for j in rng.permutation(16)]
        if reverse:demos=[(t,r,1-y) for t,r,y in demos]
        names=rng.permutation(['Alex','Sam']).tolist()
        cs.append({'demos':demos,'shown':[names[r] for _,r,y in demos],'names':names,'q':q,
                   'reverse':reverse,'food_positive_map':cross_map,'service_negative_map':service_negative_map,'food_negative_map':food_negative_map,'within_map':within_map,'quartet_lengths':[sig[0]],
                   'service_gold':[(-1 if reverse else 1)*g for g in raw_s],
                   'criterion':'A food fixed; B criterion food/service x private convention same/opposite A'})

    def prefix(ctx, world, instruction=False, namespace="shared"):
        assert namespace in WORDS
        head = HEAD
        if instruction:
            head += "Use only the examples of the requested annotator to infer and apply that annotator's labeling rule.\n\n"
        ids = enc(head); roles = [-1]*len(ids); anchors = []; input_idx=[]
        for (text, role, y), name in zip(ctx["demos"], ctx["shown"]):
            if role==1 and world!='origin':text=ctx[world+'_map'][text]
            block_text=f"Comment: {text}\nAnnotator: {name}\nLabel:"
            block=enc(block_text)
            annotated=tok(block_text,add_special_tokens=False,return_offsets_mapping=True)
            assert annotated['input_ids']==block
            if role==1:
                left=len('Comment: ');right=left+len(text)
                input_idx += [len(ids)+i for i,(a,b) in enumerate(annotated['offset_mapping']) if a<right and b>left]
            anchors.append(len(ids)+len(block))
            block += enc(" "+WORDS[namespace if role==1 else "shared"][y])+enc("\n\n")
            ids += block; roles += [role]*len(block)
        return ids, roles, anchors, input_idx

    encoded=[]
    for ctx in cs:
        e={w:prefix(ctx,w) for w in WORLDS+['within']}
        ref,roles,anchors,binputs=e['origin']
        for ids,r,a,bi in e.values():
            assert len(ids)==len(ref) and r==roles and a==anchors and bi==binputs, {
                'context':len(encoded),'lengths':[len(ref),len(ids)],
                'roles_same':r==roles,'anchors_same':a==anchors,'content_indices_same':bi==binputs,
                'index_symmetric_difference':sorted(set(bi)^set(binputs))[:12]}
            assert {i for i,(x,y) in enumerate(zip(ids,ref)) if x!=y}<=set(binputs)
            assert all(ids[a]==ref[a] for a in anchors)
        original=[t for t,r,y in ctx['demos'] if r==1]
        assert len(set(original))==8
        for world in WORLDS[1:]+['within']:
            assert sorted(original)==sorted(ctx[world+'_map'][t] for t in original)
        assert sum(ctx['service_negative_map'][t]!=t for t in original)==8
        assert sum(ctx['within_map'][t]!=t for t in original)==8
        encoded.append(e)
    preflight={'args':vars(args),'word_ids':word_ids,'prefix_lengths':[len(e['origin'][0]) for e in encoded],
               'label_source_positions_and_tokens_fixed':True,'B_input_multiset_fixed':True,'B_code_and_within_change_same_8_positions':True,
               'only_B_comment_content_changes':True,'B_criterion_and_private_convention_independently_crossed':True,
               'synthetic_polarity_lexicon':{'positive':positive,'negative':negative,'templates':templates},'valid_quartet_length_bins':len(valid),'quartet_lengths':[c['quartet_lengths'] for c in cs],
               'reversed_contexts':sum(c['reverse'] for c in cs),'planned_conditions':33,'planned_scores_per_context':264,'patch_scope':'B criterion x private convention; A label caches and historical answer KV in fixed recipient'}
    (dest / "preflight.json").write_text(json.dumps(preflight, indent=2)+"\n")
    (dest / "contexts.jsonl").write_text("".join(json.dumps(c)+"\n" for c in cs))
    if args.preflight_only:
        print("All namespace/rule pairs aligned; A tokens invariant.", flush=True)
        return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    started = time.time()
    print("Loading model", flush=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
        dtype=torch.float32, device_map="cuda", attn_implementation="eager").eval()
    model.requires_grad_(False)
    print("Model loaded", flush=True)

    if model.config.model_type == "qwen3":
        from transformers.models.qwen3 import modeling_qwen3 as mq
    elif model.config.model_type == "mistral":
        from transformers.models.mistral import modeling_mistral as mq
    elif model.config.model_type == "llama":
        from transformers.models.llama import modeling_llama as mq
    else:
        raise ValueError(model.config.model_type)
    native_eager=mq.eager_attention_forward
    active={'donor':None,'receivers':None,'senders':None,'kind':None,'mode':None,'stats':None,'ids':None}
    covered={i:{} for i in range(len(model.model.layers))};self_errors=[]
    def edge_eager(module,query,key,value,attention_mask,scaling,dropout=0.0,**kwargs):
        out,weights=native_eager(module,query,key,value,attention_mask,scaling,dropout,**kwargs)
        receivers=active['receivers']
        if active['stats'] is not None:
            aidx=receivers;bidx=active['senders'];ids=active['ids']
            cube=weights[0,:,aidx,:][:,:,bidx]
            same=torch.tensor([[ids[a]==ids[b] for b in bidx] for a in aidx],device=query.device)
            avail=torch.tensor([[b<a for b in bidx] for a in aidx],device=query.device)
            # Each receiver's past foreign-label mass. Native weights and the
            # available counts are saved separately; no after-the-fact head choice.
            active['stats'][module.layer_idx]={
                'mass':cube.sum((0,2)).cpu().tolist(),
                'same_label_mass':(cube*same[None]).sum((0,2)).cpu().tolist(),
                'past_same_label_count':(avail&same).sum(1).cpu().tolist(),
                'past_other_label_count':(avail&~same).sum(1).cpu().tolist()}
        if active['donor'] is None:return out,weights
        assert query.shape[0]==1 and query.shape[-2]==key.shape[-2]
        sender=active['senders'];src=active['donor'].layers[module.layer_idx]
        kk,vv=key,value
        if 'k' in active['kind']:
            kk=key.clone();kk[...,sender,:]=src.keys[...,sender,:]
        if 'v' in active['kind']:
            vv=value.clone();vv[...,sender,:]=src.values[...,sender,:]
        # Keep native GEMM geometry. Computing only eight receiver rows caused
        # a measurable FP32 self-interchange drift after many layers.
        alt,aw=native_eager(module,query,kk,vv,attention_mask,scaling,dropout,**kwargs)
        out=out.clone();out[:,receivers]=alt[:,receivers]
        weights=weights.clone();weights[:,:,receivers,:]=aw[:,:,receivers,:]
        d=covered[module.layer_idx];mode=active['mode'];d[mode]=d.get(mode,0)+1
        return out,weights
    mq.eager_attention_forward=edge_eager
    def prefill(ids,donor=None,receivers=None,senders=None,kind=None,mode=None,stats=None):
        active.update(donor=donor,receivers=receivers,senders=senders,kind=kind,mode=mode,stats=stats,ids=ids)
        try:return model(input_ids=torch.tensor([ids],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
        finally:active.update(donor=None,receivers=None,senders=None,kind=None,mode=None,stats=None,ids=None)

    def query(cache, roles, queries, gate=False):
        plen, n, qlen = len(roles), len(queries), max(map(len,queries))
        ids = torch.zeros((n,qlen), dtype=torch.long, device="cuda")
        pos = torch.zeros_like(ids); live = torch.zeros_like(ids, dtype=torch.bool)
        for i, q in enumerate(queries):
            ids[i,-len(q):] = torch.tensor(q,device="cuda")
            pos[i,-len(q):] = torch.arange(plen,plen+len(q),device="cuda")
            live[i,-len(q):] = True
        keep = torch.ones(plen,dtype=torch.bool,device="cuda")
        if gate:
            keep = torch.tensor(roles,device="cuda") != 1
        allowed = torch.cat([keep[None,None].expand(n,qlen,-1),
                             live[:,None].expand(-1,qlen,-1) & torch.ones((qlen,qlen),dtype=torch.bool,device="cuda").tril()[None]],dim=-1)
        mask = torch.zeros(allowed.shape,dtype=torch.float32,device="cuda")
        mask.masked_fill_(~allowed,float("-inf"))
        cp = copy.deepcopy(cache); cp.batch_repeat_interleave(n)
        lo = model(input_ids=ids,position_ids=pos,attention_mask=mask[:,None],
                   past_key_values=cp,use_cache=True,logits_to_keep=1).logits[:,-1].float()
        top = lo.argmax(-1)
        return {"z":(lo[:,label_ids[1]]-lo[:,label_ids[0]]).cpu().tolist(),
                "argmax_token":top.cpu().tolist(),
                "argmax_is_label":((top==label_ids[0])|(top==label_ids[1])).cpu().tolist()}

    def patch(base, donor, roles, kind, scope=None):
        cp = copy.deepcopy(base)
        idx = [i for i,r in enumerate(roles) if r==0] if scope is None else scope
        assert base.get_seq_length() == donor.get_seq_length()
        for dst, src in zip(cp.layers,donor.layers):
            if "k" in kind:
                dst.keys[...,idx,:] = src.keys[...,idx,:]
            if "v" in kind:
                dst.values[...,idx,:] = src.values[...,idx,:]
        return cp

    errors=[];layer0_errors=[]
    with torch.inference_mode(),(dest/'behavior.jsonl').open('w') as stream:
        for ci,ctx in enumerate(cs):
            qs=[enc(f"Comment: {t}\nAnnotator: {ctx['names'][0]}\nLabel:") for t,_ in ctx['q']]
            gold=[(-1 if ctx['reverse'] else 1)*(1 if k=='positive' else -1) for _,k in ctx['q']]
            si,roles,anchors,binputs=encoded[ci]['origin']
            labels=[a for a,d in zip(anchors,ctx['demos']) if d[1]==0]
            answer=[i for a,d in zip(anchors,ctx['demos']) if d[1]==1 for i in range(a,a+1+len(enc('\n\n')))]
            b_labels=[a for a,d in zip(anchors,ctx['demos']) if d[1]==1]
            caches={};stats={}
            for world in WORLDS+['within']:
                stats[world]={}
                caches[world]=prefill(encoded[ci][world][0],receivers=labels,senders=b_labels,stats=stats[world])
            sc=caches['origin']
            for world in WORLDS:
                fi,fr,fa,fb=prefix(ctx,world,namespace='far')
                assert fr==roles and fa==anchors and len(fi)==len(si)
                caches['far_'+world]=prefill(fi)
            for world in WORLDS[1:]+['within']:
                for t in ['keys','values']:
                    diff=float((getattr(sc.layers[0],t)[...,answer,:]-getattr(caches[world].layers[0],t)[...,answer,:]).abs().max())
                    layer0_errors.append(diff);assert diff==0,diff
            def finger(cache):
                hh=hashlib.sha256()
                for layer in cache.layers:
                    for v in (layer.keys,layer.values):hh.update(v.cpu().numpy().tobytes())
                return hh.hexdigest()
            hashes={w:finger(c) for w,c in caches.items()}
            conditions={}
            for world in WORLDS:
                donor=caches[world]
                conditions[world+'_native']=query(donor,roles,qs)
                conditions[world+'_gate']=query(donor,roles,qs,True)
                conditions[world+'_far_label']=query(patch(sc,caches['far_'+world],roles,'kv',labels),roles,qs)
                if world=='origin':continue
                formed=patch(sc,donor,roles,'kv',labels)
                conditions[world+'_label']=query(formed,roles,qs)
                conditions[world+'_label_gate']=query(formed,roles,qs,True)
                mc=prefill(si,donor=donor,receivers=labels,senders=answer,kind='kv',mode=world+'_edge')
                formed_edge=patch(sc,mc,roles,'kv',labels)
                conditions[world+'_edge']=query(formed_edge,roles,qs)
                conditions[world+'_edge_gate']=query(formed_edge,roles,qs,True)
            conditions['within_label']=query(patch(sc,caches['within'],roles,'kv',labels),roles,qs)
            mc=prefill(si,donor=caches['within'],receivers=labels,senders=answer,kind='kv',mode='within_edge')
            conditions['within_edge']=query(patch(sc,mc,roles,'kv',labels),roles,qs)
            if ci==0:
                self_cache=prefill(si,donor=sc,receivers=labels,senders=answer,kind='kv',mode='self')
                se=max(float((getattr(a,t)-getattr(b,t)).abs().max()) for a,b in zip(sc.layers,self_cache.layers) for t in ['keys','values'])
                self_errors.append(se);assert se<=.001,se
                selfq=query(patch(sc,self_cache,roles,'kv',labels),roles,qs)
                self_errors.append(max(abs(x-y) for x,y in zip(selfq['z'],conditions['origin_native']['z'])))
                # Verify all native cached query scores against full-token forward.
                for qi,q in enumerate(qs):
                    direct=model(input_ids=torch.tensor([si+q],device='cuda'),use_cache=False,logits_to_keep=1).logits[0,-1].float()
                    dz=float(direct[label_ids[1]]-direct[label_ids[0]])
                    errors.append(abs(dz-conditions['origin_native']['z'][qi]))
                assert max(errors)<=.001,errors
                assert max(self_errors)<=.001,self_errors
            own_ids=enc(HEAD);own_roles=[-1]*len(own_ids)
            for (text,role,y),name in zip(ctx['demos'],ctx['shown']):
                if role!=0:continue
                block=enc(f"Comment: {text}\nAnnotator: {name}\nLabel:")+enc(' '+WORDS['shared'][y])+enc('\n\n')
                own_ids+=block;own_roles+=[0]*len(block)
            conditions['single_A']=query(prefill(own_ids),own_roles,qs)
            bqs=[enc(f"Comment: {t}\nAnnotator: {ctx['names'][1]}\nLabel:") for t,_ in ctx['q']]
            for world in WORLDS:
                bids=enc(HEAD);broles=[-1]*len(bids)
                for (text,role,y),name in zip(ctx['demos'],ctx['shown']):
                    if role!=1:continue
                    if world!='origin':text=ctx[world+'_map'][text]
                    block=enc(f"Comment: {text}\nAnnotator: {name}\nLabel:")+enc(' '+WORDS['shared'][y])+enc('\n\n')
                    bids+=block;broles+=[1]*len(block)
                conditions['single_B_'+world]=query(prefill(bids),broles,bqs)
            for actor,aspect,qq in [(0,'food',qs)]:
                posword=WORDS['shared'][int(not ctx['reverse'])];negword=WORDS['shared'][int(ctx['reverse'])]
                other='service' if actor==0 else 'food'
                hint=(f"Annotator {ctx['names'][actor]} labels comments by the quality of the {aspect}. "
                      f"Use {posword} if the {aspect} is positive and {negword} if it is negative. "
                      f"Ignore the quality of the {other}.\n\n")
                hh=enc(hint)
                conditions['direct_'+('A' if actor==0 else 'B')]=query(prefill(hh),[-1]*len(hh),qq)
            for world in ['origin']:
                ids,ir,_,_=prefix(ctx,world,instruction=True)
                conditions[world+'_instruction']=query(prefill(ids),ir,qs)
            assert all(finger(caches[w])==hashes[w] for w in caches)
            for k,v in conditions.items():
                gg=gold
                if k.startswith('single_B_'):
                    w=k[len('single_B_'):];gg=ctx['service_gold'] if w.startswith('service') or w=='origin' else gold
                    if w.endswith('negative'):gg=[-x for x in gg]
                v['argmax_correct']=[t==label_ids[int(g>0)] for t,g in zip(v['argmax_token'],gg)]
            assert len(conditions)==33, list(conditions)
            stream.write(json.dumps({'context':ci,'gold':gold,'conditions':conditions,'native_formation_attention':stats})+'\n');stream.flush()
            print(ci+1,'/',args.n,'numeric',max(errors),'self',max(self_errors),flush=True)
    elapsed = time.time()-started
    run = {"args":vars(args),"numeric_max_error":max(errors),"elapsed_seconds":elapsed,"gpu_hours":elapsed/3600,
           "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "contexts_sha256":hashlib.sha256((dest/"contexts.jsonl").read_bytes()).hexdigest(),
           "python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,
           "git_head":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
           "sender_layer0_KV_max_error":max(layer0_errors),"model_revision":({"qwen3":"b968826d9c46dd6066d109eabc6255188de91218","mistral":"caa1feb0e54d415e2df31207e5f4e273e33509b1","llama":"1f47e50cdbe801ad8a5174156ec3a0655108fb9f"}[model.config.model_type]),"dtype":"float32","attention":"eager",
           "model_type":model.config.model_type,"training":False,"patch_layers":"all","edge_calls":covered,"edge_self_max_error":max(self_errors),"self_edge_cache_checked":True,"pristine_source_cache_exact":True,"primary_query_scope":"native all prefix positions; gated controls at all query positions","native_crossing":"B criterion x B private convention; A label-cache formation in fixed recipient"}
    (dest/"run.json").write_text(json.dumps(run,indent=2)+"\n")
    analyze(dest)


if __name__=="__main__":
    main()
