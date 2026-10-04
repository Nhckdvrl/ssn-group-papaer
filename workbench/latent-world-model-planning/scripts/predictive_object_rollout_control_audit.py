"""Audit all A10 endpoints, real trajectories and the locked strong contrasts."""
import json
import shutil
import numpy as np
from experience_transfer_control_audit import ROOT, WB, read, save, sha, verify, counts


def main():
    assert read(WB/'results/E13_20261005_rollout_endpoint_audit.json')['completed']
    bank = ROOT/'20261004-E20-fresh-control-bank48'
    script = WB/'scripts/predictive_object_rollout_control.py'
    trainer = WB/'scripts/predictive_object_rollout.py'
    groups, refs, totals, arrays = [], [], [], {}
    for seed in range(3):
        pipeline = ROOT/f'20261005-E13-rollout-control-pipeline-s{seed}'
        assert read(pipeline/'complete.json') == dict(completed=True, train_seed=seed, episodes=192)
        assert not (pipeline/'failure.json').exists()
        for geometry in ['PRED', 'VALUE']:
            source = ROOT/f'20261005-E13-rollout-{geometry}-s{seed}-A100'
            cfg = read(source/'config.json')
            assert read(source/'complete.json') == dict(completed=True, geometry=geometry, seed=seed, updates=2825)
            summary = read(source/'summary.json')
            for device in ['cpu', 'cuda']:
                pre = read(ROOT/f'20261005-E13-rollout-{geometry}-s{seed}-{device}-control-preflight/controls.json')
                assert pre['passed'] and pre['script_sha256'] == sha(script)
                assert (pre['geometry'], pre['train_seed'], pre['device']) == (geometry, seed, device)
                assert pre['all48_initial_pixels_states_exact'] and pre['weights_unchanged']
                assert pre['full_cost_error'] == 0 and pre['checkpoint_sha256'] == summary['checkpoint_sha256']
            for interface in ['native', 'physical']:
                run = ROOT/f'20261005-E13-rollout-control-{geometry}-{interface}-RTX-s{seed}'
                group, arr = verify(run, bank, 'nav', interface)
                c = group['config']
                assert (c['geometry'], c['arm'], c['train_seed'], c['history'], c['model_training_updates']) == (geometry, 'OPEN-ROLLOUT', seed, 1, 2825)
                assert c['script_sha256'] == sha(script) == sha(run/'used.py')
                assert c['trainer_sha256'] == sha(trainer) == cfg['script_sha256']
                assert c['controller_sha256'] == sha(WB/'scripts/bounded_control.py')
                assert c['source_training_run'] == source.name
                assert c['checkpoint_sha256'] == summary['checkpoint_sha256']
                manifest = cfg['feature_metadata']['manifest']
                assert np.array_equal(c['action_mean'], manifest['action_mean'])
                assert np.array_equal(c['action_std'], manifest['action_std'])
                for row in group['rows']:
                    assert len(row['decisions']) <= 4
                    for k, d in enumerate(row['decisions']):
                        assert d['decision'] == k and d['planner_seed'] == 105400+100*row['anchor']+k
                        assert 1 <= d['executed_steps'] <= 25
                        if k < len(row['decisions'])-1: assert d['executed_steps'] == 25
                    if not row['success']: assert row['env_steps'] == 100
                arrays[geometry+'-OPEN', seed, interface] = arr
                groups.append(group)
                totals.append(counts(group, geometry=geometry, arm='OPEN-ROLLOUT', seed=seed, interface=interface))
                print('A10 independent real trajectory audit', geometry, seed, interface, 'PASS', flush=True)
    assert read(WB/'results/E13_20261005_predictive_object_three_seed_control_results.json')['completed']
    assert read(WB/'results/E14_20261005_goal_policy_control_results.json')['completed']
    for seed in range(3):
        for geometry in ['PRED', 'VALUE']:
            for arm in ['DIRECT', 'LOCAL', 'GC-IDM', 'GCBC-MATCHED']:
                for interface in ['native', 'physical']:
                    if arm in ['DIRECT', 'LOCAL']:
                        prefix = 'object-repeat-v2-control' if seed else 'object-control'
                        run = ROOT/f'20261005-E13-{prefix}-{geometry}-{arm}-{interface}-RTX-s{seed}'
                    else:
                        run = ROOT/f'20261005-E14-goalpolicy-control-{geometry}-{arm}-{interface}-RTX-s{seed}'
                    group, arr = verify(run, bank, 'nav', interface)
                    arrays[geometry+'-'+arm, seed, interface] = arr
                    refs.append(group); totals.append(counts(group, reference=geometry+'-'+arm, seed=seed, interface=interface))
        for interface in ['native', 'physical']:
            prefix = '20261005-value-repeat-control' if seed else '20261004-matched-control'
            run = ROOT/f'{prefix}-VGIQL-SEPARATE-s{seed}-{interface}-RTX'
            group, arr = verify(run, bank, 'nav', interface)
            arrays['SEP', seed, interface] = arr; refs.append(group)
            totals.append(counts(group, reference='SEP', seed=seed, interface=interface))
    for interface in ['native', 'physical']:
        group, arr = verify(ROOT/f'20261005-E01-rcaux-full-H1-W0.85-{interface}-RTX', bank, 'nav', interface)
        for seed in range(3): arrays['RC-H1-ON', seed, interface] = arr
        refs.append(group); totals.append(counts(group, reference='RC-H1-ON', interface=interface))
    assert len(groups) == 12 and len({g['config']['hardware'] for g in groups+refs}) == 1
    rng = np.random.default_rng(116000)
    si = rng.integers(0, 3, (10000, 3))
    near = rng.integers(0, 24, (10000, 24)); far = rng.integers(24, 48, (10000, 24))
    allix = np.concatenate([near, far], 1); effects = []
    for interface in ['native', 'physical']:
        contrasts = [(g+'-OPEN', g+'-'+a) for g in ['PRED', 'VALUE'] for a in ['DIRECT', 'LOCAL', 'GC-IDM', 'GCBC-MATCHED']]
        contrasts += [(g+'-OPEN', a) for g in ['PRED', 'VALUE'] for a in ['SEP', 'RC-H1-ON']]
        deltas = [(arm+' minus '+ref, np.stack([arrays[arm,s,interface]-arrays[ref,s,interface] for s in range(3)])) for arm,ref in contrasts]
        deltas.append(('(VALUE OPEN-LOCAL) minus (PRED OPEN-LOCAL)', np.stack([
            (arrays['VALUE-OPEN',s,interface]-arrays['VALUE-LOCAL',s,interface])
            -(arrays['PRED-OPEN',s,interface]-arrays['PRED-LOCAL',s,interface]) for s in range(3)])))
        for contrast, delta in deltas:
            for tier, ix in [('all', allix), ('near', near), ('far', far)]:
                values = delta if tier == 'all' else delta[:,:24] if tier == 'near' else delta[:,24:]
                draws = delta[si[:,:,None],ix[:,None,:]].mean((1,2))
                effects.append(dict(interface=interface, contrast=contrast, tier=tier, mean_delta=float(values.mean()), source_deltas=values.mean(1).tolist(), paired_source_anchor_bootstrap_95=np.quantile(draws,[.025,.975]).tolist(), train_sources=3, shared_task_anchors=48))
    result = dict(completed=True, controller_groups=12, episodes=576, counts=totals, effects=effects, groups=groups, reference_groups=refs, script_sha256=sha(__file__),
        scope='All six fixed endpoints and both interfaces retained. Three independent training sources and shared48 development anchors, not144 independent tasks. OPEN/DIRECT/LOCAL match head capacity, initialization, examples, five future targets and updates; train conditioning and BN/dropout calls differ. Geometry priors differ in objectives and training budgets. Old SEP history/targets/sampling differ. GC policies differ in capacity/objective/training and real-feedback cadence. RC published training unmatched, same checkpoint reused across source contrasts. Known multi-step BPTT baseline, no novel method, pure geometry causality or speedup claim.')
    out = ROOT/'20261005-E13-rollout-control-audit'
    assert not out.exists(); out.mkdir(); shutil.copy2(__file__,out/'audit_used.py'); save(out/'result.json',result)
    for group in groups+refs: group.pop('rows')
    result['full_audit_artifact'] = str(out/'result.json')
    save(WB/'results/E13_20261005_rollout_control_results.json',result)
    print(json.dumps(totals),flush=True)


if __name__ == '__main__': main()
