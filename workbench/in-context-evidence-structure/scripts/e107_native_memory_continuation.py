"""E107: native free reasoning after E105 memory interchanges. Fixed opposite p.
No retraining, layer selection, or teacher correctness filtering.
"""
import argparse,copy,hashlib,itertools,json,platform,subprocess,time
from pathlib import Path
from e105_inferred_memory import contexts,load,prepare,write,digest
from e95_source_grouping import parse
from e103_memory_crossing import interval

TAIL='</think>\n\nAnswer:'

def analyze(rows):
    ids=sorted({r['context'] for r in rows});out={'n_rows':len(rows),'conditions':{},'paired':{}}
    def estimate(ss,field):
        return interval([sum(r['class']==r[field] for r in ss if r['context']==ci)/sum(r['context']==ci for r in ss) for ci in ids])
    for cond in sorted({r['condition'] for r in rows}):
        rr=[r for r in rows if r['condition']==cond];item={'n':len(rr),'unknown':sum(not r['valid'] for r in rr),
            'initial_censored':sum(r['initial_censored'] for r in rr),'still_censored':sum(r['still_censored'] for r in rr)}
        if cond=='own':out['conditions'][cond]=item;continue
        item['criterion_rate']=estimate(rr,'criterion_target');item['sender_function']=estimate(rr,'sender_function')
        for sub in ('mixed','concordant'):
            ss=[r for r in rr if (r['x'][0]!=r['x'][1])==(sub=='mixed')];item[sub]=estimate(ss,'criterion_target')
        gs={}
        for r in rr:gs.setdefault((r['context'],r['pr'],r['ct']),[]).append(r)
        assert all(len(g)==4 for g in gs.values());item['complete_profiles']=sum(all(r['class']==r['criterion_target'] for r in g) for g in gs.values());item['profile_denominator']=len(gs)
        out['conditions'][cond]=item
    before={(r['context'],r['pr'],r['ct'],r['query']):r for r in rows if r['condition']=='rec_before'}
    for cond in ('rec_after','rec_explicit'):
        rr=[r for r in rows if r['condition']==cond and r['x'][0]!=r['x'][1]]
        out['paired'][cond+'_minus_before_mixed']=interval([sum((r['class']==r['criterion_target'])-
            (before[r['context'],r['pr'],r['ct'],r['query']]['class']==r['criterion_target'])
            for r in rr if r['context']==ci)/sum(r['context']==ci for r in rr) for ci in ids])
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--part',type=int,choices=range(4));ap.add_argument('--out',required=True)
    ap.add_argument('--model',default='/tmp/ices_models/Qwen3.8-27B');ap.add_argument('--teachers',default='results/e105/generation/teachers.jsonl')
    ap.add_argument('--preflight-only',action='store_true');ap.add_argument('--merge',nargs='*');a=ap.parse_args();dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    if a.merge:
        rows=sum([load(Path(p)/'behavior.jsonl') for p in a.merge],[]);assert len(rows)==288 and {r['context'] for r in rows}==set(range(4))
        keys={(r['context'],r['condition'],r['pr'],r['ct'],r['query']) for r in rows};assert len(keys)==288
        for ci in range(4):assert sum(r['context']==ci for r in rows)==72
        write(dest/'analysis.json',analyze(rows));write(dest/'completeness_audit.json',{'rows':288,'unique_keys':288,'all_four_parts':True,
            'all_parents_kept':True,'opposite_private_p_all':all(r['pt']==-r['pr'] for r in rows if r['condition'].startswith('rec_')),
            'part_paths':a.merge,'gpu_hours':sum(json.load(open(Path(p)/'run.json'))['gpu_hours'] for p in a.merge)})
        (dest/'behavior.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));print('Merged',len(rows),flush=True);return
    assert a.part is not None
    cs=contexts(4,105001);teachers=load(Path(a.teachers));assert len(teachers)==16
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True);data,lookup=prepare(tok,cs,teachers)
    own,tt=data[a.part]
    for r in list(own.values())+list(tt.values()):
        text=tok.decode(r['full_ids'],skip_special_tokens=False);assert text.endswith(TAIL)
        full=tok.encode(text[:-len(TAIL)],add_special_tokens=False);assert full[:len(r['prefix_ids'])]==r['prefix_ids']
        r['full_ids']=full;r['suffix_ids']=full[len(r['prefix_ids']):]
    write(dest/'preflight.json',{'args':vars(a),'expected_requests':72,'prefixes_unchanged':True,'future_thinking_open':True,
        'no_teacher_selection':True,'teacher_sha256':hashlib.sha256(Path(a.teachers).read_bytes()).hexdigest()})
    if a.preflight_only:print('Native continuation preflight',a.part,72,flush=True);return
    assert not (dest/'behavior.jsonl').exists()
    import torch,transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6);torch.manual_seed(0);t0=time.time();print('Loading E107 part',a.part,flush=True)
    model,info=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.bfloat16,
        device_map='cuda',attn_implementation='sdpa',output_loading_info=True)
    model.eval();model.requires_grad_(False);assert not info.get('missing_keys')
    types=model.config.layer_types;carry={i:0 for i,t in enumerate(types) if t=='linear_attention'}
    flags={'consume':False,'first':False,'expected_suffix':None,'first_logits':None}
    for i in carry:
        mix=model.model.layers[i].linear_attn
        for fname in ('chunk_gated_delta_rule','recurrent_gated_delta_rule'):
            old=getattr(mix,fname)
            def fn(*args,_old=old,_i=i,**kw):
                if flags['consume']:assert kw.get('initial_state') is not None;carry[_i]+=1
                return _old(*args,**kw)
            setattr(mix,fname,fn)
    def input_guard(m,args,kw):
        if flags['first']:
            actual=kw.get('input_ids',args[0] if args else None);assert actual is not None
            assert actual[0].tolist()==flags['expected_suffix'],(actual.shape,len(flags['expected_suffix']))
    def output_guard(m,args,out):
        if flags['first']:flags['first_logits']=out.logits[0,-1].float().cpu();flags['first']=False
    model.register_forward_pre_hook(input_guard,with_kwargs=True);model.register_forward_hook(output_guard)
    def finger(cache,group='all'):
        h=hashlib.sha256()
        for i,t in enumerate(types):
            if group=='kv' and t!='full_attention' or group=='rec' and t!='linear_attention':continue
            for name in (('keys','values') if t=='full_attention' else ('conv_states','recurrent_states')):
                v=getattr(cache.layers[i],name);h.update(str((i,name,tuple(v.shape))).encode());h.update(v.float().cpu().numpy().tobytes())
        return h.hexdigest()
    def swap(base,provider):
        cp=copy.deepcopy(base)
        for i,t in enumerate(types):
            if t=='linear_attention':
                for name in ('conv_states','recurrent_states'):
                    dst=getattr(cp.layers[i],name);src=getattr(provider.layers[i],name);assert dst.shape==src.shape
                    assert dst.data_ptr()!=src.data_ptr();dst.copy_(src)
            else:
                assert torch.equal(cp.layers[i].keys,base.layers[i].keys) and torch.equal(cp.layers[i].values,base.layers[i].values)
        assert cp.get_seq_length()==base.get_seq_length();return cp
    def generate(r,cache):
        full=torch.tensor([r['full_ids']],device='cuda');n=full.shape[1]
        assert cache.get_seq_length()==len(r['prefix_ids'])
        flags.update(consume=True,first=True,expected_suffix=r['suffix_ids'],first_logits=None)
        try:
            gen=model.generate(input_ids=full,attention_mask=torch.ones_like(full),past_key_values=cache,
                max_new_tokens=1024,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id,
                return_dict_in_generate=True)
            first=flags['first_logits'];assert first is not None
            raw=gen.sequences[0,n:].tolist();initial=raw[:];censored=tok.eos_token_id not in raw
            if censored:
                fi=torch.tensor([r['full_ids']+raw],device='cuda');cp=gen.past_key_values
                assert cp.get_seq_length() in (fi.shape[1]-1,fi.shape[1])
                flags['first']=False
                more=model.generate(input_ids=fi,attention_mask=torch.ones_like(fi),past_key_values=cp,
                    max_new_tokens=2048,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id,
                    return_dict_in_generate=True)
                raw+=more.sequences[0,fi.shape[1]:].tolist();assert raw[:len(initial)]==initial
            if tok.eos_token_id in raw:raw=raw[:raw.index(tok.eos_token_id)+1]
            return raw,first,censored,tok.eos_token_id not in raw
        finally:flags.update(consume=False,first=False)
    cache={};hashes={};rows=[];errors={}
    with torch.inference_mode(),(dest/'behavior.jsonl').open('w') as f:
        parents={('own',pr,ct):own[pr,ct,0] for pr,ct in itertools.product((1,-1),(None,0,1))}
        parents.update({(stage,ct,pt):tt[ct,pt,stage,0] for stage,ct,pt in itertools.product(('before','after','explicit'),(0,1),(1,-1))})
        for key,r in parents.items():
            cache[key]=model(input_ids=torch.tensor([r['prefix_ids']],device='cuda'),use_cache=True,logits_to_keep=1).past_key_values
            hashes[key]={g:finger(cache[key],g) for g in ('all','kv','rec')}
        jobs=[('own' if ct is None else 'full_owner_cue',pr,ct,pr,qi) for pr,ct,qi in itertools.product((1,-1),(None,0,1),range(4))]
        jobs += [('rec_'+stage,pr,ct,-pr,qi) for stage,pr,ct,qi in itertools.product(('before','after','explicit'),(1,-1),(0,1),range(4))]
        for ji,(cond,pr,ct,pt,qi) in enumerate(jobs):
            k=('own',pr,ct if cond=='full_owner_cue' else None);r=own[k[1],k[2],qi]
            d=(cond.removeprefix('rec_'),ct,pt) if cond.startswith('rec_') else k
            mixed=swap(cache[k],cache[d]);raw,lo,censored,still=generate(r,mixed)
            text=tok.decode(raw,skip_special_tokens=False);cl,status=parse(text,('no','yes'))
            row={'context':a.part,'condition':cond,'pr':pr,'pt':pt,'ct':ct,'query':qi,'x':r['x'],
                'class':cl,'valid':cl!=0,'parse_status':status,'initial_censored':censored,'still_censored':still,
                'criterion_target':None if ct is None else pr*r['x'][ct],
                'sender_function':None if ct is None else pt*r['x'][ct],'token_ids':raw,'text':text,
                'kv_fingerprint':hashes[k]['kv'],'rec_fingerprint':hashes[d]['rec']}
            rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
            if cond=='full_owner_cue' and pr==1 and ct==0 and qi==0:
                again,ref,_,_=generate(r,swap(cache[k],cache[k]));assert again==raw
                errors['self_copy_max_vocab_nats']=float((ref-lo).abs().max());assert errors['self_copy_max_vocab_nats']<=.001
                ss=torch.tensor([r['suffix_ids']],device='cuda');start=len(r['prefix_ids']);flags['consume']=True
                manual=model(input_ids=ss,attention_mask=torch.ones((1,len(r['full_ids'])),device='cuda',dtype=torch.long),
                    position_ids=torch.arange(start,start+ss.shape[1],device='cuda')[None],past_key_values=copy.deepcopy(cache[k]),
                    use_cache=True,logits_to_keep=1).logits[0,-1].float().cpu();flags['consume']=False
                errors['generate_manual_firststep_max_vocab_nats']=float((manual-lo).abs().max())
                assert errors['generate_manual_firststep_max_vocab_nats']<=.001,errors
                full=model(input_ids=torch.tensor([r['full_ids']],device='cuda'),use_cache=False,logits_to_keep=1).logits[0,-1].float().cpu()
                errors['full_split_firststep_max_vocab_nats']=float((full-lo).abs().max())
                errors['full_split_firststep_argmax_same']=bool(full.argmax()==lo.argmax())
                write(dest/'numeric_audit.json',errors)
            if (ji+1)%8==0:print('part',a.part,'requests',ji+1,'/',len(jobs),'unknown',sum(not r['valid'] for r in rows),flush=True)
        assert len(rows)==72 and all(finger(v)==hashes[k]['all'] for k,v in cache.items())
    write(dest/'analysis.json',analyze(rows));write(dest/'carry_audit.json',carry)
    write(dest/'run.json',{'args':vars(a),'n_rows':72,'precision':'bf16','attention':'sdpa','training':False,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'teacher_sha256':hashlib.sha256(Path(a.teachers).read_bytes()).hexdigest(),
        'torch':torch.__version__,'transformers':transformers.__version__,'python':platform.python_version(),
        'pristine_caches_exact':True,'errors':errors,'elapsed_seconds':time.time()-t0,'gpu_hours':(time.time()-t0)/3600,
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()})
    print('E107 part complete',a.part,flush=True)

if __name__=='__main__':main()
