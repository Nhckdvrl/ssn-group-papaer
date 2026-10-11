"""Frozen full-factorial readouts and cache provenance audit for E107.
Old opposite-p records retained; four extra same-run self controls are separate.
"""
import argparse,itertools,json,sys
from pathlib import Path
from e103_memory_crossing import interval

def load(p):return [json.loads(s) for s in p.read_text().splitlines() if s]
def key(r):return (r['context'],r['condition'],r['pr'],r['pt'],r['ct'],r['query'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',default='results/e107/merged');a=ap.parse_args()
 dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True);rows=[];controls=[];runs=[]
 for i in range(4):
  old=load(Path(f'results/e107/part{i}/behavior.jsonl'));same=load(Path(f'results/e107/same{i}/behavior.jsonl'))
  assert len(old)==72 and len(same)==49 and all(r['context']==i for r in old+same)
  assert sum(r['condition']=='full_owner_cue' for r in same)==1
  controls += [r for r in same if r['condition']=='full_owner_cue']
  rows += old+[r for r in same if r['condition'].startswith('rec_')]
  for label in ('part','same'):
   run=json.load(open(f'results/e107/{label}{i}/run.json'));runs.append(run)
   assert run['pristine_caches_exact'] and run['errors']['self_copy_max_vocab_nats']<=.001
 assert len(rows)==480 and len(set(key(r) for r in rows))==480
 expected=set()
 for ci in range(4):
  for pr,q in itertools.product((1,-1),range(4)):expected.add((ci,'own',pr,pr,None,q))
  for pr,ct,q in itertools.product((1,-1),(0,1),range(4)):expected.add((ci,'full_owner_cue',pr,pr,ct,q))
  for st,pr,pt,ct,q in itertools.product(('before','after','explicit'),(1,-1),(1,-1),(0,1),range(4)):
   expected.add((ci,'rec_'+st,pr,pt,ct,q))
 assert {key(r) for r in rows}==expected
 d={key(r):r for r in rows};held_pairs=[]
 for ci,st,pt,ct,q in itertools.product(range(4),('before','after','explicit'),(1,-1),(0,1),range(4)):
  rp=d[ci,'rec_'+st,1,pt,ct,q];rm=d[ci,'rec_'+st,-1,pt,ct,q]
  assert rp['rec_fingerprint']==rm['rec_fingerprint'],'Teacher state differs across Owner p; do not interpret private-p comparison'
  assert rp['kv_fingerprint']!=rm['kv_fingerprint']
  held_pairs.append((rp,rm))
 for r in rows:
  if r['ct'] is not None:
   assert r['criterion_target']==r['pr']*r['x'][r['ct']]
   assert r['sender_function']==r['pt']*r['x'][r['ct']]
 ids=list(range(4))
 def est(rr,f):return interval([sum(f(r) for r in rr if r['context']==ci)/sum(r['context']==ci for r in rr) for ci in ids])
 out={'n_rows':480,'extra_controls':4,'conditions':{},'paired':{},'owner_p_causal_pairs':{}}
 for cond in sorted({r['condition'] for r in rows}):
  rr=[r for r in rows if r['condition']==cond];it={'n':len(rr),'unknown':sum(not r['valid'] for r in rr),
   'initial_censored':sum(r['initial_censored'] for r in rr),'still_censored':sum(r['still_censored'] for r in rr)}
  if cond=='own':out['conditions'][cond]=it;continue
  it['criterion_rate']=est(rr,lambda r:r['class']==r['criterion_target'])
  it['teacher_AB_function']=est(rr,lambda r:r['class']==r['sender_function'])
  it['teacher_C_function']=est(rr,lambda r:r['class']==-r['sender_function'])
  groups={}
  for r in rr:groups.setdefault((r['context'],r['pr'],r['pt'],r['ct']),[]).append(r)
  assert all(len(g)==4 for g in groups.values());it['complete_profiles']=sum(all(r['class']==r['criterion_target'] for r in g) for g in groups.values());it['profile_denominator']=len(groups)
  it['subsets']={}
  for rel in ('same','opposite','all'):
   ss=[r for r in rr if rel=='all' or (r['pr']==r['pt'])==(rel=='same')]
   if not ss:continue
   it['subsets'][rel]={sub:est([r for r in ss if (r['x'][0]!=r['x'][1])==(sub=='mixed')],lambda r:r['class']==r['criterion_target']) for sub in ('mixed','concordant')}
  out['conditions'][cond]=it
 for cond in ('rec_after','rec_explicit'):
  rr=[r for r in rows if r['condition']==cond and r['x'][0]!=r['x'][1]]
  for rel in ('same','opposite','all'):
   ss=[r for r in rr if rel=='all' or (r['pr']==r['pt'])==(rel=='same')]
   out['paired'][cond+'_minus_before_'+rel+'_mixed']=est(ss,lambda r:(r['class']==r['criterion_target'])-
     (d[r['context'],'rec_before',r['pr'],r['pt'],r['ct'],r['query']]['class']==r['criterion_target']))
 for st in ('before','after','explicit'):
  ps=[p for p in held_pairs if p[0]['condition']=='rec_'+st]
  out['owner_p_causal_pairs'][st]={'n_pairs':len(ps),'both_correct':interval([
   sum(a['class']==a['criterion_target'] and b['class']==b['criterion_target'] for a,b in ps if a['context']==ci)/sum(a['context']==ci for a,b in ps) for ci in ids]),
   'flip_rate':interval([sum(a['class']!=b['class'] for a,b in ps if a['context']==ci)/sum(a['context']==ci for a,b in ps) for ci in ids])}
 audit={'complete_grid':True,'rows':480,'all_record_count':484,'extra_self_controls':4,'all_four_contexts_kept':True,
  'fixed_teacher_state_pairs':192,'teacher_rec_tensors_exact_across_owner_p':True,'owner_KV_tensors_differ':True,
  'teacher_parent_selection':False,'unknown_total':sum(not r['valid'] for r in rows),'gpu_hours':sum(r['gpu_hours'] for r in runs),
  'code_note':'Original 288 opposite-p rows retained. Same-p supplement192; extra controls4 excluded before inspecting effects.'}
 (dest/'analysis.json').write_text(json.dumps(out,indent=2)+'\n');(dest/'completeness_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 (dest/'behavior.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
