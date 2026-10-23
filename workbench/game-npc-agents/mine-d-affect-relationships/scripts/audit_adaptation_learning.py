#!/usr/bin/env python3
"""Post-hoc supervision/response audit of D-E10; no model calls or score changes."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import statistics
from experience_store import ExperienceStore
from adaptation_protocol import sections


def read(p):return list(map(json.loads,p.read_text().splitlines()))


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    root=Path(a.asset_root);data=root/'data/training_D-E10';run=root/'runs/D-E10'
    entries={r['row_id']:r for r in read(data/'entries.jsonl')}
    order=json.loads((run/'train_multitask_v2/training_order.json').read_text());tasks=defaultdict(Counter)
    store=ExperienceStore(root/'data/EvolvingWorld/experience_index.sqlite');turns=[];characters=[]
    for uid in order:
        e=entries[uid];t=tasks[e['task']];t['examples']+=1;t['forward_tokens']+=e['length'];t['target_tokens']+=e['target_length']
        if e['task']=='interaction_generation':
            replies=[x['value'] for x in store.get(uid)['conversations'] if x['from']=='assistant']
            turns.append(len(replies));characters.append((len(replies[0]),sum(map(len,replies))))
    source=store.metadata['source_sha256'];store.close()
    result=dict(experiment='D-E10',post_hoc=True,model_calls=0,source_sha256=source,
        order_sha256=hashlib.sha256((run/'train_multitask_v2/training_order.json').read_bytes()).hexdigest(),tasks=dict(tasks),
        interaction_coverage=dict(selected_segments=len(turns),available_assistant_turns=sum(turns),supervised_assistant_turns=len(turns),
            multi_turn_segments=sum(t>1 for t in turns),max_turns=max(turns),first_target_characters=sum(a for a,b in characters),
            all_target_characters=sum(b for a,b in characters)),response_lengths={})
    for name in ['base','update_sft','multitask_sft','strong32','released','full_evidence','frozen','reference']:
        if name=='reference':texts=[v for row in read(root/'data/evaluation_D-E10/references.jsonl') for v in row['responses'].values()]
        else:texts=[x['response'] for x in read(run/('system_'+name)/'outputs.jsonl')]
        sizes=[len(x.split()) for x in texts];assert len(sizes)==87
        result['response_lengths'][name]=dict(n=len(sizes),mean_words=statistics.mean(sizes),median_words=statistics.median(sizes),min_words=min(sizes),max_words=max(sizes))
    result['interpretation']='Whitespace word counts are descriptive, not quality labels. First-turn coverage and brevity do not establish the cause of MT-SFT score decline or judge bias. Original preregistered results retained.'
    episodes={x['episode_id']:x for x in read(root/'data/evaluation_D-E10/episodes.jsonl')}
    paths=[]
    for task in read(run/'system_frozen/motivation_tasks.jsonl'):
        before=sections(episodes[task['episode_id']]['update_input'][1]['content'])['Scene Interactions'][2]
        history=sections(task['messages'][1]['content'])['Previous Scene Interactions'][2]
        paths.append(dict(episode_id=task['episode_id'],has_previous_scene_history=bool(history and history!='(None)'),
                          exact_completed_experience=bool(history and history==before)))
    result['frozen_information_paths']=dict(n=len(paths),previous_scene_history_nonempty=sum(x['has_previous_scene_history'] for x in paths),
        exact_completed_experience=sum(x['exact_completed_experience'] for x in paths),rows=paths,
        interpretation='Frozen fixes the persistent card, but retains the native previous-scene channel to motivation. It is not a no-experience intervention.')
    actor_tasks={x['question_id']:x for x in read(run/'system_frozen/actor_tasks.jsonl')}
    history_rows=[]
    for e in episodes.values():
        for q in e['queries']:
            actual=actor_tasks[q['question_id']]['messages'][1:]
            history_rows.append(dict(question_id=q['question_id'],episode_id=e['episode_id'],
                exact_source_history=actual==q['messages'][1:],
                source_assistant_turns=sum(m['role']=='assistant' for m in actual)))
    assert len(history_rows)==87 and all(x['exact_source_history'] for x in history_rows)
    result['actor_source_history']=dict(n=len(history_rows),
        exact_source_history=sum(x['exact_source_history'] for x in history_rows),
        queries_with_prior_source_assistant=sum(x['source_assistant_turns']>0 for x in history_rows),
        source_assistant_turn_occurrences=sum(x['source_assistant_turns'] for x in history_rows),rows=history_rows,
        interpretation='Independent next-turn queries retain publisher-provided intervening dialogue, including the character own prior replies in some queries. Occurrences overlap across queries; they are not unique turns or on-policy trajectories.')
    common={};rubrics=set();counts={};mismatches=[]
    for system in ['base','update_sft','multitask_sft','strong32','released','full_evidence','frozen']:
        tasks=read(run/'judges'/system/'tasks.jsonl');counts[system]=len(tasks)
        for task in tasks:
            rubrics.add(hashlib.sha256(task['messages'][0]['content'].encode()).hexdigest())
            body=json.loads(task['messages'][1]['content'])
            shared={k:v for k,v in body.items() if k not in ['candidate_motivation','candidate_reply']}
            q=task['question_id']
            if q in common and common[q]!=shared:mismatches.append(dict(system=system,question_id=q))
            else:common[q]=shared
    result['judge_information_parity']=dict(tasks_by_system=counts,n_queries=len(common),rubric_sha256=sorted(rubrics),
        common_evidence_mismatches=mismatches,
        interpretation='All systems share the same supplied evidence and rubric; only candidate motivation/reply vary. This verifies input parity, not judge construct validity or blindness to inferred writing style.')
    import numpy as np
    scores=json.loads((Path(__file__).resolve().parent.parent/'results/D-E10-summary.json').read_text())['systems']
    books=sorted(scores['base']['by_book']);delta=np.array([statistics.mean(scores['released']['by_book'][b].values())-statistics.mean(scores['frozen']['by_book'][b].values()) for b in books])
    draws=np.random.default_rng(173).integers(0,len(books),(10000,len(books)))
    result['released_minus_frozen_post_hoc']=dict(mean=float(delta.mean()),ci95=np.quantile(delta[draws].mean(1),[.025,.975]).tolist(),
        changed_components=['persistent state','published versus generated motivation'],
        interpretation='A system comparison, not an isolated state or experience effect. CI crossing zero is not equivalence.')
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
