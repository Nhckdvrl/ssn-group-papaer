"""E105: finite before/after inference memory interchange; no optimization.
Teacher thinking histories are generated once in BF16 then replayed in FP32.
"""
import argparse, copy, hashlib, itertools, json, platform, subprocess, time
from pathlib import Path
from e95_source_grouping import contexts, audit, body, parse
from e103_memory_crossing import interval
from e104_criterion_policy import CUE

SYSTEM='Infer rules from the examples. Return only the requested one-word answer.'
HEADER=("For the next judgment, use the reviewer's personal preference from their own examples "
        'and the common evaluation aspect. Return only yes or no.\n\n')
GOAL='Which single aspect do all three reviewers judge? Answer food for food spiciness, or service for service pace.\n'

def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def load(p): return [json.loads(s) for s in p.read_text().splitlines() if s]

def teacher_body(c,ct,pt):
    s=body(c,'criterion',pt,ct,pt,None);assert s.endswith(GOAL);return s[:-len(GOAL)]

def own_body(c,pr,ct=None):
    s=('Each reviewer decides yes or no based on exactly one aspect: food spiciness (spicy or mild), '
       'or service pace (quick or leisurely). Each reviewer has a personal preference for one of '
       'the two values of their chosen aspect. yes means the experience matches that personal '
       'preference; no means it does not. Infer their rules from the examples.\n\n')
    for d in c['demos']:
        if d['a']: s+=f'Reviewer: Dana\nReview: {d["text"]}\nLabel: {"yes" if pr*d["x"][0]==1 else "no"}\n\n'
    if ct is not None: s+=CUE.format(aspect='food spiciness' if ct==0 else 'service pace')
    return s+'Read these examples. A new review will follow.\n'

def generate(a,tok,cs,dest):
    import torch, transformers
    from transformers import AutoModelForCausalLM
    assert not (dest/'teachers.jsonl').exists();torch.set_num_threads(6);torch.manual_seed(0);t0=time.time()
    print('Loading teacher BF16/SDPA',flush=True)
    model,info=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.bfloat16,
        device_map='cuda',attn_implementation='sdpa',output_loading_info=True)
    model.eval();model.requires_grad_(False);assert not info.get('missing_keys');tok.padding_side='left'
    rows=[];continued=0
    with torch.inference_mode(), (dest/'teachers.jsonl').open('w') as f:
        for c in cs:
            cases=list(itertools.product((0,1),(1,-1)));texts=[]
            for ct,pt in cases:
                texts.append(tok.apply_chat_template([{'role':'system','content':SYSTEM},
                    {'role':'user','content':teacher_body(c,ct,pt)+GOAL}],tokenize=False,
                    add_generation_prompt=True,enable_thinking=True,reasoning_effort='medium'))
            xx=tok(texts,return_tensors='pt',padding=True,add_special_tokens=False).to('cuda');width=xx.input_ids.shape[1]
            gen=model.generate(**xx,max_new_tokens=1024,do_sample=False,pad_token_id=tok.pad_token_id,
                               eos_token_id=tok.eos_token_id)
            for j,(ct,pt) in enumerate(cases):
                pi=xx.input_ids[j][xx.attention_mask[j].bool()].tolist();raw=gen[j,width:].tolist()
                censored=tok.eos_token_id not in raw;original=raw[:]
                if censored:
                    fi=torch.tensor([pi+raw],device='cuda');more=model.generate(input_ids=fi,
                        attention_mask=torch.ones_like(fi),max_new_tokens=2048,do_sample=False,
                        pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)[0,fi.shape[1]:].tolist()
                    raw+=more;assert raw[:len(original)]==original;continued+=1
                if tok.eos_token_id in raw: raw=raw[:raw.index(tok.eos_token_id)+1]
                text=tok.decode(raw,skip_special_tokens=False);cl,status=parse(text,('food','service'))
                row={'context':c['context'],'ct':ct,'pt':pt,'reported_c':0 if cl==-1 else 1 if cl==1 else None,
                     'valid':cl!=0,'correct':cl==(-1 if ct==0 else 1),'parse_status':status,
                     'initial_censored':censored,'still_censored':tok.eos_token_id not in raw,
                     'prompt_ids':pi,'token_ids':raw,'text':text,'prompt_sha256':digest(pi)}
                rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
            print('teacher context',c['context'],'rows',len(rows),'correct',sum(r['correct'] for r in rows),flush=True)
    write(dest/'generation_analysis.json',{'n':len(rows),'correct':sum(r['correct'] for r in rows),
        'unknown':sum(not r['valid'] for r in rows),'continued':continued,
        'still_censored':sum(r['still_censored'] for r in rows),'per_context':[
            {'context':c['context'],'correct':sum(r['correct'] for r in rows if r['context']==c['context'])} for c in cs]})
    write(dest/'generation_run.json',{'args':vars(a),'precision':'bf16','attention':'sdpa',
        'elapsed_seconds':time.time()-t0,'gpu_hours':(time.time()-t0)/3600,'torch':torch.__version__,
        'transformers':transformers.__version__,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    print('Generation complete',len(rows),flush=True)

def prepare(tok,cs,teachers):
    lookup={(r['context'],r['ct'],r['pt']):r for r in teachers};all_data=[]
    def record(c,name,user,qi,after=None):
        future=HEADER+f'Reviewer: {name}\nReview: {c["queries"][qi]["text"]}\nGive this reviewer\'s yes/no label for the review.\n'
        # Canonical suffix derived from one complete template, cut inside user.
        prompt=tok.apply_chat_template([{'role':'system','content':SYSTEM},{'role':'user','content':user},
            {'role':'assistant','content':'Ready.'},{'role':'user','content':future}],tokenize=False,
            add_generation_prompt=True,enable_thinking=True,reasoning_effort='medium')+'</think>\n\nAnswer:'
        if after is not None:
            marker='<|im_start|>user\n'+HEADER;cut=prompt.rfind(marker);assert cut>=0
            actual=after['prompt_ids']+after['token_ids']
            prompt=tok.decode(actual,skip_special_tokens=False)+'\n'+prompt[cut:]
            full=tok.encode(prompt,add_special_tokens=False);assert full[:len(actual)]==actual
        field=f'Reviewer: {name}\nReview:';cut=prompt.rfind(field);assert cut>=0
        prefix=tok.encode(prompt[:cut],add_special_tokens=False);full=tok.encode(prompt,add_special_tokens=False)
        assert full[:len(prefix)]==prefix
        assert c['queries'][qi]['text'] not in prompt[:cut]
        return {'context':c['context'],'name':name,'query':qi,'x':c['queries'][qi]['x'],
                'prefix_ids':prefix,'suffix_ids':full[len(prefix):],'full_ids':full}
    for c in cs:
        own={(pr,ct,qi):record(c,'Dana',own_body(c,pr,ct),qi)
             for pr,ct,qi in itertools.product((1,-1),(None,0,1),range(4))}
        tt={}
        for ct,pt,stage,qi in itertools.product((0,1),(1,-1),('before','after','explicit'),range(4)):
            parent=lookup[c['context'],ct,pt];s=teacher_body(c,ct,pt)
            if stage=='explicit':s+=CUE.format(aspect='food spiciness' if ct==0 else 'service pace')
            s+='Read these examples. A new review will follow.\n'
            tt[ct,pt,stage,qi]=record(c,c['names'][1],s,qi,after=parent if stage=='after' else None)
        # No future-review content nor current caller identity in provider prefix.
        for ct,pt,stage in itertools.product((0,1),(1,-1),('before','after','explicit')):
            assert len({tuple(tt[ct,pt,stage,qi]['prefix_ids']) for qi in range(4)})==1
            assert 'Dana' not in tok.decode(tt[ct,pt,stage,0]['prefix_ids'])
        for pr,ct in itertools.product((1,-1),(None,0,1)):
            assert len({tuple(own[pr,ct,qi]['prefix_ids']) for qi in range(4)})==1
        for qi in range(4):
            assert len({tuple(own[pr,ct,qi]['suffix_ids']) for pr,ct in itertools.product((1,-1),(None,0,1))})==1
        all_data.append((own,tt))
    return all_data,lookup

def analyze(rows):
    ids=sorted({r['context'] for r in rows});out={'n_rows':len(rows),'conditions':{},'paired':{}}
    def rate(rr,field):
        return interval([sum(r['argmax_class']==r[field] for r in rr if r['context']==ci)
            /sum(r['context']==ci for r in rr) for ci in ids])
    for cond in sorted({r['condition'] for r in rows}):
        rr=[r for r in rows if r['condition']==cond];it={'n':len(rr),'invalid':sum(not r['valid'] for r in rr)}
        if cond=='own':out['conditions'][cond]=it;continue
        it['criterion_rate']=rate(rr,'criterion_target');it['sender_function']=rate(rr,'sender_function')
        it['subsets']={}
        for sub in ('mixed','concordant','opposite_mixed','same_mixed'):
            ss=[r for r in rr if ((r['x'][0]!=r['x'][1]) if sub=='mixed' else (r['x'][0]==r['x'][1]) if sub=='concordant'
                else r['x'][0]!=r['x'][1] and ((r['pt']!=r['pr']) if sub=='opposite_mixed' else (r['pt']==r['pr'])))]
            if ss:it['subsets'][sub]={'n':len(ss),'criterion_rate':rate(ss,'criterion_target')}
        groups={}
        for r in rr:groups.setdefault((r['context'],r['ct'],r['pt'],r['pr']),[]).append(r)
        assert all(len(g)==4 for g in groups.values())
        it['complete_profiles']=sum(all(r['argmax_class']==r['criterion_target'] for r in g) for g in groups.values())
        it['profile_denominator']=len(groups);out['conditions'][cond]=it
    def key(r):return (r['context'],r['ct'],r['pt'],r['pr'],r['query'])
    before={key(r):r for r in rows if r['condition']=='rec_before'}
    for cond in ('rec_after','rec_explicit'):
        rr=[r for r in rows if r['condition']==cond];vals=[];zs=[];same=0
        for ci in ids:
            ss=[r for r in rr if r['context']==ci and r['pt']!=r['pr'] and r['x'][0]!=r['x'][1]]
            vals.append(sum((r['argmax_class']==r['criterion_target'])-(before[key(r)]['argmax_class']==r['criterion_target']) for r in ss)/len(ss))
            zs.append(sum(r['criterion_target']*(r['z']-before[key(r)]['z']) for r in ss)/len(ss))
        out['paired'][cond+'_minus_before_opposite_mixed']={'accuracy':interval(vals),'directed_margin':interval(zs)}
        out['paired'][cond+'_same_answer_as_before']=sum(r['argmax_class']==before[key(r)]['argmax_class'] for r in rr)/len(rr)
    return out

def mechanics(a,tok,cs,dest):
    import torch,transformers
    from transformers import AutoModelForCausalLM
    teachers=load(Path(a.teachers));data,lookup=prepare(tok,cs,teachers)
    cfg=json.loads((Path(a.model)/'config.json').read_text());types=cfg['text_config']['layer_types']
    assert types.count('linear_attention')==48 and types.count('full_attention')==16
    lids=[tok.encode(' '+s,add_special_tokens=False) for s in ('no','yes')];assert all(len(x)==1 for x in lids);lids=[x[0] for x in lids]
    write(dest/'preflight.json',{'args':vars(a),'contexts_sha256':digest(cs),'expected_rows':152*a.n,
        'actual_teacher_count':len(teachers),'exact_prefix_boundary':True,'provider_future_review_absent':True,
        'provider_owner_name_absent':True,'layers':types,'training':False})
    if a.preflight_only:print('Mechanism preflight passed',152*a.n,flush=True);return
    assert not (dest/'behavior.jsonl').exists();torch.set_num_threads(6);torch.manual_seed(0);t0=time.time()
    print('Loading FP32/eager two-device mechanism model',flush=True)
    model,info=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.float32,
        device_map='auto',max_memory={0:'64GiB',1:'64GiB'},attn_implementation='eager',output_loading_info=True)
    model.eval();model.requires_grad_(False);assert not info.get('missing_keys')
    assert set(model.hf_device_map.values())<={0,1,'cuda:0','cuda:1'}
    flags={'suffix':False};carry={i:0 for i,t in enumerate(types) if t=='linear_attention'}
    for i in carry:
        mix=model.model.layers[i].linear_attn
        for fnname in ('chunk_gated_delta_rule','recurrent_gated_delta_rule'):
            old=getattr(mix,fnname)
            def fn(*args,_old=old,_i=i,**kw):
                if flags['suffix']:assert kw.get('initial_state') is not None;carry[_i]+=1
                return _old(*args,**kw)
            setattr(mix,fnname,fn)
    def fingerprint(cache,group='all'):
        h=hashlib.sha256()
        for i,t in enumerate(types):
            if group=='kv' and t!='full_attention' or group=='rec' and t!='linear_attention':continue
            for name in (('keys','values') if t=='full_attention' else ('conv_states','recurrent_states')):
                v=getattr(cache.layers[i],name);h.update(str((i,name,tuple(v.shape))).encode());h.update(v.cpu().numpy().tobytes())
        return h.hexdigest()
    def swap(base,provider):
        cache=copy.deepcopy(base)
        for i,t in enumerate(types):
            if t=='linear_attention':
                for name in ('conv_states','recurrent_states'):
                    dst=getattr(cache.layers[i],name);src=getattr(provider.layers[i],name)
                    assert dst.shape==src.shape and dst.data_ptr()!=src.data_ptr();dst.copy_(src)
                assert cache.has_previous_state(i)
            else:
                assert torch.equal(cache.layers[i].keys,base.layers[i].keys)
                assert torch.equal(cache.layers[i].values,base.layers[i].values)
        assert cache.get_seq_length()==base.get_seq_length();return cache
    def predict(r,cache):
        seq=torch.tensor([r['suffix_ids']],device='cuda:0');n=len(r['prefix_ids']);flags['suffix']=True
        try:return model(input_ids=seq,position_ids=torch.arange(n,n+seq.shape[1],device='cuda:0')[None],
            past_key_values=cache,use_cache=True,logits_to_keep=1).logits[0,-1].float().cpu()
        finally:flags['suffix']=False
    errors={'self_copy_max_vocab_nats':0.,'split_full_max_vocab_nats':0.,'split_full_max_margin_nats':0.,
            'split_full_argmax_disagreement':0,'split_full_checked':0,'untouched_KV_exact':True,'pristine_cache_exact':True}
    rows=[];unique=set()
    def save(r,lo,cond,pr,ct,pt,khash,rhash,f):
        top=int(lo.argmax());pred=1 if top==lids[1] else -1 if top==lids[0] else 0
        parent=lookup.get((r['context'],ct,pt),{});reported=parent.get('reported_c')
        row={'context':r['context'],'condition':cond,'pr':pr,'ct':ct,'pt':pt,'query':r['query'],'x':r['x'],
             'argmax_class':pred,'valid':top in lids,'argmax_token':top,'z':float(lo[lids[1]]-lo[lids[0]]),
             'criterion_target':None if ct is None else pr*r['x'][ct],
             'sender_function':None if ct is None else pt*r['x'][ct],
             'reported_c':reported,'reported_criterion_target':None if reported is None else pr*r['x'][reported],
             'kv_fingerprint':khash,'rec_fingerprint':rhash}
        rows.append(row);f.write(json.dumps(row)+'\n');f.flush();unique.add((khash,rhash,tuple(r['suffix_ids'])))
    with torch.inference_mode(), (dest/'behavior.jsonl').open('w') as f:
        for ci,(own,tt) in enumerate(data):
            caches={};hs={};native={}
            parents={('own',pr,ct):own[pr,ct,0] for pr,ct in itertools.product((1,-1),(None,0,1))}
            parents.update({(stage,ct,pt):tt[ct,pt,stage,0] for ct,pt,stage in itertools.product((0,1),(1,-1),('before','after','explicit'))})
            for k,r in parents.items():
                caches[k]=model(input_ids=torch.tensor([r['prefix_ids']],device='cuda:0'),use_cache=True,logits_to_keep=1).past_key_values
                hs[k]={g:fingerprint(caches[k],g) for g in ('all','kv','rec')}
            for pr,ct,qi in itertools.product((1,-1),(None,0,1),range(4)):
                k=('own',pr,ct);r=own[pr,ct,qi];lo=predict(r,copy.deepcopy(caches[k]));native[k,qi]=lo
                save(r,lo,'own' if ct is None else 'full_owner_cue',pr,ct,pr,hs[k]['kv'],hs[k]['rec'],f)
                if ci==0 and ct is not None:
                    full=model(input_ids=torch.tensor([r['full_ids']],device='cuda:0'),use_cache=False,logits_to_keep=1).logits[0,-1].float().cpu()
                    errors['split_full_max_vocab_nats']=max(errors['split_full_max_vocab_nats'],float((full-lo).abs().max()))
                    errors['split_full_max_margin_nats']=max(errors['split_full_max_margin_nats'],abs(float((full[lids[1]]-full[lids[0]])-(lo[lids[1]]-lo[lids[0]]))))
                    errors['split_full_argmax_disagreement']+=int(full.argmax()!=lo.argmax());errors['split_full_checked']+=1
            assert errors['split_full_argmax_disagreement']==0 and errors['split_full_max_margin_nats']<=.01
            for ct,pt,stage,qi in itertools.product((0,1),(1,-1),('before','after'),range(4)):
                k=(stage,ct,pt);r=tt[ct,pt,stage,qi];lo=predict(r,copy.deepcopy(caches[k]))
                save(r,lo,'full_teacher_'+stage,pt,ct,pt,hs[k]['kv'],hs[k]['rec'],f)
            for stage,ct,pt,pr,qi in itertools.product(('before','after','explicit'),(0,1),(1,-1),(1,-1),range(4)):
                k=('own',pr,None);d=(stage,ct,pt);r=own[pr,None,qi]
                lo=predict(r,swap(caches[k],caches[d]));save(r,lo,'rec_'+stage,pr,ct,pt,hs[k]['kv'],hs[d]['rec'],f)
            k=('own',1,None);r=own[1,None,0];lo=predict(r,swap(caches[k],caches[k]))
            errors['self_copy_max_vocab_nats']=max(errors['self_copy_max_vocab_nats'],float((lo-native[k,0]).abs().max()))
            assert errors['self_copy_max_vocab_nats']<=.001
            assert all(fingerprint(v)==hs[k]['all'] for k,v in caches.items())
            write(dest/'numeric_audit.json',errors);write(dest/'carry_audit.json',carry)
            print('mechanism context',ci+1,'rows',len(rows),flush=True)
            del caches,hs,native
        assert len(rows)==152*a.n
    aa=analyze(rows);aa['unique_memory_query_inputs']=len(unique);write(dest/'analysis.json',aa)
    write(dest/'run.json',{'args':vars(a),'n_rows':len(rows),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'teacher_file_sha256':hashlib.sha256(Path(a.teachers).read_bytes()).hexdigest(),'precision':'float32','attention':'eager',
        'training':False,'torch':torch.__version__,'transformers':transformers.__version__,'python':platform.python_version(),
        'errors':errors,'elapsed_seconds':time.time()-t0,'gpu_hours':2*(time.time()-t0)/3600,
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()})
    print('Mechanism complete',len(rows),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['generate','mechanics'],required=True)
    ap.add_argument('--model',default='/tmp/ices_models/Qwen3.8-27B');ap.add_argument('--out',required=True)
    ap.add_argument('--n',type=int,default=4);ap.add_argument('--seed',type=int,default=105001)
    ap.add_argument('--teachers',default='results/e105/generation/teachers.jsonl');ap.add_argument('--preflight-only',action='store_true');a=ap.parse_args()
    dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True);cs=contexts(a.n,a.seed)
    write(dest/'design_audit.json',audit(cs));write(dest/'contexts.json',cs)
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    if a.phase=='generate':
        if a.preflight_only:print('Generation design audit passed',4*a.n,flush=True);return
        generate(a,tok,cs,dest)
    else:mechanics(a,tok,cs,dest)

if __name__=='__main__':main()
