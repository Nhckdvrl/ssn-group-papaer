"""E63 exact natural source candidates; independent full-logit scoring gate."""
import argparse
import json
import math
import time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from violation_data import prepare, fingerprint, common_path, sha, dependencies, specs


def main():
    ap=argparse.ArgumentParser()
    for k in ['root', 'model', 'output']:ap.add_argument('--'+k, type=Path, required=True)
    for k in ['model-id', 'revision']:ap.add_argument('--'+k, required=True)
    a=ap.parse_args();assert not a.output.exists()
    m=next(m for m in specs(a.root) if m['id']==a.model_id);assert m['sha']==a.revision
    marker=json.loads((a.model/'DOWNLOAD_COMPLETE.json').read_text())
    assert marker['model']==a.model_id and marker['revision']==a.revision
    tok=AutoTokenizer.from_pretrained(common_path(a.root,m), local_files_only=True)
    rows, audit, nulls=prepare(a.root, tok)
    audit=json.loads(json.dumps(audit))
    pre=json.loads((Path(__file__).resolve().parents[1]/'results/E63-source-preflight.json').read_text())
    assert pre['gate_pass'] and pre['models']==specs(a.root)
    assert pre['audits'][a.model_id.split('/')[-1]]['source_audit']==audit and pre['audits'][a.model_id.split('/')[-1]]['input_sha256']==fingerprint(rows,nulls)
    assert pre['helper_sha256']==sha(Path(__file__).with_name('violation_data.py')) and pre['dependencies']==dependencies()
    a.output.mkdir(parents=True)
    (a.output/'input-plans.json').write_text(json.dumps({'rows':rows,'nulls':nulls}, ensure_ascii=False))
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    started=time.monotonic()
    model=AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, torch_dtype=torch.float32,
        device_map={'':0}, weights_only=True, attn_implementation='eager').eval()

    @torch.inference_mode()
    def read(p, independent=False):
        scores=[]
        atomic = all(len(ids) == p['first']+1 and end == len(ids)
                     for ids, end in zip(p['ids'], p['content_ends']))
        if atomic and not independent:
            prefix = p['ids'][0][:p['first']]
            assert all(ids[:-1] == prefix for ids in p['ids'])
            inp = torch.tensor([prefix], device=model.device)
            hidden = model.model(input_ids=inp, use_cache=False).last_hidden_state
            lp = model.lm_head(hidden[0, -1]).float().log_softmax(-1)
            scores = [{'full_logprob':float(lp[ids[-1]]), 'content_logprob':float(lp[ids[-1]])} for ids in p['ids']]
        for ids, end in ([] if scores else zip(p['ids'], p['content_ends'])):
            inp=torch.tensor([ids], device=model.device)
            if independent:
                logits=model(input_ids=inp, use_cache=False).logits[0,p['first']-1:len(ids)-1].float()
            else:
                hidden=model.model(input_ids=inp, use_cache=False).last_hidden_state
                logits=model.lm_head(hidden[0,p['first']-1:len(ids)-1]).float()
            labels=inp[0,p['first']:]
            lp=logits.log_softmax(-1).gather(1, labels[:,None]).flatten()
            scores.append({'full_logprob':float(lp.sum()), 'content_logprob':float(lp[:end-p['first']].sum())})
        out={'choice_scores':scores}
        for key in ['full_logprob','content_logprob']:
            lp=np.array([s[key] for s in scores]);z=float(np.logaddexp.reduce(lp))
            out[key]={'conditional_probs':np.exp(lp-z).tolist(), 'candidate_mass':math.exp(z), 'argmax':int(lp.argmax())}
        return out

    controls=[]
    conditions=sorted({(r['alias'],r['interface'],r['kind']) for r in rows})
    for alias,interface,kind in conditions:
        selected=[r for r in rows if r['alias']==alias and r['interface']==interface and r['kind']==kind]
        for r in [selected[0],selected[-1]]:
            x,y,z=read(r['plan']),read(r['plan']),read(r['plan'],True)
            delta=max(abs(u[k]-v[k]) for u,v in zip(x['choice_scores'],y['choice_scores']) for k in ['full_logprob','content_logprob'])
            independent=max(abs(u[k]-v[k]) for u,v in zip(x['choice_scores'],z['choice_scores']) for k in ['full_logprob','content_logprob'])
            prob=max(abs(u-v) for k in ['full_logprob','content_logprob'] for u,v in zip(x[k]['conditional_probs'],z[k]['conditional_probs']))
            agrees=all(x[k]['argmax']==z[k]['argmax'] for k in ['full_logprob','content_logprob'])
            controls.append({'id':r['id'],'repeat_lp_delta':delta,'independent_full_lp_delta':independent,
                'probability_delta':prob,'argmax_agrees':agrees,'pass':delta<1e-6 and independent<.001 and prob<.001 and agrees})
    (a.output/'numerical-control.json').write_text(json.dumps(controls,indent=2))
    assert all(c['pass'] for c in controls), 'E63 numerical gate failed; zero experiment predictions'
    config={'model':a.model_id, 'revision':a.revision, 'stage':m['stage'], 'family':m['family'],
        'source_audit':audit,'input_sha256':fingerprint(rows,nulls),'n':len(rows),'dtype':'float32',
        'batch_size':1,'attention':'eager','tf32':False,'numerical_gate_pass':True,
        'common_tokenizer':str(common_path(a.root,m)),'script_sha256':sha(Path(__file__)),
        'helper_sha256':sha(Path(__file__).with_name('violation_data.py')),'dependency_sha256':dependencies(),
        'null_readout':{i:read(p) for i,p in nulls.items()}}
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    with (a.output/'predictions.jsonl').open('w') as f:
        for i,r in enumerate(rows):
            f.write(json.dumps({**r,**read(r['plan'])},ensure_ascii=False)+'\n');f.flush()
            if i%50==0:print(json.dumps({'done':i+1,'total':len(rows)}),flush=True)
    config.update(complete=True,wall_seconds=time.monotonic()-started)
    (a.output/'config.json').write_text(json.dumps(config,indent=2))
    print(json.dumps({'complete':True,'n':len(rows)}),flush=True)


if __name__=='__main__':main()
