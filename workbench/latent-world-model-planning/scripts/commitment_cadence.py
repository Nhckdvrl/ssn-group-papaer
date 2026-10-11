"""Matched nominal Fast planning: shared first plan, execution cadence and shifted prior."""
import argparse
import copy
import importlib.metadata
import inspect
import json
from pathlib import Path
import shutil
import numpy as np
import torch
from first_wave import native_info, restore, sha256, simulator_state, sync_time, write_json
from recovery_forks import controls, task_distance
from query_proposal import encode, plan
from closed_loop import wilson

SEED = 78000
METHODS = [('EXEC5-COLD', 5), ('EXEC10-COLD', 10), ('EXEC25-COLD', 25), ('EXEC5-SHIFT-WARM', 5)]


def shift_prior(previous, used):
    previous = np.asarray(previous).reshape(25, 2)
    if not 0 < used <= 25:
        raise ValueError('Shift must equal the actual executed prefix')
    return np.concatenate([previous[used:], np.zeros((used, 2), dtype=previous.dtype)]).reshape(1, 1, 50)


def summarize(rows):
    result = []; boot = np.random.default_rng(SEED+9000).integers(0, 16, (2000, 16))
    for task in ['tworoom', 'pusht']:
        for horizon in [25, 75]:
            group = [r for r in rows if r['task'] == task and r['goal_offset'] == horizon]
            base = {r['anchor']: r for r in group if r['method'] == 'EXEC25-COLD'}
            for method, _ in METHODS:
                rr = sorted([r for r in group if r['method'] == method], key=lambda r: r['anchor'])
                delta = np.array([int(r['success'])-int(base[r['anchor']]['success']) for r in rr])
                utility = np.array([base[r['anchor']]['native_task_distance']-r['native_task_distance'] for r in rr])
                successes = sum(r['success'] for r in rr)
                result.append({'task': task, 'goal_offset': horizon, 'method': method, 'n': 16,
                    'successes': successes, 'success_wilson95': wilson(successes, 16),
                    'paired_success_gain_vs_EXEC25': float(delta.mean()),
                    'paired_success_ci95': np.quantile(delta[boot].mean(1), [.025, .975]),
                    'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0)),
                    'paired_distance_utility_vs_EXEC25': float(utility.mean()),
                    'paired_distance_ci95': np.quantile(utility[boot].mean(1), [.025, .975]),
                    'env_steps': sum(r['env_steps'] for r in rr),
                    'logical_search_calls': sum(len(r['searches']) for r in rr),
                    'candidate_evaluations': sum(s['candidate_evaluations'] for r in rr for s in r['searches'])})
    return result


@torch.inference_mode()
def run(args):
    import gymnasium as gym
    import stable_worldmodel as swm
    if importlib.metadata.version('stable-worldmodel') != '0.0.6':
        raise ValueError('Requires native CEM0.0.6')
    torch.set_num_threads(4); torch.manual_seed(SEED)
    out = Path(args.output); out.mkdir(parents=True, exist_ok=False)
    durable = Path('/home/xiang/.cache/latent-wm-results')/out.name
    if durable.exists(): raise FileExistsError(durable)
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]
    if sorted(c['task'] for c in cfgs) != ['pusht', 'tworoom']: raise ValueError('Requires both Fast task sources')
    helpers = ['first_wave.py', 'recovery_forks.py', 'query_proposal.py', 'closed_loop.py']
    write_json(out/'config.json', {'args': vars(args), 'sources': cfgs, 'seed': SEED,
        'methods': METHODS, 'count_per_task_range': 16, 'goal_offsets': [25, 75], 'budgets': [50, 150],
        'nominal': True, 'horizon': 25, 'N': 300, 'K': 30, 'iterations': 30,
        'initial_plan_seed': '78000+j*100', 'subsequent_seed': '78000+j*100+steps//5',
        'warm_padding': 'normalized zero, physical source mean; native init_action [1,1,50]',
        'normalization': 'unchanged source full-data action stats', 'wm_updates': 0,
        'accounting': 'shared initial solve/2 encodes charged logically to each method; actual totals in complete.json',
        'replay_scope': 'public reset/setters or factual_prefix restore; state/pixel equality does not establish original hidden contact memory',
        'harness_sha256': sha256(__file__), 'cem_source_sha256': sha256(inspect.getfile(swm.solver.CEMSolver)),
        'helper_sha256': {n: sha256(Path(__file__).with_name(n)) for n in helpers},
        'prepared_manifest': json.loads((Path(args.prepared)/'manifest.json').read_text()),
        'hardware': torch.cuda.get_device_name(), 'scope': 'matched cadence/search restart; no attribution to hidden velocity'})
    for name in ['commitment_cadence.py']+helpers:
        shutil.copy2(Path(__file__).with_name(name), out/name.replace('.py', '_used.py'))
    rows = []; physical = 0; actual_solves = 0
    for source, cfg in zip(args.sources, cfgs):
        task = cfg['task']; model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
        norm = dict(np.load(Path(source)/'action_normalization.npz'))
        env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
        write_json(out/f'{task}_inputs.json', {'wm_sha256': sha256(cfg['checkpoint']), 'normalization': norm,
            'anchors_sha256': {h: sha256(Path(args.prepared)/f'{task}_g{h}.npz') for h in [25, 75]}})
        for horizon in [25, 75]:
            anchors = np.load(Path(args.prepared)/f'{task}_g{horizon}.npz')
            for j in range(16):
                anchor = {k: anchors[k][j] for k in anchors.files}; reset_seed = SEED+j
                restore(env, anchor, reset_seed); image = env.render().copy(); state = simulator_state(env, env._get_info())
                begin = sync_time(); initial = encode(model, image[None]).cuda().unsqueeze(1)
                goal = encode(model, anchor['goal_pixels'][None]).cuda().unsqueeze(1); initial_encoding = sync_time()-begin
                if j == 0 and horizon == 25:
                    write_json(out/f'{task}_native_control.json', controls(model, native_info(image, anchor['goal_pixels']), initial, goal))
                common, common_search = plan(model, initial, goal, env, 300, SEED+j*100); actual_solves += 1
                common = common.reshape(25, 2).copy(); stem = f'{task}_g{horizon}_{j:03d}'
                np.savez_compressed(out/f'{stem}_initial.npz', **anchor, restored_state=state, restored_pixels=image, common_normalized_plan=common)
                for method, commitment in METHODS:
                    restore(env, anchor, reset_seed); replay_state = simulator_state(env, env._get_info()); replay_image = env.render()
                    state_error = float(np.max(np.abs(replay_state-state)))
                    pixel_error = int(np.max(np.abs(replay_image.astype(np.int16)-image.astype(np.int16))))
                    if state_error > 1e-6 or pixel_error: raise ValueError(f'Initial replay mismatch {stem} {method}')
                    action = common.copy(); assert np.array_equal(action, common)
                    steps = 0; searches = [dict(copy.deepcopy(common_search), shared_initial=True,
                        seed=SEED+j*100, current_encoding_seconds=initial_encoding, encoding_calls=2)]
                    plans = [action.copy()]; priors = [np.zeros((1, 1, 50), dtype=action.dtype)]; used_chunks = []
                    success = False; terminated = False; truncated = False; first_success = None; begin_episode = sync_time()
                    while steps < 2*horizon:
                        used = 0; issued = min(commitment, 2*horizon-steps)
                        for command in action[:issued]*norm['std']+norm['mean']:
                            _, _, terminated, truncated, _ = env.step(command); steps += 1; used += 1; physical += 1
                            if terminated: success = True; first_success = steps
                            if terminated or truncated: break
                        used_chunks.append(used)
                        if terminated or truncated or steps == 2*horizon: break
                        prior = shift_prior(action, used) if method == 'EXEC5-SHIFT-WARM' else None
                        tick = sync_time(); initial = encode(model, env.render()[None]).cuda().unsqueeze(1); encoding_seconds = sync_time()-tick
                        seed = SEED+j*100+steps//5
                        init = None if prior is None else torch.as_tensor(prior, device='cuda', dtype=torch.float32)
                        planned, search = plan(model, initial, goal, env, 300, seed, init); actual_solves += 1
                        action = planned.reshape(25, 2).copy(); plans.append(action.copy())
                        priors.append(np.zeros((1, 1, 50), dtype=action.dtype) if prior is None else prior)
                        searches.append(dict(search, shared_initial=False, seed=seed, current_encoding_seconds=encoding_seconds,
                                             encoding_calls=1, native_init_shape=None if prior is None else list(prior.shape)))
                    plan_file = f'{stem}_{method}_plans.npz'
                    np.savez_compressed(out/plan_file, normalized_plans=np.stack(plans), normalized_priors=np.stack(priors),
                                        executed_prefix_lengths=used_chunks, initial_state=replay_state, initial_pixels=replay_image,
                                        issued_commands=np.concatenate([p[:u] for p, u in zip(plans, used_chunks)])*norm['std']+norm['mean'],
                                        final_state=simulator_state(env, env._get_info()))
                    rows.append({'task': task, 'goal_offset': horizon, 'anchor': j, 'episode': int(anchor['episode']),
                        'method': method, 'success': success, 'first_success_step': first_success, 'env_steps': steps,
                        'terminated': bool(terminated), 'truncated': bool(truncated), 'native_task_distance': task_distance(env, task),
                        'initial_state_replay_error': state_error, 'initial_pixel_replay_error': pixel_error,
                        'episode_seconds_excluding_shared_first_solve': sync_time()-begin_episode, 'searches': searches, 'plan_file': plan_file})
                    write_json(out/'rows.json', rows)
                print('commitment_cadence', task, horizon, j, flush=True)
        env.close(); del model; torch.cuda.empty_cache()
    write_json(out/'summary.json', summarize(rows))
    write_json(out/'complete.json', {'completed': True, 'episodes': len(rows), 'physical_env_steps': physical,
                                    'actual_solver_calls': actual_solves, 'shared_initial_solves': 64,
                                    'actual_encoding_calls': 128+actual_solves-64, 'actual_cost_calls': actual_solves*30,
                                    'actual_candidate_evaluations': actual_solves*300*30})
    shutil.copytree(out, durable)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--sources', nargs='+', required=True)
    for name in ['prepared', 'output']: p.add_argument('--'+name, required=True)
    args = p.parse_args()
    try: run(args)
    except Exception as error:
        if Path(args.output).exists(): write_json(Path(args.output)/'failure.json', {'type': type(error).__name__, 'message': str(error)})
        raise
