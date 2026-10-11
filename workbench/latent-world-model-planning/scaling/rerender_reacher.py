"""Re-render the Reacher dataset frames with the evaluation simulator from logged qpos.

The released reacher.h5 frames use a different floor texture than the current stable-worldmodel
Reacher env (checker vs grid), so training on them and evaluating in the env would add a visual
domain shift. Reacher images depend only on qpos (target invisible), so every frame is re-rendered
at 224px and downsampled with INTER_AREA exactly like the evaluator does.
"""
import os
os.environ.setdefault('MUJOCO_GL', 'egl')
os.environ.setdefault('OMP_NUM_THREADS', '1')
from multiprocessing import Pool
import numpy as np

OUT = '/tmp/latent-wm-data/lowres/reacher_64/pixels.npy'


def work(args):
    s, e = args
    import cv2
    from eval_plan import make_env
    m = np.load('/tmp/latent-wm-data/lowres/reacher_64/meta.npz')
    q = m['qpos'][s:e]
    env = make_env('reacher')
    env.reset(seed=0)
    out = np.empty((e - s, 64, 64, 3), np.uint8)
    for k in range(e - s):
        env.set_state(q[k], np.zeros(2))
        out[k] = cv2.resize(np.asarray(env.render()), (64, 64), interpolation=cv2.INTER_AREA)
    return s, out


if __name__ == '__main__':
    n = len(np.load('/tmp/latent-wm-data/lowres/reacher_64/meta.npz')['qpos'])
    mm = np.load(OUT, mmap_mode='r+')
    chunks = [(s, min(s + 20000, n)) for s in range(0, n, 20000)]
    with Pool(12) as p:
        for i, (s, arr) in enumerate(p.imap_unordered(work, chunks)):
            mm[s:s + len(arr)] = arr
            if i % 10 == 0:
                print(i, len(chunks), flush=True)
    mm.flush()
    print('done')
    os._exit(0)
