"""Independent native trace, actual causal history and source audit of INTACT."""
import shutil
from pathlib import Path
import numpy as np
from sklearn.preprocessing import StandardScaler
from experience_transfer_control_audit import ROOT,WB,read,save,sha


def main():
    script=WB/'scripts/intact_published_control_v3.py';groups=[];metrics={};counts=[]
    for task in ['tworoom','pusht']:
        bank=ROOT/('20261004-E20-fresh-control-bank48' if task=='tworoom' else '20261005-E20-pusht-fresh-control-bank48');ledger=read(bank/'ledger.json')
        norm=np.load(ROOT/f'20261002-{task}-native-s0/action_normalization.npz');scaler=StandardScaler();scaler.mean_=norm['mean'];scaler.scale_=norm['std'];scaler.var_=scaler.scale_**2;scaler.n_features_in_=2
        for device in ['cpu','cuda']:
            c=read(ROOT/f'20261005-E01-intact-v3-{task}-{device}-preflight/controls.json')
            assert c['passed'] and c['script_sha256']==sha(script) and c['manual_full_actor_rollout_exact'] and c['all48_state_pixels_exact']
        for interface in ['native','physical']:
            run=ROOT/f'20261005-E01-intact-v3-{task}-{interface}-control';assert read(run/'complete.json')==dict(completed=True,n=48,model_unchanged=True)
            assert not (run/'failure.json').exists();cfg=read(run/'config.json');rows=read(run/'rows.json');source=cfg['source']
            assert cfg['script_sha256']==sha(script)==sha(run/'used.py') and cfg['bank_ledger_sha256']==sha(bank/'ledger.json') and (cfg['budget'],cfg['history_frames'],cfg['execution_primitive_steps'])==(100,1,25)
            assert sha(source['checkpoint']['path'])==source['checkpoint']['sha256']
            assert source['normalizer_sha256']==sha(ROOT/f'20261002-{task}-native-s0/action_normalization.npz')
            assert all(source==read(ROOT/f'20261005-E01-intact-v3-{task}-{device}-preflight/controls.json')['source'] for device in ['cpu','cuda'])
            assert [r['anchor'] for r in rows]==list(range(48));valid=[]
            for row,entry in zip(rows,ledger):
                j=row['anchor'];path=run/f'trace_{j:03d}.npz';assert row['trace_sha256']==sha(path)
                with np.load(path) as trace:state=trace['states'];actions=trace['actions']
                n=row['env_steps'];assert 0<=n<=100 and state.shape==(n+1,2 if task=='tworoom' else 25) and actions.shape==(n,2)
                assert np.isfinite(state).all() and np.isfinite(actions).all() and np.array_equal(state[0],np.load(bank/f'factual_states_{j:03d}.npy')[0])
                assert (row['episode'],row['goal_span'])==(entry['episode'],entry['goal_span']);goal=np.asarray(entry['goal_state'])
                if task=='tworoom':reached=np.linalg.norm(state-goal,axis=-1)<16
                else:
                    angle=np.abs(state[:,4]-goal[4]);reached=(np.linalg.norm(state[:,:4]-goal[:4],axis=-1)<20)&(np.minimum(angle,2*np.pi-angle)<np.pi/9)
                assert bool(reached[0])==row['initial_success'] and bool(reached.any())==row['success']
                if n:assert not reached[:-1].any()
                if not row['success']:assert n==100
                past=np.asarray(entry['warm_actions'],dtype=np.float32);offset=0
                for k,decision in enumerate(row['decisions']):
                    length=decision['executed_steps'];assert decision['decision']==k and 1<=length<=25
                    assert np.array_equal(np.asarray(decision['previous_executed_actions'],dtype=np.float32),past[-5:])
                    proposal=np.asarray(decision['standardized_proposal'],dtype=np.float32);assert proposal.shape==(25,2)
                    issued=scaler.inverse_transform(proposal);actual=np.clip(issued,-1,1) if interface=='physical' else issued
                    assert np.array_equal(actual[:length],actions[offset:offset+length])
                    assert decision['out_of_bounds_components']==int((np.abs(actual[:length])>1).sum())
                    past=np.concatenate([past,actions[offset:offset+length].astype(np.float32)]);offset+=length
                assert offset==n and (row['initial_success'] or len(row['decisions'])>0)
                if interface=='physical':assert (np.abs(actions)<=1).all()
                valid.append(float(row['success']))
            metrics[task,interface]=np.asarray(valid)
            counts.append(dict(task=task,interface=interface,n=48,successes=int(sum(valid)),initial_successes=sum(r['initial_success'] for r in rows),near_successes=sum(r['success'] for r in rows[:24]),far_successes=sum(r['success'] for r in rows[24:]),executed_env_steps=sum(r['env_steps'] for r in rows)))
            groups.append(dict(config=cfg,rows_sha256=sha(run/'rows.json'),artifact_directory=str(run)))
            print('Complete INTACT causal trace/source audit',task,interface,'PASS',flush=True)
    rng=np.random.default_rng(117901);ix=rng.integers(0,48,(10000,48));effects=[]
    for task in ['tworoom','pusht']:
        delta=metrics[task,'physical']-metrics[task,'native'];effects.append(dict(task=task,comparison='output-clip minus native',mean_delta=float(delta.mean()),paired_anchor_bootstrap_95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist()))
    result=dict(completed=True,episodes=192,groups=groups,counts=counts,effects=effects,script_sha256=sha(__file__),scope='Full published joint E5 source0, all48 per task, original native position/angle, every previous action from actual warm/execution. H1 native paper model; local100 budget differs official50, dataset/encoder pretraining unknown/unmatched. No numerical paper replication, training-only causality, novelty, or training-seed confidence.')
    out=ROOT/'20261005-E01-intact-v3-control-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');save(out/'result.json',result)
    result['full_audit_artifact']=str(out/'result.json');save(WB/'results/E01_20261005_intact_published_control_results.json',result)


if __name__=='__main__':main()
