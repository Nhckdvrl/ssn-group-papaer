"""Independent whole-matrix F3 source, execution and typed-query audit."""
import shutil
import numpy as np
import torch
import intact_published_control_v3 as a
import intact_multi_seed_source as s
from intact_recovery_forks_audit_v2 import native_hits, CONDITIONS
from experience_transfer_control_audit import ROOT, WB, read, save, sha

SEEDS = [0, 42, 3072]
METHODS = ['BASE25', 'GOAL15', 'GOAL5', 'REFERENCE5']


@torch.inference_mode()
def main():
    a.setup()
    # No efficacy report from a partial task/seed matrix.
    for task in ['tworoom', 'pusht']:
        for seed in SEEDS:
            assert read(ROOT/f'20261005-E18-intact-F3-{task}-s{seed}-pipeline.json') == dict(completed=True, task=task, seed=seed, n=576)
    groups, counts, vectors = [], [], {}
    for task in ['tworoom', 'pusht']:
        bank = s.bank(task)
        ledger = read(bank/'ledger.json')
        assert len(ledger) == 48 and [r['anchor'] for r in ledger] == list(range(48))
        for seed in SEEDS:
            net, processor, source = s.source(task, seed, 'cpu')
            before = a.state_hash(net.state_dict())
            prefix = ROOT/f'20261005-E18-intact-F3-{task}-s{seed}'
            pre = prefix.with_name(prefix.name+'-preflight')
            guards = read(pre/'controls.json')
            assert not (pre/'failure.json').exists()
            assert guards['passed'] and guards['n'] == 48 and guards['source'] == source and guards['model_unchanged']
            assert guards['script_sha256'] == sha(pre/'used.py') == sha(WB/'scripts/intact_full_recovery_control.py')
            assert [g['device'] for g in guards['cpu_cuda']] == ['cpu', 'cuda']
            assert all(all(g[k] for k in ['passed', 'first_short_full_exact', 'goal_manual_exact', 'local_manual_exact', 'clamped_std_exact', 'model_unchanged']) for g in guards['cpu_cuda'])
            checked = 0
            for condition in CONDITIONS:
                for method in METHODS:
                    out = prefix.with_name(prefix.name+f'-{condition}-{method}')
                    assert not (out/'failure.json').exists()
                    assert read(out/'complete.json') == dict(completed=True, n=48, model_unchanged=True)
                    cfg, rows = read(out/'config.json'), read(out/'rows.json')
                    assert (cfg['task'], cfg['published_train_seed'], cfg['method'], cfg['condition'], cfg['budget'], cfg['shift_onset_step']) == (task, seed, method, condition, 100, 5)
                    assert cfg['source'] == source and cfg['preflight_sha256'] == sha(pre/'controls.json')
                    assert cfg['bank_ledger_sha256'] == sha(bank/'ledger.json')
                    assert cfg['script_sha256'] == sha(out/'used.py') == guards['script_sha256']
                    for field, file in [('source_helper_sha256', s.__file__), ('actor_helper_sha256', a.__file__), ('fork_helper_sha256', WB/'scripts/intact_recovery_forks_v2.py'), ('waypoint_helper_sha256', WB/'scripts/intact_waypoint_recovery.py')]:
                        assert cfg[field] == sha(file)
                    assert [r['anchor'] for r in rows] == list(range(48))
                    for entry, row, guard in zip(ledger, rows, guards['controls']):
                        j = entry['anchor']
                        assert guard['anchor'] == j and guard['all_warm_state_pixels_exact'] and guard['short_full_first_macro_exact'] and guard['official_reference_recursion']
                        initial_path = pre/f'initial_plan_{j:03d}.npz'
                        assert guard['arrays_sha256'] == sha(initial_path)
                        assert (row['episode'], row['goal_span']) == (entry['episode'], entry['goal_span'])
                        paths = [out/f'{kind}_{j:03d}.npz' for kind in ['trace', 'queries', 'references']]
                        for field, path in zip(['trace_sha256', 'queries_sha256', 'references_sha256'], paths):
                            assert row[field] == sha(path)
                        with np.load(paths[0]) as trace:
                            state, commands, applied = [trace[k] for k in ['states', 'commands', 'applied_commands']]
                        total = row['env_steps']
                        assert 0 <= total <= 100 and state.shape == (total+1, 2 if task == 'tworoom' else 25)
                        assert commands.shape == applied.shape == (total, 2)
                        assert all(np.isfinite(v).all() for v in [state, commands, applied])
                        assert np.array_equal(state[0], np.load(bank/f'factual_states_{j:03d}.npy')[0])
                        hit = native_hits(task, state, np.asarray(entry['goal_state']))
                        assert bool(hit.any()) == row['success'] and bool(hit[0]) == row['initial_success']
                        assert total == 100 or row['success']
                        if total:
                            assert not hit[:-1].any()
                        desired = commands.astype(np.float32).copy()
                        if condition == 'gain0.7':
                            desired[5:] *= .7
                        if condition == 'physics' and task == 'tworoom':
                            desired[5:] += np.asarray([.15, 0], dtype=np.float32)
                        assert np.array_equal(desired, applied)
                        with np.load(paths[1]) as queries, np.load(paths[2]) as references, np.load(initial_path) as initial:
                            qindex, rindex, offset = 0, 0, 0
                            past = list(entry['warm_actions'])
                            ref, cycle = None, None
                            for d in row['decisions']:
                                assert d['start_step'] == offset and d['solver_seconds'] > 0 and np.isfinite(d['solver_seconds'])
                                previous = np.asarray(past[-5:], dtype=np.float32)
                                assert np.array_equal(previous, np.asarray(d['previous_issued_commands'], dtype=np.float32))
                                proposal = np.asarray(d['standardized_proposal'], dtype=np.float32)
                                if offset == 0:
                                    assert np.array_equal(proposal[:5], initial['standardized_plan'][:5])
                                    if method != 'GOAL5':
                                        assert np.array_equal(proposal, initial['standardized_plan'])
                                if method == 'REFERENCE5' and offset % 25:
                                    assert d['kind'] == 'local-reference' and proposal.shape == (5, 2)
                                    assert int(queries['step'][qindex]) == offset and int(queries['cycle_start'][qindex]) == cycle
                                    current, target, previous_emb = [torch.from_numpy(queries[key][qindex]) for key in ['current', 'target', 'previous']]
                                    assert np.array_equal(target.numpy(), ref[:, (offset-cycle)//5+1])
                                    causal = torch.as_tensor(processor.transform(previous.reshape(1, 1, 10))).float()
                                    np.testing.assert_allclose(previous_emb.numpy(), net.action_encoder(causal)[:, -1].numpy(), atol=2e-4, rtol=1e-5)
                                    delta = target-current
                                    grammar = torch.cat([current, delta, torch.zeros_like(current), current*delta, previous_emb], -1)
                                    assert torch.equal(grammar, net.inverse_actor.actor_features(current, target, previous_emb))
                                    mean, log_std = net.inverse_actor.net(grammar).chunk(2, -1)
                                    log_std = log_std.clamp(net.inverse_actor.min_log_std, net.inverse_actor.max_log_std)
                                    np.testing.assert_allclose(mean.numpy(), queries['mean'][qindex], atol=2e-4, rtol=1e-5)
                                    np.testing.assert_allclose(log_std.numpy(), queries['log_std'][qindex], atol=2e-4, rtol=1e-5)
                                    assert np.array_equal(proposal, queries['mean'][qindex].reshape(5, 2))
                                    qindex += 1
                                    checked += 1
                                    width = 5
                                else:
                                    width = {'BASE25': 25, 'GOAL15': 15, 'GOAL5': 5, 'REFERENCE5': 5}[method]
                                    assert proposal.shape == ((5 if method == 'GOAL5' else 25), 2)
                                    if method == 'REFERENCE5':
                                        assert d['kind'] == 'reference-start' and int(references['step'][rindex]) == offset
                                        cycle, ref = offset, references['reference'][rindex]
                                        assert ref.shape[:2] == (1, 6) and np.isfinite(ref).all()
                                        assert np.array_equal(references['standardized_plan'][rindex], proposal)
                                        assert d['reference_generation_seconds'] == float(references['reference_generation_seconds'][rindex]) > 0
                                        if offset == 0:
                                            assert np.array_equal(ref, initial['reference'])
                                        rindex += 1
                                    else:
                                        assert d['kind'] == 'goal'
                                width = min(width, 100-offset)
                                used = d['executed_steps']
                                assert d['planned_execution_steps'] == width and 0 < used <= width
                                assert used == width or row['success']
                                assert np.array_equal(processor.scaler.inverse_transform(proposal)[:used], commands[offset:offset+used])
                                past += list(commands[offset:offset+used])
                                offset += used
                            assert offset == total and qindex == len(queries['step']) and rindex == len(references['step'])
                    vectors[task, seed, condition, method] = np.asarray([float(r['success']) for r in rows])
                    counts.append(dict(task=task, seed=seed, condition=condition, method=method, n=48,
                        successes=sum(r['success'] for r in rows), near_successes=sum(r['success'] for r in rows[:24]), far_successes=sum(r['success'] for r in rows[24:]),
                        initial_successes=sum(r['initial_success'] for r in rows), env_steps=sum(r['env_steps'] for r in rows),
                        decisions=sum(len(r['decisions']) for r in rows), solver_seconds=sum(d['solver_seconds'] for r in rows for d in r['decisions']),
                        reference_generation_seconds=sum(d['reference_generation_seconds'] for r in rows for d in r['decisions'])))
                    groups.append(dict(config=cfg, rows_sha256=sha(out/'rows.json'), artifact_directory=str(out)))
            assert before == a.state_hash(net.state_dict())
            print('Full deployment source/native/causal/typed-query audit', task, seed, '576 PASS', 'local_queries', checked, flush=True)
    rng = np.random.default_rng(121101)
    effects = []
    for task in ['tworoom', 'pusht']:
        for condition in CONDITIONS:
            for baseline in METHODS[:-1]:
                delta = np.stack([vectors[task, seed, condition, 'REFERENCE5']-vectors[task, seed, condition, baseline] for seed in SEEDS])
                for tier, ids in [('all', np.arange(48)), ('near', np.arange(24)), ('far', np.arange(24, 48))]:
                    # Crossed resampling: same anchor IDs across sampled model sources.
                    source_draw = rng.integers(0, 3, (10000, 3, 1))
                    anchor_draw = rng.choice(ids, (10000, 1, len(ids)), replace=True)
                    draws = delta[source_draw, anchor_draw].mean((1, 2))
                    effects.append(dict(task=task, condition=condition, reference=baseline, method='REFERENCE5', tier=tier,
                        train_sources=3, n_unique_anchors=len(ids), mean_delta=float(delta[:, ids].mean()),
                        helped=int((delta[:, ids]>0).sum()), harmed=int((delta[:, ids]<0).sum()),
                        per_seed_delta={str(seed):float(delta[k, ids].mean()) for k, seed in enumerate(SEEDS)},
                        crossed_source_anchor_bootstrap_95=np.quantile(draws, [.025, .975]).tolist()))
    result = dict(completed=True, new_episodes=3456, counts=counts, effects=effects, groups=groups, script_sha256=sha(__file__),
        scope='Full new48/task deployment, three independent published seeds. Complete fixed designs/conditions retained. Native success, causal commands, source and every stored local actor query independently verified on CPU. Actual-image encoding and world-reference recursion guarded in producer/preflight, not independently repeated for every deployed query. Crossed source/anchor bootstrap with only three sources; unknown pretraining overlap. No novel-method or timing/scale claim.')
    dest = ROOT/'20261005-E18-intact-F3-audit'
    assert not dest.exists()
    dest.mkdir()
    shutil.copy2(__file__, dest/'used.py')
    save(dest/'result.json', result)
    result['full_audit_artifact'] = str(dest/'result.json')
    save(WB/'results/E18_20261005_intact_full_recovery_results.json', result)


if __name__ == '__main__':
    main()
