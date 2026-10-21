#!/usr/bin/env python3
"""Post-hoc input description; speaker-tag counts do not establish actor presence."""
import argparse,json,re
from pathlib import Path
from collections import Counter,defaultdict

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--audit',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);audit=json.loads(Path(args.audit).read_text());ann={(r['model'],r['task_id']):r for r in audit['annotations']};details=[]
 for task in map(json.loads,(root/'data/update_D-E04/tasks.jsonl').read_text().splitlines()):
  scene=task['messages'][1]['content'].split('## Scene Interactions\n')[1].split('\n\n## Current Profile')[0];counts=Counter();bad=0
  for text in re.findall(r'^(\[[^\n]*?\]):',scene,re.M):
   try:names=json.loads(text);assert isinstance(names,list)
   except Exception:bad+=1;continue
   counts.update(str(n).casefold() for n in names)
  target=task['role'].casefold();r=dict(task_id=task['task_id'],book_name=task['book_name'],target=task['role'],n_target_tagged_turns=counts[target],n_all_tagged_turns=sum(counts.values()),tag_parse_failures=bad,top_tagged_roles=counts.most_common(3))
  for model in ['qwen3_8b','qwen3_32b']:r[model+'_subject_status']=ann[model,task['task_id']]['status'];r[model+'_definite_subject_error']=ann[model,task['task_id']]['definite_current_record_subject_error']
  details.append(r)
 summary={}
 for label,pred in [('zero_target_tag',lambda r:r['n_target_tagged_turns']==0),('has_target_tag',lambda r:r['n_target_tagged_turns']>0)]:
  rows=[r for r in details if pred(r)];summary[label]=dict(n=len(rows),explicit_subject_substitutions={m:sum(r[m+'_subject_status']=='explicit_wrong_subject' for r in rows) for m in ['qwen3_8b','qwen3_32b']},definite_current_record_subject_errors={m:sum(r[m+'_definite_subject_error'] for r in rows) for m in ['qwen3_8b','qwen3_32b']})
 result=dict(status='POST-HOC descriptive input audit, no model calls',interpretation='Exact case-folded native speaker tags. Zero tags does not mean absent/unobservable: narration, reported events, aliases and group references still provide evidence. Association is not mechanism, independent samples, or a causal effect.',summary=summary,details=details)
 Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
