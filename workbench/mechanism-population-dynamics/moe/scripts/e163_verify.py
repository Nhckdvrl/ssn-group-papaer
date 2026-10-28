"""Independent NumPy reconstruction of E163 statistics and saved vector probes.

No model, Torch or author statistics implementation is imported by verification.
The pre-run fixture explicitly imports the author once to compare old-data
synthetic geometry conditions before any new held model readout.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/'results/e163'
NAMES=('P','A','B','F')
TARGETS=('R','S','RS')
MODES=('zero','norm_mean','gram_mean','gram_random0','gram_random1')
CONDITIONS=('native',)+tuple(t+'_'+m for t in TARGETS for m in MODES)
RULES=('raw','norm','gram')
LM_FIELDS=('nll','forward_KL','reverse_KL','argmax_agreement')
TASK_FIELDS=('raw_accuracy','per_char_accuracy','choice_CE','true_answer_token_NLL')
TOPICS=('high_school_biology','high_school_mathematics')


def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def arrays(path):
    with np.load(path,allow_pickle=False) as f:return {k:f[k].copy() for k in f.files}


class Oracle:
    def __init__(self,refs,groups):
        self.subjects=refs['subject'];self.indices=[np.where(self.subjects==i)[0] for i in (0,1)]
        rng=np.random.default_rng(163001)
        self.qdraw=[idx[rng.integers(len(idx),size=(1000,len(idx)))] for idx in self.indices]
        names=sorted(set(groups));byfile={g:np.flatnonzero(np.asarray(groups)==g) for g in names}
        sampled=np.random.default_rng(163002).integers(len(names),size=(1000,len(names)))
        # Resample and concatenate actual windows; no author weight matrix.
        self.fdraw=[np.concatenate([byfile[names[i]] for i in draw]) for draw in sampled]

    def question(self,x,selected=None):
        x=np.asarray(x,np.float64)
        if selected is not None:
            sub=[x[np.intersect1d(idx,np.flatnonzero(selected))] for idx in self.indices]
            return {'point':float(sum(v.mean() for v in sub)/2) if all(len(v) for v in sub) else None,
                    'pooled_point':float(x[selected].mean()) if selected.any() else None,
                    'count':int(selected.sum()),'subject_counts':[len(v) for v in sub],
                    'ci':'not computed after common-success selection'}
        means=[np.average(x[rows],axis=1) for rows in self.qdraw]
        macro=(means[0]+means[1])/2
        return {'point':float(np.average(x)),'ci95':np.percentile(macro,[2.5,97.5]).tolist(),
            'per_subject':{TOPICS[i]:{'point':float(np.average(x[idx])),
                'ci95':np.percentile(means[i],[2.5,97.5]).tolist(),'count':64}
                for i,idx in enumerate(self.indices)},'count':128,'seed':163001,'resamples':1000}

    def file(self,x):
        x=np.asarray(x,np.float64)
        boot=np.array([np.average(x[draw]) for draw in self.fdraw])
        return {'point':float(np.average(x)),'file_ci95':np.percentile(boot,[2.5,97.5]).tolist(),
            'windows':64,'file_clusters':20,'seed':163002,'resamples':1000,
            'unit':'equal-window point; paired file-cluster bootstrap, not training seeds'}


def metrics(ll,refs):
    """Calculate candidate metrics one row at a time with explicit gold gather."""
    leading=ll.shape[:-2]
    result={field:np.empty(leading+(128,),np.float64) for field in TASK_FIELDS}
    for prefix in np.ndindex(leading):
        for q in range(128):
            row=ll[prefix+(q,)];g=int(refs['gold'][q]);peak=float(np.max(row))
            result['raw_accuracy'][prefix+(q,)]=int(np.argmax(row)==g)
            result['per_char_accuracy'][prefix+(q,)]=int(np.argmax(row/refs['answer_chars'][q])==g)
            result['choice_CE'][prefix+(q,)]=peak+np.log(np.exp(row-peak).sum())-row[g]
            result['true_answer_token_NLL'][prefix+(q,)]=-row[g]/refs['answer_tokens'][q,g]
    return result


class Comparison:
    def __init__(self):self.numbers=0;self.metadata=0;self.maximum=0.
    def check(self,got,want,path='root'):
        if isinstance(want,dict):
            if set(got)!=set(want):raise AssertionError('Key mismatch '+path)
            for k in want:self.check(got[k],want[k],path+'/'+k)
        elif isinstance(want,(list,tuple,np.ndarray)):
            if len(got)!=len(want):raise AssertionError('Length mismatch '+path)
            for i,(a,b) in enumerate(zip(got,want)):self.check(a,b,path+'/'+str(i))
        elif isinstance(want,(int,float,np.integer,np.floating)) and not isinstance(want,bool):
            error=abs(float(got)-float(want));self.maximum=max(self.maximum,error);self.numbers+=1
            if not np.isfinite(error) or error>1e-9:raise AssertionError('Numeric mismatch '+path+': '+str(error))
        else:
            self.metadata+=1
            if got!=want:raise AssertionError('Metadata mismatch '+path)
    def report(self):return {'status':'passed','numeric_comparisons':self.numbers,'metadata_comparisons':self.metadata,'maximum_absolute_difference':self.maximum}


def verify_summary(summary,native,cross,refs,groups):
    oracle=Oracle(refs,groups);comparison=Comparison()
    task=metrics(np.stack([native[n]['candidate_loglikelihood'] for n in NAMES]),refs)
    lm=np.empty((4,16,64,4))
    for mi,name in enumerate(NAMES):
        for c in range(16):
            for w in range(64):
                lm[mi,c,w]=native[name]['lm_metrics'][c,w,refs['lm_valid'][w]].astype(np.float64).mean(0)
    for domain,data,func in [('task',task,oracle.question),('LM',{f:lm[:,:,:,i] for i,f in enumerate(LM_FIELDS)},oracle.file)]:
        for field,x in data.items():
            sign=-1 if field in ('raw_accuracy','per_char_accuracy','argmax_agreement') else 1
            damage=np.empty_like(x)
            for mi in range(4):
                for c in range(16):damage[mi,c]=sign*(x[mi,c]-x[mi,0])
            for mi,name in enumerate(NAMES):
                want={'absolute':{},'damage':{},'zero_minus_proxy_damage':{},'norm_minus_gram_damage':{}}
                for c,condition in enumerate(CONDITIONS):
                    want['absolute'][condition]=func(x[mi,c])
                    if c:want['damage'][condition]=func(damage[mi,c])
                for ti,target in enumerate(TARGETS):
                    start=1+5*ti
                    want['zero_minus_proxy_damage'][target]={MODES[j]:func(damage[mi,start]-damage[mi,start+j]) for j in range(1,5)}
                    want['norm_minus_gram_damage'][target]=func(damage[mi,start+1]-damage[mi,start+2])
                comparison.check(summary['native'][domain][field][name],want,domain+'/'+field+'/'+name)
            for j in range(1,4):
                for i in range(j):
                    want={'native_quality':func(x[j,0]-x[i,0]),
                          'damage':{condition:func(damage[j,c]-damage[i,c]) for c,condition in enumerate(CONDITIONS) if c}}
                    comparison.check(summary['history_contrasts'][domain][field][NAMES[j]+'_minus_'+NAMES[i]],want,'history/'+domain+'/'+field)
    for name in NAMES:
        comparison.check(summary['native']['task']['first_answer_token_KL'][name],
            {c:oracle.question(native[name]['first_answer_token_KL'][j]) for j,c in enumerate(CONDITIONS)},'nativeKL/'+name)
    mask=refs['common_success_mask']
    actual=np.ones(128,bool)
    for name in NAMES:actual&=native[name]['candidate_loglikelihood'][0].argmax(-1)==refs['gold']
    if not np.array_equal(mask,actual):raise AssertionError('Fixed common-success mask changed')
    for field,x in task.items():
        for mi,name in enumerate(NAMES):
            comparison.check(summary['common_success']['task'][field][name],
                {c:oracle.question(x[mi,j],mask) for j,c in enumerate(CONDITIONS)},'secondary/'+name+'/'+field)
    cm=metrics(cross['candidate_loglikelihood'],refs)
    for field,x in cm.items():
        sign=-1 if field.endswith('accuracy') else 1
        costs=[];absolute={}
        for ri,rule in enumerate(RULES):
            absolute[rule]={}
            diagonal=[];foreign=[]
            for ci,consumer in enumerate(NAMES[:3]):
                for pi,producer in enumerate(NAMES[:3]):
                    row=x[ri,ci,pi]
                    absolute[rule][consumer+'_'+producer]=oracle.question(row)
                    (diagonal if ci==pi else foreign).append(row)
            costs.append(sign*(sum(foreign)/6-sum(diagonal)/3))
        want={'absolute':absolute,'matching_cost':{r:oracle.question(costs[i]) for i,r in enumerate(RULES)},
              'rule_contrasts':{RULES[j]+'_minus_'+RULES[i]:oracle.question(costs[j]-costs[i]) for j in range(1,3) for i in range(j)}}
        comparison.check(summary['cross'][field],want,'cross/'+field)
    want={r:{c+'_'+p:oracle.question(cross['first_answer_token_KL'][ri,ci,pi])
        for ci,c in enumerate(NAMES[:3]) for pi,p in enumerate(NAMES[:3])} for ri,r in enumerate(RULES)}
    comparison.check(summary['cross']['first_answer_token_KL'],want,'crossKL')
    for name in NAMES:
        comparison.check(summary['geometry'][name]['LM_maxima_over_batches_layers'],np.max(native[name]['LM_geometry'],axis=(1,2)),'LMgeometry/'+name)
        comparison.check(summary['geometry'][name]['task_maxima_over_questions_layers'],np.max(native[name]['task_geometry'],axis=(1,2)),'taskgeometry/'+name)
        comparison.check(summary['geometry'][name]['native_LM_geometry_batch_mean'],np.mean(native[name]['native_LM_geometry'],axis=0),'nativegeometry/'+name)
    return comparison.report()


def fixture(refs,groups):
    """Duplicate inherited scores into a synthetic 16-condition test, no models."""
    import e163_analyze as author
    native={}
    for mi,name in enumerate(NAMES):
        lm_base=refs['native_LM_F'] if name=='F' else refs['native_LM_PAB'][mi]
        lm=np.stack([lm_base[min(c%4,len(lm_base)-1)] for c in range(16)])
        ll=np.stack([refs['native_LL'][mi,c%4] for c in range(16)])
        native[name]={'lm_metrics':lm,'candidate_loglikelihood':ll,'conditions':np.array(CONDITIONS),
            'first_answer_token_KL':np.stack([refs['native_task_KL'][mi,c%4] for c in range(16)]),
            'LM_geometry':np.zeros((16,16,16,9)), 'task_geometry':np.zeros((16,128,16,9)),
            'native_LM_geometry':np.zeros((16,3,16,3)),**{k:refs[k] for k in ('gold','subject','answer_tokens','answer_chars')}}
    cross={'candidate_loglikelihood':np.stack([refs['cross_raw_LL']]*3),'rules':np.array(RULES),
           'first_answer_token_KL':np.zeros((3,3,3,128))}
    summary=author.summarize(native,cross,refs,groups)
    report=verify_summary(summary,native,cross,refs,groups)
    report.update(fixture='Inherited E160/E162 duplicated into synthetic geometry conditions; no new model outputs',
                  author_source_sha256=sha(Path(__file__).with_name('e163_analyze.py')),
                  independent_source_sha256=sha(__file__))
    return report


def geometry_probes(path):
    data=arrays(path);prefixes=sorted({key.rsplit('_',1)[0] for key in data if key.endswith('_u')})
    maxima={'precise_norm_relative':0.,'precise_projection_scaled':0.,'BF16_norm_relative':0.,
            'BF16_projection_scaled':0.,'actual_residual_norm_relative':0.,'numpy_reconstruction_relative':0.}
    vectors=0
    for prefix in prefixes:
        condition=int(prefix.split('_')[0]);rule=CONDITIONS[condition].split('_')[1]
        u,b,d,v,cast=(data[prefix+'_'+k].astype(np.float64) for k in ('u','b','direction','precise','cast'))
        r=np.linalg.norm(u,axis=1,keepdims=True);den=np.maximum(r,1e-12)
        bhat=b/np.maximum(np.linalg.norm(b,axis=1,keepdims=True),1e-12)
        p=np.einsum('ij,ij->i',u,bhat)[:,None]
        if rule=='norm':
            dn=np.linalg.norm(d,axis=1,keepdims=True);unit=d/np.maximum(dn,1e-12)
            unit[dn[:,0]<=1e-12]=np.eye(d.shape[-1])[0]
            expected=r*unit
        else:
            dp=d-np.einsum('ij,ij->i',d,bhat)[:,None]*bhat
            dn=np.linalg.norm(d,axis=1,keepdims=True);pn=np.linalg.norm(dp,axis=1,keepdims=True)
            fallback=(pn<=1e-6*dn)|(pn<=1e-12)
            unit=dp/np.maximum(pn,1e-12)
            for row in np.flatnonzero(fallback[:,0]):
                e=np.eye(d.shape[-1])[np.argmin(np.abs(bhat[row]))]
                e=e-np.dot(e,bhat[row])*bhat[row]
                unit[row]=e/max(np.linalg.norm(e),1e-12)
            expected=p*bhat+np.linalg.norm(u-p*bhat,axis=1,keepdims=True)*unit
        expected[np.all(d==u,axis=1)]=u[np.all(d==u,axis=1)]
        expected[r[:,0]<=1e-12]=0
        def update(key,value):maxima[key]=max(maxima[key],float(np.max(value)))
        update('numpy_reconstruction_relative',np.linalg.norm(v-expected,axis=1)/den[:,0])
        update('precise_norm_relative',np.abs(np.linalg.norm(v,axis=1)-r[:,0])/den[:,0])
        update('BF16_norm_relative',np.abs(np.linalg.norm(cast,axis=1)-r[:,0])/den[:,0])
        if rule=='gram':
            update('precise_projection_scaled',np.abs(np.einsum('ij,ij->i',v-u,bhat))/den[:,0])
            update('BF16_projection_scaled',np.abs(np.einsum('ij,ij->i',cast-u,bhat))/den[:,0])
            old,new=(data[prefix+'_'+k].astype(np.float64) for k in ('native_residual','changed_residual'))
            update('actual_residual_norm_relative',np.abs(np.linalg.norm(new,axis=1)-np.linalg.norm(old,axis=1))/np.maximum(np.linalg.norm(old,axis=1),1e-12))
        vectors+=len(u)
    for key,value in maxima.items():
        limit=.02 if key=='actual_residual_norm_relative' else .01 if key.startswith('BF16') else 1e-4
        if value>limit:raise AssertionError('Independent geometry bound exceeded '+key+': '+str(value))
    return {'status':'passed','vectors':vectors,'maxima':maxima}


def verify():
    plan=read(ROOT/'plan.json');summary=read(ROOT/'summary.json')
    for name,expected in plan['source_sha256'].items():
        if sha(Path(__file__).parent/name)!=expected:raise AssertionError('Frozen source changed '+name)
    if sha(plan['references']['path'])!=plan['references']['sha256']:raise AssertionError('Reference changed')
    native={};cross=None;raws={}
    for name in (*NAMES,'cross'):
        manifest=read(ROOT/('manifest_'+name+'.json'))
        if manifest['status']!='complete' or manifest['plan_sha256']!=sha(ROOT/'plan.json'):raise AssertionError('Incomplete manifest')
        item=manifest['raw']
        if sha(item['path'])!=item['sha256']:raise AssertionError('Raw changed '+name)
        raws[name]=item['sha256']
        if name=='cross':cross=arrays(item['path'])
        else:native[name]=arrays(item['path'])
    refs=arrays(plan['references']['path'])
    if not np.array_equal(cross['candidate_loglikelihood'][0],refs['cross_raw_LL']):raise AssertionError('Raw replay changed')
    if not np.array_equal(cross['shared_signal_hashes'],refs['cross_signal_hashes']):raise AssertionError('Producer signal hashes changed')
    report=verify_summary(summary,native,cross,refs,plan['file_groups'])
    report['geometry_probes']={name:geometry_probes(read(ROOT/('preflight_'+name+'.json'))['geometry_probes']['path']) for name in NAMES}
    report.update(source_sha256=sha(__file__),plan_sha256=sha(ROOT/'plan.json'),summary_sha256=sha(ROOT/'summary.json'),raw_sha256=raws,
                  independent_implementation='NumPy candidate row loop, window selection means and explicit cluster concatenation. Same fixed draws, no author implementation imported.')
    (ROOT/'independent_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('verify',))
    args=p.parse_args();print(json.dumps(verify(),indent=2))
