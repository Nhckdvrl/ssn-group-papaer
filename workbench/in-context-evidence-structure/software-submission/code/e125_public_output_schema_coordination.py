"""E125: share source-to-output schemas while keeping supervision private.

A preregistered formation/read access crossing; no layer/head/strength search.
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

WORLDS = ['origin', 'cross']
ROSTERS = ['true', 'unrelated', 'swapped']
WORDS = [['no', 'yes'], ['pass', 'flag']]
UNRELATED_PAIRS = [('Kim', 'Lee'), ('Jamie', 'Taylor'), ('Dana', 'Chris'), ('Pat', 'Max'), ('Avery', 'Bailey')]


def analyze(dest):
    rows = [json.loads(x) for x in (dest / 'behavior.jsonl').read_text().splitlines()]
    cs = [json.loads(x) for x in (dest / 'contexts.jsonl').read_text().splitlines()]
    out = {'n_contexts': len(rows), 'primary': 'full-vocabulary next-token accuracy',
           'conditions': {}, 'phase_accuracy': {}, 'contrasts': {}, 'B_code_response': {}}
    aggregates = {}
    for key in rows[0]['conditions']:
        values = [r['conditions'][key] for r in rows]
        z = np.asarray([v['z'] for v in values])
        gold = np.asarray([v['gold'] for v in values])
        out['conditions'][key] = {
            'candidate_accuracy': interval(((z > 0) == (gold > 0)).mean(1)),
            'full_accuracy': interval([np.mean(v['argmax_correct']) for v in values]),
            'source_word_rate': interval([np.mean(v['argmax_is_label']) for v in values]),
            'other_word_rate': interval([np.mean(v['other_source_word']) for v in values]),
            'correct_margin': interval((z * gold).mean(1))}
    for roster in ROSTERS:
        for form in [0, 1]:
            for read in [0, 1]:
                key = f'{roster}_f{form}r{read}'
                full = np.asarray([[[r['conditions'][f'{world}_{key}_{owner}']['argmax_correct']
                    for owner in [0, 1]] for world in WORLDS] for r in rows], dtype=float)
                cand = np.asarray([[[[(z > 0) == (g > 0) for z, g in zip(
                    r['conditions'][f'{world}_{key}_{owner}']['z'], r['conditions'][f'{world}_{key}_{owner}']['gold'])]
                    for owner in [0, 1]] for world in WORLDS] for r in rows], dtype=float)
                words = np.asarray([[[r['conditions'][f'{world}_{key}_{owner}']['argmax_is_label']
                    for owner in [0, 1]] for world in WORLDS] for r in rows], dtype=float)
                other_words = np.asarray([[[r['conditions'][f'{world}_{key}_{owner}']['other_source_word']
                    for owner in [0, 1]] for world in WORLDS] for r in rows], dtype=float)
                metrics = {'both': full.mean((1, 2, 3)), 'A': full[:, :, 0].mean((1, 2)),
                    'B': full[:, :, 1].mean((1, 2)), 'opposite': full[:, 0].mean((1, 2)),
                    'same': full[:, 1].mean((1, 2)), 'candidate': cand.mean((1, 2, 3)),
                    'source_word': words.mean((1, 2, 3)), 'other_word': other_words.mean((1, 2, 3))}
                aggregates[key] = metrics
                out['phase_accuracy'][key] = {k: interval(v) for k, v in metrics.items()}
                z0 = np.asarray([r['conditions'][f'origin_{key}_0']['z'] for r in rows])
                z1 = np.asarray([r['conditions'][f'cross_{key}_0']['z'] for r in rows])
                ga = np.asarray([truth(c, 'origin', 0) for c in cs])
                response = (.5 * (z1 - z0) * ga).mean(1)
                out['B_code_response'][key] = {'signed': interval(response), 'absolute': interval(abs(response))}
    for roster in ROSTERS:
        def difference(name, left, right):
            out['contrasts'][name] = {k: interval(aggregates[left][k] - aggregates[right][k])
                                      for k in aggregates[left]}
        difference(roster+'_formation_only_gain', roster+'_f1r0', roster+'_f0r0')
        difference(roster+'_reading_only_gain', roster+'_f0r1', roster+'_f0r0')
        difference(roster+'_formation_minus_reading', roster+'_f1r0', roster+'_f0r1')
        out['contrasts'][roster+'_form_by_read_interaction'] = {k: interval(
            aggregates[roster+'_f1r1'][k] - aggregates[roster+'_f1r0'][k]
            - aggregates[roster+'_f0r1'][k] + aggregates[roster+'_f0r0'][k])
            for k in aggregates[roster+'_f0r0']}
    for phase, key in [('formation', 'f1r0'), ('reading', 'f0r1')]:
        out['contrasts'][phase+'_true_minus_unrelated_gain'] = {k: interval(
            aggregates['true_'+key][k] - aggregates['true_f0r0'][k]
            - aggregates['unrelated_'+key][k] + aggregates['unrelated_f0r0'][k])
            for k in aggregates['true_f0r0']}
    for phase,key in [('formation','f1r0'),('reading','f0r1')]:
        out['contrasts'][phase+'_true_minus_swapped_gain'] = {k: interval(
            aggregates['true_'+key][k] - aggregates['true_f0r0'][k]
            - aggregates['swapped_'+key][k] + aggregates['swapped_f0r0'][k])
            for k in aggregates['true_f0r0']}
    for direction in [False, True]:
        ix = np.asarray([c['reverse'] == direction for c in cs])
        out.setdefault('private_directions', {})[str(direction)] = {
            k: {m: interval(v[ix]) for m, v in values.items()} for k, values in aggregates.items()}
    (dest / 'analysis.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'n_contexts': len(rows), 'full_accuracy': {k:v['both'] for k,v in out['phase_accuracy'].items()},
        'phase_identity_contrasts': {k:v['both'] for k,v in out['contrasts'].items() if 'true_minus' in k}}), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=16)
    ap.add_argument('--seed', type=int, default=125001)
    ap.add_argument('--materials', choices=['discovery','validation'], default='discovery')
    ap.add_argument('--preflight-only', action='store_true')
    ap.add_argument('--analyze-only', action='store_true')
    args = ap.parse_args()
    dest = Path(args.out)
    if args.analyze_only:
        analyze(dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    assert not (dest / 'behavior.jsonl').exists()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda x: tok.encode(x, add_special_tokens=False)
    cs, material_meta = make_contexts(tok, args.n, args.seed, args.materials)
    source_pair = ['Alex','Sam'] if args.materials == 'discovery' else ['Robin','Jordan']
    for ctx in cs:
        ctx['names'] = [source_pair[0 if n == 'Alex' else 1] for n in ctx['names']]
        ctx['shown'] = [ctx['names'][role] for _, role, _ in ctx['demos']]
    true_names = sorted(source_pair)
    def schema_text(names, owner_order):
        return 'Output words:\n'+''.join(f'{name}: '+', '.join(WORDS[owner])+'.\n' for name,owner in zip(names,owner_order))+'\n'
    for c in cs:
        order = [c['names'].index(name) for name in true_names]
        correct = schema_text(true_names, order)
        unrelated = next((list(names) for names in UNRELATED_PAIRS
            if not (set(names) & set(source_pair))
            and len(enc(schema_text(names, order))) == len(enc(correct))), None)
        assert unrelated is not None, {'source_names':source_pair, 'cause':'no length-matched schema'}
        c['rosters'] = {'true': true_names, 'unrelated': unrelated, 'swapped':true_names}
        c['roster_texts'] = {'true':correct, 'unrelated':schema_text(unrelated,order),
            'swapped':schema_text(true_names,[1-owner for owner in order])}
        assert len({len(enc(x)) for x in c['roster_texts'].values()})==1
    (dest / 'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    assert all(len(enc(' '+w))==1 for words in WORDS for w in words)
    word_ids = [[enc(' '+w)[0] for w in words] for words in WORDS]
    assert len(set(sum(word_ids, [])))==4

    def prefix(ctx, world, roster=None, single=None, instruction=False):
        header = HEAD + ('Use only the examples of the requested annotator to infer and apply that annotator\'s labeling rule.\n\n' if instruction else '')
        ids = enc(header)
        roles = [-1]*len(ids)
        if roster is not None:
            piece = enc(ctx['roster_texts'][roster])
            ids.extend(piece)
            roles.extend([-2]*len(piece))
        for (comment, owner, y), name in zip(ctx['demos'], ctx['shown']):
            if single is not None and owner != single:
                continue
            if owner == 1 and world == 'cross':
                comment = ctx['cross_map'][comment]
            block = enc(f'Comment: {comment}\nAnnotator: {name}\nLabel:')
            answer = enc(' '+WORDS[owner][y])+enc('\n\n')
            ids.extend(block+answer)
            roles.extend([owner]*(len(block)+len(answer)))
        return ids, roles

    data = [{(world, roster):prefix(c,world,roster) for world in WORLDS for roster in ROSTERS} for c in cs]
    for worlds in data:
        ids0, roles0 = worlds['origin','true']
        for (world,roster),(ids,roles) in worlds.items():
            assert len(ids)==len(ids0) and roles==roles0
            assert all(ids[i]==ids0[i] for i,r in enumerate(roles) if r != 1 and r != -2)
            otherids,_=worlds[world,'true']
            assert all(ids[i]==otherids[i] for i,r in enumerate(roles) if r != -2)
    preflight = {'args':vars(args),'conditions':63,'queries':8,'source_names':source_pair,
        'true_roster':true_names,'unrelated_roster_by_context':[c['rosters']['unrelated'] for c in cs],
        'matched_roster_token_count':True,
        'roster_contains_private_input_label_pairings':False,'roster_contains_output_words':True,'public_HEAD_precedes_roster':True,
        'source_ownership_roles':{'public_HEAD':-1,'roster':-2,'A':0,'B':1},'word_ids':word_ids,
        'material_builder_sha256':hashlib.sha256(Path(__file__).with_name('e121_sst_materials.py').read_bytes()).hexdigest(),
        'natural_materials':material_meta,'prefix_lengths':[len(x['origin','true'][0]) for x in data],
        'scope':'source-to-output schemas shared before private supervision; same criterion, private conventions, global original positions'}
    (dest/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    if args.preflight_only:
        print('E125 geometry, source aliases, public schema without private pairings passed.',flush=True)
        return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    started=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,dtype=torch.float32,
        device_map='cuda',attn_implementation='eager').eval()
    model.requires_grad_(False)
    numeric,self_errors,graph_zero,inert_errors,consumption,query_consumption=[],[],[],[],{},{}

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
            'argmax_token':top.cpu().tolist(), 'argmax_is_label':((top==outids[0])|(top==outids[1])).cpu().tolist(),
            'other_source_word':((top==word_ids[1-owner][0])|(top==word_ids[1-owner][1])).cpu().tolist()}

    with torch.inference_mode(),(dest/'behavior.jsonl').open('w') as stream:
        for ci,ctx in enumerate(cs):
            queries={owner:[enc(f"Comment: {t}\nAnnotator: {ctx['names'][owner]}\nLabel:") for t,_ in ctx['q']] for owner in [0,1]}
            conditions={}
            def score(name,cache,roles,world,owner,reading=True):
                v=query(cache,roles,queries[owner],owner,reading,record=query_consumption.setdefault(name,{}))
                v['gold']=truth(ctx,world,owner)
                v['argmax_correct']=[t==word_ids[owner][int(g>0)] for t,g in zip(v['argmax_token'],v['gold'])]
                conditions[name]=v
            for world in WORLDS:
                true_inert=None
                for roster in ROSTERS:
                    encoded=data[ci][world,roster]
                    for form in [0,1]:
                        key=f'{world}_{roster}_f{form}'
                        cache=prefill(encoded,formation=bool(form),record=consumption.setdefault(key,{}))
                        for read in [0,1]:
                            for owner in [0,1]:score(f'{key}r{read}_{owner}',cache,encoded[1],world,owner,bool(read))
                        if ci==0 and world=='origin':
                            for read in [0,1]:
                                q=queries[0][0]
                                length=len(encoded[0])+len(q)
                                allowed=torch.zeros((length,length),dtype=torch.bool,device='cuda')
                                allowed[:len(encoded[0]),:len(encoded[0])]=prefix_allowed(encoded[1],True,bool(form))
                                keep=torch.tensor(encoded[1],device='cuda')!=-2 if read==0 else torch.ones(len(encoded[1]),device='cuda',dtype=torch.bool)
                                allowed[len(encoded[0]):,:len(encoded[0])]=keep[None]
                                allowed[len(encoded[0]):,len(encoded[0]):]=torch.ones((len(q),len(q)),device='cuda',dtype=torch.bool).tril()
                                mask=torch.zeros((1,1,length,length),device='cuda',dtype=torch.float32).masked_fill_(~allowed,float('-inf'))
                                logits=model(input_ids=torch.tensor([encoded[0]+q],device='cuda'),attention_mask=mask,use_cache=False,logits_to_keep=1).logits[0,-1]
                                expected=float(logits[word_ids[0][1]]-logits[word_ids[0][0]])
                                numeric.append(abs(expected-conditions[f'{key}r{read}_0']['z'][0]))
                        if form==0:
                            if roster=='true':true_inert=cache
                            else:
                                keep=torch.tensor(encoded[1],device='cuda')!=-2
                                inert_errors.append(max(float((getattr(a,k)[:,:,keep]-getattr(b,k)[:,:,keep]).abs().max())
                                    for a,b in zip(true_inert.layers,cache.layers) for k in ['keys','values']))
                                for owner in [0,1]:
                                    v1=conditions[f'{world}_true_f0r0_{owner}']['z']
                                    v2=conditions[f'{world}_{roster}_f0r0_{owner}']['z']
                                    inert_errors.append(max(abs(a-b) for a,b in zip(v1,v2)))
                                    assert conditions[f'{world}_true_f0r0_{owner}']['argmax_token']==conditions[f'{world}_{roster}_f0r0_{owner}']['argmax_token']
                                if roster==ROSTERS[-1]:del true_inert
                        if ci==0:
                            own=query(cache,encoded[1],queries[0],0,False,True)
                            if world=='origin':
                                ctx.setdefault('graph_reference',{})[f'{roster}_{form}']=own['z']
                            else:
                                graph_zero.append(max(abs(a-b) for a,b in zip(own['z'],ctx['graph_reference'][f'{roster}_{form}'])))
                        if not (form==0 and roster=='true'):del cache
                for policy,independent in [('native',False),('independent',True)]:
                    encoded=prefix(ctx,world)
                    cache=prefill(encoded,independent=independent,record=consumption.setdefault(f'{world}_{policy}',{}))
                    for owner in [0,1]:score(f'{world}_{policy}_{owner}',cache,encoded[1],world,owner)
                    if ci==0 and world=='origin' and not independent:
                        default=model(input_ids=torch.tensor([encoded[0]],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
                        self_errors.append(max(float((getattr(a,k)-getattr(b,k)).abs().max()) for a,b in zip(cache.layers,default.layers) for k in ['keys','values']))
                        del default
                    del cache
                encoded=prefix(ctx,world,instruction=True)
                cache=prefill(encoded,record=consumption.setdefault(world+'_instruction',{}))
                for owner in [0,1]:score(f'{world}_instruction_{owner}',cache,encoded[1],world,owner)
                del cache
            for owner in [0,1]:
                for world in (['origin'] if owner==0 else WORLDS):
                    encoded=prefix(ctx,world,single=owner)
                    key='single_A' if owner==0 else 'single_B_'+world
                    cache=prefill(encoded,independent=False,record=consumption.setdefault(key,{}))
                    score(key,cache,encoded[1],world,owner)
                    if ci==0:
                        no_op=prefill(encoded,independent=True)
                        self_errors.append(max(float((getattr(a,k)-getattr(b,k)).abs().max()) for a,b in zip(cache.layers,no_op.layers) for k in ['keys','values']))
                        del no_op
                    del cache
            assert len(conditions)==63
            assert max(numeric)<=.001 and max(self_errors)<=.001 and max(inert_errors)<=.001 and max(graph_zero)<=.001
            stream.write(json.dumps({'context':ci,'conditions':conditions})+'\n');stream.flush()
            print(ci+1,'/',args.n,'numeric',max(numeric),'inert',max(inert_errors),'graph',max(graph_zero),flush=True)
    assert all(set(v)==set(range(len(model.model.layers))) and set(v.values())=={args.n} for v in consumption.values())
    assert all(set(v)==set(range(len(model.model.layers))) and set(v.values())=={args.n} for v in query_consumption.values())
    elapsed=time.time()-started
    revisions={'qwen3':'b968826d9c46dd6066d109eabc6255188de91218','mistral':'caa1feb0e54d415e2df31207e5f4e273e33509b1','llama':'1f47e50cdbe801ad8a5174156ec3a0655108fb9f'}
    run={'args':vars(args),'model_type':model.config.model_type,'model_revision':revisions[model.config.model_type],
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'contexts_sha256':hashlib.sha256((dest/'contexts.jsonl').read_bytes()).hexdigest(),'num_layers':len(model.model.layers),
        'numeric_max_error':max(numeric),'cache_no_op_max_error':max(self_errors),
        'inert_roster_max_error':max(inert_errors),'graph_zero_max_error':max(graph_zero),
        'all_layer_consumption':consumption,'query_layer_consumption':query_consumption,'training':False,'dtype':'float32','attention':'eager',
        'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,
        'elapsed_seconds':elapsed,'gpu_hours':elapsed/3600}
    (dest/'run.json').write_text(json.dumps(run,indent=2)+'\n')
    analyze(dest)


if __name__=='__main__':main()
