"""Downsample LeWM HDF5 datasets to low-res uint8 arrays for fast GPU-resident training.
Output dir: /tmp/latent-wm-data/lowres/<task>_<res>/ with pixels.npy (N,res,res,3) + meta.npz."""
import argparse, os, time
import numpy as np
from multiprocessing import Pool

def work(args):
    path, s, e, res = args
    import hdf5plugin, h5py, cv2
    with h5py.File(path, 'r') as h:
        px = h['pixels'][s:e]
    return s, np.stack([cv2.resize(im, (res, res), interpolation=cv2.INTER_AREA) for im in px])

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--task', required=True)
    p.add_argument('--res', type=int, default=64)
    p.add_argument('--workers', type=int, default=20)
    a = p.parse_args()
    src = {'tworoom': '/tmp/latent-wm-data/tworoom.h5', 'pusht': '/tmp/latent-wm-data/pusht_expert_train.h5'}[a.task]
    out = f'/tmp/latent-wm-data/lowres/{a.task}_{a.res}'
    os.makedirs(out, exist_ok=True)
    import hdf5plugin, h5py
    with h5py.File(src, 'r') as h:
        n = h['pixels'].shape[0]
        meta = {k: h[k][:] for k in h.keys() if k != 'pixels' and h[k].ndim <= 2 and h[k].dtype != object}
    np.savez(f'{out}/meta.npz', **meta)
    mm = np.lib.format.open_memmap(f'{out}/pixels.npy', mode='w+', dtype=np.uint8, shape=(n, a.res, a.res, 3))
    chunks = [(src, s, min(s + 2000, n), a.res) for s in range(0, n, 2000)]
    t = time.time()
    with Pool(a.workers) as pool:
        for i, (s, arr) in enumerate(pool.imap_unordered(work, chunks)):
            mm[s:s + len(arr)] = arr
            if i % 50 == 0:
                print(f'{i}/{len(chunks)} {time.time()-t:.0f}s', flush=True)
    mm.flush()
    print('done', n, time.time() - t)

if __name__ == '__main__':
    main()
