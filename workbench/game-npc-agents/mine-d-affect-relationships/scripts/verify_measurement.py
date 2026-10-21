#!/usr/bin/env python3
"""Verify frozen controls, API inputs and score provenance without model calls."""
import argparse,json,hashlib,subprocess
from pathlib import Path
from collections import defaultdict,Counter

def rows(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root)
 original={x['task_id']:x for x in rows(root/'data/update_D-E04/tasks.jsonl')};control={x['task_id']:x for x in rows(root/'data/update_D-E04/identity_line_tasks.jsonl')};assert set(original)==set(control) and len(original)==64
 for tid,t in original.items():
  c=control[tid];assert c['messages'][1:]==t['messages'][1:]
  line=f"Keep every update about the specified target character ({t['role']}); distinguish that character's own actions, experiences, relations, and knowledge from those of every other person in the scene."
  assert c['messages'][0]['content']==t['messages'][0]['content']+'\n\n'+line
 candidates={}
 for condition,tasks in [('original',original),('identity_line',control)]:
  for model in ['qwen3_8b','qwen3_32b']:
   run=root/'runs/D-E04';run=run/'identity_line' if condition=='identity_line' else run
   rr=rows(run/model/'responses.jsonl');assert len(rr)==len({r['task_id'] for r in rr})==64
   for r in rr:
    assert r['messages']==tasks[r['task_id']]['messages'];candidates[model,condition,r['task_id']]=digest(r['response'])
 plan=root/'runs/D-E05/step5';attempts=rows(plan/'responses.jsonl');selected=rows(plan/'selected_responses.jsonl');assert len(selected)==len({r['task_id'] for r in selected})==64
 first_complete={}
 for r in attempts:
  assert r['request']['messages']==control[r['task_id']]['messages'];assert r['endpoint']=='https://api.stepfun.com/step_plan/v1/chat/completions'
  if r.get('complete_state'):first_complete.setdefault(r['task_id'],r)
 for r in selected:
  assert r==first_complete[r['task_id']];candidates['step5_preview','identity_line',r['task_id']]=digest(r['response'])
 puf=rows(root/'data/update_D-E04/puf_tasks.jsonl')+rows(root/'data/update_D-E04/plan_puf_tasks.jsonl');assert len(puf)==315
 tasks={r['task_id']:r for r in puf};graded=[]
 for exp in ['D-E04','D-E05']:
  for name in ['puf_judge','puf_judge_recovery']:
   path=root/'runs'/exp/name/'responses.jsonl'
   if not path.exists():continue
   assert json.loads((path.parent/'metadata.json').read_text())['complete']
   for r in rows(path):
    t=tasks[r['task_id']];assert r['messages']==t['messages'];assert r['candidate_sha256']==candidates[r['actor_model'],r['condition'],r['question_id']];graded.append(r)
 assert set(r['task_id'] for r in graded)==set(tasks)
 nll=rows(root/'runs/D-E02/target_likelihood/scores.jsonl');targets=defaultdict(list)
 for r in nll:targets[r['question_id']].append(r)
 assert len(targets)==64
 for group in targets.values():assert len(group)==4 and len({(r['target_sha256'],r['n_target_tokens']) for r in group})==1
 snapshot=plan/'runner_source.py';expected=json.loads((plan/'metadata.json').read_text())['script_sha256'];assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==expected
 committed=subprocess.check_output(['git','show','f7f3adef:workbench/game-npc-agents/mine-d-affect-relationships/scripts/run_plan_state.py']);assert committed==snapshot.read_bytes()
 local_token_rows=0
 for path in (root/'runs').rglob('responses.jsonl'):
  for r in rows(path):
   if isinstance(r.get('generated_token_ids'),list):
    assert len(r['generated_token_ids'])==r['usage']['completion_tokens']
    assert r['raw'].strip() or r['finish_reason']=='length'
    local_token_rows+=1
 result=dict(local_token_ids_verified=local_token_rows,state_tasks=64,only_control_change='One predeclared generic identity line; all original user facts unchanged',local_update_messages_verified=256,step_actor_attempt_messages_verified=len(attempts),step_selected_first_complete=64,plan_endpoint_verified=True,step_runner_matches_prerun_commit='f7f3adef',step_runner_sha256=expected,puf_candidates=315,puf_judge_attempts_provenance_verified=len(graded),nll_same_target_four_conditions=64,no_model_calls=True)
 Path(args.out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
