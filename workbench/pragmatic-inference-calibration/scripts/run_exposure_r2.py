"""E57 native generation, strict parser, independent raw-logit gate."""
import argparse
import copy
import json
import re
import time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from exposure_data import prepare,fingerprint,ROOT,specs,tokenizer_path,sha,SEEDS


def parse(text,terminated):
    m=re.fullmatch(r'\s*(Yes|No)\s*[.!]?\s*',text,re.I)
    return m.group(1).title() if m and terminated else None


def main():
    ap=argparse.ArgumentParser()
    for n in ('model','output'):ap.add_argument('--'+n,type=Path,required=True)
    for n in ('model-id','revision'):ap.add_argument('--'+n,required=True)
    a=ap.parse_args();assert not a.output.exists()
    m=next(m for m in specs(ROOT) if m['id']==a.model_id);assert m['sha']==a.revision
    marker=json.loads((a.model/'DOWNLOAD_COMPLETE.json').read_text())
    assert marker['model']==a.model_id and marker['revision']==a.revision
    tok=AutoTokenizer.from_pretrained(tokenizer_path(ROOT,a.model.name),local_files_only=True)
    rows,audit=prepare(ROOT,tok)
    pre=json.loads((Path(__file__).resolve().parents[1]/'results/E57-source-preflight.json').read_text())
    helper=Path(__file__).with_name('exposure_data.py')
    assert pre['gate_pass'] and pre['helper_sha256']==sha(helper)
    assert pre['audits'][a.model.name]['source_audit']==json.loads(json.dumps(audit))
    assert pre['audits'][a.model.name]['input_sha256']==fingerprint(rows)
    a.output.mkdir(parents=True)
    (a.output/'input-plans.json').write_text(json.dumps(rows))
    start=time.monotonic();torch.set_num_threads(8)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,
        torch_dtype=torch.float32,attn_implementation='eager',device_map={'':0},weights_only=True).eval()
    gen=copy.deepcopy(model.generation_config);gen.do_sample=False;gen.max_new_tokens=8
    gen.return_dict_in_generate=True;gen.output_scores=True;gen.output_logits=True;gen.use_cache=True
    assert gen.num_beams==1
    eos=gen.eos_token_id if isinstance(gen.eos_token_id,list) else [gen.eos_token_id]
    gen.pad_token_id=tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    @torch.inference_mode()
    def read(r,gate=False):
        ids=r['input_ids'];x=torch.tensor([ids],device=model.device)
        z=model.generate(input_ids=x,attention_mask=torch.ones_like(x),generation_config=gen,do_sample=False,use_model_defaults=False)
        new=z.sequences[0,len(ids):].tolist();text=tok.decode(new,skip_special_tokens=True)
        terminated=bool(new and new[-1] in eos)
        selected_argmax=all(int(s[0].argmax())==t for s,t in zip(z.scores,new))
        assert selected_argmax,'effective decoding is not greedy'
        score=[float(s[0].float().log_softmax(-1)[t]) for s,t in zip(z.scores,new)]
        raw=[float(s[0].float().log_softmax(-1)[t]) for s,t in zip(z.logits,new)]
        result={'every_token_processed_argmax':selected_argmax,'generated_ids':new,'raw_text':text,'terminated_by_eos':terminated,
            'answer':parse(text,terminated),'invalid':parse(text,terminated) is None,
            'processed_token_logprobs':score,'raw_token_logprobs':raw}
        if gate:
            independent=model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False).logits[0,-1].float()
            first=z.logits[0][0].float()
            result['gate']={'raw_logprob_max_delta':float((independent.log_softmax(-1)-first.log_softmax(-1)).abs().max()),
                'raw_argmax_same':int(independent.argmax())==int(first.argmax())}
        return result

    controls=[]
    for context in ('clean','noisy'):
        for seed in SEEDS:
            for goal in ('default','literal'):
                group=[r for r in rows if (r['context'],r['seed'],r['goal'])==(context,seed,goal)]
                for r in (group[0],group[-1]):
                    x,y=read(r,True),read(r)
                    delta=max([abs(u-v) for u,v in zip(x['processed_token_logprobs'],y['processed_token_logprobs'])] or [0])
                    same=x['generated_ids']==y['generated_ids']
                    c={'id':r['id'],**x['gate'],'same_generated_ids':same,'repeat_score_delta':delta}
                    c['pass']=same and delta<.001 and c['raw_logprob_max_delta']<.001 and c['raw_argmax_same']
                    controls.append(c)
    (a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2))
    assert all(c['pass'] for c in controls),'E57 gate failed: zero scientific predictions'
    cfg={'model':a.model_id,'revision':a.revision,'n':len(rows),'source_audit':audit,
        'input_sha256':fingerprint(rows),'helper_sha256':sha(helper),'script_sha256':sha(Path(__file__)),
        'numerical_gate_pass':True,'explicit_generate_kwargs':{'do_sample':False,'use_model_defaults':False},'generation_config':gen.to_dict(),'dtype':'float32','attention':'eager',
        'no_source_answer_in_prompt':True,'no_context_truncation':True}
    (a.output/'config.json').write_text(json.dumps(cfg,indent=2))
    with (a.output/'predictions.jsonl').open('w') as f:
        for i,r in enumerate(rows):
            f.write(json.dumps({**r,**read(r)})+'\n');f.flush()
            if i%25==0:print(json.dumps({'done':i+1,'n':len(rows)}),flush=True)
    cfg.update(complete=True,wall_seconds=time.monotonic()-start)
    (a.output/'config.json').write_text(json.dumps(cfg,indent=2))
    print(json.dumps({'complete':True,'n':len(rows)}),flush=True)


if __name__=='__main__':main()
