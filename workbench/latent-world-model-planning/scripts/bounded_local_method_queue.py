"""Run all locked E20 methods on the original simulator/render hardware."""
import gc
import json
from pathlib import Path
from types import SimpleNamespace
import torch
import bounded_control as b

HF = Path('/home/xiang/.cache/huggingface/latent-wm-trained')
ROOT = Path('/home/xiang/.cache/latent-wm-results')
BANK = Path('/tmp/latent-wm-runs/20261004-E20-fresh-control-bank48')
METHODS = ['PLAIN', 'GLOBAL-SG', 'CENTER', 'DET-INVERSE', 'PROB-INVERSE']


def run():
    jobs = []
    for seed in range(3):
        for method in METHODS:
            source = f'20261004-E20-joint-{method}-A100-s{seed}'
            assert json.loads((ROOT/source/'complete.json').read_text())['completed']
            checkpoint = HF/source/'u2000.ckpt'
            output = Path('/tmp/latent-wm-runs')/f'20261004-E20-control-{method}-s{seed}-physical-RTX'
            assert checkpoint.is_file() and not output.exists() and not (ROOT/output.name).exists()
            jobs.append(SimpleNamespace(bank=str(BANK), output=str(output), checkpoint=str(checkpoint), interface='physical'))
    for args in jobs:
        try:
            b.evaluate(args)
        except Exception as error:
            if Path(args.output).exists():
                b.save(Path(args.output)/'failure.json', dict(type=type(error).__name__, message=str(error)))
            raise
        gc.collect()
        torch.cuda.empty_cache()


if __name__ == '__main__':
    run()
