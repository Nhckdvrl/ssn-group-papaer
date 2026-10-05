"""Apply independent Step5 annotations without making semantic gold decisions."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
from data import CACHE, sha, write_jsonl
from step_audit import items_from

def adopt(data, audit_dir, out):
    rows=[json.loads(x) for x in data.read_text().splitlines()]
    items=items_from(rows); annotations={}; reports=[]
    for item in items:
        uid=hashlib.sha256(item['variant_id'].encode()).hexdigest()[:20]
        p=audit_dir/f'{uid}.review.json'
        if not p.exists():continue
        report=json.loads(p.read_text())
        if report['status']!='complete':continue
        request=json.loads((audit_dir/f'{uid}.request.json').read_text())
        assert json.loads(request['messages'][1]['content'])==item,'stale audit input'
        assert report['request_sha256']==hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
        assert report['response_sha256']==sha(audit_dir/f'{uid}.response.json')
        a=report['annotation']; assert a['variant_id']==item['variant_id']
        assert {q['item_id'] for q in item['questions']}=={q['item_id'] for q in a['answers']}
        reports.append(report)
        for answer in a['answers']:annotations[answer['item_id']]=(report,answer)
    applied=[]
    for r in rows:
        if r['item_id'] not in annotations:continue
        report,a=annotations[r['item_id']];v=report['annotation']
        r=dict(r,proposed_gold=r['gold'],step_gold=a['answer'],step_question_valid=a['question_valid'],
               step_grammar=v['grammaticality'],step_certainty=a['certainty'],
               step_relation_status=a['relation_status'],step_blocker_status=v['blocker_status'],
               step_ambiguity_status=v['ambiguity_status'],step_response_id=report['response_id'],
               step_request_sha256=report['request_sha256'],step_response_sha256=report['response_sha256'])
        # Preserve unscored semantic diagnostics. Restore other labels only from Step5.
        r['gold']=a['answer'] if not r['diagnostic_only'] and a['certainty']=='clear' and a['question_valid'] else None
        r['gold_status']='step5_independent' if r['gold'] is not None else 'diagnostic_no_gold'
        r['eligible']=a['question_valid'] and a['certainty']!='invalid' and v['grammaticality']!='unacceptable'
        r['clean_stratum']=r['eligible'] and v['grammaticality']=='acceptable'
        applied.append(r)
    assert len({r['item_id'] for r in applied})==len(applied)
    write_jsonl(out,applied)
    summary={'data_sha256':sha(data),'audited_sha256':sha(out),'variants_requested':len(items),
             'variants_complete':len(reports),'questions_annotated':len(applied),
             'eligible':sum(r['eligible'] for r in applied),'acceptable_eligible':sum(r['clean_stratum'] for r in applied),
             'grammar_counts':dict(collections.Counter(x['annotation']['grammaticality'] for x in reports)),
             'scored_gold_counts':dict(collections.Counter(str(r['gold']) for r in applied if r['eligible'])),
             'changed_proposed_gold':sum(r['gold'] is not None and r['proposed_gold'] is not None and r['gold']!=r['proposed_gold'] for r in applied),
             'model':'step-5-preview','proxy_used':False,
             'annotation_scope':'Step5 labels; agent checks IDs/hashes/schema only; historical agent flags retained as provenance, not exclusion rules'}
    out.with_suffix('.audit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=CACHE/'normalized/jurayj.jsonl')
    p.add_argument('--audit-dir',type=Path,default=CACHE/'step5-audit-E01-v5');p.add_argument('--out',type=Path,default=CACHE/'normalized/jurayj-step5.jsonl')
    args=p.parse_args();print(json.dumps(adopt(args.data,args.audit_dir,args.out),indent=2))
