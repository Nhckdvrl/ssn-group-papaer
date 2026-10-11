"""E18: continuous, horizon-aligned adaptation; all labels are past observations."""
import argparse
import copy
import json
from pathlib import Path
import shutil

import h5py
import hdf5plugin  # register the native HDF5 codecs
import numpy as np
import torch
from first_wave import image_tensor, native_info, restore, sha256, simulator_state, sync_time, write_json
from recovery_forks import controls, solve, task_distance
from closed_loop import wilson

METHODS = ['FROZEN', 'DENSE25-PREDLAST', 'DENSE25-PREDLAST+PROJECTOR']
CONDITIONS = ['nominal', 'gain0.7', 'physics']
SEED = 78000


def reset(env, anchor, seed, task, condition):
    restore(env, anchor, seed)
    if condition == 'physics' and task == 'pusht':
        env.block.moment *= 2.


def chunk(env, task, commands, condition, stop=True):
    """Only the evaluator applies hidden shifts; learning sees issued commands."""
    images, success, reward_sum, steps = [env.render()], False, 0., 0
    for command in commands:
        applied = command * (.7 if condition == 'gain0.7' else 1.)
        if condition == 'physics' and task == 'tworoom':
            applied = applied + np.array([.15, 0.])
        _, reward, done, truncated, _ = env.step(applied)
        steps += 1
        reward_sum += float(reward)
        success = success or bool(done)
        if stop and (done or truncated):
            break
    images.append(env.render())
    return images, success, reward_sum, steps


def selected_modules(model, method):
    if method == 'FROZEN':
        return []
    stack = model.predictor.transition_stack
    modules = [('predictor.transition_stack.layers[-1]', stack.layers[-1]),
               ('predictor.transition_stack.norm', stack.norm),
               ('predictor.transition_stack.output_proj', stack.output_proj), ('pred_proj', model.pred_proj)]
    if method.endswith('+PROJECTOR'):
        modules.append(('projector', model.projector))
    return modules


def update(model, images, commands, norm, method):
    """Every valid <=25-step direct prefix, uniformly weighted over target pairs."""
    modules = selected_modules(model, method)
    parameters = list({id(p): p for _, m in modules for p in m.parameters()}.values())
    model.eval()  # BN buffers remain fixed; encoder readout can still receive gradients.
    begin = sync_time()
    for p in parameters:
        p.requires_grad_(True)
    with torch.enable_grad():
        optimizer = torch.optim.AdamW(parameters, lr=5e-5, weight_decay=1e-3)
        optimizer.zero_grad(set_to_none=True)
        z = model.encode({'pixels': image_tensor(images).unsqueeze(0).cuda()})['emb']
        n = len(images) - 1
        a = torch.as_tensor((np.asarray(commands)-norm['mean'])/norm['std'],
                            device='cuda', dtype=torch.float32).reshape(1, n, 10)
        losses = []
        for i in range(n):
            initial = z[:, i:i+1]
            act = model.action_encoder(a[:, i:], latent=initial, return_last_only=False)
            predicted = model.predict(initial, act)
            target = z[:, i+1:].detach()
            if predicted.shape != target.shape:
                raise ValueError(f'Dense prefix shape mismatch: {predicted.shape} != {target.shape}')
            losses.append((predicted-target).square().mean(-1).reshape(-1))
        loss = torch.cat(losses).mean()
        if not torch.isfinite(loss):
            raise ValueError('Nonfinite adaptation loss; retain this attempted episode')
        loss.backward()
        gradient_norm = float(torch.nn.utils.clip_grad_norm_(parameters, 1.))
        optimizer.step()
    for p in parameters:
        p.requires_grad_(False)
    return {'gradient_steps': 1, 'loss': float(loss.detach()), 'gradient_norm_before_clip': gradient_norm,
            'seconds': sync_time()-begin, 'window_primitive_steps': len(commands),
            'target_pairs': n*(n+1)//2, 'contains_true_25_step_target': n == 5}


def summarize(rows):
    result = []
    boot = np.random.default_rng(SEED+9000).integers(0, 16, (2000, 16))
    for task in ['tworoom', 'pusht']:
        for condition in CONDITIONS:
            group = [r for r in rows if r['task'] == task and r['condition'] == condition]
            base = {r['anchor']: r for r in group if r['method'] == 'FROZEN'}
            for method in METHODS:
                rr = sorted([r for r in group if r['method'] == method], key=lambda r: r['anchor'])
                delta = np.array([int(r['success'])-int(base[r['anchor']]['success']) for r in rr])
                utility = np.array([base[r['anchor']]['native_task_distance']-r['native_task_distance'] for r in rr])
                successes = sum(r['success'] for r in rr)
                result.append({'task': task, 'condition': condition, 'method': method, 'n': 16,
                    'successes': successes, 'success_wilson_ci95': wilson(successes, 16),
                    'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0)),
                    'paired_success_gain_vs_frozen': float(delta.mean()),
                    'paired_success_ci95': np.quantile(delta[boot].mean(1), [.025, .975]).tolist(),
                    'paired_distance_utility_gain': float(utility.mean()),
                    'paired_distance_ci95': np.quantile(utility[boot].mean(1), [.025, .975]).tolist(),
                    'absorbed_in_common_prefix': sum(r['absorbed_in_common_prefix'] for r in rr),
                    'executed_steps': sum(r['env_steps'] for r in rr),
                    'candidate_evaluations': sum(s['candidate_evaluations'] for r in rr for s in r['searches']),
                    'gradient_steps': sum(len(r['updates']) for r in rr)})
    return result


def run(args):
    import gymnasium as gym
    import stable_worldmodel
    torch.set_num_threads(4)
    torch.manual_seed(SEED)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]
    config = {'args': vars(args), 'sources': cfgs, 'methods': METHODS, 'conditions': CONDITIONS,
        'count_per_task_condition': 16, 'goal_offset': 25, 'seed': SEED, 'total_env_budget': 50,
        'common_prefix_steps': 5, 'replan_every': 5, 'horizon_primitive_steps': 25,
        'cem': {'N': 300, 'K': 30, 'iterations': 30, 'consistency_weight': 0},
        'optimizer': {'name': 'AdamW', 'lr': 5e-5, 'weight_decay': 1e-3, 'clip': 1., 'new_each_update': True},
        'loss': 'all valid source/target prefix pairs in latest <=25 real steps; target stop-gradient',
        'shift_onset_primitive_step': 0, 'physics': {'pusht': 'block moment x2; mass unchanged (validated transition effect)',
            'tworoom': 'issued command plus [0.15,0], then native clipping; no filter memory'},
        'hardware': torch.cuda.get_device_name(), 'harness_sha256': sha256(__file__),
        'helper_sha256': {name: sha256(Path(__file__).with_name(name)) for name in ['first_wave.py', 'recovery_forks.py']},
        'prepared_manifest': json.loads((Path(args.prepared)/'manifest.json').read_text()),
        'scope': 'one released model/task; equal env/search budgets, extra adaptation compute reported separately; no router',
        'control_scope': 'factual suffix only diagnostics; never adapter input; public setter lacks original PushT contact memory'}
    write_json(out/'config.json', config)
    for name in ['continuous_adaptation.py', 'first_wave.py', 'recovery_forks.py']:
        (out/name.replace('.py', '_used.py')).write_text(Path(__file__).with_name(name).read_text())
    rows, diagnostics, physical_steps, replay_max, pixel_max = [], [], 0, 0., 0.
    for source, cfg in zip(args.sources, cfgs):
        task = cfg['task']
        model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
        norm = np.load(Path(source)/'action_normalization.npz')
        data = np.load(Path(args.prepared)/f'{task}_g25.npz')
        env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
        if task == 'pusht' and not env.relative:
            raise ValueError('Action shifts require native relative controls')
        config.setdefault('adapted_modules', {})[task] = {m: {name: sum(p.numel() for p in module.parameters())
            for name, module in selected_modules(model, m)} for m in METHODS}
        write_json(out/'config.json', config)
        with h5py.File(cfg['dataset']) as f:
            offsets = f['ep_offset'][:]
            for j in range(16):
                anchor = {'state': data['state'][j], 'goal_state': data['goal_state'][j]}
                seed = SEED+j
                reset(env, anchor, seed, task, 'nominal')
                info = native_info(env.render(), data['goal_pixels'][j])
                with torch.no_grad():
                    initial = model.encode({'pixels': info['pixels'].cuda()})['emb']
                    goal = model.encode({'pixels': info['goal'].cuda()})['emb']
                    if j == 0:
                        write_json(out/f'{task}_native_control.json', controls(model, info, initial, goal))
                    plan, common_search = solve(model, initial, goal, env, 1, 300, SEED+j*100)
                common = plan[0, 0, 0].cpu().numpy().reshape(25, 2)*norm['std']+norm['mean']
                np.save(out/f'{task}_common_plan_{j:03d}.npy', common)
                ix = int(offsets[int(data['episode'][j])])+int(data['start'][j])
                factual = f['action'][ix:ix+25]  # exclusively isolated diagnostic control
                for condition in CONDITIONS:
                    reset(env, anchor, seed, task, condition)
                    _, success, _, steps = chunk(env, task, factual, condition, stop=False)
                    physical_steps += steps
                    diagnostics.append({'task': task, 'anchor': j, 'condition': condition,
                        'factual_suffix_success': success, 'env_steps': steps, 'native_task_distance': task_distance(env, task)})
                    write_json(out/'factual_controls.json', diagnostics)
                    reset(env, anchor, seed, task, condition)
                    images, absorbed, prefix_return, prefix_steps = chunk(env, task, common[:5], condition)
                    physical_steps += prefix_steps
                    state, pixels = simulator_state(env, env._get_info()), env.render()
                    for method in METHODS:
                        current = copy.deepcopy(model).eval().requires_grad_(False)
                        reset(env, anchor, seed, task, condition)
                        observed, success, reward_sum, steps = chunk(env, task, common[:5], condition)
                        physical_steps += steps
                        state_error = float(np.abs(simulator_state(env, env._get_info())-state).max())
                        pixel_error = float(np.abs(env.render().astype(float)-pixels).max())
                        replay_max, pixel_max = max(replay_max, state_error), max(pixel_max, pixel_error)
                        if state_error != 0 or pixel_error != 0 or success != absorbed or steps != prefix_steps:
                            raise ValueError('Common first-five replay mismatch')
                        history, commands, searches, updates = observed, list(common[:steps]), [], []
                        while not success and steps < 50:
                            if method != 'FROZEN':
                                record = update(current, history, commands, norm, method)
                                record['deployment_primitive_step'] = steps
                                updates.append(record)
                            with torch.no_grad():
                                begin = sync_time()
                                z = current.encode({'pixels': image_tensor([env.render()]).unsqueeze(0).cuda()})['emb']
                                g = current.encode({'pixels': image_tensor([data['goal_pixels'][j]]).unsqueeze(0).cuda()})['emb']
                                a, search = solve(current, z, g, env, 1, 300, SEED+j*100+steps//5)
                                search['seconds_with_current_and_goal_encoding'] = sync_time()-begin
                            searches.append(search)
                            issued = a[0, 0, 0].cpu().numpy().reshape(25, 2)*norm['std']+norm['mean']
                            obs, success, reward, taken = chunk(env, task, issued[:5], condition)
                            physical_steps += taken
                            steps += taken
                            reward_sum += reward
                            if not success:
                                history.append(obs[-1]); commands.extend(issued[:taken])
                                history, commands = history[-6:], commands[-25:]
                        rows.append({'task': task, 'condition': condition, 'method': method, 'anchor': j,
                            'source_episode': int(data['episode'][j]), 'source_start': int(data['start'][j]),
                            'success': success, 'env_steps': steps, 'native_return': reward_sum,
                            'native_task_distance': task_distance(env, task), 'absorbed_in_common_prefix': absorbed,
                            'common_prefix_steps': prefix_steps, 'common_search': common_search, 'searches': searches, 'updates': updates})
                        write_json(out/'rows.json', rows)
                        del current
                    print('continuous_adaptation', task, j, condition, flush=True)
        env.close(); del model; torch.cuda.empty_cache()
    write_json(out/'summary.json', summarize(rows))
    write_json(out/'complete.json', {'completed': True, 'episodes': len(rows), 'physical_env_steps': physical_steps,
        'common_prefix_state_max_abs': replay_max, 'common_prefix_pixel_max_abs': pixel_max})
    shutil.copytree(out, Path('/home/xiang/.cache/latent-wm-results')/out.name)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--sources', nargs=2, required=True); p.add_argument('--prepared', required=True); p.add_argument('--output', required=True)
    args = p.parse_args()
    try:
        run(args)
    except Exception as error:
        if Path(args.output).exists():
            write_json(Path(args.output)/'failure.json', {'error': type(error).__name__, 'message': str(error)})
        raise
