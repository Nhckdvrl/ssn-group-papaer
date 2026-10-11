"""Frozen competing predictions on natural and conflicting source/code cues."""
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
    rows = [json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
    assert len(rows) == run['args']['n'] and max(run['control'].values()) <= .01
    signs = np.array([r['signs'] for r in rows])
    assert signs.shape == (len(rows),8) and np.array_equal(signs[:,:4],signs[:,4:])
    raw = {k:np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    assert all(v.shape == signs.shape and np.isfinite(v).all() for v in raw.values())
    ci = lambda v:interval(v,seed=840,nboot=4000)
    metrics = dict(natural_margin={k:(v[:,:4]*signs[:,:4]).mean(1) for k,v in raw.items()},
                   natural_accuracy={k:(v[:,:4]*signs[:,:4]>0).mean(1) for k,v in raw.items()})
    for k,v in raw.items():
        parts = output_components(v,signs)
        for name,x in parts.items():
            metrics.setdefault(name,{})[k] = x.mean(1) if name != 'common' else np.abs(x).mean(1)
        assert np.allclose(parts['field']+parts['code'],signs[:,:2]*(v[:,:2]-v[:,2:4])/2)
    out = dict(run=run,conditions={},contrasts={},prediction={},predictive_contrasts={},effects={},effect_contrasts={},limitations=[
        'Conflicting redundant identities are not a native capability accuracy test.',
        'Field/code output decomposition is descriptive; it does not by itself identify independent modules.',
        'Predictors share coefficients fitted only on E82 natural data; neither reader uses new donor output.'])
    for k in raw:
        out['conditions'][k] = {m:ci(v[k]) for m,v in metrics.items()}
    pairs = [('layout.native','D1.native','D0.native'),('code.minus_field','D0.R_code','D0.R_field')]
    pairs += [(name+'.minus_native','D0.'+name,'D0.native') for name in ['B','R_field','R_code','oracle_label']]
    pairs += [(name+'.minus_oracle','D0.'+name,'D0.oracle_label') for name in ['B','R_field','R_code']]
    for name,x,y in pairs:
        out['contrasts'][name] = {m:ci(v[x]-v[y]) for m,v in metrics.items()}
    errors = {}
    for scope,indices in [('natural',slice(0,4)),('conflict',slice(4,8))]:
        errors[scope] = {}
        out['prediction'][scope],out['effects'][scope],out['predictive_contrasts'][scope] = {},{},{}
        for name in ['B','R_field','R_code']:
            errors[scope][name] = {k:np.array([r['predictive_errors'][name][scope][k] for r in rows])
                                    for k in rows[0]['predictive_errors'][name][scope]}
            out['prediction'][scope][name] = {k:ci(v) for k,v in errors[scope][name].items()}
            pred = (raw['D0.'+name]-raw['D0.native'])[:,indices]
            actual = (raw['D0.oracle_label']-raw['D0.native'])[:,indices]
            squared_error = np.square(pred-actual).mean(1)
            out['effects'][scope][name] = dict(mse=ci(squared_error),rmse=float(np.sqrt(squared_error.mean())),
                                              correlation=float(np.corrcoef(pred.flatten(),actual.flatten())[0,1]))
        out['predictive_contrasts'][scope]['R_code.minus_R_field'] = {
            k:ci(errors[scope]['R_code'][k]-errors[scope]['R_field'][k]) for k in errors[scope]['R_code']}
        out['effect_contrasts'][scope+'.code_minus_field_mse'] = ci(
            np.square(((raw['D0.R_code']-raw['D0.oracle_label'])[:,indices])).mean(1)
            -np.square(((raw['D0.R_field']-raw['D0.oracle_label'])[:,indices])).mean(1))
    (d/'analysis.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(dict(conditions=out['conditions'],predictive_contrasts=out['predictive_contrasts'],
                          effects=out['effects'],effect_contrasts=out['effect_contrasts']),indent=2))


if __name__ == '__main__':
    main()
