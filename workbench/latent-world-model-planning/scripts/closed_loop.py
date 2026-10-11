"""E13 A1: paired native MPC; all methods share frozen feature caching."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import torch
from first_wave import native_info, restore, sha256, sync_time, write_json
from promotion import Calibration
from timing_audit import SelectiveCost


class PlannerCost:
    def __init__(self, model, mode, fraction, k, calibrations, cached, batch):
        self.model, self.mode, self.fraction, self.k = model, mode, fraction, k
        self.calibrations, self.cached, self.batch = calibrations, cached, batch
        self.calls = []

    def get_cost(self, info, actions):
        evaluator = SelectiveCost(self.model, self.k, self.mode, self.fraction,
            self.calibrations[len(self.calls)], self.batch, self.cached)
        out, timing = evaluator.evaluate(info, actions)
        self.calls.append({'candidates': actions.shape[1], 'refined_candidates': len(out['queried']),
                           'refine_batches': timing['refine_batches'], 'seconds': timing['seconds']})
        return torch.as_tensor(out['estimated_cost'][None], device=actions.device)


def wilson(successes, n):
    z = 1.959963984540054
    p = successes / n
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    margin = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return [float(center-margin), float(center+margin)]


def run(args):
    import gymnasium as gym
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    torch.set_num_threads(4)
    source, output = Path(args.source), Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    cfg = json.loads((source / 'config.json').read_text())
    if json.loads((source / 'data_source.json').read_text())['source'] != 'official_hdf5':
        raise ValueError('Closed-loop method pilot requires native dataset/action statistics')
    output_config = {'source_config': cfg, 'seed': args.seed, 'hardware': torch.cuda.get_device_name(),
                     'harness_sha256': sha256(__file__), 'feature_caching': True,
                     'sampling': 'native CEM; paired per-episode/per-decision seeds; fresh distribution',
                     'limitation': 'one released train checkpoint; eight held-out episode pairs'}
    write_json(output / 'config.json', output_config)
    (output / 'closed_loop_used.py').write_text(Path(__file__).read_text())
    model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
    data = np.load(source / 'anchors.npz')
    norm = np.load(source / 'action_normalization.npz')
    calibration_banks = [np.load(source / f'candidates_{a:04d}.npz') for a in range(cfg['calibration_anchors'])]
    calibrations = [Calibration.fit([b['cheap'][it] for b in calibration_banks],
                                  [b['refined'][it] for b in calibration_banks]) for it in range(cfg['iterations'])]
    methods = [('CHEAP-300', 'CHEAP-ALL', None, 300), ('FULL-300', 'FULL-REFINE', None, 300),
               ('TOP20-300', 'TOP-M-SCREEN', .2, 300), ('TOP30-300', 'TOP-M-SCREEN', .3, 300),
               ('INTERVAL20-300', 'INTERVAL', .2, 300), ('RANDOM30-300', 'RANDOM-M', .3, 300),
               ('LOWER64-300', 'LOWER-BOUND', None, 300), ('CHEAP-900', 'CHEAP-ALL', None, 900)]
    write_json(output / 'methods.json', methods)
    env = gym.make('swm/TwoRoom-v1' if cfg['task'] == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
    space = batch_space(env.action_space, 1)
    plan = swm.PlanConfig(horizon=1, receding_horizon=1, action_block=25, warm_start=True)
    # Initialization/warmup excluded, observation/goal encoding included in decisions.
    first = cfg['calibration_anchors']
    with torch.inference_mode():
        inputs = native_info(data['pixels'][first], data['goal_pixels'][first])
        for _ in range(2):
            model.encode({'pixels': inputs['pixels'].cuda()})
    rows = []
    rng = np.random.default_rng(args.seed)
    for a in range(first, cfg['anchors']):
        anchor = {'state': data['states'][a], 'goal_state': data['goal_states'][a]}
        for j in rng.permutation(len(methods)):
            name, mode, fraction, n = methods[j]
            restore(env, anchor, args.seed + a)
            started = sync_time()
            episode_actions, decisions, success, steps = [], [], False, 0
            goal_started = sync_time()
            with torch.inference_mode():
                goal = model.encode({'pixels': native_info(env.render(), data['goal_pixels'][a])['goal'].cuda()})['emb']
            goal_seconds = sync_time() - goal_started
            for decision in range(2):
                start = sync_time()
                info = native_info(env.render(), data['goal_pixels'][a])
                with torch.inference_mode():
                    initial = model.encode({'pixels': info['pixels'].cuda()})['emb']
                cost = PlannerCost(model, mode, fraction, cfg['elites'], calibrations, (initial, goal), 64)
                solver = swm.solver.CEMSolver(cost, batch_size=1, num_samples=n, topk=cfg['elites'],
                    n_steps=cfg['iterations'], device='cuda', seed=args.seed + a*100 + decision)
                solver.configure(action_space=space, n_envs=1, config=plan)
                solved = solver.solve(info)
                planning_seconds = sync_time() - start + (goal_seconds if decision == 0 else 0)
                actions = solved['actions'][0].numpy().reshape(25, 2) * norm['std'] + norm['mean']
                decisions.append({'planning_seconds': planning_seconds, 'cost_calls': cost.calls})
                for action in actions:
                    _, _, done, truncated, _ = env.step(action)
                    steps += 1
                    episode_actions.append(action)
                    if done or truncated:
                        success = bool(done)
                        break
                if done or truncated:
                    break
            row = {'anchor': a, 'source_episode': int(data['episodes'][a]), 'method': name,
                   'success': success, 'env_steps': steps, 'seconds': sync_time() - started,
                   'decisions': decisions, 'planning_seconds': sum(d['planning_seconds'] for d in decisions),
                   'candidate_evaluations': sum(c['candidates'] for d in decisions for c in d['cost_calls']),
                   'refined_candidates': sum(c['refined_candidates'] for d in decisions for c in d['cost_calls'])}
            rows.append(row)
            np.save(output / f'actions_{a:03d}_{name}.npy', np.asarray(episode_actions))
            write_json(output / 'rows.json', rows)
            print('episode', a, name, 'success', success, 'steps', steps, 'seconds', row['seconds'], flush=True)
    summary = []
    full = {r['anchor']: r for r in rows if r['method'] == 'FULL-300'}
    for name, _, _, _ in methods:
        subset = [r for r in rows if r['method'] == name]
        delta = np.array([float(r['success']) - float(full[r['anchor']]['success']) for r in subset])
        sample = np.random.default_rng(args.seed + 9000).integers(0, len(delta), (2000, len(delta)))
        successes = sum(r['success'] for r in subset)
        summary.append({'method': name, 'episodes': len(subset), 'successes': successes,
            'success_rate': successes/len(subset), 'success_wilson_ci95': wilson(successes, len(subset)),
            'paired_success_delta_vs_full': float(delta.mean()),
            'paired_delta_bootstrap_ci95': np.quantile(delta[sample].mean(1), [.025,.975]).tolist(),
            'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0)),
            'episode_seconds_mean': float(np.mean([r['seconds'] for r in subset])),
            'planning_seconds_per_decision': float(np.mean([d['planning_seconds'] for r in subset for d in r['decisions']])),
            'refined_candidate_fraction': sum(r['refined_candidates'] for r in subset)/sum(r['candidate_evaluations'] for r in subset)})
    write_json(output / 'summary.json', summary)
    write_json(output / 'complete.json', {'completed': True, 'paired_n': len(full),
        'limitation': 'Small pilot; no observed flips does not establish equivalence; no held-out threshold tuning'})
    env.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--seed', type=int, default=0)
    args = p.parse_args()
    try:
        run(args)
    except Exception as exc:
        out = Path(args.output)
        if out.exists(): write_json(out/'failure.json', {'exception':type(exc).__name__, 'message':str(exc)})
        raise
