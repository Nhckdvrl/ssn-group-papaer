"""E157 independent CPU recomputation; no model calls or author analysis imports."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

GROUPS=('Bio','Math')
DONORS=('A','B')
SHARED=('P','A','B')
SUBJECTS=('high_school_biology','high_school_mathematics')
SEED=157001
REPO=Path(__file__).resolve().parents[1]


def sha(path):
    with open(path,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def measures(ll, gold, tokens, chars, kl):
    n=gold.size; q=np.arange(n)
    ll=np.asarray(ll,dtype=np.float64)
    maxll=ll.max(-1)
    log_z=maxll+np.log(np.exp(ll-maxll[...,None]).sum(-1))
    true=ll[...,q,gold]
    return {'raw_accuracy':(ll.argmax(-1)==gold).astype(float),
            'per_char_accuracy':((ll/chars).argmax(-1)==gold).astype(float),
            'choice_CE':log_z-true,'true_answer_token_NLL':-true/tokens[q,gold],
            'first_answer_token_KL_vs_P':np.asarray(kl,dtype=np.float64)}


def paired_stats(x,subject,selection):
    """Subject-major paired question resampling, reset seed for each statistic."""
    rng=np.random.default_rng(SEED); draws=[]; means=[]; per={}
    for i,name in enumerate(SUBJECTS):
        values=np.asarray(x,dtype=np.float64)[selection & (subject==i)]
        if not len(values): continue
        ix=rng.integers(0,len(values),size=(1000,len(values)))
        boot=values[ix].mean(1); draws.append(boot); means.append(values.mean())
        per[name]={'point':float(values.mean()),'question_ci95':np.quantile(boot,[.025,.975]).tolist(),'questions':len(values)}
    if not draws: raise ValueError('empty selection')
    return {'point':float(np.mean(means)),'question_ci95':np.quantile(np.mean(draws,axis=0),[.025,.975]).tolist(),
            'per_subject':per,'question_count':int(selection.sum()),'bootstrap_seed':SEED}


def pairing(x,accuracy=False):
    # axes donor A/B and shared P/A/B; no P/P.
    difference=((x[0,2]-x[0,1])+(x[1,1]-x[1,2]))/2
    return -difference if accuracy else difference


def compose(groups,subject,mode):
    # indices group Bio/Math per question; fixed-group keeps entire question vector.
    if mode=='Bio':return groups[0]
    if mode=='Math':return groups[1]
    choose=subject if mode=='on_domain' else 1-subject
    return np.stack([groups[int(i),...,q] for q,i in enumerate(choose)],axis=-1)


def recompute(new,old):
    shapes={'candidate_loglikelihood':(2,2,3,128,4),'first_answer_token_KL_vs_P':(2,2,3,128),
      'native_candidate_loglikelihood':(3,128,4),'native_first_answer_token_KL_vs_P':(3,128),
      'gold':(128,),'subject':(128,),'answer_tokens':(128,4),'answer_chars':(128,4),'common_success':(128,),
      'group_names':(2,),'donor_names':(2,),'shared_names':(3,)}
    for key,shape in shapes.items():
        if key not in new or new[key].shape!=shape:raise ValueError(f'wrong/missing {key}, expected {shape}')
    for key,names in [('group_names',GROUPS),('donor_names',DONORS),('shared_names',SHARED)]:
        if tuple(new[key])!=names:raise ValueError(f'wrong {key}')
    g,sub,t,c=(new[k] for k in ('gold','subject','answer_tokens','answer_chars'))
    if any(x.dtype.kind not in 'iu' for x in (g,sub,t,c)) or np.any((g<0)|(g>3)) or np.any(t<=0) or np.any(c<=0):
        raise ValueError('invalid labels or lengths')
    if np.bincount(sub,minlength=2).tolist()!=[64,64]:raise ValueError('unexpected subject counts')
    common=new['common_success']
    if common.dtype.kind!='b' or [int((common&(sub==i)).sum()) for i in range(2)]!=[36,8]:raise ValueError('common subset counts')
    for key in ('gold','subject','answer_tokens','answer_chars','common_success'):
        if not np.array_equal(new[key],old[key]):raise ValueError('E156 input mismatch: '+key)
    if tuple(old['source_names'])!=('P','A','B') or tuple(old['policies'])!=('full','receiverP32'):
        raise ValueError('old source/policy order mismatch')
    if not np.array_equal(new['native_candidate_loglikelihood'],old['native_candidate_loglikelihood'][:,0]):raise ValueError('native LL replay differs')
    if not np.array_equal(new['native_first_answer_token_KL_vs_P'],old['native_first_answer_token_KL_vs_P'][:,0]):raise ValueError('native KL replay differs')
    if not np.array_equal(common,np.all(new['native_candidate_loglikelihood'].argmax(-1)==g,axis=0)):
        raise ValueError('common subset differs from native correct answers')
    for key in ('candidate_loglikelihood','first_answer_token_KL_vs_P','native_candidate_loglikelihood','native_first_answer_token_KL_vs_P'):
        if not np.isfinite(new[key]).all():raise ValueError('nonfinite '+key)
    fresh=measures(new['candidate_loglikelihood'],g,t,c,new['first_answer_token_KL_vs_P'])
    native=measures(new['native_candidate_loglikelihood'],g,t,c,new['native_first_answer_token_KL_vs_P'])
    old_full=measures(old['candidate_loglikelihood'][:,:,0],g,t,c,old['first_answer_token_KL_vs_P'][:,:,0])
    old_mask=measures(old['candidate_loglikelihood'][:,:,1],g,t,c,old['first_answer_token_KL_vs_P'][:,:,1])
    output={'scopes':{},'native_replay_exact':True,
      'limitation':'首token KL只存标量：只能复算汇总、差值、CI，不能重算词表分布KL；on-domain masked为E156继承，不是E157新前向。'}
    for scope,subset in [('all_questions',np.ones(128,dtype=bool)),('common_native_success',common)]:
        stat=lambda x:paired_stats(x,sub,subset)
        row={'native':{},'fixed_group':{},'on_domain':{},'off_domain':{}}
        for i,label in enumerate(('P','A','B')):
            row['native'][label]={k:stat(v[i]) for k,v in native.items()}
        for mode in (*GROUPS,'on_domain','off_domain'):
            result={};comp={k:compose(v,sub,mode) for k,v in fresh.items()}
            for r,donor in enumerate(DONORS):
                for s,shared in enumerate(SHARED):
                    item={'full':{},'delta_PP':{},'delta_same_shared_P_R':{},'delta_wholebank':{}}
                    for k,arr in comp.items():
                        cur=arr[r,s]
                        item['full'][k]=stat(cur)
                        item['delta_PP'][k]=stat(cur-old_full[k][0,0])
                        item['delta_same_shared_P_R'][k]=stat(cur-old_full[k][0,s])
                        item['delta_wholebank'][k]=stat(cur-old_full[k][r+1,s])
                    if mode=='on_domain':
                        item['inherited_on_domain_masked_E156']={k:stat(v[r+1,s]) for k,v in old_mask.items()}
                    result[donor+shared]=item
            result['AB_pairing']={}
            result['AB_pairing_vs_wholebank']={}
            result['wholebank_AB_pairing']={}
            for k,arr in comp.items():
                flip=k in ('raw_accuracy','per_char_accuracy')
                contrast=pairing(arr,flip)
                whole=pairing(old_full[k][1:3],flip)
                result['AB_pairing'][k]=stat(contrast)
                result['wholebank_AB_pairing'][k]=stat(whole)
                result['AB_pairing_vs_wholebank'][k]=stat(contrast-whole)
            if mode in GROUPS:row['fixed_group'][mode]=result
            else:row[mode]=result
        output['scopes'][scope]=row
    return output


def compare_stats(path, expected, actual, differences, counts):
    """Check point, every bootstrap interval, and both subject records."""
    for field in ('point', 'question_ci95'):
        try:
            err=float(np.max(np.abs(np.asarray(expected[field],dtype=float)-np.asarray(actual[field],dtype=float))))
            counts['numeric']+=1
            counts['max_absolute_error']=max(counts['max_absolute_error'],err)
            if not np.isfinite(err) or err>1e-10: differences.append(f'{path}/{field}: error={err}')
        except (KeyError, TypeError, ValueError): differences.append(f'{path}/{field}: missing or malformed')
    for field in ('question_count','bootstrap_seed'):
        if actual.get(field)!=expected[field]: differences.append(f'{path}/{field}: mismatch')
    if not isinstance(actual.get('unit'),str): differences.append(f'{path}/unit: missing string')
    for subject in SUBJECTS:
        try:
            e,a=expected['per_subject'][subject],actual['per_subject'][subject]
            if e['questions']!=a['questions']: differences.append(f'{path}/{subject}/questions: mismatch')
            for field in ('point','question_ci95'):
                err=float(np.max(np.abs(np.asarray(e[field],dtype=float)-np.asarray(a[field],dtype=float))))
                counts['numeric']+=1
                counts['max_absolute_error']=max(counts['max_absolute_error'],err)
                if not np.isfinite(err) or err>1e-10: differences.append(f'{path}/{subject}/{field}: error={err}')
        except (KeyError, TypeError, ValueError): differences.append(f'{path}/{subject}: missing or malformed')


def compare_summary(recomputed, summary):
    if tuple(summary.get('group_order',()))!=GROUPS or tuple(summary.get('donor_order',()))!=DONORS or tuple(summary.get('shared_order',()))!=SHARED:
        raise ValueError('summary source order differs')
    diffs=[]; counts={'numeric':0,'max_absolute_error':0.}
    cell_map={'full':'absolute','delta_PP':'minus_PP_full',
      'delta_same_shared_P_R':'minus_same_S_P_R_full','delta_wholebank':'minus_whole_bank_full',
      'inherited_on_domain_masked_E156':'inherited_E156_receiverP32'}
    contrast_map={'AB_pairing':'AB_pairing_contrast','wholebank_AB_pairing':'E156_whole_bank_AB_pairing_contrast',
      'AB_pairing_vs_wholebank':'partial_minus_whole_bank_pairing_contrast'}
    def compare_metrics(path,expected,actual):
        if set(actual)!=set(expected): diffs.append(path+': metric keys differ')
        for k,e in expected.items():
            if k not in actual: continue
            compare_stats(path+'/'+k,e,actual[k],diffs,counts)
    for scope in ('all_questions','common_native_success'):
        own=recomputed['scopes'][scope]; target=summary['scopes'][scope]
        for label in ('P','A','B'):
            compare_metrics(f'{scope}/native_full/{label}',own['native'][label],target['native_full'][label])
        for view in (*GROUPS,'on_domain','off_domain'):
            a=own['fixed_group'][view] if view in GROUPS else own[view]
            b=target['views'][view]
            for key in ('AP','AA','AB','BP','BA','BB'):
                for src,dst in cell_map.items():
                    if src in a[key]: compare_metrics(f'{scope}/{view}/{key}/{dst}',a[key][src],b['cells'][key][dst])
                    elif dst in b['cells'][key]: diffs.append(f'{scope}/{view}/{key}/{dst}: off-domain masked unexpectedly present')
            for src,dst in contrast_map.items():
                compare_metrics(f'{scope}/{view}/{dst}',a[src],b[dst])
    return {'status':'passed' if not diffs else 'failed','numeric_checks':counts['numeric'],
            'max_absolute_error':counts['max_absolute_error'],'tolerance':1e-10,'differences':diffs}


def run(raw_path,old_path,summary_path,budget_path,manifest_path,plan_path):
    budget=json.loads(budget_path.read_text()); attempts=budget.get('attempts',[])
    if not attempts or any(a.get('status')!='complete' for a in attempts):raise ValueError('budget not complete; do not read scientific results')
    manifest=json.loads(manifest_path.read_text());plan=json.loads(plan_path.read_text())
    if manifest.get('status')!='complete' or sha(plan_path)!=manifest['plan_sha256']:raise ValueError('manifest or frozen plan mismatch')
    if raw_path.resolve()!=Path(manifest['raw']['path']).resolve() or sha(raw_path)!=manifest['raw']['sha256']:raise ValueError('E157 raw mismatch')
    if old_path.resolve()!=Path(plan['previous_raw']['path']).resolve() or sha(old_path)!=plan['previous_raw']['sha256'] or manifest['previous_raw_sha256']!=plan['previous_raw']['sha256']:
        raise ValueError('E156 raw mismatch')
    if summary_path is not None:
        summary=json.loads(summary_path.read_text())
        if summary.get('raw_sha256')!=manifest['raw']['sha256'] or summary.get('status')!='complete' or summary.get('plan_sha256')!=manifest['plan_sha256'] or summary.get('previous_raw_sha256')!=manifest['previous_raw_sha256']:
            raise ValueError('summary raw/plan/reference linkage mismatch')
    with np.load(raw_path,allow_pickle=False) as fresh, np.load(old_path,allow_pickle=False) as old:
        report=recompute(fresh,old)
    comparison=compare_summary(report,summary)
    comparison.update(raw_sha256=manifest['raw']['sha256'],previous_raw_sha256=manifest['previous_raw_sha256'],limitation=report['limitation'])
    return comparison


def self_test():
    g=np.array([0,1,2,3]); l=np.array([[0.,-2,-3,-4],[-2,0,-3,-4],[-2,-3,0,-4],[-2,-3,-4,0.]])
    t=np.full((4,4),2);c=np.ones((4,4));z=np.zeros(4)
    x=measures(l,g,t,c,z)
    assert np.array_equal(x['raw_accuracy'],np.ones(4))
    assert np.allclose(x['choice_CE'],np.log1p(np.exp(-2)+np.exp(-3)+np.exp(-4)))
    l[0,0]=-1;t[0,0]=4
    assert measures(l,g,t,c,z)['true_answer_token_NLL'][0]==.25
    a=np.zeros((2,3,4));a[:,0]=100;a[0,2]=4;a[0,1]=1;a[1,1]=2;a[1,2]=3
    assert np.all(pairing(a)==1) and np.all(pairing(a,True)==-1)
    groups=np.array([[0,1,2,3],[10,11,12,13]]);sub=np.array([0,0,1,1])
    assert np.array_equal(compose(groups,sub,'on_domain'),[0,1,12,13])
    assert np.array_equal(compose(groups,sub,'off_domain'),[10,11,2,3])
    s=paired_stats(np.array([1.,1.,3.,3.]),sub,np.ones(4,dtype=bool))
    assert s['point']==2 and s['question_ci95']==[2,2]
    # Exercise numeric comparator in memory, including a deliberately corrupted CI.
    import copy
    record=paired_stats(np.array([1.,2.,3.,4.]),sub,np.ones(4,dtype=bool))
    trial=copy.deepcopy(record);trial['unit']='paired questions'
    diffs=[]; counter={'numeric':0,'max_absolute_error':0.}
    compare_stats('known',record,trial,diffs,counter)
    assert not diffs and counter['numeric']==6
    trial['per_subject'][SUBJECTS[1]]['question_ci95'][0]+=1
    compare_stats('known',record,trial,diffs,counter)
    assert diffs
    return {'status':'passed','cpu_only':True,'checks':['score and length known answer','AB sign and P exclusion','on/off assignment','paired macro bootstrap','summary comparator catches corrupted CI']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true')
    p.add_argument('--raw',type=Path);p.add_argument('--previous-raw',type=Path);p.add_argument('--summary',type=Path)
    p.add_argument('--budget',type=Path,default=REPO/'e157/budget.json');p.add_argument('--manifest',type=Path,default=REPO/'e157/manifest.json')
    p.add_argument('--plan',type=Path,default=REPO/'e157/plan.json');a=p.parse_args()
    if a.self_test:out=self_test()
    else:
        if not all((a.raw,a.previous_raw,a.summary)):p.error('--raw, --previous-raw and --summary required')
        out=run(a.raw,a.previous_raw,a.summary,a.budget,a.manifest,a.plan)
    print(json.dumps(out,ensure_ascii=False,indent=2))
    if out.get('status')=='failed': raise SystemExit(1)
