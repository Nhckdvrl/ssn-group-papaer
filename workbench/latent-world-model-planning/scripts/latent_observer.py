"""Fixed-gain latent observer audit: frozen Fast, identical EX5-SHIFT-WARM search."""
import argparse, copy, importlib.metadata, json, shutil
from pathlib import Path
import numpy as np
import torch
from first_wave import native_info, sha256, simulator_state, sync_time, write_json
from recovery_forks import controls, task_distance, MacroCost
from query_proposal import encode, plan
from commitment_cadence import shift_prior
from continuous_adaptation import reset, CONDITIONS, SEED
from closed_loop import wilson

METHODS = ['OBS', 'PRIOR', 'FILTER0.5', 'OBS-PREFIX5']
class PrefixCost(MacroCost):
    def terminal(self, actions):
        b, s, h, d = actions.shape
        if (h, d) != (1, 50): raise ValueError('Keep native 25-step/50-dimensional search')
        z = self.initial[:, None].expand(b, s, 1, 192).reshape(b*s, 1, 192)
        act = self.model.action_encoder(actions.reshape(b*s, 5, 10)[:, :1], latent=z, return_last_only=True)
        return self.model.predict(z, act)[:, -1].reshape(b, s, 192)

def plan_prefix(model, initial, goal, env, n, seed, proposal):
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    cost = PrefixCost(model, initial, goal)
    solver = swm.solver.CEMSolver(cost, batch_size=1, num_samples=n, topk=30, n_steps=30, device='cuda', seed=seed)
    solver.configure(action_space=batch_space(env.action_space, 1), n_envs=1, config=swm.PlanConfig(horizon=1, receding_horizon=1, action_block=25, warm_start=True))
    tick = sync_time(); result = solver.solve({}, init_action=proposal)
    return result['actions'].numpy(), {'seconds': sync_time()-tick, 'cost_calls': cost.calls, 'candidate_evaluations': n*cost.calls, 'predicted_prefix5_transitions': n*cost.calls}

def execute(env, task, issued, condition):
    # Evaluator alone applies the hidden shift; observer receives original issued commands.
    before = env.render().copy(); reward_sum = 0.; success = truncated = False
    for used, command in enumerate(issued, 1):
        applied = command*(.7 if condition == 'gain0.7' else 1.)
        if condition == 'physics' and task == 'tworoom': applied = applied+np.array([.15, 0.])
        _, reward, success, truncated, _ = env.step(applied); reward_sum += float(reward)
        if success or truncated: break
    return [before, env.render().copy()], bool(success), reward_sum, used, bool(truncated)

def predict5(model, state, issued, norm):
    if np.shape(issued) != (5, 2): raise ValueError('Prediction requires five actually issued commands')
    a = torch.as_tensor((issued-norm['mean'])/norm['std'], device=state.device, dtype=state.dtype).reshape(1, 1, 10)
    act = model.action_encoder(a, latent=state, return_last_only=True)
    result = model.predict(state, act)[:, -1:]
    if result.shape != state.shape or not torch.isfinite(result).all(): raise ValueError('Invalid five-step prediction')
    return result

def prefix_control(model, state, norm):
    a = torch.linspace(-.7, .7, 50, device=state.device, dtype=state.dtype).reshape(1, 5, 10)
    act = model.action_encoder(a, latent=state, return_last_only=False)
    direct = model.predict(state, act)[:, :1]
    issued = a[:, :1].cpu().numpy().reshape(5, 2)*norm['std']+norm['mean']
    five = predict5(model, state, issued, norm)
    error = float((five-direct).abs().max())
    if not torch.allclose(five, direct, atol=1e-5, rtol=1e-5): raise ValueError('Causal first-five prefix mismatch')
    candidates = a.reshape(1, 1, 1, 50).expand(1, 3, 1, 50).clone(); candidates[:, 1:, :, 10:] += .8
    costs = PrefixCost(model, state, state).get_cost({}, candidates); expected = (direct-state).square().sum(-1).expand(1, 3)
    if not torch.allclose(costs, expected, atol=1e-5, rtol=1e-5): raise ValueError('Vectorized prefix5 cost/tail invariance mismatch')
    return {'max_abs_error': error, 'prefix_cost_max_abs_error': float((costs-expected).abs().max()), 'primitive_steps': 5, 'unused_tail_invariant': True}

def summarize(rows):
    result = []; boot = np.random.default_rng(SEED+9000).integers(0, 16, (2000, 16))
    for task in ['tworoom', 'pusht']:
        for condition in CONDITIONS:
            group = [r for r in rows if r['task'] == task and r['condition'] == condition]
            base = {r['anchor']: r for r in group if r['method'] == 'OBS'}
            strong = {r['anchor']: r for r in group if r['method'] == 'OBS-PREFIX5'}
            for method in METHODS:
                rr = sorted([r for r in group if r['method'] == method], key=lambda r: r['anchor'])
                if len(rr) != 16: raise ValueError('Incomplete summary cell')
                delta = np.array([int(r['success'])-int(base[r['anchor']]['success']) for r in rr])
                utility = np.array([base[r['anchor']]['native_task_distance']-r['native_task_distance'] for r in rr])
                ds = np.array([int(r['success'])-int(strong[r['anchor']]['success']) for r in rr])
                s = sum(r['success'] for r in rr)
                result.append({'task': task, 'condition': condition, 'method': method, 'n': 16, 'successes': s,
                    'success_wilson_ci95': wilson(s, 16), 'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0)),
                    'paired_success_gain_vs_OBS': float(delta.mean()), 'paired_success_ci95': np.quantile(delta[boot].mean(1), [.025, .975]),
                    'paired_distance_utility_vs_OBS': float(utility.mean()), 'paired_distance_ci95': np.quantile(utility[boot].mean(1), [.025, .975]),
                    'paired_success_gain_vs_OBS_PREFIX5': float(ds.mean()), 'paired_success_vs_PREFIX5_ci95': np.quantile(ds[boot].mean(1), [.025, .975]),
                    'absorbed_in_common_prefix': sum(r['absorbed_in_common_prefix'] for r in rr),
                    'env_steps': sum(r['env_steps'] for r in rr), 'candidate_evaluations': sum(s['candidate_evaluations'] for r in rr for s in r['searches']),
                    'diagnostic_prior_calls': sum(r['diagnostic_prior_calls'] for r in rr), 'gradient_steps': 0})
    return result
@torch.inference_mode()
def run(args):
    import gymnasium as gym
    import stable_worldmodel
    if importlib.metadata.version('stable-worldmodel') != '0.0.6': raise ValueError('Requires native CEM0.0.6')
    torch.set_num_threads(4); torch.manual_seed(SEED)
    out = Path(args.output); durable = Path('/home/xiang/.cache/latent-wm-results')/out.name
    if durable.exists(): raise FileExistsError(durable)
    out.mkdir(parents=True, exist_ok=False)
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]
    if sorted(c['task'] for c in cfgs) != ['pusht', 'tworoom']: raise ValueError('Requires both Fast sources')
    helpers = ['first_wave.py', 'recovery_forks.py', 'query_proposal.py', 'commitment_cadence.py', 'continuous_adaptation.py', 'closed_loop.py']
    write_json(out/'config.json', {'args': vars(args), 'sources': cfgs, 'seed': SEED, 'methods': METHODS, 'conditions': CONDITIONS,
        'count_per_cell': 16, 'goal_offset': 25, 'budget': 50, 'common_prefix_steps': 5, 'horizon': 25, 'N': 300, 'K': 30, 'iterations': 30,
        'wm_updates': 0, 'feedback_period': 5, 'filter_alpha': .5, 'warm_start': 'shift actual prefix; normalized-zero tail; std1',
        'shift_onset': 0, 'physics': {'pusht': 'block moment x2, unchanged mass', 'tworoom': 'issued+[.15,0], native clipping'},
        'prior_input': 'own previous selected state and actual issued five commands; no applied/hidden commands or future labels',
        'goal': 'fixed real goal encoding; query-only', 'scope': 'fixed-gain zero-training audit; no Kalman or velocity claim',
        'OBS_control': 'same A5 g25 EXEC5-SHIFT-WARM first plan/seeds/goal/normalization; extra prior diagnostic compute',
        'OBS_PREFIX5': 'same 50dim CEM/raw elite mean/warm prior; only first5 target scored, remaining20 not scored; classic time-alignment control',
        'action_scoring': 'unchanged A5 native scoring: unbounded issued candidates; env clips applied commands; known limitation shared by all methods',
        'accounting': 'shared first solve charged logically per row; physical totals include common replay per cell; encodes/propagation extra; positive-control compute excluded and saved separately',
        'replay_scope': 'public state/pixel equality; not original hidden contact-state recovery', 'hardware': torch.cuda.get_device_name(),
        'harness_sha256': sha256(__file__), 'helper_sha256': {n: sha256(Path(__file__).with_name(n)) for n in helpers},
        'prepared_manifest': json.loads((Path(args.prepared)/'manifest.json').read_text())})
    for name in ['latent_observer.py']+helpers: shutil.copy2(Path(__file__).with_name(name), out/name.replace('.py', '_used.py'))
    rows = []; physical = solves = encodes = propagations = 0; replay_max = pixel_max = 0.
    for source, cfg in zip(args.sources, cfgs):
        task = cfg['task']; model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
        norm = dict(np.load(Path(source)/'action_normalization.npz')); data = np.load(Path(args.prepared)/f'{task}_g25.npz')
        env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
        if task == 'pusht' and not env.relative: raise ValueError('Requires relative controls')
        write_json(out/f'{task}_inputs.json', {'checkpoint_sha256': sha256(cfg['checkpoint']), 'normalization': norm,
            'anchors_sha256': sha256(Path(args.prepared)/f'{task}_g25.npz')})
        for j in range(16):
            anchor = {k: data[k][j] for k in ['state', 'goal_state', 'goal_pixels', 'episode', 'start']}; seed = SEED+j
            reset(env, anchor, seed, task, 'nominal'); image = env.render().copy(); tick = sync_time()
            initial = encode(model, image[None]).cuda().unsqueeze(1); goal = encode(model, anchor['goal_pixels'][None]).cuda().unsqueeze(1)
            initial_seconds = sync_time()-tick; encodes += 2
            if j == 0: write_json(out/f'{task}_native_controls.json', {'cost': controls(model, native_info(image, anchor['goal_pixels']), initial, goal), 'prefix5': prefix_control(model, initial, norm)})
            common, shared = plan(model, initial, goal, env, 300, SEED+j*100); solves += 1; common = common.reshape(25, 2)
            np.save(out/f'{task}_common_normalized_plan_{j:03d}.npy', common)
            for condition in CONDITIONS:
                reset(env, anchor, seed, task, condition); _, absorbed, _, prefix_steps, prefix_truncated = execute(env, task, common[:5]*norm['std']+norm['mean'], condition)
                physical += prefix_steps; reference = simulator_state(env, env._get_info()); pixels = env.render().copy()
                for method in METHODS:
                    current = copy.deepcopy(model).eval().requires_grad_(False); reset(env, anchor, seed, task, condition)
                    selected = initial.clone(); action = common.copy(); steps = 0; success = truncated = False; reward_sum = 0.; begin = sync_time()
                    frames = [env.render().copy()]; selected_states = [selected.cpu().numpy()]; obs_states = [initial.cpu().numpy()]
                    prior_states = [initial.cpu().numpy()]; issued_all = []; plans = [action.copy()]; priors = [np.zeros((1, 1, 50))]; boundary_steps = [0]
                    searches = [dict(shared, shared_initial=True, encoding_calls=2, encoding_seconds=initial_seconds, seed=SEED+j*100)]; residuals = []; costs = []
                    while not success and not truncated and steps < 50:
                        issued = action[:min(5, 50-steps)]*norm['std']+norm['mean']; obs, success, reward, used, truncated = execute(env, task, issued, condition)
                        steps += used; physical += used; reward_sum += reward; issued_all.extend(issued[:used]); frames.append(obs[-1]); boundary_steps.append(steps)
                        if len(boundary_steps) == 2:
                            se = float(np.abs(simulator_state(env, env._get_info())-reference).max()); pe = float(np.abs(obs[-1].astype(float)-pixels).max())
                            replay_max, pixel_max = max(replay_max, se), max(pixel_max, pe)
                            if se or pe or success != absorbed or truncated != prefix_truncated or used != prefix_steps: raise ValueError('Common first-five replay mismatch')
                        tick = sync_time(); observed = encode(current, obs[-1][None]).cuda().unsqueeze(1); encoding_seconds = sync_time()-tick; encodes += 1
                        tick = sync_time(); prior = predict5(current, selected, issued[:used], norm) if used == 5 else None
                        propagation_seconds = sync_time()-tick; propagations += int(prior is not None)
                        residuals.append(None if prior is None else float((observed-prior).square().mean()))
                        prior_states.append(np.full_like(initial.cpu().numpy(), np.nan) if prior is None else prior.cpu().numpy())
                        selected = observed if method in ['OBS', 'OBS-PREFIX5'] or prior is None else prior if method == 'PRIOR' else prior+.5*(observed-prior)
                        selected_states.append(selected.cpu().numpy()); obs_states.append(observed.cpu().numpy())
                        costs.append({'step': steps, 'encoding_seconds': encoding_seconds, 'propagation_seconds': propagation_seconds, 'prior_calls': int(prior is not None)})
                        if success or truncated or steps == 50: break
                        warm = shift_prior(action, used); tick = sync_time()
                        planner = plan_prefix if method == 'OBS-PREFIX5' else plan
                        planned, search = planner(current, selected, goal, env, 300, SEED+j*100+steps//5, torch.as_tensor(warm, device='cuda', dtype=torch.float32))
                        solves += 1; searches.append(dict(search, seed=SEED+j*100+steps//5, encoding_calls=1, native_init_shape=list(warm.shape)))
                        action = planned.reshape(25, 2).copy(); plans.append(action.copy()); priors.append(warm)
                    filename = f'{task}_{condition}_{j:03d}_{method}_raw.npz'
                    np.savez_compressed(out/filename, frames=np.stack(frames), boundary_steps=boundary_steps, issued_commands=np.asarray(issued_all),
                        selected_latents=np.concatenate(selected_states), observed_latents=np.concatenate(obs_states), prior_latents=np.concatenate(prior_states),
                        normalized_plans=np.stack(plans), normalized_warm_priors=np.stack(priors), goal_latent=goal.cpu().numpy())
                    rows.append({'task': task, 'condition': condition, 'method': method, 'anchor': j, 'source_episode': int(anchor['episode']), 'source_start': int(anchor['start']),
                        'success': success, 'truncated': truncated, 'env_steps': steps, 'native_return': reward_sum, 'native_task_distance': task_distance(env, task),
                        'absorbed_in_common_prefix': absorbed, 'common_prefix_steps': prefix_steps, 'searches': searches, 'diagnostic_prior_calls': sum(c['prior_calls'] for c in costs),
                        'prediction_observation_mse': residuals, 'observer_costs': costs, 'episode_seconds_excluding_shared_first_solve': sync_time()-begin, 'raw_file': filename})
                    write_json(out/'rows.json', rows); del current
                print('latent_observer', task, j, condition, flush=True)
        env.close(); del model; torch.cuda.empty_cache()
    write_json(out/'summary.json', summarize(rows)); write_json(out/'complete.json', {'completed': True, 'episodes': len(rows), 'physical_env_steps': physical,
        'common_prefix_state_max_abs': replay_max, 'common_prefix_pixel_max_abs': pixel_max, 'actual_solver_calls': solves,
        'actual_encoding_calls': encodes, 'actual_prior_calls': propagations, 'actual_candidate_evaluations': solves*300*30})
    shutil.copytree(out, durable)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--sources', nargs=2, required=True)
    for name in ['prepared', 'output']: p.add_argument('--'+name, required=True)
    args = p.parse_args()
    try: run(args)
    except Exception as error:
        if Path(args.output).exists(): write_json(Path(args.output)/'failure.json', {'type': type(error).__name__, 'message': str(error)})
        raise
