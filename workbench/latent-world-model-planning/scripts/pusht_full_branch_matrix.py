"""A11 full H3 Push bank: published model and every fixed joint endpoint."""
import argparse
import gc
import shutil
from pathlib import Path
import numpy as np
import torch
import goal_policy_pusht_control as component
from experience_transfer_control_audit import ROOT,WB,read,save,sha
from fixed_data_train_seed import normalized_pixels,state_hash
t=component.t;BANK=ROOT/'20261004-E20-legal-effect-bank44';BRANCHES=np.asarray([0]+list(range(2,12)))
METHODS=['RELEASED',*t.e.METHODS]


def load(method,device):
    model,cfg,mean,std,nsha=t.load_source(device)
    if method=='RELEASED':path=t.SOURCE;meta=dict(pretraining_split_unknown=True,branch_training_anchors=[])
    else:
        name=f'20261004-E20-joint-pusht-{method}-RTX-s0';run=ROOT/name;config=read(run/'config.json')
        assert read(run/'complete.json')==dict(completed=True,method=method,seed=0,updates=2000)
        path=Path('/home/xiang/.cache/huggingface/latent-wm-trained')/name/'u2000.ckpt'
        assert sha(path)==next(x['checkpoint_sha256'] for x in read(run/'summary.json') if x['updates']==2000)
        c=torch.load(path,map_location='cpu',weights_only=False);assert c['steps']==2000 and config['train_anchors']==list(range(32))
        assert config['script_sha256']==sha(t.__file__) and config['loss_helper_sha256']==sha(t.e.__file__)
        assert np.array_equal(c['manifest']['action_mean'],mean) and np.array_equal(c['manifest']['action_std'],std)
        model.load_state_dict(c['state_dict'],strict=True);meta=dict(training_run=name,training_config_sha256=sha(run/'config.json'),branch_training_anchors=list(range(32)),pretraining_split_unknown=True)
    assert len(model.state_dict())==303 and all(torch.isfinite(v).all() for v in model.state_dict().values())
    return model.eval().requires_grad_(False),mean,std,dict(**meta,checkpoint=str(path),checkpoint_sha256=sha(path),normalizer_sha256=nsha)


def predict(model,z,raw,mean,std,device):
    act=model.action_encoder(torch.as_tensor((raw-mean)/std,device=device).float().reshape(-1,7,10));emb=z
    outputs=[]
    for h in range(5):
        next_z=model.predict(emb[:,-3:],act[:,h:h+3])[:,-1:];emb=torch.cat([emb,next_z],1);outputs.append(next_z[:,0])
    return torch.stack(outputs,1)


def measurements(pred,z,physical):
    rows=[]
    for j in range(44):
        costs=np.sum((pred[j,:,4][None]-z[j,:,7][:,None])**2,-1);position=np.linalg.norm(physical[j][:,None,:4]-physical[j][None,:,:4],axis=-1)
        angle=np.abs(physical[j][:,None,4]-physical[j][None,:,4]);angle=np.minimum(angle,2*np.pi-angle);native=(position<20)&(angle<np.pi/9);q=np.arange(11)
        selected=costs.argmin(1);masked=costs.copy();np.fill_diagonal(masked,np.inf);leave=masked.argmin(1)
        true=np.sum((z[j,:,7][:,None]-z[j,:,7][None])**2,-1);np.fill_diagonal(true,np.inf);oracle=true.argmin(1)
        distances=position.copy();np.fill_diagonal(distances,np.inf);best=distances.min(1)
        availability=native.copy();np.fill_diagonal(availability,False)
        rows.append(dict(anchor=j,predicted_costs=costs.tolist(),actual_position_distances=position.tolist(),actual_angle_distances=angle.tolist(),native_success=native[q,selected].tolist(),selected_branch=BRANCHES[selected].tolist(),leave_goal_out_native_success=native[q,leave].tolist(),leave_goal_out_selected_branch=BRANCHES[leave].tolist(),leave_goal_out_position_regret=(position[q,leave]-best).tolist(),leave_goal_out_angle_error=angle[q,leave].tolist(),leave_goal_out_true_latent_oracle_native_success=native[q,oracle].tolist(),leave_goal_out_true_latent_oracle_branch=BRANCHES[oracle].tolist(),leave_goal_out_success_available=availability.any(1).tolist(),zero_only_native_success=native[:,0].tolist()))
    return rows


@torch.inference_mode()
def run():
    torch.set_num_threads(4);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    out=ROOT/'20261005-E13-pusht-full-branch-matrix';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        images,actions,physical=t.load_bank(BANK);assert images.shape==(44,12,8,224,224,3) and actions.shape==(44,12,35,2) and physical.shape==(44,12,7)
        assert np.array_equal(images[:,0],images[:,1]) and np.array_equal(actions[:,0],actions[:,1]) and np.array_equal(physical[:,0],physical[:,1])
        assert np.array_equal(images[:,:,:3],np.broadcast_to(images[:,0:1,:3],images[:,:,:3].shape))
        images,actions,physical=images[:,BRANCHES],actions[:,BRANCHES],physical[:,BRANCHES]
        np.save(out/'actions.npy',actions);np.save(out/'physical_endpoints.npy',physical)
        save(out/'config.json',dict(script_sha256=sha(__file__),bank_ledger_sha256=sha(BANK/'ledger.json'),bank_rows_sha256=sha(BANK/'rows.json'),branches=BRANCHES.tolist(),methods=METHODS,hardware=torch.cuda.get_device_name(),scope='Full H3 native predictors, all44 common-reset states/all11 unique branch endpoint goals. Five joint models trained on first32 branches; old12 held branch outcomes, published pretraining unknown. Offline25step choices, not closed-loop; position-only regret auxiliary, native success also requires angle. TF32 disabled for offline numeric parity; previous controls unchanged.'))
        summaries=[]
        for method in METHODS:
            controls=[]
            for device in ['cpu','cuda']:
                model,mean,std,source=load(method,device);before=state_hash(model.state_dict());x=normalized_pixels(images[0,0,:3][None],device);goal=normalized_pixels(images[0,1,-1][None,None],device)
                initial=model.encode(dict(pixels=x))['emb'].expand(11,-1,-1).clone();prediction=predict(model,initial,actions[0],mean,std,device)
                a=torch.as_tensor((actions[0]-mean)/std,device=device).float().reshape(1,11,7,10)
                info=dict(pixels=x[:,None].expand(1,11,3,3,224,224),goal=goal[:,None].expand(1,11,1,3,224,224),action=a)
                actual=model.get_cost(info,a);zg=model.encode(dict(pixels=goal))['emb'][:,0];manual=(prediction[:,-1]-zg).square().sum(-1)[None]
                assert torch.equal(actual,manual) and before==state_hash(model.state_dict()) and torch.isfinite(actual).all()
                if device=='cpu':reference=prediction.cpu();cpu_z=initial.cpu()
                else:torch.testing.assert_close(prediction.cpu(),reference,atol=2e-4,rtol=1e-5);torch.testing.assert_close(initial.cpu(),cpu_z,atol=2e-4,rtol=1e-5)
                controls.append(dict(device=device,passed=True,manual_native_cost_exact=True,source=source,weights_unchanged=True));del model;gc.collect();torch.cuda.empty_cache()
            model,mean,std,source=load(method,'cuda');before=state_hash(model.state_dict());flat=images.reshape(-1,224,224,3);pieces=[]
            for start in range(0,len(flat),64):pieces.append(model.encode(dict(pixels=normalized_pixels(flat[start:start+64][None],'cuda')))['emb'][0].cpu())
            z=torch.cat(pieces).numpy().reshape(44,11,8,192);predictions=[]
            for j in range(44):
                current=torch.tensor(z[j,0,:3],device='cuda')[None].expand(11,-1,-1).clone()
                predictions.append(predict(model,current,actions[j],mean,std,'cuda').cpu().numpy())
            pred=np.asarray(predictions);rows=measurements(pred,z,physical);assert before==state_hash(model.state_dict())
            np.save(out/f'{method}_features.npy',z);np.save(out/f'{method}_predictions.npy',pred);save(out/f'{method}_rows.json',rows);save(out/f'{method}_controls.json',controls)
            summaries.append(dict(method=method,source=source,n=484,native_successes=sum(sum(r['native_success']) for r in rows),leave_goal_out_successes=sum(sum(r['leave_goal_out_native_success']) for r in rows),prefix_mse=np.mean((pred-z[:,:,3:])**2,axis=(0,1,3)).tolist(),rows_sha256=sha(out/f'{method}_rows.json'),prediction_sha256=sha(out/f'{method}_predictions.npy'),features_sha256=sha(out/f'{method}_features.npy')))
            save(out/'summary.json',summaries);print('Full Push H3 branch matrix',method,'complete',flush=True);del model;gc.collect();torch.cuda.empty_cache()
        save(out/'complete.json',dict(completed=True,models=6,queries_per_model=484,total_queries=2904))
    except Exception as error:save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));raise


if __name__=='__main__':run()
