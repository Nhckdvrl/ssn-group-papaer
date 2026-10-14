"""E38: original PCSP Melting Pot wrapper, full CPU engine qualification.

Random actions are engine controls, never evidence about NPC personality.
Only Python's builder RNG is explicitly seeded; original game rules stay intact.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--substrate', default='commons_harvest__open')
    ap.add_argument('--seed', type=int, default=3801)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    os.environ.update(CUDA_VISIBLE_DEVICES='', TF_CPP_MIN_LOG_LEVEL='2', TF_ENABLE_ONEDNN_OPTS='0', JAX_PLATFORMS='cpu')
    root = args.source/'research/meltingpot'
    sys.path[:0] = [str(root/'upstream'), str(root/'scripts')]
    import numpy as np
    from mp_env import MeltingPotEnv
    from meltingpot import substrate
    import dmlab2d
    # Lazy substrate imports can consume Python RNG on the first construction.
    # Import the fixed config before the paired seed reset; record the actual
    # Lua/engine seed rather than assuming the wrapper's unused argument works.
    substrate.get_config(args.substrate)
    engine_builds = []; engine_starts = []
    original_lab2d = dmlab2d.Lab2d
    class LoggedNative:
        def __init__(self, native): self.native = native
        def __getattr__(self, name): return getattr(self.native, name)
        def start(self, episode, seed):
            engine_starts.append({'episode': episode, 'seed': int(seed)})
            return self.native.start(episode, seed=seed)
    def logged_lab2d(root_path, settings):
        engine_builds.append({'env_seed': settings.get('env_seed'),
            'settings_sha256': hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()})
        return LoggedNative(original_lab2d(root_path, settings))
    dmlab2d.Lab2d = logged_lab2d
    def primitive(value):
        if isinstance(value, np.ndarray): return primitive(value.tolist())
        if isinstance(value, np.generic): return primitive(value.item())
        if isinstance(value, bytes): return {'bytes_hex': value.hex(), 'utf8': value.decode('utf-8', errors='backslashreplace')}
        if isinstance(value, dict): return {k: primitive(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)): return [primitive(v) for v in value]
        return value
    summaries = []; records = []; start = time.monotonic()
    for repeat in range(2):
        random.seed(args.seed); np.random.seed(args.seed)
        rng = np.random.default_rng(args.seed)
        before = time.monotonic(); env = MeltingPotEnv(args.substrate, seed=args.seed)
        events = []; current_step = -1
        subscription = env._env.observables().events.subscribe(
            lambda event: events.append({'step': current_step, 'event': primitive(event)}))
        obs = env.reset(); initial = obs.copy(); hashes = [hashlib.sha256(obs.tobytes()).hexdigest()]
        actions = []; rewards = []; done = False
        while not done:
            current_step = len(actions)
            if current_step < 64: action = np.zeros(env.n_agents, dtype=np.int64)
            elif current_step < 128: action = np.ones(env.n_agents, dtype=np.int64)
            else: action = rng.integers(env.n_actions, size=env.n_agents, dtype=np.int64)
            assert np.all((0 <= action) & (action < env.n_actions))
            obs, reward, done = env.step(action)
            actions.append(action); rewards.append(reward)
            hashes.append(hashlib.sha256(obs.tobytes()).hexdigest())
            if len(actions) % 1000 == 0:
                print(json.dumps({'repeat': repeat, 'native_steps': len(actions), 'seconds': time.monotonic()-before}), flush=True)
        action_array = np.stack(actions); reward_array = np.stack(rewards)
        np.savez_compressed(args.out/f'episode_{repeat}.npz', actions=action_array, rewards=reward_array,
                            initial_rgb=initial, final_rgb=obs)
        (args.out/f'episode_{repeat}_hashes.json').write_text(json.dumps(hashes)+'\n')
        (args.out/f'episode_{repeat}_events.json').write_text(json.dumps(events, ensure_ascii=False)+'\n')
        summary = {'repeat': repeat, 'steps': len(actions), 'agents': env.n_agents, 'legal_actions': int(action_array.size),
            'n_actions': env.n_actions, 'rgb_shape': list(initial.shape), 'native_return_per_agent': reward_array.sum(0).tolist(),
            'events': len(events), 'rgb_changed_after_noop_window': hashes[0] != hashes[64],
            'rgb_changed_after_forward_window': hashes[64] != hashes[128],
            'seconds': time.monotonic()-before, 'engine_terminated': done}
        summaries.append(summary); records.append((action_array, reward_array, hashes, events))
        subscription.dispose(); env.close()
    a, b = records
    equality = {'actions_byte_equal': np.array_equal(a[0], b[0]), 'reward_byte_equal': np.array_equal(a[1], b[1]),
                'all_rgb_hashes_equal': a[2] == b[2], 'all_events_equal': a[3] == b[3]}
    result = {'substrate': args.substrate, 'seed': args.seed, 'source_sha': subprocess.check_output(
        ['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip(),
        'upstream_setup_sha256': hashlib.sha256((root/'upstream/setup.py').read_bytes()).hexdigest(),
        'versions': {k: importlib.metadata.version(k) for k in ['dmlab2d', 'tensorflow-cpu', 'numpy', 'chex', 'jax', 'torch']},
        'episodes': summaries, 'repeat_controls': equality, 'cloud_calls': 0, 'gpu_used': False,
        'scope': 'Engine qualification with fixed legal action controls; no trained NPC or personality result.',
        'seed_note': 'Original wrapper ignores seed argument. Config lazy imports are warmed before Python random is seeded; actual native seeds/settings recorded.',
        'engine_builds': engine_builds,
        'engine_starts': engine_starts,
        'world_or_reward_modified': False, 'wall_seconds': time.monotonic()-start,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.out/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
