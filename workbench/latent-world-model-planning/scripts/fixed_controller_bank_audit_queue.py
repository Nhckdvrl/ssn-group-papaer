"""Wait for both complete H2A tasks, then audit them once on free RTX0."""
from pathlib import Path
import subprocess
import sys
import time

root = Path('/home/xiang/.cache/latent-wm-results')
folders = [root/f'20261005-E14-fixed-controller-experience-{task}' for task in ['tworoom','pusht']]
while not all((folder/'complete.json').exists() for folder in folders):
    assert not any((folder/'failure.json').exists() for folder in folders)
    time.sleep(10)
scripts = Path(__file__).parent
subprocess.run([sys.executable,'-u',str(scripts/'run_when_gpu_free.py'),'--gpus','0','--script',str(scripts/'fixed_controller_bank_audit.py')],check=True)
