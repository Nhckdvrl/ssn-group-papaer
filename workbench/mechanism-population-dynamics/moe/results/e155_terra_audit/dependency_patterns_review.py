"""Reproduce the independent E155 dependency-pattern audit from raw arrays."""
import json
from pathlib import Path
import numpy as np

base=Path('/home/xiang/mechpop_cache/e155_native_task_branch_necessity')
root=Path(__file__).resolve().parent
raw=[np.load(base/f'scores_{s}.npz') for s in 'PAB']
gold=raw[0]['gold']; sub=raw[0]['subject']
pred=np.stack([a['candidate_loglikelihood'].argmax(-1) for a in raw])
correct=pred==gold[None,None,:]; mask=correct[:,0].all(axis=0)
# bit 0 = D, bit 1 = D+R, bit 2 = D+S; independent of author numbering.
codes=correct[:,3].astype(int)+2*correct[:,2]+4*correct[:,1]
groups=[np.flatnonzero(mask & (sub==i)) for i in (0,1)]
rng=np.random.default_rng(155201)
draws=[g[rng.integers(0,len(g),(1000,len(g)))] for g in groups]

def stats(x):
    x=np.asarray(x,dtype=float)
    b=np.mean([x[d].mean(axis=1) for d in draws],axis=0)
    return {'point':float(np.mean([x[g].mean() for g in groups])),
            'ci95':np.quantile(b,[.025,.975]).tolist(),
            'counts':[int(x[g].sum()) for g in groups]}

r={'definitions':{'code':'D + 2*(D+R) + 4*(D+S); D=all_moe_zero, D+R=shared_zero, D+S=routed_zero',
                  'selection':'P/A/B native correct; no intervention outcome used',
                  'ci':'paired within-subject bootstrap seed 155201; 1000 subject-major draws, equal-subject macro'},
   'common_counts':[len(g) for g in groups], 'patterns':{},'transitions':{},'differences':{}}
for i,s in enumerate('PAB'):
    r['patterns'][s]={str(k):stats(codes[i]==k) for k in range(8)}
for i,j,label in [(0,1,'P_to_A'),(0,2,'P_to_B'),(1,2,'A_to_B')]:
    r['transitions'][label]={f'{k}_to_{l}':stats((codes[i]==k)&(codes[j]==l)) for k in range(8) for l in range(8)}
    r['differences'][label]={str(k):stats((codes[j]==k).astype(float)-(codes[i]==k).astype(float)) for k in range(8)}
# Save raw-first calculation before opening the author's table.
p=root/'dependency_patterns_review.json'
p.write_text(json.dumps(r,indent=2)+'\n')
a=json.loads((root.parent/'e155/dependency_patterns_posthoc.json').read_text())
mp=[0,4,2,6,1,5,3,7]; errs=[]; count_errors=[]
def compare(x,y):
    errs.extend([abs(x['point']-y['point']),*[abs(u-v) for u,v in zip(x['ci95'],y['question_ci95'])]])
for s in 'PAB':
    for k in range(8):
        x=r['patterns'][s][str(mp[k])]; y=a['sources'][s]['macro_pattern_proportions'][str(k)]
        compare(x,y)
        for j in range(2): count_errors.append(abs(x['counts'][j]-a['sources'][s]['subject_pattern_counts'][str(j)][k]))
for direct,label in [('P_to_A','A_minus_P'),('P_to_B','B_minus_P'),('A_to_B','B_minus_A')]:
    for k in range(8):
        compare(r['differences'][direct][str(mp[k])],a['paired_differences'][label][str(k)])
        for l in range(8):
            x=r['transitions'][direct][f'{mp[k]}_to_{mp[l]}']['counts']
            y=a['transitions'][direct]['rows_before_columns_after'][k][l]
            count_errors.append(abs(sum(x)-y))
            for j in range(2): count_errors.append(abs(x[j]-a['transitions'][direct]['subjects'][str(j)][k][l]))
r['author_comparison']={'author_to_independent_code':mp,'max_point_or_ci_absolute_error':max(errs),
                        'max_transition_or_subject_count_error':max(count_errors),
                        'CI_scope':'24 pattern proportions and 24 paired differences; author transition output supplies counts rather than CIs, independent transition CIs are retained here'}
p.write_text(json.dumps(r,indent=2)+'\n')
print(r['author_comparison'])
