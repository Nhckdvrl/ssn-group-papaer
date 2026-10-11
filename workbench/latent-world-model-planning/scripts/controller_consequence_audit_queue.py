"""Audit the entire fixed H0 matrix once, after both tasks complete."""
from pathlib import Path
import subprocess
import sys
import time

root = Path('/home/xiang/.cache/latent-wm-results')
tasks = ['tworoom', 'pusht']
while not all((root/f'20261005-E14-controller-consequence-{task}/complete.json').exists() for task in tasks):
    assert not any((root/f'20261005-E14-controller-consequence-{task}/failure.json').exists() for task in tasks)
    time.sleep(10)
scripts = Path(__file__).parent
subprocess.run([sys.executable, '-u', str(scripts/'run_when_gpu_free.py'), '--gpus', '0', '--script', str(scripts/'controller_consequence_audit.py')], check=True)
