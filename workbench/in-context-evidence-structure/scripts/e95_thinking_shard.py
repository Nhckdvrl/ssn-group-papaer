"""Execute unchanged E95 thinking batches concurrently; never select by outcome."""
import argparse, hashlib, json, os, platform, subprocess, time
from pathlib import Path
from e95_source_grouping import records, parse


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',default='results/e95/qwen35_discovery')
    ap.add_argument('--part',type=int,required=True); ap.add_argument('--parts',type=int,default=3)
    ap.add_argument('--skip-batches',type=int,default=1); ap.add_argument('--out',required=True)
    ap.add_argument('--design-only',action='store_true'); a=ap.parse_args()
    src=Path(a.source); p=Path(a.out); p.mkdir(parents=True,exist_ok=True)
    pre=json.loads((src/'preflight.json').read_text()); args=pre['args']
    cs=[json.loads(s) for s in (src/'contexts.jsonl').read_text().splitlines()]
    allrows=records(cs); rs=[r for r in allrows if r['context']<args['thinking_n'] and r['kind'] in ('native','criterion','probe')]
    size=args['batch_size']; batches=[rs[i:i+size] for i in range(0,len(rs),size)]
    selected=[(bi,b) for bi,b in enumerate(batches) if bi>=a.skip_batches and (bi-a.skip_batches)%a.parts==a.part]
    meta={'args':vars(a),'original_args':args,'batch_indices':[i for i,_ in selected], 'n_rows':sum(len(b) for _,b in selected),
          'source_script_sha256':hashlib.sha256(Path(__file__).with_name('e95_source_grouping.py').read_bytes()).hexdigest(),
          'contexts_sha256':hashlib.sha256((src/'contexts.jsonl').read_bytes()).hexdigest(),
          'unchanged_frozen_batch_membership':True,'selection_by_outcome':False}
    (p/'dispatch.json').write_text(json.dumps(meta,indent=2)+'\n')
    if a.design_only: print(json.dumps(meta)); return
    assert not (p/'behavior.jsonl').exists()
    import torch,transformers
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(6); torch.manual_seed(0)
    tok=AutoTokenizer.from_pretrained(args['model'],local_files_only=True); tok.padding_side='left'
    if tok.pad_token_id is None: tok.pad_token_id=tok.eos_token_id
    def prompt(r,thinking=True):
        return tok.apply_chat_template([{'role':'system','content':'Infer rules from the examples. Return only the requested one-word answer.'},
          {'role':'user','content':r['body']}],tokenize=False,add_generation_prompt=True,enable_thinking=thinking,
          reasoning_effort='medium')+('' if thinking else 'Answer:')
    assert prompt(allrows[0],False)==pre['example']
    t0=time.time(); print('Loading shard',a.part,flush=True)
    model,loading=AutoModelForCausalLM.from_pretrained(args['model'],local_files_only=True,dtype=torch.bfloat16,device_map='cuda',
        attn_implementation='sdpa',output_loading_info=True)
    model.eval(); model.requires_grad_(False); assert not loading.get('missing_keys'),loading
    assert all(any(k in x for k in ('visual.','vision_','mtp.')) for x in loading.get('unexpected_keys',[])),loading
    (p/'loading_info.json').write_text(json.dumps(loading,indent=2,default=str)+'\n')
    candidates={'criterion':('food','service'),'judgment':('no','yes')}; continued=0; count=0
    with torch.inference_mode(),(p/'behavior.jsonl').open('w') as f:
        for bi,rr in selected:
            xx=tok([prompt(r) for r in rr],return_tensors='pt',padding=True,add_special_tokens=False).to('cuda'); width=xx.input_ids.shape[1]
            gen=model.generate(**xx,max_new_tokens=1024,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
            # Same batch generation and per-row continuation as the frozen engine.
            for j,raw in enumerate(gen[:,width:].tolist()):
                censored=tok.eos_token_id not in raw; old=raw[:]
                if censored:
                    full=xx.input_ids[j][xx.attention_mask[j].bool()].tolist()+raw; fi=torch.tensor([full],device='cuda')
                    more=model.generate(input_ids=fi,attention_mask=torch.ones_like(fi),max_new_tokens=2048,do_sample=False,
                        pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)[0,len(full):].tolist()
                    raw+=more; assert raw[:len(old)]==old; continued+=1
                if tok.eos_token_id in raw: raw=raw[:raw.index(tok.eos_token_id)+1]
                s=tok.decode(raw,skip_special_tokens=False); labels=candidates['criterion' if rr[j]['kind']=='criterion' else 'judgment']; cl,status=parse(s,labels)
                score={'class':cl,'valid':cl!=0,'parse_status':status,'text':s,'token_ids':raw,
                       'initial_censored':censored,'still_censored':tok.eos_token_id not in raw}
                d={k:v for k,v in rr[j].items() if k!='body'}; d.update(mode='thinking',score=score)
                f.write(json.dumps(d)+'\n'); f.flush(); count+=1
                print('part',a.part,'batch',bi,'row',j,'completed',count,'/',meta['n_rows'],'continued',continued,flush=True)
    elapsed=time.time()-t0
    meta.update(actual_model_type=model.config.model_type,continued=continued,elapsed_seconds=elapsed,gpu_hours=elapsed/3600,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),dtype='bfloat16',attention='sdpa',training=False,
        python=platform.python_version(),torch=torch.__version__,transformers=transformers.__version__,pid=os.getpid(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    (p/'run.json').write_text(json.dumps(meta,indent=2)+'\n'); print('complete',count,flush=True)


if __name__=='__main__': main()
