#!/usr/bin/env python3
"""Describe terminal native trajectories and state coverage without new inference."""
import argparse
from collections import Counter,defaultdict
import datetime
import hashlib
import json
from pathlib import Path
import statistics


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


def audit_completed_scoring(root):
    judges=root/'runs/D-E11/judges'
    if not load(judges/'status.json').get('complete'):return dict(complete=False)
    read=lambda p:[json.loads(x) for x in p.read_text().splitlines()]
    tasks={x['task_id']:x for x in read(judges/'qualified_tasks.jsonl')}
    stages={name:{x['task_id']:x for x in read(judges/name/'responses.jsonl')} for name in ['first','first_remaining','recovery']}
    assert not (set(stages['first']) & set(stages['first_remaining']))
    initial=stages['first']|stages['first_remaining'];selected=read(judges/'selected.jsonl')
    assert {x['task_id'] for x in selected}==set(tasks)
    for stage in stages.values():
        for uid,row in stage.items():assert row['messages']==tasks[uid]['messages']
    for row in selected:
        uid=row['task_id'];raw=stages['recovery'].get(uid,initial.get(uid))
        if tasks[uid].get('unscored_reason'):assert not row['valid'] and row['result'] is None
        if row['valid']:
            text=raw['response'].strip()
            if text.startswith('```'):text=text.split('\n',1)[-1].rsplit('```',1)[0].strip()
            body,_=json.JSONDecoder().raw_decode(text)
            score=max(0,min(100,50+sum(abs(x['points']) for x in body['merits'])-sum(abs(x['points']) for x in body['demerits'])))
            assert score==row['result']['score']
    result_file=Path(__file__).resolve().parent.parent/'results/D-E11-summary.json';reported=load(result_file)
    groups={}
    for system,group in reported['systems'].items():
        rows=[x for x in selected if x['system']==system];eligible=[x for x in rows if not tasks[x['task_id']].get('unscored_reason')]
        for book,metrics in group['by_book'].items():
            for metric,value in metrics.items():
                block=[x for x in rows if x['book_name']==book and x['metric']==metric and not x['repeat']]
                expected=statistics.mean(x['result']['score'] for x in block) if block and all(x['valid'] for x in block) else None
                assert value==expected,(system,book,metric)
        realized=group['execution']['processed_snapshots'];all_ok=len(realized)==6 and all(x['stop_reason']!='error' for x in realized)
        for metric,value in group['macro_metrics'].items():
            vals=[m[metric] for m in group['by_book'].values()]
            expected=statistics.mean(vals) if all_ok and all(v is not None for v in vals) else None
            assert value==expected
        prim={x['task_id']:x for x in rows if not x['repeat']};diffs=[]
        for x in rows:
            if x['repeat'] and x['valid']:
                first=prim.get(x['task_id'].removesuffix('__repeat'))
                if first and first['valid']:diffs.append(abs(x['result']['score']-first['result']['score']))
        assert len(diffs)==group['n_repeat_pairs']
        assert (statistics.mean(diffs) if diffs else None)==group['repeat_mean_absolute_difference']
        groups[system]=dict(registered=len(rows),source_qualified=len(eligible),valid=sum(x['valid'] for x in eligible),
            by_metric={m:dict(valid=sum(x['valid'] for x in eligible if x['metric']==m),planned=sum(x['metric']==m for x in eligible)) for m in ['PUF','MQ','CR','PES']})
    raw=[x for stage in stages.values() for x in stage.values()]
    return dict(complete=True,model_calls=0,execution_agent_recomputation_not_independent_review=True,
        original_task_messages_verified=True,valid_scores_and_all_aggregates_recomputed=True,groups=groups,
        saved_response_records=len(raw),prompt_tokens=sum(x['usage']['prompt_tokens'] for x in raw),
        completion_tokens=sum(x['usage']['completion_tokens'] for x in raw),
        source_invalid_returned=sum(bool(tasks[x['task_id']].get('unscored_reason')) for x in raw),
        unrecorded_inflight_attempts=load(judges/'SOURCE_INPUT_INTERRUPTION.json').get('possible_inflight_task_ids'),
        selected_sha256=hashlib.sha256((judges/'selected.jsonl').read_bytes()).hexdigest(),
        summary_sha256=hashlib.sha256(result_file.read_bytes()).hexdigest(),
        interpretation='Known returned calls include invalid-source and recovery attempts; incomplete in-flight token usage is unknown. Format validity and native rubric values are not growth accuracy.')


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
        result['completed_scoring_audit']=audit_completed_scoring(root)
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(systems=list(result['systems']),pre_update_controls=result['pre_update_controls']),indent=2))


if __name__=='__main__':main()
