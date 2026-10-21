#!/usr/bin/env python3
"""Apply the identical complete-before-state PUF adapter to the strong Plan actor."""
import argparse,json,hashlib
from pathlib import Path
from prepare_update_quality import load

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);vendor=root/'vendor/EvolvingWorld';native=load('plan_ew_utils',vendor/'simulation/utils.py');prompts=load('plan_ew_prompts',vendor/'evaluation/prompts.py');read=lambda p:[json.loads(l) for l in p.read_text().splitlines()]
 originals={r['task_id']:r for r in read(root/'data/update_D-E04/tasks.jsonl')}
 def render(r):
  t=originals[r['task_id']]
  try:
   o=native.extract_json_fragment(r['response']);flag=o.get('profile_updated');p=o.get('updated_profile');profile=native.dict_to_markdown_text(p) if isinstance(p,(dict,list)) else p
   valid=type(flag) is bool and ((flag and isinstance(profile,str) and bool(profile.strip())) or (not flag and 'updated_profile' in o and p is None)) and 'hidden_tracker' in o and isinstance(o.get('short_description'),str) and bool(o['short_description'].strip())
  except Exception:return None
  if not valid:return None
  after=dict(profile_updated=flag,profile_after=profile if flag else '(Unchanged from the scene-start profile)',hidden_tracker=o['hidden_tracker'],description=o['short_description']);user=t['messages'][1]['content'];body=f"Target character record: {r['role']}\n\n## Complete input available to the updater\n{user}\n\n## Persisted state after this scene\n{json.dumps(after,ensure_ascii=False,indent=2)}\n\n{prompts.SINGLE_METRIC_OUTPUT_FORMAT}"
  return [dict(role='system',content=prompts.build_per_scene_system_prompt('PUF')),dict(role='user',content=body)]
 # Prove the adapter did not change for the already frozen local candidates.
 local={}
 for condition in ['original','identity_line']:
  for model in ['qwen3_8b','qwen3_32b']:
   base=root/'runs/D-E04';base=base/'identity_line' if condition=='identity_line' else base
   for r in read(base/model/'responses.jsonl'):local[model,condition,r['task_id']]=r
 frozen=read(root/'data/update_D-E04/puf_tasks.jsonl')
 for task in frozen:assert render(local[task['actor_model'],task['condition'],task['question_id']])==task['messages']
 run=root/'runs/D-E05/step5';assert json.loads((run/'metadata.json').read_text())['complete'];rows=read(run/'responses.jsonl');selected={};fallback={}
 for r in rows:
  if r.get('http_status')!=200:continue
  fallback.setdefault(r['task_id'],r)
  if render(r) is not None:selected.setdefault(r['task_id'],r)
 assert set(fallback)==set(originals),'Incomplete API cohort must not be ranked as a full baseline'
 selected_rows=[selected.get(tid,fallback[tid]) for tid in originals];(run/'selected_responses.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in selected_rows));tasks=[];qual=[]
 for r in selected_rows:
  messages=render(r);meta=dict(task_id='puf/step5_preview/identity_line/'+r['task_id'],question_id=r['task_id'],actor_model='step5_preview',condition='identity_line',book_name=r['book_name'],role=r['role'],scene_index=r['scene_index'],candidate_sha256=hashlib.sha256(r['response'].encode()).hexdigest());qual.append(dict(meta,structural_valid=messages is not None))
  if messages is not None:tasks.append(dict(meta,messages=messages))
 tasks.sort(key=lambda t:hashlib.sha256(('PUF-blind|'+t['task_id']).encode()).hexdigest());out=Path(args.out);out.write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in tasks));out.with_suffix('.qualification.json').write_text(json.dumps(dict(n_candidates=64,n_qualified=len(tasks),adapter_matches_existing_local_prompts=len(frozen),details=qual),ensure_ascii=False,indent=2)+'\n');print('Plan PUF qualified',len(tasks),'/64; identical local adapter verified',len(frozen),flush=True)
if __name__=='__main__':main()
