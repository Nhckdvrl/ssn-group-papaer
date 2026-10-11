"""Recompute all fresh BASE1000 successes from physical traces."""
import json
import shutil
from pathlib import Path
import numpy as np
import bounded_control as b

ROOT=Path('/home/xiang/.cache/latent-wm-results')
if __name__=='__main__':
    bank=ROOT/'20261004-E20-fresh-control-bank48';ledger=json.loads((bank/'ledger.json').read_text())
    groups=[];effects=[];rng=np.random.default_rng(109800);indices=np.concatenate([rng.integers(0,24,(10000,24)),rng.integers(24,48,(10000,24))],1)
    for interface in ['native','physical']:
        run=ROOT/f'20261005-E16-BASE1000-fresh-{interface}-RTX'
        assert json.loads((run/'complete.json').read_text())==dict(completed=True,n=48,model_unchanged=True)
        assert not (run/'failure.json').exists()
        cfg=json.loads((run/'config.json').read_text());rows=json.loads((run/'rows.json').read_text());summary=json.loads((run/'summary.json').read_text())
        assert cfg['interface']==interface and cfg['bank_ledger_sha256']==b.sha(bank/'ledger.json') and cfg['model_training_updates']==56500
        assert b.sha(cfg['checkpoint'])==cfg['checkpoint_sha256'] and [r['anchor'] for r in rows]==list(range(48))
        for row,entry in zip(rows,ledger):
            trace=run/f'trace_{row["anchor"]:03d}.npz';assert b.sha(trace)==row['trace_sha256'];d=np.load(trace)
            assert row['episode']==entry['episode'] and row['goal_span']==entry['goal_span'] and row['env_steps']<=100
            assert d['states'].shape==(row['env_steps']+1,2) and d['actions'].shape==(row['env_steps'],2)
            assert np.isfinite(d['states']).all() and np.isfinite(d['actions']).all()
            assert np.array_equal(d['states'][0],np.load(bank/f'factual_states_{row["anchor"]:03d}.npy')[0])
            assert row['success']==bool((np.linalg.norm(d['states']-entry['goal_state'],axis=-1)<16).any())
            assert sum(v['executed_steps'] for v in row['decisions'])==row['env_steps']
            if interface=='physical':assert (np.abs(d['actions'])<=1).all()
        for s in summary:assert s['n']==24 and s['successes']==sum(r['success'] for r in rows if r['goal_span']==s['goal_span'])
        for reference in ['BASE-s0','PLAIN-s0']:
            ref=ROOT/f'20261004-E20-control-{reference}-{interface}-RTX';other=json.loads((ref/'rows.json').read_text())
            assert json.loads((ref/'config.json').read_text())['bank_ledger_sha256']==cfg['bank_ledger_sha256']
            delta=np.array([int(a['success'])-int(c['success']) for a,c in zip(rows,other)])
            effects.append(dict(interface=interface,reference=reference,mean_delta=float(delta.mean()),paired_episode_bootstrap_95=np.quantile(delta[indices].mean(1),[.025,.975]).tolist()))
        groups.append(dict(interface=interface,config=cfg,summary=summary,rows=rows,artifact_directory=str(run)))
    result=dict(completed=True,episodes=96,groups=groups,effects=effects,all_trace_hash_initial_states_and_success_recomputed=True,
        scope='Fresh48 development, one large-data training source. 1000 episodes/56500 updates versus100/5650; data and compute jointly change. Interfaces also differ in initialization coordinates/scale and bounds. Not data-only causal gain or independent training confirmation.')
    out=ROOT/'20261005-E16-fresh-exposure-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');b.save(out/'result.json',result)
    b.save(Path(__file__).resolve().parents[1]/'results/E16_20261005_fresh_exposure_control.json',result);print('fresh exposure audit PASS 96episodes',flush=True)
