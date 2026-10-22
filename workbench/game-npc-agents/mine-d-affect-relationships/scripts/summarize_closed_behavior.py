#!/usr/bin/env python3
"""Book/trajectory-paired summaries of the real continuous state experiment."""
import argparse,json,random,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean

METRICS=['mean_target_nll','visible_target_nll','thought_target_nll']
def read(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def interval(v):
 v=list(v);rng=random.Random(0);samples=sorted(sum(rng.choices(v,k=len(v)))/len(v) for _ in range(20000));return [samples[499],samples[19499]]
def macro(rows,metric):
 people=defaultdict(lambda:defaultdict(list))
 for r in rows:
  if r[metric] is not None:people[r['book_name']][r['trajectory_id']].append(r[metric])
 books={b:mean(mean(v) for v in people[b].values()) for b in sorted(people)}
 return dict(n_questions=sum(len(v) for ps in people.values() for v in ps.values()),n_trajectories=sum(len(ps) for ps in people.values()),n_books=len(books),book_macro=mean(books.values()),by_book=books,descriptive_book_bootstrap95=interval(books.values())) if books else None

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);a.add_argument('--consumer',choices=['qwen3_8b','arcane_8b_dpo','qwen3_32b'],default='qwen3_8b');args=a.parse_args();root=Path(args.asset_root);run=root/'runs/D-E06';scores=[];metas={};missing=[]
 likelihood_paths={name:run/('likelihood_'+name) for name in ['baselines','teacher_forced','recursive_native','recursive_summary']} if args.consumer=='qwen3_8b' else {'all':run/('consumer_'+args.consumer)/'likelihood'}
 for name,directory in likelihood_paths.items():
  p=directory/'metadata.json'
  if not p.exists():missing.append(name);continue
  m=json.loads(p.read_text());metas[name]=m
  if not m['complete']:missing.append(name);continue
  rr=read(p.parent/'scores.jsonl');assert len(rr)==m['n_instances'];scores+=rr
 grouped=defaultdict(list);paired=defaultdict(dict)
 for r in scores:grouped[r['condition']].append(r);paired[r['question_id']][r['condition']]=r
 groups={c:dict(n=len(rs),metrics={metric:macro(rs,metric) for metric in METRICS},by_checkpoint={str(step):{metric:macro([r for r in rs if r['after_updates']==step],metric) for metric in METRICS} for step in [1,4,8]}) for c,rs in grouped.items()}
 comparisons={}
 for lhs,rhs in [('frozen','released'),('teacher_forced','released'),('recursive_native','teacher_forced'),('recursive_summary','recursive_native'),('recursive_summary','released')]:
  if lhs not in grouped or rhs not in grouped:continue
  by_metric={}
  for metric in METRICS:
   changes=[]
   for q,v in paired.items():
    if lhs in v and rhs in v and v[lhs][metric] is not None and v[rhs][metric] is not None:
     r={k:v[lhs][k] for k in ['question_id','trajectory_id','book_name','role','after_updates']};assert v[lhs]['target_sha256']==v[rhs]['target_sha256'] and v[lhs]['n_target_tokens']==v[rhs]['n_target_tokens'];r.update(delta=v[lhs][metric]-v[rhs][metric]);changes.append(r)
   if changes:
    by_metric[metric]=dict(**macro([{**r,metric:r['delta']} for r in changes],metric),by_checkpoint={str(step):macro([{**r,metric:r['delta']} for r in changes if r['after_updates']==step],metric) for step in [1,4,8]},lower_tie_higher=[sum(r['delta']<0 for r in changes),sum(r['delta']==0 for r in changes),sum(r['delta']>0 for r in changes)],details=changes)
  comparisons[lhs+' minus '+rhs]=by_metric
 updates={};first_wave={}
 for mode in ['teacher_forced','recursive_native','recursive_summary']:
  p=run/mode/'metadata.json'
  if not p.exists():continue
  m=json.loads(p.read_text());rows=read(p.parent/'responses.jsonl') if (p.parent/'responses.jsonl').exists() else [];committed=read(p.parent/'states.jsonl') if (p.parent/'states.jsonl').exists() else []
  updates[mode]=dict(complete=m['complete'],waves_completed=m.get('waves_completed',0),recorded_attempts=len(rows),attempts_by_number=dict(Counter(r['attempt'] for r in rows)),finishes=dict(Counter(r['finish_reason'] for r in rows)),committed_states=len(committed),carried_previous_after_invalid=sum(r['carried_previous_after_invalid'] for r in committed),words_by_step={str(step):dict(profile_mean=mean(len(r['state']['profile'].split()) for r in committed if r['step']==step),tracker_mean=mean(len(str(r['state']['hidden_tracker']).split()) for r in committed if r['step']==step)) for step in range(1,m.get('waves_completed',0)+1)},usage={key:sum(r['usage'][key] for r in rows) for key in ['prompt_tokens','completion_tokens']},wall_s=m.get('wall_s'))
  if mode in ['teacher_forced','recursive_native']:first_wave[mode]={r['task_id'].split('/'+mode+'/')[0]:r for r in rows if r['step']==1 and r['attempt']==1}
 anchor={}
 if len(first_wave)==2:
  a0=first_wave['teacher_forced'];b0=first_wave['recursive_native'];common=set(a0)&set(b0);anchor=dict(n_common_first_attempts=len(common),identical_messages=sum(a0[k]['messages']==b0[k]['messages'] for k in common),identical_responses=sum(a0[k]['response']==b0[k]['response'] for k in common))
 actors={}
 actor_paths={name:run/('actor_'+name) for name in ['baselines','teacher_forced','recursive_native','recursive_summary']} if args.consumer=='qwen3_8b' else {'preselected_review':run/('consumer_'+args.consumer)/'actor'}
 for name,directory in actor_paths.items():
  p=directory/'metadata.json'
  if p.exists() and json.loads(p.read_text())['complete']:
   rr=read(p.parent/'responses.jsonl');actors[name]=dict(n=len(rr),finishes=dict(Counter(r['finish_reason'] for r in rr)),empty=sum(not r['response'].strip() for r in rr),usage={key:sum(r['usage'][key] for r in rr) for key in ['prompt_tokens','completion_tokens']})
 status='COMPLETE' if not missing and all(v['complete'] for v in updates.values()) and len(updates)==3 and len(actors)==len(actor_paths) else 'INCOMPLETE'
 if status=='COMPLETE':
  assert len(scores)==435 and len(paired)==87 and all(len(v)==5 for v in paired.values())
  assert sum(v['n'] for v in actors.values())==(435 if args.consumer=='qwen3_8b' else 120)
 result=dict(experiment='D-E06',consumer=args.consumer,status=status,missing_likelihood_runs=missing,interpretation='Source-turn predictability, not unique psychologically correct action. Outside-square-brackets is a native-format proxy for visible words/actions, not a semantic visibility certificate. T has released before-states; R/S recur. World and released motivation are shared and can provide parallel information. Equal book macro with equal trajectories inside each book; n=8 convenience books, descriptive intervals. Compare conditions within each consumer; absolute NLL is not a cross-model ability ranking.',n_likelihood_rows=len(scores),n_distinct_questions=len(paired),groups=groups,paired_differences=comparisons,updaters=updates,first_wave_control=anchor,actors=actors,likelihood_validation_extra_forwards=sum(m.get('one_forward_alignment_validation',{}).get('extra_forward_calls',0) for m in metas.values()),details=scores)
 Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(status=status,n_rows=len(scores),groups={k:{metric:v['metrics'][metric]['book_macro'] if v['metrics'][metric] else None for metric in METRICS} for k,v in groups.items()},first_wave_control=anchor),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
