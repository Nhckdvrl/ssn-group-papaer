"""E38: coverage-aware original numeric ratings, factual priors and predicate boundaries."""
import argparse,json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.stats import pearsonr
from transformers import AutoTokenizer
from projection_data import prepare,inputs,parse_rating
from iqap_data import common_model
from run_iqap_queue import models
from aggregate import estimate

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--allow-incomplete',action='store_true')
selection=ap.add_mutually_exclusive_group();selection.add_argument('--mistral-only',action='store_true');selection.add_argument('--qwen14-only',action='store_true')
a=ap.parse_args();assert not a.output.exists()
if a.qwen14_only:
    from projection_qwen14_data import inputs,common_model
    manifest=json.loads((a.root/'models/qwen25-14-stage-manifest.json').read_text())
    model_specs=[(m['id'].split('/')[-1],m['id'],m['sha']) for m in manifest]
    run_prefix='E41-projection-'
elif a.mistral_only:
    from projection_mistral_data import inputs,common_model
    manifest=json.loads((a.root/'models/mistral-stage-manifest.json').read_text())
    model_specs=[(m['id'].split('/')[-1],m['id'],m['sha']) for m in manifest]
    run_prefix='E39-projection-'
else:
    model_specs=models();run_prefix='E38-projection-'
source,audit=prepare(a.root);sourceidx={r['id']:r for r in source};out={};pending=[];allidx={}
def group_stats(rs):
    items=defaultdict(list)
    for z in rs:items[z['item']].append(z)
    valid=[z for z in rs if z['rating'] is not None]
    norm=[z for z in rs if z['human_mean'] is not None];nv=[z for z in norm if z['rating'] is not None]
    bounds=[]
    for item,zs in items.items():
        normzs=[z for z in zs if z['human_mean'] is not None]
        if normzs:
            lo=sum(abs(z['rating']-z['human_mean']) if z['rating'] is not None else 0 for z in normzs)/len(normzs)
            hi=sum(abs(z['rating']-z['human_mean']) if z['rating'] is not None else max(z['human_mean'],1-z['human_mean']) for z in normzs)/len(normzs)
            bounds.append({'lo':lo,'hi':hi})
    result={'n':len(rs),'valid_n':len(valid),'human_n':len(norm),'valid_human_n':len(nv),
        'numeric_valid_terminated_by_eos_n':sum(z['terminated_by_eos'] for z in valid),
        'numeric_valid_without_eos_n':sum(not z['terminated_by_eos'] for z in valid),
        'valid_fraction':estimate([sum(z['rating'] is not None for z in zs)/len(zs) for zs in items.values()]),
        'budget_exhausted_without_eos_n':sum(z['n_output_tokens']==5 and not z['terminated_by_eos'] for z in rs)}
    if valid:result['valid_only_mean_rating']=float(np.mean([z['rating'] for z in valid]))
    if nv:
        result['valid_only_human_mae']=float(np.mean([abs(z['rating']-z['human_mean']) for z in nv]))
        x=[z['rating'] for z in nv];y=[z['human_mean'] for z in nv]
        result['valid_only_human_pearson']=float(pearsonr(x,y).statistic) if max(x)>min(x) and max(y)>min(y) else None
    if bounds:result['all_human_mae_lower_bound']=estimate([z['lo'] for z in bounds]);result['all_human_mae_upper_bound']=estimate([z['hi'] for z in bounds])
    return result
for cp,mid,rev in model_specs:
    path=a.root/'runs'/(run_prefix+cp)
    if not (path/'config.json').exists() or not json.loads((path/'config.json').read_text()).get('complete'):
        pending.append(cp);continue
    c=json.loads((path/'config.json').read_text());assert c['source_audit']==audit and c['numerical_gate_pass'] and c['revision']==rev
    assert c['model']==mid and c['dtype']=='float32' and c['batch_size']==1 and c['max_new_tokens']==5 and not c['do_sample']
    control=json.loads((path/'numerical-control.json').read_text());assert len(control)==8 and all(z['same_generated_ids'] and z['token_lp_delta']<.001 and z['pass'] for z in control)
    script='run_projection_qwen14.py' if a.qwen14_only else 'run_projection_mistral.py' if a.mistral_only else 'run_projection_parent.py'
    assert c['script_sha256']==hashlib.sha256(Path(__file__).with_name(script).read_bytes()).hexdigest()
    if a.qwen14_only:
        assert c['helper_sha256']==hashlib.sha256(Path(__file__).with_name('projection_qwen14_data.py').read_bytes()).hexdigest()
    rs=[json.loads(l) for l in (path/'predictions.jsonl').read_text().splitlines()];assert len(rs)==c['n']==3520
    idx={(z['id'],z['interface']):z for z in rs};assert len(idx)==len(rs)
    tok=AutoTokenizer.from_pretrained(common_model(a.root,cp),local_files_only=True)
    for interface in ['bare','common-chat']:
        texts,ids,f=inputs(tok,source,interface);assert c['input_token_hashes'][interface]==f
        for r,text in zip(source,texts):
            z=idx[r['id'],interface]
            assert all(z[k]==v for k,v in r.items() if k not in ['system_text','user_text','prompt'])
            assert z['readout_prompt_sha256']==hashlib.sha256(text.encode()).hexdigest()
            assert parse_rating(z['raw_text'])==z['rating'] and z['invalid']==(z['rating'] is None)
    short_prefix_diagnostic={}
    if a.qwen14_only:
        # E42 established that a five-token numeric prefix may continue into prose.
        # Verify raw parsing above, then require EOS for all primary E41 statistics.
        short_groups=defaultdict(list)
        for z in rs:short_groups[z['interface']+'/'+z['task']+'/'+z['embedded_type']].append(z)
        short_prefix_diagnostic={g:group_stats(zs) for g,zs in short_groups.items()}
        rs=[dict(z,rating=z['rating'] if z['terminated_by_eos'] else None) for z in rs]
        idx={(z['id'],z['interface']):z for z in rs}
    groups=defaultdict(list);effect=defaultdict(list)
    for z in rs:
        groups[z['interface']+'/'+z['task']+'/'+z['embedded_type']].append(z)
        if z['task']=='projection' and z['embedded_type']=='p':groups[z['interface']+'/predicate/'+z['verb']].append(z)
    sourcepairs=defaultdict(dict)
    for z in rs:sourcepairs[z['interface'],z['task'],z['embedded_type'],z.get('verb','prior'),z['item']][z['actual_fact_human_prior_type']]=z
    for key,both in sourcepairs.items():
        assert set(both)=={'high_prior','low_prior'}
        h,l=both['high_prior'],both['low_prior'];valid=h['rating'] is not None and l['rating'] is not None
        effect['/'.join(key[:4])].append({'item':key[4],'valid':valid,'delta':h['rating']-l['rating'] if valid else None,
            'human_delta':h['human_mean']-l['human_mean'] if h['human_mean'] is not None and l['human_mean'] is not None else None})
    effects={}
    for g,zs in effect.items():
        ds=[z['delta'] for z in zs if z['valid']];hd=[z['human_delta'] for z in zs if z['human_delta'] is not None]
        effects[g]={'n_pairs':len(zs),'valid_pairs':len(ds),'valid_only_high_minus_low':estimate(ds) if ds else None,
            'human_high_minus_low':estimate(hd) if hd else None,
            'all_pair_delta_mean_bounds':[sum(z['delta'] if z['valid'] else -1 for z in zs)/len(zs),sum(z['delta'] if z['valid'] else 1 for z in zs)/len(zs)]}
    out[cp]={'run':path.name,'config_sha256':hashlib.sha256((path/'config.json').read_bytes()).hexdigest(),
             'input_token_hashes':c['input_token_hashes'],'description':{g:group_stats(zs) for g,zs in groups.items()},'actual_fact_effects':effects}
    if a.qwen14_only:
        out[cp].update(primary_requires_eos=True,short_numeric_prefix_diagnostic=short_prefix_diagnostic)
    allidx[cp]=(idx,c)
paired={}
for left,right in [('Qwen2.5-14B','Qwen2.5-14B-Instruct'),('Qwen2.5-3B','Qwen2.5-3B-Instruct'),('OLMoE-1B-7B-0125','OLMoE-1B-7B-0125-SFT'),('OLMoE-1B-7B-0125-SFT','OLMoE-1B-7B-0125-DPO'),('Qwen3-4B','Qwen3-8B'),('Qwen3-8B','Qwen3-14B'),('Mistral-7B-v0.3','Mistral-7B-Instruct-v0.3')]:
    if left not in allidx or right not in allidx:continue
    li,lc=allidx[left];ri,rc=allidx[right];assert lc['input_token_hashes']==rc['input_token_hashes'] and li.keys()==ri.keys()
    g=defaultdict(lambda:defaultdict(list))
    for key,x in li.items():
        y=ri[key];assert x['readout_prompt_sha256']==y['readout_prompt_sha256']
        if x['human_mean'] is None:continue
        group=x['interface']+'/'+x['task']+'/'+x['embedded_type'];valid=x['rating'] is not None and y['rating'] is not None
        vx=abs(x['rating']-x['human_mean']) if x['rating'] is not None else None
        vy=abs(y['rating']-y['human_mean']) if y['rating'] is not None else None
        mx=max(x['human_mean'],1-x['human_mean'])
        g[group][x['item']].append({'paired_valid':valid,'valid_delta':vy-vx if valid else None,
            'bound_lo':(vy if vy is not None else 0)-(vx if vx is not None else mx),
            'bound_hi':(vy if vy is not None else mx)-(vx if vx is not None else 0)})
    z={}
    for group,items in g.items():
        allrows=[r for zs in items.values() for r in zs]
        means=[np.mean([r['valid_delta'] for r in zs if r['paired_valid']]) for zs in items.values() if any(r['paired_valid'] for r in zs)]
        z[group]={'n_original_human_rows':len(allrows),'n_pair_valid':sum(r['paired_valid'] for r in allrows),
            'valid_only_item_average_mae_delta':estimate(means) if means else None,
            'all_human_item_average_mae_delta_lower_bound':estimate([np.mean([r['bound_lo'] for r in zs]) for zs in items.values()]),
            'all_human_item_average_mae_delta_upper_bound':estimate([np.mean([r['bound_hi'] for r in zs]) for zs in items.values()])}
    paired[left+' -> '+right]=z
assert a.allow_incomplete or not pending,pending
result={'models':out,'paired_stage_size_changes':paired,'pending':pending,'source_audit':audit,'primary_requires_eos':a.qwen14_only,
        'limits':['Generated numeric scalar is not direct belief probability or transparent knowledge.',
                  'Validity differs across endpoint/interfaces; valid-only metrics are selected-case diagnostics, not model rankings.',
                  'Unconditional bounds retain every human item, with absent numeric output allowed anywhere in [0,1].',
                  'Actual-fact high/low tags come from original human facts; four source prior labels mismatch and remain preserved.',
                  '20-item sampling CIs do not represent training-seed/model-population uncertainty.',
                  'Syntactically numeric output without EOS can be truncated; completion counts are audited separately and such ratings cannot transparently establish ability.',
                  'AIC/mixedRSA superiority and belief-representation necessity have not been reproduced or tested.',
                  'No human gold for source negated content or polar cases, no warranted/unwarranted SDT.']}
a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
for cp,v in out.items():print(cp,{g:(d['valid_n'],d['n'],d.get('valid_only_human_mae')) for g,d in v['description'].items() if '/predicate/' not in g})
print('pending',pending)
