"""OGBench visual-antmaze-<size>-navigate-v0 -> lowres/vantmaze<size>_64 (pixels.npy + meta.npz).

The dataset's own 64x64 observations (OGBench 'back' camera that follows the ant, position-coloured floor)
are used as-is; meta keeps qpos/qvel so evaluation can reset the simulator to any logged state."""
import os
import sys

import numpy as np

SIZE = sys.argv[1] if len(sys.argv) > 1 else 'medium'
SRC = f'/tmp/latent-wm-data/ogbench/visual-antmaze-{SIZE}-navigate-v0.npz'
OUT = os.path.join(os.environ.get('LWM_DATA', '/tmp/latent-wm-data/lowres'), f'vantmaze{SIZE}_64')

if __name__ == '__main__':
    d = np.load(SRC)
    term = d['terminals'].astype(bool)
    ends = np.nonzero(term)[0]
    starts = np.concatenate([[0], ends[:-1] + 1])
    os.makedirs(OUT, exist_ok=True)
    qpos, qvel = d['qpos'].astype(np.float32), d['qvel'].astype(np.float32)
    np.savez(f'{OUT}/meta.npz', action=d['actions'].astype(np.float32), proprio=qpos, qpos=qpos, qvel=qvel,
             ep_offset=starts.astype(np.int64), ep_len=(ends - starts + 1).astype(np.int32))
    mm = np.lib.format.open_memmap(f'{OUT}/pixels.npy', mode='w+', dtype=np.uint8, shape=d['observations'].shape)
    obs = d['observations']
    for i in range(0, len(obs), 100000):
        mm[i:i + 100000] = obs[i:i + 100000]
    mm.flush()
    print('done', len(obs), 'episodes', len(starts))
