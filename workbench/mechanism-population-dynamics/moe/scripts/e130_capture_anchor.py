"""One-shot E130 functional captures for the registered E128 seed0 anchor.

Wait for both original training and its original finalizer to exit. Then use
reserved physical GPU2, preserving their code, metrics, assets and readouts.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

WB = Path(__file__).resolve().parents[1]
OUT = Path('/tmp/xiang-moe-20261025/e128_seed0')
RESULT = WB / 'results/e130/seed0_anchor_functions.json'


def write(value):
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    temporary = RESULT.with_suffix('.partial')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(RESULT)


def command(pid):
    p = Path('/proc') / str(pid) / 'cmdline'
    try:
        return p.read_bytes().replace(b'\0', b' ').decode()
    except (FileNotFoundError, ProcessLookupError):
        return ''


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main(args):
    deadline = time.monotonic() + args.max_hours * 3600
    while time.monotonic() < deadline:
        train, finish = command(args.training_pid), command(args.finalizer_pid)
        if train and ('e128_epoch_recovery.py' not in train or str(OUT) not in train):
            raise RuntimeError('Training PID was reused')
        if finish and 'e128_finalize.py' not in finish:
            raise RuntimeError('Finalizer PID was reused')
        if not train and not finish:
            break
        time.sleep(30)
    else:
        write({'status': 'wait_timeout_no_capture'}); return
    import e128_finalize
    import e130_cross_seed
    e130_cross_seed.verify_frozen_sources()
    summary, provenance, protocol, checkpoint, driver_sha = e128_finalize.validate(OUT)
    apps = subprocess.check_output(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader'], text=True)
    lines = subprocess.check_output(['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader'], text=True).splitlines()
    gpu = {int(line.split(',')[0]): line.split(',')[1].strip() for line in lines}[2]
    if any(line.split(',')[0].strip() == gpu for line in apps.splitlines() if ',' in line):
        write({'status': 'deferred_gpu2_busy_no_capture', 'gpu_uuid': gpu}); return
    if os.environ.get('CUDA_VISIBLE_DEVICES') != '2':
        raise RuntimeError('Anchor capture requires reserved physical GPU2')
    assets, errors = [], {}
    destination = Path('/home/xiang/mechpop_cache/e130_seed0_anchor_functions')
    destination.mkdir(parents=True, exist_ok=True)
    for label, cp in [('final', checkpoint), ('late', OUT / 'snapshots/step061440.pt')]:
        raw = OUT / ('functional_' + label + '.npz')
        small = WB / 'results/e130/functional' / ('seed0_anchor_' + label + '.json')
        log = WB / 'results/e130/logs' / ('seed0_anchor_' + label + '.log')
        argv = ['/home/xiang/.venvs/mechpop/bin/python', '-u', str(WB / 'scripts/e124_functional_capture.py'),
                '--mode', 'capture', '--model', provenance['args']['model'], '--checkpoint', str(cp),
                '--data', provenance['args']['data'], '--plan', str(WB / 'results/e124/plan.json'),
                '--output', str(raw), '--summary', str(small), '--seed', '0', '--order-seed', '0',
                '--run-id', 'E130-seed0-anchor-' + label, '--alpha', '.125', '--batch-size', '16',
                '--cal-sequences', '64', '--seq-len', '512', '--cal-stride', '4', '--cal-seed', '91024']
        try:
            with log.open('ab') as handle:
                subprocess.run(argv, cwd=WB, stdout=handle, stderr=subprocess.STDOUT, check=True)
            for path in (raw, small):
                target = destination / path.name
                if target.exists():
                    raise FileExistsError(target)
                part = target.with_suffix(target.suffix + '.partial')
                shutil.copyfile(path, part)
                digest = sha(path)
                if sha(part) != digest:
                    raise IOError('Functional asset copy differs')
                part.replace(target)
                assets.append({'path': str(target), 'bytes': target.stat().st_size, 'sha256': digest})
        except Exception as error:
            errors[label] = f'{type(error).__name__}: {error}'
    result = {'status': 'complete' if not errors else 'capture_or_archive_failed', 'experiment': 'E130',
              'anchor': 'E128 seed0/order0', 'step': summary['step'], 'driver_sha256': driver_sha,
              'primary_checkpoint_archive': '/home/xiang/mechpop_cache/e128_seed0_512m',
              'sampling_note': 'Hcal uses the same cover manifest as the E130 new runs',
              'assets': assets, 'errors': errors}
    (destination / 'functional_assets_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    write(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--training-pid', type=int, default=3801880)
    parser.add_argument('--finalizer-pid', type=int, default=3808552)
    parser.add_argument('--max-hours', type=float, default=9.)
    try:
        main(parser.parse_args())
    except Exception as error:
        write({'status': 'failed_no_further_capture', 'error': f'{type(error).__name__}: {error}'})
        raise
