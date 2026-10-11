"""Read-only independent fixed-geometry and Push module endpoint accounting."""
import argparse
import gc
import json
from pathlib import Path
import numpy as np
import torch
from experience_transfer_control_audit import ROOT, WB, sha, read, save

HF=Path('/home/xiang/.cache/huggingface/latent-wm-trained')
PHI=('encoder.','projector.')


def main(mode):
    torch.set_num_threads(4)
    if mode=='geometry':
        import geometry_experience as trainer
        import matched_learning as m
        roster=[(g,a) for g in ['PRED','VALUE'] for a in ['FACT','MIX']]
        common=torch.load(HF/'E16_data_compute_s0/common_cpu_initial.pt',map_location='cpu',weights_only=False)
        expected_dynamic=m.state_hash({k:v for k,v in common.items() if not k.startswith(PHI)})
        cache=Path('/tmp/latent-wm-data/E16-base100-trainseed-cache')
        # Reconstruct all wholeepisode starts from the saved offsets, independently of training sampler.
        layout=read(cache/'cache_manifest.json')['layout']
        starts=np.concatenate([np.arange(v['cache_row'],v['cache_row']+v['frames']-35) for v in layout])
        assert len(starts)==5795
    else:
        import pusht_module_learning as trainer
        import effect_transfer as transfer
        roster=[(None,a) for a in ['DYNAMICS-ONLY','GEOMETRY-ONLY']]
        original,_,_,_,norm=transfer.load_source('cpu'); common=original.state_dict()
        assert sha(transfer.SOURCE)==transfer.SOURCE_SHA
    records=[]
    for geometry,arm in roster:
        name=f'20261005-E20-geometry-{geometry}-{arm}-A100-s0' if mode=='geometry' else f'20261005-E20-pusht-module-{arm}-A100-s0'
        run=ROOT/name; cfg=read(run/'config.json'); accounting=read(run/'accounting.json'); steps=2825 if mode=='geometry' else 2000
        expected_complete=dict(completed=True,arm=arm,seed=0,updates=steps)
        if geometry is not None: expected_complete['geometry']=geometry
        assert read(run/'complete.json')==expected_complete and not (run/'failure.json').exists()
        assert cfg['script_sha256']==sha(trainer.__file__)
        checkpoint=HF/name/f'u{steps}.ckpt'; digest=next(v['checkpoint_sha256'] for v in read(run/'summary.json') if v['updates']==steps)
        assert sha(checkpoint)==digest
        c=torch.load(checkpoint,map_location='cpu',weights_only=False)
        assert c['steps']==steps and len(c['state_dict'])==303
        assert all(torch.isfinite(v).all() for v in c['state_dict'].values())
        opt=c['optimizer']; nstates=204 if mode=='pusht' and arm=='GEOMETRY-ONLY' else 93
        assert len(opt['state'])==nstates and all(int(v['step'])==steps and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in opt['state'].values())
        assert len(opt['param_groups'])==1 and opt['param_groups'][0]['lr']==5e-5 and opt['param_groups'][0]['weight_decay']==1e-3
        if mode=='geometry':
            source=cfg['source']; assert source==c['geometry_source']
            assert sha(source['geometry_checkpoint'])==source['geometry_checkpoint_sha256']
            prior=torch.load(source['geometry_checkpoint'],map_location='cpu',weights_only=False)['state_dict']
            frozen={k:v for k,v in c['state_dict'].items() if k.startswith(PHI)}
            assert all(torch.equal(v,prior[k]) for k,v in frozen.items())
            assert m.state_hash(frozen)==source['frozen_geometry_sha256']==accounting['frozen_geometry_sha256']
            assert source['common_dynamic_initial_sha256']==expected_dynamic==accounting['common_dynamic_initial_sha256']
            brng=np.random.default_rng(110800); rrng=np.random.default_rng(110900); new=64 if arm=='MIX' else 0
            for step in range(steps):
                anchors=brng.integers(0,32,new); branches=brng.choice(np.array([0]+list(range(2,12))),new,replace=True); old=rrng.choice(starts,128-new,replace=True)
                if step==0:
                    assert read(run/'first_batch.json')==dict(branch_anchors=anchors.tolist(),branch_ids=branches.tolist(),replay_cache_starts=old.tolist(),new_count=new,old_count=128-new)
            assert brng.bit_generator.state==c['rng']['branch']==accounting['final_branch_rng']
            assert rrng.bit_generator.state==c['rng']['replay']==accounting['final_replay_rng']
            assert accounting['total_items']==361600 and accounting['branch_items']==new*steps and accounting['replay_items']==(128-new)*steps
        else:
            assert c['module_arm']==arm and cfg['source_sha256']==transfer.SOURCE_SHA and cfg['normalization_sha256']==norm
            assert cfg['initial_sha256']==transfer.e.state_hash(common)
            frozen={k:v for k,v in c['state_dict'].items() if k.startswith(PHI)==(arm=='DYNAMICS-ONLY')}
            assert all(torch.equal(v,common[k]) for k,v in frozen.items())
            assert transfer.e.state_hash(frozen)==cfg['frozen_sha256']==accounting['frozen_sha256']
            rng=np.random.default_rng(105800)
            for step in range(steps):
                anchors=rng.integers(0,32,8); branches=np.stack([rng.choice(np.array([0]+list(range(2,12))),4,replace=False) for _ in anchors])
                if step==0: assert read(run/'first_batch.json')==dict(anchors=anchors.tolist(),branches=branches.tolist())
            assert rng.bit_generator.state==c['rng']['sampler']==accounting['final_sampler_rng']
            assert accounting['branch_items']==64000 and accounting['optimizer_states']==nstates
        records.append(dict(geometry=geometry,arm=arm,checkpoint_sha256=digest,optimizer_states=nstates,updates=steps,frozen_parameters_and_buffers_bit_exact=True,first_batch_and_endpoint_rng_exact=True,all_weights_moments_finite=True,accounting=accounting))
        del c,opt,frozen; gc.collect(); print('module endpoint audit',mode,geometry,arm,'PASS',flush=True)
    out=ROOT/f'20261005-E20-{mode}-module-endpoint-audit'; assert not out.exists(); out.mkdir()
    import shutil
    shutil.copy2(__file__,out/'audit_used.py')
    result=dict(completed=True,mode=mode,training_runs=len(records),records=records,scope='Independent checkpoint, source, frozen parameter/buffer, optimizer, sampler and exposure accounting. Not a scientific efficacy or novelty claim.',script_sha256=sha(__file__))
    save(out/'result.json',result); save(WB/'results'/f'E20_20261005_{mode}_module_endpoint_audit.json',result)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['geometry','pusht']);main(p.parse_args().mode)
