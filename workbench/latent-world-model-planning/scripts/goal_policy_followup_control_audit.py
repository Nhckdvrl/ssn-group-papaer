"""Whole preregistered history or coverage matrix, independent native trace audit."""
import argparse
import shutil
import numpy as np
from experience_transfer_control_audit import ROOT,WB,read,save,sha,verify,counts


def main(stage):
    endpoint=WB/'results'/f'E14_20261005_{"history" if stage=="history" else "coverage"}_policy_endpoint_audit.json'
    assert read(endpoint)['completed'];groups=[];refs=[];totals=[];table={};effects=[]
    tasks=['nav','pusht'] if stage=='history' else ['pusht']
    labels=['TRUE-HISTORY','CURRENT-COPY'] if stage=='history' else ['e86-u400','e86-u4000','e860-u400','e860-u4000']
    script=WB/'scripts'/('goal_policy_history_control_v2.py' if stage=='history' else 'goal_policy_coverage_control.py')
    trainer=WB/'scripts'/('goal_policy_history.py' if stage=='history' else 'goal_policy_coverage.py')
    for task in tasks:
        bank=ROOT/('20261004-E20-fresh-control-bank48' if task=='nav' else '20261005-E20-pusht-fresh-control-bank48')
        pipe=ROOT/(f'20261005-E14-history-v2-control-{task}-pipeline' if stage=='history' else '20261005-E14-coverage-control-pipeline')
        assert read(pipe/'complete.json')['completed'] and not (pipe/'failure.json').exists()
        for device in ['cpu','cuda']:
            path=ROOT/(f'20261005-E14-history-v2-{task}-{device}-control-preflight' if stage=='history' else f'20261005-E14-coverage-{device}-control-preflight')
            pre=read(path/'controls.json');assert pre['passed'] and pre['script_sha256']==sha(script) and pre['trainer_sha256']==sha(trainer)
        for label in labels:
            source=ROOT/(f'20261005-E14-history-{task}-{label}-RTX-s0' if stage=='history' else f'20261005-E14-coverage-{label}-RTX-s0')
            for interface in ['native','physical']:
                run=ROOT/(f'20261005-E14-history-v2-control-{task}-{label}-{interface}-RTX-s0' if stage=='history' else f'20261005-E14-coverage-control-{label}-{interface}-RTX-s0')
                group,arr=verify(run,bank,task,interface);cfg=group['config']
                assert cfg['script_sha256']==sha(script)==sha(run/'used.py') and cfg['trainer_sha256']==sha(trainer)
                assert (cfg['task'],cfg['train_seed'],cfg['budget'],cfg['executed_steps_per_decision'])==(task,0,100,1)
                assert cfg['checkpoint_sha256']==read(source/'summary.json')['checkpoint_sha256']
                assert cfg['geometry_source_sha256']==read(source/'config.json')['feature_metadata']['source_sha256']
                for row in group['rows']:
                    decisions=row['decisions'];assert len(decisions)==row['env_steps']
                    for step,d in enumerate(decisions):
                        assert (d['decision'],d['executed_steps'],d['remaining_horizon'])==(step,1,0)
                        if stage=='history':assert d['relative_observation_steps']==[step-10,step-5,step]
                    trace=np.load(run/f'trace_{row["anchor"]:03d}.npz');issued=np.asarray([d['issued_action'] for d in decisions]).reshape(-1,2)
                    assert np.isfinite(issued).all() and np.array_equal(trace['actions'],np.clip(issued,-1,1) if interface=='physical' else issued)
                    assert row['success_by50']==bool(row['initial_success'] or (row['success'] and row['env_steps']<=50))
                table[task,label,interface]=arr;groups.append(group);totals.append(counts(group,task=task,label=label,interface=interface,seed=0))
                print('Follow-up policy trajectory audit',stage,task,label,interface,'PASS',flush=True)
        for interface in ['native','physical']:
            ref=ROOT/(f'20261005-E14-goalpolicy-control-PRED-GCBC-MATCHED-{interface}-RTX-s0' if task=='nav' else f'20261005-E20-pusht-control-RELEASED-{interface}-RTX-s0')
            group,arr=verify(ref,bank,task,interface);refs.append(group);table[task,'PRIOR-CAPABILITY',interface]=arr;totals.append(counts(group,task=task,reference='PRIOR-CAPABILITY',interface=interface,seed=0))
        rng=np.random.default_rng(115700 if task=='nav' else 115701);near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],1)
        contrasts=[('TRUE-HISTORY','CURRENT-COPY')] if stage=='history' else [('e860-u400','e86-u400'),('e860-u4000','e86-u4000'),('e86-u4000','e86-u400'),('e860-u4000','e860-u400')]
        contrasts += [(label,'PRIOR-CAPABILITY') for label in labels]
        for interface in ['native','physical']:
            for arm,ref in contrasts:
                delta=table[task,arm,interface]-table[task,ref,interface]
                for tier,ix in [('all',allix),('near',near),('far',far)]:
                    value=delta if tier=='all' else delta[:24] if tier=='near' else delta[24:]
                    effects.append(dict(task=task,interface=interface,arm=arm,reference=ref,tier=tier,mean_delta=float(value.mean()),paired_anchor_bootstrap_95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist(),train_sources=1))
            if stage=='coverage':
                delta=(table[task,'e860-u4000',interface]-table[task,'e86-u4000',interface])-(table[task,'e860-u400',interface]-table[task,'e86-u400',interface])
                effects.append(dict(task=task,interface=interface,contrast='data_by_compute_interaction',tier='all',mean_delta=float(delta.mean()),paired_anchor_bootstrap_95=np.quantile(delta[allix].mean(1),[.025,.975]).tolist(),train_sources=1))
    assert len(groups)==8 and len({v['config']['hardware'] for v in groups+refs})==1
    result=dict(completed=True,stage=stage,controller_groups=8,episodes=384,counts=totals,effects=effects,groups=groups,reference_groups=refs,script_sha256=sha(__file__),scope='Full preregistered matrix, all48/shared development task anchors and weak methods retained. One training seed per condition; paired anchor CI excludes training variation. Known baseline/design tests, frozen phi and published Push pretraining unknown. PRIOR-CAPABILITY differs in capacity, training starts or control feedback; it is context, not one-factor causal evidence. No novel method or manuscript-critical claim.')
    out=ROOT/f'20261005-E14-{stage}-control-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');save(out/'result.json',result)
    for group in groups+refs:group.pop('rows')
    result['full_audit_artifact']=str(out/'result.json');save(WB/'results'/f'E14_20261005_{stage}_policy_control_results.json',result)
    print(totals,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['history','coverage']);main(parser.parse_args().stage)
