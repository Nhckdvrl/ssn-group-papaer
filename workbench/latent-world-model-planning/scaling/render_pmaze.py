"""Visual PointMaze from the OGBench pointmaze-<size>-navigate-v0 dataset (established state-based data).

Each logged qpos is rendered with a fixed global top-down camera (whole maze visible, goal marker
hidden), at 224px then INTER_AREA to 64px exactly like the other tasks. Output follows the
lowres/<task>_64 layout used by wm.GPUData: pixels.npy + meta.npz (action, proprio=qpos, ep_offset, ep_len).
"""
import os
os.environ.setdefault('MUJOCO_GL', 'egl')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import sys
from multiprocessing import Pool

import numpy as np

SIZE = sys.argv[1] if len(sys.argv) > 1 else 'medium'
SRC = f'/tmp/latent-wm-data/ogbench/pointmaze-{SIZE}-navigate-v0.npz'
OUT = f'/tmp/latent-wm-data/lowres/pmaze{SIZE}_64'


def make_renderer():
    import gymnasium as gym
    import mujoco
    import ogbench  # noqa: F401
    env = gym.make(f'pointmaze-{SIZE}-v0', render_mode='rgb_array', width=224, height=224)
    env.reset(seed=0)
    u = env.unwrapped
    m = u.model
    tid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, 'target')
    m.geom_rgba[tid, 3] = 0.0
    m.geom_matid[tid] = -1
    blocks = [i for i in range(m.ngeom) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i) or '').startswith('block')]
    mujoco.mj_forward(m, u.data)
    xy = u.data.geom_xpos[blocks, :2]
    lo, hi = xy.min(0), xy.max(0)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0]
    cam.distance = 1.05 * max(hi - lo) + 4
    cam.elevation, cam.azimuth = -90, 90
    r = mujoco.Renderer(m, 224, 224)
    return u, r, cam


def render_states(qpos):
    import cv2
    u, r, cam = make_renderer()
    out = np.empty((len(qpos), 64, 64, 3), np.uint8)
    for k, q in enumerate(qpos):
        u.set_state(q, np.zeros(2))
        r.update_scene(u.data, camera=cam)
        out[k] = cv2.resize(r.render(), (64, 64), interpolation=cv2.INTER_AREA)
    return out


def work(args):
    s, q = args
    return s, render_states(q)


if __name__ == '__main__':
    d = np.load(SRC)
    qpos, act = d['qpos'].astype(np.float64), d['actions'].astype(np.float32)
    term = d['terminals'].astype(bool)
    ends = np.nonzero(term)[0]
    starts = np.concatenate([[0], ends[:-1] + 1])
    ep_len = ends - starts + 1
    os.makedirs(OUT, exist_ok=True)
    np.savez(f'{OUT}/meta.npz', action=act, proprio=qpos.astype(np.float32), qvel=d['qvel'],
             ep_offset=starts.astype(np.int64), ep_len=ep_len.astype(np.int32))
    mm = np.lib.format.open_memmap(f'{OUT}/pixels.npy', mode='w+', dtype=np.uint8, shape=(len(qpos), 64, 64, 3))
    chunks = [(s, qpos[s:s + 20000]) for s in range(0, len(qpos), 20000)]
    with Pool(12) as p:
        for i, (s, arr) in enumerate(p.imap_unordered(work, chunks)):
            mm[s:s + len(arr)] = arr
            print(i, len(chunks), flush=True)
    mm.flush()
    print('done', len(qpos), 'episodes', len(starts))
    os._exit(0)
