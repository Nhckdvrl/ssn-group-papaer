#!/usr/bin/env python3
"""E67/E68 explanatory native plan replay and paired outcome paths, all episodes."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
from native_dependency_plan_analysis import analyze
from native_rule_cross_report import summarize, key, G, A
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--dataset',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--raw-out',type=Path,required=True)
    a=ap.parse_args();sources={r['case']['case_id']:r for r in map(json.loads,a.dataset.read_text().splitlines())}
    rows=[]
    for d in a.runs:
        assert (d/'runtime.json').exists()
        rows.extend(map(json.loads,(d/'episodes.jsonl').read_text().splitlines()))
    modules=load_event_modules(CACHE/'sources/LIGHT');cache={};groups=defaultdict(lambda:defaultdict(list))
    a.raw_out.mkdir(exist_ok=False)
    with (a.raw_out/'plan_replay.jsonl').open('w') as f:
        for r in rows:
            upstream=(r['case_id'],r['seed'],r['persona'],r['mode'],r['upstream_rule'])
            if upstream not in cache:
                v,actions=analyze(r,sources[r['case_id']],modules)
                cache[upstream]=(v,actions)
                f.write(json.dumps({'upstream_key':upstream,'plan':r['update'],'replay':actions,'values':{
                    k:v[k] for k in ['planned_original_goal','replay_goal_executed','initial_plan_has_illegal_action','sequential_plan_has_illegal_action']}})+'\n')
            v,_=cache[upstream]
            fields={'plan_lists_goal':v['planned_original_goal'],'plan_replays_goal':v['replay_goal_executed'],
                    'feasible_plan_unexecuted':float(v['replay_goal_executed'] and not r['goal_executed']),
                    'plan_without_goal_actual_goal':float(not v['replay_goal_executed'] and r['goal_executed'])}
            group=(r['persona'],r['mode'],r['upstream_rule'],r['exec_rule'],r['feedback'])
            groups[group][r['case_id']].append(fields)
    cells={}
    for group,points in groups.items():
        fields=list(next(iter(points.values()))[0])
        cells['/'.join(group)]=summarize([[np.mean([v[f] for v in vs]) for f in fields] for vs in points.values()],fields)
    lookup={key(r):r for r in rows};transition_counts=defaultdict(Counter);examples=defaultdict(list)
    for k,r in sorted(lookup.items()):
        cid,seed,p,mode,up,ex,fb=k
        pairs=[]
        if mode=='goal_item' and ex==A:
            other=lookup.get((cid,seed,p,mode,up,G,fb))
            if other:pairs.append((f'execution/{p}/{up}/{fb}',other))
        if fb=='legacy':
            other=lookup[(cid,seed,p,mode,up,ex,'block_status')]
            pairs.append((f'feedback/{p}/{up}/{ex}',other))
        for label,other in pairs:
            upstream=cid,seed,p,mode,up
            plan_ok=bool(cache[upstream][0]['replay_goal_executed'])
            state=f'goal_{int(r["goal_executed"])}_to_{int(other["goal_executed"])}_plan_{int(plan_ok)}'
            transition_counts[label][state]+=1
            # Deterministic illustrative examples for every direction, not inferential sample selection.
            if len(examples[label+'/'+state])<2:
                source=sources[cid]['case']
                examples[label+'/'+state].append({'case_id':cid,'seed':seed,'goal_kind':r['goal_kind'],
                    'goal_command':source['goal_command'],'quest':{x:v for x,v in source['quest'].items() if x!='graph'},
                    'request':sources[cid]['requests'][mode],'plan':r['update'],
                    'before':[{'command':h['command'],'legal':h['legal'],'goal':h['goal_executed_after'],'error':h.get('error')} for h in r['history']],
                    'after':[{'command':h['command'],'legal':h['legal'],'goal':h['goal_executed_after'],'error':h.get('error')} for h in other['history']]})
    illustrated=a.raw_out/'illustrations.json'
    illustrated.write_text(json.dumps(dict(examples),ensure_ascii=False,indent=2)+'\n')
    result={'analysis':'EXPLANATORY: source-goal command replay, not a correctness label on intentions',
            'episodes':len(rows),'unique_upstream_plans':len(cache),'cells':cells,
            'paired_transitions':{k:dict(v) for k,v in transition_counts.items()},
            'illustrations_asset':str(illustrated),
            'illustrations_sha256':hashlib.sha256(illustrated.read_bytes()).hexdigest(),
            'model_calls':0,'gpu_hours':0}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['episodes','unique_upstream_plans','model_calls']}))


if __name__=='__main__':main()
