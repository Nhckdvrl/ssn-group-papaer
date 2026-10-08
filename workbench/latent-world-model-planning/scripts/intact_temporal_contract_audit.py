"""Same-checkpoint H1/H3 x legacy/forward-aligned oracle-action diagnostics."""
import shutil
import numpy as np
import torch
import intact_published_control_v3 as a
import controller_outcome_train as train
from experience_transfer_control_audit import ROOT, WB, read, save, sha

CELLS = [(1,'LEGACY'),(1,'ALIGNED'),(3,'LEGACY'),(3,'ALIGNED')]


def advance(net,z,incoming,command,alignment):
    width = min(3,z.size(1),incoming.size(1))
    if alignment=='LEGACY':
        actions = incoming[:,-width:].clone()
        actions[:,-1] = command
    else:
        actions = torch.cat([incoming[:,1:],command[:,None]],1)[:,-width:]
    prediction = net.predict(z[:,-width:],net.action_encoder(actions))[:,-1:]
    return torch.cat([z,prediction],1),torch.cat([incoming,command[:,None]],1)


def predict(net,z,incoming,commands,alignment):
    predictions=[]
    for k in range(5):
        z,incoming=advance(net,z,incoming,commands[:,k],alignment)
        predictions.append(z[:,-1])
    return torch.stack(predictions,1)


@torch.inference_mode()
def run():
    a.setup()
    out=ROOT/'20261005-E01-intact-temporal-contract'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__,out/'used.py')
    try:
        summaries, controls, groups=[],[],[]
        for task in ['tworoom','pusht']:
            net,scaler,source=a.source(task,'cuda')
            model_hash=a.state_hash(net.state_dict())
            features=ROOT/f'20261005-E14-controller-outcome-features-{task}'
            cfg=read(features/'config.json')
            assert cfg['source']==source and cfg['features_sha256']==sha(features/'features.npz')
            with np.load(features/'features.npz') as raw:
                data={k:raw[k].copy() for k in raw.files}
            bank=ROOT/f'20261005-E14-controller-consequence-{task}'
            ledger=sorted([e for e in read(ROOT/'20261004-E20-legal-effect-bank44/ledger.json') if e['task']==task],key=lambda e:e['anchor'])
            history, previous={},{}
            for j,e in enumerate(ledger):
                with np.load(bank/f'trace_{j:03d}_g00_OPEN25.npz') as raw:
                    images=raw['warm_history'].copy()
                encoded=net.encode(dict(pixels=a.pixels(images[None],'cuda')))['emb'][0].cpu().numpy()
                np.testing.assert_allclose(encoded[-1],data['z'][np.flatnonzero(data['anchor']==j)[0],0],atol=2e-4,rtol=1e-5)
                history[j]=encoded
                warm=np.asarray(e['warm_actions'],dtype=np.float32)
                assert warm.shape==(10,2)
                previous[j]=scaler.scaler.transform(np.concatenate([np.zeros((5,2),np.float32),warm])).reshape(3,10).astype(np.float32)
            initials={h:np.asarray([history[int(j)][-h:] for j in data['anchor']]) for h in [1,3]}
            incoming={h:np.asarray([previous[int(j)][-h:] for j in data['anchor']]) for h in [1,3]}
            # Use one identical source encode for whole-rollout/manual parity.
            index=int(np.flatnonzero(data['steps']==25)[0]);j=int(data['anchor'][index])
            example = f"trace_{j:03d}_g{int(data['branch'][index]):02d}_{['OPEN25','GOAL5','REFERENCE5'][int(data['method'][index])]}.npz"
            with np.load(bank/example) as raw:
                warm_pixels=raw['warm_history'].copy()
            future=torch.from_numpy(data['commands'][index:index+1]).cuda()
            for h,alignment in CELLS:
                z=torch.from_numpy(initials[h][index:index+1]).cuda()
                acts=torch.from_numpy(incoming[h][index:index+1]).cuda()
                manual=predict(net,z,acts,future,alignment)
                if alignment=='LEGACY':
                    original_z,original_acts=z,acts
                    expected=[]
                    for k in range(5):
                        original_z,original_acts=net.rollout_one_step(original_z,future[:,k],original_acts)
                        expected.append(original_z[:,-1])
                    assert torch.equal(manual,torch.stack(expected,1))
                else:
                    sequence=future if h==1 else torch.cat([acts[:,1:],future],1)
                    inp=dict(pixels=a.pixels(warm_pixels[None,None,-h:],'cuda'))
                    actual=net.rollout(inp,sequence[:,None])['predicted_emb'][:,0,-5:]
                    assert torch.equal(manual,actual)
                # Batched prediction numerical guard, without batching vision.
                first=np.arange(4)
                batch=predict(net,torch.from_numpy(initials[h][first]).cuda(),torch.from_numpy(incoming[h][first]).cuda(),torch.from_numpy(data['commands'][first]).cuda(),alignment)
                separate=torch.cat([predict(net,torch.from_numpy(initials[h][k:k+1]).cuda(),torch.from_numpy(incoming[h][k:k+1]).cuda(),torch.from_numpy(data['commands'][k:k+1]).cuda(),alignment) for k in first])
                np.testing.assert_allclose(batch.cpu().numpy(),separate.cpu().numpy(),atol=2e-4,rtol=1e-5)
                cpu,_,cpu_source=a.source(task,'cpu')
                assert cpu_source==source
                cp=predict(cpu,z.cpu(),acts.cpu(),future.cpu(),alignment)
                np.testing.assert_allclose(manual.cpu().numpy(),cp.numpy(),atol=2e-4,rtol=1e-5)
                del cpu
                controls.append(dict(task=task,history=h,alignment=alignment,source_API_exact=True,B1_batch_original_tolerance=True,CPU_CUDA_original_tolerance=True))
            predictions={}
            for h,alignment in CELLS:
                batches=[]
                for start in range(0,len(data['anchor']),128):
                    stop=start+128
                    z,acts,commands=[torch.from_numpy(v[start:stop]).cuda() for v in [initials[h],incoming[h],data['commands']]]
                    batches.append(predict(net,z,acts,commands,alignment).cpu().numpy())
                predictions[f'H{h}-{alignment}']=np.concatenate(batches)
            np.savez_compressed(out/f'predictions_{task}.npz',**predictions)
            _,std=train.normalization(data,train.select(data))
            for name,pred in predictions.items():
                sq=(pred-data['z'][:,1:])**2
                normalized=(sq/std.numpy()**2).mean(-1)
                raw=sq.mean(-1)
                for scope,eligible in [('ALL-VALID-MACROS',np.ones(len(raw),bool)),('FULL25',data['steps']==25),('HELD-FULL25',(data['anchor']>=32)&(data['steps']==25))]:
                    mask=data['complete_macro']&eligible[:,None]
                    counts=mask.sum(0)
                    summaries.append(dict(task=task,cell=name,scope=scope,valid_targets=counts.tolist(),unique_anchors=len(np.unique(data['anchor'][eligible&mask.any(1)])),raw_prefix_MSE=((raw*mask).sum(0)/counts).tolist(),normalized_prefix_MSE=((normalized*mask).sum(0)/counts).tolist()))
            assert model_hash==a.state_hash(net.state_dict())
            groups.append(dict(task=task,source=source,feature_sha256=cfg['features_sha256'],all_frameskip5=True,checkpoint_unchanged=True,source_kernel_sha256=sha(a.RUNTIME/'jepa.py'),normalizer_scope='Inherited local public-dataset stats; official evaluator also fits column StandardScaler, but exact published training stats are absent from checkpoint metadata and remain unverified.'))
            print('Full same-checkpoint temporal contract',task,'4 cells PASS',flush=True)
        result=dict(completed=True,groups=groups,controls=controls,summaries=summaries,script_sha256=sha(__file__),raw_artifact=str(out),scope='Oracle true future commands are diagnostic only, not a planner. Same source0 weights/normalizer/physical traces; current warm history and forward vs incoming action indexing separated. No learned method evidence or full official numerical reproduction.')
        save(out/'result.json',result)
        save(WB/'results/E01_20261005_intact_temporal_contract_audit.json',result)
    except Exception as error:
        save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise


if __name__=='__main__':
    run()
