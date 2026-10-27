#!/usr/bin/env python3
"""Independent E159 CPU audit. Never imports the production analyzer."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

WB = Path(__file__).resolve().parents[2]
NAMES = ('P', 'A', 'B', 'zero')
METRICS = ('raw_accuracy', 'per_char_accuracy', 'choice_ce', 'answer_token_nll')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def verify_record(rec):
    if sha(rec['path']) != rec['sha256']:
        raise ValueError('hash mismatch: ' + rec['path'])
    if 'raw' in rec:
        verify_record(rec['raw'])


def verify_inputs(result):
    plan, manifest, budget = (read(result / (n + '.json')) for n in ('plan', 'manifest', 'budget'))
    if manifest['status'] != 'complete' or not budget['attempts'] or budget['attempts'][-1]['status'] != 'complete' or any(a['status'] not in ('complete', 'failed') for a in budget['attempts']):
        raise ValueError('run or budget incomplete')
    if sha(result / 'plan.json') != manifest['plan_sha256'] or plan['source_sha256'] != manifest['source_sha256']:
        raise ValueError('plan or source identity mismatch')
    if budget['limit_gpu_seconds'] != plan['limit_gpu_seconds'] or sum(a['gpu_seconds'] for a in budget['attempts']) > budget['limit_gpu_seconds']:
        raise ValueError('budget cap exceeded or inconsistent')
    models = read(WB / 'results/e150/metadata.json')['models']
    parent = read(WB / 'results/e154/metadata.json')['model']
    for name, digest in manifest['source_sha256'].items():
        if '/' in name:
            source, filename = name.split('/', 1)
            record = (parent if source == 'parent' else models[source])['files'][filename]
            path = record['path']
            if record['sha256'] != digest: raise ValueError('asset manifest mismatch: ' + name)
        else:
            path = WB / 'scripts' / name
        if sha(path) != digest:
            raise ValueError('source mismatch: ' + name)
    for key in ('task_input', 'references', 'legacy_cal_input', 'inherited_cross_manifest'):
        verify_record(plan[key])
    for rec in plan['native_reference_records']:
        verify_record(rec)
    if sha(WB / 'results/e153/data_plan.json') != plan['task_data_plan_sha256']:
        raise ValueError('task plan mismatch')
    verify_record(manifest['raw'])
    if plan['source_names'] != list(NAMES) or plan['bootstrap']['seed'] != 159001 or plan['bootstrap']['resamples'] != 1000:
        raise ValueError('frozen analysis protocol mismatch')
    if not all(manifest['controls'].values()):
        raise ValueError('control failed')
    return plan, manifest


def metrics(scores, gold, tokens, chars):
    # q is penultimate dimension; score is total candidate log likelihood.
    g = np.broadcast_to(gold, scores.shape[:-1])
    selected = np.take_along_axis(scores, g[..., None], axis=-1)[..., 0]
    tok = np.take_along_axis(np.broadcast_to(tokens, scores.shape), g[..., None], axis=-1)[..., 0]
    m = scores.max(axis=-1)
    ce = m + np.log(np.exp(scores - m[..., None]).sum(-1)) - selected
    return np.stack(((scores.argmax(-1) == g).astype(float),
                     ((scores / chars).argmax(-1) == g).astype(float), ce, -selected / tok), axis=0)


def summary(v, subject, indices):
    # v has question as its final axis; fixed subjects get equal weight.
    point = (v[..., subject == 0].mean(-1) + v[..., subject == 1].mean(-1)) / 2
    boot = (v[..., indices[0]].mean(-1) + v[..., indices[1]].mean(-1)) / 2
    lo, hi = np.percentile(boot, [2.5, 97.5], axis=-1)
    return {'point': point.tolist(), 'ci95': np.stack((lo, hi), axis=-1).tolist(),
            'subject_points': [v[..., subject == s].mean(-1).tolist() for s in (0, 1)],
            'subject_ci95': [np.moveaxis(np.percentile(v[..., indices[s]].mean(-1), [2.5,97.5], axis=-1), 0, -1).tolist() for s in (0,1)]}


def primary(scores, native, gold, subject, tokens, chars):
    m = metrics(scores, gold, tokens, chars)
    n = metrics(native, gold, tokens, chars)
    # Accuracy is benefit from preserving a path; losses are removal minus full.
    direction = np.array([-1, -1, 1, 1])[:, None, None, None]
    shared = direction * (m[:, :3, 3, :][:, :, None, :] - m[:, :3, :3, :])
    routed = direction * (m[:, 3, :3, :][:, None, :, :] - m[:, :3, :3, :])
    ns = direction[:, :, 0, :] * (n[:, :, 2, :] - n[:, :, 0, :])
    nr = direction[:, :, 0, :] * (n[:, :, 1, :] - n[:, :, 0, :])
    rng = np.random.default_rng(159001)
    idx = [rng.choice(np.flatnonzero(subject == s), size=(1000, int((subject == s).sum())), replace=True) for s in (0, 1)]
    out = {}
    def put(key, value): out[key] = summary(value, subject, idx)
    put('all_16_cells', m)
    for label, value in [('shared', shared), ('routed', routed), ('balance_shared_minus_routed', shared-routed)]:
        put(label, value)
        put(label + '_fixed_S_change_R_A_B_minus_P', value[:, 1:3, :, :] - value[:, 0:1, :, :])
        put(label + '_fixed_R_change_S_A_B_minus_P', value[:, :, 1:3, :] - value[:, :, 0:1, :])
        put(label + '_AA_BB_minus_PP', np.stack((value[:, 1, 1]-value[:, 0, 0], value[:, 2, 2]-value[:, 0, 0]), axis=1))
    put('full_AA_BB_minus_PP', np.stack((m[:, 1, 1]-m[:, 0, 0], m[:, 2, 2]-m[:, 0, 0]), axis=1))
    for label, value in [('shared', ns), ('routed', nr), ('balance_shared_minus_routed', ns-nr)]:
        put('native_' + label, value)
        put('native_' + label + '_A_B_minus_P', value[:, 1:3] - value[:, 0:1])
        counterpart = {'shared': shared, 'routed': routed, 'balance_shared_minus_routed': shared-routed}[label]
        put('native_B_minus_common_body_BB_' + label, value[:, 2] - counterpart[:, 2, 2])
    put('native_full', n[:, :, 0]); put('native_B_minus_common_body_BB_full', n[:, 2, 0]-m[:, 2, 2])
    return out


def secondary(scores, gold, subject, cohort):
    correct = scores.argmax(-1) == gold
    patterns = (4 * correct[3, 3] + 2 * correct[:3, 3, None, :] + correct[3, None, :3, :]).astype(int)
    result = {'definition': '4=D only, 2=R alone, 1=S alone; full correct required', 'cells': {}, 'transitions': {}}
    for r in range(3):
        for s in range(3):
            if not correct[r, s, cohort].all(): raise ValueError('cohort not full-correct')
            counts = [np.bincount(patterns[r,s,cohort & (subject == j)], minlength=8) for j in (0,1)]
            pooled = counts[0] + counts[1]
            macro = (counts[0]/counts[0].sum() + counts[1]/counts[1].sum())/2
            result['cells'][NAMES[r]+NAMES[s]] = {'subject_counts': [x.tolist() for x in counts], 'pooled_counts': pooled.tolist(), 'pooled_rates': (pooled/pooled.sum()).tolist(), 'equal_subject_rates': macro.tolist()}
    for fixed_axis in ('S', 'R'):
        for fixed in range(3):
            for a,b in ((0,1),(0,2),(1,2)):
                x,y = (patterns[a,fixed],patterns[b,fixed]) if fixed_axis == 'S' else (patterns[fixed,a],patterns[fixed,b])
                tables = [np.bincount((8*x+y)[cohort & (subject == j)], minlength=64).reshape(8,8) for j in (0,1)]
                result['transitions'][f'fixed_{fixed_axis}_{NAMES[fixed]}_{NAMES[a]}_to_{NAMES[b]}'] = {'subject_counts':[t.tolist() for t in tables], 'pooled_counts':(tables[0]+tables[1]).tolist(), 'pooled_rates':((tables[0]+tables[1])/sum(t.sum() for t in tables)).tolist(), 'equal_subject_rates':((tables[0]/tables[0].sum()+tables[1]/tables[1].sum())/2).tolist()}
    return result


def validate(a, plan, manifest):
    shapes = {'candidate_loglikelihood':(4,4,128,4),'native_reference_candidate_loglikelihood':(3,4,128,4),'measured_cells':(4,4),'gold':(128,), 'subject':(128,), 'answer_tokens':(128,4),'answer_chars':(128,4),'all_nine_full_success':(128,), 'common_native_success':(128,)}
    for k, shape in shapes.items():
        if a[k].shape != shape: raise ValueError('shape: '+k)
    if tuple(a['source_names']) != NAMES or any(not np.isfinite(a[k]).all() for k in ('candidate_loglikelihood','native_reference_candidate_loglikelihood')): raise ValueError('sources or scores')
    if not np.array_equal(np.bincount(a['subject'], minlength=2), [64,64]) or np.any((a['gold']<0)|(a['gold']>3)) or np.any(a['answer_tokens']<=0) or np.any(a['answer_chars']<=0): raise ValueError('population or denominators')
    expected = np.zeros((4,4), bool)
    for r,s in plan['measured_cells']: expected[r,s]=True
    frozen = {(0,0),(3,0),(3,1),(3,2),(0,3),(1,3),(2,3),(3,3)}
    if set(map(tuple, plan['measured_cells'])) != frozen: raise ValueError('unexpected measured cells')
    if not np.array_equal(a['measured_cells'], expected) or plan['measured_cells'] != manifest['measured_cells'] or expected.sum()!=8: raise ValueError('measured cells')
    c = (a['candidate_loglikelihood'][:3,:3].argmax(-1)==a['gold']).all((0,1))
    if not np.array_equal(c,a['all_nine_full_success']) or [int((c & (a['subject']==s)).sum()) for s in (0,1)] != [30,3]: raise ValueError('fixed cohort')
    common = (a['native_reference_candidate_loglikelihood'][:,0].argmax(-1)==a['gold']).all(0)
    if not np.array_equal(common,a['common_native_success']) or [int((common & (a['subject']==s)).sum()) for s in (0,1)] != [36,8]: raise ValueError('native cohort')
    ref = np.load(plan['references']['path'], allow_pickle=False)
    for k in ('native_reference_candidate_loglikelihood','all_nine_full_success','common_native_success','gold','subject','answer_tokens','answer_chars'):
        if not np.array_equal(a[k],ref[k]): raise ValueError('reference mismatch '+k)
    if not np.array_equal(a['candidate_loglikelihood'][:3,:3],ref['full_candidate_loglikelihood']): raise ValueError('inherited cross mismatch')
    for cell, condition in [((0,0),0),((3,0),1),((0,3),2),((3,3),3)]:
        if not np.array_equal(a['candidate_loglikelihood'][cell], a['native_reference_candidate_loglikelihood'][0,condition]): raise ValueError('P replay mismatch')


def self_test():
    gold=np.zeros(8,dtype=int); subj=np.array([0]*4+[1]*4); den=np.ones((8,4))
    scores=np.zeros((4,4,8,4)); scores[...,1]=-1; scores[...,2:]=-2
    for q in range(8):
        for r,s,bit in [(3,3,4),(0,3,2),(3,0,1)]: scores[r,s,q,0] = 1 if q & bit else -2
    patterns=(4*(scores[3,3].argmax(-1)==gold)+2*(scores[0,3].argmax(-1)==gold)+(scores[3,0].argmax(-1)==gold))
    assert np.array_equal(patterns,np.arange(8))
    mm=metrics(scores,gold,den,den); assert mm[0,0,0].all() and np.allclose(mm[3,3,3],-scores[3,3,:,0])
    native=np.zeros((3,4,8,4)); native[...,1:]=-1
    p=primary(scores,native,gold,subj,den,den)
    assert np.isclose(p['shared']['point'][0][0][0], (mm[0,0,0]-mm[0,0,3]).mean())
    assert np.isclose(p['routed']['point'][0][0][0], (mm[0,0,0]-mm[0,3,0]).mean())
    rng=np.random.default_rng(159001); idx=[rng.choice(np.flatnonzero(subj==s),size=(1000,4),replace=True) for s in (0,1)]
    v=np.ones(8)*3; assert summary(v,subj,idx)['ci95']==[3.,3.]
    assert secondary(scores,gold,subj,np.ones(8,dtype=bool))['cells']['PP']['pooled_counts']==[1]*8
    print('self-tests passed')


def known_border_review():
    """Read only E155/E156 completed records and compare inherited-only review."""
    report = read(WB/'results/e159/known_border_posthoc.json')
    if report['status'] != 'complete_POST_HOC_inherited_only' or report['new_model_forwards'] != 0: raise ValueError('unexpected report')
    inputs = report['inputs']; raws=[]; manifests=[]
    for rec in inputs['E155'] + [inputs['E156']]:
        verify_record(rec['manifest']); verify_record(rec['raw'])
        manifest = read(rec['manifest']['path'])
        if manifest['status'] != 'complete' or manifest['raw']['sha256'] != rec['raw']['sha256'] or manifest['raw']['path'] != rec['raw']['path']: raise ValueError('manifest/raw mismatch')
        manifests.append(manifest)
        with np.load(rec['raw']['path'],allow_pickle=False) as f: raws.append({k:f[k] for k in f.files})
    cross=raws[3]; native=raws[:3]; cm=manifests[3]
    for i in range(3):
        if manifests[i]['source'] != NAMES[i] or manifests[i]['source_parameter_hash'] != cm['source_parameter_hashes'][i] or manifests[i]['source_buffer_hash'] != cm['source_buffer_hashes'][i]: raise ValueError('canonical source identity mismatch')
        for k in ('gold','subject','answer_tokens','answer_chars'):
            if not np.array_equal(native[i][k],cross[k]): raise ValueError('population mismatch '+k)
        if tuple(native[i]['conditions']) != ('native','routed_zero','shared_zero','all_moe_zero'): raise ValueError('condition order')
    gold,subj,tok,ch = (cross[k] for k in ('gold','subject','answer_tokens','answer_chars'))
    if not np.array_equal(np.bincount(subj),[64,64]): raise ValueError('subject count')
    full=cross['candidate_loglikelihood'][:,:,0]; cohort=(full.argmax(-1)==gold).all((0,1))
    if [int((cohort&(subj==i)).sum()) for i in (0,1)] != [30,3]: raise ValueError('cohort')
    nm=metrics(np.stack([x['candidate_loglikelihood'] for x in native]),gold,tok,ch)
    gm=metrics(full,gold,tok,ch)
    rng=np.random.default_rng(159001)
    idx=[rng.choice(np.flatnonzero(subj==s),size=(1000,64),replace=True) for s in (0,1)]
    point_errors=[]; ci_errors=[]; subject_point_errors=[]; counts_match=True; computed={}
    metric_names=('raw_accuracy','per_char_accuracy','choice_CE','true_answer_token_NLL')
    for i,name in enumerate(NAMES[:3]):
        computed[name]={}
        for j,metric in enumerate(metric_names):
            sign=-1 if j<2 else 1
            nf=nm[j,i,0]; sf=gm[j,0,i]; rf=gm[j,i,0]
            ns=sign*(nm[j,i,2]-nf); gs=sign*(nm[j,0,2]-sf)
            nr=sign*(nm[j,i,1]-nf); gr=sign*(nm[j,0,1]-rf)
            vals={'native_full_quality':nf, 'S_only_graft_full_quality':sf, 'R_only_graft_full_quality':rf, 'native_shared_necessity':ns, 'same_S_in_P_receiver_necessity':gs, 'native_minus_same_S_receiver_necessity':ns-gs, 'native_routed_necessity':nr, 'same_R_in_P_receiver_necessity':gr, 'native_minus_same_R_receiver_necessity':nr-gr}
            computed[name][metric]={}
            for key,v in vals.items():
                got=summary(v,subj,idx); target=report['metrics'][metric][name][key]
                point_errors.append(abs(got['point']-target['point']))
                ci_errors.extend(abs(np.array(got['ci95'])-target['question_ci95']))
                for k,subject_name in enumerate(('high_school_biology','high_school_mathematics')):
                    subject_point_errors.append(abs(got['subject_points'][k]-target['per_subject'][subject_name]['point']))
                    draws=v[idx[k]].mean(-1)
                    ci_errors.extend(abs(np.percentile(draws,[2.5,97.5])-target['per_subject'][subject_name]['question_ci95']))
                computed[name][metric][key]=got
        conditions={'native_full':native[i]['candidate_loglikelihood'][0], 'S_only_graft_full':full[0,i], 'R_only_graft_full':full[i,0], 'native_without_S':native[i]['candidate_loglikelihood'][2], 'same_S_graft_without_S_inherited_P':native[0]['candidate_loglikelihood'][2], 'native_without_R':native[i]['candidate_loglikelihood'][1], 'same_R_graft_without_R_inherited_P':native[0]['candidate_loglikelihood'][1]}
        computed[name]['cohort_counts']={}
        for key,score in conditions.items():
            correct=(score.argmax(-1)==gold)&cohort
            counts=[int((correct&(subj==s)).sum()) for s in (0,1)]
            obj={'total':sum(counts),'per_subject':counts}
            counts_match &= obj==report['same_correct_decision_counts'][name][key]
            computed[name]['cohort_counts'][key]=obj
    return {'status':'passed' if max(point_errors+ci_errors+subject_point_errors)<1e-10 and counts_match else 'mismatch', 'scope':'POST-HOC E155/E156 inherited endpoints; zero new forwards; not a fixed-partner isolation', 'input_report_sha256':sha(WB/'results/e159/known_border_posthoc.json'), 'input_raw_sha256':[m['raw']['sha256'] for m in manifests], 'canonical_parameter_buffer_hashes_match':True, 'cohort':[30,3], 'max_point_error':max(point_errors), 'max_subject_point_error':max(subject_point_errors), 'max_ci_error':max(ci_errors), 'all_counts_match':bool(counts_match), 'independent_estimates':computed}

def compare_summary(report, a, manifest, plan, plan_path):
    if report['experiment'] != 'E159' or report['status'] != 'complete' or report['raw_sha256'] != manifest['raw']['sha256'] or report['plan_sha256'] != sha(plan_path) or report['source_order'] != list(NAMES): raise ValueError('summary provenance mismatch')
    if report['analysis_source_sha256'] != manifest['source_sha256']['e159_analyze.py']: raise ValueError('analysis source mismatch')
    scores=a['candidate_loglikelihood']; native=a['native_reference_candidate_loglikelihood']; gold=a['gold']; subj=a['subject']; tok=a['answer_tokens']; chars=a['answer_chars']; cohort=a['all_nine_full_success']
    m=metrics(scores,gold,tok,chars); n=metrics(native,gold,tok,chars)
    sign=np.array([-1,-1,1,1])[:,None,None,None]
    sv=sign*(m[:,:3,3,:][:,:,None,:]-m[:,:3,:3,:]); rv=sign*(m[:,3,:3,:][:,None,:,:]-m[:,:3,:3,:]); bv=sv-rv
    ns=sign[:,:,0,:]*(n[:,:,2,:]-n[:,:,0,:]); nr=sign[:,:,0,:]*(n[:,:,1,:]-n[:,:,0,:]); nb=ns-nr
    rng=np.random.default_rng(159001); idx=[rng.choice(np.flatnonzero(subj==s),size=(1000,64),replace=True) for s in (0,1)]
    point_error=[]; ci_error=[]; count_checks=[]
    def chk(v,t):
        z=summary(v,subj,idx); point_error.append(abs(z['point']-t['point'])); ci_error.extend(abs(np.array(z['ci95'])-t['question_ci95']))
        if t['bootstrap_seed']!=159001 or t['bootstrap_replicates']!=1000: raise ValueError('bootstrap metadata')
        for k,name in enumerate(('high_school_biology','high_school_mathematics')):
            st=t['per_subject'][name]; count_checks.append(st['n']==64); point_error.append(abs(z['subject_points'][k]-st['point'])); ci_error.extend(abs(np.array(z['subject_ci95'][k])-st['question_ci95']))
    def cp(v,t):
        if not isinstance(t['overall_point_definition'],str) or not t['overall_point_definition']: raise ValueError('missing pooled definition')
        point_error.append(abs(float(v[cohort].mean())-t['overall_point']))
        pts=[float(v[cohort & (subj==s)].mean()) for s in (0,1)]
        point_error.append(abs(sum(pts)/2-t['equal_subject_macro_point']))
        for k,name in enumerate(('high_school_biology','high_school_mathematics')): point_error.append(abs(pts[k]-t['per_subject_point'][name]))
    def walk(k,report_metric,fn):
        for r in range(4):
            for s in range(4): fn(m[k,r,s],report_metric['full_and_border_table'][NAMES[r]+NAMES[s]])
        for r in range(3):
            for s in range(3):
                cell=NAMES[r]+NAMES[s]
                for label,values in (('shared_necessity',sv),('routed_necessity',rv),('shared_minus_routed_necessity',bv)): fn(values[k,r,s],report_metric[label][cell])
        for i,diff in ((1,'A-P'),(2,'B-P')):
            for j,name in enumerate(NAMES[:3]):
                fn(sv[k,i,j]-sv[k,0,j],report_metric['unchanged_partner']['shared_necessity_fixed_S'][diff][name])
                fn(rv[k,j,i]-rv[k,j,0],report_metric['unchanged_partner']['routed_necessity_fixed_R'][diff][name])
            for label,values in (('shared',sv),('routed',rv)): fn(values[k,i,i]-values[k,0,0],report_metric['diagonal_necessity_contrasts'][diff][label])
    for k,key in enumerate(('raw_accuracy','per_char_accuracy','choice_CE','true_answer_token_NLL')):
        obj=report['metrics'][key]; walk(k,obj,chk); walk(k,obj['all_nine_full_correct_points'],cp)
        nc=obj['native_context']
        for i,diff in ((1,'native_A-P'),(2,'native_B-P')): chk(n[k,i,0]-n[k,0,0],nc['full_quality_differences'][diff])
        chk(n[k,2,0]-m[k,2,2],nc['full_quality_differences']['native_B_minus_BB'])
        for label,values,common in (('shared',ns,sv),('routed',nr,rv),('balance',nb,bv)):
            for i,name in enumerate(NAMES[:3]): chk(values[k,i],nc['necessity'][name][label])
            for i,diff in ((1,'native_A-P'),(2,'native_B-P')): chk(values[k,i]-values[k,0],nc['necessity_differences'][diff][label])
            chk(values[k,2]-common[k,2,2],nc['necessity_differences']['native_B_minus_BB'][label])
    sec=secondary(scores,gold,subj,cohort); sec_report=report['all_nine_full_success']
    count_checks += [sec_report['count']==33,sec_report['per_subject']==[30,3]]
    patterns=sec_report['patterns']; count_checks += [patterns['bit_order']=={'D':4,'R_alone':2,'S_alone':1},isinstance(patterns['pattern_0'],str)]
    for cell,val in sec['cells'].items():
        t=patterns['cells'][cell]; count_checks += [t['counts']==val['pooled_counts'],t['per_subject_counts']['high_school_biology']==val['subject_counts'][0],t['per_subject_counts']['high_school_mathematics']==val['subject_counts'][1]]
    for axis in ('S','R'):
        for fixed in NAMES[:3]:
            for source in ('A','B'):
                v=sec['transitions'][f'fixed_{axis}_{fixed}_P_to_{source}']; t=patterns['transitions']['fixed_'+axis][source+'_at_'+fixed]
                count_checks += [t['counts']==v['pooled_counts'],t['per_subject_counts']['high_school_biology']==v['subject_counts'][0],t['per_subject_counts']['high_school_mathematics']==v['subject_counts'][1]]
    err=max(point_error+ci_error,default=0.)
    return {'status':'passed' if err<1e-10 and all(count_checks) else 'mismatch','max_point_error':max(point_error,default=0.),'max_ci_error':max(ci_error,default=0.),'count_checks':len(count_checks),'all_counts_match':all(count_checks),'numeric_comparisons':len(point_error)+len(ci_error)}

def comparator_self_test():
    # Uniform candidate scores, all labels zero: every full and ablation is correct.
    from tempfile import TemporaryDirectory
    q=128; subj=np.repeat([0,1],64); cohort=np.zeros(q,bool); cohort[:30]=True; cohort[64:67]=True
    a={'candidate_loglikelihood':np.zeros((4,4,q,4)), 'native_reference_candidate_loglikelihood':np.zeros((3,4,q,4)), 'gold':np.zeros(q,int),'subject':subj,'answer_tokens':np.ones((q,4)),'answer_chars':np.ones((q,4)),'all_nine_full_success':cohort}
    def stat(x): return {'point':x,'question_ci95':[x,x],'per_subject':{name:{'point':x,'question_ci95':[x,x],'n':64} for name in ('high_school_biology','high_school_mathematics')},'bootstrap_seed':159001,'bootstrap_replicates':1000}
    def cstat(x): return {'overall_point':x,'overall_point_definition':'pooled','equal_subject_macro_point':x,'per_subject_point':{name:x for name in ('high_school_biology','high_school_mathematics')}}
    def table(full,zero,make):
        return {'full_and_border_table':{r+s:make(full) for r in NAMES for s in NAMES}, **{key:{r+s:make(zero) for r in NAMES[:3] for s in NAMES[:3]} for key in ('shared_necessity','routed_necessity','shared_minus_routed_necessity')}, 'unchanged_partner':{key:{diff:{name:make(zero) for name in NAMES[:3]} for diff in ('A-P','B-P')} for key in ('shared_necessity_fixed_S','routed_necessity_fixed_R')}, 'diagonal_necessity_contrasts':{diff:{key:make(zero) for key in ('shared','routed')} for diff in ('A-P','B-P')}}
    values={}
    for metric,full in (('raw_accuracy',1.),('per_char_accuracy',1.),('choice_CE',float(np.log(4))),('true_answer_token_NLL',0.)):
        row=table(full,0.,stat); row['all_nine_full_correct_points']=table(full,0.,cstat)
        row['native_context']={'full_quality_differences':{key:stat(0.) for key in ('native_A-P','native_B-P','native_B_minus_BB')}, 'necessity':{name:{k:stat(0.) for k in ('shared','routed','balance')} for name in NAMES[:3]},'necessity_differences':{name:{k:stat(0.) for k in ('shared','routed','balance')} for name in ('native_A-P','native_B-P','native_B_minus_BB')}}; values[metric]=row
    sec=secondary(a['candidate_loglikelihood'],a['gold'],subj,cohort)
    def counts(v): return {'counts':v['pooled_counts'],'per_subject_counts':dict(zip(('high_school_biology','high_school_mathematics'),v['subject_counts']))}
    pattern={'bit_order':{'D':4,'R_alone':2,'S_alone':1},'pattern_0':'all fail','cells':{k:counts(v) for k,v in sec['cells'].items()},'transitions':{}}
    for axis in ('S','R'):
        pattern['transitions']['fixed_'+axis]={source+'_at_'+fixed:counts(sec['transitions'][f'fixed_{axis}_{fixed}_P_to_{source}']) for fixed in NAMES[:3] for source in ('A','B')}
    with TemporaryDirectory() as tmp:
        path=Path(tmp)/'plan.json'; path.write_text('{}'); manifest={'raw':{'sha256':'synthetic'},'source_sha256':{'e159_analyze.py':'synthetic'}}
        report={'experiment':'E159','status':'complete','raw_sha256':'synthetic','plan_sha256':sha(path),'analysis_source_sha256':'synthetic','source_order':list(NAMES),'metrics':values,'all_nine_full_success':{'count':33,'per_subject':[30,3],'patterns':pattern}}
        assert compare_summary(report,a,manifest,{},path)['status']=='passed'
        report['metrics']['raw_accuracy']['unchanged_partner']['shared_necessity_fixed_S']['A-P']['B']['point']=1.
        assert compare_summary(report,a,manifest,{},path)['status']=='mismatch'
    print('comparator synthetic mapping and mismatch detection passed')

def known_lm_review():
    report=read(WB/'results/e159/known_lm_border_posthoc.json')
    if report['status']!='complete_POST_HOC_inherited_only' or report['new_model_forwards']!=0: raise ValueError('unexpected report')
    data=[]; manifests=[]
    for name in ('E150','E151'):
        record=report['inputs'][name]; verify_record(record['manifest']); verify_record(record['raw'])
        manifest=read(record['manifest']['path'])
        if manifest['status']!='complete' or manifest['raw']['sha256']!=record['raw']['sha256'] or manifest['raw']['path']!=record['raw']['path']: raise ValueError('manifest identity')
        manifests.append(manifest)
        with np.load(record['raw']['path'],allow_pickle=False) as f: data.append({k:f[k] for k in ('metrics','valid','fields',*(['cases'] if name=='E150' else ['conditions']))})
    cube,abl=data; c=manifests[0]; a=manifests[1]
    if c['source_parameter_hashes']!=a['parameter_hashes'] or c['source_buffer_hashes']!=a['buffer_hashes']: raise ValueError('parameter/buffer identities differ')
    if not np.array_equal(cube['valid'],abl['valid']) or cube['metrics'].shape!=(16,64,512,2,4) or abl['metrics'].shape!=(2,6,64,512,4) or cube['fields'][0]!='nll' or abl['fields'][0]!='nll': raise ValueError('shape or valid mask mismatch')
    if tuple(abl['conditions'][:3])!=('native','routed_zero','shared_zero') or not np.array_equal(cube['metrics'][:,:,:,0,0],cube['metrics'][:,:,:,1,0]): raise ValueError('NLL reference or condition mismatch')
    mask=cube['valid']; counts=mask.sum(-1)
    if np.any(counts==0): raise ValueError('empty window')
    case_map={tuple(row):i for i,row in enumerate(cube['cases'])}
    if len(case_map)!=16: raise ValueError('case map')
    for b in (0,1):
        native=cube['metrics'][case_map[(b,b,b,b)],:,:,0,0]
        if not np.array_equal(native[mask],abl['metrics'][b,0,:,:,0][mask]): raise ValueError('native token replay')
    plan_path=WB/'results/e150/plan.json'
    if sha(plan_path)!=c['input_plan_sha256']: raise ValueError('input plan hash')
    selected=read(plan_path)['selected']
    if len(selected)!=64 or [v['sequence'] for v in selected]!=list(range(64)): raise ValueError('window order')
    keys=[(v['source'],v['file_id']) for v in selected]; unique=list(dict.fromkeys(keys))
    if len(unique)!=20: raise ValueError('cluster count')
    ids=np.array([unique.index(k) for k in keys]); rng=np.random.default_rng(159002); draws=rng.integers(0,20,size=(1000,20))
    weights=np.stack([(ids==i).astype(int) for i in range(20)])
    sampled=weights[draws].sum(axis=1)
    def window(v): return np.where(mask,v,0).sum(axis=-1,dtype=np.float64)/counts
    def stats(v):
        replicates=(sampled @ v)/sampled.sum(axis=1)
        return {'point':float(v.mean()),'input_file_ci95':np.percentile(replicates,[2.5,97.5]).tolist()}
    computed={}; pe=[]; ce=[]
    def compare(label,v,target):
        z=stats(v); pe.append(abs(z['point']-target['point'])); ce.extend(abs(np.array(z['input_file_ci95'])-target['input_file_ci95']))
        if target['file_clusters']!=20 or target['sequences']!=64 or target['bootstrap_seed']!=159002: raise ValueError('bootstrap metadata')
        return z
    for branch,axis,cond in (('shared',3,2),('routed',2,1)):
        group=report['branches'][branch]; computed[branch]={}; damages=np.empty((2,2,64))
        for b in (0,1):
            for f in (0,1):
                case=[b,b,b,b]; case[axis]=f
                full=window(cube['metrics'][case_map[tuple(case)],:,:,0,0]); removed=window(abl['metrics'][b,cond,:,:,0]); damage=removed-full; damages[b,f]=damage
                key=f'background_{"AB"[b]}_function_{"AB"[f]}'; target=group[key]
                computed[branch][key]={k:compare(k,v,target[k]) for k,v in (('full_NLL',full),('removed_NLL_inherited',removed),('removal_delta_NLL',damage))}
        diffs=damages[1]-damages[0]
        for f in (0,1):
            key=f'same_function_{"AB"[f]}_background_B_minus_A'; computed[branch][key]=compare(key,diffs[f],group[key])
        key='mean_background_B_minus_A'; computed[branch][key]=compare(key,diffs.mean(axis=0),group[key])
    return {'status':'passed' if max(pe+ce)<1e-10 else 'mismatch','scope':'POST-HOC E150/E151 inherited endpoints; zero new forwards; background includes D/G and other branch', 'report_sha256':sha(WB/'results/e159/known_lm_border_posthoc.json'),'raw_sha256':[m['raw']['sha256'] for m in manifests], 'parameter_buffer_hashes_match':True,'native_per_token_replays_exact':True,'valid_masks_match':True,'real_targets':int(mask.sum()),'file_clusters':20,'max_point_error':max(pe),'max_ci_error':max(ce),'independent_estimates':computed}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--self-test',action='store_true'); parser.add_argument('--known-border-review',action='store_true'); parser.add_argument('--known-lm-review',action='store_true'); parser.add_argument('--result',type=Path,default=WB/'results/e159'); parser.add_argument('--output',type=Path); parser.add_argument('--compare-summary',type=Path)
    args=parser.parse_args()
    if args.self_test: self_test(); comparator_self_test(); return
    if args.known_lm_review:
        if args.output is None: parser.error('--output required')
        review=known_lm_review(); args.output.write_text(json.dumps(review,indent=2,allow_nan=False)+'\n'); print(json.dumps({k:v for k,v in review.items() if k!='independent_estimates'},indent=2)); return
    if args.known_border_review:
        if args.output is None: parser.error('--output required')
        review=known_border_review(); args.output.write_text(json.dumps(review,indent=2,allow_nan=False)+'\n'); print(json.dumps({k:v for k,v in review.items() if k!='independent_estimates'},indent=2)); return
    if args.output is None: parser.error('--output required; run only after completion authorization')
    plan,manifest=verify_inputs(args.result)
    with np.load(manifest['raw']['path'],allow_pickle=False) as f: a={k:f[k] for k in f.files}
    validate(a,plan,manifest)
    out={'protocol':{'metrics':METRICS,'source_order':NAMES,'subject_order':['biology','mathematics'],'bootstrap':'1000 paired resamples within each subject, seed 159001, equal-subject macro','raw_sha256':manifest['raw']['sha256']},'primary':primary(a['candidate_loglikelihood'],a['native_reference_candidate_loglikelihood'],a['gold'],a['subject'],a['answer_tokens'],a['answer_chars']),'secondary_33':secondary(a['candidate_loglikelihood'],a['gold'],a['subject'],a['all_nine_full_success'])}
    if args.compare_summary: out['summary_comparison']=compare_summary(read(args.compare_summary),a,manifest,plan,args.result/'plan.json')
    args.output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')

if __name__=='__main__': main()
