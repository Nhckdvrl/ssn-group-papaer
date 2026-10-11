"""E104 stage A: criterion control from recurrence, private mapping from own KV.
Uses the state-swap method of arXiv:2609.04434. No learned-inference phase yet.
"""
import argparse, copy, hashlib, itertools, json, platform, subprocess, time
from pathlib import Path
from e93_selective_sharing import body, contexts
from e94_coordinate_transfer import SYSTEM
from e103_memory_crossing import interval

CUE = ('For all upcoming review judgments, use only {aspect} as the evaluation aspect. '
       "Infer each reviewer's personal preference from that reviewer's own examples.\n\n")


def analyze(rows):
    ids=sorted({r['context'] for r in rows});out={'n_rows':len(rows),'conditions':{}}
    for cond in sorted({r['condition'] for r in rows}):
        rr=[r for r in rows if r['condition']==cond]
        item={'n':len(rr),'invalid':sum(not r['valid'] for r in rr)}
        if cond=='own_baseline': out['conditions'][cond]=item;continue
        for typ in ('criterion_target','sender_function'):
            item[typ]=interval([sum(r['argmax_class']==r[typ] for r in rr if r['context']==ci)
                               /sum(r['context']==ci for r in rr) for ci in ids])
        item['by_private_relation']={}
        for relation in ('same','opposite'):
            ss=[r for r in rr if (r['pt']==r['pr'])==(relation=='same')]
            if not ss:continue
            groups={}
            for r in ss: groups.setdefault((r['context'],r['pr'],r['pt'],r['ct']),[]).append(r)
            assert all(len(g)==4 for g in groups.values())
            item['by_private_relation'][relation]={
                'n':len(ss),'criterion_rate':interval([sum(r['argmax_class']==r['criterion_target']
                    for r in ss if r['context']==ci)/sum(r['context']==ci for r in ss) for ci in ids]),
                'complete_criterion_profiles':sum(all(r['argmax_class']==r['criterion_target'] for r in g)
                                                for g in groups.values()),'profile_denominator':len(groups)}
        out['conditions'][cond]=item
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True)
    ap.add_argument('--model',default='/tmp/ices_models/Qwen3.8-27B')
    ap.add_argument('--n',type=int,default=4);ap.add_argument('--seed',type=int,default=104001)
    ap.add_argument('--preflight-only',action='store_true');a=ap.parse_args()
    dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True);assert not (dest/'behavior.jsonl').exists()
    cs=contexts(a.n,a.seed)
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    lids=[tok.encode(' '+s,add_special_tokens=False) for s in ('no','yes')]
    assert all(len(v)==1 for v in lids);lids=[v[0] for v in lids]
    def record(c,name,p,cue,qi):
        cc=copy.deepcopy(c);cc['names']=[name,'Unused']
        user=body(cc,'single',p,0,1,0,qi)
        field=f'Reviewer: {name}\nReview:';cut=user.rfind(field);assert cut>=0
        prefix_user=user[:cut]
        if cue is not None: prefix_user+=CUE.format(aspect='food spiciness' if cue==0 else 'service pace')
        user=prefix_user+user[cut:]
        prompt=tok.apply_chat_template([{'role':'system','content':SYSTEM},{'role':'user','content':user}],
            tokenize=False,add_generation_prompt=True,enable_thinking=False)+'Answer:'
        start=prompt.rfind(field);assert start>=0
        prefix=tok.encode(prompt[:start],add_special_tokens=False);full=tok.encode(prompt,add_special_tokens=False)
        assert full[:len(prefix)]==prefix
        assert c['queries'][qi]['text'] not in prompt[:start]
        assert 'Reviewer: Unused' not in prompt
        return {'context':c['context'],'name':name,'p':p,'cue':cue,'query':qi,'x':c['queries'][qi]['x'],
                'prefix_ids':prefix,'suffix_ids':full[len(prefix):],'full_ids':full}
    data=[]
    for c in cs:
        dd={(name,p,ct,qi):record(c,name,p,ct,qi) for name,p,ct,qi in
            itertools.product(('Alice','Dana'),(1,-1),(None,0,1),range(4))}
        for name,p,ct in itertools.product(('Alice','Dana'),(1,-1),(None,0,1)):
            assert len({tuple(dd[name,p,ct,qi]['prefix_ids']) for qi in range(4)})==1
        for name,qi in itertools.product(('Alice','Dana'),range(4)):
            assert len({tuple(r['suffix_ids']) for (n,pr,ct,q),r in dd.items() if n==name and q==qi})==1
        data.append(dd)
    cfg=json.loads((Path(a.model)/'config.json').read_text());tc=cfg.get('text_config',cfg);types=tc['layer_types']
    assert types.count('linear_attention')==48 and types.count('full_attention')==16
    preflight={'args':vars(a),'n_contexts':a.n,'expected_rows':88*a.n,'future_input_in_sender':False,
        'actor_names_disjoint':True,'exact_prefix_boundaries':True,'output_polarities_crossed':True,
        'cache_cut':'before future Reviewer field; new Owner identity arrives after state swap',
        'receiver_unmodified_KV_length_controls_positions':True,'training':False,'layers':types,'label_ids':lids}
    (dest/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    (dest/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    if a.preflight_only:print('Preflight passed',88*a.n,'rows',flush=True);return

    import torch,transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6);torch.manual_seed(0);starttime=time.time()
    print('Loading float32/eager two-device model',flush=True)
    model,loading=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.float32,
        device_map='auto',max_memory={0:'64GiB',1:'64GiB'},attn_implementation='eager',output_loading_info=True)
    model.eval();model.requires_grad_(False);assert not loading.get('missing_keys'),loading
    assert set(model.hf_device_map.values())<={0,1,'cuda:0','cuda:1'}
    (dest/'loading_info.json').write_text(json.dumps(loading,default=str,indent=2)+'\n')
    flags={'suffix':False};carry={i:0 for i,t in enumerate(types) if t=='linear_attention'}
    for i in carry:
        mix=model.model.layers[i].linear_attn
        for fnname in ('chunk_gated_delta_rule','recurrent_gated_delta_rule'):
            old=getattr(mix,fnname)
            def fn(*args,_old=old,_i=i,**kw):
                if flags['suffix']:assert kw.get('initial_state') is not None;carry[_i]+=1
                return _old(*args,**kw)
            setattr(mix,fnname,fn)
    errors={'self_copy_max_nats':0.,'untouched_KV_exact':True,'pristine_cache_exact':True,
            'split_full_max_vocab_nats':0.,'split_full_max_margin_nats':0.,'split_full_argmax_disagreement':0,
            'split_full_checked':0}
    rows=[];unique_inputs=set()
    def fields(cache):
        for i,t in enumerate(types):
            for name in (('keys','values') if t=='full_attention' else ('conv_states','recurrent_states')):
                yield i,name,getattr(cache.layers[i],name)
    def fingerprint(cache,group='all'):
        h=hashlib.sha256()
        for i,name,v in fields(cache):
            if group=='kv' and types[i]!='full_attention':continue
            if group=='rec' and types[i]!='linear_attention':continue
            h.update(str((i,name,tuple(v.shape))).encode());h.update(v.cpu().numpy().tobytes())
        return h.hexdigest()
    def swap_rec(receiver,provider):
        cache=copy.deepcopy(receiver)
        for i,t in enumerate(types):
            if t=='linear_attention':
                for name in ('conv_states','recurrent_states'):
                    dst=getattr(cache.layers[i],name);src=getattr(provider.layers[i],name)
                    assert dst.shape==src.shape and dst.data_ptr()!=src.data_ptr();dst.copy_(src)
                assert cache.has_previous_state(i)
            else:
                assert torch.equal(cache.layers[i].keys,receiver.layers[i].keys)
                assert torch.equal(cache.layers[i].values,receiver.layers[i].values)
        assert cache.get_seq_length()==receiver.get_seq_length()
        return cache
    def predict(r,cache):
        seq=torch.tensor([r['suffix_ids']],device='cuda:0');n=len(r['prefix_ids'])
        pos=torch.arange(n,n+seq.shape[1],device='cuda:0')[None];flags['suffix']=True
        try:return model(input_ids=seq,position_ids=pos,past_key_values=cache,
            use_cache=True,logits_to_keep=1).logits[0,-1].float().cpu()
        finally:flags['suffix']=False
    def save(r,lo,cond,pr,pt,ct,kv_hash,rec_hash,stream):
        top=int(lo.argmax());pred=1 if top==lids[1] else -1 if top==lids[0] else 0
        row={'context':r['context'],'condition':cond,'pr':pr,'pt':pt,'ct':ct,'query':r['query'],
            'x':r['x'],'argmax_class':pred,'argmax_token':top,'valid':top in lids,
            'z':float(lo[lids[1]]-lo[lids[0]]),'criterion_target':None if ct is None else pr*r['x'][ct],
            'sender_function':None if ct is None else pt*r['x'][ct],
            'kv_fingerprint':kv_hash,'rec_fingerprint':rec_hash}
        rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
        unique_inputs.add((kv_hash,rec_hash,tuple(r['suffix_ids'])))
    with torch.inference_mode(),(dest/'behavior.jsonl').open('w') as stream:
        for ci,dd in enumerate(data):
            caches={};hashes={};native={}
            # Sender uncued worlds are not run: this phase provides explicit-c positive only.
            parents=[('Dana',pr,ct) for pr,ct in itertools.product((1,-1),(None,0,1))]
            parents += [('Alice',pt,ct) for pt,ct in itertools.product((1,-1),(0,1))]
            for name,pr,ct in parents:
                r=dd[name,pr,ct,0]
                caches[name,pr,ct]=model(input_ids=torch.tensor([r['prefix_ids']],device='cuda:0'),
                                       use_cache=True,logits_to_keep=1).past_key_values
                hashes[name,pr,ct]={g:fingerprint(caches[name,pr,ct],g) for g in ('all','kv','rec')}
            for name,pr,ct in parents:
                for qi in range(4):
                    r=dd[name,pr,ct,qi];lo=predict(r,copy.deepcopy(caches[name,pr,ct]));native[name,pr,ct,qi]=lo
                    cond='own_baseline' if ct is None else 'full_cue_owner' if name=='Dana' else 'full_cue_sender'
                    save(r,lo,cond,pr,pr,ct,hashes[name,pr,ct]['kv'],hashes[name,pr,ct]['rec'],stream)
                    if ci==0 and ct is not None and name=='Dana':
                        full=model(input_ids=torch.tensor([r['full_ids']],device='cuda:0'),use_cache=False,
                                   logits_to_keep=1).logits[0,-1].float().cpu()
                        errors['split_full_max_vocab_nats']=max(errors['split_full_max_vocab_nats'],float((full-lo).abs().max()))
                        errors['split_full_max_margin_nats']=max(errors['split_full_max_margin_nats'],
                            abs(float((full[lids[1]]-full[lids[0]])-(lo[lids[1]]-lo[lids[0]]))))
                        errors['split_full_argmax_disagreement']+=int(full.argmax()!=lo.argmax());errors['split_full_checked']+=1
            (dest/'numeric_audit.json').write_text(json.dumps(errors,indent=2)+'\n')
            assert errors['split_full_argmax_disagreement']==0 and errors['split_full_max_margin_nats']<=.01
            for pr,ct,qi in itertools.product((1,-1),(0,1),range(4)):
                r=dd['Dana',pr,None,qi];base=caches['Dana',pr,None]
                provider=caches['Dana',pr,ct]
                lo=predict(r,swap_rec(base,provider))
                save(r,lo,'owner_cued_rec_only',pr,pr,ct,hashes['Dana',pr,None]['kv'],hashes['Dana',pr,ct]['rec'],stream)
                for pt in (1,-1):
                    provider=caches['Alice',pt,ct];lo=predict(r,swap_rec(base,provider))
                    save(r,lo,'sender_cued_rec_only',pr,pt,ct,hashes['Dana',pr,None]['kv'],hashes['Alice',pt,ct]['rec'],stream)
            r=dd['Dana',1,None,0];cache=caches['Dana',1,None]
            copied=predict(r,swap_rec(cache,cache));ref=native['Dana',1,None,0]
            errors['self_copy_max_nats']=max(errors['self_copy_max_nats'],float((copied-ref).abs().max()))
            assert errors['self_copy_max_nats']<=.001
            assert all(fingerprint(c)==hashes[key]['all'] for key,c in caches.items())
            (dest/'numeric_audit.json').write_text(json.dumps(errors,indent=2)+'\n')
            print('context',ci+1,'/',a.n,'rows',len(rows),flush=True)
    assert len(rows)==88*a.n
    analysis=analyze(rows);analysis['unique_state_query_inputs']=len(unique_inputs)
    (dest/'analysis.json').write_text(json.dumps(analysis,indent=2)+'\n')
    (dest/'carry_audit.json').write_text(json.dumps(carry,indent=2)+'\n')
    run={'args':vars(a),'n_rows':len(rows),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'training':False,'errors':errors,'precision':'float32','attention':'eager','model_map':model.hf_device_map,
        'torch':torch.__version__,'transformers':transformers.__version__,'python':platform.python_version(),
        'elapsed_seconds':time.time()-starttime,'gpu_hours':2*(time.time()-starttime)/3600,
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    (dest/'run.json').write_text(json.dumps(run,indent=2)+'\n');print('Complete',len(rows),'rows',flush=True)


if __name__=='__main__':main()
