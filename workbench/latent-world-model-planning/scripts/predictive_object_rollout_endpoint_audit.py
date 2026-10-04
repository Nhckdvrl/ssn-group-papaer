"""Independent full six-source A10 endpoints and common target/sample audit."""
import gc
import shutil
import numpy as np
import torch
import predictive_object_rollout as a
from experience_transfer_control_audit import read,sha,save
r=a.r


def main():
    torch.set_num_threads(4);records=[]
    for seed in range(3):
        for geometry in ['PRED','VALUE']:
            d,meta=a.data(geometry,seed);name=a.name(geometry,seed)+'-A100';run=r.m.ROOT/name
            assert read(run/'complete.json')==dict(completed=True,geometry=geometry,seed=seed,updates=2825) and not (run/'failure.json').exists()
            cfg=read(run/'config.json');summary=read(run/'summary.json');assert cfg['script_sha256']==sha(a.__file__)==sha(run/'used.py')
            assert cfg['feature_metadata']==meta and cfg['repeat_component_sha256']==sha(r.__file__) and cfg['original_component_sha256']==sha(a.original.__file__)
            path=r.m.HF/name/'u2825.ckpt';assert sha(path)==summary['checkpoint_sha256']
            c=torch.load(path,map_location='cpu',weights_only=False);assert (c['geometry'],c['train_seed'],c['arm'],c['steps'])==(geometry,seed,'OPEN-ROLLOUT',2825)
            model=r.Model(c['config'],geometry);initial=torch.load(r.m.HF/name/'initial_head.pt',map_location='cpu',weights_only=False)
            assert set(initial)==set(model.core.state_dict()) and all(torch.equal(v,model.core.state_dict()[k]) for k,v in initial.items())
            original=r.m.ROOT/f'20261005-E13-object-{geometry}-DIRECT-A100-s{seed}'
            assert r.state_hash(initial)==cfg['head_initial_sha256']==read(original/'config.json')['head_initial_sha256']
            model.load_state_dict(c['state_dict'],strict=True);assert model.frozen_hash()==meta['frozen_phi_sha256']==summary['frozen_phi_sha256']
            assert all(torch.isfinite(v).all() for v in c['state_dict'].values())
            prior=torch.load(r.g.SOURCES[geometry],map_location='cpu',weights_only=False)['state_dict']
            assert all(torch.equal(v,prior[k]) for k,v in c['state_dict'].items() if k.startswith(r.g.PREFIX))
            opt=c['optimizer'];assert len(opt['state'])==summary['optimizer_states']==len(list(model.core.parameters()))
            assert all(int(v['step'])==2825 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in opt['state'].values())
            rng=np.random.default_rng(113100+seed)
            for step in range(2825):
                ix=rng.choice(d['starts'],128,replace=True)
                if step==0:assert ix.tolist()==read(run/'first_ids.json')==read(original/'first_ids.json')
            assert rng.bit_generator.state==c['sampler']==summary['final_sampler']
            assert (summary['total_clips'],summary['total_future_targets'])==(361600,1808000)
            for device in ['cpu','cuda']:
                pre=read(r.m.ROOT/(a.name(geometry,seed)+f'-{device}-preflight')/'controls.json')
                assert pre['passed'] and pre['manual_loss_exact'] and pre['last_loss_gradient_to_first_prediction'] and pre['target_not_model_input'] and pre['script_sha256']==sha(a.__file__)
            records.append(dict(geometry=geometry,seed=seed,checkpoint_sha256=summary['checkpoint_sha256'],updates=2825,initial_and_sampling_match_DIRECT=True,frozen_prior_full_exact=True,full_optimizer_finite=True))
            print('Rollout independent endpoint audit',geometry,seed,'PASS',flush=True);del model,c,initial,opt,prior;gc.collect()
    result=dict(completed=True,training_runs=6,records=records,script_sha256=sha(__file__),scope='Known BPTT strong baseline; full source/init/optimizer/sampler audit. No closed-loop result or universal geometry claim.')
    out=r.m.ROOT/'20261005-E13-rollout-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');save(out/'result.json',result);save(r.m.WB/'results/E13_20261005_rollout_endpoint_audit.json',result)


if __name__=='__main__':main()
