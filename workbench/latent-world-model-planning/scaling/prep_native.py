"""Native-resolution (224px) subset of the LeWM HDF5 data for released checkpoints: 1000 whole episodes
(contiguous reads), same layout as lowres/<task>_64 -> /tmp/latent-wm-data/native/<task>_224/."""
import os
import sys

import h5py
import hdf5plugin  # noqa: F401
import numpy as np

SRC = {'tworoom': '/tmp/latent-wm-data/tworoom.h5', 'pusht': '/tmp/latent-wm-data/pusht_expert_train.h5'}

if __name__ == '__main__':
    task = sys.argv[1]
    meta = np.load(f'/tmp/latent-wm-data/lowres/{task}_64/meta.npz')
    off, ln = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
    eps = np.sort(np.random.default_rng(0).choice(len(ln), 1000, replace=False))
    out = f'/tmp/latent-wm-data/native/{task}_224'
    os.makedirs(out, exist_ok=True)
    N = int(ln[eps].sum())
    new_off = np.concatenate([[0], np.cumsum(ln[eps])[:-1]])
    sel = np.concatenate([np.arange(off[e], off[e] + ln[e]) for e in eps])
    np.savez(f'{out}/meta.npz', ep_offset=new_off, ep_len=ln[eps], src_episode=eps, src_index=sel,
             **{k: meta[k][sel] for k in meta.files if meta[k].shape[:1] == (len(meta['action']),)})
    mm = np.lib.format.open_memmap(f'{out}/pixels.npy', mode='w+', dtype=np.uint8, shape=(N, 224, 224, 3))
    with h5py.File(SRC[task], 'r') as h:
        d = h['pixels']
        for k, e in enumerate(eps):
            mm[new_off[k]:new_off[k] + ln[e]] = d[off[e]:off[e] + ln[e]]
            if k % 100 == 0:
                print(k, flush=True)
    mm.flush()
    print('done', N)
