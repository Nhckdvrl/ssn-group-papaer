#!/usr/bin/env python3
"""E55 frozen 200-world cohort: actual outcomes, plans and quality strata."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


def est(rows,metric):
    grouped=defaultdict(list)
    for r in rows:grouped[r['case_id']].append(metric(r))
    return estimate([np.mean(x) for x in grouped.values()])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directories',type=Path,nargs='+',required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    rows=[];manifests=[];runtimes=[];ids=set();expressions=[]
    for d in a.directories:
        m=json.loads((d/'manifest.json').read_text());rt=json.loads((d/'runtime.json').read_text())
        assert not ids.intersection(m['case_ids']);ids.update(m['case_ids']);manifests.append(m);runtimes.append(rt)
        rows.extend(map(json.loads,(d/'branches.jsonl').read_text().splitlines()))
        expressions.extend(map(json.loads,(d/'expression.jsonl').read_text().splitlines()))
    ref=manifests[0]
    for m in manifests:
        for key in ['dataset_sha256','quality_sha256','script_sha256','conditions','personas','shared_helpers']:assert m[key]==ref[key],key
        for key in ['model','seeds','dataset','quality']:assert m['arguments'][key]==ref['arguments'][key],key
    seeds=ref['arguments']['seeds'];conditions=ref['conditions'];assert len(ids)==200
    lookup={(r['case_id'],r['seed'],r['persona'],r['condition']):r for r in rows}
    assert len(lookup)==len(rows)==5600 and len(expressions)==400
    quality=json.loads(Path(ref['arguments']['quality']).read_text())
    cases={r['case_id']:r for r in map(json.loads,Path(ref['arguments']['dataset']).read_text().splitlines())}
    report={'graphs':200,'branches':5600,'expressions':400,'manifests':manifests,'runtimes':runtimes,
            'cells':{},'contrasts':{},'quality_strata':{},'goal_kind_strata':{},'plans':{},'first_events':{},
            'protocol_errors':sum(bool(r['protocol_error']) for r in rows),
            'illegal_actions':sum(not h['legal'] for r in rows for h in r['history']),
            'scope':'first allocation/consumption/equipment within <=6 actions, not full-episode welfare or a unique correct persona choice'}
    req=lambda r:float(r['flags']['request']);own=lambda r:float(r['flags']['own_task'])
    def cell(rs):
        return {'branches':len(rs),'graphs':len({r['case_id'] for r in rs}),
                'request_count':sum(req(r) for r in rs),'own_count':sum(own(r) for r in rs),
                'request':est(rs,req),'own_task':est(rs,own),
                'unresolved_or_other':est(rs,lambda r:not(r['flags']['own_task'] or r['flags']['request'])),
                'steps':est(rs,lambda r:r['steps'])}
    def paired(label,left,right,subset=None):
        gs=ids if subset is None else subset;points=defaultdict(list)
        for cid in sorted(gs):
            for seed in seeds:
                k1=(cid,seed,*left);k0=(cid,seed,*right)
                if k1 in lookup and k0 in lookup:points[cid].append(req(lookup[k1])-req(lookup[k0]))
        return estimate([np.mean(x) for x in points.values()])
    for p in ['firm','agreeable']:
        for c in conditions+['force_own','force_request']:
            rs=[r for r in rows if r['persona']==p and r['condition']==c];report['cells'][p+'/'+c]=cell(rs)
            report['first_events'][p+'/'+c]=dict(Counter(r['history'][0]['event_type'] if r['history'] else 'no_event' for r in rs))
        for l,r in [('direct_history','direct_request'),('plan_raw','direct_history'),('plan_grounded','plan_raw')]:
            report['contrasts'][p+'/'+l+'-'+r]=paired('',(p,l),(p,r))
        for c in ['plan_raw','plan_grounded']:
            rs=[r for r in rows if r['persona']==p and r['condition']==c and r['update'] is not None]
            def order(r):
                q=cases[r['case_id']];return [x for x in r['update']['priority_actions'] if x in [q['goal_command'],q['request_command']]]
            report['plans'][p+'/'+c]={'request_any':est(rs,lambda r:cases[r['case_id']]['request_command'] in order(r)),
                'request_first':est(rs,lambda r:bool(order(r)) and order(r)[0]==cases[r['case_id']]['request_command']),
                'own_then_request':est(rs,lambda r:order(r)==[cases[r['case_id']]['goal_command'],cases[r['case_id']]['request_command']]),
                'stances':dict(Counter(r['conversation']['stance'] for r in rs))}
    for c in conditions:report['contrasts']['persona/'+c]=paired('',('agreeable',c),('firm',c))
    for category in ['keep','review','reject']:
        gs={g for g in ids if quality[g]['decision']==category}
        report['quality_strata'][category]={'graphs':len(gs),'persona_effects':{c:paired('',('agreeable',c),('firm',c),gs) for c in conditions}}
    for kind in sorted({r['goal_kind'] for r in rows}):
        gs={g for g in ids if cases[g]['goal_kind']==kind}
        report['goal_kind_strata'][kind]={'graphs':len(gs),'persona_effects':{c:paired('',('agreeable',c),('firm',c),gs) for c in conditions}}
    calls=[]
    for d in a.directories:calls.extend(map(json.loads,(d/'model_calls.jsonl').read_text().splitlines()))
    report['calls']={'count':len(calls),'parse_errors':sum(bool(r['parse_error']) for r in calls),
                     'prompt_tokens':sum(r['prompt_tokens'] for r in calls),'completion_tokens':sum(r['completion_tokens'] for r in calls)}
    assert len(calls)==sum(r['calls'] for r in runtimes)
    report['raw_hashes']={str(d):hashlib.sha256((d/'branches.jsonl').read_bytes()).hexdigest() for d in a.directories}
    report['control_scope']='force_request is semantic instruction compliance with original goals retained, not an isolated motor-capability test; E56 literal control and factual mapping reported separately'
    report['history_scope']='direct_history retains earlier speech-only instruction; E56 phase_end is the explicit scope control; no-action rate here is not a persona-failure rate'
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'graphs':200,'branches':len(rows),'contrasts':report['contrasts'],'calls':report['calls'],'protocol_errors':report['protocol_errors']}))


if __name__=='__main__':main()
