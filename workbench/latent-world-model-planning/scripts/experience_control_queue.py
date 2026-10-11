"""Every fixed E20 experience-use endpoint, on original RTX simulator hardware."""
import gc
import json
import shutil
import time
from pathlib import Path
from types import SimpleNamespace
import torch
import bounded_control as b

ROOT = Path('/home/xiang/.cache/latent-wm-results')
HF = Path('/home/xiang/.cache/huggingface/latent-wm-trained')


if __name__ == '__main__':
    for seed in range(3):
        for arm in ['IID-BRANCH', 'REPLAY-ONLY', 'MIX']:
            source = f'20261005-E20-experience-{arm}-A100-s{seed}'
            while not (ROOT/source/'complete.json').exists():
                if (ROOT/source/'failure.json').exists():
                    raise RuntimeError(f'Locked training failed: {source}; no survivor replacement')
                print('waiting_for_fixed_endpoint', source, flush=True); time.sleep(30)
            assert json.loads((ROOT/source/'complete.json').read_text()) == dict(completed=True, arm=arm, seed=seed, updates=2000)
            cfg = json.loads((ROOT/source/'config.json').read_text())
            assert cfg['script_sha256'] == b.sha(Path(__file__).with_name('experience_utilization.py'))
            checkpoint = HF/source/'u2000.ckpt'
            snapshots = json.loads((ROOT/source/'summary.json').read_text())
            assert b.sha(checkpoint) == next(v['checkpoint_sha256'] for v in snapshots if v['updates']==2000)
            for interface in ['native', 'physical']:
                out = Path('/tmp/latent-wm-runs')/f'20261005-E20-experience-control-{arm}-s{seed}-{interface}-RTX'
                try:
                    b.evaluate(SimpleNamespace(bank='/tmp/latent-wm-runs/20261004-E20-fresh-control-bank48',
                        checkpoint=str(checkpoint), output=str(out), interface=interface))
                    context = dict(arm=arm, seed=seed, source_training_run=source, queue_sha256=b.sha(__file__))
                    b.save(out/'training_source.json', context); shutil.copy2(out/'training_source.json', ROOT/out.name/'training_source.json')
                except Exception as error:
                    if out.exists():
                        b.save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
                        if not (ROOT/out.name).exists(): shutil.copytree(out, ROOT/out.name)
                    raise
                gc.collect(); torch.cuda.empty_cache()
