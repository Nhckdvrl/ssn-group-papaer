"""Independent full-roster RC-aux trace, head, scaler and source audit."""
import json
import shutil
import numpy as np
import torch
import rcaux_full_control as rc
from experience_transfer_control_audit import ROOT, WB, sha, read, save, verify, counts


def main():
    torch.set_num_threads(4); model=rc.load('cpu')
    assert len(model.state_dict())==312 and len([k for k in model.state_dict() if k.startswith('reachability_head.')])==9
    mean,std,statistics=rc.stats('/tmp/latent-wm-data/tworoom.h5')
    for device in ['cpu','cuda']:
        pre=read(ROOT/f'20261005-E01-rcaux-full-{device}-preflight/controls.json')
        assert pre['passed'] and pre['script_sha256']==sha(rc.__file__) and pre['checkpoint_sha256']==rc.SHA
        assert np.array_equal(mean,pre['statistics']['action_mean']) and np.array_equal(std,pre['statistics']['action_std'])
        assert all(r['max_native_cost_error']==0 and r['manual_full_head_exact'] for r in pre['records'])
    groups=[]; totals=[]; arrays={}
    for history,weight in rc.CONDITIONS:
        for interface in ['native','physical']:
            name=f'20261005-E01-rcaux-full-H{history}-W{weight:.2f}-{interface}-RTX'
            group,arr=verify(ROOT/name,rc.BANK,'nav',interface); cfg=group['config']
            assert cfg['history']==history and cfg['reachability_weight']==weight and cfg['checkpoint_sha256']==rc.SHA
            assert cfg['script_sha256']==sha(rc.__file__) and cfg['controller_sha256']==sha(WB/'scripts/bounded_control.py')
            assert np.array_equal(mean,cfg['statistics']['action_mean']) and np.array_equal(std,cfg['statistics']['action_std'])
            assert cfg['statistics']['finite_rows']==statistics['finite_rows'] and cfg['statistics']['eval_source_sha256']==statistics['eval_source_sha256']
            groups.append(group);arrays[history,weight,interface]=arr;totals.append(counts(group,history=history,weight=weight,interface=interface))
            print('RC full trajectory audit',history,weight,interface,'PASS',flush=True)
    assert len({g['config']['hardware'] for g in groups})==1
    rng=np.random.default_rng(112600); near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],1);effects=[]
    for interface in ['native','physical']:
        contrasts=[((h,.85),(h,0.),f'head ON-OFF H{h}') for h in [1,3]]+[((3,w),(1,w),f'H3-H1 W{w}') for w in [.85,0.]]
        for arm,reference,label in contrasts:
            delta=arrays[arm+(interface,)]-arrays[reference+(interface,)]
            for tier,ix in [('all',allix),('near',near),('far',far)]:
                values=delta if tier=='all' else delta[:24] if tier=='near' else delta[24:]
                effects.append(dict(interface=interface,contrast=label,tier=tier,mean_delta=float(values.mean()),paired_anchor_bootstrap_95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist(),train_sources=1))
    result=dict(completed=True,controller_groups=8,episodes=384,counts=totals,effects=effects,groups=groups,full_head_preserved=True,model_keys=312,checkpoint_sha256=rc.SHA,normalization_recomputed_exact=True,
        scope='Published full RC-aux one checkpoint; training/data unmatched. Original criterion .85 from pinned object/README. H1 protocol and H3 explicit port; 100-step development budget, not original paper replication. Head ON/OFF comparison retains same backbone/normalization/candidates; original all48 and both interfaces retained. Not novel method confirmation.',script_sha256=sha(__file__))
    out=ROOT/'20261005-E01-rcaux-full-control-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');save(out/'result.json',result)
    for group in groups:
        group.pop('rows')
    result['full_audit_artifact']=str(out/'result.json');save(WB/'results/E01_20261005_rcaux_full_control_results.json',result)
    print(json.dumps(totals),flush=True)


if __name__=='__main__': main()
