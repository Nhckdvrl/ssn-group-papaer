"""E162 paired input statistics for one additional mature training path."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results/e162'
MODELS=('P','A','B','F')
BRANCHES=('native','routed_zero','shared_zero','all_moe_zero')
MASKS=('own_prefix','random0','random1','random2');RULES=('pool','full')
LM_CONDITIONS=BRANCHES+tuple(m+'_'+r for m in MASKS for r in RULES)
TOPICS=('high_school_biology','high_school_mathematics')
FIELDS=('nll','forward_kl','reverse_kl','argmax_agree')


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def question_stats(x,subjects,mask=None):
    x=np.asarray(x,dtype=float);subjects=np.asarray(subjects)
    if x.shape!=(128,) or subjects.shape!=(128,):raise ValueError('Expected the fixed 128 paired questions')
    selected=np.ones(128,bool) if mask is None else np.asarray(mask,dtype=bool)
    rng=np.random.default_rng(162001);means=[];boot=[];detail={}
    for i,name in enumerate(TOPICS):
        v=x[selected&(subjects==i)];mean=float(v.mean()) if len(v) else None
        means.append(mean);entry={'point':mean,'count':len(v)}
        if mask is None:
            if len(v)!=64:raise ValueError('Primary requires 64 questions per subject')
            draw=v[rng.integers(0,64,(1000,64))].mean(-1);boot.append(draw)
            entry['ci95']=np.quantile(draw,[.025,.975]).tolist()
        detail[name]=entry
    result={'point':float(np.mean(means)) if all(v is not None for v in means) else None,
            'per_subject':detail,'count':int(selected.sum())}
    if mask is None:result.update(ci95=np.quantile(np.mean(boot,axis=0),[.025,.975]).tolist(),seed=162001,resamples=1000)
    else:result.update(ci='not computed',pooled_point=float(x[selected].mean()) if selected.any() else None)
    return result


def file_stats(x,groups):
    x=np.asarray(x,dtype=float)
    if x.shape!=(64,) or len(groups)!=64:raise ValueError('Expected fixed 64 windows')
    unique=sorted(set(groups));idx=[np.flatnonzero(np.asarray(groups)==g) for g in unique]
    if len(unique)!=20:raise ValueError('Expected 20 input file clusters')
    draws=np.random.default_rng(162002).integers(0,len(unique),(1000,len(unique)))
    boot=np.array([x[np.concatenate([idx[j] for j in row])].mean() for row in draws])
    return {'point':float(x.mean()),'file_ci95':np.quantile(boot,[.025,.975]).tolist(),
            'windows':64,'file_clusters':20,'seed':162002,'resamples':1000,
            'unit':'equal-window means; paired bootstrap over input file clusters, not training paths'}


def token_means(values,mask):
    v=np.asarray(values,dtype=float);mask=np.asarray(mask,dtype=bool)
    if v.shape[-3:]!=(64,512,4) or mask.shape!=(64,512) or not mask.any(-1).all():raise ValueError('Invalid token mean axes')
    return (v*mask[...,None]).sum(-2)/mask.sum(-1)[...,None]


def task_metrics(ll,gold,tokens,chars):
    q=np.arange(128);z=ll-ll.max(-1,keepdims=True);lp=z-np.log(np.exp(z).sum(-1,keepdims=True))
    return {'raw_accuracy':(ll.argmax(-1)==gold).astype(float),
            'per_char_accuracy':((ll/chars).argmax(-1)==gold).astype(float),
            'choice_CE':-lp[...,q,gold],'true_answer_token_NLL':-ll[...,q,gold]/tokens[q,gold]}


def validate(a,ref):
    shapes={'lm_metrics':(12,64,512,4),'lm_prefix_keep':(64,16,128),'lm_random_masks':(3,64,16,128),
            'lm_valid':(64,512),'lm_suffix_valid':(64,512),'task_candidate_loglikelihood':(4,128,4),
            'task_first_answer_token_KL':(4,128),'gold':(128,),'subject':(128,),
            'answer_tokens':(128,4),'answer_chars':(128,4)}
    for key,shape in shapes.items():
        if key not in a or a[key].shape!=shape or not np.isfinite(a[key]).all():raise ValueError('Bad '+key)
    for key in ('gold','subject','answer_tokens','answer_chars'):
        if not np.array_equal(a[key],ref[key]):raise ValueError('Reference population differs '+key)
    if tuple(a['lm_conditions'])!=LM_CONDITIONS or tuple(a['task_conditions'])!=BRANCHES:raise ValueError('Condition order')
    if not np.array_equal(a['lm_valid'],ref['lm_valid']) or not np.array_equal(a['lm_suffix_valid'],ref['lm_suffix_valid']):raise ValueError('Token mask differs')
    if not np.array_equal(a['lm_random_masks'],ref['lm_random_masks']):raise ValueError('Random probes changed')
    if not a['lm_prefix_keep'][:,:,-1].all() or not np.all(a['lm_prefix_keep'].sum(-1)==32):raise ValueError('Wrong prefix budget')


def summarize(a,ref,groups):
    validate(a,ref)
    qs=lambda x:question_stats(x,a['subject']);fs=lambda x:file_stats(x,groups)
    out={'experiment':'E162','status':'complete','models':list(MODELS),'conditions':list(BRANCHES),
         'scope':'One new published mature training path; no new training, no verified independent initialization or isolated timing effect.',
         'LM':{},'task':{},'F_minus_reference':{'LM':{},'task':{}},'budget':{}}
    all_task=np.concatenate((ref['task_candidate_loglikelihood'],a['task_candidate_loglikelihood'][None]))
    metrics=task_metrics(all_task,a['gold'],a['answer_tokens'],a['answer_chars'])
    kl=np.concatenate((ref['task_first_answer_token_KL'],a['task_first_answer_token_KL'][None]))
    for metric,x in metrics.items():
        sign=-1 if metric.endswith('accuracy') else 1
        damage=sign*(x[:,1:]-x[:,0:1])
        out['task'][metric]={name:{'absolute':{c:qs(x[i,j]) for j,c in enumerate(BRANCHES)},
            'removal_cost':{c:qs(damage[i,j-1]) for j,c in enumerate(BRANCHES[1:],1)},
            'R_cost_minus_S_cost':qs(damage[i,0]-damage[i,1])} for i,name in enumerate(MODELS)}
        out['F_minus_reference']['task'][metric]={name:{
            'native_quality':qs(x[3,0]-x[i,0]),
            'removal_cost':{c:qs(damage[3,j-1]-damage[i,j-1]) for j,c in enumerate(BRANCHES[1:],1)},
            'R_cost_minus_S_cost':qs((damage[3,0]-damage[3,1])-(damage[i,0]-damage[i,1]))}
            for i,name in enumerate(MODELS[:3])}
    out['task']['first_answer_token_KL']={name:{c:qs(kl[i,j]) for j,c in enumerate(BRANCHES)} for i,name in enumerate(MODELS)}
    for scope,mask in (('full',a['lm_valid']),('suffix',a['lm_suffix_valid'])):
        new=token_means(a['lm_metrics'],mask)
        native=np.concatenate((token_means(ref['lm_native_metrics'],mask),new[None,:3]))
        out['LM'][scope]={name:{c:{field:fs(native[i,j,:,k]) for k,field in enumerate(FIELDS)}
                                 for j,c in enumerate(BRANCHES[:3])} for i,name in enumerate(MODELS)}
        out['LM'][scope]['F_dense_only']={field:fs(new[3,:,k]) for k,field in enumerate(FIELDS)}
        damage=native[:,1:,:,0]-native[:,0:1,:,0]
        out['F_minus_reference']['LM'][scope]={name:{
            'native_NLL':fs(native[3,0,:,0]-native[i,0,:,0]),
            'R_removal_NLL':fs(damage[3,0]-damage[i,0]),'S_removal_NLL':fs(damage[3,1]-damage[i,1]),
            'R_cost_minus_S_cost':fs((damage[3,0]-damage[3,1])-(damage[i,0]-damage[i,1]))}
            for i,name in enumerate(MODELS[:3])}
        if scope=='suffix':
            budgets=np.concatenate((token_means(ref['lm_budget_AB'],mask),new[None,4:].reshape(1,4,2,64,4)))
            baseline=native[1:,0]
            for i,name in enumerate(('A','B','F')):
                record={}
                for r,rule in enumerate(RULES):
                    random=budgets[i,1:,r].mean(0)
                    record[rule]={'masks':{m:{field:fs(budgets[i,j,r,:,k]) for k,field in enumerate(FIELDS)} for j,m in enumerate(MASKS)},
                        'own_prefix_delta_NLL':fs(budgets[i,0,r,:,0]-baseline[i,:,0]),
                        'random_mean_delta_NLL':fs(random[:,0]-baseline[i,:,0]),
                        'random_minus_prefix_NLL':fs(random[:,0]-budgets[i,0,r,:,0]),
                        'random_minus_prefix_KL':fs(random[:,1]-budgets[i,0,r,:,1])}
                out['budget'][name]=record
            out['budget']['F_minus_reference']={name:{rule:{
                'own_prefix_delta_NLL':fs((budgets[2,0,r,:,0]-baseline[2,:,0])-(budgets[i,0,r,:,0]-baseline[i,:,0])),
                'own_prefix_KL':fs(budgets[2,0,r,:,1]-budgets[i,0,r,:,1]),
                'random_minus_prefix_NLL':fs((budgets[2,1:,r,:,0].mean(0)-budgets[2,0,r,:,0])-(budgets[i,1:,r,:,0].mean(0)-budgets[i,0,r,:,0]))}
                for r,rule in enumerate(RULES)} for i,name in enumerate(('A','B'))}
            parent=token_means(ref['lm_budget_P_pool'],mask)
            out['budget']['P_pool_only']={m:{field:fs(parent[j,:,k]) for k,field in enumerate(FIELDS)} for j,m in enumerate(MASKS)}
            out['budget']['F_minus_P_pool_only']={'own_prefix_delta_NLL':fs((budgets[2,0,0,:,0]-baseline[2,:,0])-(parent[0,:,0]-native[0,0,:,0]))}
    correct=metrics['raw_accuracy'].astype(bool);cohort=correct[:,0].all(0)
    # bits: D, R-only (S zero), S-only (R zero). All selected full systems are correct.
    codes=4*correct[:,3]+2*correct[:,2]+correct[:,1]
    def count(code,mask):return np.bincount(code[mask],minlength=8).tolist()
    selected={'mask':cohort.tolist(),'count':int(cohort.sum()),'per_subject_count':[int((cohort&(a['subject']==i)).sum()) for i in (0,1)],
              'ci':'not computed','bits':{'D':4,'R_only':2,'S_only':1},'models':{},'transitions_to_F':{}}
    for i,name in enumerate(MODELS):
        selected['models'][name]={'counts':count(codes[i],cohort),'per_subject_counts':[count(codes[i],cohort&(a['subject']==j)) for j in (0,1)],
                                 'joint_necessary':question_stats((codes[i]==0).astype(float),a['subject'],cohort)}
    for i,name in enumerate(MODELS[:3]):
        matrix=np.zeros((8,8),int);np.add.at(matrix,(codes[i,cohort],codes[3,cohort]),1)
        selected['transitions_to_F'][name]=matrix.tolist()
    out['all_four_full_correct']=selected
    return out


def analyze():
    plan=json.loads((ROOT/'plan.json').read_text());manifest=json.loads((ROOT/'manifest.json').read_text());budget=json.loads((ROOT/'budget.json').read_text())
    if manifest['status']!='complete' or manifest['source_sha256']!=plan['source_sha256'] or manifest['plan_sha256']!=sha(ROOT/'plan.json'):raise ValueError('Incomplete provenance')
    if plan['source_sha256']['e162_analyze.py']!=sha(__file__):raise ValueError('Frozen analysis changed')
    attempts=budget['attempts']
    if not attempts or attempts[-1]['status']!='complete' or any(r['status'] not in ('complete','failed') for r in attempts) or sum(r['gpu_seconds'] for r in attempts)>7200:raise ValueError('Budget incomplete or exceeded')
    for record in (plan['references'],manifest['raw']):
        if sha(record['path'])!=record['sha256']:raise ValueError('Input/raw SHA mismatch')
    def load(path):
        with np.load(path,allow_pickle=False) as file:return {k:file[k] for k in file.files}
    result=summarize(load(manifest['raw']['path']),load(plan['references']['path']),plan['file_groups'])
    result.update(raw_sha256=manifest['raw']['sha256'],plan_sha256=manifest['plan_sha256'],analysis_source_sha256=sha(__file__))
    (ROOT/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return {'status':'complete','summary':str(ROOT/'summary.json')}


def self_test():
    subjects=np.repeat([0,1],64);v=np.r_[np.ones(64),np.full(64,3.)]
    assert question_stats(v,subjects)['ci95']==[2.,2.]
    assert question_stats(v,subjects,subjects==0)['point'] is None
    groups=[f'f{i%20:02}' for i in range(64)]
    assert file_stats(np.ones(64),groups)['file_ci95']==[1.,1.]
    mask=np.ones((64,512),bool);x=np.ones((3,2,64,512,4))
    assert token_means(x,mask).shape==(3,2,64,4) and np.all(token_means(x,mask)==1)
    gold=np.arange(128)%4;ll=np.zeros((4,4,128,4));ll[:,:,np.arange(128),gold]=2
    m=task_metrics(ll,gold,np.ones((128,4)),np.ones((128,4)))
    assert m['raw_accuracy'].all() and np.allclose(m['choice_CE'],np.log1p(3*np.exp(-2)))
    return {'status':'passed','CPU_only':True,'checks':['subject pairing and empty subset','file cluster known answer','token/window axes','four-model task metrics']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');parser.add_argument('--analyze',action='store_true');args=parser.parse_args()
    if args.self_test==args.analyze:parser.error('Choose exactly one mode')
    print(json.dumps(self_test() if args.self_test else analyze(),indent=2))
