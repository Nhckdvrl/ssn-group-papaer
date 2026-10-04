"""Wait for all locked F3 pipelines, then audit the full matrix once."""
from pathlib import Path
import subprocess
import sys
import time

root = Path('/home/xiang/.cache/latent-wm-results')
pipelines = [root/f'20261005-E18-intact-F3-{task}-s{seed}-pipeline.json'
             for task in ['tworoom', 'pusht'] for seed in [0, 42, 3072]]
last_report = 0
while not all(path.exists() for path in pipelines):
    failures = list(root.glob('20261005-E18-intact-F3-*/failure.json'))
    assert not failures, [str(path) for path in failures]
    if time.monotonic()-last_report > 60:
        print('Awaiting complete F3 matrix', sum(path.exists() for path in pipelines), '/6', flush=True)
        last_report = time.monotonic()
    time.sleep(10)
time.sleep(1)
subprocess.run([sys.executable, '-u', str(Path(__file__).with_name('intact_full_recovery_audit.py'))], check=True)
