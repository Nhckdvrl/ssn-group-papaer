"""Whole-roster Push update-module comparison, independently audited actual outcomes."""
import json
import shutil
import numpy as np
from experience_transfer_control_audit import ROOT,WB,sha,read,save,verify,counts


def main():
    bank=ROOT/'20261005-E20-pusht-fresh-control-bank48';groups=[];refs=[];totals=[];arrays={}
    for arm in ['DYNAMICS-ONLY','GEOMETRY-ONLY','RELEASED','PLAIN']:
        for interface in ['native','physical']:
            new=arm in ['DYNAMICS-ONLY','GEOMETRY-ONLY']
            name=f'20261005-E20-pusht-module-control-{arm}-{interface}-RTX-s0' if new else f'20261005-E20-pusht-control-{arm}-{interface}-RTX-s0'
            group,arr=verify(ROOT/name,bank,'pusht',interface);cfg=group['config']
            if new:
                source=ROOT/f'20261005-E20-pusht-module-{arm}-A100-s0'
                assert cfg['arm']==arm and cfg['source_training_run']==source.name
                assert cfg['script_sha256']==sha(WB/'scripts/pusht_module_control.py') and cfg['trainer_sha256']==sha(WB/'scripts/pusht_module_learning.py')
                assert read(source/'complete.json')==dict(completed=True,arm=arm,seed=0,updates=2000)
                assert cfg['checkpoint_sha256']==next(v['checkpoint_sha256'] for v in read(source/'summary.json') if v['updates']==2000)
                groups.append(group)
            else: refs.append(group)
            assert cfg['controller_sha256']==sha(WB/'scripts/bounded_control.py')
            parity=read(ROOT/name/'native_parity.json');group['native_parity']=parity
            arrays[arm,interface]=arr;totals.append(counts(group,arm=arm,interface=interface))
            print('Push module trajectory audit',arm,interface,'PASS',flush=True)
    assert len({g['config']['hardware'] for g in groups+refs})==1
    for interface in ['native','physical']:
        norms=[(g['config']['action_mean'],g['config']['action_std']) for g in groups+refs if g['config']['interface']==interface]
        assert all(n==norms[0] for n in norms)
    rng=np.random.default_rng(112700);near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],1);effects=[]
    for interface in ['native','physical']:
        for arm,ref in [('DYNAMICS-ONLY','RELEASED'),('GEOMETRY-ONLY','RELEASED'),('DYNAMICS-ONLY','PLAIN'),('GEOMETRY-ONLY','PLAIN'),('DYNAMICS-ONLY','GEOMETRY-ONLY')]:
            delta=arrays[arm,interface]-arrays[ref,interface]
            for tier,ix in [('all',allix),('near',near),('far',far)]:
                values=delta if tier=='all' else delta[:24] if tier=='near' else delta[24:]
                effects.append(dict(interface=interface,arm=arm,reference=ref,tier=tier,mean_delta=float(values.mean()),paired_anchor_bootstrap_95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist(),train_sources=1))
    result=dict(completed=True,controller_groups=4,episodes=192,reference_episodes=192,counts=totals,effects=effects,groups=groups,reference_groups=refs,
        scope='One released initialization and one transfer seed, shared development48 tasks and original controller protocol. Module permissions include normalization buffers, not gradient-only causality. No new environment acquisition or full-data replay. Pretraining split unknown. Do not infer universal encoder drift or a novel frozen-module method.',script_sha256=sha(__file__))
    out=ROOT/'20261005-E20-pusht-module-control-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');save(out/'result.json',result)
    for g in groups+refs:g.pop('rows')
    result['full_audit_artifact']=str(out/'result.json');save(WB/'results/E20_20261005_pusht_module_control_results.json',result);print(json.dumps(totals),flush=True)


if __name__=='__main__':main()
