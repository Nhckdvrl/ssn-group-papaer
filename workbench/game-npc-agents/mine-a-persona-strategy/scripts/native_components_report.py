#!/usr/bin/env python3
"""E58 role-package components; exact paired worlds, no outcome selection."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from commitment_behavior_report import estimate


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((a.directory/'manifest.json').read_text());runtime=json.loads((a.directory/'runtime.json').read_text())
    rows=list(map(json.loads,(a.directory/'branches.jsonl').read_text().splitlines()))
    cases={c['case_id']:c for c in map(json.loads,Path(manifest['arguments']['dataset']).read_text().splitlines())}
    lookup={(r['case_id'],r['persona'],r['condition']):r for r in rows}
    assert len(rows)==len(lookup)==2400 and len(cases)==200
    assert set(lookup)=={(cid,p,c) for cid in cases for p in manifest['personas'] for c in manifest['conditions']}
    report={'manifest':manifest,'runtime':runtime,'graphs':200,'branches':2400,'cells':{},'persona_effects':{},'component_contrasts':{},
            'protocol_errors':sum(bool(r['protocol_error']) for r in rows),
            'engine_rejections':dict(Counter(h.get('error','unspecified') for r in rows for h in r['history'] if not h['legal']))}
    def value(r,f):
        if f in ['request','own_task']:return float(r['flags'][f])
        if f=='accept':return float((r['conversation'] or {}).get('stance')=='accept')
        if f=='plan_request':return float(cases[r['case_id']]['request_command'] in (r.get('update') or {}).get('priority_actions',[]))
        if f=='unresolved_or_other':return float(not (r['flags']['request'] or r['flags']['own_task']))
        if f=='steps':return float(r['steps'])
        raise ValueError(f)
    for c in manifest['conditions']:
        for p in manifest['personas']:
            rs=[lookup[cid,p,c] for cid in sorted(cases)]
            report['cells'][p+'/'+c]={f:estimate([value(r,f) for r in rs]) for f in ['request','own_task','unresolved_or_other','steps','accept','plan_request']}
        for pack in ['full','traits','priority']:
            for f in ['request','own_task','unresolved_or_other','accept','plan_request']:
                report['persona_effects'][pack+'/'+c+'/'+f]=estimate([value(lookup[cid,pack+'_agreeable',c],f)-value(lookup[cid,pack+'_firm',c],f) for cid in sorted(cases)])
        for comparator in ['traits','priority']:
            for f in ['request','accept','plan_request']:
                report['component_contrasts']['full-minus-'+comparator+'/'+c+'/'+f]=estimate([
                    value(lookup[cid,'full_agreeable',c],f)-value(lookup[cid,'full_firm',c],f)
                    -value(lookup[cid,comparator+'_agreeable',c],f)+value(lookup[cid,comparator+'_firm',c],f) for cid in sorted(cases)])
    calls=list(map(json.loads,(a.directory/'model_calls.jsonl').read_text().splitlines()));assert len(calls)==runtime['calls']
    report['calls']={'count':len(calls),'parse_errors':sum(bool(r['parse_error']) for r in calls),
                     'prompt_tokens':sum(r['prompt_tokens'] for r in calls),'completion_tokens':sum(r['completion_tokens'] for r in calls)}
    report['raw_sha256']=hashlib.sha256((a.directory/'branches.jsonl').read_bytes()).hexdigest()
    report['scope']=['One new fixed sampling seed, 200 paired worlds; not pooled with E55 as independent repetitions.',
        'All three stages use the same package and regenerate their own dialogue/plan. Direct decisions do not read that dialogue.',
        'Removing a clause changes both semantics and length; the three concrete text packages are the interventions.',
        'The trait clause contains several traits, including dutiful/accommodating. This is not a pure psychometric Big Five manipulation.',
        'The native canonical action is explicitly supplied as a strong task instruction. This is not the original motivation-only human input protocol.',
        'First resource disposition is not full-episode utility or a unique normative persona choice.']
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'graphs':200,'branches':2400,'persona_request_effects':{k:v for k,v in report['persona_effects'].items() if k.endswith('/request')},'calls':report['calls']}))


if __name__=='__main__':main()
