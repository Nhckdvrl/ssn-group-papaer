"""E36 exploratory response geometry; no threshold-based scientific verdict."""
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
    ap.add_argument('--iteration', type=int, choices=[30, 100, 300], default=30)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source / 'research'))
    import numpy as np
    import torch
    from src.training.pcsp_trainer import PCSPActorCritic
    from src.env.v3_constants import OBS_DIM_V3_LARGE, N_ACTIONS_V3
    torch.set_num_threads(1)
    start = time.monotonic()
    with np.load(args.runs / 'e25_30_evaluation/no_mixed.npz') as data:
        ids = np.repeat(data['ids'], 4)
        observations = torch.from_numpy(data['obs'][:, [0, 20, 100, 199]].reshape(-1, OBS_DIM_V3_LARGE))
        worlds = np.repeat(data['world_seeds'], 4)
    canonical = np.load(args.runs / 'e26_semantic_codes/canonical.npy').astype(np.float32)
    reverse = np.load(args.runs / 'e26_semantic_codes/reverse_clauses.npy').astype(np.float32)
    repeat = np.load(args.runs / 'e26_semantic_codes/canonical_repeat.npy').astype(np.float32)
    codes_path = args.runs / 'e33_codes'
    codes = np.load(codes_path / 'vectors.npy')
    names = json.loads((codes_path / 'texts.json').read_text())['names']
    modes = {'alias': {'pids': list(range(401, 501)), 'e0': canonical[400:500], 'e1': reverse[400:500]},
             'C_edit': {'pids': [401, 421, 441, 461, 481]}}
    for key, level in [('e0', 'low'), ('e1', 'high')]:
        modes['C_edit'][key] = np.stack([codes[names.index(f'plain_{pid}_{level}')] for pid in modes['C_edit']['pids']])
    def actor(policy, obs, z):
        return policy.actor_head(policy.actor_b3(policy.actor_b2(policy.actor_b1(obs, z), z), z))
    def probabilities(policy, obs, z):
        return torch.cat([actor(policy, obs[i:i+1024], z[i:i+1024]).softmax(-1)
                          for i in range(0, len(obs), 1024)])
    roundoff = {'negative_js_count': 0, 'minimum_unclamped_js': 0.}
    def js(p, q):
        m = (p + q) / 2
        value = .5 * ((p * (p.clamp_min(1e-12).log() - m.clamp_min(1e-12).log())).sum(-1)
                     + (q * (q.clamp_min(1e-12).log() - m.clamp_min(1e-12).log())).sum(-1))
        roundoff['negative_js_count'] += int((value < 0).sum())
        roundoff['minimum_unclamped_js'] = min(roundoff['minimum_unclamped_js'], float(value.min()))
        return value.clamp_min(0)
    summaries = {}; arrays = {}; hashes = {}; numerical = {}
    with torch.inference_mode():
        for seed in [42, 43, 44]:
            policies = {}
            for route, source_route in [('no', 'no_consist'), ('full', 'full')]:
                folder = args.runs / f'e34_cpu_s{seed}_{source_route}' / f'checkpoint_{args.iteration:04d}'
                meta = json.loads((folder / 'manifest.json').read_text())
                assert meta['seed'] == seed and meta['completed_iterations'] == args.iteration
                policy = PCSPActorCritic(OBS_DIM_V3_LARGE, N_ACTIONS_V3)
                policy.load_state_dict(torch.load(folder / 'policy.pt', map_location='cpu', weights_only=True))
                policy.eval().requires_grad_(False); policies[route] = policy
                hashes[f'{seed}_{route}'] = hashlib.sha256((folder / 'policy.pt').read_bytes()).hexdigest()
            for mode_name, mode in modes.items():
                mode_ids = np.asarray(mode['pids']); selected = np.isin(ids, mode_ids)
                actual_ids = ids[selected]; obs = observations[selected]
                lookup = {pid: i for i, pid in enumerate(mode_ids)}
                index = torch.tensor([lookup[int(pid)] for pid in actual_ids], dtype=torch.long)
                e0, e1 = torch.from_numpy(mode['e0']), torch.from_numpy(mode['e1'])
                geometry = {}
                for route, policy in policies.items():
                    z0, z1 = policy.persona_proj(e0), policy.persona_proj(e1)
                    cosine = (z0 * z1).sum(-1).clamp(-1, 1)
                    angle = cosine.acos()
                    tangent = torch.nn.functional.normalize(z1 - cosine[:, None] * z0, dim=-1)
                    raw = actor(policy, obs, policy.persona_proj(e0[index]))
                    original = policy.action_logits(obs, e0[index])
                    assert torch.equal(raw, original)
                    reconstructed = angle.cos()[:, None] * z0 + angle.sin()[:, None] * tangent
                    endpoint_error = float((reconstructed - z1).abs().max())
                    assert endpoint_error < 1e-5
                    geometry[route] = (z0, z1, tangent, angle)
                    numerical[f'{seed}_{mode_name}_{route}'] = {'source_actor_logits_byte_equal': True,
                        'spherical_endpoint_max_abs_error': endpoint_error,
                        'unit_norm_max_error': float((z0.norm(dim=-1) - 1).abs().max())}
                common_angle = torch.minimum(geometry['no'][3], geometry['full'][3])
                rng = np.random.default_rng(36011 + (0 if mode_name == 'alias' else 1000))
                random_vectors = torch.from_numpy(rng.standard_normal((len(mode_ids), 16, 64)).astype(np.float32))
                for route, policy in policies.items():
                    z0, z1, tangent, angle = geometry[route]
                    random_tangent = random_vectors - (random_vectors * z0[:, None, :]).sum(-1, keepdim=True) * z0[:, None, :]
                    random_tangent = torch.nn.functional.normalize(random_tangent, dim=-1)
                    p = probabilities(policy, obs, z0[index]); q = probabilities(policy, obs, z1[index])
                    original_js = js(p, q)
                    entry = {'original_angle_mean': float(angle.mean()), 'original_js_mean': float(original_js.mean()),
                             'common_angle_mean': float(common_angle.mean()), 'fractions': {}}
                    key = f'{seed}_{mode_name}_{route}'
                    arrays[key + '_ids'] = actual_ids; arrays[key + '_worlds'] = worlds[selected]
                    arrays[key + '_original_js'] = original_js.numpy()
                    arrays[key + '_original_angle'] = angle.numpy()
                    if mode_name == 'alias':
                        qrepeat = probabilities(policy, obs, policy.persona_proj(torch.from_numpy(repeat[actual_ids - 1])))
                        entry['canonical_repeat_js'] = float(js(p, qrepeat).mean())
                    for fraction in [.5, 1.]:
                        d = common_angle * fraction
                        z = d.cos()[:, None] * z0 + d.sin()[:, None] * tangent
                        changed = probabilities(policy, obs, z[index]); actual_js = js(p, changed)
                        random_z = d.cos()[:, None, None] * z0[:, None, :] + d.sin()[:, None, None] * random_tangent
                        zbatch = random_z[index].reshape(-1, 64)
                        obatch = obs[:, None, :].expand(-1, 16, -1).reshape(-1, OBS_DIM_V3_LARGE)
                        r = probabilities(policy, obatch, zbatch).reshape(len(obs), 16, -1)
                        rjs = js(p[:, None, :].expand_as(r), r)
                        mean_random = rjs.mean(-1)
                        log_ratio = ((actual_js + 1e-12) / (mean_random + 1e-12)).log()
                        entry['fractions'][str(fraction)] = {
                            'matched_angle_js_mean': float(actual_js.mean()), 'random_js_mean': float(mean_random.mean()),
                            'mean_log_relative_response': float(log_ratio.mean()),
                            'random_direction_std_mean': float(rjs.std(-1).mean()),
                            'per_persona_matched_js': {str(pid): float(actual_js[actual_ids == pid].mean()) for pid in mode_ids},
                            'per_persona_log_relative': {str(pid): float(log_ratio[actual_ids == pid].mean()) for pid in mode_ids}}
                        arrays[f'{key}_{fraction}_matched_js'] = actual_js.numpy()
                        arrays[f'{key}_{fraction}_random_js'] = rjs.numpy()
                    summaries[key] = entry
            print(json.dumps({'seed': seed, 'iteration': args.iteration, 'wall_seconds': time.monotonic()-start}), flush=True)
    result = {'iteration': args.iteration, 'training_seeds': [42, 43, 44], 'readouts': summaries,
         'controls': numerical, 'roundoff': roundoff, 'policy_hashes': hashes, 'random_seed': 36011, 'random_directions_per_persona': 16,
         'input_states': 'E25 no_mixed, 3 worlds x 4 cycles; fixed source observations',
         'interpretation_scope': 'Finite latent-response intervention. Not text reachability or utility capability evidence. No scientific pass/fail threshold.',
         'wall_seconds': time.monotonic()-start, 'cloud_calls': 0,
         'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    np.savez_compressed(args.out / 'per_state.npz', **arrays)
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    compact = {k: {name: value for name, value in v.items() if name != 'fractions'} | {
        'matched_js': v['fractions']['1.0']['matched_angle_js_mean'],
        'random_js': v['fractions']['1.0']['random_js_mean'],
        'log_relative': v['fractions']['1.0']['mean_log_relative_response']} for k, v in summaries.items()}
    print(json.dumps(compact), flush=True)


if __name__ == '__main__':
    main()
