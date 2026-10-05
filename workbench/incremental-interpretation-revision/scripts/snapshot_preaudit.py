"""Freeze an externally reviewed exploratory cohort; never promote advisory gold."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
from data import CACHE,sha,write_jsonl
from step_audit import items_from

def snapshot(data,audit_dir,out,max_set,additional_audit_dirs=()):
    rows=[json.loads(x) for x in data.read_text().splitlines()]
    annotations={};reports=[];missing=[]
    for item in items_from(rows):
        if int(item['variant_id'].split(':')[1])>max_set:continue
        uid=hashlib.sha256(item['variant_id'].encode()).hexdigest()[:20]
        roots=[audit_dir,*additional_audit_dirs]
        candidates=[(root,root/f'{uid}.review.json') for root in roots if (root/f'{uid}.review.json').exists()]
        complete=[(root,p) for root,p in candidates if json.loads(p.read_text())['status']=='complete_advisory']
        if len(complete)>1:
            parsed=[json.loads(p.read_text()) for _,p in complete]
            assert len({r['request_sha256'] for r in parsed})==1,'Different independent audit inputs'
            signatures=[(r['annotation']['grammaticality'],sorted((a['item_id'],a['question_valid'],a['answer'],a['certainty']) for a in r['annotation']['answers'])) for r in parsed]
            assert all(x==signatures[0] for x in signatures),'External auditors disagree; preserve and resolve before adopting'
        root,p=(complete or candidates or [(audit_dir,audit_dir/f'{uid}.review.json')])[0]
        if not p.exists():missing.append({'variant_id':item['variant_id'],'status':'pending'});continue
        r=json.loads(p.read_text())
        if r['status']!='complete_advisory':missing.append({'variant_id':item['variant_id'],'status':r['status']});continue
        request=json.loads((root/f'{uid}.request.json').read_text())
        assert json.loads(request['message'].split('INPUT JSON:\n',1)[1])==item,'stale input'
        assert r['request_sha256']==hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
        event_path=root/f'{uid}.events.jsonl'
        assert sha(event_path)==r['events_sha256']
        events=[json.loads(l) for l in event_path.read_text().splitlines() if l]
        finishes=[e for e in events if e['type']=='step_finish']
        assert finishes and finishes[-1]['part']['reason']=='stop'
        assert not any(e['type'] in ('tool','tool_use','tool_call') for e in events),'unexpected tool invocation'
        a=r['annotation'];assert a['variant_id']==item['variant_id']
        assert len(a['answers'])==len({q['item_id'] for q in a['answers']})
        assert {q['item_id'] for q in a['answers']}=={q['item_id'] for q in item['questions']}
        reports.append(r)
        for answer in a['answers']:annotations[answer['item_id']]=(r,answer)
    selected=[]
    for r in rows:
        if r['item_id'] not in annotations:continue
        report,a=annotations[r['item_id']];v=report['annotation']
        eligible=a['question_valid'] and a['certainty']!='invalid' and v['grammaticality']!='unacceptable'
        r=dict(r,proposed_gold=r['gold'],gold=None,gold_status='advisory_probability_only',
               audit_provider=report['model'],audit_tier='external_advisory',audit_request_sha256=report['request_sha256'],
               audit_response_sha256=report['events_sha256'],auditor_answer=a['answer'],auditor_certainty=a['certainty'],
               auditor_grammar=v['grammaticality'],auditor_relation_status=a['relation_status'],
               auditor_blocker_status=v['blocker_status'],auditor_ambiguity_status=v['ambiguity_status'],
               eligible=eligible,clean_stratum=eligible and v['grammaticality']=='acceptable')
        selected.append(r)
    assert selected and len({r['item_id'] for r in selected})==len(selected)
    assert not out.exists(),'immutable cohort: use a new snapshot path'
    write_jsonl(out,selected)
    summary=dict(source_sha256=sha(data),snapshot_sha256=sha(out),max_source_set_index=max_set,
                 audit_directories=[str(audit_dir),*[str(p) for p in additional_audit_dirs]],
                 variants_complete=len(reports),variants_missing=missing,question_rows=len(selected),
                 eligible=sum(r['eligible'] for r in selected),gold_labels=0,proxy_used=False,
                 scope='Prior authorized independent opencode advisory; probability-only, not Step5-validated ability scores.',
                 grammar_counts=dict(collections.Counter(r['annotation']['grammaticality'] for r in reports)),
                 coverage=dict(collections.Counter(r['variant_id'].split(':')[0] for r in reports)),
                 annotation_model=sorted({r['model'] for r in reports}),
                 provenance=[{k:r[k] for k in ('variant_id','request_sha256','events_sha256','model')} for r in reports])
    out.with_suffix('.audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=CACHE/'normalized/jurayj.jsonl')
    p.add_argument('--audit-dir',type=Path,default=CACHE/'opencode-preaudit-E01-v2')
    p.add_argument('--additional-audit-dir',type=Path,action='append',default=[])
    p.add_argument('--max-set',type=int,default=3);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    s=snapshot(a.data,a.audit_dir,a.out,a.max_set,a.additional_audit_dir);print(json.dumps({k:v for k,v in s.items() if k not in ('provenance','variants_missing')},indent=2))
