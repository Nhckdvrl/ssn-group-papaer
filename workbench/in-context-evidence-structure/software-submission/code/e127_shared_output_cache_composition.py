"""E127: equivalent-context cache composition in shared and separate output spaces.

All public facts are unchanged. Only row ordering differs; no fitting or search.
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
from e56_query_adapter import HEAD
from e118_criterion_code_feature_crossing import interval
from e121_sst_materials import make_contexts
from e123_natural_source_function_policy import truth
WORLDS=['origin','cross']
WORDSETS={'shared':[['no','yes'],['no','yes']], 'far':[['no','yes'],['pass','flag']]}
NAMESPACES=['shared','far']
PAIRS=['00','11','01','10']
SCOPES=['joint','own']


def analyze(dest):
    rows=[json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    cs=[json.loads(x) for x in (dest/'contexts.jsonl').read_text().splitlines()]
    out={'n_contexts':len(rows),'primary':'shared/opposite world coherent-minus-mixed full-vocabulary accuracy',
        'conditions':{},'cache_accuracy':{},'contrasts':{},'B_code_response':{},
        'functional_source_readout':{},'functional_source_readout_contrasts':{}}
    arrays={};functional_arrays={}
    for key in rows[0]['conditions']:
        vals=[r['conditions'][key] for r in rows]
        z=np.asarray([v['z'] for v in vals]);gold=np.asarray([v['gold'] for v in vals])
        out['conditions'][key]={'full_accuracy':interval([np.mean(v['argmax_correct']) for v in vals]),
            'candidate_accuracy':interval(((z>0)==(gold>0)).mean(1)),
            'in_requested_word_set':interval([np.mean(v['argmax_is_label']) for v in vals]),
            'other_word_rate':interval([np.mean(v['other_source_word']) for v in vals]),
            'source_from_word_identifiable':all(v['source_from_word_identifiable'] for v in vals),
            'correct_margin':interval((z*gold).mean(1))}
    for namespace in NAMESPACES:
        for pair in PAIRS:
            for scope in SCOPES:
                key=f'{namespace}_cache{pair}_{scope}'
                def collect(field):
                    return np.asarray([[[r['conditions'][f'{w}_{key}_{o}'][field]
                        for o in [0,1]] for w in WORLDS] for r in rows],dtype=float)
                full=collect('argmax_correct');z=collect('z');gold=collect('gold')
                cand=(z>0)==(gold>0);words=collect('argmax_is_label');other=collect('other_source_word')
                metrics={'both':full.mean((1,2,3)),'A':full[:,:,0].mean((1,2)),
                    'B':full[:,:,1].mean((1,2)),'opposite':full[:,0].mean((1,2)),
                    'same':full[:,1].mean((1,2)),'candidate':cand.mean((1,2,3)),
                    'in_word_set':words.mean((1,2,3)),'other_word':other.mean((1,2,3)),
                    'margin':(z*gold).mean((1,2,3))}
                arrays[key]=metrics
                out['cache_accuracy'][key]={k:interval(v) for k,v in metrics.items()}
                if namespace=='far':
                    ll=collect('label_logits')
                    assert ll.shape==(*z.shape,4)
                    mass=np.logaddexp(ll[...,0],ll[...,1])-np.logaddexp(ll[...,2],ll[...,3])
                    specific=.5*(mass[:,:,0]-mass[:,:,1])
                    common=.5*(mass[:,:,0]+mass[:,:,1])
                    functional_arrays[key]={'source_specific':specific.mean((1,2)),
                        'source_common':common.mean((1,2)),
                        'source_common_absolute':abs(common).mean((1,2))}
                    readout_scope='both worlds; A-word-set minus B-word-set logsumexp'
                else:
                    ll=collect('label_logits')
                    assert ll.shape==(*z.shape,2)
                    assert np.max(abs(ll[...,1]-ll[...,0]-z))<.001
                    specific=.5*(z[:,0,0]-z[:,0,1])*gold[:,0,0]
                    common=.5*(z[:,0,0]+z[:,0,1])*gold[:,0,0]
                    functional_arrays[key]={'source_specific':specific.mean(1),
                        'source_common':common.mean(1),
                        'source_common_absolute':abs(common).mean(1)}
                    readout_scope='opposite world only; A-gold-directed shared-code logits'
                out['functional_source_readout'][key]={
                    'scope':readout_scope,
                    'metrics':{m:interval(v) for m,v in functional_arrays[key].items()}}
                response=(.5*(z[:,1,0]-z[:,0,0])*gold[:,0,0]).mean(1)
                out['B_code_response'][key]={'signed':interval(response),'absolute':interval(abs(response))}
        for scope in SCOPES:
            out['contrasts'][namespace+'_'+scope+'_coherent_minus_mixed']={m:interval(.5*(arrays[namespace+'_cache00_'+scope][m]
                +arrays[namespace+'_cache11_'+scope][m]-arrays[namespace+'_cache01_'+scope][m]-arrays[namespace+'_cache10_'+scope][m]))
                for m in arrays[namespace+'_cache00_'+scope]}
            out['contrasts'][namespace+'_'+scope+'_order11_minus_00']={m:interval(arrays[namespace+'_cache11_'+scope][m]-arrays[namespace+'_cache00_'+scope][m])
                for m in arrays[namespace+'_cache00_'+scope]}
            out['functional_source_readout_contrasts'][namespace+'_'+scope+'_coherent_minus_mixed']={m:interval(.5*(
                functional_arrays[namespace+'_cache00_'+scope][m]+functional_arrays[namespace+'_cache11_'+scope][m]
                -functional_arrays[namespace+'_cache01_'+scope][m]-functional_arrays[namespace+'_cache10_'+scope][m]))
                for m in functional_arrays[namespace+'_cache00_'+scope]}
        for pair in PAIRS:
            out['contrasts'][namespace+'_'+pair+'_joint_minus_own']={m:interval(arrays[namespace+'_cache'+pair+'_joint'][m]-arrays[namespace+'_cache'+pair+'_own'][m])
                for m in arrays[namespace+'_cache'+pair+'_own']}
        assert abs(out['contrasts'][namespace+'_own_coherent_minus_mixed']['both']['mean'])<1e-10
    out['contrasts']['shared_minus_far_joint_coherence']={m:interval(.5*(
        arrays['shared_cache00_joint'][m]+arrays['shared_cache11_joint'][m]-arrays['shared_cache01_joint'][m]-arrays['shared_cache10_joint'][m]
        -arrays['far_cache00_joint'][m]-arrays['far_cache11_joint'][m]+arrays['far_cache01_joint'][m]+arrays['far_cache10_joint'][m]))
        for m in arrays['shared_cache00_joint']}
    for direction in [False,True]:
        ix=np.asarray([c['reverse']==direction for c in cs])
        out.setdefault('private_directions',{})[str(direction)]={k:{m:interval(v[ix]) for m,v in metrics.items()}
            for k,metrics in arrays.items()}
    primary=.5*(arrays['shared_cache00_joint']['opposite']+arrays['shared_cache11_joint']['opposite']
        -arrays['shared_cache01_joint']['opposite']-arrays['shared_cache10_joint']['opposite'])
    out['primary_result']=interval(primary)
    out['primary_private_directions']={str(direction):interval(primary[[c['reverse']==direction for c in cs]]) for direction in [False,True]}
    (dest/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'n':len(rows),'primary':out['primary_result'],'namespace_coherence':{ns:out['contrasts'][ns+'_joint_coherent_minus_mixed'] for ns in NAMESPACES}}),flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--n',type=int,default=16);ap.add_argument('--seed',type=int,default=127001)
    ap.add_argument('--materials',choices=['discovery','validation'],default='discovery')
    ap.add_argument('--preflight-only',action='store_true');ap.add_argument('--analyze-only',action='store_true')
    args=ap.parse_args();dest=Path(args.out)
    if args.analyze_only:analyze(dest);return
    dest.mkdir(parents=True,exist_ok=True)
    assert not (dest/'behavior.jsonl').exists()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
    enc=lambda x:tok.encode(x,add_special_tokens=False)
    cs,material_meta=make_contexts(tok,args.n,args.seed,args.materials)
    source_pair=['Alex','Sam'] if args.materials=='discovery' else ['Robin','Jordan']
    for ctx in cs:
        ctx['names']=[source_pair[0 if n=='Alex' else 1] for n in ctx['names']]
        ctx['shown']=[ctx['names'][owner] for _,owner,_ in ctx['demos']]
        names=sorted(source_pair)
        def schema(ordered,namespace):
            return 'Output words:\n'+''.join(name+': '+', '.join(WORDSETS[namespace][ctx['names'].index(name)])+'.\n'
                for name in ordered)+'\n'
        ctx['schema_texts']={ns:[schema(names,ns),schema(names[::-1],ns)] for ns in NAMESPACES}
        assert len({len(enc(x)) for xx in ctx['schema_texts'].values() for x in xx})==1
    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    word_ids_by_namespace={ns:[[enc(' '+w)[0] for w in ww] for ww in sets] for ns,sets in WORDSETS.items()}
    assert all(len(enc(' '+w))==1 for sets in WORDSETS.values() for ww in sets for w in ww)
    assert len(set(sum(word_ids_by_namespace['shared'],[])))==2
    assert len(set(sum(word_ids_by_namespace['far'],[])))==4
    label_ids_by_namespace={ns:list(dict.fromkeys(sum(ids,[]))) for ns,ids in word_ids_by_namespace.items()}
    def prefix(ctx,world,namespace,order=None,single=None,instruction=False):
        header=HEAD+("Use only the examples of the requested annotator to infer and apply that annotator's labeling rule.\n\n" if instruction else '')
        ids=enc(header);roles=[-1]*len(ids)
        if order is not None:
            piece=enc(ctx['schema_texts'][namespace][order]);ids.extend(piece);roles.extend([-2]*len(piece))
        for (comment,owner,y),name in zip(ctx['demos'],ctx['shown']):
            if single is not None and owner!=single:continue
            if owner==1 and world=='cross':comment=ctx['cross_map'][comment]
            block=enc(f'Comment: {comment}\nAnnotator: {name}\nLabel:')
            answer=enc(' '+WORDSETS[namespace][owner][y])+enc('\n\n')
            ids.extend(block+answer);roles.extend([owner]*(len(block)+len(answer)))
        return ids,roles
    data=[{(ns,w,o):prefix(c,w,ns,o) for ns in NAMESPACES for w in WORLDS for o in [0,1]} for c in cs]
    for worlds in data:
        ids0,roles0=worlds['shared','origin',0]
        for (namespace,world,order),(ids,roles) in worlds.items():
            assert len(ids)==len(ids0) and roles==roles0
            assert all(ids[i]==ids0[i] for i,r in enumerate(roles) if r not in [-2,1])
            other,_=worlds[namespace,world,0]
            assert all(ids[i]==other[i] for i,r in enumerate(roles) if r!=-2)
    preflight={'args':vars(args),'conditions':86,'queries':8,'source_names':source_pair,'word_ids_by_namespace':word_ids_by_namespace,
        'label_logit_ids_by_namespace':label_ids_by_namespace,
        'auxiliary_readout':'source-specific difference and source-common signed/absolute components; far both-world set mass, shared opposite-world gold-directed code',
        'same_public_facts':True,'matched_schema_token_count':True,'original_global_positions':True,
        'cross_source_private_formation':False,'formation_access_public_schema':True,
        'whole_query_public_schema_access':False,'cache_pairs':PAIRS,'query_scopes':SCOPES,'namespaces':NAMESPACES,'source_word_identity_only_far':True,
        'source_ownership_roles':{'public_HEAD':-1,'schema':-2,'A':0,'B':1},
        'natural_materials':material_meta,
        'material_builder_sha256':hashlib.sha256(Path(__file__).with_name('e121_sst_materials.py').read_bytes()).hexdigest(),
        'prefix_lengths':[len(x['shared','origin',0][0]) for x in data],
        'scope':'whole-source cache composition under equivalent schema orders; not identification of binding IDs'}
    (dest/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    if args.preflight_only:
        print('E127 shared/far facts, global geometry, word-set identifiability and source aliases passed.',flush=True);return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6);torch.manual_seed(0);started=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,dtype=torch.float32,
        device_map='cuda',attn_implementation='eager').eval();model.requires_grad_(False)
    numeric,self_errors,graph_zero,composition_errors,consumption,query_consumption=[],[],[],[],{},{}
    def prefix_allowed(roles, independent, formation):
        rr=torch.tensor(roles,device='cuda')
        allowed=torch.ones((len(roles),len(roles)),dtype=torch.bool,device='cuda').tril()
        if independent:
            for owner in [0,1]:
                allowed &= ~((rr[:,None]==owner)&(rr[None,:]==1-owner))
        if not formation:
            allowed &= ~((rr[:,None]>=0)&(rr[None,:]==-2))
        assert allowed.diag().all()
        return allowed

    def prefill(encoded, independent=True, formation=True, record=None):
        ids,roles=encoded
        allowed=prefix_allowed(roles,independent,formation)
        mask=torch.zeros((1,1,len(ids),len(ids)),dtype=torch.float32,device='cuda').masked_fill_(~allowed,float('-inf'))
        handles=[]
        if record is not None:
            def hook(module, aa, kw):
                assert kw['attention_mask'].shape==mask.shape and torch.equal(kw['attention_mask'],mask)
                k=module.layer_idx
                record[k]=record.get(k,0)+1
            handles=[layer.self_attn.register_forward_pre_hook(hook,with_kwargs=True) for layer in model.model.layers]
        try:
            cache=model(input_ids=torch.tensor([ids],device='cuda'),attention_mask=mask,
                use_cache=True,logits_to_keep=1).past_key_values
        finally:
            for handle in handles:handle.remove()
        return cache

    def query(cache, roles, queries, owner, reading=True, own_only=False, record=None):
        plen,n,qlen=len(roles),len(queries),max(map(len,queries))
        ids=torch.zeros((n,qlen),dtype=torch.long,device='cuda')
        positions=torch.zeros_like(ids)
        live=torch.zeros_like(ids,dtype=torch.bool)
        for i,q in enumerate(queries):
            ids[i,-len(q):]=torch.tensor(q,device='cuda')
            positions[i,-len(q):]=torch.arange(plen,plen+len(q),device='cuda')
            live[i,-len(q):]=True
        keep=torch.ones(plen,dtype=torch.bool,device='cuda')
        role=torch.tensor(roles,device='cuda')
        if not reading:keep &= role!=-2
        if own_only:keep &= role!=1-owner
        allowed=torch.cat([keep[None,None].expand(n,qlen,-1),
            live[:,None].expand(-1,qlen,-1)&torch.ones((qlen,qlen),dtype=torch.bool,device='cuda').tril()[None]],-1)
        mask=torch.zeros(allowed.shape,dtype=torch.float32,device='cuda').masked_fill_(~allowed,float('-inf'))
        cp=copy.deepcopy(cache)
        assert all(a.keys.data_ptr()!=b.keys.data_ptr() and a.values.data_ptr()!=b.values.data_ptr()
            for a,b in zip(cp.layers,cache.layers))
        cp.batch_repeat_interleave(n)
        actual_mask=mask[:,None]
        handles=[]
        if record is not None:
            def hook(module, aa, kw):
                assert kw['attention_mask'].shape==actual_mask.shape and torch.equal(kw['attention_mask'],actual_mask)
                k=module.layer_idx
                record[k]=record.get(k,0)+1
            handles=[layer.self_attn.register_forward_pre_hook(hook,with_kwargs=True) for layer in model.model.layers]
        try:
            logits=model(input_ids=ids,position_ids=positions,attention_mask=actual_mask,past_key_values=cp,
                use_cache=True,logits_to_keep=1).logits[:,-1].float()
        finally:
            for handle in handles:handle.remove()
        assert cache.get_seq_length()==plen
        outids=word_ids[owner]
        top=logits.argmax(-1)
        return {'z':(logits[:,outids[1]]-logits[:,outids[0]]).cpu().tolist(),
            'label_logits':logits[:,label_ids_by_namespace[namespace]].cpu().tolist(),
            'argmax_token':top.cpu().tolist(), 'argmax_is_label':((top==outids[0])|(top==outids[1])).cpu().tolist(),
            'other_source_word':(((top==word_ids[1-owner][0])|(top==word_ids[1-owner][1])) & (namespace=='far')).cpu().tolist(),
            'source_from_word_identifiable':namespace=='far'}


    with torch.inference_mode(),(dest/'behavior.jsonl').open('w') as stream:
        for ci,ctx in enumerate(cs):
            queries={owner:[enc(f"Comment: {t}\nAnnotator: {ctx['names'][owner]}\nLabel:") for t,_ in ctx['q']] for owner in [0,1]}
            conditions={};a_reference={}
            def score(name,cache,roles,world,owner,scope='joint'):
                v=query(cache,roles,queries[owner],owner,False,scope=='own',record=query_consumption.setdefault(name,{}))
                v['gold']=truth(ctx,world,owner)
                v['argmax_correct']=[t==word_ids[owner][int(g>0)] for t,g in zip(v['argmax_token'],v['gold'])]
                conditions[name]=v
            for namespace in NAMESPACES:
                word_ids=word_ids_by_namespace[namespace]
                a_reference={}
                for world in WORLDS:
                    caches={o:prefill(data[ci][namespace,world,o],record=consumption.setdefault(f'{namespace}_{world}_order{o}',{})) for o in [0,1]}
                    roles=data[ci][namespace,world,0][1];owner_masks={o:torch.tensor(roles,device='cuda')==o for o in [0,1]}
                    for order in [0,1]:
                        if world=='origin':
                            a_reference[order]=[[getattr(l,k)[:,:,owner_masks[0]].clone() for k in ['keys','values']] for l in caches[order].layers]
                        else:
                            graph_zero.append(max(float((getattr(l,k)[:,:,owner_masks[0]]-a_reference[order][li][ki]).abs().max())
                                for li,l in enumerate(caches[order].layers) for ki,k in enumerate(['keys','values'])))
                    for pair in PAIRS:
                        cp=copy.deepcopy(caches[0])
                        assert all(a.keys.data_ptr()!=b.keys.data_ptr() and a.values.data_ptr()!=b.values.data_ptr()
                            for a,b in zip(cp.layers,caches[0].layers))
                        for owner in [0,1]:
                            donor=caches[int(pair[owner])]
                            for target,source in zip(cp.layers,donor.layers):
                                for k in ['keys','values']:
                                    getattr(target,k)[:,:,owner_masks[owner]]=getattr(source,k)[:,:,owner_masks[owner]]
                        for scope in SCOPES:
                            for owner in [0,1]:score(f'{world}_{namespace}_cache{pair}_{scope}_{owner}',cp,roles,world,owner,scope)
                        if pair in ['00','11']:
                            for scope in SCOPES:
                                for owner in [0,1]:
                                    original=query(caches[int(pair[0])],roles,queries[owner],owner,False,scope=='own')
                                    got=conditions[f'{world}_{namespace}_cache{pair}_{scope}_{owner}']
                                    composition_errors.append(max(abs(a-b) for a,b in zip(got['z'],original['z'])))
                                    assert got['argmax_token']==original['argmax_token']
                        del cp
                    for pair in ['01','10']:
                        for owner in [0,1]:
                            got=conditions[f'{world}_{namespace}_cache{pair}_own_{owner}']
                            target=conditions[f'{world}_{namespace}_cache{pair[owner]*2}_own_{owner}']
                            composition_errors.append(max(abs(a-b) for a,b in zip(got['z'],target['z'])))
                            assert got['argmax_token']==target['argmax_token']
                    if ci==0:
                        for order in [0,1]:
                            encoded=data[ci][namespace,world,order];q=queries[0][0];plen=len(encoded[0]);length=plen+len(q)
                            for scope in SCOPES:
                                allowed=torch.zeros((length,length),dtype=torch.bool,device='cuda')
                                allowed[:plen,:plen]=prefix_allowed(roles,True,True)
                                keep=torch.tensor(roles,device='cuda')!=-2
                                if scope=='own':keep &= torch.tensor(roles,device='cuda')!=1
                                allowed[plen:,:plen]=keep[None]
                                allowed[plen:,plen:]=torch.ones((len(q),len(q)),device='cuda',dtype=torch.bool).tril()
                                mask=torch.zeros((1,1,length,length),device='cuda',dtype=torch.float32).masked_fill_(~allowed,float('-inf'))
                                logits=model(input_ids=torch.tensor([encoded[0]+q],device='cuda'),attention_mask=mask,
                                    use_cache=False,logits_to_keep=1).logits[0,-1]
                                expected=float(logits[word_ids[0][1]]-logits[word_ids[0][0]])
                                numeric.append(abs(expected-conditions[f'{world}_{namespace}_cache{str(order)*2}_{scope}_0']['z'][0]))
                    del caches
                    for policy in ['native','instruction']:
                        encoded=prefix(ctx,world,namespace,instruction=policy=='instruction')
                        cache=prefill(encoded,independent=policy!='native',record=consumption.setdefault(f'{world}_{namespace}_{policy}',{}))
                        for owner in [0,1]:score(f'{world}_{namespace}_{policy}_{owner}',cache,encoded[1],world,owner)
                        if ci==0 and world=='origin' and policy=='native':
                            default=model(input_ids=torch.tensor([encoded[0]],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
                            self_errors.append(max(float((getattr(a,k)-getattr(b,k)).abs().max())
                                for a,b in zip(cache.layers,default.layers) for k in ['keys','values']))
                            del default
                        del cache
                for owner in [0,1]:
                    for world in (['origin'] if owner==0 else WORLDS):
                        encoded=prefix(ctx,world,namespace,single=owner);key=namespace+('_single_A' if owner==0 else '_single_B_'+world)
                        cache=prefill(encoded,independent=False,record=consumption.setdefault(key,{}))
                        score(key,cache,encoded[1],world,owner)
                        if ci==0:
                            no_op=prefill(encoded,independent=True)
                            self_errors.append(max(float((getattr(a,k)-getattr(b,k)).abs().max())
                                for a,b in zip(cache.layers,no_op.layers) for k in ['keys','values']))
                            del no_op
                        del cache
            assert len(conditions)==86
            assert all(max(x)<=.001 for x in [numeric,self_errors,graph_zero,composition_errors])
            stream.write(json.dumps({'context':ci,'conditions':conditions})+'\n');stream.flush()
            print(ci+1,'/',args.n,'numeric',max(numeric),'composition',max(composition_errors),'graph',max(graph_zero),flush=True)
    assert len(consumption)==22 and len(query_consumption)==86
    assert all(set(v)==set(range(len(model.model.layers))) and set(v.values())=={args.n} for v in consumption.values())
    assert all(set(v)==set(range(len(model.model.layers))) and set(v.values())=={args.n} for v in query_consumption.values())
    revisions={'qwen3':'b968826d9c46dd6066d109eabc6255188de91218','mistral':'caa1feb0e54d415e2df31207e5f4e273e33509b1','llama':'1f47e50cdbe801ad8a5174156ec3a0655108fb9f'}
    elapsed=time.time()-started
    run={'args':vars(args),'model_type':model.config.model_type,'model_revision':('40c069824f4251a91eefaf281ebe4c544efd3e18' if '14B' in args.model else revisions[model.config.model_type]),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'contexts_sha256':hashlib.sha256((dest/'contexts.jsonl').read_bytes()).hexdigest(),'num_layers':len(model.model.layers),
        'numeric_max_error':max(numeric),'cache_no_op_max_error':max(self_errors),
        'composition_max_error':max(composition_errors),'graph_zero_max_error':max(graph_zero),
        'all_layer_consumption':consumption,'query_layer_consumption':query_consumption,
        'training':False,'dtype':'float32','attention':'eager','python':platform.python_version(),
        'torch':torch.__version__,'transformers':transformers.__version__,
        'elapsed_seconds':elapsed,'gpu_hours':elapsed/3600,
        'git_head':None}
    (dest/'run.json').write_text(json.dumps(run,indent=2)+'\n');analyze(dest)


if __name__=='__main__':main()
