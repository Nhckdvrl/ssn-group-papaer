"""Read-only checkpoint/initialization/accounting audit of all eleven endpoints."""
import gc
import json
import shutil
from pathlib import Path
import torch
import matched_learning as m


if __name__ == '__main__':
    torch.set_num_threads(4)
    roster = [(a,s) for s in range(3) for a in ['ABS','RESIDUAL','FULL-AD']]
    roster += [(arm,s) for s in range(3) for arm in ['VGIQL-JOINT','VGIQL-SEPARATE']]
    records, common, first_batches, shuffles = [], {}, {}, {}
    for arm,seed in roster:
        name = f'20261004-E01-matched-{arm}-A100-s{seed}' if not arm.startswith('VGIQL-') else f'20261004-E14-{arm}-A100-s{seed}'
        run, cache = m.ROOT/name, m.HF/name
        assert json.loads((run/'complete.json').read_text()) == dict(completed=True,training_updates=5650,simulator_episodes=0)
        assert not (run/'failure.json').exists()
        cfg = json.loads((run/'config.json').read_text()); summary = json.loads((run/'summary.json').read_text())
        assert cfg['script_sha256'] == m.digest(m.__file__) and cfg['official_train_sha256'] == m.digest(m.REPO/'train.py')
        assert cfg['arm']==arm and cfg['seed']==seed and cfg['updates']==5650 and cfg['batch_size']==128
        checkpoint = cache/'u5650.ckpt'; assert m.digest(checkpoint)==summary['checkpoint_sha256']
        c = torch.load(checkpoint,map_location='cpu',weights_only=False)
        assert c['steps']==5650 and c['matched_method']==arm and c['train_seed']==seed
        assert c['config']==cfg['architecture'] and c['manifest']==cfg['data_manifest']
        assert len(c['manifest']['base_episodes'])==100 and len(c['state_dict'])==(321 if arm=='FULL-AD' else 303)
        assert all(torch.isfinite(v).all() for v in c['state_dict'].values())
        initial=torch.load(cache/'initial_cpu.pt',map_location='cpu',weights_only=False)
        saved=torch.load(cfg['initial']['saved_initial_path'],map_location='cpu',weights_only=False) if 'saved_initial_path' in cfg['initial'] else None
        # Reconstruct the complete initial architecture in the official namespace.
        model, expected=m.make_model(c['config'],seed,arm)
        assert set(initial)==set(model.state_dict()) and all(torch.equal(initial[k],v) for k,v in model.state_dict().items())
        assert expected['common_initial_tensor_sha256']==cfg['initial']['common_initial_tensor_sha256']
        common.setdefault(seed,expected['common_initial_tensor_sha256']);assert common[seed]==expected['common_initial_tensor_sha256']
        first_batches.setdefault(seed,summary['first_clip_ids']);assert first_batches[seed]==summary['first_clip_ids']
        shuffles.setdefault(seed,summary['final_shuffle_rng']);assert shuffles[seed]==summary['final_shuffle_rng']==c['numpy_rng']
        expected_states=93 if arm=='VGIQL-SEPARATE' else 309 if arm=='FULL-AD' else 297
        expected_steps=2825 if arm=='VGIQL-SEPARATE' else 5650
        opt=c['optimizer'];assert len(opt['state'])==expected_states==summary['optimizer_states']
        assert all(int(v['step'])==expected_steps and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in opt['state'].values())
        assert len(opt['param_groups'])==1 and opt['param_groups'][0]['lr']==5e-5 and opt['param_groups'][0]['weight_decay']==1e-3
        if arm=='VGIQL-SEPARATE':
            phase=torch.load(cache/'value_phase_u2825.ckpt',map_location='cpu',weights_only=False)
            assert phase['steps']==2825 and len(phase['optimizer']['state'])==204
            assert all(int(v['step'])==2825 for v in phase['optimizer']['state'].values())
            assert all(torch.isfinite(v).all() for v in phase['state_dict'].values())
            assert all(torch.equal(v,c['state_dict'][k]) for k,v in phase['state_dict'].items() if k.startswith(('encoder.','projector.')))
            del phase
        records.append(dict(arm=arm,seed=seed,run_directory=str(run),checkpoint_sha256=summary['checkpoint_sha256'],
            complete_initial_tensor_exact=True,common_initial_sha256=common[seed],optimizer_states=expected_states,optimizer_steps=expected_steps,
            first_clip_ids=summary['first_clip_ids'],all_weights_and_moments_finite=True))
        del c,initial,model,saved,opt;gc.collect();print('matched endpoint audit',arm,seed,'PASS',flush=True)
    assert len(set(common.values()))==3
    result=dict(completed=True,training_runs=15,records=records,common_initial_per_source=True,first_batches_and_final_sampler_states_equal=True,
        script_sha256=m.digest(__file__),training_script_sha256=m.digest(m.__file__),
        scope='Checkpoint, initialization and optimizer/data accounting only. All are local constant-LR matched development; no original-paper numeric reproduction or efficacy assertion. Value arms three sources; separate phase exposure differs.')
    out=m.ROOT/'20261005-E14-three-seed-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py')
    m.dump(out/'result.json',result);m.dump(m.WB/'results/E14_20261005_three_seed_endpoint_audit.json',result)
