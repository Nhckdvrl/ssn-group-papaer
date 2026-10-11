"""E13: classic action-trajectory parameterization with unchanged frozen Fast cost."""
import argparse
import importlib.metadata
import inspect
import json
from pathlib import Path
import shutil
import numpy as np
import torch
import torch.nn.functional as F
from first_wave import native_info, restore, sha256, sync_time, write_json
from recovery_forks import MacroCost, controls, task_distance
from closed_loop import wilson

METHODS = {'ZERO25-N300': (25, 300), 'ZERO25-N900': (25, 900),
           'LINEAR5-N300': (5, 300), 'CONSTANT1-N300': (1, 300)}
SEED = 68000


def expand_actions(parameters, knots):
    b, s, h, d = parameters.shape
    if h != 1 or d != 2*knots: raise ValueError('Expected [B,S,1,2*knots] coefficients')
    if knots == 25: return parameters
    x = parameters.reshape(b*s, knots, 2).transpose(1, 2)
    x = x.expand(-1, -1, 25) if knots == 1 else F.interpolate(x, size=25, mode='linear', align_corners=True)
    return x.transpose(1, 2).reshape(b, s, 1, 50)


class BasisCost:
    def __init__(self, native, knots): self.native, self.knots = native, knots
    def get_cost(self, info, parameters): return self.native.get_cost(info, expand_actions(parameters, self.knots))


def solver(cost, action_space, knots, candidates, seed, device):
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    cem = swm.solver.CEMSolver(cost, batch_size=1, num_samples=candidates, topk=30, n_steps=30, device=device, seed=seed)
    cem.configure(action_space=batch_space(action_space, 1), n_envs=1,
                  config=swm.PlanConfig(horizon=1, receding_horizon=1, action_block=knots, warm_start=True))
    if cem.action_dim != 2*knots: raise ValueError('Native CEM coefficient dimension mismatch')
    return cem


def cpu_controls():
    from gymnasium.spaces import Box
    class Cost:
        def __init__(self): self.shapes = []
        def get_cost(self, info, actions): self.shapes.append(list(actions.shape)); return actions.square().sum((2, 3))
    rows = []
    for k in [25, 5, 1]:
        cost = Cost(); cem = solver(BasisCost(cost, k), Box(-1., 1., (2,)), k, 300, SEED, 'cpu')
        mean, std = cem.init_action_distrib(); assert torch.equal(mean, torch.zeros_like(mean)) and torch.equal(std, torch.ones_like(std))
        raw = cem.solve({})['actions']; assert list(raw.shape) == [1, 1, 2*k]
        assert cost.shapes == [[1, 300, 1, 50]]*30
        zero = expand_actions(torch.zeros(1, 7, 1, 2*k), k); assert torch.equal(zero, torch.zeros(1, 7, 1, 50))
        one = expand_actions(torch.ones(1, 7, 1, 2*k), k); assert torch.equal(one, torch.ones(1, 7, 1, 50))
        if k == 25:
            x = torch.randn(1, 7, 1, 50); assert torch.equal(expand_actions(x, k), x)
        if k == 5:
            x = torch.arange(10.).reshape(1, 1, 1, 10); y = expand_actions(x, k).reshape(25, 2)
            assert torch.equal(y[::6], x.reshape(5, 2))
        rows.append({'knots': k, 'parameter_dim': cem.action_dim, 'return_shape': list(raw.shape), 'model_candidate_shape': cost.shapes[0], 'calls': len(cost.shapes), 'passed': True})
    return rows


@torch.inference_mode()
def run(args):
    import gymnasium as gym
    import stable_worldmodel as swm
    if importlib.metadata.version('stable-worldmodel') != '0.0.6': raise ValueError('Requires native CEM0.0.6')
    torch.set_num_threads(4); torch.manual_seed(SEED)
    out = Path(args.output); out.mkdir(parents=True, exist_ok=False)
    write_json(out/'cpu_controls.json', cpu_controls())
    if args.cpu_controls:
        (out/'action_basis_used.py').write_text(Path(__file__).read_text())
        write_json(out/'complete.json', {'completed': True, 'scope': 'CPU controls only', 'harness_sha256': sha256(__file__)})
        return
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]
    write_json(out/'config.json', {'args': vars(args), 'sources': cfgs, 'methods': METHODS, 'seed': SEED,
        'goal_offsets': [25, 75], 'count': 16, 'env_budgets': [50, 150], 'execute_steps': 25,
        'cem': {'horizon': 1, 'K': 30, 'iterations': 30, 'initial_mean': 0, 'initial_std': 1},
        'transform': 'normalized coordinates; linear interpolate align_corners=True; constant repeat; k25 identity',
        'scope': 'classic baseline/diagnostic, no training, no novelty or equal-exploration-variance/equal-wallclock claim; released WM training overlap unknown',
        'hardware': torch.cuda.get_device_name(), 'harness_sha256': sha256(__file__),
        'source_assets': {c['task']: {'wm_sha256': sha256(c['checkpoint']), 'normalization_sha256': sha256(Path(s)/'action_normalization.npz')} for s, c in zip(args.sources, cfgs)},
        'cem_sha256': sha256(inspect.getfile(swm.solver.CEMSolver)),
        'helpers': {n: sha256(Path(__file__).with_name(n)) for n in ['first_wave.py', 'recovery_forks.py']},
        'prepared_manifest': json.loads((Path(args.prepared)/'manifest.json').read_text())})
    for name in ['action_basis.py', 'first_wave.py', 'recovery_forks.py']:
        (out/name.replace('.py', '_used.py')).write_text(Path(__file__).with_name(name).read_text())
    rows = []; order = np.random.default_rng(SEED)
    for source, cfg in zip(args.sources, cfgs):
        task = cfg['task']; model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
        norm = np.load(Path(source)/'action_normalization.npz')
        env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
        for offset in [25, 75]:
            data = np.load(Path(args.prepared)/f'{task}_g{offset}.npz')
            for j in range(16):
                anchor = {'state': data['state'][j], 'goal_state': data['goal_state'][j]}; restore(env, anchor, SEED+j)
                info = native_info(env.render(), data['goal_pixels'][j]); start = sync_time(); goal = model.encode({'pixels': info['goal'].cuda()})['emb']; goal_seconds = sync_time()-start
                if offset == 25 and j == 0:
                    initial = model.encode({'pixels': info['pixels'].cuda()})['emb']; write_json(out/f'{task}_native_control.json', controls(model, info, initial, goal))
                for method in order.permutation(list(METHODS)):
                    k, n = METHODS[method]; restore(env, anchor, SEED+j); success, steps, searches = False, 0, []; episode_start = sync_time()
                    for decision in range(2*offset//25):
                        begin = sync_time(); info = native_info(env.render(), data['goal_pixels'][j]); initial = model.encode({'pixels': info['pixels'].cuda()})['emb']
                        native = MacroCost(model, initial, goal); cem = solver(BasisCost(native, k), env.action_space, k, n, SEED+j*100+decision, 'cuda')
                        coefficients = cem.solve({})['actions'].cuda().unsqueeze(1); action = expand_actions(coefficients, k).cpu().numpy().reshape(25, 2)*norm['std']+norm['mean']
                        searches.append({'parameter_dim': 2*k, 'calls': native.calls, 'candidate_evaluations': n*native.calls, 'predicted_macro_transitions': n*native.calls, 'seconds_with_current_encoding': sync_time()-begin})
                        for a in action:
                            _, _, done, truncated, _ = env.step(a); steps += 1
                            if done or truncated: success = bool(done); break
                        if done or truncated: break
                    rows.append({'task': task, 'goal_offset': offset, 'anchor': j, 'source_episode': int(data['episode'][j]), 'method': method, 'parameter_dim': 2*k, 'success': success, 'env_steps': steps, 'native_task_distance': task_distance(env, task), 'goal_encoding_seconds': goal_seconds, 'episode_seconds': sync_time()-episode_start, 'searches': searches})
                    write_json(out/'rows.json', rows); print('action_basis', task, offset, j, method, success, steps, flush=True)
        env.close(); del model; torch.cuda.empty_cache()
    summary = []; boot = np.random.default_rng(SEED+8000).integers(0, 16, (2000, 16))
    for task in ['tworoom', 'pusht']:
        for offset in [25, 75]:
            group = [r for r in rows if r['task'] == task and r['goal_offset'] == offset]
            for method in METHODS:
                rr = sorted([r for r in group if r['method'] == method], key=lambda r: r['anchor']); s = sum(r['success'] for r in rr)
                result = {'task': task, 'goal_offset': offset, 'method': method, 'parameter_dim': 2*METHODS[method][0], 'n': 16, 'successes': s, 'wilson95': wilson(s, 16), 'total_env_steps': sum(r['env_steps'] for r in rr), 'candidate_evaluations': sum(q['candidate_evaluations'] for r in rr for q in r['searches']), 'planning_seconds_total': sum(q['seconds_with_current_encoding'] for r in rr for q in r['searches'])}
                for baseline in ['ZERO25-N900', 'ZERO25-N300']:
                    base = sorted([r for r in group if r['method'] == baseline], key=lambda r: r['anchor']); delta = np.array([int(r['success'])-int(b['success']) for r, b in zip(rr, base)])
                    result[baseline] = {'paired_gain': float(delta.mean()), 'paired_ci95': np.quantile(delta[boot].mean(1), [.025, .975]).tolist(), 'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0))}
                summary.append(result)
    write_json(out/'summary.json', summary); write_json(out/'complete.json', {'completed': True, 'episodes': len(rows), 'physical_env_steps': sum(r['env_steps'] for r in rows)})
    shutil.copytree(out, Path('/home/xiang/.cache/latent-wm-results')/out.name)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--sources', nargs=2); p.add_argument('--prepared'); p.add_argument('--output', required=True); p.add_argument('--cpu-controls', action='store_true')
    args = p.parse_args()
    if not args.cpu_controls and (not args.sources or not args.prepared): p.error('--sources and --prepared required for evaluation')
    try: run(args)
    except Exception as error:
        if Path(args.output).exists(): write_json(Path(args.output)/'failure.json', {'error': type(error).__name__, 'message': str(error)})
        raise
