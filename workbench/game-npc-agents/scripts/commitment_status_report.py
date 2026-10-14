#!/usr/bin/env python3
"""E51 all-case, all-seed graph-paired status/goal/state estimates."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((a.directory/'manifest.json').read_text())
    runtime=json.loads((a.directory/'runtime.json').read_text())
    rows=list(map(json.loads,(a.directory/'branches.jsonl').read_text().splitlines()))
    lookup={(r['case_id'],r['seed'],r['persona'],r['condition']):r for r in rows}
    expected=len(manifest['case_ids'])*len(manifest['arguments']['seeds'])*2*len(manifest['conditions'])
    assert len(lookup)==len(rows)==expected,(len(rows),expected)
    report={'manifest':manifest,'runtime':runtime,'cells':{},'contrasts':{},
            'protocol_errors':sum(bool(r['protocol_error']) for r in rows),
            'illegal_actions':sum(not h['legal'] for r in rows for h in r['history'])}
    for p in ['firm','agreeable']:
        for c in manifest['conditions']:
            group=[r for r in rows if r['persona']==p and r['condition']==c]
            by_graph=defaultdict(list)
            for r in group:by_graph[r['case_id']].append(r)
            report['cells'][p+'/'+c]={'branches':len(group),'request_count':sum(r['flags']['request'] for r in group),
                'own_count':sum(r['flags']['own_task'] for r in group),
                'request':estimate([np.mean([r['flags']['request'] for r in v]) for v in by_graph.values()]),
                'own_task':estimate([np.mean([r['flags']['own_task'] for r in v]) for v in by_graph.values()]),
                'steps':estimate([np.mean([r['steps'] for r in v]) for v in by_graph.values()])}
        def contrast(label,terms):
            values=defaultdict(list)
            for case in manifest['case_ids']:
                for seed in manifest['arguments']['seeds']:
                    values[case].append(sum(w*float(lookup[(case,seed,p,c)]['flags']['request']) for c,w in terms))
            report['contrasts'][p+'/'+label]=estimate([np.mean(v) for v in values.values()])
        contrast('status_without_goal',[('completed',1),('pending',-1)])
        contrast('status_with_goal',[('completed_goal',1),('pending_goal',-1)])
        contrast('status_with_goal_state',[('completed_goal_state',1),('pending_goal_state',-1)])
        contrast('status_goal_interaction',[('completed_goal',1),('pending_goal',-1),('completed',-1),('pending',1)])
        contrast('status_state_interaction',[('completed_goal_state',1),('pending_goal_state',-1),('completed_goal',-1),('pending_goal',1)])
    calls=list(map(json.loads,(a.directory/'model_calls.jsonl').read_text().splitlines()))
    report['calls']={'count':len(calls),'parse_errors':sum(bool(r['parse_error']) for r in calls),
                    'prompt_tokens':sum(r['prompt_tokens'] for r in calls),'completion_tokens':sum(r['completion_tokens'] for r in calls)}
    report['scope']='fixed accepted immediate request; state and goal reminder causal contrast, not naturally accepted total persona effect'
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'runtime':runtime,'contrasts':report['contrasts'],'protocol_errors':report['protocol_errors']},ensure_ascii=False))

if __name__=='__main__':main()
