"""E43: target-specific crossed effects, full coverage, original conditional human norm."""
import argparse,collections,hashlib,json
from pathlib import Path
import numpy as np
from commitment_data import prepare,inputs,parse,common_model,specs
from transformers import AutoTokenizer

def interval(x):
    x=np.asarray(x,dtype=float);rng=np.random.default_rng(0)
    boot=x[rng.integers(0,len(x),size=(2000,len(x)))].mean(1)
    return {'mean':float(x.mean()),'item_bootstrap_ci95':np.quantile(boot,[.025,.975]).tolist(),'n_items':len(x)}

EFFECTS={'implicit_at_literal_false':[-1,1,0,0],'implicit_at_literal_true':[0,0,-1,1],
    'literal_at_implicit_false':[-1,0,1,0],'literal_at_implicit_true':[0,-1,0,1],
    'interaction':[1,-1,-1,1]}
CORNERS=['literal_false_meaning_false','literal_false_meaning_true','literal_true_meaning_false','literal_true_meaning_true']

def ratings_summary(rs,source=None):
    assert len(rs)==32 and len({(r['speaker'],r['corner']) for r in rs})==32
    by={ (r['speaker'],r['corner']):r for r in rs};speakers=sorted({r['speaker'] for r in rs})
    def eligible(r):return source is None or (r['prediction'] is not None and r['terminated_by_eos'])
    def value(r):return r['human_mean'] if source is None else r['prediction']
    eligible_n=sum(eligible(r) for r in rs);out={'n':32,'complete_numeric_n':eligible_n,'effects':{}}
    out['corner_means']={}
    for corner in CORNERS:
        rr=[by[(s,corner)] for s in speakers]
        out['corner_means'][corner]={'complete_n':sum(eligible(r) for r in rr),
            'all_item_mean_bounds':[sum(value(r) if eligible(r) else r['min_rating'] for r in rr)/8,
                                    sum(value(r) if eligible(r) else r['max_rating'] for r in rr)/8]}
        if all(eligible(r) for r in rr):out['corner_means'][corner]['point_and_ci']=interval([value(r) for r in rr])
    for name,weights in EFFECTS.items():
        bounds=[];vals=[]
        for s in speakers:
            rr=[by[(s,c)] for c in CORNERS];low=high=0
            for r,w in zip(rr,weights):
                lo,hi=(value(r),value(r)) if eligible(r) else (r['min_rating'],r['max_rating'])
                low+=w*(lo if w>=0 else hi);high+=w*(hi if w>=0 else lo)
            bounds.append((low,high))
            if all(eligible(r) for r in rr):vals.append(sum(w*value(r) for w,r in zip(weights,rr)))
        effect={'all_eight_item_mean_bounds':np.array(bounds).mean(0).tolist(),
            'complete_four_corner_item_n':len(vals),'point_and_ci':interval(vals) if len(vals)==8 else None}
        out['effects'][name]=effect
    if source is not None:
        out['numeric_but_non_eos_n']=sum(r['prediction'] is not None and not r['terminated_by_eos'] for r in rs)
        out['invalid_n']=sum(r['prediction'] is None for r in rs)
        lo=[];hi=[];validerr=[]
        for r in rs:
            t=r['human_mean']
            if eligible(r):e=abs(value(r)-t);lo.append(e);hi.append(e);validerr.append(e)
            else:lo.append(0);hi.append(max(abs(r['min_rating']-t),abs(r['max_rating']-t)))
        out['all_human_mae_bounds']=[float(np.mean(lo)),float(np.mean(hi))]
        out['valid_only_mae_diagnostic']=float(np.mean(validerr)) if validerr else None
        out['complete_value_counts']={str(k):v for k,v in collections.Counter(value(r) for r in rs if eligible(r)).items()}
        # Constant responses can look close to graded human means; these are not fitted models.
        out['constant_50_human_mae']=float(np.mean([abs(50-r['human_mean']) for r in rs]))
    return out

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();rows,audit=prepare(a.root);pre=json.loads(Path('workbench/pragmatic-inference-calibration/results/E43-source-preflight.json').read_text())
assert pre['gate_pass'] and pre['audit']==audit
human={target:ratings_summary([r for r in rows if r['target']==target and r['task'] in ['commitment','trust'] and r['condition']=='original'])
    for target in ['literal','meaning','trust']}
models={}
for cp,mid,revision,parent in specs(a.root):
    run=a.root/'runs'/('E43-commitment-'+cp);config=json.loads((run/'config.json').read_text())
    assert config['complete'] and config['n']==528 and config['source_audit']==audit and config['numerical_gate_pass']
    assert config['model']==mid and config['revision']==revision and config['max_new_tokens']==16 and config['dtype']=='float32'
    assert config['script_sha256']==hashlib.sha256(Path(__file__).with_name('run_commitment_parent.py').read_bytes()).hexdigest()
    assert config['helper_sha256']==hashlib.sha256(Path(__file__).with_name('commitment_data.py').read_bytes()).hexdigest()
    assert all(z['pass'] for z in json.loads((run/'numerical-control.json').read_text()))
    tok=AutoTokenizer.from_pretrained(common_model(a.root,cp),local_files_only=True)
    texts={};plans={}
    for interface in ['bare','common-chat']:
        t,ids,fp=inputs(tok,rows,interface,cp);assert fp==config['input_token_hashes'][interface]==pre['models'][cp][interface]
        texts.update({(interface,r['id']):text for r,text in zip(rows,t)})
        plans.update({(interface,r['id']):r for r in rows})
    raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()];assert len(raw)==len(plans) and len({(r['interface'],r['id']) for r in raw})==528
    for r in raw:
        k=r['interface'],r['id'];source=plans[k]
        assert all(r[key]==v for key,v in source.items() if key not in ['prompt','story','facts','human_values'])
        assert r['prediction']==parse(r['raw_text'],source) and r['invalid']==(r['prediction'] is None)
        assert r['readout_prompt_sha256']==hashlib.sha256(texts[k].encode()).hexdigest()
    interfaces={}
    for interface in ['bare','common-chat']:
        rr=[r for r in raw if r['interface']==interface];binary={}
        for task in ['comprehension','fact-verifier']:
            sel=[r for r in rr if r['task']==task]
            binary[task]={'n':len(sel),'whole_response_valid_n':sum(r['prediction'] is not None for r in sel),
                'complete_valid_n':sum(r['prediction'] is not None and r['terminated_by_eos'] for r in sel),
                'correct_all_n':sum(r['prediction']==r['gold'] and r['terminated_by_eos'] for r in sel),
                'errors_and_invalid':[{'id':r['id'],'gold':r['gold'],'prediction':r['prediction'],'raw':r['raw_text'],'eos':r['terminated_by_eos']}
                    for r in sel if r['prediction']!=r['gold'] or not r['terminated_by_eos']]}
        ratings={}
        for condition in ['original','clarification']:
            ratings[condition]={target:ratings_summary([r for r in rr if r['target']==target and r['task'] in ['commitment','trust'] and r['condition']==condition],True)
                for target in ['literal','meaning','trust']}
        interfaces[interface]={'binary':binary,'ratings':ratings}
    models[cp]={'interfaces':interfaces,'wall_seconds':config['wall_seconds'],
        'config_sha256':hashlib.sha256((run/'config.json').read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256((run/'predictions.jsonl').read_bytes()).hexdigest()}
out={'source_audit':audit,'n':5280,'models':models,'human_conditional_norm':human,'full_gate_pass':True,
    'analysis_protocol':['Primary numeric effects require EOS completion and whole-response integer validity.',
        'No filtered model item analysis. Effects have all-eight-material bounds; point/CI only if all eight four-corner items available.',
        'CI: 2000 item-cluster bootstrap, seed 0; conditional human cell means, no participant-level uncertainty.',
        'No multiplicity-adjusted confirmatory claims; all targets/conditions/readouts reported.',
        'Fresh LLM trust calls differ from human preceding commitment task; no causal architecture or isolated RLHF inference.']}
a.output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({cp:{interface:{'binary':{k:(v['correct_all_n'],v['n']) for k,v in z['binary'].items()},
    'numeric_complete':{cond:{t:q['complete_numeric_n'] for t,q in vv.items()} for cond,vv in z['ratings'].items()}}
    for interface,z in m['interfaces'].items()} for cp,m in models.items()},indent=2))
