"""Run only the early-checkpoint instrument-development stage of E01R."""
import argparse,hashlib,json,os,pathlib,socket,time
from e01r_instruments import (SEMANTICS,base_prompt,case_metrics,choose_natural_prefix,
                              first_sentence,has_answer,intervention,tag_metrics)

ROOT=pathlib.Path(__file__).resolve().parents[1]

def dump(path,data):
    tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(data,indent=2)+'\n'); tmp.replace(path)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--phase',choices=['natural','rollout'],required=True)
    ap.add_argument('--step',default='step_0100'); ap.add_argument('--batch-size',type=int,default=8)
    args=ap.parse_args()
    if args.step!='step_0100':
        raise SystemExit('E01R gate authorizes step_0100 instrument development only')
    start=time.monotonic()
    import torch,transformers
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.set_num_threads(4)
    cfg=json.loads((ROOT/'configs/e01r.json').read_text())
    qdoc=json.loads((ROOT/'configs/e01r_questions.json').read_text())
    questions=[q for q in qdoc['questions'] if q['split']=='instrument_dev']
    model_root=pathlib.Path(os.getenv('L29_MODEL_ROOT','/home/xiang/.cache/l29'))
    modelpath=model_root/args.step
    tok=AutoTokenizer.from_pretrained(modelpath,local_files_only=True); tok.padding_side='left'
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    print('loading',args.step,flush=True)
    model=AutoModelForCausalLM.from_pretrained(modelpath,local_files_only=True,
            torch_dtype=torch.bfloat16,attn_implementation='sdpa').cuda().eval()
    model.config.use_cache=True
    print('loaded',flush=True)
    meta={'status':'INSTRUMENT_DEVELOPMENT_ONLY','step':args.step,
          'model':json.loads((ROOT/'configs/models.json').read_text())['revisions'][args.step],
          'tokenizer_sha256':hashlib.sha256((modelpath/'tokenizer.json').read_bytes()).hexdigest(),
          'torch':torch.__version__,'transformers':transformers.__version__,'host':socket.gethostname(),
          'gpu':torch.cuda.get_device_name(),'CUDA_VISIBLE_DEVICES':os.getenv('CUDA_VISIBLE_DEVICES'),
          'code_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
          'instruments_sha256':hashlib.sha256((ROOT/'src/e01r_instruments.py').read_bytes()).hexdigest(),
          'config_sha256':hashlib.sha256((ROOT/'configs/e01r.json').read_bytes()).hexdigest(),
          'questions_sha256':hashlib.sha256((ROOT/'configs/e01r_questions.json').read_bytes()).hexdigest(),
          'temperature':cfg['temperature'],'top_p':cfg['top_p'],'top_k':cfg['top_k'],
          'dtype':'bfloat16','phase':args.phase}
    def encode(text): return tok.encode(text,add_special_tokens=False)
    @torch.inference_mode()
    def generate(seqs,seed,horizon):
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        batch=tok.pad({'input_ids':seqs},padding=True,return_tensors='pt').to('cuda')
        out=model.generate(**batch,max_new_tokens=horizon,do_sample=True,
            temperature=cfg['temperature'],top_p=cfg['top_p'],top_k=cfg['top_k'],
            use_cache=True,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
        continuations=[]
        for row in out[:,batch.input_ids.shape[1]:].tolist():
            if tok.eos_token_id in row: row=row[:row.index(tok.eos_token_id)+1]
            continuations.append(row)
        return continuations
    raw=ROOT/'results/raw'; raw.mkdir(parents=True,exist_ok=True)
    natural_path=raw/'e01r_dev_step_0100_natural.json'
    if args.phase=='natural':
        records=[]
        for offset in range(0,len(questions),args.batch_size):
            batchq=questions[offset:offset+args.batch_size]
            prompts=[base_prompt(q) for q in batchq]; prompt_ids=[encode(x) for x in prompts]
            seed=301000+offset; outputs=generate(prompt_ids,seed,cfg['natural_max_tokens'])
            for q,p,pids,ids in zip(batchq,prompts,prompt_ids,outputs):
                cut=choose_natural_prefix(ids,tok,cfg['fork_min_tokens'],cfg['fork_max_tokens'])
                rec={'question':q,'state_id':args.step+'_'+q['id'],'prompt':p,'prompt_ids':pids,
                     'generated_ids':ids,'text':tok.decode(ids),'cut':cut,'seed':seed,
                     'has_answer':has_answer(tok.decode(ids))}
                if cut:
                    rec['prefix_ids']=ids[:cut]; rec['prefix_text']=tok.decode(ids[:cut])
                records.append(rec)
            dump(natural_path,{'meta':meta,'complete':False,'records':records})
            print('natural',len(records),'/',len(questions),flush=True)
        meta['elapsed_seconds']=time.monotonic()-start
        dump(natural_path,{'meta':meta,'complete':True,'records':records})
        return
    natural=json.loads(natural_path.read_text()); assert natural['complete']
    states=[r for r in natural['records'] if r['cut']]
    records=[]; rollout_path=raw/'e01r_dev_step_0100_rollout.json'
    for family in cfg['families']:
        for rep in range(cfg['rollouts_per_semantic_action']):
            for offset in range(0,len(states),args.batch_size):
                batchs=states[offset:offset+args.batch_size]
                for selected in SEMANTICS[family]:
                    seqs=[]; specs=[]
                    for state in batchs:
                        q=state['question']; template=q[family+'_template']; mapping=q[family+'_mapping']
                        spec=intervention(family,template,mapping,selected); specs.append(spec)
                        seqs.append(state['prompt_ids']+state['prefix_ids']+encode(spec['text']))
                    other=SEMANTICS[family][1-SEMANTICS[family].index(selected)]
                    for state,spec in zip(batchs,specs):
                        q=state['question']; alt=intervention(family,q[family+'_template'],q[family+'_mapping'],other)
                        assert len(encode(spec['text']))==len(encode(alt['text']))
                    seed=302000+(0 if family=='case' else 10000)+rep*1000+offset
                    outputs=generate(seqs,seed,cfg['rollout_max_tokens'])
                    for state,spec,ids in zip(batchs,specs,outputs):
                        text=tok.decode(ids,skip_special_tokens=True)
                        sentence,complete,sentence_tokens=first_sentence(ids,tok)
                        metrics=case_metrics(sentence,complete) if family=='case' else tag_metrics(text)
                        records.append({'state_id':state['state_id'],'question_id':state['question']['id'],
                            'domain':state['question']['domain'],'family':family,
                            'template':state['question'][family+'_template'],
                            'mapping':state['question'][family+'_mapping'],'selected':selected,
                            'selected_label':spec['selected_label'],'definitions':spec['definitions'],
                            'intervention':spec['text'],'intervention_token_count':len(encode(spec['text'])),
                            'rep':rep,'seed':seed,'ids':ids,'text':text,'sentence_text':sentence,
                            'sentence_tokens':sentence_tokens,'eos':tok.eos_token_id in ids,
                            'answer':has_answer(text),'metrics':metrics})
                dump(rollout_path,{'meta':meta,'complete':False,'records':records})
                print('rollout',family,rep,offset,'/',len(states),flush=True)
    meta['elapsed_seconds']=time.monotonic()-start
    dump(rollout_path,{'meta':meta,'complete':True,'records':records})

if __name__=='__main__': main()
