"""Context bootstrap of state isolation and label-history counterfactuals."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args();d=Path(a.directory)
    run=json.loads((d/'run.json').read_text())
    assert run['sanity_max_error']<=.1 and run['causal_feature_error_max']==0 and run['cross_demo_attention_mass_max']==0
    rows=[json.loads(l) for l in (d/'behavior.jsonl').read_text().splitlines()];g=np.array([r['signs'] for r in rows]);half=g.shape[1]//2
    raw={k:np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    means={k:(v*g).mean(1) for k,v in raw.items()};acc={k:(v*g>0).mean(1) for k,v in raw.items()}
    rank={k:((v[:,:half]-v[:,half:])*g[:,:half]>0).mean(1) for k,v in raw.items()}
    out={'run':run,'conditions':{},'contrasts':{}}
    for k in raw:out['conditions'][k]={'margin':interval(means[k]),'accuracy':interval(acc[k]),'paired_source_ranking':interval(rank[k])}
    rng=np.random.default_rng(680);ix=rng.integers(len(rows),size=(4000,len(rows)))
    gap=means['D1Q1']-means['D0Q0'];flip=means['D1Q1']-means['rule_flipQ1']
    out['matched_gap']={label:interval(v['D1Q1']-v['D0Q0']) for label,v in [('margin',means),('accuracy',acc),('paired_source_ranking',rank)]}
    out['native_rule_flip_effect']=interval(flip)
    for k in raw:
        if k.startswith('D1Q1.'):
            sign=-1 if '.isolated_' in k or '.flip_' in k else 1
            num=sign*(means[k]-means['D1Q1']);base='D1Q1';den=gap if '.isolated_' in k else flip
        elif k.startswith('D0Q') and '.D1_' in k:
            base=k[:4];num=means[k]-means[base];den=means['D1'+base[2:]]-means[base]
        else:continue
        item={'margin_change':interval(means[k]-means[base]),'accuracy_change':interval(acc[k]-acc[base]),
              'paired_source_ranking_change':interval(rank[k]-rank[base]),'denominator':interval(den)}
        if abs(den.mean())>.2:
            ratio=num[ix].mean(1)/den[ix].mean(1)
            item['effect_ratio']={'mean':float(num.mean()/den.mean()),'ci95':np.quantile(ratio,[.025,.975]).tolist()}
        out['contrasts'][k]=item
    (d/'analysis.json').write_text(json.dumps(out,indent=2))
    print('matched_gap',out['matched_gap']);print('full_rule_flip',out['native_rule_flip_effect'])
    for k in ['D1Q1.isolated_prefix_key','D1Q1.isolated_prefix_value','D1Q1.isolated_prefix_kv',
              'D1Q1.flip_prefix_key','D1Q1.flip_prefix_value','D1Q1.flip_prefix_kv','D0Q1.D1_prefix_kv','D0Q1.D1_prefix_tag_label_kv']:
        print(k,out['contrasts'][k])

if __name__=='__main__':main()
