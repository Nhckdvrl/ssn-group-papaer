"""E38 complete native episodes, raw consequences and state-fixed responses.

Runs the original stochastic CNN policy and original world without action priors.
Readout diagnostics never enter the policy's RGB observation or game reward.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import socket
import subprocess
import sys
import time


FOCAL = ['cooperative_sustainer', 'selfish_harvester', 'cautious_observer',
         'aggressive_zapper', 'fast_mover', 'spinner']
PARTNERS = ['reciprocator', 'explorer', 'territorial_defender',
            'risk_seeking_raider', 'cleaner_helper', 'free_rider']
WORLD_SEEDS = [38011, 38012, 38013]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--shards', type=int, default=8)
    ap.add_argument('--pilot', action='store_true')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                      TF_CPP_MIN_LOG_LEVEL='2', JAX_PLATFORMS='cpu')
    root = args.source/'research/meltingpot'
    sys.path[:0] = [str(root/'upstream'), str(root/'scripts'), str(args.source/'research')]
    import numpy as np
    import torch
    from cnn_film_policy import PCSPCnnFiLMActorCritic
    from src.models.trajectory_encoder import TrajectoryEncoder
    from mp_env import MeltingPotEnv
    from meltingpot import substrate
    import dmlab2d
    torch.set_num_threads(1)
    device = torch.device('cuda')
    substrate.get_config('commons_harvest__open')  # warm lazy imports before seed

    builds, starts = [], []
    original_lab = dmlab2d.Lab2d

    class LoggedNative:
        def __init__(self, env): self.native = env
        def __getattr__(self, name): return getattr(self.native, name)
        def start(self, episode, seed):
            starts.append({'episode': episode, 'seed': int(seed)})
            return self.native.start(episode, seed=seed)

    def logged_lab(root_path, settings):
        builds.append({'env_seed': settings.get('env_seed'),
                       'settings_sha256': hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()})
        return LoggedNative(original_lab(root_path, settings))

    dmlab2d.Lab2d = logged_lab

    def primitive(x):
        if isinstance(x, bytes): return x.decode('utf-8', errors='backslashreplace')
        if isinstance(x, np.ndarray): return primitive(x.tolist())
        if isinstance(x, np.generic): return primitive(x.item())
        if isinstance(x, dict): return {str(k): primitive(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)): return [primitive(v) for v in x]
        return x

    def global_text_env(env):
        """Locate existing native GLOBAL.TEXT without enabling debug observations."""
        seen = set()
        while id(env) not in seen:
            seen.add(id(env))
            try:
                obs = env.observation()
                if isinstance(obs, dict) and 'GLOBAL.TEXT' in obs:
                    return env
            except (AttributeError, TypeError):
                pass
            if hasattr(env, '_env'): env = env._env
            elif hasattr(env, 'native'): env = env.native
            else: break
        raise RuntimeError('Original GLOBAL.TEXT observation not located')

    def decode_event(event):
        name, data = primitive(event)
        if data and data[0] == 'dict':
            payload = dict(zip(data[1::2], data[2::2]))
        else:
            payload = {'raw': data}
        return {'name': name, 'payload': payload}

    meta_path = root/'personas/personas_v0.json'
    meta = json.loads(meta_path.read_text())
    model_jobs = [(kind, seed, mode) for kind in ['correct', 'strong']
                  for seed in [1, 2, 3, 4, 5] for mode in ['full', 'no_consist']]
    if args.pilot: model_jobs = [('correct', 1, 'full')]
    else: model_jobs = [j for i, j in enumerate(model_jobs) if i % args.shards == args.shard]
    manifest = {'source_sha': subprocess.check_output(['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip(),
                'host': socket.gethostname(), 'visible_gpu': os.environ.get('CUDA_VISIBLE_DEVICES'),
                'gpu': torch.cuda.get_device_name(0), 'python': sys.executable,
                'script_sha256': sha(__file__), 'personas_sha256': sha(meta_path),
                'model_jobs': model_jobs, 'shard': args.shard, 'shards': args.shards,
                'focal': FOCAL, 'partners': PARTNERS, 'world_seeds': WORLD_SEEDS,
                'world_or_reward_modified': False, 'paid_api_calls': 0,
                'seed_scope': 'Python, NumPy, torch and actual native starts recorded; byte-paired native worlds not assumed.',
                'scope': 'Original input personas, native executed actions and consequences; CNN has no linguistic intention output.'}
    (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    episodes = []
    start = time.monotonic()
    for kind, train_seed, mode in model_jobs:
        model_dir = args.runs/f'e38_{kind}_s{train_seed}_{mode}'
        config = json.loads((model_dir/'config.json').read_text())
        cache_path = Path(config['persona_cache'])
        cache = torch.load(cache_path, map_location='cpu', weights_only=False)
        ids = cache['ids']
        embeddings = cache['embeddings'].float().to(device)
        policy = PCSPCnnFiLMActorCritic(n_actions=8, feat_dim=config['feat_dim'],
                    persona_dim=config['persona_dim'], lora_r=config['lora_r'], in_hw=88).to(device)
        policy.load_state_dict(torch.load(model_dir/'policy.pt', map_location=device, weights_only=True))
        policy.eval()
        eta = TrajectoryEncoder(obs_dim=config['feat_dim'], n_actions=8,
                    hidden_dim=config['traj_hidden'], output_dim=config['persona_dim']).to(device)
        eta.load_state_dict(torch.load(model_dir/'traj_encoder.pt', map_location=device, weights_only=True))
        eta.eval()
        with torch.inference_mode(): all_z = policy.persona_proj(embeddings)
        train_indices = [ids.index(x) for x in meta['splits']['train']]
        model_hashes = {'policy_sha256': sha(model_dir/'policy.pt'), 'eta_sha256': sha(model_dir/'traj_encoder.pt'),
                        'embedding_sha256': sha(cache_path), 'model_dir': str(model_dir)}
        for focal in FOCAL[:1] if args.pilot else FOCAL:
            for wi, world_seed in enumerate(WORLD_SEEDS[:1] if args.pilot else WORLD_SEEDS):
                begin = time.monotonic()
                random.seed(world_seed); np.random.seed(world_seed); torch.manual_seed(world_seed)
                persona_ids = PARTNERS.copy()
                focal_slot = wi % 7
                persona_ids.insert(focal_slot, focal)
                emb = embeddings[[ids.index(x) for x in persona_ids]]
                directory = args.out/f'{kind}_s{train_seed}_{mode}_{focal}_w{world_seed}'
                directory.mkdir()
                env = MeltingPotEnv('commons_harvest__open', seed=world_seed)
                timestep = [None]
                sub_ts = env._env.observables().timestep.subscribe(lambda ts: timestep.__setitem__(0, ts))
                step = -1
                events = []
                sub_ev = env._env.observables().events.subscribe(lambda event: events.append({'step': step, **decode_event(event)}))
                obs = env.reset()
                native = global_text_env(env._env)
                actions, rewards, ready, apples = [], [], [], []
                frame_steps, world_frames, focal_frames, response = [], [], [], []
                feature_trace = []
                current_features = [None]
                def hook(module, inp, out): current_features[0] = out.detach()
                handle = policy.cnn.register_forward_hook(hook)
                done = False
                with torch.inference_mode():
                    while not done:
                        step = len(actions)
                        before = timestep[0].observation
                        rr = [float(x['READY_TO_SHOOT']) for x in before]
                        text = str(primitive(native.observation()['GLOBAL.TEXT']))
                        apples.append(text.count('A'))
                        action, _, _ = policy.get_action(torch.from_numpy(obs).to(device), emb)
                        if step < 200: feature_trace.append(current_features[0].cpu().numpy())
                        if step % 100 == 0:
                            frame_steps.append(step)
                            world_frames.append(before[0]['WORLD.RGB'].copy())
                            focal_frames.append(obs[focal_slot].copy())
                            feat = current_features[0][focal_slot:focal_slot+1].expand(len(ids), -1)
                            logits, _ = policy._trunk(feat, all_z)
                            response.append(logits.double().softmax(-1).cpu().numpy())
                        action = action.cpu().numpy()
                        assert np.all((action >= 0) & (action < env.n_actions))
                        obs, reward, done = env.step(action)
                        actions.append(action); rewards.append(reward); ready.append(rr)
                    features = torch.from_numpy(np.stack(feature_trace).transpose(1, 0, 2)).to(device)
                    acts = torch.from_numpy(np.stack(actions[:len(feature_trace)]).T).to(device)
                    traj = eta(features, acts)
                    sim = traj @ all_z[train_indices].T
                    retrieval = sim.cpu().numpy()
                handle.remove()
                a = np.stack(actions); r = np.stack(rewards); ready = np.asarray(ready)
                consumed = np.zeros(7, dtype=int); hits = np.zeros(7, dtype=int); received = np.zeros(7, dtype=int)
                for e in events:
                    data = e['payload']
                    if e['name'] == 'edible_consumed': consumed[int(data['player_index'])-1] += 1
                    elif e['name'] == 'zap':
                        hits[int(data['source'])-1] += 1; received[int(data['target'])-1] += 1
                counts = np.stack([(a == i).sum(0) for i in range(8)], -1)
                fire_ready = ((a == 7) & (ready > 0)).sum(0)
                row = {'kind': kind, 'train_seed': train_seed, 'mode': mode, 'world_seed': world_seed,
                       'focal': focal, 'focal_slot': focal_slot, 'persona_ids': persona_ids,
                       'steps': len(a), 'return_per_agent': r.sum(0).tolist(), 'team_return': float(r.sum()),
                       'apples_consumed': consumed.tolist(), 'zap_hits': hits.tolist(), 'zap_received': received.tolist(),
                       'action_counts': counts.tolist(), 'ready_fire_attempts': fire_ready.tolist(),
                       'initial_apples': int(apples[0]), 'final_apples_before_action': int(apples[-1]),
                       'mean_available_apples': float(np.mean(apples)),
                       'raw_return_equals_apple_events': np.array_equal(r.sum(0), consumed),
                       'engine_terminated': done, 'legal_actions': int(a.size), 'seconds': time.monotonic()-begin,
                       'internal_retrieval_train_ids': meta['splits']['train'],
                       'internal_retrieval_top1': [meta['splits']['train'][i] for i in retrieval.argmax(-1)],
                       'heldout_retrieval_note': 'Heldout focal is absent from train candidate pool; no top1 correctness claim.',
                       'engine_build': builds[-1], 'engine_start': starts[-1], 'raw': str(directory), **model_hashes}
                np.savez_compressed(directory/'native.npz', actions=a, rewards=r, ready_to_shoot=ready,
                    available_apples=np.asarray(apples), frame_steps=np.asarray(frame_steps),
                    world_rgb=np.stack(world_frames), focal_rgb=np.stack(focal_frames),
                    state_fixed_all_persona_probabilities=np.stack(response),
                    first_200_features=np.stack(feature_trace), eta_similarity=retrieval)
                (directory/'events.json').write_text(json.dumps(events, ensure_ascii=False)+'\n')
                (directory/'summary.json').write_text(json.dumps(row, indent=2)+'\n')
                episodes.append(row)
                with (args.out/'progress.jsonl').open('a') as f: f.write(json.dumps(row)+'\n')
                print(json.dumps({'kind':kind, 'train_seed':train_seed, 'mode':mode, 'focal':focal,
                      'world_seed':world_seed, 'steps':len(a), 'team_return':row['team_return'],
                      'event_reward_equal':row['raw_return_equals_apple_events'], 'seconds':row['seconds']}), flush=True)
                sub_ts.dispose(); sub_ev.dispose(); env.close()
    result = {'episodes': episodes, 'episode_count': len(episodes), 'wall_seconds': time.monotonic()-start,
              'manifest': manifest, 'cloud_calls': 0, 'all_engine_terminated': all(x['engine_terminated'] for x in episodes)}
    (args.out/'summary.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__': main()
