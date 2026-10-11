"""Read the complete H1 four-model matrix after actual training."""
from pathlib import Path
import subprocess
import sys
import time

root = Path('/home/xiang/.cache/latent-wm-results')
folders = [root/f'20261005-E14-controller-outcome-{task}-{arm}-s0' for task in ['tworoom', 'pusht'] for arm in ['FINETUNE-WORLD', 'DIRECT-CONTROLLER']]
while not all((folder/'complete.json').exists() for folder in folders):
    assert not any((folder/'failure.json').exists() for folder in folders)
    time.sleep(10)
scripts = Path(__file__).parent
subprocess.run([sys.executable, '-u', str(scripts/'run_when_gpu_free.py'), '--gpus', '2', '--script', str(scripts/'controller_outcome_evaluate.py')], check=True)
