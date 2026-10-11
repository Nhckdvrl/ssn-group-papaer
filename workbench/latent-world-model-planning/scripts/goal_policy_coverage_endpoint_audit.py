"""G3 complete data/compute matrix, independent random streams and optimizer audit."""
import gc
import shutil
import numpy as np
import torch
import goal_policy_coverage as c
g=c.g


def main():
    torch.set_num_threads(4);records=[];initials=[]
    assert g.read(g.ROOT/'20261005-E14-coverage-pipeline/complete.json')==dict(completed=True,training_runs=4)
    for episodes in [86,860]:
        data=c.load(episodes);z,a,ep,end,starts,val,meta=data
        for updates in [400,4000]:
            name=f'20261005-E14-coverage-e{episodes}-u{updates}-RTX-s0';run=g.ROOT/name;cfg=g.read(run/'config.json');summary=g.read(run/'summary.json')
            assert g.read(run/'complete.json')==dict(completed=True,episodes=episodes,updates=updates) and not (run/'failure.json').exists()
            assert cfg['script_sha256']==g.sha(c.__file__)==g.sha(run/'used.py') and cfg['feature_metadata']==meta and cfg['train_starts']==starts.tolist() and cfg['validation_starts']==val.tolist()
            path=g.HF/name/f'u{updates}.ckpt';assert g.sha(path)==summary['checkpoint_sha256'];checkpoint=torch.load(path,map_location='cpu',weights_only=False)
            assert (checkpoint['episodes'],checkpoint['updates'])==(episodes,updates)
            initial=torch.load(g.HF/name/'initial.pt',map_location='cpu',weights_only=False);fresh=g.model(0,'cpu')
            assert set(initial)==set(fresh.state_dict()) and all(torch.equal(v,fresh.state_dict()[k]) for k,v in initial.items())
            initials.append(c.state_hash(initial));assert initials[-1]==cfg['initial_sha256']==summary['initial_sha256'];fresh.load_state_dict(checkpoint['state_dict'],strict=True)
            assert all(torch.isfinite(v).all() for v in checkpoint['state_dict'].values())
            opt=checkpoint['optimizer'];assert len(opt['state'])==summary['optimizer_states']==len(list(fresh.parameters()))
            assert all(int(v['step'])==updates and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in opt['state'].values())
            assert checkpoint['scheduler']['last_epoch']==updates and np.isclose(opt['param_groups'][0]['lr'],.00001)
            indices=np.random.default_rng(115200);goals=np.random.default_rng(115100)
            for step in range(updates):
                ix=indices.choice(starts,1024,replace=True);h=goals.integers(1,np.minimum(50,end[ix]-1-ix)+1);gi=ix+h
                assert (ep[ix]==ep[gi]).all() and np.isfinite(a[ix]).all()
                if step==0:
                    first=g.read(run/'first_batch.json');assert first['indices']==ix.tolist() and first['goal_indices']==gi.tolist() and first['physical_horizon']==h.tolist()
            assert indices.bit_generator.state==checkpoint['indices_rng'] and goals.bit_generator.state==checkpoint['goal_rng'] and summary['training_examples']==updates*1024
            for device in ['cpu','cuda']:
                pre=g.read(g.ROOT/f'20261005-E14-coverage-{device}-preflight/controls.json');assert pre['passed'] and pre['first86_subset_exact'] and pre['script_sha256']==g.sha(c.__file__)
            records.append(dict(episodes=episodes,updates=updates,frames=len(z),checkpoint_sha256=summary['checkpoint_sha256'],initial_sha256=initials[-1],first_batch_final_rng_optimizer_exact=True))
            print('Coverage policy independent endpoint audit',episodes,updates,'PASS',flush=True);del initial,checkpoint,opt,fresh;gc.collect()
    assert len(set(initials))==1
    result=dict(completed=True,training_runs=4,records=records,script_sha256=g.sha(__file__),scope='All fixed data/compute endpoints retained; one seed, known GCBC and published frozen phi overlap unknown; no deployment inference.')
    out=g.ROOT/'20261005-E14-coverage-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');g.save(out/'result.json',result);g.save(g.WB/'results/E14_20261005_coverage_policy_endpoint_audit.json',result)


if __name__=='__main__':main()
