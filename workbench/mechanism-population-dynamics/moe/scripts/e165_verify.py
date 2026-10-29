"""Independent E165 raw-score formulas, coefficient vectors and draw lookup."""
import itertools
import json
from pathlib import Path
import hashlib

import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'results/e165'


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def coefficients(field):
    eye = np.eye(26); sign = -1 if field.endswith('accuracy') else 1
    names = ['D_'+d+'_G_'+g+'_E_'+e+'_'+p for p in ('full','P16')
             for d,g,e in itertools.product('PA',repeat=3)]
    names += ['E_'+e+'_route_'+g+'_'+p for p in ('full','P16') for e,g in [('P','A'),('A','P')]]
    names += ['native_'+r+'_random'+str(k) for r in 'PA' for k in range(3)]
    out = {'absolute/'+name: eye[i] for i,name in enumerate(names)}
    def index(case): return 4*case[0]+2*case[1]+case[2]
    def two_way(rows, prefix):
        pp,pa,ap,aa = rows
        return {prefix+'natural_A_minus_P':aa-pp,
                prefix+'E_A_minus_P_at_route_P':ap-pp,
                prefix+'E_A_minus_P_at_route_A':aa-pa,
                prefix+'route_A_minus_P_at_E_P':pa-pp,
                prefix+'route_A_minus_P_at_E_A':aa-ap,
                prefix+'interaction':aa-ap-pa+pp}
    route_rows = []
    for policy,p in enumerate(('full','P16')):
        offset=policy*8
        for axis,label in enumerate('DGE'):
            for j,k in itertools.product(range(2),repeat=2):
                lo=[j,k];lo.insert(axis,0);hi=lo.copy();hi[axis]=1
                out[p+'/'+label+'_A_minus_P_fixed_'+str(j)+str(k)] = eye[offset+index(hi)]-eye[offset+index(lo)]
        for first,second in itertools.combinations(range(3),2):
            other=3-first-second
            for fixed in (0,1):
                weights=np.zeros(26)
                for d,g,e in itertools.product(range(2),repeat=3):
                    case=(d,g,e)
                    if case[other]==fixed:
                        weights[offset+index(case)]=1 if case[first]==case[second] else -1
                out[p+'/'+'DGE'[first]+'_x_'+'DGE'[second]+'_other_'+str(fixed)]=weights
        weights=np.zeros(26);weights[[offset+3,offset+4]]=sign*.5;weights[[offset,offset+7]]=-sign*.5
        out[p+'/D_x_MoE_matching_cost']=weights
        weights=np.zeros(26)
        for case in itertools.product(range(2),repeat=3):
            weights[offset+index(case)]=1 if sum(case)%2 else -1
        out[p+'/three_way']=weights
        rows=[eye[offset],eye[16+2*policy],eye[17+2*policy],eye[offset+1]]
        route_rows.append(rows);out.update(two_way(rows,p+'/actual_route/'))
    for case in itertools.product(range(2),repeat=3):
        i=index(case);out['mask_damage/'+''.join(map(str,case))]=sign*(eye[i+8]-eye[i])
    out.update(two_way([sign*(b-a) for a,b in zip(*route_rows)],'mask_damage/actual_route/'))
    for name,i,start in [('P',0,20),('A',7,23)]:
        random=eye[start:start+3].sum(0)/3
        out['native/'+name+'/selected_damage']=sign*(eye[i+8]-eye[i])
        out['native/'+name+'/random_mean_damage']=sign*(random-eye[i])
        out['native/'+name+'/random_minus_selected_value']=sign*(random-eye[i+8])
    out['native/A_minus_P_full']=eye[7]-eye[0]
    out['native/A_minus_P_selected']=eye[15]-eye[8]
    out['native/A_minus_P_selected_damage']=sign*(eye[15]-eye[7]-eye[8]+eye[0])
    return names,out


def independent_scores(a):
    ll=a['candidate_loglikelihood'].astype(np.float64);gold=a['gold'];q=np.arange(440)
    correct=ll[:,q,gold]
    return {'raw_accuracy':(np.argmax(ll,axis=2)==gold).astype(float),
            'per_char_accuracy':(np.argmax(ll/a['answer_chars'],axis=2)==gold).astype(float),
            'choice_CE':np.logaddexp.reduce(ll,axis=2)-correct,
            'true_answer_token_NLL':-correct/a['answer_tokens'][q,gold]}


def verify(a, summary, names):
    names_expected,_=coefficients('choice_CE')
    assert list(a['conditions'])==names_expected==summary['conditions']
    assert a['candidate_loglikelihood'].shape==(26,440,4) and np.isfinite(a['candidate_loglikelihood']).all()
    assert a['natural_LL'].shape==(2,2,440,4)
    for p in range(2):
        for m in range(2):
            assert np.array_equal(a['candidate_loglikelihood'][8*p+7*m],a['natural_LL'][m,p])
    assert np.array_equal(a['gate0_hashes'][:,0],a['gate0_hashes'][:,1])
    assert a['trace_hashes'].shape==(2,2,440) and all(len(v)==64 for v in a['trace_hashes'].flat)
    groups=[np.flatnonzero(a['subject']==i) for i in range(55)]
    assert len(names)==55 and all(len(g)==8 for g in groups)
    draws=np.random.default_rng(165002).integers(0,55,(2000,55))
    numeric=0;metadata=9;maximum=0.
    def check(row,x):
        nonlocal numeric,metadata,maximum
        subject=np.array([np.mean(x[g]) for g in groups])
        expected=np.r_[subject.mean(),np.quantile(subject[draws].mean(axis=1),[.025,.975])]
        difference=np.max(np.abs(expected-np.r_[row['point'],row['ci95']]))
        assert difference<1e-11,difference
        maximum=max(maximum,float(difference));numeric+=3
        assert row['subjects']==55 and row['questions']==440 and row['resamples']==2000 and row['seed']==165002
        metadata+=4
        assert set(row['per_subject'])==set(names)
        for i,name in enumerate(names):
            part=row['per_subject'][name];delta=abs(part['point']-subject[i]);assert delta<1e-11
            maximum=max(maximum,float(delta));numeric+=1;assert part['questions']==8;metadata+=1
    for field,values in independent_scores(a).items():
        _,vectors=coefficients(field);assert set(vectors)==set(summary[field]);metadata+=1
        for key,weights in vectors.items():
            # Explicit nonzero weighted sum, independent of author's contrast arrays.
            x=sum(weights[i]*values[i] for i in np.flatnonzero(weights))
            check(summary[field][key],x)
    for i,name in enumerate(names_expected):
        check(summary['first_answer_token_KL_vs_P_full'][name],a['first_answer_token_KL'][i])
    return {'status':'passed','numeric_comparisons':numeric,'metadata_comparisons':metadata,
            'maximum_absolute_difference':maximum,
            'independent_implementation':'Logaddexp candidate scoring; explicit26-condition coefficient vectors; subject draw lookup.',
            'scope':'KL scalar aggregation checked; vocabulary distribution validated by native interface and original numerical program, not reconstructed here.'}


def main():
    manifest=json.loads((ROOT/'manifest.json').read_text());plan=json.loads((ROOT/'plan.json').read_text())
    assert manifest['status']=='complete' and sha(manifest['raw']['path'])==manifest['raw']['sha256']
    assert sha(ROOT/'plan.json')==manifest['plan_sha256']
    with np.load(manifest['raw']['path'],allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
    summary=json.loads((ROOT/'summary.json').read_text())
    result=verify(a,summary,plan['subjects'])
    result.update(raw_sha256=manifest['raw']['sha256'],plan_sha256=manifest['plan_sha256'],
                  summary_sha256=sha(ROOT/'summary.json'),source_sha256=sha(__file__))
    (ROOT/'independent_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
