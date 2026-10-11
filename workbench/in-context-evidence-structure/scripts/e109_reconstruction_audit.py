"""Frozen identity prediction of functional namespace intervention effects.
No fitted coefficients; resampling units are contexts, not scores.
"""
import argparse,json
from pathlib import Path
import numpy as np


def summarize(target,pred):
    n=target.shape[0];rng=np.random.default_rng(109910)
    idx=rng.integers(n,size=(10000,n))
    error=((target-pred)**2).reshape(n,-1).mean(1)
    zero=(target**2).reshape(n,-1).mean(1)
    t=target.reshape(n,-1);y=pred.reshape(n,-1)
    width=t.shape[1]
    moments=np.stack([t.sum(1),y.sum(1),(t*t).sum(1),(y*y).sum(1),(t*y).sum(1)],1)
    def correlation(m):
        count=n*width
        return (m[...,4]-m[...,0]*m[...,1]/count)/np.sqrt(
            (m[...,2]-m[...,0]**2/count)*(m[...,3]-m[...,1]**2/count))
    boot_corr=correlation(moments[idx].sum(1))
    return {'rmse':float(np.sqrt(error.mean())),
        'rmse_ci95':np.quantile(np.sqrt(error[idx].mean(1)),[.025,.975]).tolist(),
        'correlation':float(correlation(moments.sum(0))),
        'correlation_ci95':np.quantile(boot_corr,[.025,.975]).tolist(),
        'zero_rmse':float(np.sqrt(zero.mean())),'n_contexts':n,'n_scores':int(target.size)}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True)
    a=ap.parse_args();p=Path(a.out)
    protocol=json.loads(Path('results/e109/frozen_reconstruction_protocol.json').read_text())
    assert protocol['fit'] is False and protocol['coefficient']==1
    rows=[json.loads(x) for x in (p/'behavior.jsonl').read_text().splitlines()]
    z={k:np.array([r['conditions'][k]['z'] for r in rows]) for k in rows[0]['conditions']}
    base=np.stack([z[w+'_shared_gate'] for w in ['aligned','conflict']],1)
    target=np.stack([z[w+'_far_label'] for w in ['aligned','conflict']],1)-base
    out={'protocol':'results/e109/frozen_reconstruction_protocol.json','coefficient':1,'fit':False,'models':{}}
    for mode in protocol['predictors']:
        pred=np.stack([z[w+'_'+mode] for w in ['aligned','conflict']],1)-base
        raw=summarize(target,pred)
        double=summarize(target[:,0]-target[:,1],pred[:,0]-pred[:,1])
        out['models'][mode]={'raw_namespace':raw,'rule_double_contrast':double}
        print(mode,'double',double,flush=True)
    (p/'reconstruction_audit.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()
