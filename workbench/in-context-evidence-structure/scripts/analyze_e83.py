"""Fixed E83 predictive and behavioral comparisons, with context bootstrap."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d/'run.json').read_text())
    rows = [json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
    assert len(rows) == run['args']['n'] and max(run['control'].values()) <= .01
    signs = np.array([r['signs'] for r in rows])
    assert signs.shape == (len(rows),4) and np.array_equal(signs[:,:2],-signs[:,2:])
    raw = {k:np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    assert all(v.shape == signs.shape and np.isfinite(v).all() for v in raw.values())
    metrics = dict(margin={k:(v*signs).mean(1) for k,v in raw.items()},
                   accuracy={k:(v*signs>0).mean(1) for k,v in raw.items()},
                   output_source_ranking={k:((v[:,:2]-v[:,2:])*signs[:,:2]>0).mean(1) for k,v in raw.items()},
                   abs_common_component={k:np.abs((v[:,:2]+v[:,2:])/2).mean(1) for k,v in raw.items()})
    ci = lambda v:interval(v,seed=830,nboot=4000)
    out = dict(run=run,conditions={},contrasts={},prediction={},attention={},effect_prediction={},limitations=[
        'Predictors use synthetic semantic kind metadata; this is a scientific surrogate, not a deployable method.',
        'All coefficients fitted to native attention differences, not accuracy or output gold.',
        'Final-receiver replay keeps native past query attention, but final states and normalization remain live.',
        'Same model, schema, words and label pair; no abstract algorithm or new circuit component claim.'])
    for k in raw:
        out['conditions'][k] = {m:ci(v[k]) for m,v in metrics.items()}
        out['attention'][k] = {}
        for stat in ['label_mass','within_source','within_kind','within_source_kind']:
            vals = np.array([[r['attention'][k][str(l)][stat] for l in range(run['n_layers'])] for r in rows])
            out['attention'][k][stat] = ci(vals.mean((1,2)))
    pairs = [('layout.native','D1.native','D0.native'),('R.minus_B','D0.R','D0.B'),
             ('RJ.minus_R','D0.RJ','D0.R'),('RY.minus_RJ','D0.RY','D0.RJ'),
             ('RJ.minus_source_flip','D0.RJ','D0.RJ_source_flip')]
    for name in ['B','R','RJ','RY','oracle_label','instruction']:
        pairs.append((name+'.minus_native','D0.'+name,'D0.native'))
    for name in ['B','R','RJ','RY']:
        pairs.append((name+'.minus_oracle','D0.'+name,'D0.oracle_label'))
    for name,x,y in pairs:
        out['contrasts'][name] = {m:ci(v[x]-v[y]) for m,v in metrics.items()}
    for name in ['B','R','RJ','RY']:
        out['prediction'][name] = {k:ci(np.array([r['predictive_errors'][name][k] for r in rows]))
                                  for k in rows[0]['predictive_errors'][name]}
        for label,num,den in [('mse_reduction','mse','target_energy'),
                              ('allocation_mse_reduction','allocation_mse','allocation_energy'),
                              ('weighted_mse_reduction','conditional_mass_weighted_mse','conditional_mass_weighted_energy'),
                              ('weighted_allocation_mse_reduction','conditional_mass_weighted_allocation_mse','conditional_mass_weighted_allocation_energy')]:
            values = np.array([[r['predictive_errors'][name][k] for k in [num,den]] for r in rows])
            out['prediction'][name][label] = ci(1-values[:,0]/values[:,1])
        predicted = metrics['margin']['D0.'+name]-metrics['margin']['D0.native']
        actual = metrics['margin']['D0.oracle_label']-metrics['margin']['D0.native']
        out['effect_prediction'][name] = dict(rmse=float(np.sqrt(np.square(predicted-actual).mean())),
                                              correlation=float(np.corrcoef(predicted,actual)[0,1]),
                                              mean_difference=ci(predicted-actual))
    (d/'analysis.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(dict(conditions=out['conditions'],contrasts=out['contrasts'],effect_prediction=out['effect_prediction']),indent=2))


if __name__ == '__main__':
    main()
