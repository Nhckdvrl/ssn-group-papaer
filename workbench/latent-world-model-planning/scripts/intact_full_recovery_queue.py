"""Fixed-GPU serial queues for the preregistered six F3 pipelines."""
import argparse
from pathlib import Path
import subprocess
import sys

QUEUES = {
    0: [('tworoom', 0), ('tworoom', 3072)],
    1: [('tworoom', 42), ('pusht', 3072)],
    2: [('pusht', 0)],
    3: [('pusht', 42)],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', type=int, choices=QUEUES, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    subprocess.run([sys.executable, '-m', 'py_compile',
                    str(here/'intact_full_recovery_control.py'),
                    str(here/'intact_multi_seed_source.py')], check=True)
    for task, seed in QUEUES[args.gpu]:
        print('Starting fixed queue', args.gpu, task, seed, flush=True)
        subprocess.run([sys.executable, '-u', str(here/'run_when_gpu_free.py'),
                        '--gpus', str(args.gpu), '--script',
                        str(here/'intact_full_recovery_control.py'), '--',
                        '--task', task, '--seed', str(seed)], check=True)
