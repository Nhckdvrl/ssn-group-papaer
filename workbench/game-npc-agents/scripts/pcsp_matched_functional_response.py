"""E37: matched role, state and latent displacement; original game rewards.

All roles/seeds remain in the output. No scientific pass/fail threshold.
Reward reconstruction and source-logit equality check implementation only.
"""
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
    ap.add_argument('--iteration', type=int, choices=[30, 100, 300], required=True)
    ap.add_argument('--state-directory', type=Path)
    ap.add_argument('--state-route', choices=['no', 'full'], default='no')
    ap.add_argument('--policy-manifest', type=Path)
    ap.add_argument('--identity-controls', action='store_true')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source / 'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv
    from src.env.v3_constants import OBS_DIM_V3_LARGE, N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic
    from pcsp_observation_rewards import reward_vector
    torch.set_num_threads(1); start = time.monotonic()
    root = args.runs
    supplied_policies = json.loads(args.policy_manifest.read_text()) if args.policy_manifest else None
    native = args.state_directory or root / 'e34_eval_s42_i30/native'
    manifest = json.loads((native / 'manifest.json').read_text())
    with np.load(native / f'{args.state_route}_native.npz') as d:
        observations = d['obs']; actions = d['actions']; total_rewards = d['rewards']
        native_ids = d['ids']; worlds = d['world_seeds']
    definitions = json.loads((args.source / 'research/data/personas/test_100_v3.json').read_text())
    definitions = {int(r['id']): r for r in definitions}
    metadata = json.loads((root / 'e37_role_edit_codes/texts.json').read_text())
    pairs = metadata['pairs']; pids = np.asarray([p['id'] for p in pairs])
    canonical = np.load(root / 'e26_semantic_codes/canonical.npy').astype(np.float32)[pids - 1]
    identity_donors = None
    if args.identity_controls:
        def signature(r):
            return json.dumps({k:r[k] for k in ['big_five','decay_modifiers','preferred_actions']},sort_keys=True)
        classes = {}
        for pid,row in definitions.items():classes.setdefault(signature(row),[]).append(pid)
        identity_donors = {}
        for group in classes.values():
            group.sort()
            for i,pid in enumerate(group):identity_donors[pid]=group[(i+1)%len(group)]
        identity_codes=np.load(root/'e26_semantic_codes/canonical.npy').astype(np.float32)[[identity_donors[int(pid)]-1 for pid in pids]]
        assert all(signature(definitions[int(pid)])==signature(definitions[identity_donors[int(pid)]]) for pid in pids)
    aliases = np.load(root / 'e26_semantic_codes/reverse_clauses.npy').astype(np.float32)[pids - 1]
    repeated = np.load(root / 'e37_role_edit_codes/canonical_repeat.npy').astype(np.float32)[pids - 401]
    edited = np.load(root / 'e37_role_edit_codes/C_edits.npy').astype(np.float32)
    cycles = [0, 20, 100, 199]
    environments = {}; cohort_for = {}
    for ci, cohort in enumerate(manifest['cohorts']):
        env = MiniInzoiV3LargeEnv(personas=[PersonaConfig.from_dict(definitions[pid])
              for pid in cohort['padded_ids']], max_steps=200)
        env.reset(seed=cohort['native_seed']); environments[ci] = env
        for actor, pid in enumerate(cohort['padded_ids'][:cohort['actual']]):
            cohort_for[(cohort['world_seed'], pid)] = (ci, actor)
    # Independently reconstruct every action's observed native reward, including
    # mixed cohorts, actor ordering and the padded final cohort.
    native_errors = []; r0_by_row = {}; rows_by_id = {}
    for row, (pid, world) in enumerate(zip(native_ids, worlds)):
        ci, actor = cohort_for[(int(world), int(pid))]; env = environments[ci]
        actual = sum(reward_vector(env, actor, observations[row, t], actions=[actions[row, t]])[0]
                     for t in range(200))
        native_errors.append(abs(actual - total_rewards[row]))
        rows_by_id.setdefault(int(pid), []).append(row)
        r0_by_row[row] = np.stack([reward_vector(env, actor, observations[row, t]) for t in cycles])
    assert max(native_errors) < 1e-4, 'Native reward reconstruction implementation mismatch'
    obs_pairs = []; r0_pairs = []; r1_pairs = []; state_worlds = []
    for pair in pairs:
        selected = rows_by_id[pair['id']]
        obs_pairs.append(np.concatenate([observations[row, cycles] for row in selected]))
        r0_pairs.append(np.concatenate([r0_by_row[row] for row in selected]))
        target = []
        for row in selected:
            ci, actor = cohort_for[(int(worlds[row]), pair['id'])]
            target.extend(reward_vector(environments[ci], actor, observations[row, t], target_C=pair['target_C']) for t in cycles)
        r1_pairs.append(np.stack(target)); state_worlds.append(np.repeat(worlds[selected], len(cycles)))
    for env in environments.values(): env.close()
    obs = torch.from_numpy(np.stack(obs_pairs))
    r0 = torch.from_numpy(np.stack(r0_pairs)); r1 = torch.from_numpy(np.stack(r1_pairs))
    n, states, _ = obs.shape
    assert n == 120 and states == 12 and obs.shape[-1] == OBS_DIM_V3_LARGE
    def actor(policy, observations, z):
        return policy.actor_head(policy.actor_b3(policy.actor_b2(policy.actor_b1(observations, z), z), z))
    def probabilities(policy, z):
        expanded = z[:, None, :].expand(-1, states, -1)
        return actor(policy, obs.reshape(-1, OBS_DIM_V3_LARGE), expanded.reshape(-1, 64)).double().softmax(-1).reshape(n, states, -1)
    def js(p, q):
        m = (p + q) / 2
        return .5 * ((p * (p.log() - m.log())).sum(-1) + (q * (q.log() - m.log())).sum(-1))
    def cells(p, q):
        result = torch.stack([(p*r0).sum(-1), (q*r0).sum(-1), (p*r1).sum(-1), (q*r1).sum(-1)], -1)
        return result, (result[..., 3] - result[..., 2]) - (result[..., 1] - result[..., 0])
    def geometry(policy, e0, e1):
        z0, z1 = policy.persona_proj(e0), policy.persona_proj(e1)
        cosine = (z0*z1).sum(-1).clamp(-1, 1); angle = cosine.acos()
        tangent = torch.nn.functional.normalize(z1 - cosine[:, None]*z0, dim=-1)
        endpoint = angle.cos()[:, None]*z0 + angle.sin()[:, None]*tangent
        error = float((endpoint-z1).abs().max()); assert error < 1e-5
        return z0, z1, tangent, angle, error
    def by_persona(x):
        return {str(pid): float(x[pids == pid].mean()) for pid in sorted(set(pids))}
    summaries = {}; arrays = {}; controls = {}; hashes = {}
    e0, ea, ec = map(torch.from_numpy, (canonical, aliases, edited))
    edit_directions=[('alias',ea),('C_edit',ec)]
    if args.identity_controls:edit_directions.append(('identity_same_utility',torch.from_numpy(identity_codes)))
    er = torch.from_numpy(repeated)
    with torch.inference_mode():
        for seed in [42, 43, 44]:
            policies = {}; geometries = {}
            routes = supplied_policies[str(seed)] if supplied_policies else {
                'no': str(root/f'e34_cpu_s{seed}_no_consist'/f'checkpoint_{args.iteration:04d}'),
                'full': str(root/f'e34_cpu_s{seed}_full'/f'checkpoint_{args.iteration:04d}')}
            for route, folder_name in routes.items():
                folder = Path(folder_name)
                policy = PCSPActorCritic(OBS_DIM_V3_LARGE, N_ACTIONS_V3)
                policy.load_state_dict(torch.load(folder/'policy.pt', map_location='cpu', weights_only=True))
                policy.eval().requires_grad_(False); policies[route] = policy
                meta = json.loads((folder/'manifest.json').read_text())
                assert meta['seed'] == seed and meta['completed_iterations'] == args.iteration
                hashes[f'{seed}_{route}'] = hashlib.sha256((folder/'policy.pt').read_bytes()).hexdigest()
                geometries[route] = {direction: geometry(policy, e0, e) for direction, e in edit_directions}
                direct = actor(policy, obs[:, 0], policy.persona_proj(e0))
                assert torch.equal(direct, policy.action_logits(obs[:, 0], e0))
                controls[f'{seed}_{route}'] = {'source_actor_logits_byte_equal': True,
                    'maximum_spherical_endpoint_error': max(g[-1] for g in geometries[route].values())}
            common = torch.stack([g[3] for route in geometries.values() for g in route.values()]).min(0).values
            arrays[f'{seed}_common_angle'] = common.numpy()
            for route, policy in policies.items():
                z0 = geometries[route]['alias'][0]; p = probabilities(policy, z0)
                repeat_js = js(p, probabilities(policy, policy.persona_proj(er)))
                rng = np.random.default_rng(37011)
                random = torch.from_numpy(rng.standard_normal((n, 16, 64)).astype(np.float32))
                random = torch.nn.functional.normalize(random - (random*z0[:, None]).sum(-1, keepdim=True)*z0[:, None], dim=-1)
                random_responses = {}
                for fraction in [.5, 1.]:
                    d = common*fraction
                    rjs = []
                    for k in range(16):
                        z = d.cos()[:, None]*z0 + d.sin()[:, None]*random[:, k]
                        rjs.append(js(p, probabilities(policy, z)))
                    random_responses[fraction] = torch.stack(rjs, -1)
                for direction,_ in edit_directions:
                    _, z1, tangent, angle, _ = geometries[route][direction]
                    key = f'{seed}_{route}_{direction}'
                    entry = {'natural_angle_mean': float(angle.mean()), 'common_angle_mean': float(common.mean()),
                        'repeat_js_mean': float(repeat_js.mean()), 'readouts': {}}
                    for mode in ['natural', '.5', '1.0']:
                        if mode == 'natural': z = z1
                        else:
                            d = common*float(mode); z = d.cos()[:, None]*z0 + d.sin()[:, None]*tangent
                        q = probabilities(policy, z); response = js(p, q); four, dd = cells(p, q)
                        record = {'js_mean': float(response.mean()), 'expected_reward_four_cells_mean': four.mean((0, 1)).tolist(),
                            'reward_orientation_dd_mean': float(dd.mean()), 'per_persona_js': by_persona(response.numpy()),
                            'per_persona_reward_dd': by_persona(dd.numpy())}
                        if mode != 'natural':
                            rjs = random_responses[float(mode)]
                            record.update(random_js_mean=float(rjs.mean()), random_direction_sd_mean=float(rjs.std(-1).mean()))
                            arrays[f'{key}_{mode}_random_js'] = rjs.numpy()
                        entry['readouts'][mode] = record
                        arrays[f'{key}_{mode}_js'] = response.numpy()
                        arrays[f'{key}_{mode}_reward_cells'] = four.numpy()
                        arrays[f'{key}_{mode}_probabilities'] = q.numpy()
                    arrays[f'{key}_original_angle'] = angle.numpy()
                    summaries[key] = entry
            print(json.dumps({'iteration': args.iteration, 'seed': seed, 'wall_seconds': time.monotonic()-start}), flush=True)
    arrays.update(pair_ids=pids, observations=obs.numpy(), reward_original=r0.numpy(), reward_edited=r1.numpy(),
                  state_worlds=np.stack(state_worlds), cycles=np.tile(cycles, 3))
    np.savez_compressed(args.out/'per_state.npz', **arrays)
    (args.out/'pairs.json').write_text(json.dumps(pairs, ensure_ascii=False, indent=2)+'\n')
    result = {'iteration': args.iteration, 'training_seeds': [42, 43, 44], 'personas': 100, 'edit_pairs': n,
        'states_per_pair': states, 'reward_cell_order': ['pi_original_R_original', 'pi_changed_R_original', 'pi_original_R_edited', 'pi_changed_R_edited'],
        'readouts': summaries, 'controls': controls, 'policy_hashes': hashes,
        'explicit_policy_manifest': supplied_policies,
        'identity_control_donors': identity_donors,
        'identity_scope': 'Same source utility/body/preferred-actions, changed authored age/occupation text. Distinct style remains allowed; action equality is not a scientific requirement.' if args.identity_controls else None,
        'reward_reconstruction': {'native_transitions': len(actions)*actions.shape[1],
            'native_episodes': len(actions), 'maximum_total_reward_abs_error': max(native_errors), 'mean_total_reward_abs_error': float(np.mean(native_errors))},
        'state_source': str(native), 'state_route': args.state_route, 'observation_timing': manifest['observation_timing'],
        'interpretation': 'Immediate author-defined reward, not long-term utility or psychometric validity. Mid-C roles have two edits; they are not independent personas. All seeds retained; no scientific cutoff.',
        'wall_seconds': time.monotonic()-start, 'cloud_calls': 0,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.out/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'reward_reconstruction': result['reward_reconstruction'], 'wall_seconds': result['wall_seconds']}), flush=True)


if __name__ == '__main__':
    main()
