#!/usr/bin/env python3
"""Connect frozen native next-role turns to each actual state pathway."""
import argparse,json,copy,hashlib
from pathlib import Path

def render_query(q,role,state):
 messages=copy.deepcopy(q['native_messages']);current=copy.deepcopy(q['native_state']);current['profile']=state['profile'];current['hidden_tracker']=state['hidden_tracker'];s=messages[0]['content'];a=q['state_json_start'];b=q['state_json_end'];assert json.loads(s[a:b])=={role:q['native_state']};messages[0]['content']=s[:a]+json.dumps({role:current},ensure_ascii=False,indent=2)+s[b:];assert messages[1:]==q['native_messages'][1:]
 check=json.loads(messages[0]['content'][a:].split('\n\n## Other Characters',1)[0]);assert check[role]['motivation']==q['native_state']['motivation'];return messages

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--conditions',nargs='+',required=True,choices=['released','frozen','teacher_forced','recursive_native','recursive_summary']);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);trajectories=[json.loads(l) for l in (root/'data/closed_D-E06/trajectories.jsonl').read_text().splitlines()];tasks=[];sources={}
 for condition in args.conditions:
  state_index={}
  if condition not in ['released','frozen']:
   run=root/'runs/D-E06'/condition;assert json.loads((run/'metadata.json').read_text())['complete'];state_index={(r['trajectory_id'],r['step']):r for r in map(json.loads,(run/'states.jsonl').read_text().splitlines())}
  for t in trajectories:
   for q in t['queries']:
    if condition=='released':state={k:q['native_state'][k] for k in ['profile','hidden_tracker']};valid=True
    elif condition=='frozen':state=t['initial_state'];valid=True
    else:r=state_index[t['trajectory_id'],q['after_updates']];state=r['state'];valid=r['complete_state']
    messages=render_query(q,t['role'],state);task=dict(task_id=q['question_id']+'/'+condition,question_id=q['question_id'],trajectory_id=t['trajectory_id'],book_name=t['book_name'],role=t['role'],after_updates=q['after_updates'],scene_index=q['scene_index'],condition=condition,updater_complete_state=valid,messages=messages,state_sha256=hashlib.sha256(json.dumps(state,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),preselected_review=t['preselected_review']);tasks.append(task)
    sources[task['task_id']]=dict(state_sha256=task['state_sha256'],actor_input_sha256=hashlib.sha256(json.dumps(messages,ensure_ascii=False,sort_keys=True).encode()).hexdigest())
 tasks.sort(key=lambda r:hashlib.sha256(('D-E06-actor-order|'+r['task_id']).encode()).hexdigest());out=Path(args.out);assert not out.exists();out.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in tasks));out.with_suffix('.provenance.json').write_text(json.dumps(dict(n_tasks=len(tasks),conditions=args.conditions,only_target_profile_tracker_changed=True,other_world_characters_motivation_live_cue_unchanged=True,details=sources),ensure_ascii=False,indent=2)+'\n');print('Frozen actor tasks',len(tasks),args.conditions,flush=True)
if __name__=='__main__':main()
