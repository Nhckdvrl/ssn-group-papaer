"""Paired bootstrap: common/centered context corrections, no selected sites."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args();d=Path(a.directory);run=json.loads((d/'run.json').read_text())
    assert run['sanity_max_error']<=.1 and run['nonlabel_flip_feature_error_max']==0 and run['forbidden_attention_mass_max']==0 and run['fixedQ_common_relative_logit_spread_max']<=.02
    rows=[json.loads(l) for l in (d/'behavior.jsonl').read_text().splitlines()];g=np.array([r['signs'] for r in rows]);half=g.shape[1]//2
    raw={k:np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    means={k:(v*g).mean(1) for k,v in raw.items()};acc={k:(v*g>0).mean(1) for k,v in raw.items()}
    rank={k:((v[:,:half]-v[:,half:])*g[:,:half]>0).mean(1) for k,v in raw.items()}
    out={'run':run,'conditions':{},'contrasts':{}}
    for k in raw:
        item={'margin':interval(means[k]),'accuracy':interval(acc[k]),'paired_source_ranking':interval(rank[k])}
        if k in rows[0]['attention']:
            nlayer=len(rows[0]['attention'][k]);item['attention']={metric:[interval(np.array([r['attention'][k][str(l)][metric] for r in rows]).mean(1)) for l in range(nlayer)] for metric in ['mass','within_source']}
        out['conditions'][k]=item
    den=means['blind']-means['isolated'];out['full_blind_minus_isolated']=interval(den)
    rng=np.random.default_rng(700);ix=rng.integers(len(rows),size=(4000,len(rows)))
    for k in ['common','centered','both','norm','negative_common','blind']:
        result={name:{label:interval(v[k]-v[base]) for label,v in [('margin',means),('accuracy',acc),('paired_source_ranking',rank)]} for name,base in [('minus_isolated','isolated'),('minus_native','D1Q1')]}
        if abs(den.mean())>.2:
            num=means[k]-means['isolated'];ratio=num[ix].mean(1)/den[ix].mean(1)
            result['effect_fraction']={'mean':float(num.mean()/den.mean()),'ci95':np.quantile(ratio,[.025,.975]).tolist()}
        out['contrasts'][k]=result
    (d/'analysis.json').write_text(json.dumps(out,indent=2));print('full_effect',out['full_blind_minus_isolated'])
    for k in ['common','centered','norm','negative_common']:print(k,out['contrasts'][k])

if __name__=='__main__':main()
