"""Complete locked matched-learning arms for a single source or value pilot."""
import argparse
import gc
import json
from pathlib import Path
from types import SimpleNamespace
import torch
import matched_learning as m


def run(seed, value=False):
    current = m.digest(m.__file__)
    for device in ['CPU', 'CUDA']:
        p = m.ROOT/f'20261004-E01-matched-learning-{device}-preflight-retry3/controls.json'
        controls = json.loads(p.read_text())
        assert controls['passed'] and controls['source_sha256'] == current
    arms = ['VGIQL-JOINT', 'VGIQL-SEPARATE'] if value else ['ABS', 'RESIDUAL', 'FULL-AD']
    for arm in arms:
        args = SimpleNamespace(cache='/tmp/latent-wm-data/E16-base100-trainseed-cache', arm=arm, seed=seed)
        m.train(args)
        gc.collect()
        torch.cuda.empty_cache()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--seed', type=int, choices=[0,1,2], required=True)
    parser.add_argument('--value', action='store_true'); args = parser.parse_args()
    run(args.seed, args.value)
