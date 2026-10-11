"""All36 goal-policy groups; both budgets and source/anchor-paired comparisons."""
import json
import shutil
import numpy as np
import goal_policy_baseline as g
from experience_transfer_control_audit import verify,counts


def main():
    assert g.read(g.WB/'results/E14_20261005_goal_policy_endpoint_audit.json')['completed']
    bank=g.ROOT/'20261004-E20-fresh-control-bank48';groups=[];refs=[];totals=[];arrays={};arrays50={}
    for seed in range(3):
        assert g.read(g.ROOT/f'20261005-E14-goalpolicy-control-pipeline-s{seed}/complete.json')==dict(completed=True,seed=seed,episodes=576)
        for geometry in g.GEOMETRIES:
            for device in ['cpu','cuda']:
                pre=g.read(g.ROOT/f'20261005-E14-goalpolicy-{geometry}-{device}-control-preflight-s{seed}/controls.json')
                assert pre['passed'] and pre['script_sha256']==g.sha(g.WB/'scripts/goal_policy_control.py')
                assert pre['official_policy_sha256']==g.sha(g.VENDOR/'eval_idm.py') and pre['all48_initial_pixels_states_exact']
            for arm in g.ARMS:
                source=g.ROOT/f'20261005-E14-goalpolicy-{geometry}-{arm}-A100-s{seed}';cfg=g.read(source/'config.json')
                for interface in ['native','physical']:
                    name=f'20261005-E14-goalpolicy-control-{geometry}-{arm}-{interface}-RTX-s{seed}'
                    group,arr=verify(g.ROOT/name,bank,'nav',interface);c=group['config']
                    assert c['script_sha256']==g.sha(g.WB/'scripts/goal_policy_control.py')==g.sha(g.ROOT/name/'used.py')
                    assert (c['geometry'],c['arm'],c['train_seed'],c['budget'],c['executed_steps_per_decision'])==(geometry,arm,seed,100,1)
                    assert c['trainer_sha256']==g.sha(g.__file__) and c['vendor_model_sha256']==g.sha(g.VENDOR/'idm/model.py')
                    assert c['checkpoint_sha256']==g.read(source/'summary.json')['checkpoint_sha256'] and c['geometry_source_sha256']==cfg['feature_metadata']['source_sha256']
                    arr50=[]
                    for row in group['rows']:
                        assert len(row['decisions'])==row['env_steps']
                        for k,d in enumerate(row['decisions']):
                            h=0 if arm=='GCBC-MATCHED' else 1 if arm=='PAIRWISE' else min(100-k,50)
                            assert d['decision']==k and d['executed_steps']==1 and d['remaining_horizon']==h
                            assert np.isfinite(d['issued_action']).all()
                        trace=np.load(g.ROOT/name/f'trace_{row["anchor"]:03d}.npz');issued=np.asarray([d['issued_action'] for d in row['decisions']]).reshape(-1,2)
                        assert np.array_equal(trace['actions'],np.clip(issued,-1,1) if interface=='physical' else issued)
                        goal=np.asarray(g.read(bank/'ledger.json')[row['anchor']]['goal_state'])
                        by50=bool((np.linalg.norm(trace['states'][:51]-goal,axis=-1)<16).any())
                        assert by50==row['success_by50'];arr50.append(float(by50))
                    key=geometry+'-'+arm;arrays[key,seed,interface]=arr;arrays50[key,seed,interface]=np.asarray(arr50)
                    groups.append(group);totals.append(dict(**counts(group,geometry=geometry,arm=arm,seed=seed,interface=interface),success_by50=int(sum(arr50))))
                    print('goalpolicy trajectory audit',seed,geometry,arm,interface,'PASS',flush=True)
    for seed in range(3):
        for geometry in g.GEOMETRIES:
            for obj in ['DIRECT','LOCAL']:
                for interface in ['native','physical']:
                    prefix='object-repeat-v2-control' if seed else 'object-control'
                    group,arr=verify(g.ROOT/f'20261005-E13-{prefix}-{geometry}-{obj}-{interface}-RTX-s{seed}',bank,'nav',interface)
                    key=geometry+'-'+obj;arrays[key,seed,interface]=arr;refs.append(group)
                    totals.append(counts(group,reference=key,seed=seed,interface=interface))
    assert len(groups)==36 and len({v['config']['hardware'] for v in groups+refs})==1
    rng=np.random.default_rng(115500);si=rng.integers(0,3,(10000,3));near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],axis=1);effects=[]
    for interface in ['native','physical']:
        contrasts=[]
        for geometry in g.GEOMETRIES:
            contrasts += [(geometry+'-GC-IDM',geometry+'-'+a) for a in ['GCBC-MATCHED','PAIRWISE','DIRECT','LOCAL']]
        contrasts += [('VALUE-'+a,'PRED-'+a) for a in g.ARMS]
        for budget,table in [(100,arrays),(50,arrays50)]:
            for arm,reference in contrasts:
                if (arm,0,interface) not in table or (reference,0,interface) not in table:continue
                delta=np.stack([table[arm,s,interface]-table[reference,s,interface] for s in range(3)])
                for tier,ix in [('all',allix),('near',near),('far',far)]:
                    values=delta if tier=='all' else delta[:,:24] if tier=='near' else delta[:,24:]
                    draws=delta[si[:,:,None],ix[:,None,:]].mean((1,2));effects.append(dict(interface=interface,controller_budget=100,evaluation_prefix_steps=budget,arm=arm,reference=reference,tier=tier,mean_delta=float(values.mean()),source_deltas=values.mean(1).tolist(),paired_source_anchor_bootstrap_95=np.quantile(draws,[.025,.975]).tolist()))
    result=dict(completed=True,controller_groups=36,episodes=1728,counts=totals,effects=effects,groups=groups,reference_groups=refs,script_sha256=g.sha(__file__),scope='The 50-step numbers are the first50 actions of the100-step-budget controller, NOT separately rerun50-step-budget controllers. Horizon policy uses min(100-steps,50). Known GC-IDM/GCBC baselines, three independent training sources and same48 shared development tasks. SAME hindsight goals/capacity/init/data for zero-horizon GCBC contrast; PAIRWISE changes goal distribution; CEM references also differ in training targets/capacity/budget and real-feedback cadence. Raw policy native/clip interfaces do not change proposal coordinates unlike CEM. Validation frame split is not held-out episode confirmation; no novel method or paper-reproduction claim.')
    out=g.ROOT/'20261005-E14-goalpolicy-control-audit-v2';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');g.save(out/'result.json',result)
    for group in groups+refs:group.pop('rows')
    result['full_audit_artifact']=str(out/'result.json');g.save(g.WB/'results/E14_20261005_goal_policy_control_results.json',result);print(json.dumps(totals),flush=True)


if __name__=='__main__':main()
