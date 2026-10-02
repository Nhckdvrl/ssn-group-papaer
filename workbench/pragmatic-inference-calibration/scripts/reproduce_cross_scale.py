#!/usr/bin/env python3
"""Original strong alternative, original SyntaxGym region joining; frozen readout."""
import argparse,csv,hashlib,json,subprocess,time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from scipy.stats import pearsonr,spearmanr
from transformers import AutoModelForCausalLM,AutoTokenizer

def prepare(root):
 up=root/'upstream/expectations-over-alternatives/cross-scale'
 rates={}
 for ds in ['rx22','g18','pvt21','vt16']:
  d=pd.read_csv(up/'human_data'/f'{ds}.csv')
  for _,r in d.iterrows():
   if ds=='rx22':weak,strong,y=r.Weaker,r.Stronger,r['SI percent (Exp 1)']/100
   elif ds=='g18':weak,strong,y=r.weak_adj,r.strong_adj,r.si_rate
   elif ds=='pvt21':weak,strong,y=r.weak_adj,r.strong_adj,r.SI_rate
   else:weak,strong,y=r.weak_scalemate,r.strong_scalemate,r.si_nonneutral/100
   rates[(ds,weak+'/'+strong)]=float(y)
 rows=[]
 for p in sorted((up/'test_suites').rglob('*.json')):
  ds=p.relative_to(up/'test_suites').parts[0]
  weak,strong=p.stem.split('_',1);d=json.loads(p.read_text())
  chosen=[i for i in d['items'] if i['conditions'][0]['regions'][4]['content']==strong]
  assert len(chosen)==1
  item=chosen[0];regs=item['conditions'][0]['regions']
  # SyntaxGym Suite.iter_sentences: lstrip, omit empty regions, join with spaces.
  prefix=' '.join(r['content'].lstrip() for r in regs[:4] if r['content'].strip())
  target=' '+regs[4]['content'].lstrip();ending=' '+regs[5]['content'].lstrip()
  pub=up/'model_results'/p.relative_to(up/'test_suites').with_name(p.stem+'_gpt2.tsv')
  vals=[]
  if pub.exists():
   with pub.open() as f:
    vals=[float(r['metric_value']) for r in csv.DictReader(f,delimiter='\t') if int(r['item_number'])==item['item_number'] and int(r['region_number'])==5]
   assert len(vals)==1
  rows.append({'dataset':ds,'scale_id':weak+'/'+strong,'template':p.parent.name if ds=='vt16' else None,
   'suite':str(p.relative_to(up)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
   'source_item_number':item['item_number'],'prefix':prefix,'target':target,'ending':ending,
   'human_si_rate':rates[(ds,weak+'/'+strong)],'published_surprisal':vals[0] if vals else None})
 assert len(rows)==300
 return rows,up

ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,required=True);ap.add_argument('--model',type=Path,required=True)
ap.add_argument('--model-id',required=True);ap.add_argument('--revision',required=True)
ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
assert not args.output.exists();args.output.mkdir(parents=True)
rows,up=prepare(args.root)
torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='right')
if tok.pad_token_id is None:tok.pad_token=tok.eos_token
model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,device_map={'':0}).eval()
@torch.inference_mode()
def read(rs):
 texts=[r['prefix']+r['target']+r['ending'] for r in rs]
 inp=tok(texts,add_special_tokens=False,padding=True,return_tensors='pt',return_offsets_mapping=True)
 offsets=inp.pop('offset_mapping');inp=inp.to(model.device)
 logits=model(**inp).logits.float()
 out=[]
 for i,r in enumerate(rs):
  start=len(r['prefix']);end=start+len(r['target']);positions=[]
  for j,(a,b) in enumerate(offsets[i].tolist()):
   if b<=start or a>=end:continue
   assert a>=start and b<=end,(r['scale_id'],a,b,start,end)
   assert j>0;positions.append(j)
  assert positions
  lp=sum(float(logits[i,j-1].log_softmax(-1)[inp.input_ids[i,j]]) for j in positions)
  out.append({'logprob_nats':lp,'target_tokens':len(positions)})
 return out
start=time.monotonic();selected=rows[:7]+rows[-1:];many=read(selected)
delta=max(abs(read([selected[i]])[0]['logprob_nats']-many[i]['logprob_nats']) for i in [0,7])
control={'batch1_8_max_logprob_delta':delta,'threshold':1e-3,'pass':delta<1e-3}
(args.output/'numerical-control.json').write_text(json.dumps(control,indent=2));assert control['pass']
output=[]
for n in range(0,len(rows),8):
 for r,d in zip(rows[n:n+8],read(rows[n:n+8])):output.append(dict(r,**d))
(args.output/'predictions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in output))
df=pd.DataFrame(output);df['surprisal_nats']=-df.logprob_nats
# LM Zoo transformers-base/get_surprisals.py returns -log(p)/log(2).
matched=df.dropna(subset=['published_surprisal'])
diff=np.abs(matched.surprisal_nats/np.log(2)-matched.published_surprisal)
parity={'unit':'bits','n_matched':len(matched),'mean_absolute_delta':float(diff.mean()),
 'max_absolute_delta':float(diff.max()),'pass':float(diff.max())<1e-3,
 'unavailable_published_suites':df.loc[df.published_surprisal.isna(),'suite'].tolist()}
summary={}
for ds,g in df.groupby('dataset'):
 means=g.groupby('scale_id',as_index=False).agg(surprisal_nats=('surprisal_nats','mean'),human_si_rate=('human_si_rate','mean'))
 means=means.dropna(subset=['surprisal_nats','human_si_rate']);x=means.surprisal_nats.values;y=means.human_si_rate.values
 def stats(idx):return [float(pearsonr(x[idx],y[idx]).statistic),float(spearmanr(x[idx],y[idx]).statistic)]
 obs=stats(np.arange(len(x)));rng=np.random.default_rng(0);boots=[stats(rng.integers(len(x),size=len(x))) for _ in range(2000)]
 summary[ds]={'n_templates':len(g),'n_scales':len(means),'pearson':obs[0],'spearman':obs[1],
  'ci95_scale_bootstrap':np.quantile(boots,[.025,.975],axis=0).T.tolist()}
config={'task':'cross_scale_parent','model':args.model_id,'revision':args.revision,'dtype':'float32','special_tokens':False,
 'upstream_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=up,text=True).strip(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'n':len(output),'numerical_gate_pass':control['pass'],'wall_seconds':time.monotonic()-start,'complete':True}
result={'config':config,'numerical_control':control,'published_parity':parity,'datasets':summary,
 'limits':['String predictor only; concept and full WordNet alternative distribution not reproduced.',
 'Explicit contrast continuation is not a pragmatic decision, human mean is not binary warrant.',
 'Parent complete-case exclusions involving conceptual predictors are not applied to primary string-only scope.']}
(args.output/'config.json').write_text(json.dumps(config,indent=2));(args.output/'summary.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
