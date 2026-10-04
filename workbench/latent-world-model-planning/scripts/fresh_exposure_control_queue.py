"""Locked sufficiently exposed BASE1000 reference on the existing fresh ledger."""
import gc
import json
from pathlib import Path
from types import SimpleNamespace
import torch
import bounded_control as b

ROOT=Path('/home/xiang/.cache/latent-wm-results')
if __name__=='__main__':
    run=ROOT/'20261004-E16-data-exposure-resume-RTX-s0'
    assert json.loads((run/'complete.json').read_text())==dict(completed=True,snapshots=1,updates=56500,source_immutable=True)
    summary=json.loads((run/'summary.json').read_text())[0]
    checkpoint=summary['checkpoint'];assert b.sha(checkpoint)==summary['checkpoint_sha256']
    for interface in ['native','physical']:
        out=Path('/tmp/latent-wm-runs')/f'20261005-E16-BASE1000-fresh-{interface}-RTX'
        b.evaluate(SimpleNamespace(bank='/tmp/latent-wm-runs/20261004-E20-fresh-control-bank48',
            output=str(out),checkpoint=checkpoint,interface=interface))
        gc.collect();torch.cuda.empty_cache()
