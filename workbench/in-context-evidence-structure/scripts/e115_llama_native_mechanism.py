"""E115: frozen E114 mechanism test in the Llama family.
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


def analyze(dest):
    from e109_reconstruction_audit import summarize
    rows=[json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    run=json.loads((dest/'run.json').read_text());assert len(rows)==run['args']['n']
    z={k:np.array([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    gold=np.array([r['gold'] for r in rows]);out={'n_contexts':len(rows),'metrics':{},'rule_dependence':{},'contrasts':{},'reconstruction':{},'relation':{}}
    for k in z:
        out['metrics'][k]={'accuracy':interval(((z[k]>0)==(gold>0)).mean(1)),
            'argmax_accuracy':interval([np.mean(r['conditions'][k]['argmax_correct']) for r in rows]),
            'argmax_label_rate':interval([np.mean(r['conditions'][k]['argmax_is_label']) for r in rows])}
    ds={}
    for suffix in ['f0r0','f0r1','f1r0','f1r1','label_r0','label_r1','edge_k_r0','edge_k_r1','edge_kv_r0','edge_kv_r1','edge_v_r0','edge_v_r1','gate_shared','gate_label','gate_edge_k']:
        ds[suffix]=((z['cross_'+suffix]-z['origin_'+suffix])*gold).mean(1)
        out['rule_dependence'][suffix]={'signed':interval(ds[suffix]),'absolute':interval(abs(ds[suffix]))}
    for name,left,right in [('A_formation_B_shared','f0r0','f1r0'),('A_formation_B_far','f0r1','f1r1'),
        ('B_reading_A_shared','f0r0','f0r1'),('B_reading_A_far','f1r0','f1r1'),('total_namespace','f0r0','f1r1'),
        ('label_effect_B_shared','f0r0','label_r0'),('label_effect_B_far','f0r1','label_r1'),
        ('edge_K_B_shared','f0r0','edge_k_r0'),('edge_K_B_far','f0r1','edge_k_r1')]:
        out['contrasts'][name]={'absolute_rule_effect':interval(abs(ds[left])-abs(ds[right])),
            'signed_rule_effect':interval(ds[left]-ds[right])}
    out['contrasts']['stage_interaction']={'absolute_rule_effect':interval(abs(ds['f1r1'])-abs(ds['f1r0'])-abs(ds['f0r1'])+abs(ds['f0r0'])),
        'signed_rule_effect':interval(ds['f1r1']-ds['f1r0']-ds['f0r1']+ds['f0r0'])}
    # Fixed coefficient one; all channels and both B reading backgrounds reported.
    for r in [0,1]:
        base=np.stack([z[w+f'_f0r{r}'] for w in ['origin','cross']],1)
        for target_name,target_suffix in [('label_interface',f'label_r{r}'),('all_A_formation',f'f1r{r}')]:
            target=np.stack([z[w+'_'+target_suffix] for w in ['origin','cross']],1)-base
            for kind in ['k','kv','v']:
                pred=np.stack([z[w+f'_edge_{kind}_r{r}'] for w in ['origin','cross']],1)-base
                out['reconstruction'][f'{target_name}_B{r}_{kind}']={'coefficient':1,'fit':False,
                    'raw':summarize(target,pred),'rule_double_contrast':summarize(target[:,1]-target[:,0],pred[:,1]-pred[:,0])}
    rb=z['origin_f0r0'];ef={k:((z[k]-rb)*gold).mean(1) for k in z}
    for name,l,r in [('full_native','cross_f0r0','within_native'),('label_native','relation_label_cross_native','relation_label_within_native'),
        ('answer_native','relation_answer_cross_kv_native','relation_answer_within_kv_native')]:
        out['relation'][name]={'absolute_effect':interval(abs(ef[l])-abs(ef[r])),'signed_effect':interval(ef[l]-ef[r])}
    for name,l,r in [('cross_KV_minus_K','relation_answer_cross_kv_native','relation_answer_cross_k_native'),
        ('cross_KV_minus_V','relation_answer_cross_kv_native','relation_answer_cross_v_native')]:
        out['relation'][name]={'absolute_effect':interval(abs(ef[l])-abs(ef[r])),'signed_effect':interval(ef[l]-ef[r])}
    for k in ['relation_f0r1','relation_f1r0','relation_label_cross_native','relation_answer_cross_kv_native','relation_answer_cross_k_native','relation_answer_cross_v_native']:
        out['relation'][k]={'absolute_effect':interval(abs(ef[k])),'signed_effect':interval(ef[k])}
    cs=[json.loads(x) for x in (dest/'contexts.jsonl').read_text().splitlines()]
    out['single_source_by_polarity']={str(p):interval(((z['single_A'][np.array([c['reverse']==p for c in cs])]>0)==(gold[np.array([c['reverse']==p for c in cs])]>0)).mean(1)) for p in [False,True]}
    (dest/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
    for k,v in out['contrasts'].items():print(k,v['absolute_rule_effect'],flush=True)
    for k in ['full_native','label_native','answer_native']:print('relation',k,out['relation'][k],flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/tmp/ices_models/Llama-3.1-8B")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed", type=int, default=114001)
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

    from collections import defaultdict
    positive=['excellent','great','wonderful','superb','pleasant','delicious','fantastic','lovely','tasty','delightful']
    negative=['terrible','poor','awful','horrible','unpleasant','disgusting','dreadful','bad','nasty','disappointing']
    templates=['The food was {a}.','The meal was {a}.','The food was absolutely {a}.',
       'The meal was truly {a}.','My dinner was {a}.','Our lunch was {a}.',
       'The soup was {a}.','The dessert was {a}.','The food tasted {a}.','The meal tasted absolutely {a}.']
    if args.materials=='validation':
        positive=['good','amazing','enjoyable','splendid','satisfying','impressive','outstanding','exceptional','magnificent','incredible']
        negative=['abysmal','lousy','appalling','unsatisfactory','atrocious','unacceptable','pathetic','miserable','disastrous','displeasing']
        templates=['The dish was {a}.','The dinner was {a}.','The lunch was really {a}.',
            'The sandwich was simply {a}.','This salad was {a}.','Our breakfast was {a}.',
            'The pizza was {a}.','The experience was {a}.','The dish tasted {a}.','The dinner tasted remarkably {a}.']
    pool=[[t.format(a=a) for t in templates for a in words] for words in [positive,negative]]
    bins=[defaultdict(list),defaultdict(list)]
    for kind,items in enumerate(pool):
        for text in items:
            block=f"Comment: {text}\nAnnotator: Alex\nLabel:"
            annotation=tok(block,add_special_tokens=False,return_offsets_mapping=True)
            left=len('Comment: ');right=left+len(text)
            positions=tuple(i for i,(a,b) in enumerate(annotation['offset_mapping']) if a<right and b>left)
            # Equal total lengths alone do not hold boundary tokenization
            # fixed (some words share a token with the following newline).
            outside=tuple((i,t) for i,t in enumerate(annotation['input_ids']) if i not in positions)
            signature=(len(annotation['input_ids']),positions,outside)
            bins[kind][signature].append(text)
    valid=sorted(k for k in bins[0] if min(len(bins[0][k]),len(bins[1][k]))>=2)
    assert len(valid)>=2
    cs=[]
    for ci in range(args.n):
        B=[];cross_map={};within_map={}
        signatures=[valid[int(i)] for i in rng.choice(len(valid),2,replace=False)]
        lengths=[k[0] for k in signatures]
        for signature in signatures:
            race=rng.choice(bins[0][signature],2,replace=False).tolist()
            gender=rng.choice(bins[1][signature],2,replace=False).tolist()
            q=race+gender;c=gender+race;w=[race[1],race[0],gender[1],gender[0]]
            for i,t in enumerate(q):
                B.append((t,1,int(i>=2)));cross_map[t]=c[i];within_map[t]=w[i]
        used={t for t,_,_ in B};A=[];queries=[]
        for kind,items in enumerate(pool):
            available=[t for t in items if t not in used]
            drawn=rng.choice(available,8,replace=False).tolist()
            A.extend((t,0,int(kind==0)) for t in drawn[:4])
            queries.extend((t,'positive' if kind==0 else 'negative') for t in drawn[4:])
        reverse=bool(ci%2)
        demos=[(A+B)[i] for i in rng.permutation(16)]
        if reverse:demos=[(t,r,1-y) for t,r,y in demos]
        names=rng.permutation(['Alex','Sam']).tolist()
        cs.append({'demos':demos,'shown':[names[r] for _,r,_ in demos],'names':names,'q':queries,
                   'reverse':reverse,'cross_map':cross_map,'within_map':within_map,'quartet_lengths':lengths})

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
        e={w:prefix(ctx,w) for w in ['origin','cross','within']}
        ref,roles,anchors,binputs=e['origin']
        for ids,r,a,bi in e.values():
            assert len(ids)==len(ref) and r==roles and a==anchors and bi==binputs, {
                'context':len(encoded),'lengths':[len(ref),len(ids)],
                'roles_same':r==roles,'anchors_same':a==anchors,'content_indices_same':bi==binputs,
                'index_symmetric_difference':sorted(set(bi)^set(binputs))[:12]}
            assert {i for i,(x,y) in enumerate(zip(ids,ref)) if x!=y}<=set(binputs)
            assert all(ids[a]==ref[a] for a in anchors)
        original=[t for t,r,y in ctx['demos'] if r==1]
        assert sorted(original)==sorted(ctx['cross_map'].values())==sorted(ctx['within_map'].values())
        assert all(ctx['cross_map'][t]!=t and ctx['within_map'][t]!=t for t in original)
        encoded.append(e)
    preflight={'args':vars(args),'word_ids':word_ids,'prefix_lengths':[len(e['origin'][0]) for e in encoded],
               'label_source_positions_and_tokens_fixed':True,'B_input_multiset_fixed':True,'all_8_B_inputs_reassigned':True,
               'only_B_comment_content_changes':True,'source_rule_changes_only_cross':True,
               'synthetic_polarity_lexicon':{'positive':positive,'negative':negative,'templates':templates},'valid_quartet_length_bins':len(valid),'quartet_lengths':[c['quartet_lengths'] for c in cs],
               'reversed_contexts':sum(c['reverse'] for c in cs),'planned_conditions':43,'planned_scores_per_context':344,'patch_scope':'B answer messages at A label formation; native full-source query with independent A/B cached-state crossing'}
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
            for world in ['origin','cross','within']:
                stats[world]={}
                caches[world]=prefill(encoded[ci][world][0],receivers=labels,senders=b_labels,stats=stats[world])
            sc,cc,wc=caches['origin'],caches['cross'],caches['within']
            for world in ['origin','cross']:
                fi,fr,fa,fb=prefix(ctx,world,namespace='far')
                assert fr==roles and fa==anchors and len(fi)==len(si)
                caches['far_'+world]=prefill(fi)
            for donor in [cc,wc]:
                for t in ['keys','values']:
                    diff=float((getattr(sc.layers[0],t)[...,answer,:]-getattr(donor.layers[0],t)[...,answer,:]).abs().max())
                    layer0_errors.append(diff);assert diff==0,diff
            def finger(cache):
                hh=hashlib.sha256()
                for layer in cache.layers:
                    for v in (layer.keys,layer.values):hh.update(v.cpu().numpy().tobytes())
                return hh.hexdigest()
            hashes={w:finger(c) for w,c in caches.items()}
            conditions={}
            bindices=[i for i,r in enumerate(roles) if r==1]
            for world in ['origin','cross']:
                base=caches[world];donor=caches['far_'+world]
                bfar=patch(base,donor,roles,'kv',bindices)
                conditions[world+'_f0r0']=query(base,roles,qs)
                conditions[world+'_f0r1']=query(bfar,roles,qs)
                conditions[world+'_f1r0']=query(patch(base,donor,roles,'kv'),roles,qs)
                conditions[world+'_f1r1']=query(patch(bfar,donor,roles,'kv'),roles,qs)
                # Complete reconstructed corner must match the native far run.
                far_native=query(donor,roles,qs)
                er=max(abs(x-y) for x,y in zip(far_native['z'],conditions[world+'_f1r1']['z']))
                errors.append(er);assert er<=.001,er
                for r,bc in [(0,base),(1,bfar)]:
                    conditions[world+f'_label_r{r}']=query(patch(bc,donor,roles,'kv',labels),roles,qs)
                conditions[world+'_gate_shared']=query(base,roles,qs,True)
                conditions[world+'_gate_label']=query(patch(base,donor,roles,'kv',labels),roles,qs,True)
                for kind in ['k','kv','v']:
                    mode=world+'_namespace_edge_'+kind
                    mc=prefill(encoded[ci][world][0],donor=donor,receivers=labels,senders=answer,kind=kind,mode=mode)
                    for r,bc in [(0,base),(1,bfar)]:
                        conditions[world+f'_edge_{kind}_r{r}']=query(patch(bc,mc,roles,'kv',labels),roles,qs)
                    if kind=='k':conditions[world+'_gate_edge_k']=query(patch(base,mc,roles,'kv',labels),roles,qs,True)
            conditions['within_native']=query(wc,roles,qs)
            conditions['relation_label_cross_native']=query(patch(sc,cc,roles,'kv',labels),roles,qs)
            conditions['relation_label_within_native']=query(patch(sc,wc,roles,'kv',labels),roles,qs)
            conditions['relation_f0r1']=query(patch(sc,cc,roles,'kv',bindices),roles,qs)
            conditions['relation_f1r0']=query(patch(sc,cc,roles,'kv'),roles,qs)
            for mode,donor,kind in [('relation_answer_cross_kv_native',cc,'kv'),('relation_answer_cross_k_native',cc,'k'),('relation_answer_cross_v_native',cc,'v'),('relation_answer_within_kv_native',wc,'kv')]:
                mc=prefill(si,donor=donor,receivers=labels,senders=answer,kind=kind,mode=mode)
                conditions[mode]=query(patch(sc,mc,roles,'kv',labels),roles,qs)
            if ci==0:
                self_cache=prefill(si,donor=sc,receivers=labels,senders=answer,kind='kv',mode='self')
                se=max(float((getattr(a,t)-getattr(b,t)).abs().max()) for a,b in zip(sc.layers,self_cache.layers) for t in ['keys','values'])
                self_errors.append(se);assert se<=.001,se
                selfq=query(patch(sc,self_cache,roles,'kv',labels),roles,qs)
                self_errors.append(max(abs(x-y) for x,y in zip(selfq['z'],conditions['origin_f0r0']['z'])))
                # Verify all native cached query scores against full-token forward.
                for qi,q in enumerate(qs):
                    direct=model(input_ids=torch.tensor([si+q],device='cuda'),use_cache=False,logits_to_keep=1).logits[0,-1].float()
                    dz=float(direct[label_ids[1]]-direct[label_ids[0]])
                    errors.append(abs(dz-conditions['origin_f0r0']['z'][qi]))
                assert max(errors)<=.001,errors
                assert max(self_errors)<=.001,self_errors
            own_ids=enc(HEAD);own_roles=[-1]*len(own_ids)
            for (text,role,y),name in zip(ctx['demos'],ctx['shown']):
                if role!=0:continue
                block=enc(f"Comment: {text}\nAnnotator: {name}\nLabel:")+enc(' '+WORDS['shared'][y])+enc('\n\n')
                own_ids+=block;own_roles+=[0]*len(block)
            conditions['single_A']=query(prefill(own_ids),own_roles,qs)
            for world in ['origin','cross','within']:
                ids,ir,_,_=prefix(ctx,world,instruction=True)
                conditions[world+'_instruction']=query(prefill(ids),ir,qs)
            assert all(finger(caches[w])==hashes[w] for w in caches)
            for v in conditions.values():v['argmax_correct']=[t==label_ids[int(g>0)] for t,g in zip(v['argmax_token'],gold)]
            assert len(conditions)==43, list(conditions)
            stream.write(json.dumps({'context':ci,'gold':gold,'conditions':conditions,'native_formation_attention':stats})+'\n');stream.flush()
            print(ci+1,'/',args.n,'numeric',max(errors),'self',max(self_errors),flush=True)
    elapsed = time.time()-started
    run = {"args":vars(args),"numeric_max_error":max(errors),"elapsed_seconds":elapsed,"gpu_hours":elapsed/3600,
           "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "contexts_sha256":hashlib.sha256((dest/"contexts.jsonl").read_bytes()).hexdigest(),
           "python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,
           "git_head":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
           "sender_layer0_KV_max_error":max(layer0_errors),"model_revision":({"qwen3":"b968826d9c46dd6066d109eabc6255188de91218","mistral":"caa1feb0e54d415e2df31207e5f4e273e33509b1","llama":"1f47e50cdbe801ad8a5174156ec3a0655108fb9f"}[model.config.model_type]),"dtype":"float32","attention":"eager",
           "model_type":model.config.model_type,"training":False,"patch_layers":"all","edge_calls":covered,"edge_self_max_error":max(self_errors),"self_edge_cache_checked":True,"pristine_source_cache_exact":True,"primary_query_scope":"native all prefix positions; gated controls at all query positions","native_crossing":"A cached evidence formation x B cached reading environment"}
    (dest/"run.json").write_text(json.dumps(run,indent=2)+"\n")
    analyze(dest)


if __name__=="__main__":
    main()
