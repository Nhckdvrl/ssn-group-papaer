#!/usr/bin/env python3
"""Declared E67 new diagonal vs historical reference; primary effects remain within-run."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from native_rule_cross_report import metrics,summarize


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--sources',type=Path,nargs='+',required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();new=[];old={}
    for d in a.runs:
        assert (d/'runtime.json').exists()
        new.extend(r for r in map(json.loads,(d/'episodes.jsonl').read_text().splitlines())
                   if r['feedback']=='legacy' and r['upstream_rule']==r['exec_rule'])
    for d in a.sources:
        for r in map(json.loads,(d/'episodes.jsonl').read_text().splitlines()):
            old[r['case_id'],r['seed'],r['persona'],r['mode'],r['rule']]=r
    groups=defaultdict(lambda:defaultdict(list))
    for r in new:
        original=old[r['case_id'],r['seed'],r['persona'],r['mode'],r['upstream_rule']]
        assert r['conversation']==original['conversation'] and r['update']==original['update']
        now,before=metrics(r),metrics(original)
        v={f:now[f]-before[f] for f in ['goal','transfer','first_step_block','any_legal_block','repeat_block_errors']}
        v['identical_command_sequence']=float([h['command'] for h in r['history']]==[h['command'] for h in original['history']])
        groups[r['persona']+'/'+r['upstream_rule']][r['case_id']].append(v)
    cells={}
    for label,points in groups.items():
        fields=list(next(iter(points.values()))[0]);cells[label]=summarize([[np.mean([v[f] for v in vs]) for f in fields] for vs in points.values()],fields)
    a.out.write_text(json.dumps({'comparison':'new legacy diagonal minus historical execution; upstream outputs identical',
        'scope':'Old look/inventory ordering and runtime batching differ. Primary rule and feedback contrasts use new paired diagonals.',
        'episodes':len(new),'cells':cells,'model_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
