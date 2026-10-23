#!/usr/bin/env python3
"""Describe terminal native trajectories and state coverage without new inference."""
import argparse
from collections import Counter,defaultdict
import datetime
import hashlib
import json
from pathlib import Path


def load(path):
    try:return json.loads(path.read_text())
    except (FileNotFoundError,json.JSONDecodeError):return None


def prefix_until_update(path,index):
    rows=[]
    if not path.exists():return None
    with path.open() as f:
        for line in f:
            if not line.endswith('\n'):break  # A live writer has not committed this row yet.
            row=json.loads(line)
            if row['snapshot_index']!=index:continue
            if row['task']=='character_update':return rows
            rows.append(row)
    return None


def terminal_call_audit(run,system,meta):
    if not meta.get('finished_utc'):return dict(terminal=False)
    tasks=defaultdict(lambda:dict(calls=0,prompt_tokens=0,completion_tokens=0,generation_wall_s=0.0))
    ids=[];routing=[];usage=[];finish=Counter()
    for line in (run/'raw.jsonl').open():
        row=json.loads(line);ids.append(row['call_index']);finish[row['finish_reason']]+=1
        expected=row['owner']=='character' and (system=='multitask_sft' or system=='update_sft' and row['task']=='character_update')
        if row['adapter_active']!=expected:routing.append(row['call_index'])
        if len(row['prompt_token_ids'])!=row['usage']['prompt_tokens']:usage.append(row['call_index'])
        if row['completion_token_ids'] is not None and len(row['completion_token_ids'])!=row['usage']['completion_tokens']:usage.append(row['call_index'])
        t=tasks[row['task']];t['calls']+=1;t['prompt_tokens']+=row['usage']['prompt_tokens']
        t['completion_tokens']+=row['usage']['completion_tokens'] or 0;t['generation_wall_s']+=row['wall_s']
    requests=[json.loads(x)['call_index'] for x in (run/'requests.jsonl').read_text().splitlines()]
    return dict(terminal=True,tasks=dict(tasks),raw_records=len(ids),request_records=len(requests),finish_reasons=dict(finish),
        recorded_attempts=meta['recorded_generation_attempts'],process_wall_s=meta['wall_s'],
        duplicate_raw_ids=len(ids)-len(set(ids)),requests_without_response=sorted(set(requests)-set(ids)),
        responses_without_request=sorted(set(ids)-set(requests)),routing_mismatches=routing,usage_mismatches=usage,
        interpretation='Wall times describe this implementation and generated workload, including parser retries. They are not equal-content model latency comparisons. Initial interrupted attempt is accounted separately.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    root=Path(a.asset_root);runs=root/'runs/D-E11';frozen=root/'data/native_D-E11/snapshots.json'
    inputs={x['source_index']:x['input'] for x in json.loads(frozen.read_text())}
    result=dict(experiment='D-E11',post_hoc=True,model_calls=0,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        input_sha256=hashlib.sha256(frozen.read_bytes()).hexdigest(),systems={},pre_update_controls=[],
        interpretation='Operational/state-coverage description. Update flags and exact repeated strings are not growth/failure scores. Terminal snapshots include errors; incomplete cohorts are not survivor-only quality estimates.')
    for system in ['base','update_sft','multitask_sft']:
        run=runs/system;meta=load(run/'metadata.json')
        if meta is None:continue
        summaries=[]
        for item in meta.get('processed_snapshots',[]):
            index=item['source_index'];p=run/('snapshot_'+str(index))/'result.json';data=load(p)
            if data is None:raise ValueError('Terminal snapshot without readable result: '+str(p))
            known=set(inputs[index]['character_states']);scenes=[];seen=Counter()
            for scene in data['scenes']:
                interactions=scene['interactions'];reflections=scene['character_reflections']
                repeats=0
                for x in interactions:
                    key=(tuple(x['characters']),x['content']);repeats+=int(seen[key]>0);seen[key]+=1
                scenes.append(dict(scene=scene['scene_index'],n_interactions=len(interactions),cast=scene['involved_characters'],
                    cast_without_persisted_state=[n for n in scene['involved_characters'] if n not in known and n!='Environment'],
                    n_reflections=len(reflections),profile_updated=sum(bool(x['profile_updated']) for x in reflections),
                    exact_repeated_interactions=repeats,scene_error=bool(scene.get('error'))))
            summaries.append(dict(snapshot_index=index,book=inputs[index]['book_name'],stop_reason=data['stop_reason'],
                error_type=(data.get('error') or '').split(':',1)[0],result_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scenes=scenes))
        result['systems'][system]=dict(cohort_processed=meta.get('complete'),terminal_snapshots=summaries,
                                      not_terminal_snapshot_indices=sorted(set(inputs)-{x['snapshot_index'] for x in summaries}),
                                      calls=terminal_call_audit(run,system,meta))
    shared={x['snapshot_index'] for x in result['systems'].get('base',{}).get('terminal_snapshots',[])} & {x['snapshot_index'] for x in result['systems'].get('update_sft',{}).get('terminal_snapshots',[])}
    for index in sorted(shared):
        base=prefix_until_update(runs/'base/raw.jsonl',index);updated=prefix_until_update(runs/'update_sft/raw.jsonl',index)
        if base is None or updated is None:continue
        result['pre_update_controls'].append(dict(snapshot_index=index,base_calls=len(base),updated_calls=len(updated),
            messages_equal=len(base)==len(updated) and all(a['messages']==b['messages'] for a,b in zip(base,updated)),
            responses_equal=len(base)==len(updated) and all(a['response']==b['response'] for a,b in zip(base,updated)),
            token_ids_equal=len(base)==len(updated) and all(a['completion_token_ids']==b['completion_token_ids'] for a,b in zip(base,updated))))
    judges=runs/'judges';interruption=load(judges/'SOURCE_INPUT_INTERRUPTION.json')
    if interruption:
        tasks=[json.loads(x) for x in (judges/'all_tasks.jsonl').read_text().splitlines()]
        example=next(x for x in tasks if x['task_id']=='base/6/scene0/PF')
        before=inputs[6]['character_states']['Alice']['hidden_tracker']
        after=next(x['hidden_tracker'] for x in load(runs/'base/snapshot_6/result.json')['scenes'][0]['character_reflections'] if x['character']=='Alice')
        section=example['messages'][1]['content'].split('## Character Hidden Trackers (at scene start)',1)[1].split('\n## ',1)[0]
        assert before!=after and after in section and before not in section
        result['scoring_source_time_audit']=dict(interruption=interruption,
            affected_metrics=['PF','SSF','MDB'],affected_registered_tasks=sum(x['metric'] in ['PF','SSF','MDB'] for x in tasks),
            example_task_id=example['task_id'],example_prompt_sha256=hashlib.sha256(example['messages'][1]['content'].encode()).hexdigest(),
            actual_before_tracker_sha256=hashlib.sha256(before.encode()).hexdigest(),
            actual_after_tracker_sha256=hashlib.sha256(after.encode()).hexdigest(),
            labeled_start_section_contains_actual_end_tracker=True,labeled_start_section_contains_actual_start_tracker=False,
            corrected_input_reruns=False,
            interpretation='Input time mismatch in the fixed native implementation, confirmed on saved input. Entire affected metric classes are invalidated without selecting by score; no claim about the effect size or all published results.')
        qualified=judges/'qualified_tasks.jsonl'
        if qualified.exists():
            newer=[json.loads(x) for x in qualified.read_text().splitlines()]
            assert [(x['task_id'],x['messages']) for x in tasks]==[(x['task_id'],x['messages']) for x in newer]
            result['scoring_source_time_audit']['registered_messages_unchanged']=True
            result['scoring_source_time_audit']['source_qualified_tasks']=sum(not x.get('unscored_reason') for x in newer)
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(systems=list(result['systems']),pre_update_controls=result['pre_update_controls']),indent=2))


if __name__=='__main__':main()
