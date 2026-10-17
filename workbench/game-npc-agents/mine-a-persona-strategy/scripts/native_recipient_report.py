#!/usr/bin/env python3
"""E62 complete conditional native outcomes and prewritten causal controls."""
import argparse
from collections import Counter
import json
from pathlib import Path
from commitment_behavior_report import estimate


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    manifest=json.loads((args.run/'manifest.json').read_text());runtime=json.loads((args.run/'runtime.json').read_text())
    rows=list(map(json.loads,(args.run/'records.jsonl').read_text().splitlines()))
    assert len(rows)==runtime['generation_calls']==manifest['graphs']*48
    by={(r['case_id'],r['persona'],r['context'],r['condition'],r['draw_seed']):r for r in rows}
    assert len(by)==len(rows)
    ids=sorted({r['case_id'] for r in rows});assert len(ids)==manifest['graphs']
    seeds=manifest['draw_seeds'];contexts=manifest['contexts'];conditions=manifest['conditions']
    assert set(by)=={(cid,p,c,k,s) for cid in ids for p in ['firm','agreeable'] for c in contexts for k in conditions for s in seeds}
    def value(cid,p,c,k):
        return sum(float((by[cid,p,c,k,s]['flags'] or {}).get('request',False)) for s in seeds)/len(seeds)
    report={'manifest':manifest,'runtime':runtime,'graphs':len(ids),'cells':{},'contrasts':{},'sham':{}}
    for context in contexts:
        for p in ['firm','agreeable']:
            for condition in conditions:
                selected=[by[cid,p,context,condition,s] for cid in ids for s in seeds]
                report['cells'][context+'/'+p+'/'+condition]={
                    'request_rate':estimate([value(cid,p,context,condition) for cid in ids]),
                    'protocol_errors':sum(bool(r['protocol_error']) for r in selected),
                    'native_errors':sum((r['native'] or {}).get('event_type')=='ErrorEvent' for r in selected),
                    'commands':dict(Counter(r['command'] for r in selected)),
                    'own_task_count':sum(bool((r['flags'] or {}).get('own_task')) for r in selected)}
        for condition in conditions:
            report['contrasts'][context+'/persona/'+condition]=estimate([
                value(cid,'agreeable',context,condition)-value(cid,'firm',context,condition) for cid in ids])
        for condition in ['sham','donor','random']:
            for p in ['firm','agreeable']:
                report['contrasts'][context+'/'+p+'/'+condition+'-baseline']=estimate([
                    value(cid,p,context,condition)-value(cid,p,context,'baseline') for cid in ids])
            # Positive means the intervention moves both targets toward the donor role's direction.
            report['contrasts'][context+'/signed/'+condition]=estimate([
                ((value(cid,'firm',context,condition)-value(cid,'firm',context,'baseline'))
                 -(value(cid,'agreeable',context,condition)-value(cid,'agreeable',context,'baseline')))/2 for cid in ids])
        report['sham'][context]={'pairs':len(ids)*2*len(seeds),'command_mismatches':sum(
            by[cid,p,context,'sham',s]['command']!=by[cid,p,context,'baseline',s]['command']
            for cid in ids for p in ['firm','agreeable'] for s in seeds)}
    prompts=list(map(json.loads,(args.run/'prompts.jsonl').read_text().splitlines()))
    scores={(r['case_id'],r['persona'],r['context']):r['candidate_log_likelihood'] for r in prompts}
    report['language_scores']={}
    for c in contexts:
        margin=lambda cid,p:scores[cid,p,c]['request_command']-scores[cid,p,c]['own_command']
        report['language_scores'][c]={'persona_margin_change':estimate([margin(cid,'agreeable')-margin(cid,'firm') for cid in ids]),
            'firm_margin':estimate([margin(cid,'firm') for cid in ids]),
            'agreeable_margin':estimate([margin(cid,'agreeable') for cid in ids])}
    report['scope']=['All 102 authored Give-goal worlds; two paired draws per cell, graph bootstrap.',
        'Explicit conditioning on Give action family: no free-policy or full-persona ability claim.',
        'Choices are original/request recipient allocations, not total character welfare or unique gold choices.',
        'Donor residual changes one midpoint position; full input roles remain coherent.',
        'Source role package includes multiple traits/values and a length change; random controls are not exhaustive confound removal.',
        'Full suffix language scores differ from constrained decoder probabilities; companion readout reports exact first-branch probabilities.',
        'No independent learned cross-task direction or new steering method claimed.']
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'graphs':len(ids),'runtime':runtime,'sham':report['sham'],
        'baseline_persona':{c:report['contrasts'][c+'/persona/baseline'] for c in contexts},
        'signed_donor':{c:report['contrasts'][c+'/signed/donor'] for c in contexts},
        'signed_random':{c:report['contrasts'][c+'/signed/random'] for c in contexts}}))


if __name__=='__main__':main()
