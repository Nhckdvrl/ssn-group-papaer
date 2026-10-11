"""Full 22-group matched controller audit; keep training sources and tasks paired."""
import json
import shutil
from pathlib import Path
import numpy as np
import bounded_control as b

ROOT=Path('/home/xiang/.cache/latent-wm-results')
ARMS=['ABS','RESIDUAL','FULL-AD']

if __name__=='__main__':
    bank=ROOT/'20261004-E20-fresh-control-bank48';ledger=json.loads((bank/'ledger.json').read_text())
    roster=[(arm,s) for s in range(3) for arm in ARMS]+[('VGIQL-JOINT',0),('VGIQL-SEPARATE',0)]
    groups=[];counts=[];arrays={};checkpoints={}
    for arm,seed in roster:
        for interface in ['physical','native']:
            run=ROOT/f'20261004-matched-control-{arm}-s{seed}-{interface}-RTX'
            assert json.loads((run/'complete.json').read_text())==dict(completed=True,n=48,model_unchanged=True) and not (run/'failure.json').exists()
            cfg=json.loads((run/'config.json').read_text());context=json.loads((run/'matched_loader.json').read_text())
            assert context['arm']==arm and context['seed']==seed and context['loader_sha256']==b.sha(Path(__file__).with_name('matched_control_queue.py'))
            assert cfg['interface']==interface and cfg['model_training_updates']==5650 and cfg['bank_ledger_sha256']==b.sha(bank/'ledger.json')
            checkpoint=cfg['checkpoint']
            if checkpoint not in checkpoints:checkpoints[checkpoint]=b.sha(checkpoint)
            assert checkpoints[checkpoint]==cfg['checkpoint_sha256']==context['train_checkpoint_sha256']
            source=ROOT/context['source_training_run']
            assert json.loads((source/'complete.json').read_text())['completed'] and json.loads((source/'summary.json').read_text())['checkpoint_sha256']==checkpoints[checkpoint]
            rows=json.loads((run/'rows.json').read_text());assert [r['anchor'] for r in rows]==list(range(48))
            for row,entry in zip(rows,ledger):
                trace=run/f'trace_{row["anchor"]:03d}.npz';assert b.sha(trace)==row['trace_sha256'];d=np.load(trace)
                assert row['episode']==entry['episode'] and row['goal_span']==entry['goal_span'] and row['env_steps']<=100
                assert d['states'].shape==(row['env_steps']+1,2) and d['actions'].shape==(row['env_steps'],2)
                assert np.isfinite(d['states']).all() and np.isfinite(d['actions']).all()
                assert np.array_equal(d['states'][0],np.load(bank/f'factual_states_{row["anchor"]:03d}.npy')[0])
                assert row['success']==bool((np.linalg.norm(d['states']-entry['goal_state'],axis=-1)<16).any())
                assert sum(v['executed_steps'] for v in row['decisions'])==row['env_steps']
                if interface=='physical':assert (np.abs(d['actions'])<=1).all()
            summaries=json.loads((run/'summary.json').read_text())
            for s in summaries:assert s['n']==24 and s['successes']==sum(r['success'] for r in rows if r['goal_span']==s['goal_span'])
            arrays[(arm,seed,interface)]=np.asarray([r['success'] for r in rows],dtype=float)
            counts.append(dict(arm=arm,seed=seed,interface=interface,near=sum(r['success'] for r in rows[:24]),far=sum(r['success'] for r in rows[24:]),n_per_tier=24,new_env_steps=sum(r['env_steps'] for r in rows)))
            groups.append(dict(arm=arm,seed=seed,interface=interface,config=cfg,loader=context,rows=rows,artifact_directory=str(run)))
            print('matched control audit',arm,seed,interface,'PASS',flush=True)
    assert len({v['config']['hardware'] for v in groups})==1
    rng=np.random.default_rng(109900);si=rng.integers(0,3,(10000,3))
    near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));all_ix=np.concatenate([near,far],1);effects=[]
    for interface in ['physical','native']:
        for arm,reference in [('RESIDUAL','ABS'),('FULL-AD','ABS'),('FULL-AD','RESIDUAL')]:
            delta=np.stack([arrays[(arm,s,interface)]-arrays[(reference,s,interface)] for s in range(3)])
            for tier,ix in [('all',all_ix),('near',near),('far',far)]:
                values=delta if tier=='all' else delta[:,:24] if tier=='near' else delta[:,24:]
                draws=delta[si[:,:,None],ix[:,None,:]].mean((1,2))
                effects.append(dict(interface=interface,arm=arm,reference=reference,tier=tier,mean_delta=float(values.mean()),source_deltas=values.mean(1).tolist(),paired_source_anchor_bootstrap_95=np.quantile(draws,[.025,.975]).tolist()))
        for arm in ['VGIQL-JOINT','VGIQL-SEPARATE']:
            for reference in ['ABS','VGIQL-JOINT'] if arm=='VGIQL-SEPARATE' else ['ABS']:
                delta=arrays[(arm,0,interface)]-arrays[(reference,0,interface)]
                draws=delta[all_ix].mean(1)
                effects.append(dict(interface=interface,arm=arm,reference=reference,tier='all',mean_delta=float(delta.mean()),paired_episode_bootstrap_95=np.quantile(draws,[.025,.975]).tolist(),train_seed_count=1))
    result=dict(completed=True,model_endpoints=11,controller_groups=22,episodes=1056,counts=counts,effects=effects,groups=groups,
        audit=dict(all_locked_48_retained=True,all_trace_hashes_and_physical_success_recomputed=True,same_hardware_ledger_and_budget=True,all_train_eval_checkpoints_and_explicit_loaders_match=True),
        scope='Matched local constant-LR development, not original-paper numeric reproduction. ABS/RES/FULL share3 train sources and48 tasks; paired source+anchor CIs are exploratory, not144 independent tasks. Value arms only one train source and separate-phase exposure differs. Physical/native jointly differ in initialization coordinate/scale and bounds. No second-task or novelty confirmation.')
    out=ROOT/'20261005-E01-E14-matched-control-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');b.save(out/'result.json',result)
    b.save(Path(__file__).resolve().parents[1]/'results/E01_E14_20261005_matched_control_results.json',result)
    print(json.dumps(counts),flush=True)
