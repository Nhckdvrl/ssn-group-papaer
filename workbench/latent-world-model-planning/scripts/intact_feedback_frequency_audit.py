"""E18 independent all-frequency source, causal execution and paired utility audit."""
import shutil
import numpy as np
from sklearn.preprocessing import StandardScaler
from experience_transfer_control_audit import ROOT,WB,read,save,sha


def main():
    producer=WB/'scripts/intact_feedback_frequency.py';helper=WB/'scripts/intact_published_control_v3.py';counts=[];groups=[];vectors={}
    for task in ['tworoom','pusht']:
        bank=ROOT/('20261004-E20-fresh-control-bank48' if task=='tworoom' else '20261005-E20-pusht-fresh-control-bank48');ledger=read(bank/'ledger.json')
        norm=np.load(ROOT/f'20261002-{task}-native-s0/action_normalization.npz');scaler=StandardScaler();scaler.mean_=norm['mean'];scaler.scale_=norm['std'];scaler.var_=scaler.scale_**2;scaler.n_features_in_=2
        pre=read(ROOT/f'20261005-E18-intact-feedback-{task}-preflight/controls.json');assert pre['passed'] and pre['script_sha256']==sha(producer) and pre['helper_sha256']==sha(helper)
        assert [v['device'] for v in pre['records']]==['cpu','cuda'] and all(v['passed'] and v['model_unchanged'] and v['all48warm_exact'] for v in pre['records'])
        baseline=read(ROOT/f'20261005-E01-intact-v3-{task}-native-control/rows.json')
        for execution in [25,5,1]:
            run=ROOT/(f'20261005-E01-intact-v3-{task}-native-control' if execution==25 else f'20261005-E18-intact-feedback-{task}-EX{execution}')
            assert read(run/'complete.json')==dict(completed=True,n=48,model_unchanged=True) and not (run/'failure.json').exists()
            cfg=read(run/'config.json');rows=read(run/'rows.json');assert [v['anchor'] for v in rows]==list(range(48))
            assert cfg['bank_ledger_sha256']==sha(bank/'ledger.json') and cfg['budget']==100 and cfg['source']==pre['source']
            assert cfg['script_sha256']==sha(run/'used.py')==sha(helper if execution==25 else producer)
            if execution!=25:assert cfg['execution_steps']==execution and cfg['planning_steps']==25 and cfg['helper_sha256']==sha(helper)
            assert sha(cfg['source']['checkpoint']['path'])==cfg['source']['checkpoint']['sha256']
            valid=[];calls=[];time_seconds=[]
            for row,entry in zip(rows,ledger):
                j=row['anchor'];path=run/f'trace_{j:03d}.npz';assert row['trace_sha256']==sha(path)
                with np.load(path) as trace:state=trace['states'];actions=trace['actions']
                n=row['env_steps'];assert 0<=n<=100 and state.shape==(n+1,2 if task=='tworoom' else 25) and actions.shape==(n,2)
                assert np.isfinite(state).all() and np.isfinite(actions).all() and np.array_equal(state[0],np.load(bank/f'factual_states_{j:03d}.npy')[0])
                assert (row['episode'],row['goal_span'])==(entry['episode'],entry['goal_span']);goal=np.asarray(entry['goal_state'])
                if task=='tworoom':hit=np.linalg.norm(state-goal,axis=-1)<16
                else:
                    angle=np.abs(state[:,4]-goal[4]);hit=(np.linalg.norm(state[:,:4]-goal[:4],axis=-1)<20)&(np.minimum(angle,2*np.pi-angle)<np.pi/9)
                assert bool(hit[0])==row['initial_success'] and bool(hit.any())==row['success']
                if n:assert not hit[:-1].any()
                if not row['success']:assert n==100
                past=np.asarray(entry['warm_actions'],dtype=np.float32);offset=0
                for k,d in enumerate(row['decisions']):
                    length=d['executed_steps'];assert d['decision']==k and 1<=length<=execution
                    assert np.array_equal(np.asarray(d['previous_executed_actions'],dtype=np.float32),past[-5:])
                    proposal=np.asarray(d['standardized_proposal'],dtype=np.float32);assert proposal.shape==(25,2)
                    if k==0:assert np.array_equal(proposal,np.asarray(baseline[j]['decisions'][0]['standardized_proposal'],dtype=np.float32))
                    actual=scaler.inverse_transform(proposal)[:length];assert np.array_equal(actual,actions[offset:offset+length])
                    assert d['out_of_bounds_components']==int((np.abs(actual)>1).sum())
                    if execution!=25:assert np.isfinite(d['solver_seconds']) and d['solver_seconds']>0;time_seconds.append(d['solver_seconds'])
                    past=np.concatenate([past,actions[offset:offset+length].astype(np.float32)]);offset+=length
                assert offset==n;valid.append(float(row['success']));calls.append(len(row['decisions']))
            vectors[task,execution]=np.asarray(valid)
            counts.append(dict(task=task,execution_steps=execution,n=48,successes=int(sum(valid)),initial_successes=sum(r['initial_success'] for r in rows),near_successes=sum(r['success'] for r in rows[:24]),far_successes=sum(r['success'] for r in rows[24:]),executed_env_steps=sum(r['env_steps'] for r in rows),replan_calls=sum(calls),mean_replan_calls=float(np.mean(calls)),synchronized_solver_seconds_sum=float(sum(time_seconds)) if time_seconds else None,mean_solver_seconds=float(np.mean(time_seconds)) if time_seconds else None))
            groups.append(dict(config=cfg,rows_sha256=sha(run/'rows.json'),artifact_directory=str(run)))
            print('Full feedback frequency causal/source audit',task,execution,'PASS',flush=True)
    rng=np.random.default_rng(119901);effects=[]
    for task in ['tworoom','pusht']:
        for execution,reference in [(5,25),(1,25),(1,5)]:
            delta=vectors[task,execution]-vectors[task,reference]
            for tier,ids in [('all',np.arange(48)),('near',np.arange(24)),('far',np.arange(24,48))]:
                ix=rng.choice(ids,(10000,len(ids)),replace=True);effects.append(dict(task=task,execution_steps=execution,reference_execution_steps=reference,tier=tier,n=len(ids),mean_delta=float(delta[ids].mean()),helped=int((delta[ids]>0).sum()),harmed=int((delta[ids]<0).sum()),paired_anchor_bootstrap_95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist(),train_sources=1))
    result=dict(completed=True,new_episodes=192,reference_episodes=96,groups=groups,counts=counts,effects=effects,script_sha256=sha(__file__),scope='Full published joint source0, same starts/goal/100steps/full25plan and native actions; only execution prefix differs. Every actual causal past5 and first plan exact. One trainseed/48 development goals per task, no router, novelty or numerical paper replication. Baseline timing unavailable; new solver calls include unused future computation, no optimal speedup claim.')
    out=ROOT/'20261005-E18-intact-feedback-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');save(out/'result.json',result);result['full_audit_artifact']=str(out/'result.json');save(WB/'results/E18_20261005_intact_feedback_frequency_results.json',result)


if __name__=='__main__':main()
