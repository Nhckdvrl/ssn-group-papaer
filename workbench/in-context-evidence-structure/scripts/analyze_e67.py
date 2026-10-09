"""Preregistered native factorial/transfer reads; context bootstrap."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args();d=Path(a.directory)
    run=json.loads((d/'run.json').read_text());assert run['sanity_max_error']<=.1
    rows=[json.loads(l) for l in (d/'behavior.jsonl').read_text().splitlines()]
    g=np.array([r['signs'] for r in rows]);half=g.shape[1]//2
    raw={k:np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    means={k:(v*g).mean(1) for k,v in raw.items()};acc={k:(v*g>0).mean(1) for k,v in raw.items()}
    ranks={k:((v[:,:half]-v[:,half:])*g[:,:half]>0).mean(1) for k,v in raw.items()}
    att={};out={'run':run,'conditions':{},'contrasts':{},'transfers':{}}
    for k,v in raw.items():
        item={'margin':interval(means[k]),'accuracy':interval(acc[k]),'paired_source_ranking':interval(ranks[k])}
        if k in rows[0]['attention']:
            av=np.array([[r['attention'][k][str(l)]['requested_source'] for l in range(len(r['attention'][k]))] for r in rows])
            att[k]=av.mean((1,2));item['requested_source_label_attention']=interval(att[k]);item['attention_by_layer']=[interval(av[:,l].mean(1)) for l in range(av.shape[1])]
        if k in rows[0]['prefix']:
            item['native_prefix_candidate_accuracy']=interval(np.array([r['prefix'][k]['candidate_accuracy'] for r in rows]).mean(1))
            item['native_prefix_candidate_probability']=interval(np.array([r['prefix'][k]['candidate_probability'] for r in rows]).mean(1))
        out['conditions'][k]=item
    for name,x,y in [('matched_gap','D1Q1','D0Q0'),('demo_effect_at_Q0','D1Q0','D0Q0'),('demo_effect_at_Q1','D1Q1','D0Q1'),('query_effect_at_D0','D0Q1','D0Q0'),('query_effect_at_D1','D1Q1','D1Q0')]:
        out['contrasts'][name]={'margin':interval(means[x]-means[y]),'accuracy':interval(acc[x]-acc[y]),'paired_source_ranking':interval(ranks[x]-ranks[y])}
    out['contrasts']['DxQ_interaction']={label:interval(values['D1Q1']-values['D1Q0']-values['D0Q1']+values['D0Q0']) for label,values in [('margin',means),('accuracy',acc),('paired_source_ranking',ranks)]}
    rng=np.random.default_rng(670);ix=rng.integers(len(rows),size=(4000,len(rows)))
    for recipient,donor in [(0,1),(1,0)]:
        for q in (0,1):
            base=f'D{recipient}Q{q}';target=f'D{donor}Q{q}';gap=means[target]-means[base]
            for channel in ['key','value','kv']:
                k=base+'.label_'+channel;num=means[k]-means[base]
                item={'margin_minus_base':interval(num),'accuracy_minus_base':interval(acc[k]-acc[base]),'paired_source_ranking_minus_base':interval(ranks[k]-ranks[base]),'attention_minus_base':interval(att[k]-att[base]),'natural_donor_gap':interval(gap)}
                if abs(gap.mean())>.2:
                    ratio=num[ix].mean(1)/gap[ix].mean(1)
                    item['fraction_of_format_gap']={'mean':float(num.mean()/gap.mean()),'ci95':np.quantile(ratio,[.025,.975]).tolist()}
                out['transfers'][k]=item
    (d/'analysis.json').write_text(json.dumps(out,indent=2))
    for k in ['D0Q0','D0Q1','D1Q0','D1Q1']:
        v=out['conditions'][k];print(k,{x:v[x] for x in ['margin','accuracy','paired_source_ranking','requested_source_label_attention','native_prefix_candidate_accuracy']})
    print('contrasts',out['contrasts'])
    print('transfer_Q1',{k:v for k,v in out['transfers'].items() if k.startswith('D0Q1')})

if __name__=='__main__':main()
