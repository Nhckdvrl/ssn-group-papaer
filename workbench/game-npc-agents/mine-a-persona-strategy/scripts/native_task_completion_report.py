#!/usr/bin/env python3
"""E69 adaptive control paired to the unchanged complete eight-step baseline."""
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
from native_matched_task_report import metrics
from native_rule_cross_report import summarize


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--base-runs',type=Path,nargs='+',required=True)
    ap.add_argument('--data',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();assert (a.run/'runtime.json').exists()
    sources={r['case']['case_id']:r for r in map(json.loads,(a.data/'continuation_tasks.jsonl').read_text().splitlines())}
    rows=list(map(json.loads,(a.run/'episodes.jsonl').read_text().splitlines()));baseline={}
    for d in a.base_runs:
        assert (d/'runtime.json').exists()
        for r in map(json.loads,(d/'episodes.jsonl').read_text().splitlines()):
            if r['panel']=='continuation':baseline[r['case_id'],r['seed'],r['persona'],r['rule']]=r
    lookup={(r['case_id'],r['seed'],r['persona'],r['rule'],r['control']):r for r in rows}
    controls=['completion_notice','mechanics_fact'];seeds=[6801,6802,6803]
    expected={(cid,s,p,r,c) for cid in sources for s in seeds for p in ['firm','agreeable']
              for r in ['generic_priority','negative_only'] for c in controls}
    assert len(rows)==len(lookup)==72 and set(lookup)==expected and len(baseline)==36
    fields=['goal','request','both','goal_then_request','final_goal_holds','native_rejections']
    cells={};differences={};counts={};changed=[]
    for p in ['firm','agreeable']:
        for rule in ['generic_priority','negative_only']:
            for control in controls:
                key=p+'/'+rule+'/'+control;matrix=[];delta=[];raw=[]
                for cid in sorted(sources):
                    vs=[];ds=[]
                    for s in seeds:
                        r=lookup[cid,s,p,rule,control];base=baseline[cid,s,p,rule]
                        v=metrics(r,sources[cid]);b=metrics(base,sources[cid])
                        vs.append([v[f] for f in fields]);ds.append([v[f]-b[f] for f in fields]);raw.append(v)
                        if r['request_given']!=base['request_given'] or r['both_completed']!=base['both_completed']:
                            changed.append({'case_id':cid,'seed':s,'persona':p,'rule':rule,'control':control,
                                'baseline_request':base['request_given'],'control_request':r['request_given'],
                                'baseline_both':base['both_completed'],'control_both':r['both_completed'],
                                'baseline_commands':[h['command'] for h in base['history']],
                                'control_commands':[h['command'] for h in r['history']]})
                    matrix.append(np.mean(vs,axis=0));delta.append(np.mean(ds,axis=0))
                cells[key]=summarize(matrix,fields);differences[key]=summarize(delta,fields)
                counts[key]={'trajectories':len(raw),**{f:sum(v[f] for v in raw) for f in ['goal','request','both']}}
    calls=[json.loads(line) for line in (a.run/'model_calls.jsonl').open()]
    runtime=json.loads((a.run/'runtime.json').read_text());assert len(calls)==runtime['calls']
    # Descriptive follow-up after the Gemma outcome; not a preregistered mechanism test.
    action_diagnostics={}
    for control in controls:
        counter=Counter()
        for r in rows:
            if r['control']!=control:continue
            base=baseline[r['case_id'],r['seed'],r['persona'],r['rule']]
            valid=[h for h in r['history'] if h['legal'] and h.get('executed') and not h.get('stochastic_failure')]
            item=r['goal_item_id']
            counter['episodes']+=1
            counter['action_sequence_changed']+=int([h['command'] for h in r['history']]!=[h['command'] for h in base['history']])
            counter['target_remove_episodes']+=int(any(h['event_type']=='RemoveObjectEvent' and h['before'][item]['equipped'] in ['wear','wield'] and h['after'][item]['equipped'] is None for h in valid))
            counter['target_drop_episodes']+=int(any(h['command'].startswith('drop ') and h['before'][item]['container']==h['actor'] and h['after'][item]['container']!=h['actor'] for h in valid))
        action_diagnostics[control]=dict(counter)
    traces=[{k:r[k] for k in ['case_id','seed','persona','rule','control','goal_command','request_given','both_completed']} |
            {'history':[{'command':h['command'],'legal':h['legal'],'event_type':h['event_type']} for h in r['history']]}
            for r in rows if r['case_id']=='063911927a783158' and r['seed']==6801 and r['persona']=='firm' and r['rule']=='negative_only']
    result={'status':'COMPLETE' ,'design':'ADAPTIVE / POST-HOC control following the prespecified Panel A result.',
            'worlds':3,'episodes':len(rows),'counts':counts,'cells':cells,'paired_differences':differences,
            'all_changed_outcomes':changed,'descriptive_posthoc_action_diagnostics':action_diagnostics,
            'descriptive_posthoc_woman_traces':traces,'actual_calls':len(calls),
            'parse_errors':sum(bool(r['parse_error']) for r in calls),
            'prompt_tokens':sum(r['prompt_tokens'] for r in calls),
            'completion_tokens':sum(r['completion_tokens'] for r in calls),
            'runtime':runtime,'scope':'All original worlds/seeds retained; no population-frequency inference from three worlds. Changes begin only after the same native goal event.'}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','worlds','episodes','actual_calls','counts']}))


if __name__=='__main__':main()
