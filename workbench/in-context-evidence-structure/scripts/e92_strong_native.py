"""E92 strong native diagnostic, fixed first four contexts; no hybrid-cache masks."""
import argparse,hashlib,json,platform,re,subprocess,time
from pathlib import Path


def records(cs):
    out=[]
    for c in cs:
        na,nb=c['names']
        for kind in ('native','oracle','probe'):
            for rel in (('same',) if kind=='probe' else ('same','different')):
                for world in ('base','flip'):
                    cb=c['base_b_criterion']^(world=='flip');ca=cb^(rel=='different');role=1 if kind=='probe' else 0
                    head=("Each reviewer judges only one aspect of a restaurant: food or service. A positive judgment means that aspect was good; a negative judgment means it was bad. "
                          "Reviewers may use different label words, whose meanings can be inferred from their examples.\n"
                          f"{na} and {nb} judge {'the same aspect' if rel=='same' else 'different aspects'}. Infer their criteria from the examples.\n\n")
                    if kind=='oracle':head+=f"{na} judges only the {'food' if ca==0 else 'service'}.\n\n"
                    for d in c['demos']:
                        sign=d['food'] if d['role']==0 else (d['food'],d['service'])[cb]
                        head+=f"Reviewer: {c['names'][d['role']]}\nReview: {d['text']}\nLabel: {'positive' if sign>0 else 'negative'}\n\n"
                    for qi,q in enumerate(c['queries'][:4]):
                        if kind=='oracle' and q['food']==q['service']:continue
                        gold=(q['food'],q['service'])[cb if role else ca]
                        out.append({'uid':f"{c['context']}.{kind}.{rel}.{world}.{qi}",'context':c['context'],'kind':kind,'relation':rel,'world':world,'query':qi,
                                    'discordant':q['food']!=q['service'],'gold':gold,
                                    'body':head+f"Reviewer: {c['names'][role]}\nReview: {q['text']}\nGive this reviewer's label for the review.\n"})
    return out


def parse(text):
    if '</think>' not in text:return 0,'thinking_not_closed'
    tail=text.rsplit('</think>',1)[1]
    tail=re.sub(r'<\|[^>]*\|>','',tail).strip().replace('**','').replace('__','')
    exact=re.fullmatch(r'(?is)\s*(?:Answer:\s*)?(positive|negative)[.!]?\s*',tail)
    if exact:return (1 if exact.group(1).lower()=='positive' else -1),'valid'
    lines=re.findall(r'(?im)^\s*Answer:\s*(positive|negative)[.!]?\s*$',tail)
    if lines:return (1 if lines[-1].lower()=='positive' else -1),'valid_final_line'
    return 0,'unresolved_final_answer'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',default='/tmp/ices_models/Qwen3.8-27B');ap.add_argument('--source',default='results/e92/qwen3_discovery/contexts.jsonl')
    ap.add_argument('--out',required=True);ap.add_argument('--n',type=int,default=4);ap.add_argument('--batch-size',type=int,default=8)
    ap.add_argument('--tokens',type=int,default=1024);ap.add_argument('--continuation-tokens',type=int,default=2048);a=ap.parse_args()
    p=Path(a.out);p.mkdir(parents=True,exist_ok=True);assert not(p/'behavior.jsonl').exists()
    cs=[json.loads(x) for x in Path(a.source).read_text().splitlines()][:a.n];rows=records(cs);assert len(rows)==32*a.n
    (p/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs));(p/'prompts.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    import torch,transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(6);torch.manual_seed(0);tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True);tok.padding_side='left'
    if tok.pad_token_id is None:tok.pad_token_id=tok.eos_token_id
    system="Infer the requested reviewer's criterion and label. Return exactly the requested label word."
    def prompt(r,thinking):return tok.apply_chat_template([{'role':'system','content':system},{'role':'user','content':r['body']}],tokenize=False,add_generation_prompt=True,enable_thinking=thinking,reasoning_effort='medium')+('' if thinking else 'Answer:')
    labels=[tok.encode(' '+s,add_special_tokens=False) for s in ('negative','positive')];assert all(len(x)==1 for x in labels);lid=[x[0] for x in labels]
    (p/'preflight.json').write_text(json.dumps({'args':vars(a),'n_records':len(rows),'actual_model_config':json.loads((Path(a.model)/'config.json').read_text()),'label_ids':lid,
                                              'direct_example':prompt(rows[0],False),'thinking_example':prompt(rows[0],True),'hybrid_source_gate':False},indent=2)+'\n')
    t0=time.time();print('Loading strong model',flush=True)
    model,loading=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa',output_loading_info=True)
    model.eval();model.requires_grad_(False);assert not loading.get('missing_keys'),loading
    assert all(any(k in x for k in ('visual.','vision_','mtp.')) for x in loading.get('unexpected_keys',[])),loading.get('unexpected_keys',[])[:10]
    (p/'loading_info.json').write_text(json.dumps(loading,indent=2,default=str)+'\n');print('Strong model loaded',flush=True)
    def batch(prompts):return tok(prompts,return_tensors='pt',padding=True,add_special_tokens=False).to('cuda')
    summary={};max_noop=0.;continued=0
    with torch.inference_mode(),(p/'behavior.jsonl').open('w') as stream:
        for mode in ('direct','thinking'):
            answers=[]
            for st in range(0,len(rows),a.batch_size):
                rr=rows[st:st+a.batch_size];xx=batch([prompt(r,mode=='thinking') for r in rr]);width=xx.input_ids.shape[1]
                if mode=='direct':
                    pos=(xx.attention_mask.cumsum(-1)-1).clamp_min(0)
                    lo=model(**xx,position_ids=pos,logits_to_keep=1,use_cache=False).logits[:,-1].float()
                    if st==0:
                        again=model(**xx,position_ids=pos,logits_to_keep=1,use_cache=False).logits[:,-1].float();max_noop=float((again-lo).abs().max());assert max_noop<1e-4
                    z=(lo[:,lid[1]]-lo[:,lid[0]]).tolist();top=lo.argmax(-1).tolist()
                    scores=[{'class':1 if t==lid[1] else -1 if t==lid[0] else 0,'z':v,'argmax_token':t,'valid':t in lid} for v,t in zip(z,top)]
                else:
                    gen=model.generate(**xx,max_new_tokens=a.tokens,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
                    scores=[]
                    for j,raw in enumerate(gen[:,width:].tolist()):
                        original=raw[:];censored=tok.eos_token_id not in raw
                        if censored:
                            full=xx.input_ids[j][xx.attention_mask[j].bool()].tolist()+raw
                            fi=torch.tensor([full],device='cuda');more=model.generate(input_ids=fi,attention_mask=torch.ones_like(fi),max_new_tokens=a.continuation_tokens,do_sample=False,
                                pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)[0,len(full):].tolist()
                            raw+=more;assert raw[:len(original)]==original;continued+=1
                        if tok.eos_token_id in raw:raw=raw[:raw.index(tok.eos_token_id)+1]
                        text=tok.decode(raw,skip_special_tokens=False);cl,status=parse(text)
                        scores.append({'class':cl,'valid':cl!=0,'parse_status':status,'text':text,'token_ids':raw,'initial_censored':censored,'still_censored':tok.eos_token_id not in raw})
                for r,s in zip(rr,scores):
                    d={k:v for k,v in r.items() if k!='body'};d.update(mode=mode,score=s);answers.append(d);stream.write(json.dumps(d)+'\n');stream.flush()
                print(mode,min(st+a.batch_size,len(rows)),'/',len(rows),'continued',continued,flush=True)
            sm={}
            for kind in ('native','oracle','probe'):
                for rel in (('same',) if kind=='probe' else ('same','different')):
                    aa=[r for r in answers if r['kind']==kind and r['relation']==rel]
                    sm[kind+'_'+rel]={'n':len(aa),'accuracy':sum(r['score']['class']==r['gold'] for r in aa)/len(aa),'valid_fraction':sum(r['score']['valid'] for r in aa)/len(aa)}
                    for disc in (False,True):
                        bb=[r for r in aa if r['discordant']==disc]
                        if bb:sm[kind+'_'+rel]['discordant_accuracy' if disc else 'concordant_accuracy']=sum(r['score']['class']==r['gold'] for r in bb)/len(bb)
            summary[mode]=sm
    elapsed=time.time()-t0
    run={'args':vars(a),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_contexts_sha256':hashlib.sha256(Path(a.source).read_bytes()).hexdigest(),
         'n_records':len(rows),'source_context_indices':[c['context'] for c in cs],'actual_model_type':model.config.model_type,'dtype':'bfloat16','attention':'sdpa','training':False,
         'cache_or_activation_interventions':False,'direct_noop_max':max_noop,'continued_all_initially_censored':continued,'elapsed_seconds':elapsed,'gpu_hours':elapsed/3600,
         'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    (p/'run.json').write_text(json.dumps(run,indent=2)+'\n');(p/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
