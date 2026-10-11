"""A12 complete three-object Push matrix, independently native trace-scored."""
import shutil
import numpy as np
from experience_transfer_control_audit import ROOT,WB,read,save,sha,verify,counts


def main():
    assert read(WB/'results/E13_20261005_pusht_object_endpoint_audit.json')['completed']
    bank=ROOT/'20261005-E20-pusht-fresh-control-bank48';groups=[];refs=[];totals=[];arrays={}
    script=WB/'scripts/predictive_object_pusht_control.py';trainer=WB/'scripts/predictive_object_pusht.py'
    for arm in ['DIRECT','LOCAL','OPEN']:
        source=ROOT/f'20261005-E13-pusht-object-{arm}-RTX-s0';sourcecfg=read(source/'config.json')
        assert read(ROOT/f'20261005-E13-pusht-object-control-{arm}-pipeline/complete.json')==dict(completed=True,arm=arm,episodes=96)
        for device in ['cpu','cuda']:
            pre=read(ROOT/f'20261005-E13-pusht-object-{arm}-{device}-control-preflight/controls.json')
            assert pre['passed'] and pre['script_sha256']==sha(script) and pre['trainer_sha256']==sha(trainer)
            assert pre['all48_full25D_warm_pixels_exact'] and pre['weights_unchanged'] and pre['full_cost_error']==0
        for interface in ['native','physical']:
            run=ROOT/f'20261005-E13-pusht-object-control-{arm}-{interface}-RTX-s0'
            group,arr=verify(run,bank,'pusht',interface);cfg=group['config']
            assert (cfg['task'],cfg['arm'],cfg['train_seed'],cfg['budget'],cfg['history'],cfg['model_training_updates'])==('pusht',arm,0,100,1,2825)
            assert cfg['script_sha256']==sha(script)==sha(run/'used.py') and cfg['trainer_sha256']==sha(trainer)
            assert cfg['checkpoint_sha256']==read(source/'summary.json')['checkpoint_sha256']
            assert cfg['controller_sha256']==sha(WB/'scripts/bounded_control.py') and cfg['restore_sha256']==sha(WB/'scripts/pusht_fresh_control.py')
            assert cfg['source_training_run']==source.name
            assert cfg['geometry_source_sha256']==sourcecfg['data_metadata']['feature_metadata']['source_sha256']
            for key in ['action_mean','action_std']:assert np.array_equal(cfg[key],sourcecfg['data_metadata']['manifest'][key])
            for row in group['rows']:
                assert len(row['decisions'])<=4
                for k,d in enumerate(row['decisions']):
                    assert d['decision']==k and d['planner_seed']==109400+row['anchor']*100+k and 1<=d['executed_steps']<=25
                    if k<len(row['decisions'])-1:assert d['executed_steps']==25
                if not row['success']:assert row['env_steps']==100
            groups.append(group);arrays[arm,interface]=arr;totals.append(counts(group,arm=arm,interface=interface,seed=0))
            print('Push object full trajectory audit',arm,interface,'PASS',flush=True)
    for interface in ['native','physical']:
        for label,run in [('RELEASED',ROOT/f'20261005-E20-pusht-control-RELEASED-{interface}-RTX-s0'),
                          ('GCBC-860-U4000',ROOT/f'20261005-E14-coverage-control-e860-u4000-{interface}-RTX-s0')]:
            group,arr=verify(run,bank,'pusht',interface);refs.append(group);arrays[label,interface]=arr
            totals.append(counts(group,reference=label,interface=interface))
    assert len(groups)==6 and len({g['config']['hardware'] for g in groups+refs})==1
    rng=np.random.default_rng(116200);near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],1);effects=[]
    for interface in ['native','physical']:
        contrasts=[('DIRECT','LOCAL'),('DIRECT','OPEN'),('OPEN','LOCAL')]
        contrasts += [(arm,ref) for arm in ['DIRECT','LOCAL','OPEN'] for ref in ['RELEASED','GCBC-860-U4000']]
        for arm,ref in contrasts:
            delta=arrays[arm,interface]-arrays[ref,interface]
            for tier,ix in [('all',allix),('near',near),('far',far)]:
                value=delta if tier=='all' else delta[:24] if tier=='near' else delta[24:]
                effects.append(dict(interface=interface,arm=arm,reference=ref,tier=tier,mean_delta=float(value.mean()),paired_anchor_bootstrap_95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist(),train_sources=1))
    result=dict(completed=True,controller_groups=6,episodes=288,counts=totals,effects=effects,groups=groups,reference_groups=refs,script_sha256=sha(__file__),
        scope='All3 objects and both interfaces on shared48 development tasks, one headseed. Same frozen published phi, head capacity/initialization, fact86 clips, five targets and2825updates; conditioning and BN/dropout calls differ. Published pretraining unknown. Native unbounded-normalized and physical bounded CEM jointly change proposal coordinates/scale/bounds. Released H3 differs in context/training and GCBC860 in data/objective/capacity/feedback; references are capability context. Known baselines, not novel method, independent task confirmation or numerical paper replication.')
    out=ROOT/'20261005-E13-pusht-object-control-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');save(out/'result.json',result)
    for g in groups+refs:g.pop('rows')
    result['full_audit_artifact']=str(out/'result.json');save(WB/'results/E13_20261005_pusht_object_control_results.json',result)
    print(totals,flush=True)


if __name__=='__main__':main()
