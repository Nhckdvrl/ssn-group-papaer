#!/usr/bin/env python3
"""Separate actor generations, teachers, judges, forward scores, and API attempts."""
import argparse,json
from pathlib import Path
from collections import Counter,defaultdict

def read(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);local=[];api=[];totals=defaultdict(Counter)
 for meta in sorted((root/'runs').rglob('metadata.json')):
  run=meta.parent;m=json.loads(meta.read_text());relative=str(run.relative_to(root/'runs'))
  if (run/'judgments.jsonl').exists() or m.get('transport')=='step_plan':
   actor=m.get('kind')=='state_update_actor';rows=read(run/('responses.jsonl' if actor else 'judgments.jsonl'));usage={k:sum(r.get('usage',{}).get(k,0) for r in rows) for k in ['prompt_tokens','completion_tokens','total_tokens']};valid={r['task_id'] if actor else r['judge_id'] for r in rows if r.get('complete_state' if actor else 'parse_ok')};api.append(dict(run=relative,kind='state_update_actor' if actor else 'judge',model=m.get('model'),endpoint=m.get('endpoint'),n_recorded_attempts=len(rows),n_complete_state_tasks=len(valid) if actor else None,n_valid_judge_ids=len(valid) if not actor else None,errors=dict(Counter(r.get('error') for r in rows if r.get('error'))),finishes=dict(Counter(r.get('finish_reason') for r in rows)),usage=usage,complete=m.get('complete'),reasoning_effort=m.get('reasoning_effort')));continue
  assert m.get('complete'),'Not complete: '+relative
  if run.name=='target_likelihood':
   rows=read(run/'scores.jsonl');kind='teacher_forced_forward';usage=dict(prompt_tokens=sum(r['n_prompt_tokens'] for r in rows),target_tokens_scored=sum(r['n_target_tokens'] for r in rows));finishes={}
  else:
   rows=read(run/'responses.jsonl');assert len(rows)==len({r['task_id'] for r in rows})==m['n_responses'];usage={k:sum(r['usage'][k] for r in rows) for k in ['prompt_tokens','completion_tokens']};finishes=dict(Counter(r['finish_reason'] for r in rows))
   kind='judge' if 'judge' in run.name else 'chapter_summary_teacher' if run.name=='summary_teacher' else 'state_update' if relative.startswith('D-E04/') else 'role_reply'
  model=m.get('model') or m.get('args',{}).get('model');revision=m.get('revision') or m.get('args',{}).get('revision');r=dict(run=relative,kind=kind,model=model,model_revision=revision,n=len(rows),usage=usage,finishes=finishes,wall_s=m['wall_s'],gpu_process_hours=m['wall_s']/3600,started_utc=m.get('started_utc'),finished_utc=m.get('finished_utc'),script_sha256=m.get('script_sha256'));local.append(r);totals[kind]['n']+=len(rows);totals[kind]['wall_s']+=m['wall_s']
  for k,v in usage.items():totals[kind][k]+=v
  for k,v in finishes.items():totals[kind]['finish_'+str(k)]+=v
 generations=sum(r['n'] for r in local if r['kind']!='teacher_forced_forward');api_usage={k:sum(r['usage'][k] for r in api) for k in ['prompt_tokens','completion_tokens','total_tokens']}
 result=dict(local_model_generations=generations,teacher_forced_forward_evaluations=sum(r['n'] for r in local if r['kind']=='teacher_forced_forward'),sum_gpu_process_hours=sum(r['gpu_process_hours'] for r in local),cost_note='Sum of single-GPU process wall intervals including import/load; not active-kernel GPU time or sum of per-row batch latency. Forward target tokens are not generated completions. No training.',by_kind={k:dict(v) for k,v in totals.items()},local_runs=local,step_plan=dict(recorded_attempts=sum(r['n_recorded_attempts'] for r in api),recorded_usage=api_usage,unrecorded_calibration_inflight_upper_bound=2,uncertainty='Up to two medium calibration calls were in flight when stopped; their output/usage was not persisted. Recorded totals are a lower bound. No cash endpoint or redirect used.',runs=api))
 Path(args.out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['local_runs','step_plan']},indent=2));print(json.dumps(result['step_plan'],indent=2))
if __name__=='__main__':main()
