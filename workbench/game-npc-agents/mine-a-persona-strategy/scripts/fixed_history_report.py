#!/usr/bin/env python3
"""E59 labeled text claims and independent state answers; all fixed worlds."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from commitment_behavior_report import estimate


def wilson(values):
    n=len(values);p=sum(values)/n;z=1.959963984540054;den=1+z*z/n
    center=(p+z*z/(2*n))/den
    width=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0.,center-width),min(1.,center+width)]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--labels',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((a.run/'manifest.json').read_text());runtime=json.loads((a.run/'runtime.json').read_text())
    records=list(map(json.loads,(a.run/'records.jsonl').read_text().splitlines()));assert len(records)==400
    mapping=json.loads((a.labels/'private_mapping.json').read_text());public={r['annotation_id']:r for r in json.loads((a.labels/'public_data.json').read_text())}
    labels={};metadata=[]
    for d in sorted(a.labels.glob('batch_*')):
        if (d/'metadata.json').exists():metadata.append(json.loads((d/'metadata.json').read_text()))
        if not (d/'labels.json').exists():continue
        for row in json.loads((d/'labels.json').read_text()):
            aid=row['annotation_id'];assert aid not in labels and aid in mapping
            assert row['exact_quote'] in public[aid]['memory'];labels[aid]=row
    assert set(labels)==set(mapping) and len(labels)==808,'Preserve missing labels; do not fabricate rows'
    lookup={(r['case_id'],r['persona']):r for r in records};assert len(lookup)==400
    ids=sorted({r['case_id'] for r in records});assert len(ids)==200
    sem={};anchors={}
    for aid,key in mapping.items():
        if 'anchor_expected' in key:
            anchors[aid]={'expected':key['anchor_expected'],'actual':labels[aid]['handover_claim'],
                          'match':key['anchor_expected']==labels[aid]['handover_claim']}
        else:sem[key['case_id'],key['persona'],key['condition']]=labels[aid]
    report={'manifest':manifest,'runtime':runtime,'graphs':200,'records':400,'cells':{},'contrasts':{},'anchors':anchors,
            'label_sha256':hashlib.sha256(json.dumps(labels,sort_keys=True).encode()).hexdigest()}
    claim=lambda k:float(sem[k]['handover_claim']=='yes')
    for p in ['firm','agreeable']:
        for c in ['natural','fixed_future']:
            values=[sem[cid,p,c]['handover_claim'] for cid in ids]
            v=[claim((cid,p,c)) for cid in ids]
            report['cells'][p+'/'+c]={'labels':dict(Counter(values)),'asserted_physical_transfer':estimate(v),
                                    'asserted_transfer_wilson_95':wilson(v)}
        rs=[lookup[cid,p] for cid in ids]
        report['cells'][p+'/factual']={'holder_correct':estimate([float((r['factual_readout'] or {}).get('holder')==r['expected_holder']) for r in rs]),
            'physical_transfer_answer_yes':estimate([float((r['factual_readout'] or {}).get('give_executed')=='yes') for r in rs]),
            'give_answers':dict(Counter((r['factual_readout'] or {}).get('give_executed','parse_error') for r in rs))}
        report['contrasts'][p+'/fixed-natural']=estimate([claim((cid,p,'fixed_future'))-claim((cid,p,'natural')) for cid in ids])
    for c in ['natural','fixed_future']:
        report['contrasts']['persona/'+c]=estimate([claim((cid,'agreeable',c))-claim((cid,'firm',c)) for cid in ids])
    audit_path=Path(__file__).parent.parent/'results/E59_literal_claim_audit.json'
    if audit_path.exists():
        audit=json.loads(audit_path.read_text())
        replacements={r['annotation_id']:r['reviewed_claim'] for r in audit['rows'] if r['annotation_id'] in labels}
        corrected={}
        for aid,key in mapping.items():
            if 'case_id' in key:
                corrected[key['case_id'],key['persona'],key['condition']]=replacements.get(aid,labels[aid]['handover_claim'])
        report['literal_review']={'scope':audit['scope'],'changed_labels':len(replacements),'cells':{},'contrasts':{}}
        for p in ['firm','agreeable']:
            for c in ['natural','fixed_future']:
                report['literal_review']['cells'][p+'/'+c]=dict(Counter(corrected[cid,p,c] for cid in ids))
        for c in ['natural','fixed_future']:
            report['literal_review']['contrasts']['persona/'+c]=estimate([
                float(corrected[cid,'agreeable',c]=='yes')-float(corrected[cid,'firm',c]=='yes') for cid in ids])
    report['usage']={'requests':len(metadata),'completed':sum(m['complete'] for m in metadata),
        **{k:sum((m.get('usage') or {}).get(k,0) for m in metadata) for k in ['prompt_tokens','completion_tokens','total_tokens']},
        'model':'step-5-preview','endpoint':'https://api.stepfun.com/step_plan/v1/chat/completions','cash_endpoint_calls':0,'npc_cloud_calls':0}
    calls=list(map(json.loads,(a.run/'model_calls.jsonl').read_text().splitlines()))
    assert len(calls)==runtime['calls'];report['npc_calls']={'count':len(calls),'parse_errors':sum(bool(r['parse_error']) for r in calls)}
    report['scope']=['Labels classify text assertions, not internal beliefs or executed goal truth.',
        'Both histories have zero physical handovers; factual answers are not fed to the writer.',
        'Persona comparison within fixed_future shares the same prior utterance and world.',
        'The explicit future utterance changes semantics/length and also fixes acceptance; natural comparison is a clarity/context control.',
        'Ambiguous claims are preserved as their own class, never promoted to physically completed.']
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'graphs':200,'cells':report['cells'],'contrasts':report['contrasts'],'usage':report['usage']}))


if __name__=='__main__':main()
