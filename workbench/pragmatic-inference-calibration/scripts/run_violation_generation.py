"""E64: exact E63 token prefixes, raw greedy generation, no prompt repairs."""
import argparse
import json
import time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from violation_data import specs,common_path,sha,dependencies

def main():
    ap=argparse.ArgumentParser()
    for k in ['root','model','output']:ap.add_argument('--'+k,type=Path,required=True)
    for k in ['model-id','revision']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();assert not a.output.exists()
    m=next(m for m in specs(a.root) if m['id']==a.model_id);assert m['sha']==a.revision
    cp=m['id'].split('/')[-1];src=a.root/'runs'/('E63-violation-reason-'+cp)
    cfg=json.loads((src/'config.json').read_text());assert cfg['complete'] and cfg['n']==1380 and cfg['revision']==m['sha']
    pre=json.loads((Path(__file__).resolve().parents[1]/'results/E64-source-preflight.json').read_text());assert pre['gate_pass']
    assert pre['models']==specs(a.root) and pre['source_hashes'][cp]=={f:sha(src/f) for f in ['config.json','predictions.jsonl','input-plans.json']}
    rows=[json.loads(s) for s in (src/'predictions.jsonl').open() if json.loads(s)['interface']=='common-chat']
    assert len(rows)==690 and len({r['id'] for r in rows})==690
    tok=AutoTokenizer.from_pretrained(common_path(a.root,m),local_files_only=True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    started=time.monotonic()
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,
        device_map={'':0},weights_only=True,attn_implementation='eager').eval()
    @torch.inference_mode()
    def generate(r,check=False):
        p=r['plan'];prefix=p['ids'][0][:p['first']];terminal=p['ids'][0][-1]
        assert all(ids[:p['first']]==prefix and ids[-1]==terminal for ids in p['ids'])
        inp=torch.tensor([prefix],device=model.device)
        gc=GenerationConfig(do_sample=False,max_new_tokens=256,eos_token_id=terminal,pad_token_id=terminal,use_cache=True,repetition_penalty=1.)
        z=model.generate(input_ids=inp,generation_config=gc,return_dict_in_generate=True,output_scores=True)
        ids=z.sequences[0,len(prefix):].tolist();ended=bool(ids and ids[-1]==terminal)
        response=tok.decode(ids[:-1] if ended else ids,skip_special_tokens=False)
        s=response.strip();parsed=next((i for i,t in enumerate(r['targets']) if s in [t,t+'.']),None)
        first=z.scores[0][0].float().log_softmax(-1)
        out={'id':r['id'],'alias':r['alias'],'kind':r['kind'],'response':response,'token_ids':ids,'eos':ended,
             'truncated':not ended and len(ids)==256,'prediction':parsed,'lp_prediction':r['full_logprob']['argmax'],
             'prefix_ids':prefix,'raw_first_argmax':int(first.argmax()),'unrestricted_first_probability':float(first.exp().max())}
        for k in ['scene','context','utterance','attribute','expected_index','human_counts','human_n']:
            if k in r:out[k]=r[k]
        if check:
            direct=model(input_ids=inp,use_cache=False).logits[0,-1].float().log_softmax(-1)
            delta=float((direct-first).abs().max());out['first_step_max_lp_delta']=delta
            out['numeric_pass']=delta<.001 and int(direct.argmax())==int(first.argmax())
        return out
    controls=[]
    for alias,kind in sorted({(r['alias'],r['kind']) for r in rows}):
        rs=[r for r in rows if r['alias']==alias and r['kind']==kind]
        controls.extend(generate(r,True) for r in [rs[0],rs[-1]])
    a.output.mkdir(parents=True)
    (a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2))
    assert len(controls)==16 and all(r['numeric_pass'] for r in controls), 'E64 generation first-step gate failed; no natural predictions'
    conf={'model':m['id'],'revision':m['sha'],'n':690,'dtype':'float32','attention':'eager','batch_size':1,'tf32':False,
          'script_sha256':sha(Path(__file__)),'dependencies':dependencies(),'source_hashes':pre['source_hashes'][cp],
          'generation':'raw greedy repetition_penalty1 max256 same E63 terminal','numerical_gate_pass':True}
    (a.output/'config.json').write_text(json.dumps(conf,indent=2))
    with (a.output/'predictions.jsonl').open('w') as f:
        for i,r in enumerate(rows):
            f.write(json.dumps(generate(r),ensure_ascii=False)+'\n');f.flush()
            if i%25==0:print(json.dumps({'done':i+1,'total':len(rows)}),flush=True)
    conf.update(complete=True,wall_seconds=time.monotonic()-started)
    (a.output/'config.json').write_text(json.dumps(conf,indent=2));print(json.dumps({'complete':True,'n':len(rows)}),flush=True)

if __name__=='__main__':main()
