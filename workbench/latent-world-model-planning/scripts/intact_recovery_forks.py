"""E18 F1: exact replay forks, one response window, common future policy.

Hidden interventions belong to the evaluator. Feature generation receives only
past images, issued commands, the frozen model, and the supplied goal image.
"""
import argparse
import shutil
import time
import numpy as np
import torch
import intact_published_control_v3 as a
from experience_transfer_control_audit import ROOT, read, save, sha

CONDITIONS = ['nominal', 'gain0.7', 'physics']
METHODS = ['HOLD', 'REFRESH15', 'REFRESH5']


def call(net, inputs, horizon=5, prefix=None):
    torch.cuda.synchronize()
    tick = time.perf_counter()
    proposal = net.get_action(inputs, horizon=horizon, prefix_actions=prefix)
    torch.cuda.synchronize()
    return proposal, time.perf_counter()-tick


def advance(task, env, command, condition, step):
    """The policy never receives condition, applied command, or physics state."""
    if condition == 'physics' and task == 'pusht' and step == 5:
        env.block.moment *= 2.
    applied = np.asarray(command, dtype=np.float32).copy()
    if step >= 5:
        if condition == 'gain0.7':
            applied *= .7
        if condition == 'physics' and task == 'tworoom':
            applied += np.asarray([.15, 0.], dtype=np.float32)
    _, _, done, truncated, _ = env.step(applied)
    assert not truncated
    return a.diagnostic(task, env), applied, bool(done)


def prefix(task, entry, commands, condition):
    env, history = a.restore(task, entry)
    j = entry['anchor']
    assert np.array_equal(history, np.load(a.bank(task)/f'history_{j:03d}.npy'))
    state = a.diagnostic(task, env)
    assert np.array_equal(state, np.load(a.bank(task)/f'factual_states_{j:03d}.npy')[0])
    goal = np.asarray(entry['goal_state'])
    states, issued, applied, observations = [state], [], [], [env.render().copy()]
    reached = a.success(task, state, goal)
    initial_success = reached
    moment_start = float(env.block.moment) if task == 'pusht' else None
    for step, command in enumerate(commands[:10]):
        if reached:
            break
        state, executed, done = advance(task, env, command, condition, step)
        reached = a.success(task, state, goal)
        assert done == reached
        states.append(state)
        issued.append(command)
        applied.append(executed)
        if (step+1) % 5 == 0:
            observations.append(env.render().copy())
    return env, dict(states=np.asarray(states), commands=np.asarray(issued, dtype=np.float32).reshape(-1, 2),
                     applied=np.asarray(applied, dtype=np.float32).reshape(-1, 2), observations=np.asarray(observations),
                     current=env.render().copy(), reached=reached, initial_success=initial_success,
                     moment_start=moment_start, moment_end=float(env.block.moment) if task == 'pusht' else None)


def equal_prefix(left, right):
    for key in ['states', 'commands', 'applied', 'observations', 'current']:
        assert np.array_equal(left[key], right[key]), key
    for key in ['reached', 'initial_success', 'moment_start', 'moment_end']:
        assert left[key] == right[key], key


def observable_features(net, scaler, initial_info, observed_pixels, issued_past, initial_plan, goal_pixels):
    """No hidden condition, privileged state, or future outcome argument."""
    assert observed_pixels.shape[0] == 3
    z = net.encode(dict(pixels=initial_info['pixels']))['emb']
    history = initial_info['action'].clone()
    expected = [z[:, -1].clone()]
    for k in range(2):
        z, history = net.rollout_one_step(z, initial_plan[:, k], history,
                                         history_size=net.predictor.pos_embedding.size(1))
        expected.append(z[:, -1].clone())
    truth = [net.encode(dict(pixels=a.pixels(image[None, None], 'cuda')))['emb'][:, -1]
             for image in observed_pixels]
    assert torch.equal(truth[0], expected[0])
    inputs = a.info(observed_pixels[-1], goal_pixels, issued_past, scaler, 'cuda')
    fresh, elapsed = call(net, inputs)
    goal = net.encode(dict(pixels=inputs['goal']))['emb'][:, -1]
    previous = net.action_encoder(inputs['action'])[:, -1]
    stats = net.inverse_action_distribution(truth[-1], goal, previous)
    assert torch.equal(stats['map_mean'], fresh[:, 0])
    features = dict(residual5=float((truth[1]-expected[1]).square().mean()),
                    residual10=float((truth[2]-expected[2]).square().mean()),
                    observed_goal_mse_initial=float((truth[0]-goal).square().mean()),
                    observed_goal_mse_fork=float((truth[-1]-goal).square().mean()),
                    goal_progress=float((truth[0]-goal).square().mean()-(truth[-1]-goal).square().mean()),
                    actor_variance=float(stats['log_std'].mul(2).exp().mean()),
                    plan_disagreement15=float((initial_plan[:, 2:].reshape(15, 2)-fresh.reshape(25, 2)[:15]).square().mean()))
    assert all(np.isfinite(value) for value in features.values())
    arrays = dict(expected_embeddings=torch.stack(expected, 1).cpu().numpy(),
                  observed_embeddings=torch.stack(truth, 1).cpu().numpy(),
                  goal_embedding=goal.cpu().numpy(), log_std=stats['log_std'].cpu().numpy(),
                  fresh_plan=fresh.cpu().numpy(), initial_plan=initial_plan.cpu().numpy())
    return features, fresh.cpu().numpy().reshape(25, 2), arrays, elapsed


@torch.inference_mode()
def run(task):
    a.setup()
    net, scaler, source = a.source(task, 'cuda')
    initial_hash = a.state_hash(net.state_dict())
    bank = a.bank(task)
    ledger = read(bank/'ledger.json')
    original = ROOT/f'20261005-E01-intact-v3-{task}-native-control'
    baseline = read(original/'rows.json')
    out = ROOT/f'20261005-E18-intact-forks-{task}'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__, out/'used.py')
    try:
        # Inherited actual CPU/CUDA and all-48 guards, matched source identity.
        for device in ['cpu', 'cuda']:
            guard = read(ROOT/f'20261005-E01-intact-v3-{task}-{device}-preflight/controls.json')
            assert guard['passed'] and guard['script_sha256'] == sha(a.__file__) and guard['source'] == source
        feedback = read(ROOT/f'20261005-E18-intact-feedback-{task}-preflight/controls.json')
        assert feedback['passed'] and feedback['source'] == source
        save(out/'config.json', dict(task=task, methods=METHODS, conditions=CONDITIONS, n_anchors=48,
             fork_step=10, response_end_step=25, budget=100, shift_onset_step=5, train_seed=0,
             source=source, script_sha256=sha(__file__), helper_sha256=sha(a.__file__),
             bank_ledger_sha256=sha(bank/'ledger.json'), reference_rows_sha256=sha(original/'rows.json'),
             feature_inputs='observed pixels, past issued commands, goal pixels, frozen model only',
             hardware=torch.cuda.get_device_name(),
             scope='Same-state one 15step response window, EX25 common suffix; full joint published source0, 48 development goals. Hidden shifts never enter policy/features; one seed, no router or novelty claim.'))
        prepared, guards = [], []
        for entry in ledger:
            j = entry['anchor']
            goal_image = np.load(bank/f'goal_{j:03d}.npy')
            current = np.load(bank/f'history_{j:03d}.npy')[-1]
            inp = a.info(current, goal_image, entry['warm_actions'], scaler, 'cuda')
            proposal, _ = call(net, inp)
            plan = proposal.cpu().numpy().reshape(25, 2)
            if not baseline[j]['initial_success']:
                assert np.array_equal(plan, np.asarray(baseline[j]['decisions'][0]['standardized_proposal'], dtype=np.float32))
            tail, _ = call(net, inp, horizon=3, prefix=proposal[:, :2])
            assert torch.equal(tail, proposal[:, 2:])
            commands = scaler.scaler.inverse_transform(plan)
            records = {}
            for condition in CONDITIONS:
                env, record = prefix(task, entry, commands, condition)
                env.close()
                repeated, second = prefix(task, entry, commands, condition)
                equal_prefix(record, second)
                repeated.close()
                records[condition] = record
                path = out/f'prefix_{j:03d}_{condition}.npz'
                np.savez_compressed(path, **{k: record[k] for k in ['states','commands','applied','observations','current']})
                if not record['reached']:
                    features, fresh, arrays, seconds = observable_features(
                        net, scaler, inp, record['observations'],
                        list(entry['warm_actions'])+list(record['commands']), proposal, goal_image)
                    array_path = out/f'features_{j:03d}_{condition}.npz'
                    np.savez_compressed(array_path, **arrays)
                    save(out/f'features_{j:03d}_{condition}.json', dict(features=features, array_sha256=sha(array_path),
                         array_path=str(array_path), prefix_sha256=sha(path), generated_before_all_continuations=True))
                else:
                    features, fresh, seconds = None, None, None
                    save(out/f'features_{j:03d}_{condition}.json', dict(features=None, prefix_sha256=sha(path),
                         absorbed_in_common_prefix=True, generated_before_all_continuations=True))
                record.update(plan=plan, fresh=fresh, preparation_feature_seconds=seconds)
            nominal = records['nominal']
            with np.load(original/f'trace_{j:03d}.npz') as trace:
                length = len(nominal['commands'])
                assert np.array_equal(nominal['states'], trace['states'][:length+1])
                assert np.array_equal(nominal['commands'], trace['actions'][:length])
            for condition in CONDITIONS:
                record = records[condition]
                common = min(6, len(record['states']), len(nominal['states']))
                assert np.array_equal(record['states'][:common], nominal['states'][:common])
                if task == 'pusht' and condition == 'physics' and len(record['commands']) > 5:
                    assert record['moment_end'] == 2*record['moment_start']
                comparable = min(len(record['states']), len(nominal['states']))
                changed = not np.array_equal(record['states'][:comparable], nominal['states'][:comparable])
                guards.append(dict(anchor=j, condition=condition, native_nominal_prefix_exact=True,
                     all_prefix_replay_exact=True, shift_pre_onset_exact=True, actual_trajectory_changed=changed,
                     absorbed_in_prefix=record['reached'], initial_success=record['initial_success'],
                     prefix_env_steps=len(record['commands']), moment_start=record['moment_start'], moment_end=record['moment_end'],
                     predicted_tail_exact=True, original_first_plan_exact=True,
                     prefix_sha256=sha(out/f'prefix_{j:03d}_{condition}.npz')))
            prepared.append(records)
            print('INTACT fork all-condition prepare', task, j, 'PASS', flush=True)
        assert initial_hash == a.state_hash(net.state_dict())
        save(out/'preflight.json', dict(passed=True, n=144, controls=guards, model_unchanged=True,
             script_sha256=sha(__file__), helper_sha256=sha(a.__file__), source=source))
        # All conditions/states prepared and their features saved before efficacy.
        rows = []
        for entry, records in zip(ledger, prepared):
            j = entry['anchor']
            goal = np.asarray(entry['goal_state'])
            goal_image = np.load(bank/f'goal_{j:03d}.npy')
            for condition in CONDITIONS:
                reference = records[condition]
                raw_plan = scaler.scaler.inverse_transform(reference['plan'])
                for method in METHODS:
                    env, repeat = prefix(task, entry, raw_plan, condition)
                    equal_prefix(reference, repeat)
                    states = list(repeat['states'])
                    commands = list(repeat['commands'])
                    applied_commands = list(repeat['applied'])
                    past = list(entry['warm_actions'])+list(commands)
                    reached = repeat['reached']
                    decisions = []
                    while not reached and len(commands) < 100:
                        step = len(commands)
                        previous = np.asarray(past[-5:], dtype=np.float32)
                        if step < 25 and method == 'HOLD':
                            proposal = reference['plan'][10:]
                            width, kind, seconds = 15, 'cached-tail', 0.
                        else:
                            inputs = a.info(env.render().copy(), goal_image, past, scaler, 'cuda')
                            tensor, seconds = call(net, inputs)
                            proposal = tensor.cpu().numpy().reshape(25, 2)
                            width = (5 if method == 'REFRESH5' else 15) if step < 25 else 25
                            kind = 'refresh' if step < 25 else 'common-suffix'
                            if step == 10:
                                assert np.array_equal(proposal, reference['fresh'])
                        width = min(width, (25 if step < 25 else 100)-step)
                        issued = scaler.scaler.inverse_transform(proposal)[:width]
                        used = 0
                        for command in issued:
                            state, actual, done = advance(task, env, command, condition, len(commands))
                            reached = a.success(task, state, goal)
                            assert done == reached
                            commands.append(command)
                            applied_commands.append(actual)
                            past.append(command)
                            states.append(state)
                            used += 1
                            if reached:
                                break
                        decisions.append(dict(start_step=step, kind=kind, planned_execution_steps=width,
                             executed_steps=used, previous_issued_commands=previous.tolist(),
                             standardized_proposal=proposal.tolist(), solver_seconds=seconds))
                    env.close()
                    path = out/f'trace_{j:03d}_{condition}_{method}.npz'
                    np.savez_compressed(path, states=np.asarray(states), commands=np.asarray(commands).reshape(-1,2),
                                        applied_commands=np.asarray(applied_commands).reshape(-1,2))
                    rows.append(dict(anchor=j, episode=entry['episode'], goal_span=entry['goal_span'], condition=condition,
                         method=method, success=reached, initial_success=reference['initial_success'],
                         absorbed_in_common_prefix=reference['reached'], env_steps=len(commands), decisions=decisions,
                         prefix_sha256=sha(out/f'prefix_{j:03d}_{condition}.npz'), trace_sha256=sha(path),
                         features_sha256=sha(out/f'features_{j:03d}_{condition}.json')))
                    save(out/'rows.json', rows)
                print('INTACT all-response fork', task, j, condition, 'COMPLETE', flush=True)
        assert len(rows) == 432 and initial_hash == a.state_hash(net.state_dict())
        prefix_steps = sum(g['prefix_env_steps'] for g in guards)
        save(out/'complete.json', dict(completed=True, n=432, model_unchanged=True,
             preparation_replay_env_steps=2*prefix_steps, features_saved_before_all_continuations=True))
    except Exception as error:
        save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        raise


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--task', choices=['tworoom', 'pusht'], required=True)
    run(p.parse_args().task)
