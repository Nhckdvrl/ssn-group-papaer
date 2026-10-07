"""Independent complete-matrix F1 execution, hidden-shift and utility audit."""
import shutil
import numpy as np
from sklearn.preprocessing import StandardScaler
from experience_transfer_control_audit import ROOT, WB, read, save, sha

METHODS = ['HOLD', 'REFRESH15', 'REFRESH5']
CONDITIONS = ['nominal', 'gain0.7', 'physics']


def native_hits(task, state, goal):
    if task == 'tworoom':
        return np.linalg.norm(state-goal, axis=-1) < 16
    angle = np.abs(state[:, 4]-goal[4])
    return (np.linalg.norm(state[:, :4]-goal[:4], axis=-1) < 20) & (np.minimum(angle, 2*np.pi-angle) < np.pi/9)


def main():
    producer = WB/'scripts/intact_recovery_forks_v2.py'
    helper = WB/'scripts/intact_published_control_v3.py'
    groups, counts, vectors, controls = [], [], {}, []
    for task in ['tworoom', 'pusht']:
        out = ROOT/f'20261005-E18-intact-forks-v2-{task}'
        assert not (out/'failure.json').exists()
        complete = read(out/'complete.json')
        assert complete['completed'] and complete['n'] == 432 and complete['model_unchanged']
        assert complete['features_saved_before_all_continuations']
        pre, config, rows = read(out/'preflight.json'), read(out/'config.json'), read(out/'rows.json')
        assert pre['passed'] and pre['n'] == 144 and pre['model_unchanged']
        assert config['script_sha256'] == sha(producer) == sha(out/'used.py') == pre['script_sha256']
        assert config['helper_sha256'] == sha(helper) == pre['helper_sha256']
        assert pre['source'] == config['source']
        assert (config['methods'], config['conditions'], config['budget'], config['fork_step'], config['response_end_step'], config['shift_onset_step']) == (METHODS, CONDITIONS, 100, 10, 25, 5)
        assert sha(config['source']['checkpoint']['path']) == config['source']['checkpoint']['sha256']
        bank = ROOT/('20261004-E20-fresh-control-bank48' if task == 'tworoom' else '20261005-E20-pusht-fresh-control-bank48')
        ledger = read(bank/'ledger.json')
        assert sha(bank/'ledger.json') == config['bank_ledger_sha256']
        original = ROOT/f'20261005-E01-intact-v3-{task}-native-control'
        baseline = read(original/'rows.json')
        assert config['reference_rows_sha256'] == sha(original/'rows.json')
        assert [(r['anchor'], r['condition'], r['method']) for r in rows] == [(j,c,m) for j in range(48) for c in CONDITIONS for m in METHODS]
        normal = np.load(ROOT/f'20261002-{task}-native-s0/action_normalization.npz')
        scaler = StandardScaler()
        scaler.mean_, scaler.scale_ = normal['mean'], normal['std']
        scaler.var_, scaler.n_features_in_ = scaler.scale_**2, 2
        index = {(r['anchor'],r['condition'],r['method']): r for r in rows}
        preparation_steps = 0
        for entry in ledger:
            j, goal = entry['anchor'], np.asarray(entry['goal_state'])
            with np.load(original/f'trace_{j:03d}.npz') as trace:
                nominal_state, nominal_actions = trace['states'], trace['actions']
            prefix_nominal = np.load(out/f'prefix_{j:03d}_nominal.npz')
            n_nominal = len(prefix_nominal['commands'])
            assert np.array_equal(prefix_nominal['states'], nominal_state[:n_nominal+1])
            assert np.array_equal(prefix_nominal['commands'], nominal_actions[:n_nominal])
            for condition in CONDITIONS:
                prefix_path = out/f'prefix_{j:03d}_{condition}.npz'
                with np.load(prefix_path) as prefix:
                    prefix_state, prefix_actions, prefix_applied = prefix['states'], prefix['commands'], prefix['applied']
                    n = len(prefix_actions)
                    assert n <= 10 and prefix_state.shape == (n+1, 2 if task == 'tworoom' else 25)
                    assert np.array_equal(prefix_state[0], np.load(bank/f'factual_states_{j:03d}.npy')[0])
                    assert np.array_equal(prefix['observations'][0], np.load(bank/f'history_{j:03d}.npy')[-1])
                    hit = native_hits(task, prefix_state, goal)
                    if n:
                        assert not hit[:-1].any()
                    if not hit.any():
                        assert n == 10
                    guard = next(g for g in pre['controls'] if (g['anchor'],g['condition']) == (j,condition))
                    assert guard['prefix_sha256'] == sha(prefix_path)
                    assert guard['prefix_env_steps'] == n and guard['absorbed_in_prefix'] == bool(hit.any())
                    assert guard['initial_success'] == bool(hit[0])
                    assert all(guard[k] for k in ['native_nominal_prefix_exact','all_prefix_replay_exact','shift_pre_onset_exact','predicted_tail_exact','original_first_plan_exact'])
                    common = min(6,len(prefix_state),len(prefix_nominal['states']))
                    assert np.array_equal(prefix_state[:common],prefix_nominal['states'][:common])
                    comparable = min(len(prefix_state),len(prefix_nominal['states']))
                    assert guard['actual_trajectory_changed'] == (not np.array_equal(prefix_state[:comparable],prefix_nominal['states'][:comparable]))
                    if task == 'pusht' and condition == 'physics':
                        assert guard['moment_end'] == guard['moment_start'] * (2 if n>5 else 1)
                    if n:
                        planned = np.asarray(baseline[j]['decisions'][0]['standardized_proposal'],dtype=np.float32)
                        assert np.array_equal(prefix_actions,scaler.inverse_transform(planned)[:n])
                    preparation_steps += 2*n
                    features_path = out/f'features_{j:03d}_{condition}.json'
                    features = read(features_path)
                    assert features['prefix_sha256'] == sha(prefix_path) and features['generated_before_all_continuations']
                    if hit.any():
                        assert features['features'] is None and features['absorbed_in_common_prefix']
                    else:
                        array_path = out/f'features_{j:03d}_{condition}.npz'
                        assert sha(array_path) == features['array_sha256']
                        with np.load(array_path) as arrays:
                            expected,observed,zg = arrays['expected_embeddings'],arrays['observed_embeddings'],arrays['goal_embedding']
                            assert expected.shape == observed.shape and expected.shape[:2] == (1,3)
                            assert np.array_equal(expected[:,0],observed[:,0])
                            assert np.array_equal(arrays['initial_plan'].reshape(25,2),planned)
                            fresh = arrays['fresh_plan'].reshape(25,2)
                            recomputed = dict(residual5=float(np.mean((expected[:,1]-observed[:,1])**2)),
                                residual10=float(np.mean((expected[:,2]-observed[:,2])**2)),
                                observed_goal_mse_initial=float(np.mean((observed[:,0]-zg)**2)),
                                observed_goal_mse_fork=float(np.mean((observed[:,-1]-zg)**2)),
                                actor_variance=float(np.exp(2*arrays['log_std']).mean()),
                                plan_disagreement15=float(np.mean((planned[10:]-fresh[:15])**2)))
                            recomputed['goal_progress'] = recomputed['observed_goal_mse_initial']-recomputed['observed_goal_mse_fork']
                            assert features['features'].keys() == recomputed.keys()
                            for key,value in recomputed.items():
                                np.testing.assert_allclose(features['features'][key],value,atol=2e-7,rtol=1e-5)
                for method in METHODS:
                    row = index[j,condition,method]
                    assert (row['episode'],row['goal_span']) == (entry['episode'],entry['goal_span'])
                    path = out/f'trace_{j:03d}_{condition}_{method}.npz'
                    assert sha(path) == row['trace_sha256'] and sha(prefix_path) == row['prefix_sha256'] and sha(features_path) == row['features_sha256']
                    with np.load(path) as trace:
                        state,actions,applied = trace['states'],trace['commands'],trace['applied_commands']
                    total = row['env_steps']
                    assert total <= 100 and state.shape == (total+1,2 if task=='tworoom' else 25)
                    assert actions.shape == applied.shape == (total,2)
                    assert all(np.isfinite(v).all() for v in [state,actions,applied])
                    assert np.array_equal(state[:n+1],prefix_state) and np.array_equal(actions[:n],prefix_actions)
                    assert np.array_equal(applied[:n],prefix_applied)
                    desired_applied = actions.astype(np.float32).copy()
                    if condition == 'gain0.7':
                        desired_applied[5:] *= .7
                    if condition == 'physics' and task == 'tworoom':
                        desired_applied[5:] += np.asarray([.15,0],dtype=np.float32)
                    assert np.array_equal(desired_applied,applied)
                    hit = native_hits(task,state,goal)
                    assert bool(hit.any()) == row['success'] and bool(hit[0]) == row['initial_success']
                    assert row['absorbed_in_common_prefix'] == bool(native_hits(task,prefix_state,goal).any())
                    if total:
                        assert not hit[:-1].any()
                    if not row['success']:
                        assert total == 100
                    if row['absorbed_in_common_prefix']:
                        assert total == n and row['decisions'] == []
                    past = list(entry['warm_actions'])+list(actions[:n])
                    offset = n
                    for d in row['decisions']:
                        assert d['start_step'] == offset
                        assert np.array_equal(np.asarray(d['previous_issued_commands'],dtype=np.float32),np.asarray(past[-5:],dtype=np.float32))
                        proposal = np.asarray(d['standardized_proposal'],dtype=np.float32)
                        if offset < 25:
                            width = 5 if method=='REFRESH5' else 15
                            assert d['kind'] == ('cached-tail' if method=='HOLD' else 'refresh')
                            if method == 'HOLD':
                                assert offset == 10 and proposal.shape == (15,2) and np.array_equal(proposal,planned[10:])
                                assert d['solver_seconds'] == 0
                            else:
                                assert proposal.shape == (25,2) and np.isfinite(d['solver_seconds']) and d['solver_seconds']>0
                                if offset == 10:
                                    assert np.array_equal(proposal,fresh)
                        else:
                            width = 25
                            assert d['kind']=='common-suffix' and proposal.shape==(25,2) and d['solver_seconds']>0
                        width = min(width,(25 if offset<25 else 100)-offset)
                        used = d['executed_steps']
                        assert d['planned_execution_steps'] == width and 0<used<=width
                        assert used==width or row['success']
                        assert np.array_equal(scaler.inverse_transform(proposal)[:used],actions[offset:offset+used])
                        past += list(actions[offset:offset+used])
                        offset += used
                    assert offset == total
                if condition == 'nominal':
                    # Splitting the cached first chunk and common EX25 suffix is
                    # physically identical to the audited original controller.
                    row = index[j,condition,'HOLD']
                    with np.load(out/f'trace_{j:03d}_{condition}_HOLD.npz') as trace:
                        assert np.array_equal(trace['states'],nominal_state) and np.array_equal(trace['commands'],nominal_actions)
                    assert row['success'] == baseline[j]['success']
            prefix_nominal.close()
        assert preparation_steps == complete['preparation_replay_env_steps']
        for condition in CONDITIONS:
            for method in METHODS:
                subset = [index[j,condition,method] for j in range(48)]
                vectors[task,condition,method] = np.asarray([float(r['success']) for r in subset])
                counts.append(dict(task=task,condition=condition,method=method,n=48,
                    successes=sum(r['success'] for r in subset),near_successes=sum(r['success'] for r in subset[:24]),
                    far_successes=sum(r['success'] for r in subset[24:]),initial_successes=sum(r['initial_success'] for r in subset),
                    absorbed_common_prefix=sum(r['absorbed_in_common_prefix'] for r in subset),
                    env_steps=sum(r['env_steps'] for r in subset),
                    response_model_calls=sum(d['kind']=='refresh' for r in subset for d in r['decisions']),
                    suffix_model_calls=sum(d['kind']=='common-suffix' for r in subset for d in r['decisions']),
                    solver_seconds=sum(d['solver_seconds'] for r in subset for d in r['decisions'])))
            guards = [g for g in pre['controls'] if g['condition']==condition]
            controls.append(dict(task=task,condition=condition,n=48,
                trajectory_changed_count=sum(g['actual_trajectory_changed'] for g in guards),
                prefix_absorbed=sum(g['absorbed_in_prefix'] for g in guards)))
        groups.append(dict(config=config,rows_sha256=sha(out/'rows.json'),preflight_sha256=sha(out/'preflight.json'),artifact_directory=str(out)))
        print('Complete same-state causal/shift/source audit',task,'432 PASS',flush=True)
    rng = np.random.default_rng(120001)
    effects,oracle = [],[]
    for task in ['tworoom','pusht']:
        for condition in CONDITIONS:
            for method in ['REFRESH15','REFRESH5']:
                difference = vectors[task,condition,method]-vectors[task,condition,'HOLD']
                for tier,ids in [('all',np.arange(48)),('near',np.arange(24)),('far',np.arange(24,48))]:
                    draws = rng.choice(ids,(10000,len(ids)),replace=True)
                    effects.append(dict(task=task,condition=condition,method=method,reference='HOLD',tier=tier,n=len(ids),
                        mean_delta=float(difference[ids].mean()),helped=int((difference[ids]>0).sum()),
                        harmed=int((difference[ids]<0).sum()),paired_anchor_bootstrap_95=np.quantile(difference[draws].mean(1),[.025,.975]).tolist(),train_sources=1))
            values = np.stack([vectors[task,condition,method] for method in METHODS])
            oracle.append(dict(task=task,condition=condition,clairvoyant_union_successes=int(values.max(0).sum()),
                best_fixed_successes=int(values.sum(1).max()),scope='Future-label ceiling only; no trained or deployable router.'))
    result = dict(completed=True,new_continuations=864,groups=groups,counts=counts,effects=effects,controls=controls,
        oracle_diagnostics=oracle,script_sha256=sha(__file__),
        scope='Full joint source0, one matched 15step intervention window, common EX25 suffix, all original48 goals per task/condition including absorbed starts. Native state, issued-vs-hidden-applied commands, causal history, prefix/source/features all audited. One trainseed, development data; no gate or novelty/causal observer-only claim.')
    dest = ROOT/'20261005-E18-intact-fork-v2-audit'
    assert not dest.exists()
    dest.mkdir()
    shutil.copy2(__file__,dest/'used.py')
    save(dest/'result.json',result)
    result['full_audit_artifact'] = str(dest/'result.json')
    save(WB/'results/E18_20261005_intact_recovery_fork_results.json',result)


if __name__ == '__main__':
    main()
