#!/usr/bin/env python3
"""Offline fixed aggregation of ArcANE and LongEvo role-play reproduction runs."""
import argparse,json,itertools,math,ast,re,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean

def read(path):return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
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

def arcane(root,experiment):
 run=root/'runs'/experiment;raw=read(run/'step5_judge/judgments.jsonl');valid_new=first_valid(raw,'judge_id');valid=list(valid_new);reused=[]
 if experiment=='D-E03':
  selected={r['trial_id'].rsplit('__p',1)[0] for r in read(root/'data/arcane_D-E03/references.jsonl')}
  reused=[r for r in first_valid(read(root/'runs/D-E01/step5_judge/judgments.jsonl'),'judge_id') if r['probe_id'] in selected]
  valid+=reused
 bucket=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
 details=defaultdict(dict)
 for r in valid:
  group=r['model']+'|'+r['mode'];novel=r['novel']
  dims=['apf','rpf','rae'] if r['kind']=='per_response' else ['ptf_alignment','ptf_direction','ptf_shape']
  scores={k:r['scores'][k] for k in dims}
  if r['kind']=='trajectory':scores={'ptf':mean(scores.values())}
  for dim,score in scores.items():bucket[group][novel][dim].append(score)
  details[group][r['judge_id']]=r
 result={}
 for group,novels in sorted(bucket.items()):
  by_novel={n:{d:mean(v) for d,v in dims.items()} for n,dims in novels.items()}
  metrics={d:mean(x[d] for x in by_novel.values() if d in x) for d in ['apf','rpf','rae','ptf'] if any(d in x for x in by_novel.values())}
  result[group]=dict(metrics=metrics,by_novel=by_novel,metric_descriptive_novel_bootstrap95={d:interval([x[d] for x in by_novel.values() if d in x]) for d in metrics},n_per_response=sum(r['kind']=='per_response' for r in details[group].values()),n_trajectories=sum(r['kind']=='trajectory' for r in details[group].values()))
 paired={}
 models=sorted({g.split('|')[0] for g in result})
 for model in models:
  if model+'|vanilla' not in result:continue
  for mode in ['arc','summary']:
   if model+'|'+mode not in result:continue
   a=result[model+'|'+mode]['by_novel'];b=result[model+'|vanilla']['by_novel'];common=sorted(set(a)&set(b));out={}
   for dim in ['apf','rpf','rae','ptf']:
    ds={n:a[n][dim]-b[n][dim] for n in common if dim in a[n] and dim in b[n]}
    if ds:out[dim]=dict(mean_delta=mean(ds.values()),by_novel=ds,descriptive_novel_bootstrap95=interval(ds.values()))
   paired[model+'|'+mode+'-vanilla']=out
 sources={}
 for path in sorted(run.glob('*/responses.jsonl')):
  rows=read(path);sources[path.parent.name]=dict(n=len(rows),unique_task_ids=len({r.get('task_id') for r in rows}),finishes=dict(Counter(r.get('finish_reason') for r in rows)),tokens={k:sum(r.get('usage',{}).get(k,0) for r in rows) for k in ['prompt_tokens','completion_tokens']})
 return dict(experiment=experiment,judge='Step5 low; official prompts, scale100; different from original paper judge',aggregation='Per-metric novel macro means; no pooled cross-benchmark overall. Phase-level APF/RPF/RAE pooled within novel as native table, PTF over complete probe trajectories. Paired deltas by novel; six-book convenience sample intervals descriptive only.',calls_recorded=len(raw),unique_judge_ids=len({r['judge_id'] for r in raw}),valid_judge_ids=len(valid_new),reused_reference_judgments=len(reused),valid_by_kind=dict(Counter(r['kind'] for r in valid)),error_attempts=dict(Counter(r.get('error') for r in raw if r.get('error'))),usage={k:sum(r.get('usage',{}).get(k,0) for r in raw) for k in ['prompt_tokens','completion_tokens','total_tokens']},groups=result,paired_deltas=paired,source_runs=sources)

def phase(root):
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
   except ValueError:obj=native_parse(r['response']);parse_method='native_parser_fallback';fallback+=1
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
 return dict(experiment='D-E02',judge='Local Qwen3-32B, native PHASE-Tree rubric, greedy/nonthinking; not original GPT4.1 or official Emb',n_judgments=len(rows),valid=len(scores),native_parser_fallback=fallback,invalid=errors,groups=groups,paired=pairs,details=scores,aggregation='Four-corpus macro, question-level pairing; intervals descriptive, four corpora not population sample. No cross-benchmark score pooling.')

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--experiment',choices=['D-E01','D-E02','D-E03'],required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root)
 obj=phase(root) if args.experiment=='D-E02' else arcane(root,args.experiment)
 Path(args.out).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
 if args.experiment=='D-E02':print(json.dumps(obj['groups'],indent=2))
 else:print(json.dumps({k:dict(metrics=v['metrics'],n_per_response=v['n_per_response'],n_trajectories=v['n_trajectories']) for k,v in obj['groups'].items()},indent=2))
if __name__=='__main__':main()
