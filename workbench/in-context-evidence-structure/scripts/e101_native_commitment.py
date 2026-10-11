"""E101: one-time native activation interchange at an annotated rule event."""
import argparse, collections, hashlib, itertools, json, platform, time
from pathlib import Path
from e95_source_grouping import CELLS, parse

ROOT = Path(__file__).resolve().parents[1]
LAYERS = (15, 31, 47, 63)
COMPONENTS = [(kind, layer) for layer in LAYERS for kind in ('mixer', 'residual')]
BATCH = 8

def read(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def key(r):
    return tuple(r[k] for k in ('context','pa','cb','pb','query'))

def build(tok, annotations):
    directory = Path(annotations)
    mapping = {r['id']:tuple(r['key'][1:]) for r in json.loads((directory/'private_manifest.json').read_text())}
    aa = read(directory/'reviewed_annotations.jsonl')
    assert len(aa) == len(mapping) == 32 and len({a['id'] for a in aa}) == 32
    source = ROOT/'results/e99/qwen35_part0'
    rr = {key(r):r for r in read(source/'behavior.jsonl') if r['kind']=='native' and r['pb']==1}
    pp = {key(r):r for r in read(source/'prompts.jsonl') if r['kind']=='native' and r['pb']==1}
    assert len(rr)==len(pp)==32
    events, issues = {}, []
    for a in aa:
        k = mapping[a['id']]; r = rr[k]
        original = r['score']['token_ids']
        text = tok.decode(original, skip_special_tokens=False, clean_up_tokenization_spaces=False)
        assert text == r['score']['text']
        assert text[a['char_start']:a['char_end']] == a['exact_span']
        if a['status']!='event':
            issues.append({'key':list(k),'id':a['id'],'reason':a['status']}); continue
        # Preserve the original generated token prefix; never retokenize it.
        cut = None
        for j in range(len(original)):
            before = tok.decode(original[:j], skip_special_tokens=False, clean_up_tokenization_spaces=False)
            after = tok.decode(original[:j+1], skip_special_tokens=False, clean_up_tokenization_spaces=False)
            if len(before)<=a['char_start']<len(after):
                if after.startswith(before) and not text[len(before):a['char_start']].strip():
                    cut = j; break
        if cut is None:
            issues.append({'key':list(k),'id':a['id'],'reason':'not_at_token_start_except_leading_whitespace'}); continue
        prompt_ids = tok.encode(pp[k]['prompt'], add_special_tokens=False)
        events[k] = {'key':list(k),'id':a['id'],'criterion_hat':a['criterion'],
                     'cut':cut,'char_start':a['char_start'],'exact_span':a['exact_span'],
                     'prefix_ids':prompt_ids+original[:cut], 'original_thinking_ids':original[:cut],
                     'original_final_class':r['score']['class'],'gold':r['gold'],
                     'prefix_sha256':digest(prompt_ids+original[:cut]),
                     'source_prompt_sha256':r['prompt_sha256']}
    expected, pairs, absent = [], [], []
    for rc in (0,1):
        for pr, cr, qd, qr in itertools.product((1,-1),(0,1),(1,2),range(4)):
            rk=(rc,pr,cr,1,qr); dk=(1-rc,-pr,1-cr,1,qd)
            item={'recipient':list(rk),'donor':list(dk)}; expected.append(item)
            if rk not in events or dk not in events:
                absent.append(item);continue
            item.update(pair_id=len(pairs), recipient_id=events[rk]['id'],donor_id=events[dk]['id'])
            xr,xd=CELLS[qr],CELLS[qd]
            predictions={}
            for mode,cd in [('world',1-cr),('event',events[dk]['criterion_hat'])]:
                predictions[mode]={'criterion':pr*xr[cd],'private_function':-pr*xr[cd],
                                   'selected_attribute':pr*xd[cd],'answer':-pr*xd[cd]}
            item.update(predictions=predictions,original_recipient=rr[rk]['score']['class'],
                        original_donor=rr[dk]['score']['class'])
            pairs.append(item)
    assert len(expected)==64 and len(pairs)+len(absent)==64
    audit={'frozen_native_trajectories':32,'located_events':len(events),'issues':issues,
           'expected_pairs':64,'located_pairs':len(pairs),'absent_pairs':absent,
           'components':COMPONENTS,'original_prefix_tokens_preserved':True,
           'annotation_sha256':hashlib.sha256((directory/'reviewed_annotations.jsonl').read_bytes()).hexdigest(),
           'scope':'Fixed two-context causal development sample, not independent confirmation.',
           'source_behavior_sha256':hashlib.sha256((source/'behavior.jsonl').read_bytes()).hexdigest(),
           'source_prompts_sha256':hashlib.sha256((source/'prompts.jsonl').read_bytes()).hexdigest()}
    return events,pairs,audit

def analyze(rows):
    out={}
    for component in sorted({r['component'] for r in rows}):
        ss=[r for r in rows if r['component']==component]
        entry={'n':len(ss),'valid':sum(r['score']['class']!=0 for r in ss),'profiles':{}}
        for mode in ('world','event'):
            mm={}
            for hypothesis in ('criterion','private_function','selected_attribute','answer'):
                correct=sum(r['score']['class']==r['predictions'][mode][hypothesis] for r in ss)
                groups=collections.defaultdict(list)
                for r in ss:
                    groups[(tuple(r['donor']),tuple(r['recipient'][:4]))].append(r)
                complete=[g for g in groups.values() if len(g)==4 and {r['recipient'][4] for r in g}==set(range(4))]
                full=sum(all(r['score']['class']==r['predictions'][mode][hypothesis] for r in g) for g in complete)
                base_matches=sum(r['replayed_recipient']==r['predictions'][mode][hypothesis] for r in ss)
                mm[hypothesis]={'matches':correct,'denominator':len(ss),'rate':correct/len(ss) if ss else None,
                                'complete_profiles':len(complete),'profiles_all_four_match':full,
                                'replayed_baseline_matches':base_matches,
                                'match_gain_vs_replayed':(correct-base_matches)/len(ss) if ss else None,
                                'baseline_differs_from_prediction':sum(r['replayed_recipient']!=r['predictions'][mode][hypothesis] for r in ss),
                                'became_prediction':sum(r['replayed_recipient']!=r['predictions'][mode][hypothesis] and r['score']['class']==r['predictions'][mode][hypothesis] for r in ss)}
            entry['profiles'][mode]=mm
        entry['unchanged_original_answer']=sum(r['score']['class']==r['original_recipient'] for r in ss)
        entry['unchanged_replayed_answer']=sum(r['score']['class']==r['replayed_recipient'] for r in ss)
        entry['actual_donor_answer_match']=sum(r['score']['class']==r['original_donor'] for r in ss)
        out[component]=entry
    return {'n_rows':len(rows),'components':out,'uncertainty':'n2 exploratory; no population or independent-mechanism claim.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--annotations',default=str(ROOT/'results/e101/annotations'))
    ap.add_argument('--part',type=int,choices=range(4));ap.add_argument('--design-only',action='store_true')
    ap.add_argument('--model',default='/tmp/ices_models/Qwen3.8-27B');ap.add_argument('--merge',nargs='+')
    args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    if args.merge:
        assert len(args.merge)==4
        rows=[];runs=[];baseline=[]
        for p in map(Path,args.merge):
            r=json.loads((p/'run.json').read_text()); rr=read(p/'behavior.jsonl')
            assert len(rr)==r['n_rows'] and r['self_copy_max_nats']<=.001
            rows+=rr;runs.append(r);baseline+=read(p/'baseline.jsonl')
        assert sorted(r['part'] for r in runs)==list(range(4))
        for f in ('script_sha256','design_sha256','model_config_sha256','torch','transformers'):
            assert len({json.dumps(r[f],sort_keys=True) for r in runs})==1,f
        assert len({(r['component'],r['pair_id']) for r in rows})==len(rows)
        assert not (out/'behavior_merged.jsonl').exists()
        (out/'behavior_merged.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        save(out/'analysis.json',analyze(rows))
        lookup=collections.defaultdict(list)
        for r in baseline:lookup[tuple(r['key'])].append(r['score']['class'])
        save(out/'completeness_audit.json',{'n_rows':len(rows),'parts':[r['part'] for r in runs],
             'gpu_hours':sum(r['gpu_hours'] for r in runs),'baseline_unique_prefixes':len(lookup),
             'baseline_answers_differ_across_parts':sum(len(set(v))>1 for v in lookup.values()),
             'unresolved':sum(r['score']['class']==0 for r in rows),'source_runs':runs})
        return
    import torch,transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(6);torch.manual_seed(0)
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True);tok.padding_side='left'
    if tok.pad_token_id is None:tok.pad_token_id=tok.eos_token_id
    events,pairs,audit=build(tok,args.annotations);save(out/'design_audit.json',audit)
    (out/'events.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in events.values()))
    save(out/'pair_manifest.json',pairs)
    if args.design_only:print(json.dumps(audit));return
    assert args.part is not None and not (out/'behavior.jsonl').exists()
    selected=COMPONENTS[2*args.part:2*args.part+2]
    script_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();start=time.time()
    print('Loading E101',args.part,flush=True)
    model,loading=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,dtype=torch.bfloat16,
                 device_map='cuda',attn_implementation='sdpa',output_loading_info=True)
    assert not loading.get('missing_keys')
    model.eval();model.requires_grad_(False)
    save(out/'loading_info.json',json.loads(json.dumps(loading,default=str)))
    layers=model.model.layers
    assert len(layers)==64 and all(layers[l].layer_type=='full_attention' for l in LAYERS)
    ordered=sorted(events)
    acts={};baseline=[];self_max=0.
    def tensor(keys):
        ids=[events[k]['prefix_ids'] for k in keys]
        x=tok.pad({'input_ids':ids},padding=True,return_tensors='pt').to('cuda')
        return x
    def module(kind,layer):return layers[layer].self_attn if kind=='mixer' else layers[layer]
    def hook_for(kind, action):
        def hook(m,inp,output):
            h=output[0] if kind=='mixer' else output
            changed=action(h)
            return (changed,)+output[1:] if kind=='mixer' else changed
        return hook
    def generate(keys,component=None,donor_keys=None):
        x=tensor(keys);width=x.input_ids.shape[1];calls=[0];handle=None
        if component:
            kind,layer=component
            def patch(h):
                if calls[0]:return h
                calls[0]+=1;assert h.shape[1]==width
                edited=h.clone()
                for i,k in enumerate(donor_keys):edited[i,-1]=acts[(kind,layer,k)].to(h.device,dtype=h.dtype)
                return edited
            handle=module(kind,layer).register_forward_hook(hook_for(kind,patch))
        try:
            g=model.generate(**x,max_new_tokens=1024,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
        finally:
            if handle:handle.remove()
        if component:assert calls[0]==1
        scores=[]
        for i,k in enumerate(keys):
            initial=g[i,width:].tolist();more=[];raw=initial[:]
            censored=tok.eos_token_id not in raw
            if censored:
                full=events[k]['prefix_ids']+raw
                fi=torch.tensor([full],device='cuda')
                continuation_handle=None;replay_calls=[0]
                if component:
                    kind,layer=component;original_position=len(events[k]['prefix_ids'])-1
                    donor_key=donor_keys[i]
                    def replay_patch(h):
                        if replay_calls[0]:return h
                        replay_calls[0]+=1;assert h.shape[1]==len(full)
                        edited=h.clone()
                        edited[0,original_position]=acts[(kind,layer,donor_key)].to(h.device,dtype=h.dtype)
                        return edited
                    continuation_handle=module(kind,layer).register_forward_hook(hook_for(kind,replay_patch))
                try:
                    more=model.generate(input_ids=fi,attention_mask=torch.ones_like(fi),max_new_tokens=2048,
                       do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)[0,len(full):].tolist()
                finally:
                    if continuation_handle:continuation_handle.remove()
                if component:assert replay_calls[0]==1
                raw+=more;assert raw[:len(initial)]==initial
            if tok.eos_token_id in raw:raw=raw[:raw.index(tok.eos_token_id)+1]
            text=tok.decode(events[k]['original_thinking_ids']+raw,skip_special_tokens=False)
            cl,status=parse(text,('no','yes'))
            scores.append({'class':cl,'parse_status':status,'text':text,'initial_censored':censored,
                 'still_censored':tok.eos_token_id not in raw,'initial_token_ids':initial,
                 'continuation_token_ids':more,'token_ids':raw,'original_prefix_preserved':True,
                 'treatment_replayed_at_original_event_if_continued':bool(component and censored)})
        return scores
    print('Loaded; capturing native updates',flush=True)
    with torch.inference_mode():
        for offset in range(0,len(ordered),BATCH):
            keys=ordered[offset:offset+BATCH];x=tensor(keys)
            handles=[]
            for kind,layer in selected:
                def catch(h,kind=kind,layer=layer):
                    for i,k in enumerate(keys):acts[(kind,layer,k)]=h[i,-1].detach().cpu().clone()
                    return h
                handles.append(module(kind,layer).register_forward_hook(hook_for(kind,catch)))
            try:
                base_out=model.generate(**x,max_new_tokens=1,do_sample=False,pad_token_id=tok.pad_token_id,
                     eos_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True)
                base=base_out.scores[0].float();del base_out
            finally:
                for h in handles:h.remove()
            for kind,layer in selected:
                def self_copy(h,kind=kind,layer=layer):
                    edited=h.clone()
                    for i,k in enumerate(keys):edited[i,-1]=acts[(kind,layer,k)].to(h.device,dtype=h.dtype)
                    return edited
                handle=module(kind,layer).register_forward_hook(hook_for(kind,self_copy))
                try:
                    again_out=model.generate(**x,max_new_tokens=1,do_sample=False,pad_token_id=tok.pad_token_id,
                         eos_token_id=tok.eos_token_id,return_dict_in_generate=True,output_scores=True)
                    again=again_out.scores[0].float();del again_out
                finally:handle.remove()
                error=float((again-base).abs().max());self_max=max(self_max,error);assert error<=.001,error
            scores=generate(keys)
            baseline.extend({'key':list(k),'score':s} for k,s in zip(keys,scores))
        (out/'baseline.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in baseline))
        base_lookup={tuple(r['key']):r['score']['class'] for r in baseline}
        rows=[]
        with (out/'behavior.jsonl').open('w') as stream:
            for component in selected:
                label=f'{component[0]}_L{component[1]}'
                for offset in range(0,len(pairs),BATCH):
                    batch=pairs[offset:offset+BATCH]
                    keys=[tuple(r['recipient']) for r in batch];donors=[tuple(r['donor']) for r in batch]
                    scores=generate(keys,component,donors)
                    for r,s in zip(batch,scores):
                        record=dict(r,component=label,score=s,replayed_recipient=base_lookup[tuple(r['recipient'])])
                        rows.append(record);stream.write(json.dumps(record)+'\n')
                    stream.flush();print(label,offset+len(batch),'/',len(pairs),flush=True)
        assert len(rows)==2*len(pairs)
        save(out/'analysis.json',analyze(rows))
    assert script_sha==hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    run={'part':args.part,'n_rows':len(rows),'components':selected,'script_sha256':script_sha,
         'design_sha256':digest(audit),'model_config_sha256':hashlib.sha256((Path(args.model)/'config.json').read_bytes()).hexdigest(),
         'self_copy_max_nats':self_max,'gpu_hours':(time.time()-start)/3600,'torch':torch.__version__,
         'transformers':transformers.__version__,'python':platform.python_version(),'generation':[1024,2048],
         'precision':'bfloat16','attention':'sdpa','training':False}
    save(out/'run.json',run);print('Complete',len(rows),flush=True)

if __name__=='__main__':main()
