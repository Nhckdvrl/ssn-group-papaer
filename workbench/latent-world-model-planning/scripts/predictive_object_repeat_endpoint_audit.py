"""Independent fixed-budget checks for every repeat endpoint, including low seeds."""
import gc
import shutil
import numpy as np
import torch
import predictive_object_repeat as r
from experience_transfer_control_audit import read,save,sha


def main():
    torch.set_num_threads(4);records=[];initials={};firsts={};samplers={}
    for seed in [1,2]:
        r.set_seed(seed)
        for geometry in ['PRED','VALUE']:
            feature=r.m.ROOT/f'20261005-E13-object-{geometry}-features-s{seed}';meta=read(feature/'config.json');starts=np.load(feature/'starts.npy')
            assert meta['train_seed']==seed and len(starts)==5795 and meta['geometry_checkpoint']==str(r.g.SOURCES[geometry])
            assert all(sha(feature/f'{key}.npy')==value for key,value in meta['array_sha256'].items())
            assert sha(r.g.SOURCES[geometry])==meta['source_sha256']
            prior=torch.load(r.g.SOURCES[geometry],map_location='cpu',weights_only=False)['state_dict']
            for arm in ['DIRECT','LOCAL']:
                name=f'20261005-E13-object-{geometry}-{arm}-A100-s{seed}';run=r.m.ROOT/name;cfg=read(run/'config.json');summary=read(run/'summary.json')
                assert read(run/'complete.json')==dict(completed=True,geometry=geometry,arm=arm,seed=seed,updates=2825)
                assert cfg['train_seed']==seed and cfg['head_seed']==113000+seed and cfg['sampler_seed']==113100+seed
                assert cfg['feature_metadata']==meta and cfg['script_sha256']==sha(r.__file__) and not (run/'failure.json').exists()
                checkpoint=r.m.HF/name/'u2825.ckpt';assert sha(checkpoint)==summary['checkpoint_sha256']
                c=torch.load(checkpoint,map_location='cpu',weights_only=False)
                assert c['steps']==2825 and c['train_seed']==seed and c['geometry']==geometry and c['arm']==arm
                frozen={k:v for k,v in c['state_dict'].items() if k.startswith(r.g.PREFIX)}
                assert all(torch.equal(v,prior[k]) for k,v in frozen.items()) and r.state_hash(frozen)==summary['frozen_phi_sha256']==meta['frozen_phi_sha256']
                assert all(torch.isfinite(v).all() for v in c['state_dict'].values())
                model=r.Model(c['config'],geometry);initial=torch.load(r.m.HF/name/'initial_head.pt',map_location='cpu',weights_only=False)
                assert set(initial)==set(model.core.state_dict()) and all(torch.equal(v,model.core.state_dict()[k]) for k,v in initial.items())
                current=r.state_hash(initial);initials.setdefault(seed,current);assert current==initials[seed]==cfg['head_initial_sha256']
                model.load_state_dict(c['state_dict'],strict=True);opt=c['optimizer']
                assert len(opt['state'])==len(list(model.core.parameters()))==summary['optimizer_states']
                assert all(int(v['step'])==2825 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in opt['state'].values())
                assert len(opt['param_groups'])==1 and opt['param_groups'][0]['lr']==5e-5 and opt['param_groups'][0]['weight_decay']==.001
                rng=np.random.default_rng(113100+seed)
                for step in range(2825):
                    ids=rng.choice(starts,128,replace=True).tolist()
                    if step==0:firsts.setdefault(seed,ids);assert ids==firsts[seed]==read(run/'first_ids.json')
                samplers.setdefault(seed,rng.bit_generator.state);assert rng.bit_generator.state==samplers[seed]==c['sampler']==summary['final_sampler']
                assert summary['total_clips']==361600 and summary['total_future_targets']==1808000
                for device in ['cpu','cuda']:
                    pre=read(r.m.ROOT/f'20261005-E13-object-{geometry}-{device}-preflight-s{seed}/controls.json')
                    assert pre['passed'] and pre['script_sha256']==sha(r.__file__) and pre['vendor_module_sha256']==sha(r.VENDOR/'module.py')
                    assert all(v['head_initial_sha256']==initials[seed] and v['max_full_cost_error']==0 and v['causal_error']<1e-5 for v in pre['records'])
                records.append(dict(seed=seed,geometry=geometry,arm=arm,checkpoint_sha256=summary['checkpoint_sha256'],initial_head_sha256=current,all_frozen_phi_exact=True,all_optimizer_moments_finite=True,all_first_batch_and_final_rng_exact=True,summary=summary))
                print('repeat endpoint audit',seed,geometry,arm,'PASS',flush=True);del model,c,opt,initial;gc.collect()
    assert len(set(initials.values()))==2 and firsts[1]!=firsts[2] and samplers[1]!=samplers[2]
    result=dict(completed=True,training_runs=8,records=records,independent_head_and_sample_seeds=True,within_source_four_cells_common_initialization_and_samples=True,scope='Fixed source1/2 independent representation/head training, all sources retained. Decoder targets/history/budgets unchanged from original port; source0 separate endpoint audit. No efficacy or novel method assertion.',script_sha256=sha(__file__))
    out=r.m.ROOT/'20261005-E13-object-repeat-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');save(out/'result.json',result);save(r.m.WB/'results/E13_20261005_predictive_object_repeat_endpoint_audit.json',result)


if __name__=='__main__':main()
