"""Retain every E20 arm and source under the stronger native interface."""
import gc
import json
from pathlib import Path
from types import SimpleNamespace
import torch
import bounded_control as b

ROOT = Path('/home/xiang/.cache/latent-wm-results')
HF = Path('/home/xiang/.cache/huggingface/latent-wm-trained')
METHODS = ['PLAIN', 'GLOBAL-SG', 'CENTER', 'DET-INVERSE', 'PROB-INVERSE']


def run():
    jobs = []
    for seed in range(3):
        for method in METHODS:
            source = f'20261004-E20-joint-{method}-A100-s{seed}'
            assert json.loads((ROOT/source/'complete.json').read_text())['completed']
            output = Path('/tmp/latent-wm-runs')/f'20261004-E20-control-{method}-s{seed}-native-RTX'
            assert not output.exists() and not (ROOT/output.name).exists()
            jobs.append(SimpleNamespace(bank='/tmp/latent-wm-runs/20261004-E20-fresh-control-bank48',
                output=str(output), checkpoint=str(HF/source/'u2000.ckpt'), interface='native'))
    for args in jobs:
        try:
            b.evaluate(args)
        except Exception as error:
            if Path(args.output).exists():
                b.save(Path(args.output)/'failure.json', dict(type=type(error).__name__, message=str(error)))
            raise
        gc.collect(); torch.cuda.empty_cache()


if __name__ == '__main__': run()
