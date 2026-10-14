#!/usr/bin/env python3
"""E25 frozen corrected-baseline policies: native utility and separate units."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--prefix', default='e25_30_')
    ap.add_argument('--embeddings', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs/e23_embedding_context/proper_pool.npy'))
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source / 'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv, N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE, N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic, TrajectoryEncoder
    from src.eval.consistency import _rollout_persona
    torch.set_num_threads(1)
    records = json.loads((args.source / 'research/data/personas/test_100_v3.json').read_text())
    ids = np.asarray([int(r['id']) for r in records])
    table = np.load(args.embeddings).astype(np.float32)
    vectors = torch.from_numpy(table[ids - 1])
    dump = lambda name, value: (args.out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    before = time.monotonic()
    policies, readers, targets, hashes = {}, {}, {}, {}
    for route in ['no', 'readout', 'full']:
        folder = args.runs / (args.prefix + route)
        policy = PCSPActorCritic(OBS_DIM_V3_LARGE, N_ACTIONS_V3)
        policy.load_state_dict(torch.load(folder / 'policy.pt', map_location='cpu', weights_only=True), strict=True)
        reader = TrajectoryEncoder(OBS_DIM_V3_LARGE, N_ACTIONS_V3)
        reader.load_state_dict(torch.load(folder / 'traj_encoder.pt', map_location='cpu', weights_only=True), strict=True)
        policy.eval().requires_grad_(False); reader.eval().requires_grad_(False)
        policies[route], readers[route] = policy, reader
        with torch.inference_mode(): targets[route] = policy.persona_proj(vectors)
        hashes[route] = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in ['policy.pt', 'traj_encoder.pt']}
    assert all(torch.equal(policies['no'].state_dict()[k], policies['readout'].state_dict()[k]) for k in policies['no'].state_dict())
    dump('manifest.json', {'source_sha': '5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
        'harness_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'asset_hashes': hashes,
        'embedding_sha256': hashlib.sha256(args.embeddings.read_bytes()).hexdigest(), 'test_ids': ids.tolist(),
        'mixed_world_seeds': [25011, 25012, 25013], 'joint_world_seed': 25031,
        'native_reward_includes_author_style': True, 'world_or_reward_changed': False, 'cloud_calls': 0})

    def mixed_rollout(policy, rows, world_seed):
        actual = len(rows); padded = list(rows)
        while len(padded) < N_AGENTS: padded.append(rows[len(padded) % actual])
        env = MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(r) for r in padded], max_steps=200)
        env.reset(seed=world_seed); torch.manual_seed(world_seed + 1000003)
        e = torch.from_numpy(table[[int(r['id']) - 1 for r in padded]])
        observations, actions = [], []
        rewards = np.zeros(N_AGENTS)
        for cycle in range(200):
            obs = np.stack([env.observe(a) for a in env.possible_agents])
            with torch.inference_mode(): selected = torch.distributions.Categorical(logits=policy.action_logits(torch.from_numpy(obs), e)).sample().numpy()
            observations.append(obs); actions.append(selected)
            for i, (agent, action) in enumerate(zip(env.possible_agents, selected)):
                assert env.agent_selection == agent
                env.step(int(action)); rewards[i] += float(env.rewards[agent])
        result = {'obs': np.stack(observations).transpose(1, 0, 2)[:actual],
            'actions': np.stack(actions).T[:actual], 'rewards': rewards[:actual],
            'final_needs': env.needs[:actual].copy(), 'final_positions': env.positions[:actual].copy()}
        env.close()
        return result

    def decode(route, obs, actions, actual_ids):
        predicted, top3 = [], []
        for offset in range(0, len(actual_ids), 32):
            with torch.inference_mode():
                z = readers[route](torch.from_numpy(obs[offset:offset+32]), torch.from_numpy(actions[offset:offset+32]))
                ranking = (z @ targets[route].T).topk(3, dim=-1).indices.numpy()
            predicted.extend(ids[ranking[:, 0]].tolist())
            top3.extend([int(pid in ids[rank]) for pid, rank in zip(actual_ids[offset:offset+32], ranking)])
        correct = np.asarray(predicted) == np.asarray(actual_ids)
        return {'top1': float(correct.mean()), 'top3': float(np.mean(top3)), 'correct': correct.astype(int).tolist(),
            'predicted_ids': predicted, 'actual_ids': list(map(int, actual_ids)), 'candidate_count': len(ids)}

    mixed, summary = {}, {}
    for route in ['no', 'readout', 'full']:
        if route == 'readout':
            # Equality is checked above, so the native rollout is shared exactly.
            mixed[route] = mixed['no']
        else:
            parts = []; actual_ids = []; worlds = []
            for seed in [25011, 25012, 25013]:
                rows = [records[int(i)] for i in np.random.default_rng(seed).permutation(len(records))]
                for offset in range(0, len(rows), N_AGENTS):
                    batch = rows[offset:offset+N_AGENTS]
                    parts.append(mixed_rollout(policies[route], batch, seed + offset*100))
                    actual_ids.extend(int(r['id']) for r in batch); worlds.extend([seed]*len(batch))
            mixed[route] = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
            mixed[route].update(ids=np.asarray(actual_ids), world_seeds=np.asarray(worlds))
            np.savez_compressed(args.out / f'{route}_mixed.npz', **mixed[route])
        data = mixed[route]
        summary[route] = {'native_reward_mean': float(data['rewards'].mean()),
            'own200_reader': decode(route, data['obs'], data['actions'], data['ids'])}
        dump('summary.json', summary)
        print(json.dumps({'phase': 'mixed', 'route': route, 'reward': summary[route]['native_reward_mean'],
            'reader_top1': summary[route]['own200_reader']['top1']}), flush=True)

    # Source consistency evaluator: homogeneous 16-persona population, sequential
    # AEC, all-actor first200 frames. Its unit is kept separate from own200 above.
    joint_data = {}
    for route in ['no', 'readout', 'full']:
        if route == 'readout': joint_data[route] = joint_data['no']
        else:
            obs_parts, action_parts = [], []
            for index, record in enumerate(records):
                torch.manual_seed(25031 + index + 1000003)
                data = _rollout_persona(policies[route], vectors[index:index+1], PersonaConfig.from_dict(record), 1,
                    torch.device('cpu'), seed_offset=25031+index, n_agents=N_AGENTS,
                    env_factory=lambda personas: MiniInzoiV3LargeEnv(personas=personas, max_steps=200))[0]
                obs_parts.append(data['obs_seq'][:200]); action_parts.append(data['act_seq'][:200])
            joint_data[route] = (np.asarray(obs_parts, dtype=np.float32), np.asarray(action_parts, dtype=np.int64))
            np.savez_compressed(args.out / f'{route}_joint.npz', obs=joint_data[route][0], actions=joint_data[route][1], ids=ids)
        summary[route]['source_joint_prefix200_reader'] = decode(route, *joint_data[route], ids)
        dump('summary.json', summary)
        print(json.dumps({'phase': 'joint', 'route': route,
            'reader_top1': summary[route]['source_joint_prefix200_reader']['top1']}), flush=True)
    delta = mixed['full']['rewards'] - mixed['no']['rewards']
    per_id = np.asarray([delta[mixed['no']['ids'] == pid].mean() for pid in ids])
    rng = np.random.default_rng(252525)
    boot = [rng.choice(per_id, len(per_id), replace=True).mean() for _ in range(2000)]
    summary['controls'] = {'no_readout_policy_byte_identical': True, 'no_readout_native_byte_identical': True,
        'full_minus_no_reward': float(delta.mean()), 'paired_persona_cluster95': np.quantile(boot, [.025, .975]).tolist(),
        'training_seed_count': 1, 'iterations': 30, 'independent_semantic_validity_established': False,
        'wall_seconds': time.monotonic()-before, 'cloud_calls': 0, 'scientific_increment': 0}
    dump('summary.json', summary)


if __name__ == '__main__': main()
