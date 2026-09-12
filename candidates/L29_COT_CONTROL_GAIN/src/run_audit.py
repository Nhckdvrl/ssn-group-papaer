"""Bounded behavioral audit. Generation and scoring are separate resumable phases."""
import argparse,hashlib,json,os,pathlib,socket,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
from instruments import FAMILIES,prompt,instruction,choose_prefix,suffixes,violation,has_answer,reasoning_text

def dump(path,data):
    tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(data,indent=2)+'\n'); tmp.replace(path)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--step',required=True); ap.add_argument('--phase',choices=['natural','score','rollout'],required=True); ap.add_argument('--batch-size',type=int,default=8)
    ap.add_argument('--arms',nargs='+',choices=['neutral','active','structural','anaphoric_active','anaphoric_neutral'],default=['neutral','active'])
    ap.add_argument('--output-tag',default='')
    args=ap.parse_args()
    start=time.monotonic()
    print('importing',flush=True)
    import torch,transformers,numpy as np
    from transformers import AutoTokenizer,AutoModelForCausalLM,TopPLogitsWarper
    torch.set_num_threads(4)
    model_root=pathlib.Path(os.getenv('L29_MODEL_ROOT','/home/xiang/.cache/l29'))
    modelpath=str(model_root/args.step)
    tok=AutoTokenizer.from_pretrained(modelpath,local_files_only=True); tok.padding_side='left'
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    print('loading',args.step,flush=True)
    model=AutoModelForCausalLM.from_pretrained(modelpath,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa').cuda().eval()
    model.config.use_cache=True
    print('loaded',flush=True)
    raw=ROOT/'results/raw'; raw.mkdir(exist_ok=True,parents=True)
    bad_masks={}
    meta={'step':args.step,'model':json.loads((ROOT/'configs/models.json').read_text())['revisions'][args.step],
          'tokenizer_sha256':hashlib.sha256((pathlib.Path(modelpath)/'tokenizer.json').read_bytes()).hexdigest(),
          'torch':torch.__version__,'transformers':transformers.__version__,'host':socket.gethostname(),
          'gpu':torch.cuda.get_device_name(),'CUDA_VISIBLE_DEVICES':os.getenv('CUDA_VISIBLE_DEVICES'),
          'code_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
          'instruments_sha256':hashlib.sha256((ROOT/'src/instruments.py').read_bytes()).hexdigest(),
          'temperature':0.6,'top_p':0.95,'top_k':0,'dtype':'bfloat16','seed':290912,'phase':args.phase}
    def encode(s): return tok.encode(s,add_special_tokens=False)
    @torch.inference_mode()
    def generate(seqs,seed,horizon):
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        batch=tok.pad({'input_ids':seqs},padding=True,return_tensors='pt').to('cuda')
        out=model.generate(**batch,max_new_tokens=horizon,do_sample=True,temperature=.6,top_p=.95,top_k=0,use_cache=True,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
        result=[]
        for row in out[:,batch.input_ids.shape[1]:].tolist():
            if tok.eos_token_id in row: row=row[:row.index(tok.eos_token_id)+1]
            result.append(row)
        return result
    @torch.inference_mode()
    def score(ids,prefix_start):
        x=torch.tensor([ids],device='cuda')
        logits=model(x,use_cache=False).logits[0,prefix_start-1:-1].float()
        targets=x[0,prefix_start:]
        losses=torch.nn.functional.cross_entropy(logits,targets,reduction='none').cpu().numpy()
        window=min(16,len(losses))
        rolling=np.convolve(losses,np.ones(window)/window,mode='valid')
        return {'mean_nll':float(losses.mean()),'max_window16_nll':float(rolling.max()),'token_nll':losses.tolist()}
    audit_cfg=json.loads((ROOT/'configs/audit.json').read_text())
    families=tuple(audit_cfg['families'])
    questions=[q for q in json.loads((ROOT/'configs/questions.json').read_text()) if q['split']=='audit']
    if args.phase=='natural':
        jobs=[{'question':q,'family':f,'prompt':prompt(q,f),'seed':290912} for q in questions for f in families]
        records=[]
        for offset in range(0,len(jobs),args.batch_size):
            js=jobs[offset:offset+args.batch_size]; seqs=[encode(j['prompt']) for j in js]
            outputs=generate(seqs,290912+offset,128)
            for j,pids,ids in zip(js,seqs,outputs):
                f=j['family']; q=j['question']; cut=choose_prefix(ids,tok,f,q['keyword'])
                r={**j,'source_step':args.step,'state_id':args.step+'_'+q['id']+'_'+f,
                   'batch_seed':290912+offset,'prompt_ids':pids,'generated_ids':ids,'text':tok.decode(ids),'cut':cut,
                   'initial_32_compliant':not violation(tok.decode(ids[:32]),f,q['keyword']),
                   'initial_128_compliant':not violation(tok.decode(ids),f,q['keyword']),
                   'has_answer':has_answer(tok.decode(ids))}
                # Fixed-length natural reference, irrespective of legality; separate from selected states.
                if len(ids)>=32:
                    refids=ids[:ids.index(tok.eos_token_id)] if tok.eos_token_id in ids else ids
                    if len(refids)>=32:
                        r['reference_all']=score(pids+refids,len(pids))
                        losses=r['reference_all']['token_nll'][:32]
                        r['reference32']={'mean_nll':float(np.mean(losses)),'max_window16_nll':float(np.convolve(losses,np.ones(16)/16,mode='valid').max())}
                if cut:
                    r['prefix_ids']=ids[:cut]; r['prefix_text']=tok.decode(ids[:cut]); r['suffixes']=suffixes(tok,f,q['keyword'])
                    r['natural_support']=score(pids+ids[:cut],len(pids))
                records.append(r)
            print('natural',len(records),'/',len(jobs),flush=True)
            dump(raw/(args.step+'_natural.json'),{'meta':meta,'complete':False,'records':records})
        meta['elapsed_seconds']=time.monotonic()-start
        dump(raw/(args.step+'_natural.json'),{'meta':meta,'complete':True,'records':records})
    elif args.phase=='score':
        states=[]
        for step in json.loads((ROOT/'configs/models.json').read_text())['revisions']:
            doc=json.loads((raw/(step+'_natural.json')).read_text()); assert doc['complete']
            assert doc['meta']['tokenizer_sha256']==meta['tokenizer_sha256'], 'Cannot reuse shared token IDs across different tokenizers'
            states.extend(r for r in doc['records'] if r['cut'] and r['family'] in families)
        records=[]
        for j in states:
            base=j['prompt_ids']+j['prefix_ids']; rec={'state_id':j['state_id'],'source_step':j['source_step'],'question_id':j['question']['id'],'family':j['family'],'support':score(base,len(j['prompt_ids'])),'suffix':{}}
            current_suffixes=suffixes(tok,j['family'],j['question']['keyword'])
            for arm,s in current_suffixes.items():
                sid=encode(s)
                # Suffix log likelihood without window statistic when shorter than 16 tokens.
                x=torch.tensor([base+sid],device='cuda')
                with torch.inference_mode():
                    all_logits=model(x,use_cache=False).logits[0].float()
                    loss=torch.nn.functional.cross_entropy(all_logits[len(base)-1:-1],x[0,len(base):],reduction='none')
                    raw_probs=all_logits[-1].softmax(-1)
                    probs=TopPLogitsWarper(.95)(x,all_logits[-1:].clone()/.6).softmax(-1)[0]
                    if j['family']!='suppression':
                        if j['family'] not in bad_masks:
                            bad_masks[j['family']]=torch.tensor([violation(tok.decode([k],skip_special_tokens=True),j['family'],'') for k in range(len(tok))],device='cuda')
                        badmass=float(probs[bad_masks[j['family']]].sum())
                        raw_badmass=float(raw_probs[bad_masks[j['family']]].sum())
                    else: badmass=None; raw_badmass=None
                rec['suffix'][arm]={'text':s,'token_count':len(sid),'mean_nll':float(loss.mean()),'next_token_bad_mass':badmass,'raw_T1_next_token_bad_mass':raw_badmass,'next_token_eos_mass':float(probs[tok.eos_token_id])}
            records.append(rec)
            if len(records)%10==0: print('scored',len(records),'/',len(states),flush=True)
        meta['elapsed_seconds']=time.monotonic()-start
        dump(raw/(args.step+'_score.json'),{'meta':meta,'complete':True,'records':records})
    else:
        plan=json.loads((ROOT/'configs/audit_rollout_states.json').read_text())
        states=[]
        for step in json.loads((ROOT/'configs/models.json').read_text())['revisions']:
            source_path=raw/(step+'_natural.json')
            if not source_path.exists():
                continue
            doc=json.loads(source_path.read_text())
            assert doc['complete']
            states.extend(r for r in doc['records'] if r['state_id'] in plan[args.step])
        records=[]
        for rep in range(4):
            for offset in range(0,len(states),args.batch_size):
                js=states[offset:offset+args.batch_size]
                for arm in args.arms:
                    seqs=[j['prompt_ids']+j['prefix_ids']+encode(suffixes(tok,j['family'],j['question']['keyword'])[arm]) for j in js]
                    seed=291000+rep*1000+offset
                    outputs=generate(seqs,seed,32)
                    for j,ids in zip(js,outputs):
                        text=tok.decode(ids,skip_special_tokens=True); f=j['family']; kw=j['question']['keyword']
                        rec={'state_id':j['state_id'],'question_id':j['question']['id'],'family':f,'source_step':j['source_step'],'arm':arm,'rep':rep,'seed':seed,'ids':ids,'text':text,'eos':tok.eos_token_id in ids,'answer':has_answer(text),
                             'violation8':violation(reasoning_text(tok.decode(ids[:8],skip_special_tokens=True)),f,kw,complete=tok.eos_token_id in ids[:8]),
                             'violation32':violation(reasoning_text(text),f,kw,complete=tok.eos_token_id in ids or has_answer(text)),
                             'raw_violation32':violation(text,f,kw,complete=tok.eos_token_id in ids),
                             'alphabetic_chars':sum(c.isalpha() for c in reasoning_text(text)),
                             'meta_discussion':bool(__import__('re').search(r'(?i)\b(reminder|requirement|constraint|instruction|uppercase|lowercase)\b|\b(?:not use|avoid)\b',reasoning_text(text)))}
                        records.append(rec)
                print('rollout',rep,offset,'/',len(states),flush=True)
                tag=('_'+args.output_tag) if args.output_tag else ''
                dump(raw/(args.step+'_rollout'+tag+'.json'),{'meta':meta,'complete':False,'records':records})
        meta['elapsed_seconds']=time.monotonic()-start
        tag=('_'+args.output_tag) if args.output_tag else ''
        dump(raw/(args.step+'_rollout'+tag+'.json'),{'meta':meta,'complete':True,'records':records})
if __name__=='__main__': main()
