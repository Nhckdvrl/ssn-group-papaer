"""E57 frozen all-item bounds; no selection of jointly valid answers."""
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from exposure_data import ROOT,specs,prepare,fingerprint,sha,tokenizer_path,SEEDS
from run_exposure_r2 import parse

W=Path(__file__).resolve().parents[1]


def summarize_bounds(values):
    # Each value: (scene cluster, lower bound, upper bound). Repeated conditions
    # and both history permutations remain inside the original scene cluster.
    grouped=defaultdict(list)
    for key,lo,hi in values:grouped[key].append((lo,hi))
    a=np.array([np.mean(v,axis=0) for _,v in sorted(grouped.items())])
    assert len(a)>0 and np.isfinite(a).all()
    rng=np.random.default_rng(20261003)
    samples=a[rng.integers(0,len(a),size=(5000,len(a)))].mean(1)
    return {'mean_bounds':a.mean(0).tolist(),
        'item_cluster_ci95_envelope':[float(np.quantile(samples[:,0],.025)),float(np.quantile(samples[:,1],.975))],
        'n_rows':len(values),'n_item_clusters':len(a),'bootstrap_seed':20261003,'bootstrap_replicates':5000}


def literal_bounds(r):
    if r['invalid']:return 0.,1.
    value=float(r['answer']==r['literal_answer']);return value,value


def cluster(r):return r['family']+'/'+r['source']['Item']


def cell(rows):
    vals=[(cluster(r),*literal_bounds(r)) for r in rows]
    return {'literal_response':summarize_bounds(vals),'n_invalid':sum(r['invalid'] for r in rows),
        'n_terminated_by_eos':sum(r['terminated_by_eos'] for r in rows),'n':len(rows)}


def difference(rows,field,level_a,level_b):
    matched=defaultdict(dict)
    for r in rows:
        key=(r['family'],r['source']['Item'],r['source']['Condition'])
        key += tuple(r[k] for k in ('context','seed','goal') if k!=field)
        assert r[field] not in matched[key]
        matched[key][r[field]]=r
    values=[]
    for k,v in matched.items():
        assert set(v)=={level_a,level_b}
        a,b=v[level_a],v[level_b]
        assert a['source']==b['source'] and a['literal_answer']==b['literal_answer']
        al,ah=literal_bounds(a);bl,bh=literal_bounds(b)
        values.append((cluster(a),al-bh,ah-bl))
    return summarize_bounds(values)


def main():
    out=W/'results/E57-exposure-summary.json';assert not out.exists()
    config_audit=json.loads((W/'results/E57-effective-config-audit.json').read_text())
    assert config_audit['five_original_endpoints_verified']
    pre=json.loads((W/'results/E57-source-preflight.json').read_text());assert pre['gate_pass']
    models={}
    for m in specs(ROOT):
        cp=m['id'].split('/')[-1];r2='Qwen3-' in cp
        p=ROOT/'runs'/('E57-exposure-'+('r2-' if r2 else '')+cp)
        cfg=json.loads((p/'config.json').read_text());assert cfg.get('complete') and cfg['n']==2944
        assert cfg['model']==m['id'] and cfg['revision']==m['sha'] and cfg['numerical_gate_pass']
        runner=Path(__file__).with_name('run_exposure_r2.py' if r2 else 'run_exposure.py')
        assert cfg['script_sha256']==sha(runner)
        assert cfg['helper_sha256']==pre['helper_sha256']==sha(Path(__file__).with_name('exposure_data.py'))
        assert cfg['generation_config']['do_sample'] is False
        if r2:assert cfg['explicit_generate_kwargs']=={'do_sample':False,'use_model_defaults':False}
        else:assert next(x for x in config_audit['models'] if x['model']==cp)['requested_config_matches_effective']
        tok=AutoTokenizer.from_pretrained(tokenizer_path(ROOT,cp),local_files_only=True)
        planned,audit=prepare(ROOT,tok)
        assert cfg['source_audit']==json.loads(json.dumps(audit))
        assert cfg['input_sha256']==pre['audits'][cp]['input_sha256']==fingerprint(planned)
        saved=json.loads((p/'input-plans.json').read_text());assert saved==planned
        controls=json.loads((p/'numerical-control.json').read_text())
        assert len(controls)==16 and all(c['pass'] for c in controls)
        rows=[json.loads(line) for line in (p/'predictions.jsonl').open()]
        assert len(rows)==len({r['id'] for r in rows})==2944
        eos=cfg['generation_config']['eos_token_id'];eos=eos if isinstance(eos,list) else [eos]
        for r,s in zip(rows,planned):
            assert all(r[k]==v for k,v in s.items())
            ids=r['generated_ids'];assert 0<len(ids)<=8
            assert r['raw_text']==tok.decode(ids,skip_special_tokens=True)
            assert r['terminated_by_eos']==(ids[-1] in eos)
            assert r['answer']==parse(r['raw_text'],r['terminated_by_eos'])
            assert r['invalid']==(r['answer'] is None)
            assert len(r['processed_token_logprobs'])==len(r['raw_token_logprobs'])==len(ids)
            assert all(math.isfinite(v) and v<=.001 for k in ('processed_token_logprobs','raw_token_logprobs') for v in r[k])
            if r2:assert r['every_token_processed_argmax']
        cells=[];effects=[];goal_effects=[]
        families=sorted({r['family'] for r in rows if r['kind']=='critical'})
        for family in families+['shared-active-passive']:
            rr=[r for r in rows if r['family']==family]
            groups=[None] if family=='shared-active-passive' else [False,True]
            for implausible in groups:
                subset=rr if implausible is None else [r for r in rr if ('implaus' in r['source']['Condition'])==implausible]
                for context in ('clean','noisy'):
                    for seed in SEEDS:
                        for goal in ('default','literal'):
                            z=[r for r in subset if (r['context'],r['seed'],r['goal'])==(context,seed,goal)]
                            cells.append({'family':family,'implausible':implausible,'context':context,'seed':seed,'goal':goal,**cell(z)})
                for goal in ('default','literal'):
                    for seed in (*SEEDS,'mean_of_both'):
                        z=[r for r in subset if r['goal']==goal and (seed=='mean_of_both' or r['seed']==seed)]
                        effects.append({'family':family,'implausible':implausible,'goal':goal,'seed':seed,
                            'noisy_minus_clean_literal_response':difference(z,'context','noisy','clean')})
                for context in ('clean','noisy'):
                    for seed in (*SEEDS,'mean_of_both'):
                        z=[r for r in subset if r['context']==context and (seed=='mean_of_both' or r['seed']==seed)]
                        goal_effects.append({'family':family,'implausible':implausible,'context':context,'seed':seed,
                            'literal_goal_minus_default_response':difference(z,'goal','literal','default')})
        models[cp]={'n':len(rows),'revision':m['sha'],'numerical_and_source_gates_pass':True,
            'wall_seconds':cfg['wall_seconds'],'cells':cells,'exposure_effects':effects,'goal_effects':goal_effects}
    out.write_text(json.dumps({'n':23552,'models':models,'all_gates_pass':True,
        'primary':'all-item strict-EOS response bounds, full missingness retained',
        'no_human_exact_replication':True,'no_binary_inference_gold':True,
        'no_pure_channel_or_training_cause_claim':True},indent=2)+'\n')
    print(json.dumps({'n':23552,'all_gates_pass':True}))


if __name__=='__main__':main()
