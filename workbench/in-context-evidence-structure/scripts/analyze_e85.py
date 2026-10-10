"""E85 crossed-cue causal responses; counterfactuals use base-rule reference."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval
from e84_reader_features import output_components


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d/'run.json').read_text())
    assert max(run['control'].values()) <= .01
    rows = [json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
    assert len(rows) == run['args']['n']
    signs = np.array([r['signs'] for r in rows])
    assert signs.shape == (len(rows),8) and np.array_equal(signs[:,:4],signs[:,4:])
    raw = {k:np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    assert all(v.shape == signs.shape and np.isfinite(v).all() for v in raw.values())
    metrics = dict(base_rule_margin={k:(v[:,:4]*signs[:,:4]).mean(1) for k,v in raw.items()},
                   base_rule_agreement={k:(v[:,:4]*signs[:,:4]>0).mean(1) for k,v in raw.items()})
    for k,v in raw.items():
        parts = output_components(v,signs)
        for name,x in parts.items():
            metrics.setdefault(name,{})[k] = x.mean(1) if name!='common' else np.abs(x).mean(1)
        assert np.allclose(parts['field']+parts['code'],signs[:,:2]*(v[:,:2]-v[:,2:4])/2)
    ci = lambda v:interval(v,seed=850,nboot=4000)
    out = dict(run=run,conditions={},contrasts={},factorial={},limitations=[
        'Counterfactual scores are relative to base rule, not counterfactual task accuracy.',
        'Cue-specific path dependence does not identify the number of abstract source representations.',
        'Independent donors have different contextual histories; joint hybrid is not full NM.'])
    for k in raw:
        out['conditions'][k] = {m:ci(v[k]) for m,v in metrics.items()}
    for layout in (0,1):
        pre = f'D{layout}.'
        for name in ['name_K','label_KV','joint','full_N','full_M','full_NM','instruction']:
            out['contrasts'][pre+name+'.minus_base'] = {m:ci(v[pre+name]-v[pre+'full_base']) for m,v in metrics.items()}
        for name,full in [('name_K','full_N'),('label_KV','full_M'),('joint','full_NM')]:
            out['contrasts'][pre+name+'.minus_'+full] = {m:ci(v[pre+name]-v[pre+full]) for m,v in metrics.items()}
        out['factorial'][pre] = {}
        for m,v in metrics.items():
            b,n,l,j = [v[pre+k] for k in ['full_base','name_K','label_KV','joint']]
            out['factorial'][pre][m] = dict(name_shapley=ci(.5*((n-b)+(j-l))),
                                           label_shapley=ci(.5*((l-b)+(j-n))),interaction=ci(j-n-l+b))
    (d/'analysis.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(dict(conditions=out['conditions'],contrasts=out['contrasts']),indent=2))


if __name__ == '__main__':
    main()
