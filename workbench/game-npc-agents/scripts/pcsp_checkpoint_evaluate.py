"""E34 fixed-checkpoint evaluation; no best-seed or best-iteration selection."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--seed', type=int, choices=[42, 43, 44], required=True)
    ap.add_argument('--iteration', type=int, choices=[30, 100, 300], required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    sources = {alias: args.runs / f'e34_cpu_s{args.seed}_{route}' / f'checkpoint_{args.iteration:04d}'
               for alias, route in [('no', 'no_consist'), ('full', 'full')]}
    for alias, folder in sources.items():
        meta = json.loads((folder / 'manifest.json').read_text())
        assert meta['completed_iterations'] == args.iteration and meta['seed'] == args.seed
        assert (folder / 'policy.pt').exists() and (folder / 'training_state.pt').exists()
    args.out.mkdir(parents=True, exist_ok=False)
    prefix = args.out / 'policy_'
    for alias, folder in sources.items():
        Path(str(prefix) + alias).symlink_to(folder, target_is_directory=True)
    script_dir = Path(__file__).resolve().parent
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    start = time.monotonic()
    operations = [
        ('native', 'pcsp_native_aec_evaluate.py', []),
        ('semantic', 'pcsp_semantic_selectivity.py', ['--training-seed', str(args.seed)]),
        ('interest', 'pcsp_interest_edit.py', ['--mode', 'run', '--training-seed', str(args.seed)]),
    ]
    summaries = {}
    for name, filename, extra in operations:
        command = [sys.executable, str(script_dir / filename), '--policy-prefix', str(prefix),
                   '--out', str(args.out / name), *extra]
        with (args.out / f'{name}.log').open('w') as log:
            result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(f'{name} failed; preserve logs at {args.out}')
        summaries[name] = json.loads((args.out / name / 'summary.json').read_text())
        print(json.dumps({'seed': args.seed, 'iteration': args.iteration, 'completed': name,
                          'wall_seconds': time.monotonic()-start}), flush=True)
    episodes = json.loads((args.out / 'interest/episodes.json').read_text())
    cells = []
    for route in ['no', 'full']:
        for pid in [401, 421, 441, 461, 481]:
            group = [r for r in episodes if r['route'] == route and r['id'] == pid]
            mean = lambda input_C, goal: sum(r[goal] for r in group if r['input_C'] == input_C) / 3
            x = mean('high', 'J_high') - mean('low', 'J_high')
            y = mean('high', 'J_low') - mean('low', 'J_low')
            cells.append({'route': route, 'id': pid, 'J_H_given_H': mean('high', 'J_high'),
                 'J_H_given_L': mean('low', 'J_high'), 'J_L_given_H': mean('high', 'J_low'),
                 'J_L_given_L': mean('low', 'J_low'), 'high_goal_effect': x, 'low_goal_effect': y,
                 'classification': 'low_input_dominates' if x < 0 and y < 0 else 'high_input_dominates' if x > 0 and y > 0
                                   else 'preference_crossover' if x > 0 and y < 0 else 'reverse_crossover'})
    result = {'training_seed': args.seed, 'completed_iterations': args.iteration,
         'native': summaries['native'], 'semantic': summaries['semantic'], 'interest': summaries['interest'],
         'interest_four_cells': cells, 'wall_seconds': time.monotonic()-start,
         'raw': str(args.out), 'cloud_calls': 0, 'scientific_increment': 0}
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'seed': args.seed, 'iteration': args.iteration,
         'native_utility': {r: summaries['native']['policies'][r]['native_reward_mean'] for r in ['no', 'full']},
         'semantic_log_difference': summaries['semantic']['full_minus_no_log_selectivity'],
         'interest_relative_effect': summaries['interest']['routes'],
         'interest_crossover_count': sum(c['classification'] == 'preference_crossover' for c in cells)}), flush=True)


if __name__ == '__main__':
    main()
