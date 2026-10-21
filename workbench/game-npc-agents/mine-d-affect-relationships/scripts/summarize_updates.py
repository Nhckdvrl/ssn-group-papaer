#!/usr/bin/env python3
"""Book-level descriptive agreement on frozen native update supervision."""
import argparse,json,hashlib,random
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean

def read(p):return [json.loads(l) for l in p.read_text().splitlines()]
def ci(values):
 values=list(values);rng=random.Random(0);samples=sorted(mean(rng.choices(values,k=len(values))) for _ in range(20000));return [samples[499],samples[19499]]
def parse(text):
 s=text.strip()
 if s.startswith('```'):s='\n'.join(l for l in s.splitlines() if not l.strip().startswith('```')).strip()
 try:o=json.loads(s)
 except ValueError:return None
 return o if isinstance(o,dict) else None
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);refs={r['task_id']:r for r in read(root/'data/update_D-E04/references.jsonl')};groups={};details=[]
 for folder in ['qwen3_8b','qwen3_32b']:
  run=root/'runs/D-E04'/folder;rows=read(run/'responses.jsonl');assert len(rows)==len({r['task_id'] for r in rows})==len(refs);assert json.loads((run/'metadata.json').read_text())['complete'];book=defaultdict(list);g=[]
  for r in rows:
   o=parse(r['response']);ref=refs[r['task_id']];gold=ref['target']['profile_updated'];core=bool(o is not None and type(o.get('profile_updated')) is bool and ((o['profile_updated'] and isinstance(o.get('updated_profile'),str) and o['updated_profile'].strip()) or (not o['profile_updated'] and 'updated_profile' in o and o['updated_profile'] is None)))
   schema=bool(core and 'hidden_tracker' in o and (o['hidden_tracker'] is None or isinstance(o['hidden_tracker'],(str,dict))) and isinstance(o.get('short_description'),str) and o['short_description'].strip());flag=o.get('profile_updated') if o else None
   v=dict(model=folder,task_id=r['task_id'],book_name=r['book_name'],role=r['role'],scene_index=r['scene_index'],reference_profile_updated=gold,predicted_profile_updated=flag,core_valid=core,full_schema_valid=schema,tracker_type=type(o.get('hidden_tracker')).__name__ if o else 'invalid',agreement=bool(core and flag==gold),finish_reason=r['finish_reason'],description_words=len(o.get('short_description','').split()) if o and isinstance(o.get('short_description'),str) else None,response_sha256=hashlib.sha256(r['response'].encode()).hexdigest(),preselected_case=ref['preselected_case']);g.append(v);book[r['book_name']].append(v)
  by={}
  for b,rr in sorted(book.items()):by[b]=dict(n=len(rr),agreement=mean(v['agreement'] for v in rr),change_recall=mean(v['agreement'] for v in rr if v['reference_profile_updated']),no_change_preservation=mean(v['agreement'] for v in rr if not v['reference_profile_updated']))
  metrics={k:mean(v[k] for v in by.values()) for k in ['agreement','change_recall','no_change_preservation']}
  groups[folder]=dict(n=len(rows),core_valid=sum(v['core_valid'] for v in g),full_schema_valid=sum(v['full_schema_valid'] for v in g),tracker_types=dict(Counter(v['tracker_type'] for v in g)),confusion=dict(tp=sum(v['reference_profile_updated'] and v['agreement'] for v in g),tn=sum(not v['reference_profile_updated'] and v['agreement'] for v in g),fp=sum(not v['reference_profile_updated'] and v['core_valid'] and v['predicted_profile_updated'] for v in g),fn=sum(v['reference_profile_updated'] and v['core_valid'] and not v['predicted_profile_updated'] for v in g)),finishes=dict(Counter(v['finish_reason'] for v in g)),predicted_flags=dict(Counter(str(v['predicted_profile_updated']) for v in g)),by_book=by,book_macro=metrics,descriptive_book_bootstrap95={k:ci(v[k] for v in by.values()) for k in metrics},usage={k:sum(r['usage'][k] for r in rows) for k in ['prompt_tokens','completion_tokens']},wall_s=json.loads((run/'metadata.json').read_text())['wall_s']);details.extend(g)
 paired={k:{b:groups['qwen3_32b']['by_book'][b][k]-groups['qwen3_8b']['by_book'][b][k] for b in groups['qwen3_8b']['by_book']} for k in ['agreement','change_recall','no_change_preservation']}
 both=defaultdict(dict)
 for r in details:both[r['task_id']][r['model']]=r
 common=[tid for tid,v in both.items() if all(not r['agreement'] for r in v.values())]
 result=dict(experiment='D-E04',interpretation='Agreement with released hindsight-constructed supervision, not unique psychological accuracy; teacher-forced native training-asset diagnostic, no rollout/generalization claim.',groups=groups,constant_references={'always_no_update':dict(agreement=.5,change_recall=0,no_change_preservation=1),'always_update':dict(agreement=.5,change_recall=1,no_change_preservation=0)},paired_book_deltas_32b_minus_8b={k:dict(mean=mean(v.values()),by_book=v,descriptive_bootstrap95=ci(v.values())) for k,v in paired.items()},both_disagree_reference=common,details=details,bootstrap='20000 book-resamples, Random(0); n=8 convenience books, descriptive only')
 Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:{x:y for x,y in v.items() if x not in ['by_book']} for k,v in groups.items()},indent=2))
if __name__=='__main__':main()
