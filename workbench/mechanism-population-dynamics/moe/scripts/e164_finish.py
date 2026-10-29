"""Durable E164 phase chain; never retries or starts a follow-up experiment."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

WB = Path(__file__).resolve().parents[2]
ROOT = WB/'moe/results/e164'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--physical-gpu', type=int, default=0); args = parser.parse_args()
    plan = read(ROOT/'plan.json')
    if (ROOT/'execution_complete.json').exists():
        raise FileExistsError('Preserve prior E164 complete execution')
    for phase in ('preflight', 'run'):
        status = ROOT/('supervision_'+phase+'.json')
        if status.exists():
            raise FileExistsError('Inspect prior supervised attempt; this chain does not retry: '+phase)
        command = [sys.executable, '-B', str(WB/'moe/scripts/supervised_process.py'),
                   '--status', str(status), '--log', str(ROOT/('run_'+phase+'.log')),
                   '--cwd', str(WB), '--timeout', '28800', '--', sys.executable, '-B', '-u',
                   str(WB/'moe/scripts/e164_run.py'), phase, '--physical-gpu', str(args.physical_gpu)]
        subprocess.run(command, cwd=WB, check=True)
        state = read(status)
        if state['status'] != 'complete' or state['returncode'] != 0:
            raise ValueError('E164 supervised phase did not exit successfully')
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for command in [('e164_analyze.py', 'analyze'), ('e164_verify.py', 'verify'), ('e164_plot.py',)]:
        subprocess.run([sys.executable, '-B', str(WB/'moe/scripts'/command[0]), *command[1:]],
                       cwd=WB, env=env, check=True)
    manifest = read(ROOT/'manifest.json'); ledger = read(ROOT/'budget.json'); audit = read(ROOT/'independent_audit.json')
    seconds = sum(row['gpu_seconds'] for row in ledger['attempts'])
    if manifest['status'] != 'complete' or audit['status'] != 'passed' or seconds > plan['gpu_limit_seconds']:
        raise ValueError('E164 lacks complete provenance or exceeded its package')
    output = {'experiment': 'E164', 'status': 'complete', 'numerical_source_commit': plan['numerical_source_commit'],
              'plan_sha256': sha(ROOT/'plan.json'), 'manifest_sha256': sha(ROOT/'manifest.json'),
              'summary_sha256': sha(ROOT/'summary.json'), 'independent_audit_sha256': sha(ROOT/'independent_audit.json'),
              'supervision': {phase: sha(ROOT/('supervision_'+phase+'.json')) for phase in ('preflight', 'run')},
              'gpu_seconds': seconds, 'peak_GPU_GB': manifest['peak_GPU_GB'],
              'finisher_sha256': sha(__file__), 'plot_source_sha256': sha(WB/'moe/scripts/e164_plot.py'),
              'no_new_training_or_followup_experiments': True}
    (ROOT/'execution_complete.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
