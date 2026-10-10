"""Separate seen lookup, interpolation and extrapolation, including both rules."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def ci(x):return interval(x,seed=770,nboot=4000)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args();d=Path(a.directory)
    run=json.loads((d/'run.json').read_text());assert run['sanity_max_error']<=.1
    rows=[json.loads(l) for l in (d/'behavior.jsonl').read_text().splitlines()];n=len(rows);assert n==run['args']['n']
    out={'run':run,'conditions':{},'contrasts':{},'source_responses':{},'limitations':['Familiar operator recognition, not arbitrary function learning.','Candidate choices, not native free-generation accuracy.','Single context has shorter length; direct rules add information.']}
    metrics={};ld={};groups={'seen':[2,7],'interpolation':[3,4,5,6],'extrapolation':[0,1,8,9]}
    ni=np.arange(n)[:,None];qi=np.arange(20)[None]
    for k in rows[0]['scores']:
        v=np.array([r['scores'][k] for r in rows]);assert v.shape==(n,20,10) and np.isfinite(v).all()
        gold=np.array([r['gold'][k] for r in rows]);correct=v[ni,qi,gold];other=v.copy();other[ni,qi,gold]=-np.inf
        margin=(correct-other.max(-1)).reshape(n,2,10);pred=v.argmax(-1).reshape(n,2,10)
        ts=np.array([[1 if g[0]==0 else -1,1 if g[10]==0 else -1] for g in gold])
        # Rule identity is unambiguously read at input zero from the oracle.
        metrics[k]={};out['conditions'][k]={}
        for name,xs in groups.items():
            vals={'accuracy':(margin[:,:,xs]>0).mean((1,2)),'margin':margin[:,:,xs].mean((1,2)),
                  'demo_word_choice':np.isin(pred[:,:,xs],[2,7]).mean((1,2))}
            metrics[k][name]=vals;out['conditions'][k][name]={stat:ci(x) for stat,x in vals.items()}
            for theta,rule in [(1,'identity'),(-1,'complement')]:
                selected=(ts==theta)
                # Both sources remain opposite even after only one is flipped?
                # Counterfactuals may make them equal; guard missing subgroup.
                counts=selected.sum(1)
                if np.all(counts>0):
                    acc=((margin[:,:,xs]>0).mean(-1)*selected).sum(1)/counts
                    out['conditions'][k][name][rule+'_accuracy']=ci(acc)
        ld[k]=(v.reshape(n,2,10,10)[:,:,np.arange(10),np.arange(10)]-
               v.reshape(n,2,10,10)[:,:,np.arange(10),9-np.arange(10)])
    modes=['mixed','mixed_instruction','single','single_instruction','direct']
    for mode in modes:
        for name,xs in groups.items():
            for s,owner in [(0,'owned_a'),(1,'owned_b')]:
                theta=np.array([r['theta'][s] for r in rows])
                delta=(ld[mode+'.base'][:,s,xs]-ld[mode+'.'+owner][:,s,xs]).mean(-1)*theta
                out['source_responses'][mode+'.'+name+'.'+owner]=ci(delta)
    for label,x,y in [('single_minus_mixed','single','mixed'),('instruction','mixed_instruction','mixed'),('direct_minus_mixed','direct','mixed')]:
        out['contrasts'][label]={name:{stat:ci(metrics[x+'.base'][name][stat]-metrics[y+'.base'][name][stat]) for stat in ['accuracy','margin']} for name in groups}
    (d/'analysis.json').write_text(json.dumps(out,indent=2))
    print({k:v for k,v in out['conditions'].items() if k.endswith('.base')});print(out['contrasts'])


if __name__=='__main__':main()
