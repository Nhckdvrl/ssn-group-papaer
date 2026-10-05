"""E14 H0: observed outcomes of fixed feedback controllers, not oracle actions."""
import argparse
import shutil
from pathlib import Path
import numpy as np
import torch
import intact_published_control_v3 as a
import intact_recovery_forks_v2 as f
import intact_waypoint_recovery as w
from experience_transfer_control_audit import ROOT, read, save, sha

METHODS = ['OPEN25', 'GOAL5', 'REFERENCE5']
GOALS = [0]+list(range(2, 12))
BANK = ROOT/'20261004-E20-legal-effect-bank44'


def diagnostic(task, env):
    return np.asarray(env._get_obs(), dtype=np.float64) if task == 'tworoom' else a.p.diagnostic(env)


@torch.inference_mode()
def run(task):
    a.setup()
    out = ROOT/f'20261005-E14-controller-consequence-{task}'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__, out/'used.py')
    try:
        complete = read(BANK/'complete.json')
        assert complete['completed'] and complete['anchors'] == 88 and complete['branches'] == 1056
        entries = sorted([e for e in read(BANK/'ledger.json') if e['task'] == task], key=lambda e:e['anchor'])
        assert [e['anchor'] for e in entries] == list(range(44))
        original = {(r['anchor'], r['branch']):r for r in read(BANK/'rows.json') if r['task'] == task}
        data, controls = {}, []
        for entry in entries:
            j = entry['anchor']
            # Check every original branch, including excluded duplicate, once.
            for branch in range(12):
                path = BANK/f'{task}_{j:03d}_b{branch:02d}.npz'
                assert sha(path) == original[j, branch]['trace_sha256']
                with np.load(path) as raw:
                    if branch == 2:
                        factual = {k:raw[k].copy() for k in ['history', 'history_states', 'diagnostic_states', 'issued_actions']}
                    if branch in GOALS:
                        state = raw['diagnostic_states'][-1].copy()
                        data[j, branch] = dict(goal_image=raw['pixels'][-1].copy(), goal_state=state[:2 if task == 'tworoom' else 7])
            env, history = a.restore(task, entry)
            assert np.array_equal(history, factual['history'])
            assert np.array_equal(diagnostic(task, env), factual['history_states'][-1])
            replay = [diagnostic(task, env)]
            for command in factual['issued_actions']:
                env.step(command.astype(np.float32))
                replay.append(diagnostic(task, env))
            assert np.array_equal(np.asarray(replay), factual['diagnostic_states'])
            env.close()
            controls.append(dict(anchor=j, warm_pixels_exact=True, complete_diagnostic_exact=True, factual25_replay_exact=True))
            data[j, 'warm'] = factual['history']
            data[j, 'state'] = factual['history_states'][-1]
        net, scaler, source = a.source(task, 'cuda')
        before = a.state_hash(net.state_dict())
        cpu_net, cpu_scaler, cpu_source = a.source(task, 'cpu')
        assert source == cpu_source
        entry = entries[0]
        tests = []
        for device, model, processor in [('cpu', cpu_net, cpu_scaler), ('cuda', net, scaler)]:
            inputs = a.info(data[0, 'warm'][-1], data[0, 2]['goal_image'], entry['warm_actions'], processor, device)
            full = model.get_action(inputs, horizon=5)
            short = model.get_action(inputs, horizon=1)
            assert torch.equal(short[:, 0], full[:, 0])
            reference = w.reference(model, inputs, full)
            target = model.encode(dict(pixels=inputs['goal']))['emb'][:, -1]
            previous = model.action_encoder(inputs['action'])[:, -1]
            global_stats = w.query(model, reference[:, 0], target, previous)
            local_stats = w.query(model, reference[:, 0], reference[:, 1], previous)
            assert torch.equal(global_stats['map_mean'], full[:, 0])
            values = torch.cat([global_stats['map_mean'], global_stats['log_std'], local_stats['map_mean'], local_stats['log_std']], -1).cpu().numpy()
            if device == 'cpu':
                cpu_values = values
            else:
                np.testing.assert_allclose(values, cpu_values, atol=2e-4, rtol=1e-5)
            tests.append(dict(device=device, passed=True, short_full_exact=True, typed_global_local_mean_std_exact=True))
        del cpu_net
        save(out/'preflight.json', dict(passed=True, n=44, controls=controls, cpu_cuda=tests, source=source))
        save(out/'config.json', dict(task=task, model_seed=0, source=source, methods=METHODS, goals=GOALS, anchors=44,
            budget=25, source_ledger_sha256=sha(BANK/'ledger.json'), source_rows_sha256=sha(BANK/'rows.json'),
            source_bank=str(BANK), script_sha256=sha(__file__), actor_helper_sha256=sha(a.__file__),
            fork_helper_sha256=sha(f.__file__), waypoint_helper_sha256=sha(w.__file__), hardware=torch.cuda.get_device_name(),
            supervision='Observed pixels and issued commands; native physical states evaluator/restore only. Imagined references supplied by frozen model. Given subgoal images from recorded experience; no true future trajectory or shifted physics in controller input.',
            scope='Development44 anchors/11 nonduplicate branch goals, one published model source, fixed25-step controllers. Feedback changes executed actions: controller-induced outcome data, not primitive-action causal comparison or new skill method. Train/held anchors must be separated before outcome-model learning; pretraining overlap unknown.'))
        rows = []
        for entry in entries:
            j = entry['anchor']
            for branch in GOALS:
                target = data[j, branch]
                goal = target['goal_state']
                first_plan, first_commands, first_states, first_pixels = None, None, None, None
                for method in METHODS:
                    env, history = a.restore(task, entry)
                    assert np.array_equal(history, data[j, 'warm']) and np.array_equal(diagnostic(task, env), data[j, 'state'])
                    # The subgoal is given task information, set after the shared warm-up.
                    physical_before = a.diagnostic(task, env)
                    env._set_goal_state(goal)
                    assert np.array_equal(a.diagnostic(task, env), physical_before)
                    image, state = env.render().copy(), diagnostic(task, env)
                    if first_states is None:
                        first_states, first_pixels = state.copy(), image.copy()
                    assert np.array_equal(state, first_states) and np.array_equal(image, first_pixels)
                    reached = a.success(task, a.diagnostic(task, env), goal)
                    initial_success = reached
                    states, commands = [state], []
                    observed, observation_steps = [image], [0]
                    past = list(entry['warm_actions'])
                    decisions, queries = [], []
                    reference = None
                    while not reached and len(commands) < 25:
                        step = len(commands)
                        previous_raw = np.asarray(past[-5:], dtype=np.float32)
                        if method == 'REFERENCE5' and step:
                            current = net.encode(dict(pixels=a.pixels(env.render()[None, None], 'cuda')))['emb'][:, -1]
                            previous = net.action_encoder(torch.as_tensor(scaler.transform(previous_raw.reshape(1, 1, 10)), device='cuda').float())[:, -1]
                            desired = reference[:, step//5+1]
                            stats = w.query(net, current, desired, previous)
                            proposal = stats['map_mean'].cpu().numpy().reshape(5, 2)
                            queries.append(dict(step=step, current=current.cpu().numpy(), target=desired.cpu().numpy(), previous=previous.cpu().numpy(), mean=stats['map_mean'].cpu().numpy(), log_std=stats['log_std'].cpu().numpy()))
                            kind, width = 'local-reference', 5
                        else:
                            inputs = a.info(env.render().copy(), target['goal_image'], past, scaler, 'cuda')
                            plan = net.get_action(inputs, horizon=1 if method == 'GOAL5' else 5)
                            proposal = plan.cpu().numpy().reshape(-1, 2)
                            if step == 0:
                                if first_plan is None:
                                    first_plan = proposal.copy()
                                assert np.array_equal(proposal[:5], first_plan[:5])
                                if method != 'GOAL5':
                                    assert np.array_equal(proposal, first_plan)
                            if method == 'REFERENCE5':
                                reference = w.reference(net, inputs, plan)
                            kind, width = 'goal', 25 if method == 'OPEN25' else 5
                        issued = scaler.scaler.inverse_transform(proposal)[:width]
                        used = 0
                        for command in issued:
                            _, _, done, truncated, _ = env.step(command.astype(np.float32))
                            state = diagnostic(task, env)
                            reached = a.success(task, a.diagnostic(task, env), goal)
                            assert bool(done) == reached and not truncated
                            commands.append(command)
                            states.append(state)
                            past.append(command)
                            used += 1
                            if len(commands) % 5 == 0 or reached:
                                observed.append(env.render().copy())
                                observation_steps.append(len(commands))
                            if reached:
                                break
                        decisions.append(dict(step=step, kind=kind, previous_issued_commands=previous_raw.tolist(), standardized_proposal=proposal.tolist(), executed_steps=used))
                    env.close()
                    # Every policy shares its initial real five steps, up to absorption.
                    if first_commands is None:
                        first_commands = np.asarray(commands).reshape(-1, 2)[:5].copy()
                    assert np.array_equal(np.asarray(commands).reshape(-1, 2)[:5], first_commands)
                    stem = f'{j:03d}_g{branch:02d}_{method}'
                    path, qpath = out/f'trace_{stem}.npz', out/f'queries_{stem}.npz'
                    np.savez_compressed(path, states=np.asarray(states), commands=np.asarray(commands).reshape(-1, 2), observations=np.asarray(observed), observation_steps=np.asarray(observation_steps),
                        goal_image=target['goal_image'], goal_state=goal, warm_history=history,
                        reference=reference.cpu().numpy() if reference is not None else np.asarray([]))
                    np.savez_compressed(qpath, **({key:np.asarray([q[key] for q in queries]) for key in queries[0]} if queries else dict(step=np.asarray([], dtype=np.int64))))
                    rows.append(dict(anchor=j, episode=entry['episode'], goal_branch=branch, method=method, initial_success=initial_success,
                        success=reached, env_steps=len(commands), decisions=decisions, trace_sha256=sha(path), queries_sha256=sha(qpath)))
                    save(out/'rows.json', rows)
            print('Controller outcome anchor', task, j, '33 COMPLETE', flush=True)
        assert len(rows) == 1452 and before == a.state_hash(net.state_dict())
        save(out/'complete.json', dict(completed=True, n=1452, model_unchanged=True))
    except Exception as error:
        save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', choices=['tworoom', 'pusht'], required=True)
    run(parser.parse_args().task)
