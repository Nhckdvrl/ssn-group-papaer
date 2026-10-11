"""All three original training sources for one predeclared experience arm."""
import argparse
import gc
from types import SimpleNamespace
import torch
import experience_utilization as u


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--arm', choices=u.ARMS, required=True)
    args = p.parse_args()
    for seed in range(3):
        u.train(SimpleNamespace(arm=args.arm, seed=seed,
            bank='/tmp/latent-effect-data/20261004-E20-legal-effect-bank44',
            cache='/tmp/latent-wm-data/E16-base100-trainseed-cache'))
        gc.collect(); torch.cuda.empty_cache()
