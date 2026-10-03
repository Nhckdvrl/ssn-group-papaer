"""E13 A3: wider short search versus longer recursive imagination."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
import torch
from first_wave import native_info, restore, sha256, sync_time, write_json
from closed_loop import wilson
from recovery_forks import controls, solve, task_distance


METHODS = {'H25-N300': (1, 300), 'H25-N900': (1, 900), 'H75-N300': (3, 300)}


def occupancy():
    return subprocess.check_output(['nvidia-smi', '--query-gpu=index,memory.used,utilization.gpu',
                                   '--format=csv,noheader'], text=True).strip()


def run(args):
    import gymnasium as gym
    import stable_worldmodel
    torch.set_num_threads(4)
    torch.manual_seed(66000)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    cfgs = [json.loads((Path(s)/'config.json').read_text()) for s in args.sources]
    write_json(out/'config.json', {'args': vars(args), 'sources': cfgs, 'seed': 66000, 'count': 32,
        'methods': METHODS, 'goal_offsets': [25, 75], 'receding_primitive_steps': 25, 'env_budget_multiple': 2,
        'cem': {'K': 30, 'iterations': 30, 'consistency_weight': 0}, 'hardware': torch.cuda.get_device_name(),
        'harness_sha256': sha256(__file__), 'recovery_helper_sha256': sha256(Path(__file__).with_name('recovery_forks.py')),
        'prepared_manifest': json.loads((Path(args.prepared)/'manifest.json').read_text()),
        'scope': 'zero training, one released model per task; transition counts are not wall-clock speedups'})
    (out/'horizon_breadth_used.py').write_text(Path(__file__).read_text())
    (out/'recovery_forks_used.py').write_text(Path(__file__).with_name('recovery_forks.py').read_text())
    write_json(out/'gpu_start.json', {'occupancy': occupancy()})
    rows = []
    rng = np.random.default_rng(66000)
    with torch.inference_mode():
        for source, cfg in zip(args.sources, cfgs):
            task = cfg['task']
            model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
            norm = np.load(Path(source)/'action_normalization.npz')
            env = gym.make('swm/TwoRoom-v1' if task == 'tworoom' else 'swm/PushT-v1', render_mode='rgb_array').unwrapped
            for offset in [25, 75]:
                data = np.load(Path(args.prepared)/f'{task}_g{offset}.npz')
                for j in range(32):
                    anchor = {'state': data['state'][j], 'goal_state': data['goal_state'][j]}
                    restore(env, anchor, 66000+j)
                    info = native_info(env.render(), data['goal_pixels'][j])
                    goal = model.encode({'pixels': info['goal'].cuda()})['emb']
                    if offset == 25 and j == 0:
                        initial = model.encode({'pixels': info['pixels'].cuda()})['emb']
                        write_json(out/f'{task}_native_control.json', controls(model, info, initial, goal))
                    for method in rng.permutation(list(METHODS)):
                        horizon, candidates = METHODS[method]
                        restore(env, anchor, 66000+j)
                        success, steps, searches = False, 0, []
                        for decision in range(2*offset//25):
                            info = native_info(env.render(), data['goal_pixels'][j])
                            begin = sync_time()
                            initial = model.encode({'pixels': info['pixels'].cuda()})['emb']
                            actions, search = solve(model, initial, goal, env, horizon, candidates, 66000+j*100+decision)
                            search['planning_seconds_with_current_encoding'] = sync_time()-begin
                            search['predicted_macro_transitions'] = horizon*search['candidate_evaluations']
                            searches.append(search)
                            first = actions[0, 0, 0].cpu().numpy().reshape(25, 2)*norm['std']+norm['mean']
                            for a in first:
                                _, _, done, truncated, _ = env.step(a)
                                steps += 1
                                if done or truncated:
                                    success = bool(done)
                                    break
                            if done or truncated:
                                break
                        rows.append({'task': task, 'goal_offset': offset, 'anchor': j,
                            'source_episode': int(data['episode'][j]), 'method': method, 'success': success,
                            'env_steps': steps, 'native_task_distance': task_distance(env, task), 'searches': searches})
                        write_json(out/'rows.json', rows)
                        print('horizon_breadth', task, offset, j, method, success, steps, flush=True)
                write_json(out/f'gpu_after_{task}_{offset}.json', {'occupancy': occupancy()})
            env.close()
            del model
            torch.cuda.empty_cache()
    summary = []
    boot = np.random.default_rng(86000).integers(0, 32, (2000, 32))
    for task in ['tworoom', 'pusht']:
        for offset in [25, 75]:
            group = [r for r in rows if r['task'] == task and r['goal_offset'] == offset]
            base = {r['anchor']: r for r in group if r['method'] == 'H25-N300'}
            for method in METHODS:
                data = sorted([r for r in group if r['method'] == method], key=lambda r: r['anchor'])
                delta = np.array([int(r['success'])-int(base[r['anchor']]['success']) for r in data])
                successes = sum(r['success'] for r in data)
                summary.append({'task': task, 'goal_offset': offset, 'method': method, 'n': 32, 'successes': successes,
                    'success_wilson_ci95': wilson(successes, 32), 'paired_gain_vs_H25N300': float(delta.mean()),
                    'paired_gain_ci95': np.quantile(delta[boot].mean(1), [.025, .975]).tolist(),
                    'helped': int(sum(delta > 0)), 'harmed': int(sum(delta < 0)),
                    'total_env_steps': sum(r['env_steps'] for r in data),
                    'predicted_macro_transitions': sum(s['predicted_macro_transitions'] for r in data for s in r['searches']),
                    'planning_seconds_mean': float(np.mean([s['planning_seconds_with_current_encoding'] for r in data for s in r['searches']]))})
    write_json(out/'summary.json', summary)
    write_json(out/'complete.json', {'completed': True, 'episodes': len(rows)})
    durable = Path('/home/xiang/.cache/latent-wm-results')/out.name
    shutil.copytree(out, durable)
    print('durable_results', durable, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--sources', nargs='+', required=True)
    p.add_argument('--prepared', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    try:
        run(args)
    except Exception as error:
        out = Path(args.output)
        if out.exists():
            write_json(out/'failure.json', {'error': type(error).__name__, 'message': str(error)})
        raise
