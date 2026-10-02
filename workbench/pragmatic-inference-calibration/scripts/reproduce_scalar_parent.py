#!/usr/bin/env python3
"""Reproduce the original BERT alternative expectation, without changing stimuli."""
import argparse, hashlib, json, subprocess, time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from scipy.stats import pearsonr, spearmanr
from transformers import BertForMaskedLM, BertTokenizer

ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,required=True)
ap.add_argument('--model',type=Path,required=True)
ap.add_argument('--revision',required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
assert not args.output.exists()
args.output.mkdir(parents=True)
upstream=args.root/'upstream/expectations-over-alternatives'
data=upstream/'within-scale/data/some-all'
inputs=pd.read_csv(data/'sentences_for_model.csv')
human=pd.read_csv(data/'some_database.tsv',sep='\t')
assert not inputs.Item.duplicated().any() and not inputs.isna().any().any()
alternatives=['each','every','few','half','much','many','most','all']
torch.backends.cuda.matmul.allow_tf32=False
torch.backends.cudnn.allow_tf32=False
tok=BertTokenizer.from_pretrained(args.model)
model=BertForMaskedLM.from_pretrained(args.model,torch_dtype=torch.float32).cuda().eval()
ids=[tok.encode(x,add_special_tokens=False) for x in alternatives]
assert all(len(x)==1 for x in ids)
ids=[x[0] for x in ids]
texts=[s.replace('some','some, but not [MASK],') for s in inputs.Sentence]
@torch.inference_mode()
def read(batch):
    inp=tok(batch,padding=True,return_tensors='pt').to('cuda')
    logits=model(**inp).logits
    out=[]
    for i in range(len(batch)):
        positions=(inp.input_ids[i]==tok.mask_token_id).nonzero().flatten()
        assert len(positions)>0
        lp=logits[i,positions[0]].float().log_softmax(-1)
        out.append((-lp[ids].cpu().numpy(),tok.decode(logits[i,positions].argmax(-1)),len(positions)))
    return out
start=time.monotonic()
selected=texts[:15]+texts[-1:]
batch=read(selected)
delta=max(float(np.max(np.abs(read([selected[k]])[0][0]-batch[k][0]))) for k in [0,15])
control={'batch1_16_max_surprisal_delta':delta,'threshold':0.001,'pass':delta<0.001}
(args.output/'numerical-control.json').write_text(json.dumps(control,indent=2))
assert control['pass'],'Numerical gate failed'
rows=[]
for offset in range(0,len(texts),16):
    for k,(surprisals,predicted,count) in enumerate(read(texts[offset:offset+16])):
        r=inputs.iloc[offset+k]
        rows.append({'Item':r.Item,'Sentence':r.Sentence,'predicted_token':predicted,'mask_count':count,
                     **{a:float(s) for a,s in zip(alternatives,surprisals)}})
result=pd.DataFrame(rows)
result.to_csv(args.output/'predictions.csv',index=False)
parity={}
for a in alternatives:
    published=pd.read_csv(data/'model_output'/('bert-base-uncased_'+a+'.csv'))
    joined=result.merge(published,on=['Item','Sentence'],suffixes=('_local','_published'),validate='one_to_one')
    assert len(joined)==len(result)
    diff=np.abs(joined[a]-joined.surprisal_at_strong)
    parity[a]={'n':len(joined),'mean_absolute_delta':float(diff.mean()),'max_absolute_delta':float(diff.max()),
               'prediction_match_rate':float((joined.predicted_token_local==joined.predicted_token_published).mean())}
joined=result.merge(human.groupby('Item',as_index=False).Rating.mean(),on='Item',validate='one_to_one')
def stats(d):
    return {'surprisal_pearson':float(pearsonr(d['all'],d.Rating).statistic),
            'surprisal_spearman':float(spearmanr(d['all'],d.Rating).statistic),
            'probability_pearson':float(pearsonr(np.exp(-d['all']),d.Rating).statistic)}
association=stats(joined)
rng=np.random.default_rng(0)
boots=[stats(joined.iloc[rng.integers(len(joined),size=len(joined))]) for _ in range(2000)]
ci={k:np.quantile([b[k] for b in boots],[0.025,0.975]).tolist() for k in association}
config={'task':'scalar_parent','model':'google-bert/bert-base-uncased','revision':args.revision,
        'upstream_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip(),
        'dtype':'float32','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256':hashlib.sha256((data/'sentences_for_model.csv').read_bytes()).hexdigest(),
        'human_sha256':hashlib.sha256((data/'some_database.tsv').read_bytes()).hexdigest(),
        'n':len(result),'multi_mask_items':int((result.mask_count>1).sum()),
        'missing_human_items':sorted(set(human.Item)-set(result.Item)),
        'wall_seconds':time.monotonic()-start,'numerical_controls':control,'complete':True}
summary={'config':config,'published_parity':parity,'human_association':association,'ci95_item_bootstrap':ci,
         'limits':['String predictor only; concept/GloVe and multivariate model not reproduced.',
                   'Explicit masked alternative expectation is not an SI decision or binary warrant.']}
(args.output/'config.json').write_text(json.dumps(config,indent=2))
(args.output/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary),flush=True)
