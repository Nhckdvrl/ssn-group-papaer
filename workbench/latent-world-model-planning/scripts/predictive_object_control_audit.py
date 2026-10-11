"""All predictive-object controller outcomes and unfiltered strong references."""
import json
import shutil
import numpy as np
from experience_transfer_control_audit import ROOT,WB,sha,read,save,verify,counts


def main():
    bank=ROOT/'20261004-E20-fresh-control-bank48';groups=[];refs=[];totals=[];arrays={}
    assert read(WB/'results/E13_20261005_predictive_object_endpoint_audit.json')['completed']
    for geometry in ['PRED','VALUE']:
        for arm in ['DIRECT','LOCAL']:
            source=ROOT/f'20261005-E13-object-{geometry}-{arm}-A100-s0'
            assert read(source/'complete.json')==dict(completed=True,geometry=geometry,arm=arm,updates=2825)
            for interface in ['native','physical']:
                name=f'20261005-E13-object-control-{geometry}-{arm}-{interface}-RTX-s0'
                group,arr=verify(ROOT/name,bank,'nav',interface);cfg=group['config']
                assert cfg['geometry']==geometry and cfg['arm']==arm and cfg['history']==1 and cfg['model_training_updates']==2825
                assert cfg['script_sha256']==sha(WB/'scripts/predictive_object_control.py') and cfg['trainer_sha256']==sha(WB/'scripts/predictive_object.py') and cfg['controller_sha256']==sha(WB/'scripts/bounded_control.py')
                assert cfg['checkpoint_sha256']==read(source/'summary.json')['checkpoint_sha256'] and cfg['source_training_run']==source.name
                arrays[f'{geometry}-{arm}',interface]=arr;groups.append(group);totals.append(counts(group,geometry=geometry,arm=arm,interface=interface))
                print('object trajectory audit',geometry,arm,interface,'PASS',flush=True)
    for arm in ['ABS','VGIQL-SEPARATE','FULL-AD','RC-H1-ON']:
        for interface in ['native','physical']:
            name=f'20261005-E01-rcaux-full-H1-W0.85-{interface}-RTX' if arm=='RC-H1-ON' else f'20261004-matched-control-{arm}-s0-{interface}-RTX'
            group,arr=verify(ROOT/name,bank,'nav',interface);refs.append(group);arrays[arm,interface]=arr;totals.append(counts(group,reference=arm,interface=interface))
    assert len({g['config']['hardware'] for g in groups+refs})==1
    rng=np.random.default_rng(113500);near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],1);effects=[]
    for interface in ['native','physical']:
        contrasts=[('PRED-DIRECT','PRED-LOCAL'),('VALUE-DIRECT','VALUE-LOCAL'),('VALUE-DIRECT','PRED-DIRECT'),('VALUE-LOCAL','PRED-LOCAL')]
        contrasts+=[(f'{g}-{a}',ref) for g in ['PRED','VALUE'] for a in ['DIRECT','LOCAL'] for ref in ['ABS','VGIQL-SEPARATE','FULL-AD','RC-H1-ON']]
        for arm,reference in contrasts:
            delta=arrays[arm,interface]-arrays[reference,interface]
            for tier,ix in [('all',allix),('near',near),('far',far)]:
                values=delta if tier=='all' else delta[:24] if tier=='near' else delta[24:]
                effects.append(dict(interface=interface,arm=arm,reference=reference,tier=tier,mean_delta=float(values.mean()),paired_anchor_bootstrap_95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist(),train_sources=1))
    result=dict(completed=True,controller_groups=8,episodes=384,counts=totals,effects=effects,groups=groups,reference_groups=refs,
        scope='One exploratory source/shared development48 tasks. Within geometry DIRECT/LOCAL shared head architecture, initial weights, training clips/targets/update budget and T1 deployment; teacher inputs and prediction objects differ. PRED/VALUE priors5650/2825 differ in objective and budget. Old LeWM refs H3 and distinct targets/sampling/total compute; published RC training unmatched/H1. Reference effects are capability context, not isolated predictive-object causality or speedup. All48 retained, no novel method confirmation.',script_sha256=sha(__file__))
    out=ROOT/'20261005-E13-object-control-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');save(out/'result.json',result)
    for group in groups+refs:group.pop('rows')
    result['full_audit_artifact']=str(out/'result.json');save(WB/'results/E13_20261005_predictive_object_control_results.json',result)
    print(json.dumps(totals),flush=True)


if __name__=='__main__':main()
