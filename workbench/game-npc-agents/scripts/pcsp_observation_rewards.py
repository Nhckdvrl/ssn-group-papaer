"""Reconstruct only source immediate reward inputs, not an entire hidden world."""
import argparse
import json
from pathlib import Path
import sys
import time

import numpy as np


def reward_vector(env, actor_index, observation, *, target_C=None, actions=None):
    """Call the original reward-bearing action function on the observed fields.

    In the pinned v3 source, reward uses own needs, preferred actions, own
    Big Five and the first nearby peer's Big Five. Other hidden needs/time
    are not used. This routine cannot simulate future transitions.
    """
    own = env.personas[actor_index]
    old_C = own.big_five['C']; old_bf = env._bf_vecs[actor_index].copy()
    positions = np.empty_like(env.positions)
    positions[actor_index] = np.rint(observation[:2] * (env.grid_size - 1)).astype(np.int64)
    cursor = 24
    for peer in range(env.n_agents):
        if peer == actor_index: continue
        positions[peer] = np.rint(observation[cursor:cursor+2] * (env.grid_size - 1)).astype(np.int64)
        cursor += 3
    assert cursor == len(observation)
    needs = np.full_like(env.needs, .7)
    needs[actor_index] = observation[3:11]
    selected = list(range(env.n_actions)) if actions is None else list(actions)
    values = []
    try:
        if target_C is not None:
            own.big_five['C'] = target_C; env._bf_vecs[actor_index] = own.bf_vec
        for action in selected:
            env.positions[:] = positions; env.needs[:] = needs
            env.last_actions.fill(0); env.repeat_counts.fill(0); env.novelty_steps.fill(0)
            assert env.action_space(env.possible_agents[actor_index]).contains(int(action))
            values.append(float(env._apply_action(actor_index, int(action))))
    finally:
        own.big_five['C'] = old_C; env._bf_vecs[actor_index] = old_bf
    return np.asarray(values, dtype=np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source / 'research'))
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv, N_AGENTS
    start = time.monotonic()
    train = json.loads((args.source / 'research/data/personas/train_400_v3.json').read_text())
    with np.load(args.runs / 'e34_cpu_s42_full/first_rollout.npz') as data:
        observations = data['obs']; actions = data['actions']; expected = data['rewards']
    assert len(observations) == 8 * 200 * N_AGENTS
    rng = np.random.default_rng(42); errors = []; examples = []
    for episode in range(8):
        chosen = rng.choice(len(train), N_AGENTS, replace=False)
        env = MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(train[int(i)]) for i in chosen], max_steps=200)
        env.reset(seed=episode)
        for cycle in range(200):
            for actor in range(N_AGENTS):
                index = episode * 200 * N_AGENTS + cycle * N_AGENTS + actor
                actual = reward_vector(env, actor, observations[index], actions=[actions[index]])[0]
                error = abs(actual - float(expected[index])); errors.append(error)
                if len(examples) < 5: examples.append({'index': index, 'source_reward': float(expected[index]), 'reconstructed': actual})
        env.close()
    result = {'source_sha': '5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
         'native_transitions_checked': len(errors), 'maximum_abs_error': max(errors),
         'mean_abs_error': float(np.mean(errors)), 'examples': examples,
         'scope': 'Immediate source reward only; not complete world-state recovery or long-term utility.',
         'wall_seconds': time.monotonic()-start, 'cloud_calls': 0}
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)
    assert max(errors) < 1e-6, 'Implementation mismatch: inspect pinned source dependencies'


if __name__ == '__main__':
    main()
