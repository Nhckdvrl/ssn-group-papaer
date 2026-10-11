"""Prospective E119 observer: distinguish common direction from task-specific rotation.
Frozen before any E119 GPU scores. Original E118 readouts stay unchanged.
"""
import argparse,json
from pathlib import Path
import numpy as np
from e118_criterion_code_feature_crossing import interval


def analyze(dest):
    rows=[json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    cs=[json.loads(x) for x in (dest/'contexts.jsonl').read_text().splitlines()]
    f=np.array([r['gold'] for r in rows]);s=np.array([c['service_gold'] for c in cs])
    z={k:np.array([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    out={'n_contexts':len(rows),'status':'prospective E119 observer, frozen before first E119 score',
         'null':'within-context two criterion code responses share one functional F/S direction; independent gains permitted',
         'scope':'functional response directions under stated cache interfaces; not proof of a unique hidden program', 'modes':{}}
    for mode in ['native','gate','label','label_gate','edge','edge_gate','far_label']:
        def condition(w):
            if w=='origin' and mode not in ['native','gate','far_label']:
                return 'origin_'+('gate' if mode.endswith('gate') else 'native')
            return w+'_'+mode
        dfood=.5*(z[condition('food_positive')]-z[condition('food_negative')])
        dservice=.5*(z[condition('origin')]-z[condition('service_negative')])
        m=np.stack([np.stack([(dfood*f).mean(1),(dfood*s).mean(1)],1),
                    np.stack([(dservice*f).mean(1),(dservice*s).mean(1)],1)],1)
        determinant=m[:,0,0]*m[:,1,1]-m[:,0,1]*m[:,1,0]
        norms=np.linalg.norm(m,axis=2);weak=np.any(norms<=.001,axis=1)
        denom=norms.prod(1)
        normalized=np.divide(determinant,denom,out=np.zeros_like(determinant),where=~weak)
        out['modes'][mode]={'matrix_mean':m.mean(0).tolist(),
            'determinant_nats_squared':interval(determinant),
            'normalized_rotation':interval(normalized),'weak_row_contexts':int(weak.sum()),
            'weak_handling':'either row norm <= .001 nats: rotation defined zero, all contexts retained',
            'per_context_matrix':m.tolist()}
    (dest/'response_rotation.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();analyze(Path(a.out))
