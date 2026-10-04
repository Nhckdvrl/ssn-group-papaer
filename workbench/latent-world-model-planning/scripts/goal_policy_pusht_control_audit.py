"""Independent full-roster Push goal-policy trace and provenance audit."""
import json
import shutil
import numpy as np
import goal_policy_baseline as g
from experience_transfer_control_audit import verify, counts


def main():
    assert g.read(g.WB/'results/E14_20261005_pusht_goal_policy_endpoint_audit.json')['completed']
    pipeline=g.ROOT/'20261005-E14-goalpolicy-pusht-control-pipeline-s0'
    assert g.read(pipeline/'complete.json')['completed']
    bank=g.ROOT/'20261005-E20-pusht-fresh-control-bank48'
    control=g.WB/'scripts/goal_policy_pusht_control.py'
    for device in ['cpu','cuda']:
        pre=g.read(g.ROOT/f'20261005-E14-goalpolicy-pusht-{device}-control-preflight-s0/controls.json')
        assert pre['passed'] and pre['all48_full25D_initial_state_and_pixels_exact']
        assert pre['script_sha256']==g.sha(control)
        assert pre['shared_policy_component_sha256']==g.sha(g.WB/'scripts/goal_policy_control.py')
        assert pre['official_policy_sha256']==g.sha(g.VENDOR/'eval_idm.py')
        assert {v['arm'] for v in pre['records']}==set(g.ARMS)
    ledger=g.read(bank/'ledger.json');groups=[];refs=[];totals=[];arrays={};prefixes={}
    for arm in g.ARMS:
        training=g.ROOT/f'20261005-E14-goalpolicy-RELEASED-{arm}-A100-s0'
        traincfg=g.read(training/'config.json')
        for interface in ['native','physical']:
            run=g.ROOT/f'20261005-E14-goalpolicy-pusht-control-{arm}-{interface}-RTX-s0'
            group,arr=verify(run,bank,'pusht',interface);cfg=group['config']
            assert (cfg['task'],cfg['arm'],cfg['train_seed'],cfg['budget'],cfg['history'])==('pusht',arm,0,100,1)
            assert cfg['script_sha256']==g.sha(control)==g.sha(run/'used.py')
            for field,path in [('policy_component_sha256','goal_policy_control.py'),('trainer_sha256','goal_policy_baseline.py'),('source_adapter_sha256','goal_policy_pusht_adapter.py'),('restore_sha256','pusht_fresh_control.py')]:
                assert cfg[field]==g.sha(g.WB/'scripts'/path)
            assert g.sha(cfg['geometry_checkpoint'])==cfg['geometry_source_sha256']==traincfg['feature_metadata']['source_sha256']
            assert cfg['checkpoint_sha256']==g.read(training/'summary.json')['checkpoint_sha256']
            by50=[]
            for row in group['rows']:
                trace=np.load(run/f'trace_{row["anchor"]:03d}.npz');states=trace['states'];decisions=row['decisions']
                assert len(decisions)==row['env_steps']
                for step,d in enumerate(decisions):
                    horizon=0 if arm=='GCBC-MATCHED' else 1 if arm=='PAIRWISE' else min(100-step,50)
                    assert (d['decision'],d['executed_steps'],d['remaining_horizon'])==(step,1,horizon)
                issued=np.asarray([d['issued_action'] for d in decisions]).reshape(-1,2)
                assert np.isfinite(issued).all()
                assert np.array_equal(trace['actions'],np.clip(issued,-1,1) if interface=='physical' else issued)
                goal=np.asarray(ledger[row['anchor']]['goal_state']);subset=states[:51]
                diff=np.abs(subset[:,4]-goal[4]);angle=np.minimum(diff,2*np.pi-diff)
                reached=(np.linalg.norm(subset[:,:4]-goal[:4],axis=-1)<20)&(angle<np.pi/9)
                hit=bool(reached.any());assert hit==row['success_by50'];by50.append(float(hit))
            groups.append(group);arrays[arm,interface]=arr;prefixes[arm,interface]=np.asarray(by50)
            totals.append(dict(**counts(group,arm=arm,seed=0,interface=interface),success_by50=int(sum(by50))))
            print('Push goal-policy independent audit',arm,interface,'PASS',flush=True)
    for arm in ['RELEASED','PLAIN','AD-REFERENCE']:
        for interface in ['native','physical']:
            run=g.ROOT/f'20261005-E20-pusht-control-{arm}-{interface}-RTX-s0'
            group,arr=verify(run,bank,'pusht',interface)
            assert group['config']['script_sha256']==g.sha(g.WB/'scripts/pusht_fresh_control.py')
            refs.append(group);arrays[arm,interface]=arr;totals.append(counts(group,reference=arm,seed=0,interface=interface))
    assert len(groups)==6 and len({v['config']['hardware'] for v in groups+refs})==1
    rng=np.random.default_rng(115600);near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],1);effects=[]
    contrasts=[('GC-IDM',a) for a in ['GCBC-MATCHED','PAIRWISE','RELEASED','PLAIN','AD-REFERENCE']]+[('GCBC-MATCHED','RELEASED'),('PAIRWISE','RELEASED')]
    for interface in ['native','physical']:
        for prefix,table in [(100,arrays),(50,prefixes)]:
            for arm,ref in contrasts:
                if (arm,interface) not in table or (ref,interface) not in table:continue
                delta=table[arm,interface]-table[ref,interface]
                for tier,ix in [('all',allix),('near',near),('far',far)]:
                    value=delta if tier=='all' else delta[:24] if tier=='near' else delta[24:]
                    draws=delta[ix].mean(1)
                    effects.append(dict(interface=interface,controller_budget=100,evaluation_prefix_steps=prefix,arm=arm,reference=ref,tier=tier,mean_delta=float(value.mean()),paired_anchor_bootstrap_95=np.quantile(draws,[.025,.975]).tolist(),train_sources=1))
    result=dict(completed=True,controller_groups=6,episodes=288,counts=totals,effects=effects,groups=groups,reference_groups=refs,script_sha256=g.sha(__file__),audit=dict(full_roster_complete=True,all_48_retained=True,full25D_initial_states_native_angle_position_success_recomputed=True,raw_vs_clip_actions_exact=True,source_and_checkpoint_hashes_match=True),scope='One exploratory policy training seed on first86 factual episodes, encoder published pretraining overlap unknown. Known controllers; capacity, head supervision, training budget and every-step observation feedback differ from CEM. Actual RTX despite legacy A100 training directory basename. 50-step readout is prefix of100-budget controller, not separate50-budget policy. Shared48 development tasks; no novel method, causal mechanism or complete paper replication claim.')
    out=g.ROOT/'20261005-E14-goalpolicy-pusht-control-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');g.save(out/'result.json',result)
    for group in groups+refs:group.pop('rows')
    result['full_audit_artifact']=str(out/'result.json');g.save(g.WB/'results/E14_20261005_pusht_goal_policy_control_results.json',result)
    print(json.dumps(totals),flush=True)


if __name__=='__main__':main()
