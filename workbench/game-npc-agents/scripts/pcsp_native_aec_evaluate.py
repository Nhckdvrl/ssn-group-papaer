"""E34 canonical utility: fresh observation for each source AEC action."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--policy-prefix', type=Path, required=True)
    ap.add_argument('--embeddings', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs/e23_embedding_context/proper_pool.npy'))
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source / 'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv, N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE, N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    from src.eval.consistency import _rollout_persona
    torch.set_num_threads(1)
    start = time.monotonic()
    dump = lambda name, obj: (args.out / name).write_text(json.dumps(obj, indent=2) + '\n')
    records = json.loads((args.source / 'research/data/personas/test_100_v3.json').read_text())
    table = np.load(args.embeddings).astype(np.float32)
    hashes = {}; summary = {}; cohorts = []; source_controls = {}
    world_seeds = [34011, 34012, 34013]
    def collect(policy, rows, seed):
        configs = [PersonaConfig.from_dict(r) for r in rows]
        env = MiniInzoiV3LargeEnv(personas=configs, max_steps=200)
        env.reset(seed=seed); torch.manual_seed(seed + 1000003)
        e = torch.from_numpy(table[[int(r['id']) - 1 for r in rows]])
        obs = np.empty((N_AGENTS, 200, OBS_DIM_V3_LARGE), dtype=np.float32)
        actions = np.empty((N_AGENTS, 200), dtype=np.int64)
        rewards = np.zeros(N_AGENTS); preferred = np.zeros(N_AGENTS); critical = np.zeros(N_AGENTS)
        for cycle in range(200):
            for index, agent in enumerate(env.possible_agents):
                assert env.agent_selection == agent
                current = env.observe(agent).copy(); obs[index, cycle] = current
                with torch.inference_mode():
                    action, _, _ = policy.get_action(torch.from_numpy(current).unsqueeze(0), e[index:index+1])
                action = int(action.item()); actions[index, cycle] = action
                env.step(action); rewards[index] += float(env.rewards[agent])
                preferred[index] += int(action in rows[index]['preferred_actions'])
            critical += (env.needs < .2).mean(-1)
        result = {'obs': obs, 'actions': actions, 'rewards': rewards,
                  'preferred_rate': preferred / 200, 'critical_fraction': critical / 200,
                  'final_needs': env.needs.copy(), 'final_positions': env.positions.copy()}
        env.close(); return result
    for route in ['no', 'full']:
        folder = Path(str(args.policy_prefix) + route)
        policy = PCSPActorCritic(OBS_DIM_V3_LARGE, N_ACTIONS_V3)
        policy.load_state_dict(torch.load(folder / 'policy.pt', map_location='cpu', weights_only=True), strict=True)
        policy.eval().requires_grad_(False)
        hashes[route] = hashlib.sha256((folder / 'policy.pt').read_bytes()).hexdigest()
        first = records[0]; check_seed = 34001
        check = collect(policy, [first] * N_AGENTS, check_seed)
        torch.manual_seed(check_seed + 1000003)
        source = _rollout_persona(policy, torch.from_numpy(table[first['id']-1]).unsqueeze(0),
                    PersonaConfig.from_dict(first), 1, torch.device('cpu'), seed_offset=check_seed,
                    n_agents=N_AGENTS, env_factory=lambda personas: MiniInzoiV3LargeEnv(personas=personas, max_steps=200))[0]
        assert np.array_equal(check['obs'].transpose(1, 0, 2).reshape(-1, OBS_DIM_V3_LARGE), source['obs_seq'])
        assert np.array_equal(check['actions'].T.reshape(-1), source['act_seq'])
        source_controls[route] = {'source_helper_obs_actions_byte_identical': True, 'frames': len(source['act_seq'])}
        parts = []; actual_ids = []; seeds = []
        for world_seed in world_seeds:
            rows = [records[int(i)] for i in np.random.default_rng(world_seed).permutation(len(records))]
            for offset in range(0, len(rows), N_AGENTS):
                group = list(rows[offset:offset+N_AGENTS]); actual = len(group)
                padded = list(group)
                while len(padded) < N_AGENTS: padded.append(group[len(padded) % actual])
                native_seed = world_seed + offset * 100
                data = collect(policy, padded, native_seed)
                parts.append({k: v[:actual] for k, v in data.items()})
                actual_ids.extend(int(r['id']) for r in group); seeds.extend([world_seed] * actual)
                if route == 'no': cohorts.append({'world_seed': world_seed, 'offset': offset,
                     'native_seed': native_seed, 'actual': actual, 'padded_ids': [r['id'] for r in padded]})
        data = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
        data.update(ids=np.asarray(actual_ids), world_seeds=np.asarray(seeds))
        assert data['obs'].shape == (300, 200, OBS_DIM_V3_LARGE)
        np.savez_compressed(args.out / f'{route}_native.npz', **data)
        summary[route] = {'native_reward_mean': float(data['rewards'].mean()),
             'preferred_rate': float(data['preferred_rate'].mean()), 'critical_fraction': float(data['critical_fraction'].mean()),
             'mean_final_needs': data['final_needs'].mean(0).tolist(),
             'per_persona_reward': {str(pid): float(data['rewards'][data['ids'] == pid].mean()) for pid in sorted(set(actual_ids))}}
        print(json.dumps({'route': route, 'native_reward_mean': summary[route]['native_reward_mean'],
                          'wall_seconds': time.monotonic() - start}), flush=True)
    dump('manifest.json', {'source_sha': '5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
         'policy_hashes': hashes, 'policy_prefix': str(args.policy_prefix),
         'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'embedding_sha256': hashlib.sha256(args.embeddings.read_bytes()).hexdigest(),
         'world_seeds': world_seeds, 'cohorts': cohorts, 'source_replay_controls': source_controls,
         'observation_timing': 'fresh observation immediately before every native AEC actor action',
         'world_or_reward_changed': False, 'cloud_calls': 0})
    dump('summary.json', {'policies': summary, 'wall_seconds': time.monotonic()-start,
         'training_seed_count': 1, 'source_replay_controls': source_controls,
         'full_minus_no_reward': summary['full']['native_reward_mean'] - summary['no']['native_reward_mean'],
         'scientific_increment': 0})


if __name__ == '__main__':
    main()
