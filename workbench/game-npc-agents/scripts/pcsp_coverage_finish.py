"""E41 all seeds and registered stages using unchanged E34/E37 readouts."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--surface-prefix', default='e41_s{seed}_surface_v2')
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    scripts = Path(__file__).resolve().parent
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    finished = []

    def run(name, script, extra):
        with (args.out/f'{name}.log').open('w') as f:
            result = subprocess.run([sys.executable, str(scripts/script), *extra],
                                    env=env, stdout=f, stderr=subprocess.STDOUT)
        if result.returncode: raise RuntimeError(f'{name} failed; inspect preserved log')

    def evaluate(stage, seed, augmentation):
        run_name = args.surface_prefix.format(seed=seed) if augmentation=='surface' else f'e41_s{seed}_intervention'
        directory = args.runs/run_name/f'checkpoint_{stage:04d}'
        while not (directory/'manifest.json').exists(): time.sleep(15)
        meta = json.loads((directory/'manifest.json').read_text())
        assert meta['seed'] == seed and meta['completed_iterations'] == stage
        reference = args.runs/f'e34_cpu_s{seed}_no_consist'/f'checkpoint_{stage:04d}'
        suffix='_v2' if augmentation=='surface' else ''
        destination = args.runs/f'e41_eval_s{seed}_{augmentation}_i{stage}{suffix}'
        if not (destination/'summary.json').exists():
            run(f'{seed}_{augmentation}_{stage}', 'pcsp_checkpoint_evaluate.py',
                ['--runs', str(args.runs), '--seed', str(seed), '--iteration', str(stage),
                 '--reference-directory', str(reference), '--alternative-directory', str(directory),
                 '--comparison-name', f'{augmentation}_vs_original_no_infoNCE', '--out', str(destination)])
        print(json.dumps({'completed_stage':stage, 'seed':seed, 'augmentation':augmentation}), flush=True)
        return {'stage':stage, 'seed':seed, 'augmentation':augmentation, 'raw':str(destination)}

    for stage in [30, 100, 300]:
        with ThreadPoolExecutor(max_workers=3) as pool:
            for future in as_completed([pool.submit(evaluate,stage,s,a)
                    for s in [42,43,44] for a in ['surface','intervention']]):
                finished.append(future.result())
        policies = {str(s): {'original':str(args.runs/f'e34_cpu_s{s}_no_consist'/f'checkpoint_{stage:04d}'),
                            'surface':str(args.runs/args.surface_prefix.format(seed=s)/f'checkpoint_{stage:04d}'),
                            'intervention':str(args.runs/f'e41_s{s}_intervention'/f'checkpoint_{stage:04d}')} for s in [42,43,44]}
        manifest = args.out/f'policies_i{stage}.json'
        manifest.write_text(json.dumps(policies, indent=2)+'\n')
        destination = args.runs/f'e41_functional_i{stage}_v2'
        if not (destination/'summary.json').exists():
            run(f'functional_{stage}', 'pcsp_matched_functional_response.py',
                ['--runs',str(args.runs), '--iteration',str(stage), '--policy-manifest',str(manifest),
                 '--out',str(destination)])
        (args.out/f'stage_{stage}_complete.json').write_text(json.dumps({
             'stage':stage, 'completed_evaluations':[x for x in finished if x['stage']==stage],
             'functional_raw':str(destination), 'selection':False}, indent=2)+'\n')
        print(json.dumps({'all_seeds_complete_at':stage}), flush=True)
    (args.out/'summary.json').write_text(json.dumps({'evaluations':finished,
          'seeds':[42,43,44], 'stages':[30,100,300], 'best_selection':False, 'cloud_calls':0}, indent=2)+'\n')


if __name__ == '__main__': main()
