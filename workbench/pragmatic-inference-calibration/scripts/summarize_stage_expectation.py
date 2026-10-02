"""E32 original predictor; paired uncertainty over scales, not templates."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr,spearmanr
from aggregate import estimate

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists()
paths=list(sorted((a.root/'runs').glob('E32-expectation-*')))+[a.root/'runs/E18-Qwen2.5-3B-Instruct-r2',a.root/'runs/E18-Qwen3-4B-r2']
models={};frames={};reference=None
for p in paths:
    c=json.loads((p/'config.json').read_text());assert c['complete'] and c['numerical_gate_pass'] and c['dtype']=='float32'
    assert c['script_sha256']==hashlib.sha256(Path(__file__).with_name('reproduce_cross_scale.py').read_bytes()).hexdigest()
    rows=[json.loads(l) for l in (p/'predictions.jsonl').read_text().splitlines()];assert len(rows)==300
    df=pd.DataFrame(rows);assert not df.suite.duplicated().any()
    source=df[['suite','source_sha256','prefix','target','ending','human_si_rate']].to_dict('records')
    if reference is None:reference=source
    else:assert source==reference
    df['surprisal_nats']=-df.logprob_nats
    frames[c['model']]=df
    models[c['model']]={'run':p.name,'config_sha256':hashlib.sha256((p/'config.json').read_bytes()).hexdigest(),
                       'datasets':json.loads((p/'summary.json').read_text())['datasets']}
pairs=[('Qwen/Qwen2.5-3B','Qwen/Qwen2.5-3B-Instruct'),
       ('allenai/OLMoE-1B-7B-0125','allenai/OLMoE-1B-7B-0125-SFT'),
       ('allenai/OLMoE-1B-7B-0125-SFT','allenai/OLMoE-1B-7B-0125-DPO'),
       ('Qwen/Qwen3-4B','Qwen/Qwen3-8B'),('Qwen/Qwen3-8B','Qwen/Qwen3-14B')]
paired={}
for left,right in pairs:
    x=frames[left];y=frames[right]
    assert x.suite.tolist()==y.suite.tolist() and x.target_tokens.tolist()==y.target_tokens.tolist()
    groups={}
    for ds in sorted(x.dataset.unique()):
        xx=x[x.dataset==ds].groupby('scale_id').agg(s=('surprisal_nats','mean'),human=('human_si_rate','mean'))
        yy=y[y.dataset==ds].groupby('scale_id').agg(s=('surprisal_nats','mean'),human=('human_si_rate','mean'))
        assert xx.index.tolist()==yy.index.tolist() and np.array_equal(xx.human.values,yy.human.values)
        h=xx.human.values;u=xx.s.values;v=yy.s.values
        def delta(idx):
            return [float(pearsonr(v[idx],h[idx]).statistic-pearsonr(u[idx],h[idx]).statistic),
                    float(spearmanr(v[idx],h[idx]).statistic-spearmanr(u[idx],h[idx]).statistic)]
        rng=np.random.default_rng(0);boots=np.array([delta(rng.integers(len(u),size=len(u))) for _ in range(2000)])
        groups[ds]={'n_scales':len(u),'mean_surprisal_delta_nats':estimate(v-u),
                    'correlation_delta_pearson_spearman':delta(np.arange(len(u))),
                    'correlation_delta_ci95':np.quantile(boots,[.025,.975],axis=0).T.tolist()}
    paired[left+' -> '+right]=groups
out={'models':models,'paired_changes':paired,'all_300_source_records_identical':True,
     'all_within_family_target_token_counts_identical':True,
     'input_token_parity_file':'E32-token-source-parity.json',
     'limits':['String continuation expectedness only; no pragmatic decision/criterion/knowledge mediation.',
               'VT16 three templates averaged before scale bootstrap.',
               'Eight endpoints are two families, not eight independent replications.',
               'Scale includes changes in training/data; checkpoint stage effects are not isolated training objectives.']}
a.output.write_text(json.dumps(out,indent=2)+'\n')
for pair,ds in paired.items():
    print(pair,{d:round(z['mean_surprisal_delta_nats']['mean'],4) for d,z in ds.items()})
