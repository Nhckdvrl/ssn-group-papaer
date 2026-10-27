import json
from pathlib import Path
import numpy as np
R=Path('/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/moe/results')
O=R/'e155_terra_audit/report.json'
raw=Path('/home/xiang/mechpop_cache/e155_native_task_branch_necessity')
d=[np.load(raw/f'scores_{s}.npz') for s in 'PAB']; old=np.load('/home/xiang/mechpop_cache/e153_mmlu_source_transfer/scores.npz')
for f in d[1:]:
 for k in ('conditions','gold','subject','answer_tokens','answer_chars'): assert np.array_equal(f[k],d[0][k]),k
for f,c in [(d[1],0),(d[2],3)]:
 for k in ('gold','subject','answer_tokens','answer_chars'): assert np.array_equal(f[k],old[k]),k
ll=np.stack([f['candidate_loglikelihood'] for f in d]); gold=d[0]['gold']; topic=d[0]['subject']; q=np.arange(len(gold)); chars=d[0]['answer_chars']; tokens=d[0]['answer_tokens']; centered=ll-ll.max(-1,keepdims=True)
metrics={'raw_accuracy':(ll.argmax(-1)==gold).astype(float),'per_char_accuracy':((ll/chars[None,None,:,:]).argmax(-1)==gold).astype(float),'choice_CE':np.log(np.exp(centered).sum(-1))-centered[:,:,q,gold], 'true_answer_token_NLL':-ll[:,:,q,gold]/tokens[q,gold][None,None,:], 'first_answer_token_KL':np.stack([f['first_answer_token_KL'] for f in d])}
def stats(x):
 rng=np.random.default_rng(155001); vals=[x[topic==i] for i in (0,1)]; boot=np.mean([v[rng.integers(0,len(v),(1000,len(v)))].mean(1) for v in vals],axis=0)
 return {'point':float(np.mean([v.mean() for v in vals])),'ci95':np.quantile(boot,[.025,.975]).tolist()}
res={'conditions':d[0]['conditions'].tolist(),'subjects':[int((topic==i).sum()) for i in (0,1)],'ci':'paired question bootstrap within fixed subjects, equal macro, seed 155001, 1000, subject-major; not seed or subject population', 'native_replay':{s:{'exact':bool(np.array_equal(ll[i,0],old['candidate_loglikelihood'][j,0])),'max_abs_error':float(np.max(np.abs(ll[i,0]-old['candidate_loglikelihood'][j,0])))} for s,i,j in [('A',1,0),('B',2,3)]},'metrics':{}}
for name,v in metrics.items():
 out={'profiles':{},'relative_to_native':{},'interaction':{},'source_difference':{},'relative_damage_source_difference':{},'interaction_source_difference':{}}
 for i,s in enumerate('PAB'):
  out['profiles'][s]={c:stats(v[i,j]) for j,c in enumerate(res['conditions'])}
  out['relative_to_native'][s]={c:stats(v[i,j]-v[i,0]) for j,c in enumerate(res['conditions'])}
  out['interaction'][s]=stats(v[i,0]-v[i,1]-v[i,2]+v[i,3])
 for x,y,label in [(1,0,'A_minus_P'),(2,0,'B_minus_P'),(2,1,'B_minus_A')]:
  out['source_difference'][label]={c:stats(v[x,j]-v[y,j]) for j,c in enumerate(res['conditions'])}
  out['relative_damage_source_difference'][label]={c:stats((v[x,j]-v[x,0])-(v[y,j]-v[y,0])) for j,c in enumerate(res['conditions'])}
  out['interaction_source_difference'][label]=stats((v[x,0]-v[x,1]-v[x,2]+v[x,3])-(v[y,0]-v[y,1]-v[y,2]+v[y,3]))
 res['metrics'][name]=out
O.write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n')
print('native_replay',res['native_replay'])
# Author comparison begins only after independent results are saved above.
s=json.loads((R/'e155/summary.json').read_text()); errors=[]
def cmp(actual,expected,sign=1):
 got=np.array([actual['point'],*actual['ci95']]); ref=np.array([expected['point'],*expected['question_ci95']]);
 if sign<0: got=np.array([-got[0],-got[2],-got[1]])
 errors.append(float(np.max(np.abs(got-ref))))
for metric,out in res['metrics'].items():
 for source in 'PAB':
  for c in res['conditions']:
   row=s['sources'][source][c];cmp(out['profiles'][source][c],row[metric])
   if c!='native' and metric=='raw_accuracy':cmp(out['relative_to_native'][source][c],row['accuracy_drop'],-1)
   if c!='native' and metric in ('choice_CE','true_answer_token_NLL'):cmp(out['relative_to_native'][source][c],row[metric+'_increase'])
  if metric!='first_answer_token_KL':cmp(out['interaction'][source],s['sources'][source]['R_x_S_interaction'][metric])
 if metric!='first_answer_token_KL':
  for label in ('A_minus_P','B_minus_P','B_minus_A'):
   for c in res['conditions']:
    row=s['source_differences'][label][c];cmp(out['source_difference'][label][c],row[metric])
    if c!='native' and metric=='raw_accuracy':cmp(out['relative_damage_source_difference'][label][c],row['accuracy_drop'],-1)
    if c!='native' and metric=='choice_CE':cmp(out['relative_damage_source_difference'][label][c],row['choice_CE_increase'])
import hashlib
hashes={}
for source in 'PAB':
 m=json.loads((R/'e155'/f'manifest_{source}.json').read_text()); p=raw/f'scores_{source}.npz'; h=hashlib.file_digest(p.open('rb'),'sha256').hexdigest(); hashes[source]={'manifest_match':h==m['raw']['sha256'],'sha256':h}
res['comparison']={'num_statistics':len(errors),'maximum_point_or_ci_absolute_error':max(errors),'raw_manifest_hashes':hashes,'sign_note':'accuracy relative_to_native is variant minus native; author accuracy_drop uses the opposite sign','interpretation':'R×S is a difference-in-differences of measured network outputs, not a knowledge allocation or percentage'}
O.write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n')
print(res['comparison'])

# POST-HOC common-native-success condition; selection never uses intervention outcomes.
def common_success_posthoc():
 import json, numpy as np
 from pathlib import Path
 base=Path('/home/xiang/mechpop_cache/e155_native_task_branch_necessity')
 output=Path('/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/moe/results/e155_terra_audit/common_success_posthoc.json')
 d=[np.load(base/f'scores_{s}.npz') for s in 'PAB']; gold=d[0]['gold']; sub=d[0]['subject']; names=d[0]['conditions'].tolist()
 for f in d[1:]:
  for k in ('gold','subject','conditions'): assert np.array_equal(f[k],d[0][k])
 pred=np.stack([f['candidate_loglikelihood'].argmax(-1) for f in d]); success=(pred[:,0,:]==gold).all(axis=0); idx=[np.flatnonzero(success & (sub==i)) for i in (0,1)]
 def statistic(x):
  group=[x[g].astype(float) for g in idx]; details={}
  rng=np.random.default_rng(155101); boot=[]; points=[]
  for i,v in enumerate(group):
   if not len(v): details[str(i)]={'n':0,'point':None,'ci95':None}; continue
   samples=v[rng.integers(0,len(v),(1000,len(v)))].mean(axis=1); points.append(v.mean());boot.append(samples)
   details[str(i)]={'n':len(v),'sum':int(v.sum()),'point':float(v.mean()),'ci95':np.quantile(samples,[.025,.975]).tolist()}
  return {'point':float(np.mean(points)) if len(points)==2 else None,'ci95':np.quantile(np.mean(boot,axis=0),[.025,.975]).tolist() if len(points)==2 else None,'subjects':details}
 correct=(pred==gold[None,None,:]); flip=(pred!=pred[:,0:1,:]); result={'label':'POST-HOC, chosen after full intervention matrix; not independent confirmation or replacement of full-sample analysis', 'selection':'all P/A/B native argmax equal gold; no intervention outcome used', 'total':int(success.sum()), 'subject_counts':{str(i):int(len(g)) for i,g in enumerate(idx)}, 'macro_available':all(len(g)>0 for g in idx), 'bootstrap':'paired stratified question bootstrap seed 155101, 1000 subject-major draws, equal subject macro', 'limitations':'conditioning on native correctness excludes intervention corrections and applies only to common-success questions','sources':{},'differences':{}}
 for i,s in enumerate('PAB'):
  result['sources'][s]={}
  for j,name in enumerate(names): result['sources'][s][name]={'accuracy':statistic(correct[i,j]),'flip_rate':statistic(flip[i,j])}
 for i,j,label in [(2,0,'B_minus_P'),(2,1,'B_minus_A')]:
  result['differences'][label]={}
  for k in (1,2): result['differences'][label][names[k]]={'accuracy':statistic(correct[i,k].astype(float)-correct[j,k].astype(float)),'flip_rate':statistic(flip[i,k].astype(float)-flip[j,k].astype(float))}
 output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print('n',result['total'],result['subject_counts']); print('diffs',json.dumps(result['differences']))
common_success_posthoc()
