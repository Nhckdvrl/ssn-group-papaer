"""PRE-RESULT extra observer; discovery tagged POST-HOC-DESIGN.
No GPU execution and no changes to E117 primary analysis or condition set.
"""
import argparse,json
from pathlib import Path
import numpy as np
from e117_criterion_feature_formation import interval


def analyze(dest,phase):
    rows=[json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    cs=[json.loads(x) for x in (dest/'contexts.jsonl').read_text().splitlines()]
    f=np.array([r['gold'] for r in rows]);s=np.array([c['service_gold'] for c in cs])
    p=np.array([-1 if c['reverse'] else 1 for c in cs])[:,None]
    assert f.shape==s.shape==(len(rows),8)
    assert np.all((f*s).sum(1)==0) and np.all(f.sum(1)==0) and np.all(s.sum(1)==0)
    z={k:np.array([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    coeff={}
    for k,v in z.items():
        b=(v*p).mean(1);ff=(v*f).mean(1);ss=(v*s).mean(1);fs=(v*f*s*p).mean(1)
        coeff[k]={'bias':b,'food':ff,'service':ss,'food_service':fs,
                  'service_at_food_positive':ss+fs,'service_at_food_negative':ss-fs}
    pairs=[('origin_f0r0','cross_f0r0'),('origin_gate_shared','cross_gate_shared'),
           ('relation_label_cross_native','relation_label_within_native'),
           ('relation_gate_label_cross','relation_gate_label_within'),
           ('relation_answer_cross_kv_native','relation_answer_within_kv_native'),
           ('relation_answer_cross_kv_native_gate','relation_answer_within_kv_native_gate'),
           ('relation_answer_cross_v_native_gate','origin_gate_shared')]
    out={'n_contexts':len(rows),'phase':phase,'discovery_status':'POST-HOC-DESIGN, defined before author inspected E117 outcomes',
         'confirmation_status':'frozen before independent n32 run','feature_decomposition':'exact four-point contrasts, not trained linear probe',
         'responses':{k:{q:interval(v) for q,v in vv.items()} for k,vv in coeff.items()},
         'contrasts':{l+'_minus_'+r:{q:interval(coeff[l][q]-coeff[r][q]) for q in coeff[l]} for l,r in pairs}}
    (dest/'complete_feature_profile.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--phase',choices=['discovery','confirmation'],required=True)
    a=ap.parse_args();analyze(Path(a.out),a.phase)
