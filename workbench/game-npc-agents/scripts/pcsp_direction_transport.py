"""E39: transport measured trait directions between original persona anchors.

This is a latent causal diagnosis, not natural-language reachability or a new
deployment method. All donors, recipients, seeds and registered stages remain.
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
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.source/'research'))
    import numpy as np
    import torch
    from src.training.pcsp_trainer import PCSPActorCritic
    from src.env.v3_constants import OBS_DIM_V3_LARGE, N_ACTIONS_V3
    torch.set_num_threads(1); start = time.monotonic()
    root = args.runs
    data = np.load(root/f'e37_matched_i{args.iteration}/per_state.npz')
    pairs = json.loads((root/'e37_role_edit_codes/texts.json').read_text())['pairs']
    ids = data['pair_ids']; groups = np.asarray([(int(pid)-401)//20 for pid in ids])
    obs = torch.from_numpy(data['observations']); r0 = torch.from_numpy(data['reward_original']); r1 = torch.from_numpy(data['reward_edited'])
    n, states, _ = obs.shape
    e0 = torch.from_numpy(np.load(root/'e26_semantic_codes/canonical.npy').astype(np.float32)[ids-1])
    e1 = torch.from_numpy(np.load(root/'e37_role_edit_codes/C_edits.npy').astype(np.float32))
    value = {'low': -1., 'mid': 0., 'high': 1.}
    dc = torch.tensor([value[p['target_C']]-value[p['original_C']] for p in pairs])
    sign = dc.sign(); arrays = {}; summaries = {}; controls = {}; hashes = {}
    def logits(policy, obs, z):
        return policy.actor_head(policy.actor_b3(policy.actor_b2(policy.actor_b1(obs, z), z), z))
    def probability(policy, z):
        zz = z[:, None].expand(-1, states, -1).reshape(-1, 64)
        return logits(policy, obs.reshape(-1, OBS_DIM_V3_LARGE), zz).double().softmax(-1).reshape(n, states, -1)
    def js(p, q):
        m = (p+q)/2
        return .5*((p*(p.log()-m.log())).sum(-1)+(q*(q.log()-m.log())).sum(-1))
    def cells(p, q, ra, rb):
        return torch.stack([(p*ra).sum(-1), (q*ra).sum(-1), (p*rb).sum(-1), (q*rb).sum(-1)], -1)
    def dd(c): return c[..., 3]-c[..., 2]-c[..., 1]+c[..., 0]
    def group_matrix(matrix):
        return [[float(matrix[groups==a][:, groups==b].mean()) for b in range(5)] for a in range(5)]
    for seed in [42, 43, 44]:
        angle = torch.from_numpy(data[f'{seed}_common_angle'])
        for route, name in [('no', 'no_consist'), ('full', 'full')]:
            folder=root/f'e34_cpu_s{seed}_{name}'/f'checkpoint_{args.iteration:04d}'
            policy=PCSPActorCritic(OBS_DIM_V3_LARGE, N_ACTIONS_V3)
            policy.load_state_dict(torch.load(folder/'policy.pt', map_location='cpu', weights_only=True))
            policy.eval().requires_grad_(False)
            hashes[f'{seed}_{route}']=hashlib.sha256((folder/'policy.pt').read_bytes()).hexdigest()
            with torch.no_grad():
                z0, z1 = policy.persona_proj(e0), policy.persona_proj(e1)
                p = probability(policy, z0)
                positive_chord = (z1-z0)/dc[:, None]
                tangents = positive_chord[None].expand(n, -1, -1)
                tangents = tangents - (tangents*z0[:, None]).sum(-1, keepdim=True)*z0[:, None]
                tangents = torch.nn.functional.normalize(tangents, dim=-1)*sign[:, None, None]
                assert torch.equal(logits(policy, obs[:, 0], z0), policy.action_logits(obs[:, 0], e0))
            # White-box functional reference, averaged across the same 12 states.
            zgrad=z0.detach().clone().requires_grad_(True)
            utility=(probability(policy, zgrad)*(r1-r0)).sum(-1).mean(-1).sum()
            gradient=torch.autograd.grad(utility, zgrad)[0].detach()
            gradient=gradient-(gradient*z0).sum(-1, keepdim=True)*z0
            gradient_norm=gradient.norm(dim=-1)
            gradient=torch.nn.functional.normalize(gradient, dim=-1)
            own_tangent=tangents[torch.arange(n), torch.arange(n)]
            alignment=(own_tangent*gradient).sum(-1)
            with torch.no_grad():
                for fraction in [.5, 1.]:
                    d=angle*fraction
                    transported=d.cos()[:, None, None]*z0[:, None]+d.sin()[:, None, None]*tangents
                    cell_parts=[]; js_parts=[]; own_probs=[]
                    for start_row in range(0, n, 10):
                        end=min(n, start_row+10); count=end-start_row
                        ob=obs[start_row:end, None].expand(-1, n, -1, -1).reshape(-1, OBS_DIM_V3_LARGE)
                        zz=transported[start_row:end, :, None].expand(-1, -1, states, -1).reshape(-1, 64)
                        q=logits(policy, ob, zz).double().softmax(-1).reshape(count, n, states, -1)
                        pp=p[start_row:end, None].expand_as(q)
                        cc=cells(pp, q, r0[start_row:end, None], r1[start_row:end, None])
                        cell_parts.append(cc); js_parts.append(js(pp, q))
                        own_probs.extend(q[i, start_row+i] for i in range(count))
                    cc=torch.cat(cell_parts); response=torch.cat(js_parts); own_probs=torch.stack(own_probs)
                    mode='.5' if fraction == .5 else '1.0'
                    ref_key=f'{seed}_{route}_C_edit_{mode}_probabilities'
                    own_error=float((own_probs-torch.from_numpy(data[ref_key])).abs().max())
                    assert own_error < 1e-5, 'Own direction failed to restore E37 implementation'
                    oracle=probability(policy, d.cos()[:, None]*z0+d.sin()[:, None]*gradient)
                    oracle_cells=cells(p, oracle, r0, r1)
                    key=f'{seed}_{route}_{fraction}'; orientation=dd(cc).mean(-1)
                    # Additive donor/recipient effects are descriptive: they
                    # are not a causal variance attribution without interaction.
                    centered=orientation-orientation.mean()
                    recipient=centered.mean(1); donor=centered.mean(0)
                    residual=centered-recipient[:, None]-donor[None]
                    summaries[key]={'donor_recipient_archetype_dd': group_matrix(orientation.numpy()),
                        'donor_recipient_archetype_js': group_matrix(response.mean(-1).numpy()),
                        'own_direction_dd_mean': float(orientation.diagonal().mean()),
                        'all_transported_dd_mean': float(orientation.mean()),
                        'oracle_mean_dd': float(dd(oracle_cells).mean()),
                        'mean_own_gradient_alignment': float(alignment.mean()),
                        'recipient_additive_sd': float(recipient.std()), 'donor_additive_sd': float(donor.std()),
                        'interaction_sd': float(residual.std()),
                        'per_persona_oracle_dd': {str(pid): float(dd(oracle_cells)[ids==pid].mean()) for pid in sorted(set(ids))}}
                    controls[key]={'own_direction_probability_max_abs_error': own_error,
                        'transported_norm_max_error': float((transported.norm(dim=-1)-1).abs().max()),
                        'gradient_zero_count': int((gradient_norm==0).sum()), 'source_logits_byte_equal': True}
                    arrays[key+'_four_cells_mean_states']=cc.mean(2).numpy()
                    arrays[key+'_dd_per_state']=dd(cc).numpy(); arrays[key+'_js_per_state']=response.numpy()
                    arrays[key+'_oracle_cells']=oracle_cells.numpy(); arrays[key+'_gradient_alignment']=alignment.numpy()
            print(json.dumps({'iteration':args.iteration,'seed':seed,'route':route,'seconds':time.monotonic()-start}),flush=True)
    arrays['pair_ids']=ids
    np.savez_compressed(args.out/'transport.npz',**arrays)
    result={'iteration':args.iteration,'training_seeds':[42,43,44],'personas':100,'pairs':120,
        'matrix_axes':['recipient','donor'],'archetypes':[401,421,441,461,481],
        'readouts':summaries,'controls':controls,'policy_hashes':hashes,'wall_seconds':time.monotonic()-start,
        'scope':'Latent finite displacement and immediate author reward only; not a deployable method or natural text ability.',
        'raw_e37':str(root/f'e37_matched_i{args.iteration}'),'cloud_calls':0,'new_training':False,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'iteration':args.iteration,'wall_seconds':result['wall_seconds']}),flush=True)


if __name__=='__main__':
    main()
