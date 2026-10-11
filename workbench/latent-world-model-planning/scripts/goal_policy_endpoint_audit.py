"""Independent all18 frozen-feature policy endpoints, including exact full samplers."""
import shutil
import numpy as np
import torch
from fixed_data_train_seed import state_hash
import goal_policy_baseline as g


def main():
    records=[];initials={};firsts={}
    for seed in range(3):
        assert g.read(g.ROOT/f'20261005-E14-goalpolicy-pipeline-s{seed}/complete.json')==dict(completed=True,seed=seed,training_runs=6)
        for geometry in g.GEOMETRIES:
            pre=g.ROOT/f'20261005-E14-goalpolicy-{geometry}-cpu-preflight-s{seed}'
            data=np.load(pre/'official_input.npz');z=data['embeddings'];actions=data['actions'];ep=data['episode_ids']
            stops=np.r_[np.flatnonzero(ep[:-1]!=ep[1:])+1,len(ep)]
            end=np.empty(len(ep),int);start=0
            for stop in stops:end[start:stop]=stop;start=stop
            valid=np.flatnonzero((ep[:-1]==ep[1:])&np.isfinite(actions[:-1]).all(1))
            perm=np.random.default_rng(115200+seed).permutation(valid);nval=int(len(valid)*.1);expected_train=perm[nval:];expected_val=perm[:nval]
            for device in ['cpu','cuda']:
                controls=g.read(g.ROOT/f'20261005-E14-goalpolicy-{geometry}-{device}-preflight-s{seed}/controls.json')
                assert controls['passed'] and controls['script_sha256']==g.sha(g.__file__)
                assert len(controls['records'])==3 and controls['vendor_model_sha256']==g.sha(g.VENDOR/'idm/model.py')
            for arm in g.ARMS:
                source=g.ROOT/f'20261005-E14-goalpolicy-{geometry}-{arm}-A100-s{seed}'
                assert g.read(source/'complete.json')==dict(completed=True,geometry=geometry,seed=seed,arm=arm,epochs=50)
                cfg=g.read(source/'config.json');summary=g.read(source/'summary.json')
                assert cfg['script_sha256']==g.sha(g.__file__) and cfg['geometry']==geometry and cfg['arm']==arm and cfg['train_seed']==seed
                assert cfg['feature_metadata']==controls['feature_metadata'] and cfg['vendor_model_sha256']==g.sha(g.VENDOR/'idm/model.py')
                assert np.array_equal(cfg['train_starts'],expected_train) and np.array_equal(cfg['validation_starts'],expected_val)
                assert cfg['lr']==.001 and cfg['weight_decay']==.0001 and cfg['cosine_eta_min']==.00001 and cfg['drop_last']
                checkpoint=g.HF/source.name/'epoch50.ckpt';assert g.sha(checkpoint)==summary['checkpoint_sha256']
                c=torch.load(checkpoint,map_location='cpu',weights_only=False);updates=(len(expected_train)//1024)*50
                assert updates==c['updates']==summary['updates']==400 and summary['training_examples']==409600
                assert (c['geometry'],c['arm'],c['train_seed'])==(geometry,arm,seed)
                net=g.model(seed,'cpu');original=torch.load(checkpoint.parent/'initial.pt',map_location='cpu',weights_only=False)
                assert set(original)==set(net.state_dict()) and all(torch.equal(original[k],v) for k,v in net.state_dict().items())
                initial=state_hash(original);assert initial==cfg['initial_sha256']==summary['initial_sha256']
                initials[seed,geometry,arm]=initial;net.load_state_dict(c['state_dict'],strict=True)
                assert all(torch.isfinite(v).all() for v in net.state_dict().values())
                state=c['optimizer']['state'];assert len(state)==len(list(net.parameters()))==summary['optimizer_states']
                assert all(int(v['step'])==400 and all(torch.isfinite(x).all() for x in v.values()) for v in state.values())
                assert c['optimizer']['param_groups'][0]['lr']==.00001 and c['optimizer']['param_groups'][0]['weight_decay']==.0001
                assert c['scheduler']['last_epoch']==50
                rng=np.random.default_rng(115100+seed);shuffle=np.random.default_rng(115200+seed)
                first=None
                for epoch in range(50):
                    order=shuffle.permutation(expected_train)
                    for begin in range(0,len(order)-1024+1,1024):
                        ix=order[begin:begin+1024];maxh=np.minimum(50,end[ix]-1-ix)
                        h=np.ones(1024,int) if arm=='PAIRWISE' else rng.integers(1,maxh+1)
                        assert (maxh>=1).all() and np.array_equal(ep[ix],ep[ix+h])
                        if first is None:first=dict(indices=ix.tolist(),goal_indices=(ix+h).tolist(),physical_horizon=h.tolist(),input_horizon=(np.zeros_like(h) if arm=='GCBC-MATCHED' else h).tolist())
                assert first==g.read(source/'first_batch.json') and rng.bit_generator.state==c['goal_rng'] and shuffle.bit_generator.state==c['shuffle_rng']
                firsts[seed,geometry,arm]=first
                logs=g.read(source/'training.json');assert len(logs)==50 and [v['epoch'] for v in logs]==list(range(1,51))
                assert all(v['updates']==(k+1)*8 and np.isfinite(v['train_mse']) and np.isfinite(v['validation_mse']) for k,v in enumerate(logs))
                records.append(dict(seed=seed,geometry=geometry,arm=arm,checkpoint_sha256=g.sha(checkpoint),head_initial_sha256=initial,updates=400,training_examples=409600,optimizer_states=len(state),finite_weights_moments=True,full50_epoch_goal_and_shuffle_rng_replayed=True,original_raw_action_dataset=True,geometry_source_sha256=cfg['feature_metadata']['source_sha256'],train_seconds=summary['train_seconds'],peak_vram_gib=summary['peak_vram_gib']))
                print('goalpolicy independent endpoint',seed,geometry,arm,'PASS',flush=True)
        assert len({initials[s,geom,arm] for s,geom,arm in initials if s==seed})==1
        for geometry in g.GEOMETRIES:
            a,b=firsts[seed,geometry,'GC-IDM'],firsts[seed,geometry,'GCBC-MATCHED']
            assert a['indices']==b['indices'] and a['goal_indices']==b['goal_indices']
    assert len(set(initials.values()))==3
    result=dict(completed=True,training_runs=18,records=records,all_independent_source_heads_retained=True,within_source_geometry_arm_initializations_common=True,gcidm_gcbc_goal_samples_common=True,scope='Frozen priors differ in objective and budget. Raw physical single-step action regression; published GC-IDM component reused, no novelty or complete paper reproduction. Validation split shares episodes, only optimization diagnostic. No control result inferred.',script_sha256=g.sha(__file__))
    out=g.ROOT/'20261005-E14-goalpolicy-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');g.save(out/'result.json',result)
    g.save(g.WB/'results/E14_20261005_goal_policy_endpoint_audit.json',result)


if __name__=='__main__':torch.set_num_threads(4);main()
