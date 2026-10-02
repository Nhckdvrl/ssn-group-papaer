"""E33 fixed semantic strength and response distribution, no binary warrant."""
import argparse,json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import rel_entr
from aggregate import estimate

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--allow-incomplete',action='store_true');a=ap.parse_args();assert not a.output.exists()
models={};pending=[];by_model={}

def metrics(r,key):
    p=np.array(r[key+'_normalized']);h=np.array(r['human_counts'])/30
    yes=p[:2].sum();hy=h[:2].sum();definite=p[[0,2]].sum();hd=h[[0,2]].sum()
    mid=(p+h)/2
    m={'polarity_mae':abs(yes-hy),'definite_probability':float(definite),'human_definite':float(hd),
       'definite_minus_human':float(definite-hd),'four_way_brier':float(np.square(p-h).sum()),
       'js_divergence_nats':float((rel_entr(p,mid).sum()+rel_entr(h,mid).sum())/2)}
    if hy!=.5:
        yes_majority=hy>.5;first=0 if yes_majority else 2
        m['polarity_correct']=float((yes>.5)==yes_majority)
        m['conditional_definite_minus_human']=float(p[first]/p[first:first+2].sum()-h[first]/h[first:first+2].sum())
    return m

def summarize(rs,key):
    values=[metrics(r,key) for r in rs]
    out={k:estimate([r[k] for r in values if k in r]) for k in values[0]}
    # Group repeated transcript/excerpt items without changing the item-weighted estimand.
    for k in out:
        groups=defaultdict(list)
        for r,v in zip(rs,values):
            if k in v:groups[r['classification']+'/'+r['source']].append(v[k])
        sums=np.array([sum(v) for v in groups.values()]);counts=np.array([len(v) for v in groups.values()])
        rng=np.random.default_rng(0);idx=rng.integers(len(sums),size=(2000,len(sums)))
        boot=sums[idx].sum(1)/counts[idx].sum(1)
        out[k]['source_cluster_ci95_sensitivity']=np.quantile(boot,[.025,.975]).tolist()
        out[k]['n_source_clusters']=len(sums)
    return out

for cp in ['Qwen2.5-3B','Qwen2.5-3B-Instruct','OLMoE-1B-7B-0125','OLMoE-1B-7B-0125-SFT','OLMoE-1B-7B-0125-DPO','Qwen3-4B','Qwen3-8B','Qwen3-14B']:
    path=a.root/'runs'/('E33-iqap-'+cp)
    if not (path/'config.json').exists() or not json.loads((path/'config.json').read_text()).get('complete'):
        pending.append(cp);continue
    c=json.loads((path/'config.json').read_text());assert c['numerical_gate_pass'] and c['batch_size']==1
    rows=[json.loads(l) for l in (path/'predictions.jsonl').read_text().splitlines()];assert len(rows)==300
    index={(r['item'],r['interface']):r for r in rows};assert len(index)==300
    by_model[cp]=(rows,c)
    groups=defaultdict(list)
    for r in rows:groups[r['interface'],'all'].append(r);groups[r['interface'],r['classification']].append(r)
    models[cp]={'run':path.name,'input_token_hashes':c['input_token_hashes'],
        'config_sha256':hashlib.sha256((path/'config.json').read_bytes()).hexdigest(),
        'descriptions':{i+'/'+g:{key:summarize(rs,key) for key in ['full_logprob','content_logprob']} for (i,g),rs in groups.items()},
        'null_normalized':{i:{key:(lambda x:(np.exp(x-x.max())/np.exp(x-x.max()).sum()).tolist())(np.array([s[key] for s in scores]))
                              for key in ['full_logprob','content_logprob']} for i,scores in c['null_readout'].items()}}
paired={}
for left,right in [('Qwen2.5-3B','Qwen2.5-3B-Instruct'),('OLMoE-1B-7B-0125','OLMoE-1B-7B-0125-SFT'),
                   ('OLMoE-1B-7B-0125-SFT','OLMoE-1B-7B-0125-DPO'),('Qwen3-4B','Qwen3-8B'),('Qwen3-8B','Qwen3-14B')]:
    if left not in by_model or right not in by_model:continue
    ls,lc=by_model[left];rs,rc=by_model[right]
    assert lc['input_token_hashes']==rc['input_token_hashes']
    idx={(r['item'],r['interface']):r for r in rs}
    groups=defaultdict(list)
    for r in ls:
        other=idx[r['item'],r['interface']];assert r['prompt_sha256']==other['prompt_sha256'] and r['human_counts']==other['human_counts']
        for key in ['full_logprob','content_logprob']:
            m=metrics(r,key);n=metrics(other,key)
            for source in ['all',r['classification']]:groups[r['interface']+'/'+source+'/'+key].append({k:n[k]-v for k,v in m.items()})
    paired[left+' -> '+right]={g:{k:estimate([r[k] for r in rows if k in r]) for k in rows[0]} for g,rows in groups.items()}
assert a.allow_incomplete or not pending,pending
out={'models':models,'paired_changes':paired,'pending':pending,'limits':[
    'Human forced-choice category distribution is not unique true speaker intent or calibrated model knowledge.',
    'Model probabilities are relative full candidate string probabilities, not sampled human population.',
    'Conditional definiteness is evaluated on human majority polarity; polarity ties excluded only from those metrics.',
    'Source-cluster sensitivity preserves item-weighted means; item CI is not a training-replicate CI.',
    'Primary full sequence and secondary content-only reported without selecting an interface.']}
a.output.write_text(json.dumps(out,indent=2)+'\n')
for cp,z in models.items():
    print(cp,{i:{k:round(z['descriptions'][i+'/all']['full_logprob'][k]['mean'],4) for k in ['polarity_correct','definite_minus_human','four_way_brier']} for i in ['bare','common-chat']})
print('pending',pending)
