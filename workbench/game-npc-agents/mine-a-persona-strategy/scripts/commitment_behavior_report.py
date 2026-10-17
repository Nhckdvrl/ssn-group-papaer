#!/usr/bin/env python3
"""E50 complete-run graph clustered statistics, all seeds and failed cases retained."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import numpy as np


def estimate(values):
    x=np.asarray(values,dtype=float)
    if not len(x):return None
    rng=np.random.default_rng(5050)
    means=x[rng.integers(0,len(x),(4000,len(x)))].mean(1)
    return {'mean':float(x.mean()),'graph_bootstrap_95':np.quantile(means,[.025,.975]).tolist(),
            'independent_graphs':len(x)}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((a.directory/'manifest.json').read_text())
    runtime=json.loads((a.directory/'runtime.json').read_text())
    data=[json.loads(s) for s in (a.directory/'branches.jsonl').read_text().splitlines()]
    cases={r['case_id']:r for r in map(json.loads,Path(manifest['arguments']['dataset']).read_text().splitlines())}
    grouped=defaultdict(list)
    for r in data:grouped[(r['conv_persona'],r['down_persona'],r['channel'],r['control'])].append(r)
    report={'manifest':manifest,'runtime':runtime,'cells':{},'contrasts':{},
            'graphs':len({r['case_id'] for r in data}),
            'protocol_errors':sum(bool(r['protocol_error']) for r in data),
            'illegal_action_count':sum(not t['legal'] for r in data for t in r['history']),
            'scope':'six-action-or-first-allocation decision slices, not long-term game utility'}
    for key,rows in grouped.items():
        label='/'.join(key)
        by_graph=defaultdict(list)
        for r in rows:by_graph[r['case_id']].append(r)
        metrics={name:estimate([np.mean([float(r['flags'][name]) for r in rs]) for rs in by_graph.values()])
                 for name in ['own_task','request']}
        metrics['steps']=estimate([np.mean([r['steps'] for r in rs]) for rs in by_graph.values()])
        metrics['neither']=estimate([np.mean([not(r['flags']['own_task'] or r['flags']['request']) for r in rs]) for rs in by_graph.values()])
        report['cells'][label]={'branches':len(rows),'metrics':metrics,
                              'stances':dict(Counter(r['conversation']['stance'] for r in rows))}
    lookup={(r['case_id'],r['seed'],r['conv_persona'],r['down_persona'],r['channel'],r['control']):r for r in data}
    def contrast(label,left,right,metric):
        points=defaultdict(list)
        for graph,seed in sorted({(r['case_id'],r['seed']) for r in data}):
            k1=(graph,seed,*left);k0=(graph,seed,*right)
            if k1 in lookup and k0 in lookup:
                points[graph].append(metric(lookup[k1])-metric(lookup[k0]))
        report['contrasts'][label]=estimate([np.mean(v) for v in points.values()])
    req=lambda r:float(r['flags']['request'])
    accept=lambda r:float(r['conversation']['stance']=='accept')
    def plan_req(r):
        case=cases[r['case_id']]
        actions=r['update']['priority_actions']
        relevant=[c for c in actions if c in [case['goal_command'],case['request_command']]]
        return float(bool(relevant) and relevant[0]==case['request_command'])
    for channel in ['00','10','01','11']:
        contrast('coherent_persona_request_'+channel,
                 ('agreeable','agreeable',channel,'none'),('firm','firm',channel,'none'),req)
    contrast('coherent_persona_accept',('agreeable','agreeable','11','none'),('firm','firm','11','none'),accept)
    contrast('coherent_persona_plan_request',('agreeable','agreeable','11','none'),('firm','firm','11','none'),plan_req)
    for c in ['firm','agreeable']:
        for down in ['firm','agreeable']:
            contrast(f'total_entry_{c}_{down}',(c,down,'11','none'),(c,down,'00','none'),req)
            # Interaction per graph/seed retains all four actual outcomes.
            points=defaultdict(list)
            for graph,seed in sorted({(r['case_id'],r['seed']) for r in data}):
                ks=[(graph,seed,c,down,ch,'none') for ch in ['00','10','01','11']]
                if all(k in lookup for k in ks):
                    y=[req(lookup[k]) for k in ks];points[graph].append(y[3]-y[1]-y[2]+y[0])
            report['contrasts'][f'channel_interaction_{c}_{down}']=estimate([np.mean(x) for x in points.values()])
    for p in ['firm','agreeable']:
        contrast('conversation_persona_effect_down_'+p,
                 ('agreeable',p,'11','none'),('firm',p,'11','none'),req)
        contrast('downstream_persona_effect_conv_'+p,
                 (p,'agreeable','11','none'),(p,'firm','11','none'),req)
    calls=[json.loads(x) for x in (a.directory/'model_calls.jsonl').read_text().splitlines()]
    report['calls']={'count':len(calls),'parse_errors':sum(bool(r['parse_error']) for r in calls),
                     'prompt_tokens':sum(r['prompt_tokens'] for r in calls),
                     'completion_tokens':sum(r['completion_tokens'] for r in calls)}
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'graphs':report['graphs'],'runtime':runtime,'calls':report['calls'],
                     'contrasts':report['contrasts']},ensure_ascii=False))


if __name__=='__main__':main()
