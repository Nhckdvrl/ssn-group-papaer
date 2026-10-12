"""E130: input-independent source-cue information under fixed recipient evidence."""
import argparse,copy,hashlib,json,platform,subprocess,sys,time
from pathlib import Path
import numpy as np
from e56_query_adapter import HEAD
from e118_criterion_code_feature_crossing import WORLDS,interval
from e122_source_preserving_formation import truth
RECIPIENTS=['origin','food_positive']
SCOPES=['own','joint']
TYPES={'food':['food_positive','food_negative'],'service':['origin','service_negative']}
POLICIES=['independent','native','targeted']

def analyze(dest):
    rows=[json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    cs=[json.loads(x) for x in (dest/'contexts.jsonl').read_text().splitlines()]
    f=np.asarray([truth(c,'food_positive',1) for c in cs],float)
    s=np.asarray([truth(c,'origin',1) for c in cs],float)
    p=np.asarray([-1 if c['reverse'] else 1 for c in cs])[:,None]
    discord=f!=s
    assert np.all(discord.sum(1)==4)
    features={'food':f,'service':s,'bias':np.broadcast_to(p,f.shape),'food_service':f*s*p}
    word_ids=json.loads((dest/'preflight.json').read_text())['word_ids']
    out={'n_contexts':len(rows),'conditions':{},'matrices':{},'matrix_statistics':{},'contrasts':{},
         'primary':'native donor formation; within-context mean over two recipients: signed determinants of CueB functional matrix and CueB-minus-CueA matrix; own body scope',
         'scope':'functional source-conditioned criterion/code information in a pre-input multi-layer KV block, not a single abstract task vector'}
    raw={};performance={}
    for k in rows[0]['conditions']:
        vals=[r['conditions'][k] for r in rows]
        z=np.asarray([v['z'] for v in vals]);g=np.asarray([v['gold'] for v in vals])
        out['conditions'][k]={'full_accuracy':interval([np.mean(v['argmax_correct']) for v in vals]),
            'candidate_accuracy':interval(((z>0)==(g>0)).mean(1)),
            'correct_margin':interval((z*g).mean(1)),
            'discordant_full_accuracy':interval((np.asarray([v['argmax_correct'] for v in vals])*discord).sum(1)/4),
            'features':{n:interval((z*x).mean(1)) for n,x in features.items()}}
        if 'donor_gold' in vals[0]:
            donor_gold=np.asarray([v['donor_gold'] for v in vals])
            donor_tokens=np.asarray(word_ids)[(donor_gold>0).astype(int)]
            donor_correct=np.asarray([v['argmax_token'] for v in vals])==donor_tokens
            out['conditions'][k].update({
                'donor_full_accuracy':interval(donor_correct.mean(1)),
                'donor_candidate_accuracy':interval(((z>0)==(donor_gold>0)).mean(1)),
                'donor_correct_margin':interval((z*donor_gold).mean(1)),
                'donor_discordant_full_accuracy':interval((donor_correct*discord).sum(1)/4)})
        raw[k]=z
        full=np.asarray([v['argmax_correct'] for v in vals])
        performance[k]={'full_accuracy':full.mean(1),'candidate_accuracy':((z>0)==(g>0)).mean(1),
            'correct_margin':(z*g).mean(1),'discordant_full_accuracy':(full*discord).sum(1)/4}
        if 'donor_gold' in vals[0]:
            performance[k].update({'donor_full_accuracy':donor_correct.mean(1),
                'donor_candidate_accuracy':((z>0)==(donor_gold>0)).mean(1),
                'donor_correct_margin':(z*donor_gold).mean(1),
                'donor_discordant_full_accuracy':(donor_correct*discord).sum(1)/4})
    def statistics(m):
        det=np.linalg.det(m)
        row_norms=np.linalg.norm(m,axis=2);norm=row_norms.prod(axis=1)
        rotation=np.where((row_norms>.001).all(axis=1),det/np.maximum(norm,1e-30),0)
        return {'det':det,'rotation':rotation,'food_selectivity':m[:,0,0]-m[:,0,1],
                'service_selectivity':m[:,1,1]-m[:,1,0],'interaction':.5*(m[:,0,0]-m[:,0,1]+m[:,1,1]-m[:,1,0])}
    primary={};arrays={}
    for policy in POLICIES:
        for scope in SCOPES:
            group={'CueB':[],'Source_specific':[]}
            for r in RECIPIENTS:
                mats={}
                for actor in [0,1]:
                    ds=[.5*(raw[f'patch_{policy}_{r}_{pos}_cue{actor}_{scope}']-raw[f'patch_{policy}_{r}_{neg}_cue{actor}_{scope}']) for pos,neg in TYPES.values()]
                    m=np.stack([np.stack([(d*f).mean(1),(d*s).mean(1)],axis=1) for d in ds],axis=1)
                    mats[actor]=m
                    key=f'{policy}_{r}_cue{actor}_{scope}'
                    out['matrices'][key]={t:{feat:interval(m[:,i,j]) for j,feat in enumerate(['food','service'])} for i,t in enumerate(TYPES)}
                    out['matrix_statistics'][key]={k:interval(v) for k,v in statistics(m).items()}
                delta=mats[1]-mats[0];key=f'{policy}_{r}_source_specific_{scope}'
                out['matrices'][key]={t:{feat:interval(delta[:,i,j]) for j,feat in enumerate(['food','service'])} for i,t in enumerate(TYPES)}
                out['matrix_statistics'][key]={k:interval(v) for k,v in statistics(delta).items()}
                group['CueB'].append(statistics(mats[1]));group['Source_specific'].append(statistics(delta))
            for kind,values in group.items():
                m={k:np.mean([v[k] for v in values],axis=0) for k in values[0]}
                arrays[policy,scope,kind]=m
                out['contrasts'][policy+'_'+scope+'_'+kind]={k:interval(v) for k,v in m.items()}
                if scope=='own' and policy=='native':primary[kind]=m['det']
    out['co_primary_results']={k:interval(v) for k,v in primary.items()}
    out['co_primary_private_directions']={str(d):{k:interval(v[[c['reverse']==d for c in cs]]) for k,v in primary.items()} for d in [False,True]}
    out['formation_contrasts']={}
    for first,second in [('native','independent'),('targeted','native'),('targeted','independent')]:
        for scope in SCOPES:
            for kind in ['CueB','Source_specific']:
                a,b=arrays[first,scope,kind],arrays[second,scope,kind]
                key=f'{first}_minus_{second}_{scope}_{kind}'
                out['formation_contrasts'][key]={k:interval(a[k]-b[k]) for k in a}
    out['formation_performance_contrasts']={}
    for first,second in [('native','independent'),('targeted','native'),('targeted','independent')]:
        for r in RECIPIENTS:
            for world in WORLDS:
                for actor in [0,1]:
                    for scope in SCOPES:
                        tail=f'{r}_{world}_cue{actor}_{scope}'
                        a,b=performance['patch_'+first+'_'+tail],performance['patch_'+second+'_'+tail]
                        out['formation_performance_contrasts'][first+'_minus_'+second+'_'+tail]={k:interval(a[k]-b[k]) for k in a}
    out['criterion_only']={}
    for policy in POLICIES:
        for r in RECIPIENTS:
            for scope in SCOPES:
                for code,food,service,sign in [('same','food_positive','origin',1),('opposite','food_negative','service_negative',-1)]:
                    responses={a:raw[f'patch_{policy}_{r}_{food}_cue{a}_{scope}']-raw[f'patch_{policy}_{r}_{service}_cue{a}_{scope}'] for a in [0,1]}
                    for actor,response in [('cue0',responses[0]),('cue1',responses[1]),('source_specific',responses[1]-responses[0])]:
                        fields={name:(response*x).mean(1) for name,x in features.items()}
                        fields['A_code_Food_minus_Service_selectivity']=fields['food']-fields['service']
                        fields['donor_code_Food_minus_Service_selectivity']=sign*(fields['food']-fields['service'])
                        key=f'{policy}_{r}_{actor}_{scope}_{code}'
                        out['criterion_only'][key]={'all':{k:interval(v) for k,v in fields.items()},
                            'private':{str(d):{k:interval(v[[c['reverse']==d for c in cs]]) for k,v in fields.items()} for d in [False,True]}}
    out['all_private_directions']={str(d):{k:{feat:interval((z*x).mean(1)[[c['reverse']==d for c in cs]]) for feat,x in features.items()} for k,z in raw.items()} for d in [False,True]}
    (dest/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out['co_primary_results']),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--n',type=int,default=16);ap.add_argument('--seed',type=int,default=130001)
    ap.add_argument('--materials',choices=['discovery','validation'],default='discovery')
    ap.add_argument('--preflight-only',action='store_true');ap.add_argument('--analyze-only',action='store_true')
    args=ap.parse_args();dest=Path(args.out)
    if args.analyze_only:analyze(dest);return
    dest.mkdir(parents=True,exist_ok=True);assert not (dest/'behavior.jsonl').exists()
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True);enc=lambda x:tok.encode(x,add_special_tokens=False)
    material=dest/'materials'
    subprocess.run([sys.executable,str(Path(__file__).with_name('e119_criterion_scale.py')),'--model',args.model,'--out',str(material),
        '--n',str(args.n),'--seed',str(args.seed),'--materials',args.materials,'--preflight-only'],check=True)
    cs=[json.loads(x) for x in (material/'contexts.jsonl').read_text().splitlines()]
    aliases=['Alex','Sam'] if args.materials=='discovery' else ['Robin','Jordan']
    for c in cs:
        c['names']=[aliases[0 if x=='Alex' else 1] for x in c['names']]
        c['shown']=[c['names'][o] for _,o,_ in c['demos']]
    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    words=['no','yes'];word_ids=[[enc(' '+w)[0] for w in words] for _ in [0,1]]
    assert all(len(enc(' '+w))==1 for w in words)
    namespace='shared';label_ids_by_namespace={'shared':word_ids[0]}
    def prefix_metadata(c,world,single=None,instruction=False):
        header=HEAD+("Use only the examples of the requested annotator to infer and apply that annotator's labeling rule.\n\n" if instruction else '')
        ids=enc(header);roles=[-1]*len(ids);labels=[];answers=[[],[]]
        for (text,owner,y),name in zip(c['demos'],c['shown']):
            if single is not None and owner!=single:continue
            if owner==1 and world!='origin':text=c[world+'_map'][text]
            front=enc(f'Comment: {text}\nAnnotator: {name}\nLabel:');answer=enc(' '+words[y])+enc('\n\n')
            anchor=len(ids)+len(front);labels.append(anchor);answers[owner].extend(range(anchor,anchor+len(answer)))
            piece=front+answer;ids.extend(piece);roles.extend([owner]*len(piece))
        return ids,roles,labels,answers
    def prefix(c,world,single=None,instruction=False):return prefix_metadata(c,world,single,instruction)[:2]
    def field(c,actor):return enc(f"Annotator: {c['names'][actor]}\nComment:")
    def body(c):return [enc(' '+text+'\nLabel:') for text,_ in c['q']]
    def early(c,actor):return [field(c,actor)+q for q in body(c)]
    def late(c,actor):return [enc(f"Comment: {text}\nAnnotator: {c['names'][actor]}\nLabel:") for text,_ in c['q']]
    metadata=[{w:prefix_metadata(c,w) for w in WORLDS} for c in cs]
    data=[{w:v[:2] for w,v in d.items()} for d in metadata]
    for c,ds,md in zip(cs,data,metadata):
        assert len(field(c,0))==len(field(c,1))
        ids0,roles0=ds['origin']
        for ids,roles in ds.values():
            assert len(ids)==len(ids0) and roles==roles0
            assert all(a==b for a,b,o in zip(ids,ids0,roles) if o!=1)
        assert all(v[2:]==md['origin'][2:] for v in md.values())
    preflight={'args':vars(args),'conditions':136,'queries':8,'prefix_interfaces':21,'cue_interfaces':24,'donor_formation_policies':POLICIES,
        'names':aliases,'words':words,'word_ids':word_ids[0],'recipients':RECIPIENTS,'donor_worlds':WORLDS,
        'donor_cue_actors':[0,1],'body_scopes':SCOPES,'receiving_actor':1,
        'source_cue_before_all_query_content':True,'cue_reads_all_private_sources':True,
        'recipient_private_formation':'independent','donor_private_formation':POLICIES,'primary_body_scope':'own',
        'source_cue_is_full_KV_block':True,'prefix_lengths':[len(ds['origin'][0]) for ds in data],
        'cue_lengths':[[len(field(c,a)) for a in [0,1]] for c in cs],
        'primary':'native donor Cue; context mean of per-recipient det(M_CueB) and det(M_CueB-M_CueA), own body',
        'material_builder_sha256':hashlib.sha256(Path(__file__).with_name('e119_criterion_scale.py').read_bytes()).hexdigest(),
        'truth_source_sha256':hashlib.sha256(Path(__file__).with_name('e122_source_preserving_formation.py').read_bytes()).hexdigest(),
        'field_semantics':'complete Annotator/name/Comment-header block; no query comment or answer, no oracle source selection in cue',
        'instruction_control':'one sentence with native formation',
        'label_receiver_and_answer_sender_positions':[{w:{'labels':v[2],'answers':v[3]} for w,v in d.items()} for d in metadata]}
    (dest/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    if args.preflight_only:print('E130 actual tokens, pre-input fields and world geometry passed.',flush=True);return
    import torch,transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6);torch.manual_seed(0);started=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,dtype=torch.float32,device_map='cuda',attn_implementation='eager').eval();model.requires_grad_(False)
    numeric,cache_noop,graph_zero,composition_errors=[],[],[],[]
    consumption,query_consumption,cue_consumption={},{},{}

    def prefix_allowed(roles, independent, formation, target_map=None):
            rr=torch.tensor(roles,device='cuda')
            allowed=torch.ones((len(roles),len(roles)),dtype=torch.bool,device='cuda').tril()
            if independent:
                for owner in [0,1]:
                    allowed &= ~((rr[:,None]==owner)&(rr[None,:]==1-owner))
            if not formation:
                allowed &= ~((rr[:,None]>=0)&(rr[None,:]==-2))
            if target_map is not None:
                labels,answers=target_map
                for owner in [0,1]:
                    receivers=torch.tensor([i for i in labels if roles[i]==owner],device='cuda',dtype=torch.long)
                    senders=torch.tensor(answers[1-owner],device='cuda',dtype=torch.long)
                    if len(receivers) and len(senders):
                        past=senders[None,:]<receivers[:,None]
                        allowed[receivers[:,None],senders[None,:]] &= ~past
            assert allowed.diag().all()
            return allowed

    def prefill(encoded, independent=True, formation=True, record=None, target_map=None):
            ids,roles=encoded
            allowed=prefix_allowed(roles,independent,formation,target_map)
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

    def prepare(cache,roles,ids,record=None):
        plen=len(roles);size=len(ids);cp=copy.deepcopy(cache)
        allowed=torch.cat([torch.ones((size,plen),dtype=torch.bool,device='cuda'),torch.ones((size,size),dtype=torch.bool,device='cuda').tril()],dim=1)
        mask=torch.zeros((1,1,size,plen+size),device='cuda').masked_fill_(~allowed[None,None],float('-inf'))
        handles=[]
        if record is not None:
            def hook(module,aa,kw):
                assert torch.equal(kw['attention_mask'],mask)
                k=module.layer_idx;record[k]=record.get(k,0)+1
            handles=[l.self_attn.register_forward_pre_hook(hook,with_kwargs=True) for l in model.model.layers]
        try:
            got=model(input_ids=torch.tensor([ids],device='cuda'),position_ids=torch.arange(plen,plen+size,device='cuda')[None],
                attention_mask=mask,past_key_values=cp,use_cache=True,logits_to_keep=1).past_key_values
        finally:
            for h in handles:h.remove()
        assert cache.get_seq_length()==plen and got.get_seq_length()==plen+size
        return got
    def plain_check(encoded,queries,owner,independent,expected,only_own=False,target_map=None):
        ids,roles=encoded;plen=len(ids);q=queries[0];size=plen+len(q)
        allowed=torch.zeros((size,size),dtype=torch.bool,device='cuda');allowed[:plen,:plen]=prefix_allowed(roles,independent,True,target_map)
        keep=torch.ones(plen,dtype=torch.bool,device='cuda')
        if only_own:keep &= torch.tensor(roles,device='cuda')!=1-owner
        allowed[plen:,:plen]=keep;allowed[plen:,plen:]=torch.ones((len(q),len(q)),dtype=torch.bool,device='cuda').tril()
        mask=torch.zeros((1,1,size,size),device='cuda').masked_fill_(~allowed[None,None],float('-inf'))
        v=model(input_ids=torch.tensor([ids+q],device='cuda'),attention_mask=mask,use_cache=False,logits_to_keep=1).logits[0,-1]
        numeric.append(abs(float(v[word_ids[owner][1]]-v[word_ids[owner][0]])-expected))
    with torch.inference_mode(),(dest/'behavior.jsonl').open('w') as stream:
        for ci,c in enumerate(cs):
            conditions={}
            def score(key,cache,roles,queries,owner,world,scope='joint',donor_world=None,donor_actor=None):
                v=query(cache,roles,queries,owner,False,scope=='own',record=query_consumption.setdefault(key,{}));v['gold']=truth(c,world,owner)
                v['argmax_correct']=[t==word_ids[owner][int(g>0)] for t,g in zip(v['argmax_token'],v['gold'])]
                if donor_world is not None:v['donor_gold']=truth(c,donor_world,donor_actor)
                conditions[key]=v
            independent={w:prefill(data[ci][w],independent=True,record=consumption.setdefault('independent_'+w,{})) for w in WORLDS}
            native={w:prefill(data[ci][w],independent=False,record=consumption.setdefault('native_'+w,{})) for w in WORLDS}
            targeted={w:prefill(data[ci][w],independent=False,target_map=metadata[ci][w][2:],record=consumption.setdefault('targeted_'+w,{})) for w in WORLDS}
            policy_caches={'independent':independent,'native':native,'targeted':targeted}
            roles=data[ci]['origin'][1];plen=len(roles);aidx=torch.tensor(roles,device='cuda')==0
            for w in WORLDS[1:]:
                graph_zero.append(max(float((getattr(l,k)[:,:,aidx]-getattr(o,k)[:,:,aidx]).abs().max()) for l,o in zip(independent[w].layers,independent['origin'].layers) for k in ['keys','values']))
            cues={(p,w,a):prepare(caches[w],roles,field(c,a),record=cue_consumption.setdefault(f'{p}_{w}_cue{a}',{})) for p,caches in policy_caches.items() for w in WORLDS for a in [0,1]}
            cue_roles=roles+[-3]*len(field(c,1))
            for policy in POLICIES:
                for r in RECIPIENTS:
                    for d in WORLDS:
                        for actor in [0,1]:
                            cp=copy.deepcopy(cues['independent',r,1])
                            assert all(getattr(t,k).data_ptr()!=getattr(o,k).data_ptr() and getattr(t,k).data_ptr()!=getattr(donor,k).data_ptr() for t,o,donor in zip(cp.layers,cues['independent',r,1].layers,cues[policy,d,actor].layers) for k in ['keys','values'])
                            for target,donor in zip(cp.layers,cues[policy,d,actor].layers):
                                for k in ['keys','values']:
                                    getattr(target,k)[:,:,plen:]=getattr(donor,k)[:,:,plen:]
                            assert cp.get_seq_length()==plen+len(field(c,1))
                            assert all(torch.equal(getattr(t,k)[:,:,:plen],getattr(o,k)[:,:,:plen]) for t,o in zip(cp.layers,cues['independent',r,1].layers) for k in ['keys','values'])
                            for scope in SCOPES:
                                key=f'patch_{policy}_{r}_{d}_cue{actor}_{scope}'
                                score(key,cp,cue_roles,body(c),1,r,scope,d,actor)
                                if policy=='independent' and d==r and actor==1:
                                    original=query(cues['independent',r,1],cue_roles,body(c),1,False,scope=='own')
                                    composition_errors.append(max(abs(a-b) for a,b in zip(original['z'],conditions[key]['z'])))
                                    assert original['argmax_token']==conditions[key]['argmax_token']
                            del cp
            for w in WORLDS:
                score('independent_early_'+w+'_B',cues['independent',w,1],cue_roles,body(c),1,w,'own')
                score('independent_late_'+w+'_B',independent[w],roles,late(c,1),1,w,'own')
                score('native_early_'+w+'_B',native[w],roles,early(c,1),1,w)
                score('native_late_'+w+'_B',native[w],roles,late(c,1),1,w)
                score('targeted_early_'+w+'_B',targeted[w],roles,early(c,1),1,w)
                score('targeted_late_'+w+'_B',targeted[w],roles,late(c,1),1,w)
                for p in ['native','targeted']:
                    prepared=query(cues[p,w,1],cue_roles,body(c),1,False,False)
                    base=conditions[p+'_early_'+w+'_B']
                    composition_errors.append(max(abs(a-b) for a,b in zip(prepared['z'],base['z'])))
                    assert prepared['argmax_token']==base['argmax_token']
                encoded=prefix(c,w,instruction=True)
                inst=prefill(encoded,independent=False,record=consumption.setdefault('instruction_'+w,{}))
                score('instruction_early_'+w+'_B',inst,encoded[1],early(c,1),1,w)
                encoded=prefix(c,w,single=1)
                single=prefill(encoded,independent=False,record=consumption.setdefault('single_B_'+w,{}))
                score('single_early_'+w+'_B',single,encoded[1],early(c,1),1,w)
                score('single_late_'+w+'_B',single,encoded[1],late(c,1),1,w)
                if ci==0:
                    no_op=prefill(encoded,independent=True)
                    cache_noop.append(max(float((getattr(a,k)-getattr(b,k)).abs().max()) for a,b in zip(single.layers,no_op.layers) for k in ['keys','values']))
                    del no_op
                    target_no_op=prefill(encoded,independent=False,target_map=prefix_metadata(c,w,single=1)[2:])
                    cache_noop.append(max(float((getattr(a,k)-getattr(b,k)).abs().max()) for a,b in zip(single.layers,target_no_op.layers) for k in ['keys','values']))
                    del target_no_op
                    plain_check(data[ci][w],early(c,1),1,False,conditions['native_early_'+w+'_B']['z'][0])
                    plain_check(data[ci][w],late(c,1),1,True,conditions['independent_late_'+w+'_B']['z'][0],True)
                    plain_check(data[ci][w],early(c,1),1,False,conditions['targeted_early_'+w+'_B']['z'][0],target_map=metadata[ci][w][2:])
                    # Full-token equivalent of cue-all / body-own two-stage computation.
                    ids=data[ci][w][0]+field(c,1)+body(c)[0];cue_end=plen+len(field(c,1));length=len(ids)
                    allowed=torch.ones((length,length),device='cuda',dtype=torch.bool).tril();allowed[:plen,:plen]=prefix_allowed(roles,True,True)
                    keep=torch.tensor(roles,device='cuda')!=0;allowed[cue_end:,:plen]=keep[None]
                    mask=torch.zeros((1,1,length,length),device='cuda').masked_fill_(~allowed[None,None],float('-inf'))
                    ll=model(input_ids=torch.tensor([ids],device='cuda'),attention_mask=mask,use_cache=False,logits_to_keep=1).logits[0,-1]
                    numeric.append(abs(float(ll[word_ids[1][1]]-ll[word_ids[1][0]])-conditions['independent_early_'+w+'_B']['z'][0]))
                del inst,single
            score('native_early_origin_A',native['origin'],roles,early(c,0),0,'origin')
            score('independent_early_origin_A',cues['independent','origin',0],roles+[-3]*len(field(c,0)),body(c),0,'origin','own')
            encoded=prefix(c,'origin',single=0);single=prefill(encoded,independent=False,record=consumption.setdefault('single_A',{}))
            score('single_early_A',single,encoded[1],early(c,0),0,'origin');score('single_late_A',single,encoded[1],late(c,0),0,'origin')
            if ci==0:
                default=model(input_ids=torch.tensor([data[ci]['origin'][0]],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
                cache_noop.append(max(float((getattr(a,k)-getattr(b,k)).abs().max()) for a,b in zip(native['origin'].layers,default.layers) for k in ['keys','values']))
                del default
            assert len(conditions)==136 and all(max(x)<=.001 for x in [numeric,cache_noop,graph_zero,composition_errors])
            stream.write(json.dumps({'context':ci,'conditions':conditions})+'\n');stream.flush()
            print(ci+1,'/',args.n,'numeric',max(numeric),'graph',max(graph_zero),'composition',max(composition_errors),flush=True)
            del single,cues,independent,native,targeted,policy_caches
    assert len(consumption)==21 and len(cue_consumption)==24 and len(query_consumption)==136
    for block in [consumption,cue_consumption,query_consumption]:
        assert all(set(v)==set(range(len(model.model.layers))) and set(v.values())=={args.n} for v in block.values())
    run={'args':vars(args),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'contexts_sha256':hashlib.sha256((dest/'contexts.jsonl').read_bytes()).hexdigest(),
        'num_layers':len(model.model.layers),'model_type':model.config.model_type,'model_revision':'40c069824f4251a91eefaf281ebe4c544efd3e18' if '14B' in args.model else '1f47e50cdbe801ad8a5174156ec3a0655108fb9f',
        'numeric_max_error':max(numeric),'cache_no_op_max_error':max(cache_noop),'composition_max_error':max(composition_errors),'graph_zero_max_error':max(graph_zero),
        'all_layer_consumption':consumption,'cue_layer_consumption':cue_consumption,'query_layer_consumption':query_consumption,
        'training':False,'dtype':'float32','attention':'eager','python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,
        'gpu_hours':(time.time()-started)/3600,'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    (dest/'run.json').write_text(json.dumps(run,indent=2)+'\n');analyze(dest)
if __name__=='__main__':main()
