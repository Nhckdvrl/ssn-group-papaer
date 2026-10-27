import json, numpy as np
from pathlib import Path
R=Path('/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/moe/results')
O=R/'e153154_terra_audit/report.json'
a=np.load('/home/xiang/mechpop_cache/e153_mmlu_source_transfer/scores.npz')
subs=a['subject']; groups=[np.flatnonzero(subs==x) for x in np.unique(subs)]
rng=np.random.default_rng(153001); samples=np.stack([np.concatenate([rng.choice(g,len(g),replace=True) for g in groups]) for _ in range(1000)])
def macro(x): return float(np.mean([x[...,g].mean() for g in groups]))
def mci(x):
 p=macro(x); bs=np.array([np.mean([x[g].mean() for g in (row[:len(groups[0])],row[len(groups[0]):])]) for row in samples]); return [p,*map(float,np.quantile(bs,[.025,.975]))]
ll=a['candidate_loglikelihood']; gold=a['gold']; stats={}
for scale in ['sum','token_mean','char_mean']:
 scores=ll if scale=='sum' else ll/a['answer_tokens' if scale=='token_mean' else 'answer_chars'][None,None,:,:]
 hit=(scores.argmax(-1)==gold)
 stats[scale]={}
 for ci,c in enumerate(a['case_names']):
  for pi,p in enumerate(a['policies']): stats[scale][f'{c}/{p}']=mci(hit[ci,pi])
  stats[scale][f'{c}/B-A']=mci(hit[ci,2].astype(float)-hit[ci,1].astype(float))
for ci,c in enumerate(a['case_names']):
 for pi,p in enumerate(a['policies']): stats.setdefault('first_KL',{})[f'{c}/{p}']=mci(a['first_answer_token_KL'][ci,pi])
b=np.load('/home/xiang/mechpop_cache/e154_native_parent_boundary/metrics.npz'); plan=json.loads((R/'e154/plan.json').read_text()); selected=plan['selected']; keys=[(x['source'],x['file_id']) for x in selected]; unique=list(dict.fromkeys(keys)); clusters=[np.array([i for i,k in enumerate(keys) if k==v]) for v in unique]; assert len(clusters)==20
rng=np.random.default_rng(154001); draws=rng.integers(0,len(clusters),(1000,len(clusters))); indices=[np.concatenate([clusters[i] for i in row]) for row in draws]
def ci(x): return [float(x.mean()),*map(float,np.quantile([x[idx].mean() for idx in indices],[.025,.975]))]
metrics=b['metrics'].astype(float); out={}; names=b['conditions'].tolist(); fields=b['fields'].tolist()
for maskname in ['valid','suffix_valid']:
 mask=b[maskname]; seq=(metrics*mask[None,:,:,None]).sum(axis=2)/mask.sum(axis=1)[None,:,None]
 out[maskname]={}
 for fi,f in enumerate(fields):
  vals=seq[:,:,fi]; d={n:ci(vals[i]) for i,n in enumerate(names)}
  for i,n in enumerate(names[1:],1): d[n+'-native']=ci(vals[i]-vals[0])
  d['prefixB-prefixA']=ci(vals[3]-vals[2]); d['random_mean-native']=ci(vals[4:7].mean(axis=0)-vals[0]); out[maskname][f]=d
report={'calculation_only_before_author_comparison':True,'E153':{'subject_counts':[len(g) for g in groups], 'case_names':a['case_names'].tolist(),'policies':a['policies'].tolist(),'results':stats},'E154':{'conditions':names,'fields':fields,'cluster_sizes':[len(c) for c in clusters],'results':out},'CI':'percentile 2.5/97.5; paired inputs; not seed population'}
O.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
# Independent descendant reconstruction from the two original raw files, after saving parent-only intermediate results.
e150=np.load('/home/xiang/mechpop_cache/e150_native_protocol_cube/cube_metrics.npz'); e151=np.load('/home/xiang/mechpop_cache/e151_native_selectivity_necessity/metrics.npz'); assert np.array_equal(e150['valid'],b['valid']) and np.array_equal(e151['valid'],b['valid']) and np.array_equal(e150['suffix_valid'],b['suffix_valid']) and np.array_equal(e151['suffix_valid'],b['suffix_valid'])
rows=[]
for source,case in [(0,0),(1,15)]:
 raw=e151['metrics']; prefixes=e150['restricted_metrics']; rows.append(np.stack([raw[source,0],prefixes[source,case],prefixes[0,case],prefixes[1,case],*raw[source,3:6],raw[source,1],raw[source,2]]))
all_raw=np.concatenate([metrics[None],np.stack(rows).astype(float)],axis=0); cross={}
for maskname in ['valid','suffix_valid']:
 mask=b[maskname]; seq=(all_raw*mask[None,None,:,:,None]).sum(3)/mask.sum(1)[None,None,:,None]
 cross[maskname]={}
 for child,label in [(1,'A_minus_P'),(2,'B_minus_P')]:
  cross[maskname][label]={}
  for i,n in enumerate(names):
   x=(seq[child,i,:,0]-seq[child,0,:,0])-(seq[0,i,:,0]-seq[0,0,:,0]); cross[maskname][label][n]=ci(x)
report['E154']['descendant_minus_parent_delta_nll']=cross
# Compare author tables only after independent results are in report.json.
author153=json.loads((R/'e153/summary.json').read_text()); author154=json.loads((R/'e154/summary.json').read_text()); diffs153=[]; diff154=[]
for c in a['case_names']:
 for pol in a['policies']:
  for key,author_key in [('sum','raw_accuracy'),('char_mean','per_char_accuracy'),('first_KL','first_answer_token_KL')]:
   ours=stats[key][f'{c}/{pol}']; theirs=author153['cases'][c][pol][author_key]; diffs153.append([key,str(c),str(pol),abs(ours[0]-theirs['point']),max(abs(ours[j+1]-theirs['question_ci95'][j]) for j in (0,1))])
for maskname,scope in [('valid','full'),('suffix_valid','suffix')]:
 for child,label in [(1,'A_minus_P'),(2,'B_minus_P')]:
  for n in names:
   x=cross[maskname][label][n]; y=author154['scopes'][scope]['descendant_minus_parent'][label][n]['delta_NLL'];diff154.append(max(abs(x[0]-y['point']),*(abs(x[j+1]-y['input_file_ci95'][j]) for j in (0,1))))
report['comparison']={'E153_max_point_abs':max(x[3] for x in diffs153),'E153_max_CI_endpoint_abs':max(x[4] for x in diffs153),'E153_CI_difference_explanation':'same seed and stratified bootstrap, different valid random-number draw ordering: independent audit interleaves subjects by replicate; author draws all replicates per subject','E154_cross_source_max_abs':max(diff154)}
O.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')

# E153 supplementary audit: independent reconstruction and two bootstrap draw orders.
def e153_supplement():
 import json, numpy as np
 from pathlib import Path
 R=Path('/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/moe/results'); O=R/'e153154_terra_audit/report.json'
 a=np.load('/home/xiang/mechpop_cache/e153_mmlu_source_transfer/scores.npz'); ll=a['candidate_loglikelihood']; gold=a['gold']; topic=a['subject']; q=np.arange(len(gold)); tokens=a['answer_tokens']; chars=a['answer_chars']
 v=ll-ll.max(axis=-1,keepdims=True); logz=np.log(np.exp(v).sum(axis=-1)); ce=logz-v[:,:,q,gold]
 metrics={'raw_accuracy':(ll.argmax(-1)==gold).astype(float),'per_char_accuracy':((ll/chars[None,None]).argmax(-1)==gold).astype(float),'choice_CE':ce,'true_answer_token_NLL':-ll[:,:,q,gold]/tokens[q,gold][None,None,:],'first_answer_token_KL':a['first_answer_token_KL']}
 weights={'G_B_minus_G_A_in_A_body':[-1,1,0,0], 'G_B_minus_G_A_in_B_body':[0,0,-1,1], 'body_B_minus_body_A_with_A_gate':[-1,0,1,0], 'body_B_minus_body_A_with_B_gate':[0,-1,0,1], 'average_gate_source':[-.5,.5,-.5,.5], 'average_body_source':[-.5,-.5,.5,.5]}
 def calc(x,order):
  rng=np.random.default_rng(153001); groups=[np.flatnonzero(topic==i) for i in (0,1)]; point=np.mean([x[g].mean() for g in groups])
  if order=='subject_major': draws=np.mean([x[g][rng.integers(0,len(g),size=(1000,len(g)))].mean(axis=1) for g in groups],axis=0)
  else: draws=np.array([np.mean([x[rng.choice(g,len(g),replace=True)].mean() for g in groups]) for _ in range(1000)])
  return [float(point),*map(float,np.quantile(draws,[.025,.975]))]
 def both(x): return {'subject_major':calc(x,'subject_major'),'replicate_major':calc(x,'replicate_major')}
 results={'cases':{},'source_effects':{}}
 for c,name in enumerate(a['case_names']):
  for p,policy in enumerate(a['policies']):
   results['cases'][f'{name}/{policy}']={k:both(v[c,p]) for k,v in metrics.items()}
 for p,policy in enumerate(a['policies']):
  results['source_effects'][str(policy)]={}
  for name,w in weights.items():
   w=np.array(w); row={}
   for k,v in metrics.items():
    if p==0 and k=='first_answer_token_KL': continue
    row[k]=both(np.einsum('c,cq->q',w,v[:,p]))
    if p and k!='first_answer_token_KL': row[k+'_change_from_same_full']=both(np.einsum('c,cq->q',w,v[:,p]-v[:,0]))
   results['source_effects'][str(policy)][name]=row
 # Persist the independent computations before accessing either author output.
 report=json.loads(O.read_text()); report['E153_supplement']=results; O.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 s=json.loads((R/'e153/summary.json').read_text()); e=json.loads((R/'e153/source_effects.json').read_text()); errs=[]
 for key,row in results['cases'].items():
  case,policy=key.split('/')
  for k,ours in row.items():
   x=ours['subject_major']; y=s['cases'][case][policy][k]; errs.append(max(abs(x[0]-y['point']),abs(x[1]-y['question_ci95'][0]),abs(x[2]-y['question_ci95'][1])))
 for policy,rows in results['source_effects'].items():
  for name,row in rows.items():
   for k,ours in row.items():
    x=ours['subject_major']; y=e['policies'][policy][name][k]; errs.append(max(abs(x[0]-y['point']),abs(x[1]-y['question_ci95'][0]),abs(x[2]-y['question_ci95'][1])))
 report['E153_supplement_comparison']={'statistics_compared':len(errs),'max_point_or_ci_endpoint_absolute_error':max(errs),'body_source_scope':'D/R/S; changes hidden states and may change actual routing','ci_note':'subject_major matches author RNG ordering; replicate_major remains independent legitimate paired stratified bootstrap; finite Monte Carlo interval differences are not numerical errors'}
 O.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(report['E153_supplement_comparison'])
e153_supplement()
