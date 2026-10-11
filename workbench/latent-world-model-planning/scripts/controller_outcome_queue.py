"""Execute locked H1 cache or matched training after actual prerequisites."""
import argparse
from pathlib import Path
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('--task', choices=['tworoom', 'pusht'], required=True)
p.add_argument('--mode', choices=['features', 'train'], required=True)
p.add_argument('--gpus', required=True)
args = p.parse_args()
root = Path('/home/xiang/.cache/latent-wm-results')
scripts = Path(__file__).parent
needed = [root/f'20261005-E14-controller-consequence-{args.task}/complete.json']
if args.mode == 'train':
    needed += [root/f'20261005-E14-controller-outcome-features-{args.task}/complete.json', scripts.parent/'results/E14_20261005_controller_consequence_results.json']
while not all(path.exists() for path in needed):
    assert not (root/f'20261005-E14-controller-consequence-{args.task}/failure.json').exists()
    assert not (root/f'20261005-E14-controller-outcome-features-{args.task}/failure.json').exists()
    time.sleep(10)
arms = ['FINETUNE-WORLD', 'DIRECT-CONTROLLER'] if args.mode == 'train' else [None]
for arm in arms:
    script = scripts/('controller_outcome_train.py' if arm else 'controller_outcome_features.py')
    command = [sys.executable, '-u', str(scripts/'run_when_gpu_free.py'), '--gpus', args.gpus, '--script', str(script), '--', '--task', args.task]
    if arm:
        command += ['--arm', arm]
    subprocess.run(command, check=True)
