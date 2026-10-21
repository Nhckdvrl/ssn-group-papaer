#!/usr/bin/env python3
"""Book-level descriptive agreement on frozen native update supervision."""
import argparse,json,hashlib,random,importlib.util
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
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);a.add_argument('--condition',choices=['original','identity_line'],default='original');a.add_argument('--plan-run');args=a.parse_args();root=Path(args.asset_root);refs={r['task_id']:r for r in read(root/'data/update_D-E04/references.jsonl')};groups={};details=[]
 spec=importlib.util.spec_from_file_location('native_ew_utils',root/'vendor/EvolvingWorld/simulation/utils.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
 base=root/'runs/D-E04';base=base/'identity_line' if args.condition=='identity_line' else base
 specs=[(folder,base/folder,'responses.jsonl') for folder in ['qwen3_8b','qwen3_32b']] if not args.plan_run else [('step5_preview',Path(args.plan_run),'selected_responses.jsonl')]
 for folder,run,filename in specs:
  rows=read(run/filename);assert len(rows)==len({r['task_id'] for r in rows})==len(refs);assert json.loads((run/'metadata.json').read_text())['complete'];book=defaultdict(list);g=[]
  for r in rows:
   o=parse(r['response']);ref=refs[r['task_id']];gold=ref['target']['profile_updated'];core=bool(o is not None and type(o.get('profile_updated')) is bool and ((o['profile_updated'] and isinstance(o.get('updated_profile'),str) and o['updated_profile'].strip()) or (not o['profile_updated'] and 'updated_profile' in o and o['updated_profile'] is None)))
   schema=bool(core and 'hidden_tracker' in o and (o['hidden_tracker'] is None or isinstance(o['hidden_tracker'],(str,dict,list))) and isinstance(o.get('short_description'),str) and o['short_description'].strip());flag=o.get('profile_updated') if o else None
   try:literal=json.loads(r['response']);literal_ok=isinstance(literal,dict)
   except ValueError:literal_ok=False
   try:
    compatible=native.extract_json_fragment(r['response']);cp=compatible.get('updated_profile');cf=compatible.get('profile_updated');converted=native.dict_to_markdown_text(cp) if isinstance(cp,(dict,list)) else cp
    # Missing task keys must not silently turn an inner fragment into a No-Update.
    runtime_ok=type(cf) is bool and ((cf and isinstance(converted,str) and bool(converted.strip())) or (not cf and 'updated_profile' in compatible and cp is None))
   except Exception:runtime_ok=False;cf=None
   v=dict(model=folder,task_id=r['task_id'],book_name=r['book_name'],role=r['role'],scene_index=r['scene_index'],reference_profile_updated=gold,predicted_profile_updated=flag,literal_json_valid=literal_ok,core_valid=core,full_schema_valid=schema,native_runtime_valid=runtime_ok,native_runtime_agreement=bool(runtime_ok and cf==gold),flag_only_agreement=bool(o is not None and type(flag) is bool and flag==gold),tracker_type=type(o.get('hidden_tracker')).__name__ if o else 'invalid',agreement=bool(core and flag==gold),finish_reason=r['finish_reason'],description_words=len(o.get('short_description','').split()) if o and isinstance(o.get('short_description'),str) else None,response_sha256=hashlib.sha256(r['response'].encode()).hexdigest(),preselected_case=ref['preselected_case']);g.append(v);book[r['book_name']].append(v)
  by={}
  for b,rr in sorted(book.items()):by[b]=dict(n=len(rr),agreement=mean(v['agreement'] for v in rr),change_recall=mean(v['agreement'] for v in rr if v['reference_profile_updated']),no_change_preservation=mean(v['agreement'] for v in rr if not v['reference_profile_updated']))
  metrics={k:mean(v[k] for v in by.values()) for k in ['agreement','change_recall','no_change_preservation']}
  runtime_by={b:dict(agreement=mean(v['native_runtime_agreement'] for v in rr),change_recall=mean(v['native_runtime_agreement'] for v in rr if v['reference_profile_updated']),no_change_preservation=mean(v['native_runtime_agreement'] for v in rr if not v['reference_profile_updated'])) for b,rr in book.items()}
  groups[folder]=dict(n=len(rows),literal_json_valid=sum(v['literal_json_valid'] for v in g),core_valid=sum(v['core_valid'] for v in g),full_schema_valid=sum(v['full_schema_valid'] for v in g),native_runtime_valid=sum(v['native_runtime_valid'] for v in g),native_runtime_book_macro={k:mean(v[k] for v in runtime_by.values()) for k in metrics},native_runtime_by_book=runtime_by,native_runtime_bootstrap95={k:ci(v[k] for v in runtime_by.values()) for k in metrics},flag_only_agreement=mean(v['flag_only_agreement'] for v in g),tracker_types=dict(Counter(v['tracker_type'] for v in g)),confusion=dict(tp=sum(v['reference_profile_updated'] and v['agreement'] for v in g),tn=sum(not v['reference_profile_updated'] and v['agreement'] for v in g),fp=sum(not v['reference_profile_updated'] and v['core_valid'] and v['predicted_profile_updated'] for v in g),fn=sum(v['reference_profile_updated'] and v['core_valid'] and not v['predicted_profile_updated'] for v in g)),finishes=dict(Counter(v['finish_reason'] for v in g)),predicted_flags=dict(Counter(str(v['predicted_profile_updated']) for v in g)),by_book=by,book_macro=metrics,descriptive_book_bootstrap95={k:ci(v[k] for v in by.values()) for k in metrics},usage={k:sum(r['usage'][k] for r in rows) for k in ['prompt_tokens','completion_tokens']},wall_s=json.loads((run/'metadata.json').read_text())['wall_s']);details.extend(g)
 paired={k:{b:groups['qwen3_32b']['by_book'][b][k]-groups['qwen3_8b']['by_book'][b][k] for b in groups['qwen3_8b']['by_book']} for k in ['agreement','change_recall','no_change_preservation']} if not args.plan_run else {}
 both=defaultdict(dict)
 for r in details:both[r['task_id']][r['model']]=r
 common=[tid for tid,v in both.items() if len(v)>1 and all(not r['agreement'] for r in v.values())]
 native_common=[tid for tid,v in both.items() if len(v)>1 and all(not r['native_runtime_agreement'] for r in v.values())]
 result=dict(experiment='D-E05' if args.plan_run else 'D-E04',condition=args.condition,interpretation='Agreement with released hindsight-constructed supervision, not unique psychological accuracy; teacher-forced native training-asset diagnostic, no rollout/generalization claim. Original strict primary preserved; native-runtime compatibility is post-hoc code-aligned sensitivity, no missing field imputation. Per-group usage describes selected candidate rows; request-attempt usage is in the run ledger.',groups=groups,constant_references={'always_no_update':dict(agreement=.5,change_recall=0,no_change_preservation=1),'always_update':dict(agreement=.5,change_recall=1,no_change_preservation=0)},paired_book_deltas_32b_minus_8b={k:dict(mean=mean(v.values()),by_book=v,descriptive_bootstrap95=ci(v.values())) for k,v in paired.items()},both_disagree_reference=common,both_disagree_reference_native_runtime=native_common,details=details,bootstrap='20000 book-resamples, Random(0); n=8 convenience books, descriptive only')
 Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:{x:y for x,y in v.items() if x not in ['by_book']} for k,v in groups.items()},indent=2))
if __name__=='__main__':main()
