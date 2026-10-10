"""E96: logically equal criterion scopes and criterion-only communication."""
import argparse, hashlib, itertools, json, math, platform, subprocess, time
from pathlib import Path
from e95_source_grouping import body, world, CELLS, estimate, parse


def build(source):
    cs=[json.loads(s) for s in (source/'contexts.jsonl').read_text().splitlines()][:2]
    old=[json.loads(s) for s in (source/'behavior_merged.jsonl').read_text().splitlines()]
    cr={(r['context'],r['pa'],r['cb'],r['pb']):r for r in old if r['mode']=='thinking' and r['kind']=='criterion'}
    direct=[]; scopes=[]
    for c in cs:
        na,nb,nc=c['names']
        for pa,cb,pb in itertools.product((1,-1),(0,1),(1,-1)):
            r=cr[c['context'],pa,cb,pb]; assert r['query'] is None
            chat=r['score']['class']; cc=(1 if chat==1 else 0) if chat!=0 else None
            common={'context':c['context'],'pa':pa,'cb':cb,'pb':pb,'self_criterion':cc,'parent_valid':r['score']['valid']}
            base=body(c,'criterion',pa,cb,pb,None)
            before=base[:base.index('Which single aspect do all three reviewers judge?')]
            for kind,name in (('scope_a',na),('scope_b',nb),('scope_a_instruction',na)):
                extra=(f'All three reviewers judge the same aspect, so use any reviewer\'s informative examples to infer {na}\'s aspect.\n' if kind=='scope_a_instruction' else '')
                text=before+extra+f'Which single aspect does {name} judge? Answer food for food spiciness, or service for service pace.\n'
                scopes.append(dict(common,kind=kind,query=None,gold=1 if cb==1 else -1,body=text))
            own=('The reviewer decides yes or no based on exactly one aspect: food spiciness (spicy or mild), '
                 'or service pace (quick or leisurely). The reviewer has a personal preference for one of the two values '
                 'of that aspect. yes means the experience matches that personal preference; no means it does not. '
                 'Infer the rule from the examples.\n\n')
            for d in world(c,pa,cb,pb):
                if d['role']==0: own+=f'Reviewer: {na}\nReview: {d["text"]}\nLabel: {"yes" if d["y"]==1 else "no"}\n\n'
            assert nb not in own and nc not in own
            for qi,q in enumerate(c['queries']):
                suffix=f'Reviewer: {na}\nReview: {q["text"]}\nGive this reviewer\'s yes/no label for the review.\n'
                full=body(c,'native',pa,cb,pb,qi); assert full.endswith(suffix)
                full_prefix=full[:-len(suffix)]
                for kind in ('full_self','own_none','own_self','own_inverse'):
                    cue=None if kind=='own_none' or cc is None else (1-cc if kind=='own_inverse' else cc)
                    clause=('' if kind=='own_none' else 'The relevant aspect is unavailable.\n\n') if cue is None else (
                        f'{na} judges only {"food spiciness" if cue==0 else "service pace"}. Infer their personal preference from their examples.\n\n')
                    text=(full_prefix if kind=='full_self' else own)+clause+suffix
                    if kind!='full_self': assert nb not in text and nc not in text
                    direct.append(dict(common,kind=kind,query=qi,discordant=q['x'][0]!=q['x'][1],gold=pa*q['x'][cb],
                                       cue_criterion=cue,cue_gold=pa*q['x'][cue] if cue is not None else None,body=text))
    return cs,direct,scopes,old


def audit(cs,direct,scopes):
    assert len(direct)==256 and len(scopes)==48
    keys=lambda r:(r['context'],r['pa'],r['cb'],r['pb'],r['kind'],r['query'])
    assert len({keys(r) for r in direct+scopes})==304
    for c in cs:
        for pa in (1,-1):
            raws=[[ (d['text'],d['y']) for d in world(c,pa,cb,pb) if d['role']==0]
                  for cb,pb in itertools.product((0,1),(1,-1))]
            assert all(v==raws[0] for v in raws)
            for cc in (0,1):
                assert all(pa*d['x'][cc]==d['y'] for d in world(c,pa,0,1) if d['role']==0)
    return {'n_contexts':2,'direct_rows':256,'scope_rows':48,'teacher_criterion_rows_used':16,'selection_by_correctness':False,
            'teacher_never_saw_new_review':True,'own_receiver_foreign_source_names_absent':True,'own_raw_examples_unchanged':True,
            'own_both_criterion_worlds_valid':True,'private_preferences_not_provided_in_cue':True,
            'evidence_type':'static interface check, not new model evidence'}


def summarize(rows,old):
    out={'n_rows':len(rows),'behavior':{},'functional_contrasts':{}}
    ids=sorted({r['context'] for r in rows})
    kinds=sorted({r['kind'] for r in rows})
    for kind in kinds:
        rr=[r for r in rows if r['kind']==kind]; sm={}
        for subset in (('all',) if kind.startswith('scope') else ('all','discordant','concordant')):
            ss=[r for r in rr if subset=='all' or r['discordant']==(subset=='discordant')]
            for metric in ('true_accuracy','cue_accuracy','valid_fraction','binary_true_accuracy'):
                if metric=='cue_accuracy' and kind.startswith('scope'): continue
                if metric=='cue_accuracy' and kind=='own_none': continue
                def val(r):
                    if metric=='valid_fraction': return r['score']['valid']
                    pred=r['score'].get('binary_class',r['score']['class']) if metric=='binary_true_accuracy' else r['score']['class']
                    return pred==(r['cue_gold'] if metric=='cue_accuracy' else r['gold'])
                sm[subset+'_'+metric]=estimate([sum(val(r) for r in ss if r['context']==ci)/sum(r['context']==ci for r in ss) for ci in ids])
        out['behavior'][kind]=sm
    if 'full_self' in kinds:
        baseline={(r['context'],r['pa'],r['cb'],r['pb'],r['query']):r for r in old if r['mode']=='direct' and r['kind']=='native'}
        gain=[]; rr=[r for r in rows if r['kind']=='full_self']
        for ci in ids:
            ss=[r for r in rr if r['context']==ci and r['discordant']]
            gain.append(sum((r['score']['class']==r['gold'])-(baseline[r['context'],r['pa'],r['cb'],r['pb'],r['query']]['score']['class']==r['gold']) for r in ss)/len(ss))
        out['functional_contrasts']['full_self_mixed_gain']=estimate(gain)
        diff=[]; flips=[]
        lut={(r['context'],r['pa'],r['cb'],r['pb'],r['query']):r for r in rows if r['kind']=='own_inverse'}
        for ci in ids:
            ss=[r for r in rows if r['kind']=='own_self' and r['context']==ci and r['discordant']]
            diff.append(sum(r['cue_gold']*(r['score']['z']-lut[r['context'],r['pa'],r['cb'],r['pb'],r['query']]['score']['z'])/2 for r in ss)/len(ss))
            flips.append(sum(r['score']['class']!=lut[r['context'],r['pa'],r['cb'],r['pb'],r['query']]['score']['class'] for r in ss)/len(ss))
        out['functional_contrasts'].update(own_criterion_content_response_nats=estimate(diff),own_mixed_flip_rate=estimate(flips))
    if 'scope_a' in kinds:
        for kind in kinds:
            vals=[]
            for ci in ids:
                lut={(r['pa'],r['cb'],r['pb']):r for r in rows if r['kind']==kind and r['context']==ci}
                vals.append(sum(r['score']['valid'] and lut[pa,cb,-pb]['score']['valid'] and r['score']['class']!=lut[pa,cb,-pb]['score']['class'] for (pa,cb,pb),r in lut.items())/len(lut))
            out['functional_contrasts'][kind+'_pB_flip']=estimate(vals)
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',default='results/e95/qwen35_discovery'); ap.add_argument('--out',required=True)
    ap.add_argument('--phase',choices=('direct','scopes'),required=True); ap.add_argument('--design-only',action='store_true'); a=ap.parse_args()
    src=Path(a.source); p=Path(a.out); p.mkdir(parents=True,exist_ok=True); cs,direct,scopes,old=build(src); design=audit(cs,direct,scopes)
    (p/'design_audit.json').write_text(json.dumps(design,indent=2)+'\n')
    if a.design_only: print(json.dumps(design)); return
    assert not (p/'behavior.jsonl').exists(); rs=direct if a.phase=='direct' else scopes
    (p/'prompts.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rs))
    import torch,transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0); model_path='/tmp/ices_models/Qwen3.8-27B'
    tok=AutoTokenizer.from_pretrained(model_path,local_files_only=True); tok.padding_side='left'
    if tok.pad_token_id is None: tok.pad_token_id=tok.eos_token_id
    labels=('no','yes') if a.phase=='direct' else ('food','service')
    enc=[tok.encode(' '+s,add_special_tokens=False) for s in labels]; assert all(len(x)==1 for x in enc); lids=[x[0] for x in enc]
    def prompt(r):
        return tok.apply_chat_template([{'role':'system','content':'Infer rules from the examples. Return only the requested one-word answer.'},
            {'role':'user','content':r['body']}],tokenize=False,add_generation_prompt=True,enable_thinking=a.phase=='scopes',
            reasoning_effort='medium')+('Answer:' if a.phase=='direct' else '')
    (p/'preflight.json').write_text(json.dumps({'args':vars(a),'n_rows':len(rs),'label_ids':lids,'example':prompt(rs[0]),
        'parent_contexts_sha256':hashlib.sha256((src/'contexts.jsonl').read_bytes()).hexdigest()},indent=2)+'\n')
    t0=time.time(); print('Loading',a.phase,flush=True)
    model,loading=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa',output_loading_info=True)
    model.eval(); model.requires_grad_(False); assert not loading.get('missing_keys'),loading
    assert all(any(k in x for k in ('visual.','vision_','mtp.')) for x in loading.get('unexpected_keys',[])),loading
    (p/'loading_info.json').write_text(json.dumps(loading,indent=2,default=str)+'\n')
    out=[]; noop=0.; continued=0
    with torch.inference_mode(),(p/'behavior.jsonl').open('w') as f:
        for st in range(0,len(rs),8):
            rr=rs[st:st+8]; xx=tok([prompt(r) for r in rr],return_tensors='pt',padding=True,add_special_tokens=False).to('cuda'); width=xx.input_ids.shape[1]
            if a.phase=='direct':
                pos=(xx.attention_mask.cumsum(-1)-1).clamp_min(0); lo=model(**xx,position_ids=pos,logits_to_keep=1,use_cache=False).logits[:,-1].float()
                if st==0:
                    again=model(**xx,position_ids=pos,logits_to_keep=1,use_cache=False).logits[:,-1].float(); noop=float((again-lo).abs().max()); assert noop<=.001
                raws=None
            else:
                gen=model.generate(**xx,max_new_tokens=1024,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
                raws=gen[:,width:].tolist()
            for j,r in enumerate(rr):
                if a.phase=='direct':
                    z=float(lo[j,lids[1]]-lo[j,lids[0]]); top=int(lo[j].argmax())
                    score={'z':z,'class':1 if top==lids[1] else -1 if top==lids[0] else 0,'binary_class':1 if z>=0 else -1,'valid':top in lids,'argmax_token':top}
                else:
                    raw=raws[j]; initial_censored=tok.eos_token_id not in raw; orig=raw[:]
                    if initial_censored:
                        full=xx.input_ids[j][xx.attention_mask[j].bool()].tolist()+raw; fi=torch.tensor([full],device='cuda')
                        more=model.generate(input_ids=fi,attention_mask=torch.ones_like(fi),max_new_tokens=2048,do_sample=False,
                            pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)[0,len(full):].tolist()
                        raw+=more; assert raw[:len(orig)]==orig; continued+=1
                    if tok.eos_token_id in raw: raw=raw[:raw.index(tok.eos_token_id)+1]
                    s=tok.decode(raw,skip_special_tokens=False); cl,status=parse(s,labels)
                    score={'class':cl,'valid':cl!=0,'parse_status':status,'text':s,'token_ids':raw,'initial_censored':initial_censored,'still_censored':tok.eos_token_id not in raw}
                d={k:v for k,v in r.items() if k!='body'}; d['score']=score; out.append(d); f.write(json.dumps(d)+'\n'); f.flush()
            print(a.phase,min(st+8,len(rs)),'/',len(rs),'continued',continued,flush=True)
    elapsed=time.time()-t0
    (p/'analysis.json').write_text(json.dumps(summarize(out,old),indent=2)+'\n')
    (p/'run.json').write_text(json.dumps({'args':vars(a),'n_rows':len(out),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'actual_model_type':model.config.model_type,'dtype':'bfloat16','attention':'sdpa','training':False,'noop_max':noop,'continued':continued,
        'elapsed_seconds':elapsed,'gpu_hours':elapsed/3600,'parent_criterion_rows':16,'parent_correctness_selection':False,
        'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},indent=2)+'\n')
    print('complete',len(out),elapsed,flush=True)


if __name__=='__main__': main()
