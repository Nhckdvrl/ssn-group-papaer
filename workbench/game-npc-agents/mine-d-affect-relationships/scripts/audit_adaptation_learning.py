#!/usr/bin/env python3
"""Post-hoc supervision/response audit of D-E10; no model calls or score changes."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import statistics
from experience_store import ExperienceStore


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
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
