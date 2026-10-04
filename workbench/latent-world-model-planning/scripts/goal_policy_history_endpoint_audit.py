"""G2 independent sampler, initial parameters and full optimizer audit."""
import gc
import shutil
import numpy as np
import torch
import goal_policy_history as h
g=h.g


def main():
    torch.set_num_threads(4);records=[]
    for task in ['nav','pusht']:
        data=h.load(task);z,a,ep,end,starts,val,meta=data;initials=[];samplers=[]
        assert g.read(g.ROOT/f'20261005-E14-history-{task}-pipeline/complete.json')==dict(completed=True,task=task,training_runs=2)
        for arm in h.ARMS:
            name=f'20261005-E14-history-{task}-{arm}-RTX-s0';run=g.ROOT/name;cfg=g.read(run/'config.json');summary=g.read(run/'summary.json')
            assert g.read(run/'complete.json')==dict(completed=True,task=task,arm=arm,epochs=50) and not (run/'failure.json').exists()
            assert cfg['script_sha256']==g.sha(h.__file__)==g.sha(run/'used.py') and cfg['feature_metadata']==meta
            assert cfg['official_model_sha256']==g.sha(g.VENDOR/'idm/model.py') and cfg['train_starts']==starts.tolist() and cfg['validation_starts']==val.tolist()
            path=g.HF/name/'epoch50.ckpt';assert g.sha(path)==summary['checkpoint_sha256']
            c=torch.load(path,map_location='cpu',weights_only=False);initial=torch.load(g.HF/name/'initial.pt',map_location='cpu',weights_only=False)
            fresh=h.model('cpu');assert set(fresh.state_dict())==set(initial) and all(torch.equal(v,fresh.state_dict()[k]) for k,v in initial.items())
            initials.append(h.state_hash(initial));assert initials[-1]==cfg['initial_sha256']==summary['initial_sha256']
            assert (c['task'],c['arm'],c['updates'])==(task,arm,350)
            fresh.load_state_dict(c['state_dict'],strict=True);assert all(torch.isfinite(v).all() for v in c['state_dict'].values())
            opt=c['optimizer'];assert len(opt['state'])==summary['optimizer_states']==len(list(fresh.parameters()))
            assert all(int(v['step'])==350 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in opt['state'].values())
            rng=np.random.default_rng(115100);shuffle=np.random.default_rng(115200);step=0
            for epoch in range(50):
                order=shuffle.permutation(starts)
                for begin in range(0,len(order)-1024+1,1024):
                    ix=order[begin:begin+1024];horizon=rng.integers(1,np.minimum(50,end[ix]-1-ix)+1);gi=ix+horizon
                    assert (ep[ix-10]==ep[ix]).all() and (ep[gi]==ep[ix]).all() and np.isfinite(a[ix]).all()
                    if step==0:
                        saved=g.read(run/'first_batch.json');assert saved['indices']==ix.tolist() and saved['goal_indices']==gi.tolist() and saved['physical_horizon']==horizon.tolist()
                        expected=ix[:,None]+[-10,-5,0] if arm=='TRUE-HISTORY' else np.repeat(ix[:,None],3,1)
                        assert saved['history_indices']==expected.tolist()
                    step+=1
            assert step==350 and rng.bit_generator.state==c['goal_rng'] and shuffle.bit_generator.state==c['shuffle_rng']
            assert summary['training_examples']==358400;samplers.append((c['goal_rng'],c['shuffle_rng']))
            for device in ['cpu','cuda']:
                pre=g.read(g.ROOT/f'20261005-E14-history-{task}-{device}-preflight/controls.json')
                assert pre['passed'] and pre['matched_goal_targets_capacity_initial'] and pre['script_sha256']==g.sha(h.__file__)
            records.append(dict(task=task,arm=arm,checkpoint_sha256=summary['checkpoint_sha256'],initial_sha256=initials[-1],updates=350,training_examples=358400,all50epoch_sampler_firstbatch_optimizer_exact=True))
            print('History policy independent endpoint audit',task,arm,'PASS',flush=True);del fresh,c,initial,opt;gc.collect()
        assert len(set(initials))==1 and samplers[0]==samplers[1]
    result=dict(completed=True,training_runs=4,records=records,script_sha256=g.sha(__file__),scope='Independent full endpoint and sample provenance audit; no deployment result or novel method inference.')
    out=g.ROOT/'20261005-E14-history-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');g.save(out/'result.json',result);g.save(g.WB/'results/E14_20261005_history_policy_endpoint_audit.json',result)


if __name__=='__main__':main()
