"""Complete A9 matrix only: unchanged A8 source0 plus corrected v2 sources1/2."""
import json
import shutil
import numpy as np
from experience_transfer_control_audit import ROOT, WB, read, save, sha, verify, counts


def main():
    bank = ROOT / '20261004-E20-fresh-control-bank48'
    assert read(WB / 'results/E13_20261005_predictive_object_endpoint_audit.json')['completed']
    assert read(WB / 'results/E13_20261005_predictive_object_repeat_endpoint_audit.json')['completed']
    groups, refs, totals, arrays = [], [], [], {}
    for seed in range(3):
        for geometry in ['PRED', 'VALUE']:
            for arm in ['DIRECT', 'LOCAL']:
                source = ROOT / f'20261005-E13-object-{geometry}-{arm}-A100-s{seed}'
                expected = dict(completed=True, geometry=geometry, arm=arm, updates=2825)
                if seed: expected['seed'] = seed
                assert read(source / 'complete.json') == expected
                for interface in ['native', 'physical']:
                    prefix = 'object-repeat-v2-control' if seed else 'object-control'
                    run = ROOT / f'20261005-E13-{prefix}-{geometry}-{arm}-{interface}-RTX-s{seed}'
                    group, arr = verify(run, bank, 'nav', interface)
                    cfg = group['config']
                    assert cfg['geometry'] == geometry and cfg['arm'] == arm
                    assert cfg['history'] == 1 and cfg['model_training_updates'] == 2825
                    controller = 'predictive_object_repeat_control_v2.py' if seed else 'predictive_object_control.py'
                    trainer = 'predictive_object_repeat.py' if seed else 'predictive_object.py'
                    assert cfg['script_sha256'] == sha(WB / 'scripts' / controller)
                    assert cfg['script_sha256'] == sha(run / 'predictive_object_control_used.py')
                    assert cfg['trainer_sha256'] == sha(WB / 'scripts' / trainer)
                    assert cfg['controller_sha256'] == sha(WB / 'scripts/bounded_control.py')
                    assert cfg['checkpoint_sha256'] == read(source / 'summary.json')['checkpoint_sha256']
                    assert cfg['source_training_run'] == source.name
                    if seed: assert cfg['train_seed'] == seed == read(source / 'config.json')['train_seed']
                    assert np.array_equal(cfg['action_mean'], read(source/'config.json')['feature_metadata']['manifest']['action_mean'])
                    assert np.array_equal(cfg['action_std'], read(source/'config.json')['feature_metadata']['manifest']['action_std'])
                    arrays[geometry+'-'+arm, seed, interface] = arr
                    groups.append(group)
                    totals.append(counts(group, geometry=geometry, arm=arm, seed=seed, interface=interface))
                    print('A9 independent trajectory audit', geometry, arm, seed, interface, 'PASS', flush=True)
    for seed in range(3):
        for arm in ['ABS', 'VGIQL-SEPARATE', 'FULL-AD']:
            for interface in ['native', 'physical']:
                prefix = '20261005-value-repeat-control' if arm=='VGIQL-SEPARATE' and seed else '20261004-matched-control'
                group, arr = verify(ROOT/f'{prefix}-{arm}-s{seed}-{interface}-RTX', bank, 'nav', interface)
                context = read(ROOT/f'{prefix}-{arm}-s{seed}-{interface}-RTX'/'matched_loader.json')
                assert context['arm']==arm and context['seed']==seed
                assert context['train_checkpoint_sha256']==group['config']['checkpoint_sha256']
                refs.append(group); arrays[arm,seed,interface]=arr
                totals.append(counts(group, reference=arm, seed=seed, interface=interface))
    for interface in ['native', 'physical']:
        group, arr = verify(ROOT/f'20261005-E01-rcaux-full-H1-W0.85-{interface}-RTX',bank,'nav',interface)
        refs.append(group); totals.append(counts(group, reference='RC-H1-ON', interface=interface))
        # Same published checkpoint/task outcomes reused across source comparisons,
        # not three independent RC training seeds.
        for seed in range(3): arrays['RC-H1-ON',seed,interface]=arr
    assert len(groups)==24 and len({g['config']['hardware'] for g in groups+refs})==1
    rng=np.random.default_rng(114500)
    si=rng.integers(0,3,(10000,3))
    near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24))
    allix=np.concatenate([near,far],axis=1);effects=[]
    for interface in ['native','physical']:
        contrasts=[('PRED-DIRECT','PRED-LOCAL'),('VALUE-DIRECT','VALUE-LOCAL')]
        contrasts += [(g+'-'+a,ref) for g in ['PRED','VALUE'] for a in ['DIRECT','LOCAL']
                      for ref in ['ABS','VGIQL-SEPARATE','FULL-AD','RC-H1-ON']]
        deltas=[(arm+' minus '+ref,np.stack([arrays[arm,s,interface]-arrays[ref,s,interface] for s in range(3)]))
                for arm,ref in contrasts]
        interaction=np.stack([(arrays['VALUE-DIRECT',s,interface]-arrays['VALUE-LOCAL',s,interface])
                             -(arrays['PRED-DIRECT',s,interface]-arrays['PRED-LOCAL',s,interface]) for s in range(3)])
        deltas.append(('(VALUE DIRECT-LOCAL) minus (PRED DIRECT-LOCAL)',interaction))
        for contrast,delta in deltas:
            for tier,ix in [('all',allix),('near',near),('far',far)]:
                values=delta if tier=='all' else delta[:,:24] if tier=='near' else delta[:,24:]
                draws=delta[si[:,:,None],ix[:,None,:]].mean((1,2))
                effects.append(dict(interface=interface,contrast=contrast,tier=tier,mean_delta=float(values.mean()),
                    source_deltas=values.mean(1).tolist(),paired_source_anchor_bootstrap_95=np.quantile(draws,[.025,.975]).tolist(),
                    train_sources=3,shared_task_anchors=48))
    result=dict(completed=True,controller_groups=24,episodes=1152,counts=totals,effects=effects,groups=groups,reference_groups=refs,
        excluded_controller_artifact=str(ROOT/'20261005-E13-object-repeat-controller-seed-shadow-failure'),
        scope='Three independent training sources, same100 training episodes and shared48 development anchors; not144 independent tasks. A8 source0 and A9 independent repeats retained in full, no source/goal selection. Within-geometry matched head init/capacity/clip targets/updates/T1 deployment; conditioning differs. Geometry priors differ in objectives and5650/2825 budgets; old LeWM H3/targets/sampling/total compute differs; published RC data unmatched, its same checkpoint outcomes repeated in source contrasts. Not novel method confirmation, pure objective causality, Markov sufficiency, or speedup. Invalid first repeat controller outputs fully excluded.',script_sha256=sha(__file__))
    out=ROOT/'20261005-E13-object-repeat-v2-control-audit'
    assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');save(out/'result.json',result)
    for group in groups+refs:group.pop('rows')
    result['full_audit_artifact']=str(out/'result.json')
    save(WB/'results/E13_20261005_predictive_object_three_seed_control_results.json',result)
    print(json.dumps(totals),flush=True)


if __name__=='__main__':main()
