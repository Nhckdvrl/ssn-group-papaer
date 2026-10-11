"""A12 independent saved endpoints, initializations and full clip RNG streams."""
import shutil
import numpy as np
import torch
import predictive_object_pusht as a
from experience_transfer_control_audit import ROOT, WB, read, save, sha
from fixed_data_train_seed import state_hash


def main():
    feature_cfg=read(a.CACHE/'config.json');starts=[]
    for row in feature_cfg['layout']:starts.extend(range(row['cache_row'],row['cache_row']+row['frames']-35))
    starts=np.asarray(starts); records=[];initials=[];norm=ROOT/'20261002-pusht-native-s0/action_normalization.npz'
    for arm in ['DIRECT','LOCAL','OPEN']:
        source=ROOT/a.name(arm);cfg=read(source/'config.json');summary=read(source/'summary.json')
        assert read(source/'complete.json')==dict(completed=True,task='pusht',arm=arm,train_seed=0,updates=2825)
        assert read(ROOT/(a.name(arm)+'-pipeline')/'complete.json')==dict(completed=True,arm=arm)
        assert not (source/'failure.json').exists()
        assert cfg['script_sha256']==sha(a.__file__)==sha(source/'used.py')
        assert cfg['rollout_component_sha256']==sha(a.rollout.__file__) and cfg['repeat_component_sha256']==sha(a.r.__file__)
        assert cfg['source_loader_sha256']==sha(a.t.__file__) and cfg['vendor_sha256']==sha(a.r.VENDOR/'module.py')
        assert cfg['data_metadata']['feature_metadata']==feature_cfg and cfg['data_metadata']['legal_starts']==len(starts)
        assert cfg['data_metadata']['normalizer_sha256']==sha(norm)==feature_cfg['unused_cem_action_normalization_sha256']
        for device in ['cpu','cuda']:
            pre=read(ROOT/(a.name(arm)+f'-{device}-preflight')/'controls.json')
            assert pre['passed'] and pre['script_sha256']==sha(a.__file__) and pre['manual_loss_exact']
            assert pre['target_not_prediction_input'] and pre['head_initial_sha256']==cfg['head_initial_sha256']
        path=a.HF/a.name(arm)/'u2825.ckpt';assert sha(path)==summary['checkpoint_sha256']
        c=torch.load(path,map_location='cpu',weights_only=False)
        assert (c['steps'],c['arm'],c['train_seed'])==(2825,arm,0) and c['manifest']==cfg['data_metadata']['manifest']
        net=a.Model();initial=state_hash(net.core.state_dict());initials.append(initial)
        saved_initial=torch.load(a.HF/a.name(arm)/'initial_head.pt',map_location='cpu',weights_only=False)
        assert saved_initial.keys()==net.core.state_dict().keys()
        assert all(torch.equal(v,net.core.state_dict()[k]) for k,v in saved_initial.items())
        assert initial==state_hash(saved_initial)==cfg['head_initial_sha256']==summary['head_initial_sha256']
        frozen=net.frozen_hash()
        assert frozen==cfg['frozen_phi_sha256']==summary['frozen_phi_sha256']
        for key,value in net.state_dict().items():
            if key.startswith(('encoder.','projector.')):assert torch.equal(c['state_dict'][key],value)
        net.load_state_dict(c['state_dict'],strict=True)
        assert net.frozen_hash()==frozen and all(torch.isfinite(v).all() for v in net.state_dict().values())
        opt=c['optimizer'];params=list(net.core.parameters());assert len(opt['state'])==len(params)==summary['optimizer_states']
        assert opt['param_groups'][0]['params']==list(range(len(params)))
        assert opt['param_groups'][0]['lr']==5e-5 and opt['param_groups'][0]['weight_decay']==.001
        for index,value in opt['state'].items():
            assert int(value['step'])==2825
            for moment in ['exp_avg','exp_avg_sq']:
                assert value[moment].shape==params[index].shape and torch.isfinite(value[moment]).all()
        rng=np.random.default_rng(113100)
        for update in range(2825):
            ix=rng.choice(starts,128,replace=True)
            if update==0:assert ix.tolist()==read(source/'first_ids.json')
        assert rng.bit_generator.state==c['sampler']==summary['final_sampler']
        assert summary['total_clips']==361600 and summary['total_future_targets']==1808000
        records.append(dict(arm=arm,checkpoint_sha256=sha(path),head_initial_sha256=initial,frozen_phi_sha256=frozen,
            legal_starts=len(starts),full2825_sampler_exact=True,optimizer_steps_all2825=True,all_moments_finite=True,frozen_all_parameters_buffers_exact=True))
        print('Push object independent endpoint audit',arm,'PASS',flush=True)
    assert len(set(initials))==1
    result=dict(completed=True,models=3,records=records,script_sha256=sha(__file__),trainer_sha256=sha(a.__file__),scope='All fixed final endpoints retained; one trainseed on shared86 facts and same published phi, unknown encoder pretraining. Endpoint and data integrity only, no efficacy or novel method evidence.')
    out=ROOT/'20261005-E13-pusht-object-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');save(out/'result.json',result)
    save(WB/'results/E13_20261005_pusht_object_endpoint_audit.json',result)


if __name__=='__main__':torch.set_num_threads(4);main()
