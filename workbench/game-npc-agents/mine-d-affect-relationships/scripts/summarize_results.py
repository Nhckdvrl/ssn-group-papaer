#!/usr/bin/env python3
"""Offline fixed aggregation of ArcANE and LongEvo role-play reproduction runs."""
import argparse,json,itertools,math,ast,re,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean

def read(path):return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
def token_sum(rows,key):
 return sum((r.get('usage',{}).get('total_tokens',r.get('usage',{}).get('prompt_tokens',0)+r.get('usage',{}).get('completion_tokens',0)) if key=='total_tokens' else r.get('usage',{}).get(key,0)) for r in rows)
def interval(v):
 v=list(v)
 if not v:return None
 x=sorted(mean(z) for z in itertools.product(v,repeat=len(v)))
 return [x[int(.025*(len(x)-1))],x[int(.975*(len(x)-1))]]
def first_valid(rows,key):
 result={}
 for r in rows:
  if r.get('parse_ok') and r[key] not in result:result[r[key]]=r
 return list(result.values())

def parse_arcane_local(row):
 """Validate scores, keeping native JSON compliance separate from score recovery.

 A complete leading JSON object is never reconstructed from partial numbers.
 Trailing prose/extra braces are retained in raw and explicitly flagged.
 """
 s=row['response'].strip();native=s
 if native.startswith('```'):native='\n'.join(l for l in native.splitlines() if not l.strip().startswith('```')).strip()
 strict=False;obj=None;method='invalid'
 try:obj=json.loads(native);strict=True;method='native_json'
 except ValueError:
  prefix=re.sub(r'^```(?:json)?\s*','',s).lstrip()
  try:obj,end=json.JSONDecoder().raw_decode(prefix);method='complete_leading_json'
  except ValueError:pass
 dims=['apf','rpf','rae'] if row['kind']=='per_response' else ['ptf_alignment','ptf_direction','ptf_shape']
 ok=isinstance(obj,dict) and isinstance(obj.get('scores'),dict) and all(type(obj['scores'].get(d)) is int and 1<=obj['scores'][d]<=100 for d in dims)
 out={k:row[k] for k in ['kind','mode','novel','character_slug','probe_id','finish_reason']}
 out.update(judge_id=row['task_id'],model=row['actor_model'],parse_ok=ok,native_json=strict and ok,parse_method=method,judge_response_sha256=hashlib.sha256(row['response'].encode()).hexdigest(),evaluator_messages_sha256=hashlib.sha256(json.dumps(row.get('messages',[]),sort_keys=True,ensure_ascii=False).encode()).hexdigest(),scores={d:obj['scores'][d] for d in dims} if ok else None,usage=row.get('usage',{}))
 if 'candidate_sha256' in row:out['candidate_sha256']=row['candidate_sha256']
 for k in ['phase_idx','n_phases']:
  if k in row:out[k]=row[k]
 return out

def load_arcane(root,experiment,judge,strict=False):
 run=root/'runs'/experiment
 if judge=='step5':return read(run/'step5_judge/judgments.jsonl')
 paths=[run/name/'responses.jsonl' for name in ['local_qwen32_judge','local_qwen32_judge_recovery','local_qwen32_capacity_judge','local_qwen32_capacity_judge_recovery']]
 raw=[parse_arcane_local(r) for p in paths if p.exists() for r in read(p)]
 if strict:
  for r in raw:r['parse_ok']=r['native_json']
 return raw

def paired_arcane(details,lhs,rhs):
 def key(r):return (r['kind'],r['novel'],r['probe_id'],r.get('phase_idx'))
 a={key(r):r for r in details[lhs].values()};b={key(r):r for r in details[rhs].values()};common=set(a)&set(b);out={}
 for dim in ['apf','rpf','rae','ptf']:
  ds=defaultdict(list)
  for k in common:
   if (dim=='ptf')!=(k[0]=='trajectory'):continue
   def score(r):return mean(r['scores'][d] for d in ['ptf_alignment','ptf_direction','ptf_shape']) if dim=='ptf' else r['scores'][dim]
   ds[k[1]].append(score(a[k])-score(b[k]))
  if ds:
   means={n:mean(v) for n,v in ds.items()};out[dim]=dict(mean_delta=mean(means.values()),n_common_units=sum(map(len,ds.values())),by_novel=means,descriptive_novel_bootstrap95=interval(means.values()))
 return out

def arcane(root,experiment,judge='local',strict=False):
 run=root/'runs'/experiment;raw=load_arcane(root,experiment,judge,strict);valid_new=first_valid(raw,'judge_id');valid=list(valid_new);reused=[]
 if experiment=='D-E03':
  selected={r['trial_id'].rsplit('__p',1)[0] for r in read(root/'data/arcane_D-E03/references.jsonl')}
  reused=[r for r in first_valid(load_arcane(root,'D-E01',judge,strict),'judge_id') if r['probe_id'] in selected]
  valid+=reused
 elif experiment=='D-E09':
  selected={r['trial_id'].rsplit('__p',1)[0] for r in read(root/'data/prefix_D-E09/references.jsonl')}
  reused=[r for r in first_valid(load_arcane(root,'D-E01',judge,strict),'judge_id') if r['probe_id'] in selected]
  valid+=reused
 elif experiment in ['D-E07','D-E08']:
  # S/Monte in the old D-E03 run used the wrong narrative-unit binding.
  # Only source-qualified rows enter the corrected table, irrespective of score.
  selected={r['trial_id'].rsplit('__p',1)[0] for r in read(root/'data/arcane_D-E03/references.jsonl')}
  prior=first_valid(load_arcane(root,'D-E03',judge,strict),'judge_id')+[r for r in first_valid(load_arcane(root,'D-E01',judge,strict),'judge_id') if r['probe_id'] in selected]
  reused=[r for r in prior if not (r['novel']=='Monte_Cristo' and r['mode']=='summary')]
  if experiment=='D-E08':reused+=first_valid(load_arcane(root,'D-E07',judge,strict),'judge_id')
  assert len({r['judge_id'] for r in reused})==len(reused)
  assert not (set(r['judge_id'] for r in reused)&set(r['judge_id'] for r in valid_new))
  valid+=reused
 trials={}
 for t in read(root/'data/arcane_D-E01/tasks.jsonl'):
  tr=t['trial'];trials[tr['novel'],tr['probe_id']]=tr
 bucket=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
 types=defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:defaultdict(list))))
 characters=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
 axes=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
 details=defaultdict(dict)
 for r in valid:
  group=r['model']+'|'+r['mode'];novel=r['novel']
  dims=['apf','rpf','rae'] if r['kind']=='per_response' else ['ptf_alignment','ptf_direction','ptf_shape']
  scores={k:r['scores'][k] for k in dims}
  if r['kind']=='trajectory':scores={'ptf':mean(scores.values())}
  tr=trials[novel,r['probe_id']]
  for dim,score in scores.items():
   bucket[group][novel][dim].append(score);types[group][tr['probe_type']][novel][dim].append(score);characters[group][novel+'/'+r['character_slug']][dim].append(score);axes[group][novel+'/'+r['character_slug']+'/'+tr['axis_id']][dim].append(score)
  details[group][r['judge_id']]=r
 result={}
 for group,novels in sorted(bucket.items()):
  by_novel={n:{d:mean(v) for d,v in dims.items()} for n,dims in novels.items()}
  metrics={d:mean(x[d] for x in by_novel.values() if d in x) for d in ['apf','rpf','rae','ptf'] if any(d in x for x in by_novel.values())}
  by_type={}
  for typ,books in types[group].items():
   nb={n:{d:mean(v) for d,v in ds.items()} for n,ds in books.items()};by_type[typ]=dict(n_books=len(nb),metrics={d:mean(v[d] for v in nb.values() if d in v) for d in metrics if any(d in v for v in nb.values())},by_novel=nb)
  slices={name:{d:mean(v[d] for n,v in by_novel.items() if n in novels and d in v) for d in metrics if any(n in novels and d in v for n,v in by_novel.items())} for name,novels in [('main_public_four',{'don_quixote','Benjamin_Franklin','Monte_Cristo','Anna_Kareina'}),('lowpop_two',{'He Knew He Was Right','The Odd Women'})]}
  result[group]=dict(metrics=metrics,by_novel=by_novel,by_evaluation_slice=slices,by_probe_type=by_type,by_character={c:{d:dict(mean=mean(v),n=len(v)) for d,v in ds.items()} for c,ds in characters[group].items()},by_axis={c:{d:dict(mean=mean(v),n=len(v)) for d,v in ds.items()} for c,ds in axes[group].items()},metric_descriptive_novel_bootstrap95={d:interval([x[d] for x in by_novel.values() if d in x]) for d in metrics},n_per_response=sum(r['kind']=='per_response' for r in details[group].values()),n_trajectories=sum(r['kind']=='trajectory' for r in details[group].values()))
 paired={}
 models=sorted({g.split('|')[0] for g in result})
 for model in models:
  if model+'|vanilla' not in result:continue
  for mode in ['arc','summary','state_summary','state_summary_step','prefix_memory']:
   if model+'|'+mode not in result:continue
   paired[model+'|'+mode+'-vanilla']=paired_arcane(details,model+'|'+mode,model+'|vanilla')
  if model+'|summary' in result and model+'|arc' in result:paired[model+'|arc-summary']=paired_arcane(details,model+'|arc',model+'|summary')
  if model+'|state_summary' in result:
   for other in ['summary','arc']:
    if model+'|'+other in result:paired[model+'|state_summary-'+other]=paired_arcane(details,model+'|state_summary',model+'|'+other)
  if model+'|state_summary_step' in result:
   for other in ['state_summary','summary','arc']:
    if model+'|'+other in result:paired[model+'|state_summary_step-'+other]=paired_arcane(details,model+'|state_summary_step',model+'|'+other)
  if model+'|prefix_memory' in result and model+'|arc' in result:paired[model+'|prefix_memory-arc']=paired_arcane(details,model+'|prefix_memory',model+'|arc')
 for mode in ['vanilla','arc','summary','state_summary','state_summary_step','prefix_memory']:
  for lhs,rhs,label in [('arcane-8B-dpo','Qwen/Qwen3-8B','ArcANE8DPO-minus-Qwen8'),('Qwen/Qwen3-32B','Qwen/Qwen3-8B','Qwen32-minus-Qwen8'),('arcane-8B-dpo','Qwen/Qwen3-32B','ArcANE8DPO-minus-Qwen32')]:
   if lhs+'|'+mode in result and rhs+'|'+mode in result:paired[label+'|'+mode]=paired_arcane(details,lhs+'|'+mode,rhs+'|'+mode)
 sources={}
 for path in sorted(run.glob('*/responses.jsonl')):
  rows=read(path);sources[path.parent.name]=dict(n=len(rows),unique_task_ids=len({r.get('task_id') for r in rows}),finishes=dict(Counter(r.get('finish_reason') for r in rows)),tokens={k:sum(r.get('usage',{}).get(k,0) for r in rows) for k in ['prompt_tokens','completion_tokens']})
 detail_keys=['judge_id','kind','model','mode','novel','character_slug','probe_id','phase_idx','n_phases','scores','parse_method','native_json','finish_reason','judge_response_sha256','evaluator_messages_sha256','candidate_sha256','input_response_sha256']
 compact=[]
 for r in valid:
  row={k:r[k] for k in detail_keys if k in r}
  if judge=='step5':row['judge_response_sha256']=hashlib.sha256(str(r.get('raw','')).encode()).hexdigest();row['evaluator_messages_sha256']=hashlib.sha256(json.dumps(r['request']['messages'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
  compact.append(row)
 return dict(experiment=experiment,judge=('Local Qwen3-32B greedy/nonthinking' if judge=='local' else 'Step5 low partial only')+'; official prompts, scale100; different from original paper judge',strict_native_json=strict,aggregation='Per-metric novel macro means; no pooled cross-benchmark overall. Phase-level APF/RPF/RAE pooled within novel as native table, PTF over complete probe trajectories. Paired deltas by novel; six-book convenience sample intervals descriptive only.',calls_recorded=len(raw),unique_judge_ids=len({r['judge_id'] for r in raw}),valid_judge_ids=len(valid_new),reused_reference_judgments=len(reused),valid_by_kind=dict(Counter(r['kind'] for r in valid)),parse_methods=dict(Counter(r.get('parse_method','step_api') for r in valid_new)),error_attempts=dict(Counter(r.get('error') for r in raw if r.get('error'))),invalid_judge_ids=[r['judge_id'] for r in raw if not r.get('parse_ok') and r['judge_id'] not in {v['judge_id'] for v in valid_new}],usage={k:token_sum(raw,k) for k in ['prompt_tokens','completion_tokens','total_tokens']},groups=result,paired_deltas=paired,source_runs=sources,details=compact)

def phase(root,strict=False):
 rows=read(root/'runs/D-E02/qwen3_32b_judge/responses.jsonl');scores=[];errors=[]
 source=ast.parse((root/'vendor/PHASE-Tree/evaluation/judge.py').read_text())
 parser_node=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='parse_judge_response')
 namespace={'json':json,'re':re};exec(compile(ast.Module(body=[parser_node],type_ignores=[]),'<native PHASE parser>','exec'),namespace)
 native_parse=namespace['parse_judge_response'];fallback=0
 for r in rows:
  text=r['response'].strip()
  if text.startswith('```'):text='\n'.join(l for l in text.splitlines() if not l.strip().startswith('```'))
  try:
   try:obj=json.loads(text);parse_method='strict_json'
   except ValueError:
    if strict:raise
    obj=native_parse(r['response']);parse_method='native_parser_fallback';fallback+=1
   assert all(type(obj[k]) in [int,float] and 1<=obj[k]<=5 for k in ['character_score','semantic_score'])
   scores.append(dict(task_id=r['task_id'],question_id=r['question_id'],corpus=r['corpus'],split=r['split'],role=r['role'],mode=r['mode'],parse_method=parse_method,character_score=obj['character_score'],semantic_score=obj['semantic_score'],reasoning_sha256=hashlib.sha256(str(obj.get('reasoning','')).encode()).hexdigest()))
  except Exception:errors.append(dict(task_id=r['task_id'],finish_reason=r['finish_reason']))
 bucket=defaultdict(lambda:defaultdict(list))
 for r in scores:bucket[r['mode']][r['corpus']].append(r)
 groups={}
 for mode,corpora in sorted(bucket.items()):
  by_corpus={c:{k:mean(r[k] for r in rs) for k in ['character_score','semantic_score']} for c,rs in corpora.items()}
  by_split={split:{k:mean(x[k] for x in scores if x['mode']==mode and x['split']==split) for k in ['character_score','semantic_score']} for split in ['random_test','ood_test']}
  groups[mode]=dict(n=sum(len(rs) for rs in corpora.values()),by_corpus=by_corpus,by_split=by_split,macro={k:mean(x[k] for x in by_corpus.values()) for k in ['character_score','semantic_score']},descriptive_corpus_bootstrap95={k:interval([x[k] for x in by_corpus.values()]) for k in ['character_score','semantic_score']})
 by_question=defaultdict(dict)
 for r in scores:by_question[r['question_id']][r['mode']]=r
 pairs={}
 for comparison in ['base','raw_profile','naive_rewrite']:
  changes=[]
  for q,m in by_question.items():
   if 'phase_tree' in m and comparison in m:changes.append(dict(question_id=q,corpus=m['phase_tree']['corpus'],split=m['phase_tree']['split'],role=m['phase_tree']['role'],character_delta=m['phase_tree']['character_score']-m[comparison]['character_score'],semantic_delta=m['phase_tree']['semantic_score']-m[comparison]['semantic_score']))
  pairs['phase_tree-'+comparison]=dict(n=len(changes),semantic_win_tie_loss=[sum(x['semantic_delta']>0 for x in changes),sum(x['semantic_delta']==0 for x in changes),sum(x['semantic_delta']<0 for x in changes)],changes=changes)
 return dict(experiment='D-E02',judge='Local Qwen3-32B, native PHASE-Tree rubric, greedy/nonthinking; not original GPT4.1 or official Emb',strict_native_json=strict,n_judgments=len(rows),valid=len(scores),native_parser_fallback=fallback,invalid=errors,groups=groups,paired=pairs,details=scores,aggregation='Four-corpus macro, question-level pairing; intervals descriptive, four corpora not population sample. No cross-benchmark score pooling.')

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--experiment',choices=['D-E01','D-E02','D-E03','D-E07','D-E08','D-E09'],required=True);a.add_argument('--out',required=True);a.add_argument('--judge',choices=['local','step5'],default='local');a.add_argument('--strict-native-json',action='store_true');args=a.parse_args();root=Path(args.asset_root)
 if args.experiment in ['D-E07','D-E08','D-E09']:assert args.judge=='local','The Step compiler is not a Step judge run'
 obj=phase(root,args.strict_native_json) if args.experiment=='D-E02' else arcane(root,args.experiment,args.judge,args.strict_native_json)
 Path(args.out).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
 if args.experiment=='D-E02':print(json.dumps(obj['groups'],indent=2))
 else:print(json.dumps({k:dict(metrics=v['metrics'],n_per_response=v['n_per_response'],n_trajectories=v['n_trajectories']) for k,v in obj['groups'].items()},indent=2))
if __name__=='__main__':main()
