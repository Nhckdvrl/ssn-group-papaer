"""E97: logically irrelevant review and yes/no versus named criterion goals."""
import argparse, hashlib, itertools, json, platform, subprocess, time
from pathlib import Path
from e95_source_grouping import body, estimate, parse


def records(source):
    cs=[json.loads(s) for s in (source/'contexts.jsonl').read_text().splitlines()][:2]
    old=[json.loads(s) for s in (source/'behavior_merged.jsonl').read_text().splitlines()]
    parents={(r['context'],r['pa'],r['cb'],r['pb']):r for r in old if r['mode']=='thinking' and r['kind']=='criterion'}
    out=[]
    for c in cs:
        name=c['names'][0]
        for pa,cb,pb in itertools.product((1,-1),(0,1),(1,-1)):
            parent=parents[c['context'],pa,cb,pb]; assert parent['query'] is None
            cl=parent['score']['class']; chat=(1 if cl==1 else 0) if cl else None
            common={'context':c['context'],'pa':pa,'cb':cb,'pb':pb,'self_criterion':chat}
            full=body(c,'criterion',pa,cb,pb,None); prefix=full[:full.index('Which single aspect do all three reviewers judge?')]
            for kind in ('name_with_review','bool_no_review','bool_with_review','bool_given_criterion'):
                qis=(1,2) if kind in ('name_with_review','bool_with_review') else (None,)
                asked=(None,) if kind=='name_with_review' else (0,1)
                for qi,aspect in itertools.product(qis,asked):
                    text=prefix
                    if kind=='bool_given_criterion':
                        text+=(f'{name} judges only {"food spiciness" if chat==0 else "service pace"}.\n\n' if chat is not None else 'The criterion is unavailable.\n\n')
                    if qi is not None: text+=f'Reviewer: {name}\nUnlabelled new review: {c["queries"][qi]["text"]}\n\n'
                    if aspect is None:
                        text+=f'Which single aspect does {name} judge? Answer food for food spiciness, or service for service pace.\n'
                        labels=('food','service'); gold=1 if cb==1 else -1
                    else:
                        item='food spiciness' if aspect==0 else 'service pace'
                        text+=f'Does {name} judge reviews based on {item}? Answer yes or no.\n'
                        labels=('no','yes'); gold=1 if cb==aspect else -1
                    out.append(dict(common,kind=kind,query=qi,asked=aspect,labels=labels,gold=gold,body=text))
    assert len(out)==160
    return out


def key(r): return (r['context'],r['pa'],r['cb'],r['pb'],r['kind'],r['query'],r['asked'])


def analyze(rows):
    out={'n_rows':len(rows),'behavior':{},'invariance':{}}
    for kind in sorted({r['kind'] for r in rows}):
        rr=[r for r in rows if r['kind']==kind]; ids=sorted({r['context'] for r in rr}); sm={}
        for field in ('accuracy','valid_fraction'):
            sm[field]=estimate([sum((r['score']['class']==r['gold']) if field=='accuracy' else r['score']['valid'] for r in rr if r['context']==ci)/sum(r['context']==ci for r in rr) for ci in ids])
        out['behavior'][kind]=sm
        inv={}
        for param in ('pa','pb'):
            vals=[]
            for ci in ids:
                lut={(r['pa'],r['cb'],r['pb'],r['query'],r['asked']):r for r in rr if r['context']==ci}
                dif=[]
                for (pa,cb,pb,qi,a),r in lut.items():
                    o=lut[-pa,cb,pb,qi,a] if param=='pa' else lut[pa,cb,-pb,qi,a]
                    dif.append(r['score']['valid'] and o['score']['valid'] and r['score']['class']!=o['score']['class'])
                vals.append(sum(dif)/len(dif))
            inv[param+'_flip']=estimate(vals)
        out['invariance'][kind]=inv
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',default='results/e95/qwen35_discovery'); ap.add_argument('--out',required=True)
    ap.add_argument('--part',type=int,required=True); ap.add_argument('--parts',type=int,default=3); ap.add_argument('--design-only',action='store_true'); a=ap.parse_args()
    src=Path(a.source); p=Path(a.out); p.mkdir(parents=True,exist_ok=True); rs=records(src)
    assert len({key(r) for r in rs})==160
    batches=[rs[i:i+8] for i in range(0,len(rs),8)]; chosen=[(bi,b) for bi,b in enumerate(batches) if bi%a.parts==a.part]
    audit={'n_total':160,'n_part':sum(len(b) for _,b in chosen),'batch_indices':[i for i,_ in chosen],
        'source_context_sha256':hashlib.sha256((src/'contexts.jsonl').read_bytes()).hexdigest(),
        'selection_by_outcome':False,'review_not_new_supervision':True,'goals_only_ask_criterion':True,'private_preference_not_in_given_cue':True}
    (p/'design_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    if a.design_only: print(json.dumps(audit)); return
    assert not (p/'behavior.jsonl').exists()
    (p/'prompts.jsonl').write_text(''.join(json.dumps(r)+'\n' for _,b in chosen for r in b))
    import torch,transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0); model_path='/tmp/ices_models/Qwen3.8-27B'
    tok=AutoTokenizer.from_pretrained(model_path,local_files_only=True); tok.padding_side='left'
    if tok.pad_token_id is None: tok.pad_token_id=tok.eos_token_id
    def prompt(r):
        return tok.apply_chat_template([{'role':'system','content':'Infer rules from the examples. Return only the requested one-word answer.'},
          {'role':'user','content':r['body']}],tokenize=False,add_generation_prompt=True,enable_thinking=True,reasoning_effort='medium')
    (p/'preflight.json').write_text(json.dumps({'args':vars(a),'example':prompt(chosen[0][1][0]),'tokens':1024,'continuation_tokens':2048},indent=2)+'\n')
    t0=time.time(); print('Loading',a.part,flush=True)
    model,loading=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa',output_loading_info=True)
    model.eval(); model.requires_grad_(False); assert not loading.get('missing_keys'),loading
    assert all(any(k in x for k in ('visual.','vision_','mtp.')) for x in loading.get('unexpected_keys',[])),loading
    (p/'loading_info.json').write_text(json.dumps(loading,indent=2,default=str)+'\n')
    out=[]; continued=0
    with torch.inference_mode(),(p/'behavior.jsonl').open('w') as f:
        for bi,rr in chosen:
            xx=tok([prompt(r) for r in rr],return_tensors='pt',padding=True,add_special_tokens=False).to('cuda'); width=xx.input_ids.shape[1]
            gen=model.generate(**xx,max_new_tokens=1024,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
            for j,raw in enumerate(gen[:,width:].tolist()):
                initial=tok.eos_token_id not in raw; before=raw[:]
                if initial:
                    full=xx.input_ids[j][xx.attention_mask[j].bool()].tolist()+raw; fi=torch.tensor([full],device='cuda')
                    more=model.generate(input_ids=fi,attention_mask=torch.ones_like(fi),max_new_tokens=2048,do_sample=False,
                        pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)[0,len(full):].tolist()
                    raw+=more; assert raw[:len(before)]==before; continued+=1
                if tok.eos_token_id in raw: raw=raw[:raw.index(tok.eos_token_id)+1]
                s=tok.decode(raw,skip_special_tokens=False); cl,status=parse(s,rr[j]['labels'])
                d={k:v for k,v in rr[j].items() if k!='body'}
                d['score']={'class':cl,'valid':cl!=0,'parse_status':status,'text':s,'token_ids':raw,'initial_censored':initial,'still_censored':tok.eos_token_id not in raw}
                out.append(d); f.write(json.dumps(d)+'\n'); f.flush(); print('part',a.part,'batch',bi,'completed',len(out),'/',audit['n_part'],flush=True)
    elapsed=time.time()-t0
    # Parts do not contain every preference counterpart; analyze only after merging.
    (p/'summary.json').write_text(json.dumps({'n_rows':len(out),'unresolved':sum(not r['score']['valid'] for r in out),
        'still_censored':sum(r['score']['still_censored'] for r in out)},indent=2)+'\n')
    (p/'run.json').write_text(json.dumps({'args':vars(a),'n_rows':len(out),'batch_indices':audit['batch_indices'],
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'actual_model_type':model.config.model_type,
        'dtype':'bfloat16','attention':'sdpa','training':False,'continued':continued,'elapsed_seconds':elapsed,'gpu_hours':elapsed/3600,
        'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},indent=2)+'\n'); print('complete',len(out),flush=True)


if __name__=='__main__': main()
