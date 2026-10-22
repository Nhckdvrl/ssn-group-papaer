#!/usr/bin/env python3
"""Attempt-level continuation ledger; interrupted source work is not a success."""
import argparse,json
from pathlib import Path
from collections import Counter,defaultdict

def read(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);a.add_argument('--require-complete',action='store_true');a.add_argument('--include-strong-compiler',action='store_true');args=a.parse_args();root=Path(args.asset_root);runs=[];api=[];totals=defaultdict(Counter);incomplete=[];unknown=0;experiments=['D-E06','D-E07']+(['D-E08'] if args.include_strong_compiler else [])
 for exp in experiments:
  for p in sorted((root/'runs'/exp).rglob('metadata.json')):
   m=json.loads(p.read_text());d=p.parent;rel=str(d.relative_to(root/'runs'));interruption=d/'INTERRUPTION.json';note=json.loads(interruption.read_text()) if interruption.exists() else None
   if not m['complete'] and not note:incomplete.append(rel)
   if note:assert note.get('stopped_utc') and m.get('finished_utc');unknown+=note.get('unpersisted_local_inflight_generation_upper_bound',0)
   if m.get('transport')=='step_plan':
    rows=read(d/'responses.jsonl') if (d/'responses.jsonl').exists() else [];assert len(rows)==len({(r['task_id'],r['attempt']) for r in rows});assert m['endpoint']=='https://api.stepfun.com/step_plan/v1/chat/completions'
    usage={k:sum(r.get('usage',{}).get(k,0) for r in rows) for k in ['prompt_tokens','completion_tokens','total_tokens']};assert len(rows)<=m['max_requests'] and usage['total_tokens']<=m['recorded_token_budget']
    api.append(dict(run=rel,complete=m['complete'],kind=m['kind'],model=m['model'],endpoint=m['endpoint'],recorded_attempts=len(rows),usable_tasks=len({r['task_id'] for r in rows if r.get('usable')}),usage=usage,finishes=dict(Counter(r.get('finish_reason') for r in rows)),errors=dict(Counter(r.get('error') for r in rows if r.get('error'))),wall_s=m.get('wall_s'),reasoning_effort=m.get('reasoning_effort')));continue
   if (d/'scores.jsonl').exists() and not (d/'responses.jsonl').exists():
    rows=read(d/'scores.jsonl');kind='teacher_forced_forward';usage=dict(prompt_tokens=sum(r['n_prompt_tokens'] for r in rows),target_tokens=sum(r['n_target_tokens'] for r in rows));finishes={};extra=m.get('one_forward_alignment_validation',{}).get('extra_forward_calls',0)
   else:
    rows=read(d/'responses.jsonl') if (d/'responses.jsonl').exists() else [];keys=[(r['task_id'],r.get('attempt',1)) for r in rows];assert len(keys)==len(set(keys)),rel
    usage={k:sum(r['usage'][k] for r in rows) for k in ['prompt_tokens','completion_tokens']};finishes=dict(Counter(r['finish_reason'] for r in rows));extra=0
    if 'judge' in d.name:kind='judge'
    elif m.get('kind')=='state_update':kind='state_update'
    elif d.name.startswith('source_repair_maps'):kind='source_fragment_summary_teacher'
    elif d.name.startswith('source_repair_reduce'):kind='source_unit_summary_teacher'
    elif d.name.startswith('state_compiler'):kind='character_state_summary_teacher'
    else:kind='role_reply'
   wall=m.get('wall_s');v=dict(run=rel,kind=kind,complete=m['complete'],recorded_attempts=len(rows),unique_tasks=len({r['task_id'] for r in rows}),usage=usage,finishes=finishes,extra_validation_forward_calls=extra,wall_s=wall,gpu_process_hours=wall/3600 if wall is not None else None,model=m.get('model') or m.get('args',{}).get('model'),revision=m.get('revision') or m.get('args',{}).get('revision'),script_sha256=m.get('script_sha256'),source_interruption=note);runs.append(v);t=totals[kind];t['recorded_attempts']+=len(rows);t['extra_validation_forward_calls']+=extra
   if wall is not None:t['completed_or_stopped_process_wall_s']+=wall
   for k,n in usage.items():t[k]+=n
 required=['D-E06/'+n for n in ['teacher_forced','recursive_native','recursive_summary','actor_baselines','likelihood_baselines','actor_teacher_forced','likelihood_teacher_forced','actor_recursive_native','likelihood_recursive_native','actor_recursive_summary','likelihood_recursive_summary']]+['D-E06/consumer_'+m+'/'+k for m in ['arcane_8b_dpo','qwen3_32b'] for k in ['actor','likelihood']]+['D-E07/'+n for n in ['source_repair_maps','source_repair_reduce','state_compiler_v2','qwen3_8b','arcane_8b_dpo','qwen3_32b','source_repair/qwen3_8b_summary','source_repair/arcane_8b_dpo_summary','source_repair/qwen3_32b_summary','local_qwen32_judge','local_qwen32_capacity_judge']]
 if args.include_strong_compiler:required+=['D-E08/'+n for n in ['step5_compiler','qwen3_8b','arcane_8b_dpo','local_qwen32_judge']]
 missing=sorted(set(required)-{r['run'] for r in runs+api});status='COMPLETE' if not missing and not incomplete else 'INCOMPLETE'
 if args.require_complete:assert status=='COMPLETE',dict(missing=missing,incomplete=incomplete)
 result=dict(status=status,experiments=experiments,missing_required_runs=missing,running_or_failed_without_approved_source_stop=incomplete,local_generations_recorded=sum(r['recorded_attempts'] for r in runs if r['kind']!='teacher_forced_forward'),source_turn_forward_rows=sum(r['recorded_attempts'] for r in runs if r['kind']=='teacher_forced_forward'),extra_alignment_validation_forwards=sum(r['extra_validation_forward_calls'] for r in runs),unpersisted_source_interruption_local_generation_upper_bound=unknown,completed_or_stopped_gpu_process_hours=sum(r['gpu_process_hours'] or 0 for r in runs),cost_note='Known process wall includes load/import, not per-row shared batch latency. Running process wall not imputed as zero. Up to four in-flight local compiler generations were not persisted at the source-audit interruption; raw count is a lower bound. API wall and usage are separate; first-night API totals are not included here.',by_kind={k:dict(v) for k,v in totals.items()},runs=runs,step_plan=dict(recorded_attempts=sum(r['recorded_attempts'] for r in api),usage={k:sum(r['usage'][k] for r in api) for k in ['prompt_tokens','completion_tokens','total_tokens']},runs=api))
 Path(args.out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['runs','by_kind']},indent=2))
if __name__=='__main__':main()
