"""Prespecified input-rule and alias responses, plus frozen gap forecasts."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    ap.add_argument('--forecast',default='results/e86/frozen_forecast.json')
    a = ap.parse_args()
    dest = Path(a.directory)
    run = json.loads((dest/'run.json').read_text())
    assert max(run['control'].values())<=.01
    rows = [json.loads(x) for x in (dest/'behavior.jsonl').read_text().splitlines()]
    n = len(rows)
    assert n==run['args']['n']
    signs = np.array([r['signs'] for r in rows]).reshape(n,2,2,2,2)
    matched = np.array([r['matched'] for r in rows],dtype=bool).reshape(n,2,2,2,2)
    assert np.array_equal(signs[...,0],signs[...,1])
    assert np.array_equal(signs[...,0,:],-signs[...,1,:])
    assert matched.sum((2,3,4)).tolist()==[[4,4]]*n
    g = signs[...,1,0]
    alias_sign = g*(2*matched[...,0,0].astype(int)-1)
    metrics = {scope:{} for scope in ['unseen','seen']}
    ci = lambda v:interval(v,seed=860,nboot=4000)
    conditions = {}
    for key in rows[0]['scores']:
        z = np.array([r['scores'][key] for r in rows]).reshape(n,2,2,2,2)
        assert np.isfinite(z).all()
        m = z*signs
        rule = g*(z[...,1,:].mean(-1)-z[...,0,:].mean(-1))/2
        alias = alias_sign*(z[...,:,1].mean(-1)-z[...,:,0].mean(-1))/2
        conditions[key] = {}
        for i,scope in enumerate(['unseen','seen']):
            mask = matched[:,i]
            zm = m[:,i]
            good = np.where(mask,zm,0).sum((1,2,3))/4
            bad = np.where(~mask,zm,0).sum((1,2,3))/4
            r,al = rule[:,i].mean(1),alias[:,i].mean(1)
            assert np.allclose(good,r+al) and np.allclose(bad,r-al)
            vals = dict(rule=r,alias=al,gap=good-bad,matched_margin=good,crossed_margin=bad,
                        margin=zm.mean((1,2,3)),accuracy=(zm>0).mean((1,2,3)),
                        matched_accuracy=np.where(mask,zm>0,False).sum((1,2,3))/4,
                        crossed_accuracy=np.where(~mask,zm>0,False).sum((1,2,3))/4,
                        common_abs=np.abs(z[:,i].mean((2,3))).mean(1))
            metrics[scope][key] = vals
            conditions[key][scope] = {k:ci(v) for k,v in vals.items()}
    contrasts = {}
    for scope in metrics:
        v = metrics[scope]
        contrasts[scope] = {}
        for layout in (0,1):
            for mode in ['native','instruction']:
                s,b = [v[f'{support}.D{layout}.{mode}'] for support in ['segregated','balanced']]
                contrasts[scope][f'D{layout}.{mode}.seg_minus_bal'] = {k:ci(s[k]-b[k]) for k in s}
            for support in ['balanced','segregated']:
                ins,nat = [v[f'{support}.D{layout}.{mode}'] for mode in ['instruction','native']]
                contrasts[scope][f'{support}.D{layout}.instruction_minus_native'] = {k:ci(ins[k]-nat[k]) for k in ins}
        for mode in ['native','instruction']:
            contrasts[scope][mode+'.layout_support_interaction'] = {
                k:ci(v[f'segregated.D1.{mode}'][k]-v[f'balanced.D1.{mode}'][k]
                     -v[f'segregated.D0.{mode}'][k]+v[f'balanced.D0.{mode}'][k])
                for k in v[f'balanced.D0.{mode}']}
    forecast_path = Path(a.forecast)
    frozen = json.loads(forecast_path.read_text())
    comparisons,loss0,loss1 = {},[],[]
    for layout in (0,1):
        actual = metrics['unseen'][f'segregated.D{layout}.native']['gap']-metrics['unseen'][f'balanced.D{layout}.native']['gap']
        pred = frozen['predictions'][f'D{layout}']['cue_gap']['mean']
        l0,l1 = actual**2,(actual-pred)**2
        loss0.append(l0)
        loss1.append(l1)
        comparisons[f'D{layout}'] = dict(actual_delta_gap=ci(actual),
                                        frozen_scope_gap=0.,frozen_cue_gap=frozen['predictions'][f'D{layout}']['cue_gap'],
                                        actual_minus_cue=ci(actual-pred),scope_mse=ci(l0),cue_mse=ci(l1),
                                        cue_minus_scope_mse=ci(l1-l0))
    primary = ci(np.stack(loss1).mean(0)-np.stack(loss0).mean(0))
    out = dict(run=run,conditions=conditions,contrasts=contrasts,
               frozen_comparison=comparisons,primary_cue_minus_scope_mse=primary,
               forecast_sha256=hashlib.sha256(forecast_path.read_bytes()).hexdigest(),
               limitations=['Teacher-forced valid code, not native end-to-end generation.',
                            'Rule/alias response decomposition does not identify internal modules.',
                            'Scope wording and extra aliases can change gains; old f/c are an extrapolation.'])
    (dest/'analysis.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(dict(conditions=conditions,contrasts=contrasts,
                         frozen_comparison=comparisons,primary=primary),indent=2))


if __name__=='__main__':
    main()
