"""Independent E162 input-statistic and provenance verification; no model imports."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

WB=Path(__file__).resolve().parents[2];ROOT=WB/'results/e162'
NAMES=('P','A','B','F');CONDITIONS=('native','routed_zero','shared_zero','all_moe_zero')
MASKS=('own_prefix','random0','random1','random2');RULES=('pool','full')
FIELDS=('nll','forward_kl','reverse_kl','argmax_agree')
TOPICS=('high_school_biology','high_school_mathematics')


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text())


def load(path):
    with np.load(path,allow_pickle=False) as file:return {key:file[key] for key in file.files}


class Check:
    def __init__(self,subjects,groups):
        self.errors=[];self.counts=0;self.numeric=0;self.maximum=0.;self.subjects=np.asarray(subjects)
        rng=np.random.default_rng(162001)
        self.questions=[rng.choice(np.flatnonzero(self.subjects==i),(1000,64),replace=True) for i in (0,1)]
        self.file_rows=[np.flatnonzero(np.asarray(groups)==g) for g in sorted(set(groups))]
        if len(self.file_rows)!=20:raise ValueError('Wrong file-cluster population')
        draws=np.random.default_rng(162002).choice(20,(1000,20),replace=True)
        self.multiplicity=np.zeros((1000,20),int)
        np.add.at(self.multiplicity,(np.repeat(np.arange(1000),20),draws.ravel()),1)
        self.denominator=self.multiplicity@np.array([len(row) for row in self.file_rows])

    def eq(self,path,expected,actual):
        if expected is None or actual is None:
            self.counts+=1
            if expected is not None or actual is not None:self.errors.append(path+': null differs')
            return
        x=np.asarray(expected);y=np.asarray(actual)
        if x.shape!=y.shape:self.errors.append(path+': shape differs');return
        if x.dtype.kind in 'fiu' and y.dtype.kind in 'fiu':
            if not np.isfinite(x).all() or not np.isfinite(y).all():self.errors.append(path+': nonfinite');return
            err=float(np.max(np.abs(x.astype(float)-y.astype(float)))) if x.size else 0
            self.maximum=max(self.maximum,err);self.numeric+=x.size
            if err>1e-10:self.errors.append(path+': numeric difference '+str(err))
        else:
            self.counts+=x.size
            if not np.array_equal(x,y):self.errors.append(path+': values differ')

    def file(self,path,x,got):
        x=np.asarray(x,dtype=float)
        totals=np.array([x[rows].sum() for rows in self.file_rows])
        boot=(self.multiplicity@totals)/self.denominator
        self.eq(path+'/point',float(x.mean()),got['point']);self.eq(path+'/CI',np.quantile(boot,[.025,.975]),got['file_ci95'])
        for key,value in [('windows',64),('file_clusters',20),('seed',162002),('resamples',1000)]:self.eq(path+'/'+key,value,got[key])

    def question(self,path,x,got,mask=None):
        x=np.asarray(x,dtype=float);selected=np.ones(128,bool) if mask is None else mask
        means=[];draws=[]
        for i,name in enumerate(TOPICS):
            v=x[selected&(self.subjects==i)];value=float(v.mean()) if len(v) else None;means.append(value)
            entry=got['per_subject'][name];self.eq(path+'/'+name+'/point',value,entry['point']);self.eq(path+'/'+name+'/count',len(v),entry['count'])
            if mask is None:
                boot=x[self.questions[i]].mean(-1);draws.append(boot)
                self.eq(path+'/'+name+'/CI',np.quantile(boot,[.025,.975]),entry['ci95'])
        macro=(means[0]+means[1])/2 if all(v is not None for v in means) else None
        self.eq(path+'/point',macro,got['point']);self.eq(path+'/count',int(selected.sum()),got['count'])
        if mask is None:
            self.eq(path+'/CI',np.quantile((draws[0]+draws[1])/2,[.025,.975]),got['ci95'])
            self.eq(path+'/seed',162001,got['seed']);self.eq(path+'/resamples',1000,got['resamples'])
        else:
            self.eq(path+'/CI label','not computed',got['ci'])
            self.eq(path+'/pooled',float(x[selected].mean()) if selected.any() else None,got['pooled_point'])


def means(values,mask):
    weights=np.asarray(mask,dtype=float)/np.asarray(mask).sum(-1)[:,None]
    return (np.asarray(values,dtype=float)*weights[...,None]).sum(-2)


def scores(ll,gold,tokens,chars):
    ll=np.asarray(ll,dtype=float);labels=np.broadcast_to(gold,ll.shape[:-1]);chosen=np.take_along_axis(ll,labels[...,None],-1)[...,0]
    norm=np.max(ll,-1);ce=norm+np.log(np.exp(ll-norm[...,None]).sum(-1))-chosen
    length=np.take_along_axis(np.broadcast_to(tokens,ll.shape),labels[...,None],-1)[...,0]
    return np.stack(((ll.argmax(-1)==labels).astype(float),((ll/chars).argmax(-1)==labels).astype(float),ce,-chosen/length))


def compare(a,ref,s,groups):
    check=Check(a['subject'],groups)
    ll=np.concatenate((ref['task_candidate_loglikelihood'],a['task_candidate_loglikelihood'][None]))
    metrics=scores(ll,a['gold'],a['answer_tokens'],a['answer_chars'])
    for k,metric in enumerate(('raw_accuracy','per_char_accuracy','choice_CE','true_answer_token_NLL')):
        value=metrics[k];sgn=-1 if k<2 else 1;cost=sgn*(value[:,1:]-value[:,0:1])
        for i,name in enumerate(NAMES):
            row=s['task'][metric][name]
            for j,c in enumerate(CONDITIONS):check.question(f'task/{metric}/{name}/{c}',value[i,j],row['absolute'][c])
            for j,c in enumerate(CONDITIONS[1:]):check.question(f'task/{metric}/{name}/{c}/cost',cost[i,j],row['removal_cost'][c])
            check.question(f'task/{metric}/{name}/allocation',cost[i,0]-cost[i,1],row['R_cost_minus_S_cost'])
        for i,name in enumerate(NAMES[:3]):
            row=s['F_minus_reference']['task'][metric][name]
            check.question(f'task/F-{name}/{metric}/quality',value[3,0]-value[i,0],row['native_quality'])
            for j,c in enumerate(CONDITIONS[1:]):check.question(f'task/F-{name}/{metric}/{c}',cost[3,j]-cost[i,j],row['removal_cost'][c])
            check.question(f'task/F-{name}/{metric}/allocation',(cost[3,0]-cost[3,1])-(cost[i,0]-cost[i,1]),row['R_cost_minus_S_cost'])
    kl=np.concatenate((ref['task_first_answer_token_KL'],a['task_first_answer_token_KL'][None]))
    for i,name in enumerate(NAMES):
        for j,c in enumerate(CONDITIONS):check.question(f'task/{name}/{c}/firstKL',kl[i,j],s['task']['first_answer_token_KL'][name][c])
    for scope,mask in [('full',a['lm_valid']),('suffix',a['lm_suffix_valid'])]:
        new=means(a['lm_metrics'],mask);native=np.concatenate((means(ref['lm_native_metrics'],mask),new[None,:3]))
        for i,name in enumerate(NAMES):
            for j,c in enumerate(CONDITIONS[:3]):
                for k,field in enumerate(FIELDS):check.file(f'LM/{scope}/{name}/{c}/{field}',native[i,j,:,k],s['LM'][scope][name][c][field])
        for k,field in enumerate(FIELDS):check.file(f'LM/{scope}/F_D/{field}',new[3,:,k],s['LM'][scope]['F_dense_only'][field])
        cost=native[:,1:,:,0]-native[:,0:1,:,0]
        for i,name in enumerate(NAMES[:3]):
            row=s['F_minus_reference']['LM'][scope][name]
            values={'native_NLL':native[3,0,:,0]-native[i,0,:,0],'R_removal_NLL':cost[3,0]-cost[i,0],
                    'S_removal_NLL':cost[3,1]-cost[i,1],'R_cost_minus_S_cost':(cost[3,0]-cost[3,1])-(cost[i,0]-cost[i,1])}
            for key,x in values.items():check.file(f'LM/{scope}/F-{name}/{key}',x,row[key])
        if scope!='suffix':continue
        budget=np.concatenate((means(ref['lm_budget_AB'],mask),new[None,4:].reshape(1,4,2,64,4)))
        base=native[1:,0]
        for i,name in enumerate(('A','B','F')):
            for r,rule in enumerate(RULES):
                row=s['budget'][name][rule];random=budget[i,1:,r].sum(0)/3
                for j,m in enumerate(MASKS):
                    for k,field in enumerate(FIELDS):check.file(f'budget/{name}/{m}/{rule}/{field}',budget[i,j,r,:,k],row['masks'][m][field])
                values={'own_prefix_delta_NLL':budget[i,0,r,:,0]-base[i,:,0],'random_mean_delta_NLL':random[:,0]-base[i,:,0],
                        'random_minus_prefix_NLL':random[:,0]-budget[i,0,r,:,0],'random_minus_prefix_KL':random[:,1]-budget[i,0,r,:,1]}
                for key,x in values.items():check.file(f'budget/{name}/{rule}/{key}',x,row[key])
        for i,name in enumerate(('A','B')):
            for r,rule in enumerate(RULES):
                row=s['budget']['F_minus_reference'][name][rule]
                values={'own_prefix_delta_NLL':(budget[2,0,r,:,0]-base[2,:,0])-(budget[i,0,r,:,0]-base[i,:,0]),
                        'own_prefix_KL':budget[2,0,r,:,1]-budget[i,0,r,:,1],
                        'random_minus_prefix_NLL':(budget[2,1:,r,:,0].mean(0)-budget[2,0,r,:,0])-(budget[i,1:,r,:,0].mean(0)-budget[i,0,r,:,0])}
                for key,x in values.items():check.file(f'budget/F-{name}/{rule}/{key}',x,row[key])
        parent=means(ref['lm_budget_P_pool'],mask)
        for j,m in enumerate(MASKS):
            for k,field in enumerate(FIELDS):check.file(f'budget/P/{m}/{field}',parent[j,:,k],s['budget']['P_pool_only'][m][field])
        check.file('budget/F-P/own',(budget[2,0,0,:,0]-base[2,:,0])-(parent[0,:,0]-native[0,0,:,0]),s['budget']['F_minus_P_pool_only']['own_prefix_delta_NLL'])
    correct=metrics[0].astype(bool);eligible=correct[:,0].all(0);codes=4*correct[:,3]+2*correct[:,2]+correct[:,1];sec=s['all_four_full_correct']
    check.eq('secondary/mask',eligible,sec['mask']);check.eq('secondary/count',int(eligible.sum()),sec['count'])
    check.eq('secondary/subject counts',[int((eligible&(a['subject']==j)).sum()) for j in (0,1)],sec['per_subject_count'])
    check.eq('secondary/CI','not computed',sec['ci'])
    for i,name in enumerate(NAMES):
        row=sec['models'][name];check.eq(f'secondary/{name}/patterns',np.bincount(codes[i,eligible],minlength=8),row['counts'])
        check.eq(f'secondary/{name}/subject patterns',[np.bincount(codes[i,eligible&(a['subject']==j)],minlength=8).tolist() for j in (0,1)],row['per_subject_counts'])
        check.question(f'secondary/{name}/joint',(codes[i]==0).astype(float),row['joint_necessary'],eligible)
    for i,name in enumerate(NAMES[:3]):
        transition=np.bincount(8*codes[i,eligible]+codes[3,eligible],minlength=64).reshape(8,8)
        check.eq(f'secondary/{name}/toF',transition,sec['transitions_to_F'][name])
    return {'status':'passed' if not check.errors else 'failed','numeric_comparisons':check.numeric,
            'count_checks':check.counts,'max_absolute_error':check.maximum,'differences':check.errors}


def audit(summary):
    plan=read(ROOT/'plan.json');manifest=read(ROOT/'manifest.json');ledger=read(ROOT/'budget.json')
    if manifest['status']!='complete' or manifest['plan_sha256']!=sha(ROOT/'plan.json') or manifest['source_sha256']!=plan['source_sha256']:raise ValueError('Manifest/plan mismatch')
    rows=ledger['attempts']
    if not rows or rows[-1]['status']!='complete' or any(r['status'] not in ('complete','failed') for r in rows) or sum(r['gpu_seconds'] for r in rows)>7200:raise ValueError('Incomplete/exceeded GPU budget')
    if plan['max_concurrent_gpus']!=4 or plan['bootstrap']!={'questions':162001,'files':162002,'resamples':1000}:raise ValueError('Protocol mismatch')
    old=read(WB/'results/e150/metadata.json')['models']
    for name,digest in plan['source_sha256'].items():
        if '/' in name:
            model,filename=name.split('/',1);record=plan['model']['files'][filename] if model=='F' else old[model]['files'][filename];path=record['path']
        else:path=WB/'scripts'/name
        if sha(path)!=digest:raise ValueError('Source identity '+name)
    for key in ('model_asset_manifest','lm_input','lm_input_plan','task_input','references'):
        record=plan[key]
        if sha(record['path'])!=record['sha256']:raise ValueError('Input identity '+key)
    for group in plan['old_artifacts'].values():
        for record in group.values():
            if sha(record['path'])!=record['sha256']:raise ValueError('Old artifact differs')
    preflight=read(ROOT/'preflight.json')
    if preflight['parameter_hash']!=manifest['source_parameter_hash'] or preflight['buffer_hash']!=manifest['source_buffer_hash'] or not all(manifest['controls'].values()):raise ValueError('Engineering/source control')
    if sha(preflight['calibration']['path'])!=preflight['calibration']['sha256'] or not preflight['repeat_and_both_full_slot_rules_exact'] or not preflight['partial_pool_equals_old_hook_exact']:raise ValueError('Calibration control')
    if np.asarray(preflight['FP32_to_BF16_per_sequence'])[:,1].max()>.02:raise ValueError('Precision gate')
    if sha(manifest['raw']['path'])!=manifest['raw']['sha256']:raise ValueError('Raw differs')
    a=load(manifest['raw']['path']);ref=load(plan['references']['path']);s=read(summary)
    expected_lm=CONDITIONS+tuple(m+'_'+r for m in MASKS for r in RULES)
    if tuple(a['lm_conditions'])!=expected_lm or tuple(a['task_conditions'])!=CONDITIONS:raise ValueError('Raw condition order differs')
    for key,shape in [('lm_metrics',(12,64,512,4)),('task_candidate_loglikelihood',(4,128,4)),('task_first_answer_token_KL',(4,128))]:
        if a[key].shape!=shape or not np.isfinite(a[key]).all():raise ValueError('Invalid raw '+key)
    if s['experiment']!='E162' or s['status']!='complete' or s['models']!=list(NAMES) or s['conditions']!=list(CONDITIONS):raise ValueError('Summary axes differ')
    for key in ('gold','subject','answer_tokens','answer_chars'):
        if not np.array_equal(a[key],ref[key]):raise ValueError('Question population differs')
    for rawkey,refkey in [('lm_valid','lm_valid'),('lm_suffix_valid','lm_suffix_valid'),('lm_random_masks','lm_random_masks')]:
        if not np.array_equal(a[rawkey],ref[refkey]):raise ValueError('Mask differs')
    if not np.all(a['lm_prefix_keep'].sum(-1)==32) or not a['lm_prefix_keep'][:,:,-1].all():raise ValueError('Wrong prefix budget')
    if s['raw_sha256']!=manifest['raw']['sha256'] or s['plan_sha256']!=manifest['plan_sha256'] or s['analysis_source_sha256']!=plan['source_sha256']['e162_analyze.py']:raise ValueError('Summary provenance')
    result=compare(a,ref,s,plan['file_groups'])
    return {**result,'raw_sha256':manifest['raw']['sha256'],'plan_sha256':manifest['plan_sha256'],'audit_source_sha256':sha(__file__),
            'limitations':'Recomputes all task metrics and input CIs from saved raw. Stored KL scalars and runtime engine controls are verified by lineage; unavailable full-vocabulary distributions are not independently recomputed. Not an independent new training or L3 scientific review.'}


def self_test():
    c=Check(np.repeat([0,1],64),[f'f{i%20:02}' for i in range(64)])
    c.file('constant',np.ones(64),{'point':1.,'file_ci95':[1.,1.],'windows':64,'file_clusters':20,'seed':162002,'resamples':1000})
    expected={'point':2.,'ci95':[2.,2.],'count':128,'seed':162001,'resamples':1000,
              'per_subject':{TOPICS[0]:{'point':1.,'count':64,'ci95':[1.,1.]},TOPICS[1]:{'point':3.,'count':64,'ci95':[3.,3.]}}}
    c.question('known',np.r_[np.ones(64),np.full(64,3.)],expected)
    assert not c.errors
    bad=dict(expected);bad['point']=2.1;c.question('bad',np.r_[np.ones(64),np.full(64,3.)],bad)
    assert c.errors
    return {'status':'passed','CPU_only':True,'checks':['independent clustered weighted bootstrap','paired subject bootstrap','intentional point corruption detected']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--summary',type=Path);p.add_argument('--output',type=Path);args=p.parse_args()
    if args.self_test:print(json.dumps(self_test(),indent=2))
    else:
        if not args.summary or not args.output:p.error('--summary and --output required')
        report=audit(args.summary);args.output.write_text(json.dumps(report,indent=2)+'\n');print(report)
        if report['status']!='passed':raise SystemExit(1)
