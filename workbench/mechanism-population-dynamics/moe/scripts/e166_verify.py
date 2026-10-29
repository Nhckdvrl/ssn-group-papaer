"""Independent raw logaddexp scoring, explicit condition vectors and draw lookup."""
import json
from pathlib import Path
import numpy as np


def verify(a,summary,names,family):
    shared=family=='emo';ns=2 if shared else 1;n=12 if shared else 6
    labels=[r+'_'+p+'_S'+s for r in ('P','donor','GainP') for p in ('full','pool') for s in (('1','0') if shared else ('1',))]
    assert list(a['conditions'])==summary['conditions']==labels
    ll=np.asarray(a['candidate_loglikelihood'],dtype=np.float64);assert ll.shape==(n,440,4) and np.isfinite(ll).all()
    q=np.arange(440);correct=ll[:,q,a['gold']]
    fields={'true_answer_token_NLL':-correct/a['answer_tokens'][q,a['gold']],
            'choice_CE':np.logaddexp.reduce(ll,axis=2)-correct,
            'raw_accuracy':(ll.argmax(2)==a['gold']).astype(float),
            'per_char_accuracy':((ll/a['answer_chars']).argmax(2)==a['gold']).astype(float)}
    def row(r,p,s):return np.eye(n)[(r*2+p)*ns+s]
    def vectors(field):
        sign=-1 if field.endswith('accuracy') else 1
        out={'absolute/'+label:np.eye(n)[i] for i,label in enumerate(labels)}
        for p,policy in enumerate(('full','pool')):
            for s in range(ns):
                for hi,lo,name in [(1,0,'donor_minus_P'),(2,0,'GainP_minus_P'),(2,1,'GainP_minus_donor')]:
                    out[policy+'/S'+str(1-s)+'/'+name]=row(hi,p,s)-row(lo,p,s)
            if shared:
                for r,name in enumerate(('P','donor','GainP')):
                    out[policy+'/S_role/'+name]=sign*(row(r,p,1)-row(r,p,0))
                for hi,lo,name in [(1,0,'donor_minus_P'),(2,0,'GainP_minus_P'),(2,1,'GainP_minus_donor')]:
                    out[policy+'/S_role/'+name]=sign*(row(hi,p,1)-row(hi,p,0)-row(lo,p,1)+row(lo,p,0))
        for s in range(ns):
            for r,name in enumerate(('P','donor','GainP')):out['mask_damage/S'+str(1-s)+'/'+name]=sign*(row(r,1,s)-row(r,0,s))
            for hi,lo,name in [(1,0,'donor_minus_P'),(2,0,'GainP_minus_P'),(2,1,'GainP_minus_donor')]:
                out['mask_damage/S'+str(1-s)+'/'+name]=sign*(row(hi,1,s)-row(hi,0,s)-row(lo,1,s)+row(lo,0,s))
        return out
    groups=[np.flatnonzero(a['subject']==i) for i in range(55)]
    assert len(names)==55 and all(len(g)==8 for g in groups)
    draws=np.random.default_rng(166002).integers(0,55,(2000,55))
    numeric=0;meta=5;maximum=0.
    def check(record,x):
        nonlocal numeric,meta,maximum
        values=np.array([x[group].mean() for group in groups])
        expected=np.r_[values.mean(),np.quantile(values[draws].mean(1),[.025,.975])]
        actual=np.r_[record['point'],record['ci95']]
        delta=float(abs(expected-actual).max());assert delta<1e-11
        maximum=max(maximum,delta);numeric+=3
        assert (record['subjects'],record['questions'],record['resamples'],record['seed'])==(55,440,2000,166002);meta+=4
        assert set(record['per_subject'])==set(names);meta+=1
        for name,value in zip(names,values):
            delta=abs(record['per_subject'][name]['point']-value);assert delta<1e-11
            maximum=max(maximum,float(delta));numeric+=1
            assert record['per_subject'][name]['questions']==8;meta+=1
    for field,x in fields.items():
        cs=vectors(field);assert set(cs)==set(summary[field]);meta+=1
        for name,weights in cs.items():check(summary[field][name],sum(weights[i]*x[i] for i in np.flatnonzero(weights)))
    assert a['first_answer_token_KL'].shape==(n,440) and a['trace_hashes'].shape==(2,440)
    for i,label in enumerate(labels):check(summary['first_answer_token_KL_vs_P_full'][label],a['first_answer_token_KL'][i])
    return {'status':'passed','numeric_comparisons':numeric,'metadata_comparisons':meta,
            'maximum_absolute_difference':maximum,'implementation':'Independent logaddexp and condition coefficient vectors, direct subject draw lookup.',
            'scope':'KL scalar aggregation only; original vocabulary arithmetic checked by exact old raw guards.'}


def main():
    import e166_common as c
    from e166_analyze import arrays
    plan=c.checked_plan();results={}
    for family,spec in plan['families'].items():
        m=c.read(c.ROOT/(family+'_manifest.json'));s=c.read(c.ROOT/(family+'_summary.json'))
        assert m['status']=='complete' and c.sha(m['raw']['path'])==m['raw']['sha256']
        result=verify(arrays(m['raw']['path']),s,spec['subjects'],family)
        cal=arrays(m['calibration']['path']);assert c.sha(m['calibration']['path'])==m['calibration']['sha256']
        assert np.array_equal(cal['gain'],np.sqrt(cal['donor_energy']/cal['P_energy']).astype(np.float32))
        assert np.isfinite(cal['cosine']).all() and len(cal['gain'])==16
        result.update(raw_sha256=m['raw']['sha256'],summary_sha256=c.sha(c.ROOT/(family+'_summary.json')),
                      calibration_sha256=m['calibration']['sha256'])
        results[family]=result
    c.write(c.ROOT/'independent_audit.json',{'status':'passed','families':results,
            'plan_sha256':c.sha(c.ROOT/'plan.json'),'verify_sha256':c.sha(__file__)})
    print(json.dumps(results))


if __name__=='__main__':main()
