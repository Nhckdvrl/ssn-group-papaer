"""Compare label-blind contextualization to isolation without selecting sites."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args();d=Path(a.directory)
    run=json.loads((d/'run.json').read_text())
    assert run['sanity_max_error']<=.1 and run['nonlabel_flip_feature_error_max']==0 and run['label_forbidden_attention_mass_max']==0 and run['cross_demo_attention_mass_max']==0
    rows=[json.loads(l) for l in (d/'behavior.jsonl').read_text().splitlines()];g=np.array([r['signs'] for r in rows]);half=g.shape[1]//2
    raw={k:np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    means={k:(v*g).mean(1) for k,v in raw.items()};acc={k:(v*g>0).mean(1) for k,v in raw.items()}
    rank={k:((v[:,:half]-v[:,half:])*g[:,:half]>0).mean(1) for k,v in raw.items()}
    out={'run':run,'conditions':{},'comparisons':{}}
    for k in raw:out['conditions'][k]={'margin':interval(means[k]),'accuracy':interval(acc[k]),'paired_source_ranking':interval(rank[k])}
    rng=np.random.default_rng(690);ix=rng.integers(len(rows),size=(4000,len(rows)))
    out['matched_gap']={label:interval(v['D1Q1']-v['D0Q0']) for label,v in [('margin',means),('accuracy',acc),('paired_source_ranking',rank)]}
    for b in [k for k in raw if k.startswith('blind.')]:
        iso=b.replace('blind.','isolated.',1)
        result={}
        for name,x,y in [('blind_minus_native',b,'D1Q1'),('isolated_minus_native',iso,'D1Q1'),('blind_minus_isolated',b,iso)]:
            result[name]={label:interval(v[x]-v[y]) for label,v in [('margin',means),('accuracy',acc),('paired_source_ranking',rank)]}
        den=means['D1Q1']-means[iso];num=means['D1Q1']-means[b]
        if abs(den.mean())>.2:
            ratio=num[ix].mean(1)/den[ix].mean(1)
            result['blind_loss_fraction_of_isolation_loss']={'mean':float(num.mean()/den.mean()),'ci95':np.quantile(ratio,[.025,.975]).tolist()}
        out['comparisons'][b]=result
    (d/'analysis.json').write_text(json.dumps(out,indent=2))
    print('matched_gap',out['matched_gap'])
    for k in ['blind.prefix.key','blind.prefix.value','blind.prefix.kv','blind.source_tag_prefix.kv','blind.all_nonlabel.kv']:
        print(k,out['comparisons'][k])

if __name__=='__main__':main()
