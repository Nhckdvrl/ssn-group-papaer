"""Independently replay every H0 trace and recompute all visual action queries."""
import shutil
import numpy as np
import torch
import intact_published_control_v3 as a
from experience_transfer_control_audit import ROOT, WB, read, save, sha

METHODS = ['OPEN25', 'GOAL5', 'REFERENCE5']
GOALS = [0]+list(range(2, 12))


def diagnostic(task, env):
    return np.asarray(env._get_obs(), dtype=np.float64) if task == 'tworoom' else a.p.diagnostic(env)


def native_hits(task, states, goal):
    if task == 'tworoom':
        return np.linalg.norm(states[:, :2]-goal, axis=-1) < 16
    delta = np.abs(states[:, 4]-goal[4])
    return (np.linalg.norm(states[:, :4]-goal[:4], axis=-1) < 20) & (np.minimum(delta, 2*np.pi-delta) < np.pi/9)


def mean(net, current, target, previous):
    delta = target-current
    inputs = torch.cat([current, delta, torch.zeros_like(current), current*delta, previous], -1)
    mu, std = net.inverse_actor.net(inputs).chunk(2, -1)
    return mu, std.clamp(net.inverse_actor.min_log_std, net.inverse_actor.max_log_std)


def append(net, emb, past, action):
    # Independent explicit indexing, not the producer reference helper.
    width = min(net.predictor.pos_embedding.size(1), emb.size(1), past.size(1))
    context = past[:, -width:].clone()
    context[:, -1] = action
    predicted = net.predict(emb[:, -width:], net.action_encoder(context))[:, -1:]
    return torch.cat([emb, predicted], 1), torch.cat([past, action[:, None]], 1)


@torch.inference_mode()
def main():
    a.setup()
    for task in ['tworoom', 'pusht']:
        assert read(ROOT/f'20261005-E14-controller-consequence-{task}/complete.json') == dict(completed=True, n=1452, model_unchanged=True)
    groups, counts, effects, coverage = [], [], [], []
    rng = np.random.default_rng(123101)
    for task in ['tworoom', 'pusht']:
        net, processor, source = a.source(task, 'cuda')
        before = a.state_hash(net.state_dict())
        out = ROOT/f'20261005-E14-controller-consequence-{task}'
        cfg, pre, rows = read(out/'config.json'), read(out/'preflight.json'), read(out/'rows.json')
        assert not (out/'failure.json').exists() and cfg['source'] == pre['source'] == source
        assert cfg['script_sha256'] == sha(out/'used.py') == sha(WB/'scripts/controller_consequence_bank.py')
        assert cfg['methods'] == METHODS and cfg['goals'] == GOALS and cfg['budget'] == 25
        for field, file in [('actor_helper_sha256', a.__file__), ('fork_helper_sha256', WB/'scripts/intact_recovery_forks_v2.py'), ('waypoint_helper_sha256', WB/'scripts/intact_waypoint_recovery.py')]:
            assert cfg[field] == sha(file)
        bank = ROOT/'20261004-E20-legal-effect-bank44'
        assert cfg['source_ledger_sha256'] == sha(bank/'ledger.json') and cfg['source_rows_sha256'] == sha(bank/'rows.json')
        ledger = sorted([e for e in read(bank/'ledger.json') if e['task'] == task], key=lambda e:e['anchor'])
        original = {(r['anchor'], r['branch']):r for r in read(bank/'rows.json') if r['task'] == task}
        supplied_goals = {}
        for j in range(44):
            for branch in GOALS:
                path = bank/f'{task}_{j:03d}_b{branch:02d}.npz'
                assert sha(path) == original[j, branch]['trace_sha256']
                with np.load(path) as raw:
                    supplied_goals[j, branch] = (raw['diagnostic_states'][-1, :2 if task == 'tworoom' else 7].copy(), raw['pixels'][-1].copy())
        assert pre['passed'] and pre['n'] == 44 and [g['anchor'] for g in pre['controls']] == list(range(44))
        assert all(g['warm_pixels_exact'] and g['complete_diagnostic_exact'] and g['factual25_replay_exact'] for g in pre['controls'])
        assert [g['device'] for g in pre['cpu_cuda']] == ['cpu', 'cuda']
        assert all(g['passed'] and g['short_full_exact'] and g['typed_global_local_mean_std_exact'] for g in pre['cpu_cuda'])
        assert [(r['anchor'], r['goal_branch'], r['method']) for r in rows] == [(j, g, m) for j in range(44) for g in GOALS for m in METHODS]
        vectors = {m:np.zeros((44, 11)) for m in METHODS}
        matrix = {m:np.zeros((44, 11, 11), dtype=bool) for m in METHODS}
        terminal = {m:np.zeros((44, 11, 11), dtype=bool) for m in METHODS}
        visual_queries = 0
        for row in rows:
            j, branch, method = row['anchor'], row['goal_branch'], row['method']
            stem = f'{j:03d}_g{branch:02d}_{method}'
            path, qpath = out/f'trace_{stem}.npz', out/f'queries_{stem}.npz'
            assert row['trace_sha256'] == sha(path) and row['queries_sha256'] == sha(qpath)
            with np.load(path) as data, np.load(qpath) as queries:
                states, commands, images, steps = [data[k] for k in ['states', 'commands', 'observations', 'observation_steps']]
                goal, goal_image, warm, reference = [data[k] for k in ['goal_state', 'goal_image', 'warm_history', 'reference']]
                assert np.array_equal(goal, supplied_goals[j, branch][0]) and np.array_equal(goal_image, supplied_goals[j, branch][1])
                n = row['env_steps']
                assert n <= 25 and states.shape == (n+1, 10 if task == 'tworoom' else 25) and commands.shape == (n, 2)
                assert np.isfinite(states).all() and np.isfinite(commands).all() and images.dtype == np.uint8
                assert steps[0] == 0 and steps[-1] == n and len(steps) == len(images)
                hit = native_hits(task, states, goal)
                assert bool(hit.any()) == row['success'] and bool(hit[0]) == row['initial_success']
                assert n == 25 or row['success']
                if n:
                    assert not hit[:-1].any()
                # Verify physical execution and all saved observed pixels, including query frames.
                env, replayed_warm = a.restore(task, ledger[j])
                assert np.array_equal(warm, replayed_warm)
                physical = a.diagnostic(task, env)
                env._set_goal_state(goal)
                assert np.array_equal(physical, a.diagnostic(task, env))
                assert np.array_equal(states[0], diagnostic(task, env)) and np.array_equal(images[0], env.render())
                for k, command in enumerate(commands):
                    _, _, done, truncated, _ = env.step(command.astype(np.float32))
                    assert not truncated and bool(done) == bool(hit[k+1])
                    assert np.array_equal(states[k+1], diagnostic(task, env))
                    if k+1 in steps:
                        assert np.array_equal(images[np.flatnonzero(steps == k+1)[0]], env.render())
                env.close()
                offset, qindex, past = 0, 0, list(ledger[j]['warm_actions'])
                for d in row['decisions']:
                    assert d['step'] == offset
                    image = images[np.flatnonzero(steps == offset)[0]]
                    previous = np.asarray(past[-5:], dtype=np.float32)
                    assert np.array_equal(previous, np.asarray(d['previous_issued_commands'], dtype=np.float32))
                    inputs = a.info(image, goal_image, past, processor, 'cuda')
                    emb = net.encode(dict(pixels=inputs['pixels']))['emb']
                    action_history = inputs['action'].clone()
                    previous_emb = net.action_encoder(action_history)[:, -1]
                    proposal = np.asarray(d['standardized_proposal'], dtype=np.float32)
                    if method == 'REFERENCE5' and offset:
                        assert d['kind'] == 'local-reference' and int(queries['step'][qindex]) == offset
                        assert np.array_equal(emb[:, -1].cpu().numpy(), queries['current'][qindex])
                        assert np.array_equal(previous_emb.cpu().numpy(), queries['previous'][qindex])
                        target = torch.from_numpy(reference[:, offset//5+1]).cuda()
                        assert np.array_equal(target.cpu().numpy(), queries['target'][qindex])
                        mu, std = mean(net, emb[:, -1], target, previous_emb)
                        assert np.array_equal(mu.cpu().numpy(), queries['mean'][qindex]) and np.array_equal(std.cpu().numpy(), queries['log_std'][qindex])
                        recomputed = mu.cpu().numpy().reshape(5, 2)
                        qindex += 1
                    else:
                        assert d['kind'] == 'goal'
                        zgoal = net.encode(dict(pixels=inputs['goal']))['emb'][:, -1]
                        proposed, refs = [], [emb[:, -1].clone()]
                        for _ in range(1 if method == 'GOAL5' else 5):
                            mu, _ = mean(net, emb[:, -1], zgoal, net.action_encoder(action_history[:, -1:])[:, -1])
                            proposed.append(mu)
                            emb, action_history = append(net, emb, action_history, mu)
                            refs.append(emb[:, -1].clone())
                        recomputed = torch.stack(proposed, 1).cpu().numpy().reshape(-1, 2)
                        if method == 'REFERENCE5':
                            assert np.array_equal(torch.stack(refs, 1).cpu().numpy(), reference)
                    assert np.array_equal(recomputed, proposal)
                    visual_queries += 1
                    used = d['executed_steps']
                    assert 0 < used <= (25 if method == 'OPEN25' else 5)
                    assert np.array_equal(processor.scaler.inverse_transform(proposal)[:used], commands[offset:offset+used])
                    past += list(commands[offset:offset+used])
                    offset += used
                assert offset == n and qindex == len(queries['step'])
                goal_index = GOALS.index(branch)
                vectors[method][j, goal_index] = row['success']
                for k, other in enumerate(GOALS):
                    other_goal = supplied_goals[j, other][0]
                    cross = native_hits(task, states, other_goal)
                    matrix[method][j, goal_index, k] = cross.any()
                    terminal[method][j, goal_index, k] = cross[-1]
        assert before == a.state_hash(net.state_dict())
        for method in METHODS:
            subset = [r for r in rows if r['method'] == method]
            counts.append(dict(task=task, method=method, n_queries=484, unique_anchors=44, source_models=1,
                successes=sum(r['success'] for r in subset), initial_successes=sum(r['initial_success'] for r in subset),
                env_steps=sum(r['env_steps'] for r in subset), decisions=sum(len(r['decisions']) for r in subset)))
            valid = ~np.eye(11, dtype=bool)[None]
            coverage.append(dict(task=task, method=method, n_final_goals=484,
                anytime_leave_self_goal_oracle=int((matrix[method]&valid).any(1).sum()),
                terminal_leave_self_goal_oracle=int((terminal[method]&valid).any(1).sum()),
                scope='Offline union over alternative subgoal controllers; not deployable selection, primitive bank comparison or independent 484-state estimate.'))
        for method, baseline in [('GOAL5', 'OPEN25'), ('REFERENCE5', 'OPEN25'), ('REFERENCE5', 'GOAL5')]:
            delta = vectors[method]-vectors[baseline]
            ids = rng.integers(0, 44, (10000, 44))
            effects.append(dict(task=task, method=method, reference=baseline, mean_delta=float(delta.mean()),
                helped=int((delta>0).sum()), harmed=int((delta<0).sum()), unique_anchors=44, queries_per_anchor=11,
                paired_anchor_bootstrap_95=np.quantile(delta[ids].mean((1, 2)), [.025, .975]).tolist(), source_models=1))
        groups.append(dict(config=cfg, rows_sha256=sha(out/'rows.json'), preflight_sha256=sha(out/'preflight.json'), independent_visual_queries=visual_queries, artifact_directory=str(out)))
        print('Full controller-outcome replay/visual/manual-query audit', task, '1452 PASS', visual_queries, flush=True)
    result = dict(completed=True, new_continuations=2904, groups=groups, counts=counts, effects=effects, coverage=coverage,
        script_sha256=sha(__file__), scope='Development44/task, one frozen source0, 11 supplied experience subgoals/3fixed controllers/25budget. Every physical trace and query observation replayed; every visual encoding, global plan and local query independently recomputed on same-hardware CUDA with explicit actor grammar and world recursion. Not a trained option-outcome method or paper-scale demonstration; candidate-oracle labels offline only.')
    dest = ROOT/'20261005-E14-controller-consequence-audit'
    assert not dest.exists()
    dest.mkdir()
    shutil.copy2(__file__, dest/'used.py')
    save(dest/'result.json', result)
    result['full_audit_artifact'] = str(dest/'result.json')
    save(WB/'results/E14_20261005_controller_consequence_results.json', result)


if __name__ == '__main__':
    main()
