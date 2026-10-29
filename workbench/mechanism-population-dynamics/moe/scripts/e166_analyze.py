"""All frozen E166 contrasts, equally weighted paired55-subject intervals."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results/e166'


def cases(family):
    return [(r,p,s) for r in range(3) for p in range(2) for s in range(2 if family=='emo' else 1)]


def conditions(family):
    return [('P','donor','GainP')[r]+'_'+('full','pool')[p]+'_S'+str(1-s) for r,p,s in cases(family)]


def arrays(path):
    with np.load(path,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}


def metrics(a):
    ll=a['candidate_loglikelihood'];q=np.arange(440);gold=a['gold']
    shifted=ll-ll.max(-1,keepdims=True)
    return {'true_answer_token_NLL':-ll[:,q,gold]/a['answer_tokens'][q,gold],
            'choice_CE':np.log(np.exp(shifted).sum(-1))-shifted[:,q,gold],
            'raw_accuracy':(ll.argmax(-1)==gold).astype(float),
            'per_char_accuracy':((ll/a['answer_chars']).argmax(-1)==gold).astype(float)}


def contrasts(x,family,field):
    c=cases(family);lookup={case:x[i] for i,case in enumerate(c)}
    out={'absolute/'+name:x[i] for i,name in enumerate(conditions(family))}
    sign=-1 if field.endswith('accuracy') else 1
    for p in range(2):
        for s in range(2 if family=='emo' else 1):
            for high,low,name in [(1,0,'donor_minus_P'),(2,0,'GainP_minus_P'),(2,1,'GainP_minus_donor')]:
                out[('full','pool')[p]+'/S'+str(1-s)+'/'+name]=lookup[high,p,s]-lookup[low,p,s]
        if family=='emo':
            roles=[]
            for r,name in enumerate(('P','donor','GainP')):
                roles.append(sign*(lookup[r,p,1]-lookup[r,p,0]))
                out[('full','pool')[p]+'/S_role/'+name]=roles[-1]
            for high,low,name in [(1,0,'donor_minus_P'),(2,0,'GainP_minus_P'),(2,1,'GainP_minus_donor')]:
                out[('full','pool')[p]+'/S_role/'+name]=roles[high]-roles[low]
    for s in range(2 if family=='emo' else 1):
        damage=[]
        for r,name in enumerate(('P','donor','GainP')):
            damage.append(sign*(lookup[r,1,s]-lookup[r,0,s]))
            out['mask_damage/S'+str(1-s)+'/'+name]=damage[-1]
        for high,low,name in [(1,0,'donor_minus_P'),(2,0,'GainP_minus_P'),(2,1,'GainP_minus_donor')]:
            out['mask_damage/S'+str(1-s)+'/'+name]=damage[high]-damage[low]
    return out


def summarize(a,names,family):
    if a['candidate_loglikelihood'].shape!=(len(cases(family)),440,4) or list(a['conditions'])!=conditions(family):
        raise ValueError('Require complete predeclared condition population')
    groups=[np.flatnonzero(a['subject']==i) for i in range(55)]
    if len(names)!=55 or any(len(g)!=8 for g in groups):raise ValueError('Subject population changed')
    draws=np.random.default_rng(166002).integers(0,55,(2000,55))
    weights=np.zeros((2000,55));np.add.at(weights,(np.arange(2000)[:,None],draws),1/55)
    def stat(x):
        if not np.isfinite(x).all():raise ValueError('Nonfinite scores')
        pts=np.array([x[g].mean() for g in groups])
        return {'point':float(pts.mean()),'ci95':np.quantile(weights@pts,[.025,.975]).tolist(),
                'subjects':55,'questions':440,'resamples':2000,'seed':166002,
                'per_subject':{name:{'point':float(v),'questions':8} for name,v in zip(names,pts)}}
    out={'experiment':'E166','family':family,'status':'complete','conditions':conditions(family),
         'scope':'Frozen model/cal/input conditional; two tokenizers analyzed separately; not initialization population.',
         'definitions':{'source_changes':'High minus low; loss negative / accuracy positive better.',
                        'S_role_and_mask_damage':'Positive means damaging removal, including accuracy.'}}
    for field,x in metrics(a).items():out[field]={k:stat(v) for k,v in contrasts(x,family,field).items()}
    out['first_answer_token_KL_vs_P_full']={name:stat(a['first_answer_token_KL'][i]) for i,name in enumerate(conditions(family))}
    return out


def main():
    import e166_common as c
    plan=c.checked_plan()
    for family,spec in plan['families'].items():
        manifest=c.read(ROOT/(family+'_manifest.json'))
        if manifest['status']!='complete' or manifest['plan_sha256']!=c.sha(ROOT/'plan.json'):raise ValueError('Incomplete family')
        if c.sha(manifest['raw']['path'])!=manifest['raw']['sha256']:raise ValueError('Raw changed')
        result=summarize(arrays(manifest['raw']['path']),spec['subjects'],family)
        result.update(raw_sha256=manifest['raw']['sha256'],plan_sha256=manifest['plan_sha256'],analysis_sha256=c.sha(__file__))
        c.write(ROOT/(family+'_summary.json'),result)
    print(json.dumps({'status':'complete','families':list(plan['families'])}))


if __name__=='__main__':main()
