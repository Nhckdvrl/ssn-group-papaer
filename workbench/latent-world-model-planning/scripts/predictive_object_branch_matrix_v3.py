"""A11: full common-reset consequences, no outcome-dependent candidate selection."""
import argparse
import gc
import shutil
from pathlib import Path
import numpy as np
import torch
import predictive_object_rollout as rollout
import effect_training as effect
from experience_transfer_control_audit import ROOT, WB, read, save, sha
from fixed_data_train_seed import normalized_pixels, state_hash
r = rollout.r
BANK = ROOT/'20261004-E20-legal-effect-bank44'
BRANCHES = np.asarray([0]+list(range(2,12)))


def load(geometry, seed, arm, device):
    rollout.setup(seed)
    name = f'20261005-E13-rollout-{geometry}-s{seed}-A100' if arm == 'OPEN' else f'20261005-E13-object-{geometry}-{arm}-A100-s{seed}'
    source = ROOT/name; cfg = read(source/'config.json'); summary = read(source/'summary.json')
    assert read(source/'complete.json')['completed']
    path = r.m.HF/name/'u2825.ckpt'
    assert sha(path) == summary['checkpoint_sha256']
    c = torch.load(path,map_location='cpu',weights_only=False)
    assert c['steps'] == 2825 and c['geometry'] == geometry
    if seed or arm == 'OPEN': assert c['train_seed'] == seed
    assert c['arm'] == ('OPEN-ROLLOUT' if arm == 'OPEN' else arm)
    net = r.Model(c['config'],geometry); net.load_state_dict(c['state_dict'],strict=True)
    net = net.to(device).eval().requires_grad_(False)
    assert net.frozen_hash() == cfg['feature_metadata']['frozen_phi_sha256']
    return net, c, dict(checkpoint=str(path),checkpoint_sha256=sha(path),training_run=name,training_config_sha256=sha(source/'config.json'))


def predict(net, z, actions, arm):
    if arm == 'DIRECT': return net.prefix(z,actions)
    values = []
    for step in range(5):
        z = net.prefix(z,actions[:,step:step+1])[:,0]; values.append(z)
    return torch.stack(values,1)


def manual(net, z, actions, arm):
    if arm == 'DIRECT':
        ap = net.core['action'](actions,latent=z[:,None])
        pr = net.core['predictor'](z[:,None],ap)
        return net.core['projection'](pr.flatten(0,1)).reshape(pr.shape)
    values = []
    for step in range(5):
        ap = net.core['action'](actions[:,step:step+1],latent=z[:,None])
        pr = net.core['predictor'](z[:,None],ap)
        z = net.core['projection'](pr[:,0]); values.append(z)
    return torch.stack(values,1)


def matrix(prediction, truth, physical):
    # Goal is supplied as an actual image. Candidate scores never use physical
    # state, actual candidate outcomes or the identity of the generating branch.
    costs = ((prediction[:,-1,None]-truth[None,:,-1])**2).sum(-1).T
    chosen = costs.argmin(1)
    scores_without_goal = costs.copy(); np.fill_diagonal(scores_without_goal,np.inf)
    chosen_without_goal = scores_without_goal.argmin(1)
    # These are evaluation-only counterfactual outcomes, after choices are fixed.
    actual = np.linalg.norm(physical[:,None]-physical[None,:],axis=-1)
    oracle_costs = ((truth[:,-1,None]-truth[None,:,-1])**2).sum(-1).T
    np.fill_diagonal(oracle_costs,np.inf); oracle = oracle_costs.argmin(1)
    min_without_goal = actual.copy(); np.fill_diagonal(min_without_goal,np.inf)
    best_without_goal = min_without_goal.min(1)
    j = np.arange(11)
    assert (chosen_without_goal != j).all() and (oracle != j).all()
    result = dict(predicted_costs=costs.tolist(),actual_endpoint_distances=actual.tolist(),
        selected_branch=BRANCHES[chosen].tolist(),native_success=(actual[j,chosen]<16).tolist(),trajectory_endpoint_regret=actual[j,chosen].tolist(),
        leave_goal_out_selected_branch=BRANCHES[chosen_without_goal].tolist(),leave_goal_out_native_success=(actual[j,chosen_without_goal]<16).tolist(),
        leave_goal_out_best_distance=best_without_goal.tolist(),leave_goal_out_trajectory_endpoint_regret=(actual[j,chosen_without_goal]-best_without_goal).tolist(),
        leave_goal_out_true_latent_oracle_branch=BRANCHES[oracle].tolist(),leave_goal_out_true_latent_oracle_native_success=(actual[j,oracle]<16).tolist(),
        leave_goal_out_true_latent_oracle_regret=(actual[j,oracle]-best_without_goal).tolist())
    assert np.isfinite(costs).all() and np.isfinite(actual).all()
    return result


@torch.inference_mode()
def run(geometry,seed):
    name = f'20261005-E13-branch-matrix-v3-{geometry}-s{seed}-RTX'
    out = ROOT/name; assert not out.exists(); out.mkdir(); shutil.copy2(__file__,out/'used.py')
    try:
        for endpoint in ['E13_20261005_predictive_object_three_seed_control_results.json','E13_20261005_rollout_control_results.json']:
            assert read(WB/'results'/endpoint)['completed']
        images, actions, physical, bankcfg = effect.load_bank(BANK)
        assert images.shape == (44,12,8,224,224,3) and physical.shape == (44,12,10)
        # Native TwoRoom public state: agent2 + target2 + door centers6.
        # The latter eight coordinates are constant across this same-state bank.
        assert np.array_equal(physical[:,:,2:],np.repeat(physical[:,:1,2:],12,axis=1))
        physical = physical[:,:,:2]
        assert np.array_equal(images[:,0],images[:,1]) and np.array_equal(actions[:,0],actions[:,1])
        assert np.array_equal(physical[:,0],physical[:,1])
        assert np.array_equal(images[:,:,:3],np.repeat(images[:,:1,:3],12,axis=1))
        images = images[:,BRANCHES]; actions = actions[:,BRANCHES,10:35]; physical = physical[:,BRANCHES]
        ledger = sorted([e for e in read(BANK/'ledger.json') if e['task']=='tworoom'],key=lambda e:e['anchor'])
        net,c,source = load(geometry,seed,'DIRECT','cuda')
        assert set(e['episode'] for e in ledger) <= set(c['manifest']['base_episodes'])
        mean,std = np.asarray(c['manifest']['action_mean']),np.asarray(c['manifest']['action_std'])
        acts = torch.tensor((actions-mean)/std,device='cuda').float().reshape(44,11,5,10)
        # Current frame followed by the real five prefix endpoints.
        pixels = images[:,:,2:].reshape(-1,224,224,3); encoded=[]; frozen=net.frozen_hash()
        for begin in range(0,len(pixels),64):
            encoded.append(net.encode_pixels(normalized_pixels(pixels[begin:begin+64],'cuda')).cpu().numpy())
        z = np.concatenate(encoded).reshape(44,11,6,192)
        assert np.isfinite(z).all() and frozen == net.frozen_hash()
        for key,value in [('features',z),('physical_endpoints',physical),('actions',actions)]: np.save(out/f'{key}.npy',value)
        metadata = dict(geometry=geometry,seed=seed,branches=BRANCHES.tolist(),bank_ledger_sha256=sha(BANK/'ledger.json'),bank_rows_sha256=sha(BANK/'rows.json'),
            bank_config=bankcfg,source_episodes=[e['episode'] for e in ledger],frozen_phi_sha256=frozen,script_sha256=sha(__file__),data_helper_sha256=sha(effect.__file__),
            array_sha256={k:sha(out/f'{k}.npy') for k in ['features','physical_endpoints','actions']},hardware=torch.cuda.get_device_name(),encoding_precision='FP32, matmul and cuDNN TF32 disabled; offline evaluation differs from earlier default-cuDNN CEM numerics',
            scope='Same factual-train source states, all counterfactual futures held from fact-only heads. 44 shared states, not484 independent tasks. Old32/12 branch-sampling strata are not train/test for these models. Offline25step trajectory regret, not first-action regret or closed-loop success. Cross-geometry raw MSE not comparable. No new method/causal sufficiency/speedup claim.')
        save(out/'config.json',metadata); del net; gc.collect(); torch.cuda.empty_cache()
        summaries=[]
        for arm in ['DIRECT','LOCAL','OPEN']:
            controls=[]
            for device in ['cpu','cuda']:
                net,c,source=load(geometry,seed,arm,device); before=state_hash(net.state_dict())
                assert net.frozen_hash() == frozen
                ix=np.asarray([0,2,10]); starts=normalized_pixels(images[0,ix,2],device)
                # Check the real pixel interface against cached vectors and the
                # independently spelled-out predictor calculation.
                latent=net.encode_pixels(starts); cached=torch.tensor(z[0,ix,0],device=device)
                assert torch.allclose(latent,cached,atol=2e-4,rtol=1e-5)
                aa=acts[0,ix].to(device); p=predict(net,latent,aa,arm); m=manual(net,latent,aa,arm)
                assert torch.equal(p,m) and torch.isfinite(p).all()
                singleton=torch.cat([predict(net,latent[j:j+1],aa[j:j+1],arm) for j in range(3)])
                assert torch.allclose(p,singleton,atol=2e-4,rtol=1e-5)
                assert before==state_hash(net.state_dict())
                controls.append(dict(device=device,manual_exact=True,batch_subset_error=float((p-singleton).abs().max()),actual_pixel_cache_error=float((latent-cached).abs().max()),weights_unchanged=True,**source))
                if device=='cpu': del net; gc.collect()
            save(out/f'{arm}_controls.json',controls)
            before=state_hash(net.state_dict()); predictions=[]; rows=[]
            for j in range(44):
                p=predict(net,torch.tensor(z[j,:,0],device='cuda'),acts[j],arm).cpu().numpy()
                predictions.append(p); row=matrix(p,z[j,:,1:],physical[j]); row['anchor']=j;row['source_episode']=ledger[j]['episode'];rows.append(row)
            predictions=np.asarray(predictions); assert before==state_hash(net.state_dict())
            np.save(out/f'{arm}_predictions.npy',predictions); save(out/f'{arm}_rows.json',rows)
            mse=((predictions-z[:,:,1:])**2).mean(-1)
            centered_pred=predictions-predictions.mean(1,keepdims=True)
            centered_true=z[:,:,1:]-z[:,:,1:].mean(1,keepdims=True)
            numerator=((centered_pred-centered_true)**2).mean((1,3));denominator=(centered_true**2).mean((1,3))
            # Retain denominators/zero-variation flags, never silently discard.
            np.savez(out/f'{arm}_errors.npz',prefix_mse=mse,effect_error=numerator,true_effect_variation=denominator)
            summaries.append(dict(arm=arm,source=source,prediction_sha256=sha(out/f'{arm}_predictions.npy'),rows_sha256=sha(out/f'{arm}_rows.json'),errors_sha256=sha(out/f'{arm}_errors.npz'),
                native_successes=sum(sum(v['native_success']) for v in rows),queries=484,leave_goal_out_successes=sum(sum(v['leave_goal_out_native_success']) for v in rows),
                factual_prefix_mse=mse[:,0].mean(0).tolist(),counterfactual_prefix_mse=mse[:,1:].mean((0,1)).tolist()))
            print('Full branch matrix',geometry,seed,arm,'complete',flush=True); del net;gc.collect();torch.cuda.empty_cache()
        save(out/'summary.json',summaries);save(out/'complete.json',dict(completed=True,geometry=geometry,seed=seed,arms=3,queries_per_arm=484))
    except Exception as error:
        save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--geometry',choices=['PRED','VALUE']);p.add_argument('--seed',type=int,choices=[0,1,2])
    args=p.parse_args();torch.set_num_threads(4)
    # Patch embedding is a convolution: cuDNN TF32 differs from CPU FP32.
    # Use full FP32 for this offline whole-bank comparison, before encoding.
    torch.set_float32_matmul_precision('highest')
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    for seed in ([args.seed] if args.seed is not None else range(3)):
        for geometry in ([args.geometry] if args.geometry else ['PRED','VALUE']): run(geometry,seed)
