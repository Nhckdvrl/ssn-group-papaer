#!/usr/bin/env python3
"""E67 frozen cache analysis: group OOF transport, raw human deltas, validity gates."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import spearmanr


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def source(item):
    if item.startswith('swb_'):
        return item.split('_utt@')[0]
    if item.startswith('wsj_'):
        if item.startswith('wsj_not_found_'):
            return 'wsj_unknown_origin'
        article=re.match(r'wsj_\d+',item)
        assert article, item
        return article.group(0)
    return re.sub(r'_\d+$', '', item)


def folds(ids,seed):
    counts=Counter(source(i) for i in ids)
    gs=sorted(counts)
    np.random.default_rng(seed).shuffle(gs)
    gs.sort(key=lambda g:-counts[g])
    loads=[0]*5;assignment={}
    for g in gs:
        k=int(np.argmin(loads));loads[k]+=counts[g];assignment[g]=k
    out=np.array([assignment[source(i)] for i in ids])
    assert set(out)==set(range(5))
    return out,assignment


def ci(x,ids):
    # Fixed OOF fits, source bootstrap; ratio retains unequal cluster weights.
    groups=sorted({source(i) for i in ids})
    if len(groups)<2:
        return dict(mean=float(np.mean(x)),ci95=None,source_groups=len(groups),n_items=len(ids),
                    limitation='Only one source group: no source-bootstrap uncertainty estimate')
    sums=np.array([sum(v for v,i in zip(x,ids) if source(i)==g) for g in groups])
    sizes=np.array([sum(source(i)==g for i in ids) for g in groups])
    draws=np.random.default_rng(0).multinomial(len(groups),np.ones(len(groups))/len(groups),size=2000)
    bs=(draws@sums)/(draws@sizes)
    return dict(mean=float(np.mean(x)),ci95=np.quantile(bs,[.025,.975]).tolist(),source_groups=len(groups),n_items=len(ids))


def design(p,h,kind):
    # Frozen numerical regularization of saturated source probabilities.
    p=np.clip(p,1e-6,1-1e-6)
    z=np.log(p)-np.log1p(-p)
    state=np.tile([0,1],len(h))
    cols=[z.reshape(-1),np.ones(p.size)]
    if kind in ['condition','human']:cols.append(state)
    if kind=='human':cols.append(state*np.repeat(h,2))
    return np.array(cols).T


def fit_predict(p,t,h,train,test,kind):
    X=design(p,h,kind)
    rows=np.repeat(train,2);held=np.repeat(test,2)
    y=t.reshape(-1)[rows];x=X[rows]
    def loss(w):
        z=x@w
        q=expit(z)
        return float(np.mean(np.logaddexp(0,z)-y*z)+1e-6*np.dot(w,w)), x.T@(q-y)/len(y)+2e-6*w
    w=np.zeros(X.shape[1]);w[0]=1
    opt=minimize(loss,w,jac=True,method='L-BFGS-B',bounds=[(0,8)]+[(-20,20)]*(len(w)-1),
                 options={'maxiter':2000,'ftol':1e-13,'gtol':1e-8})
    assert opt.success, opt.message
    return expit(X[held]@opt.x).reshape(-1,2),opt.x.tolist()


def oof(p,t,h,ids,seed,kind):
    f,assignment=folds(ids,seed)
    pred=np.zeros_like(t);params=[]
    for k in range(5):
        tr=f!=k;te=f==k
        out,w=fit_predict(p,t,h,tr,te,kind)
        pred[te]=out;params.append(dict(fold=k,parameters=w,n_train=int(tr.sum()),n_test=int(te.sum())))
        assert not {source(i) for i,v in zip(ids,tr) if v} & {source(i) for i,v in zip(ids,te) if v}
    return pred,params,assignment


def read_run(run,split=False):
    cfg=json.loads((run/'config.json').read_text())
    assert cfg['complete'] and cfg['numerical_gate_pass'] and cfg['dtype']=='float32'
    files=[run/'predictions.jsonl'] if split else [run/(c+'-predictions.jsonl') for c in ['parent','format']]
    rows=[json.loads(line) for p in files for line in p.read_text().splitlines()]
    if split:
        assert sha(files[0])==cfg['output_sha256'] and len(rows)==cfg['n_rows']
    for r in rows:
        assert len(r['label_probs'])==2 and abs(sum(r['label_probs'])-1)<1e-6
        assert abs(r['p_true']-r['label_probs'][int(r['true_label'])-1])<1e-8
        assert 0<=r['support_mass']<=1.00001
    return rows,cfg,{str(p):sha(p) for p in files+[run/'config.json']}


def arrays(rows,ids,c,order):
    natural={ (r['item_id'],r['state'],r['true_label']):r for r in rows
             if r['condition']==c and r.get('kind','natural')=='natural' and r['state'] in ['baseline','cancel']}
    assert len(natural)==271*4
    orders=['1','2'] if order=='average' else [order]
    p=np.array([[np.mean([natural[i,s,o]['p_true'] for o in orders]) for s in ['baseline','cancel']] for i in ids])
    return p,natural


def diagnostics(rows,ids,c):
    p,rs=arrays(rows,ids,c,'average')
    controls=[r for r in rows if r['condition']==c and r.get('kind')=='control']
    differences=[abs(rs[i,s,'1']['p_true']-rs[i,s,'2']['p_true']) for i in ids for s in ['baseline','cancel']]
    mass=float(np.mean([rs[i,s,o]['support_mass'] for i in ids for s in ['baseline','cancel'] for o in ['1','2']]))
    accuracy=None if not controls else float(np.mean([(r['p_true']>.5)==r['expected_true'] for r in controls]))
    med=float(np.median(differences))
    return dict(mean_mass=mass,median_order_difference=med,mean_order_difference=float(np.mean(differences)),
                fraction_order_class_disagreement=float(np.mean([(rs[i,s,'1']['p_true']>.5)!=(rs[i,s,'2']['p_true']>.5) for i in ids for s in ['baseline','cancel']])),
                n_controls=len(controls),control_accuracy=accuracy,
                gate_pass=None if accuracy is None else mass>=.8 and accuracy>=.9 and med<=.15)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    human={r['item_id']:r for r in [json.loads(x) for x in (a.root/'data/E66-canonical-human-audit/items.jsonl').read_text().splitlines()]}
    # Post-hoc technical sensitivity: literal annotation tokens may not render
    # in the human innerHTML UI. Retain frozen 243 cohort; never select by effects.
    cue_risks={i for i,r in human.items() if any(re.search(r'<\s*/?\s*[\w-]+',c['model_scenario']) for c in r['conditions'].values())}
    models={};hashes={};configs={}
    for stage in ['SFT','DPO']:
        allrows=[];confs=[]
        for k in range(4):
            rows,cfg,h=read_run(a.root/'runs'/f'E67-canonical-{stage}-shard{k}',True)
            allrows+=rows;confs.append(cfg);hashes.update(h)
        assert len(allrows)==(1084+128)*2
        keys=[(r['kind'],r['item_id'],r['state'],r['true_label'],r['condition']) for r in allrows]
        assert len(keys)==len(set(keys))
        models[stage]=allrows;configs[stage]=confs
    for k in range(4):
        assert configs['SFT'][k]['input_token_hashes']==configs['DPO'][k]['input_token_hashes']
        assert configs['SFT'][k]['source_audit']==configs['DPO'][k]['source_audit']
    for cp in ['Qwen3-8B','Qwen3-14B']:
        rows,cfg,h=read_run(a.root/'runs'/('E28-implicaturex-'+cp))
        models[cp]=rows;hashes.update(h)
    # Positive control uses known map, the same grouped folds and held-out inputs.
    ids=sorted(human)
    synth=np.random.default_rng(0).uniform(.05,.95,(len(ids),2))
    sy=expit(.7*(np.log(synth)-np.log1p(-synth))+.3)
    yp,_,_=oof(synth,sy,np.zeros(len(ids)),ids,20261003,'global')
    assert float(np.mean((yp-sy)**2))<1e-7
    results={};oofrows=[]
    for scope in ['text_matched','all_canonical','no_ui_cue_risk_sensitivity']:
        ids=sorted(i for i,r in human.items() if scope=='all_canonical' or
                   (r['text_match_both'] and (scope=='text_matched' or i not in cue_risks)))
        h=np.array([human[i]['raw_cancel_delta'] for i in ids]);hz=np.array([human[i]['z_cancel_delta'] for i in ids])
        results[scope]=dict(n=len(ids),source_groups=len({source(i) for i in ids}),human_delta=ci(h,ids),endpoints={},transport={})
        for model,rows in models.items():
            results[scope]['endpoints'][model]={}
            for c in ['parent','format']:
                p,_=arrays(rows,ids,c,'average');delta=p[:,1]-p[:,0]
                byph={}
                for ph in sorted({human[i]['phenomenon'] for i in ids}):
                    ix=[j for j,i in enumerate(ids) if human[i]['phenomenon']==ph]
                    byph[ph]=dict(n=len(ix),mean_baseline=float(p[ix,0].mean()),mean_cancel=float(p[ix,1].mean()),
                                 delta=ci(delta[ix],[ids[j] for j in ix]),human_raw_rho=float(spearmanr(delta[ix],h[ix]).statistic))
                results[scope]['endpoints'][model][c]=dict(**diagnostics(rows,ids,c),mean_baseline=float(p[:,0].mean()),mean_cancel=float(p[:,1].mean()),
                        delta=ci(delta,ids),human_raw_rho=float(spearmanr(delta,h).statistic),human_z_rho=float(spearmanr(delta,hz).statistic),by_phenomenon=byph)
        for c in ['parent','format']:
            results[scope]['transport'][c]={}
            for order in ['average','1','2']:
                p,_=arrays(models['SFT'],ids,c,order);t,_=arrays(models['DPO'],ids,c,order)
                group={}
                for seed in [20261003,1]:
                    group[str(seed)]={}
                    identity_mse=float(np.mean((p-t)**2))
                    previous=None
                    global_mse=None
                    for kind in ['global','condition','human']:
                        pred,params,assignment=oof(p,t,h,ids,seed,kind)
                        err=np.mean((pred-t)**2,axis=1);mse=float(err.mean())
                        if kind=='global':global_mse=mse
                        yy=np.clip(t,1e-12,1-1e-12);qq=np.clip(pred,1e-12,1-1e-12)
                        kl=float(np.mean(yy*np.log(yy/qq)+(1-yy)*np.log((1-yy)/(1-qq))))
                        stage_delta=(t[:,1]-t[:,0])-(p[:,1]-p[:,0])
                        residual=(t[:,1]-t[:,0])-(pred[:,1]-pred[:,0])
                        group[str(seed)][kind]=dict(identity_mse=identity_mse,oof_mse=mse,oof_kl=kl,identity_error_reduction=1-mse/identity_mse,
                                    improvement_vs_global=1-mse/global_mse,
                                    improvement_vs_previous=None if previous is None else 1-mse/previous,
                                    stage_change=ci(stage_delta,ids),cancel_delta_prediction_mse=float(np.mean(residual**2)),
                                    residual_cancel_change=ci(residual,ids),residual_human_raw_rho=float(spearmanr(residual,h).statistic),
                                    parameters=params,source_assignment=assignment)
                        previous=mse
                        for i,pp,tt,qq in zip(ids,p,t,pred):
                            oofrows.append(dict(scope=scope,condition=c,order=order,seed=seed,kind=kind,item=i,sft=pp.tolist(),dpo=tt.tolist(),prediction=qq.tolist()))
                results[scope]['transport'][c][order]=group
    output=a.root/'runs/E67-analysis'
    output.mkdir(exist_ok=False)
    path=output/'oof.jsonl';path.write_text(''.join(json.dumps(x)+'\n' for x in oofrows))
    hours=sum(x['wall_seconds'] for xs in configs.values() for x in xs)/3600
    summary=dict(experiment='E67',new_gpu_hours=hours,results=results,hashes=hashes,
                 analysis_script_sha256=sha(Path(__file__)),
                 positive_control_mse=float(np.mean((yp-sy)**2)),token_hash_parity=True,
                 oof_path=str(path),oof_sha256=sha(path),n_oof_records=len(oofrows),
                 limitations=['Conditional source-bootstrap, not refit/training-seed CI; shared human raters not resampled',
                              'Frozen 243 presentation-matched cohort includes 16 literal annotation cue risks; 227 sensitivity is post-hoc technical audit, not new confirmation',
                              'Human Likert differences not true belief probabilities',
                              'Global/conditional mapping descriptive not algorithm causality',
                              'Logit predictor clips SFT probabilities to [1e-6,1-1e-6]; KL clips to [1e-12,1-1e-12]',
                              'Do not interpret transport if endpoint order/semantic gate fails'])
    a.output.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(dict(gpu_hours=hours,primary_endpoints=results['text_matched']['endpoints'],primary_transport=results['text_matched']['transport']['format']['average']),ensure_ascii=False))


if __name__=='__main__':
    main()
