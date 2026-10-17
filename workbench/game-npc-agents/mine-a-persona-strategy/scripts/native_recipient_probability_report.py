#!/usr/bin/env python3
"""E62 exact branch mass, role effects and declared activation controls."""
import argparse
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((a.run/'manifest.json').read_text());runtime=json.loads((a.run/'runtime.json').read_text())
    src=manifest['source_manifest'];rows=list(map(json.loads,(a.run/'probabilities.jsonl').read_text().splitlines()))
    by={(r['case_id'],r['persona'],r['context'],r['condition']):r for r in rows}
    ids=src['case_ids'];assert len(rows)==len(by)==len(ids)*3*2*4
    value=lambda cid,p,c,k:by[cid,p,c,k]['request_probability']
    report={'manifest':manifest,'runtime':runtime,'cells':{},'contrasts':{},'sham':{}}
    for context in src['contexts']:
        for p in ['firm','agreeable']:
            for cond in src['conditions']:
                probs=[value(cid,p,context,cond) for cid in ids]
                odds=[by[cid,p,context,cond]['processed_branch_log_odds'] for cid in ids]
                report['cells'][context+'/'+p+'/'+cond]={'request_probability':estimate(probs),
                    'probability_quantiles':dict(zip(['min','q25','median','q75','max'],map(float,np.quantile(probs,[0,.25,.5,.75,1])))),
                    'log_odds':estimate(odds), 'observed_probability_below_01':sum(v<.01 for v in probs),
                    'observed_probability_above_99':sum(v>.99 for v in probs)}
        for cond in src['conditions']:
            report['contrasts'][context+'/persona/'+cond]=estimate([
                value(cid,'agreeable',context,cond)-value(cid,'firm',context,cond) for cid in ids])
        for cond in ['sham','donor','random']:
            report['contrasts'][context+'/signed/'+cond]=estimate([
                (value(cid,'firm',context,cond)-value(cid,'firm',context,'baseline')
                 -value(cid,'agreeable',context,cond)+value(cid,'agreeable',context,'baseline'))/2 for cid in ids])
            report['contrasts'][context+'/absolute/'+cond]=estimate([
                (abs(value(cid,'firm',context,cond)-value(cid,'firm',context,'baseline'))
                 +abs(value(cid,'agreeable',context,cond)-value(cid,'agreeable',context,'baseline')))/2 for cid in ids])
        report['sham'][context]={'max_probability_change':max(abs(value(cid,p,context,'sham')-value(cid,p,context,'baseline'))
                for cid in ids for p in ['firm','agreeable'])}
    report['scope']=['Exact probability of the full conditional native Give command: two leaves share a maximal prefix, first branch determines the unique leaf.',
        'Uses actual generation logits processors and temperature .7; unconstrained language suffix scores remain a separate diagnostic.',
        'This is a fixed action-family/JSON-prefix task, not full free-policy probability or private welfare.',
        'Small probability shifts under a dominant goal do not establish missing persona representations; single midpoint null does not establish absence.',
        'The 1%/99% counts describe the observed distribution, never a scientific pass/fail bar.']
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'baseline_role':{c:report['contrasts'][c+'/persona/baseline'] for c in src['contexts']},
        'signed_donor':{c:report['contrasts'][c+'/signed/donor'] for c in src['contexts']},
        'signed_random':{c:report['contrasts'][c+'/signed/random'] for c in src['contexts']},
        'sham':report['sham']}))


if __name__=='__main__':main()
