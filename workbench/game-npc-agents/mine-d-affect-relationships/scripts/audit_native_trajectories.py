#!/usr/bin/env python3
"""Describe terminal native trajectories and state coverage without new inference."""
import argparse
from collections import Counter
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
                                      not_terminal_snapshot_indices=sorted(set(inputs)-{x['snapshot_index'] for x in summaries}))
    shared={x['snapshot_index'] for x in result['systems'].get('base',{}).get('terminal_snapshots',[])} & {x['snapshot_index'] for x in result['systems'].get('update_sft',{}).get('terminal_snapshots',[])}
    for index in sorted(shared):
        base=prefix_until_update(runs/'base/raw.jsonl',index);updated=prefix_until_update(runs/'update_sft/raw.jsonl',index)
        if base is None or updated is None:continue
        result['pre_update_controls'].append(dict(snapshot_index=index,base_calls=len(base),updated_calls=len(updated),
            messages_equal=len(base)==len(updated) and all(a['messages']==b['messages'] for a,b in zip(base,updated)),
            responses_equal=len(base)==len(updated) and all(a['response']==b['response'] for a,b in zip(base,updated)),
            token_ids_equal=len(base)==len(updated) and all(a['completion_token_ids']==b['completion_token_ids'] for a,b in zip(base,updated))))
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(systems=list(result['systems']),pre_update_controls=result['pre_update_controls']),indent=2))


if __name__=='__main__':main()
