"""Independent all-four predictive-object initialization and sample accounting."""
import gc
import json
import shutil
import numpy as np
import torch
import predictive_object as r
from experience_transfer_control_audit import sha,read,save


def main():
    torch.set_num_threads(4);records=[];initials=[];first=[]
    for geometry in ['PRED','VALUE']:
        feature=r.m.ROOT/f'20261005-E13-object-{geometry}-features';meta=read(feature/'config.json')
        starts=np.load(feature/'starts.npy');assert len(starts)==5795
        assert sha(feature/'starts.npy')==meta['array_sha256']['starts'] and sha(feature/'features.npy')==meta['array_sha256']['features'] and sha(feature/'actions.npy')==meta['array_sha256']['actions']
        prior=torch.load(r.g.SOURCES[geometry],map_location='cpu',weights_only=False)['state_dict']
        assert sha(r.g.SOURCES[geometry])==meta['source_sha256']
        for arm in r.ARMS:
            name=f'20261005-E13-object-{geometry}-{arm}-A100-s0';run=r.m.ROOT/name;cfg=read(run/'config.json');summary=read(run/'summary.json')
            assert read(run/'complete.json')==dict(completed=True,geometry=geometry,arm=arm,updates=2825)
            assert not (run/'failure.json').exists() and cfg['script_sha256']==sha(r.__file__) and cfg['feature_metadata']==meta
            checkpoint=r.m.HF/name/'u2825.ckpt';assert sha(checkpoint)==summary['checkpoint_sha256']
            c=torch.load(checkpoint,map_location='cpu',weights_only=False);assert c['steps']==2825 and c['geometry']==geometry and c['arm']==arm
            frozen={k:v for k,v in c['state_dict'].items() if k.startswith(r.g.PREFIX)}
            assert all(torch.equal(v,prior[k]) for k,v in frozen.items())
            assert r.state_hash(frozen)==summary['frozen_phi_sha256']==meta['frozen_phi_sha256']
            assert all(torch.isfinite(v).all() for v in c['state_dict'].values())
            model=r.Model(c['config'],geometry)
            model.load_state_dict(c['state_dict'],strict=True)
            initial=torch.load(r.m.HF/name/'initial_head.pt',map_location='cpu',weights_only=False)
            constructed=r.Model(c['config'],geometry)
            assert set(initial)==set(constructed.core.state_dict()) and all(torch.equal(v,constructed.core.state_dict()[k]) for k,v in initial.items())
            initials.append(r.state_hash(initial));assert initials[-1]==cfg['head_initial_sha256']
            opt=c['optimizer'];assert len(opt['state'])==summary['optimizer_states']==len(list(model.core.parameters()))
            assert all(int(v['step'])==2825 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in opt['state'].values())
            assert len(opt['param_groups'])==1 and opt['param_groups'][0]['lr']==5e-5 and opt['param_groups'][0]['weight_decay']==.001
            rng=np.random.default_rng(113100)
            for step in range(2825):
                ids=rng.choice(starts,128,replace=True).tolist()
                if step==0:
                    first.append(ids);assert ids==read(run/'first_ids.json')
            assert rng.bit_generator.state==c['sampler']==summary['final_sampler']
            assert summary['total_clips']==361600 and summary['total_future_targets']==1808000
            for device in ['cpu','cuda']:
                pre=read(r.m.ROOT/f'20261005-E13-object-{geometry}-{device}-preflight-retry1/controls.json')
                assert pre['passed'] and pre['script_sha256']==sha(r.__file__) and pre['vendor_module_sha256']==sha(r.VENDOR/'module.py')
                assert all(x['head_initial_sha256']==initials[-1] and x['max_full_cost_error']==0 and x['causal_error']<1e-5 for x in pre['records'])
            records.append(dict(geometry=geometry,arm=arm,checkpoint_sha256=summary['checkpoint_sha256'],head_initial_sha256=initials[-1],frozen_phi_bit_exact=True,optimizer_states=len(opt['state']),updates=2825,first_ids_final_rng_exact=True,summary=summary))
            print('object endpoint audit',geometry,arm,'PASS',flush=True)
            del model,constructed,c,initial,opt;gc.collect()
    assert len(set(initials))==1 and all(x==first[0] for x in first)
    result=dict(completed=True,training_runs=4,records=records,all_four_capacity_and_initial_head_exact=True,all_four_first_batches_and_final_samplers_equal=True,
        scope='Independent source/frozenphi/feature arrays, initial head, strict full checkpoint, optimizer and sampling audit; priors differ, one source, no control or scientific novelty inference.',script_sha256=sha(__file__))
    out=r.m.ROOT/'20261005-E13-object-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');save(out/'result.json',result);save(r.m.WB/'results/E13_20261005_predictive_object_endpoint_audit.json',result)


if __name__=='__main__':main()
