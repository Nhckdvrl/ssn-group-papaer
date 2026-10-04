"""Independent complete experience/Nav and transfer/Push trajectory audits."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
import numpy as np

ROOT=Path('/home/xiang/.cache/latent-wm-results')
WB=Path(__file__).resolve().parents[1]
HASHES={}
def sha(p):
    p=Path(p)
    if str(p) not in HASHES:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(1048576),b''):h.update(block)
        HASHES[str(p)]=h.hexdigest()
    return HASHES[str(p)]
def read(p): return json.loads(Path(p).read_text())
def save(p,v): Path(p).write_text(json.dumps(v,indent=2)+'\n')
def verify(run,bank,task,interface):
    assert read(run/'complete.json')==dict(completed=True,n=48,model_unchanged=True)
    assert not (run/'failure.json').exists()
    cfg=read(run/'config.json'); rows=read(run/'rows.json'); ledger=read(bank/'ledger.json')
    assert cfg['interface']==interface and cfg['bank_ledger_sha256']==sha(bank/'ledger.json')
    assert sha(cfg['checkpoint'])==cfg['checkpoint_sha256']
    assert [r['anchor'] for r in rows]==list(range(48))
    for row,entry in zip(rows,ledger):
        j=row['anchor'];trace=run/f'trace_{j:03d}.npz'
        assert sha(trace)==row['trace_sha256']
        with np.load(trace) as d:
            state,actions=d['states'],d['actions']
        n=row['env_steps'];assert isinstance(n,int) and 0<=n<=100
        assert state.shape==(n+1,2 if task=='nav' else 25) and actions.shape==(n,2)
        assert np.isfinite(state).all() and np.isfinite(actions).all()
        assert np.array_equal(state[0],np.load(bank/f'factual_states_{j:03d}.npy')[0])
        assert row['episode']==entry['episode'] and row['goal_span']==entry['goal_span']
        goal=np.asarray(entry['goal_state'])
        if task=='nav': reached=np.linalg.norm(state-goal,axis=-1)<16
        else:
            # Independent native Push criterion; velocities/forces never define success.
            assert ((state[:,4]>=0)&(state[:,4]<2*np.pi)).all()
            delta=np.abs(state[:,4]-goal[4]);angle=np.minimum(delta,2*np.pi-delta)
            reached=(np.linalg.norm(state[:,:4]-goal[:4],axis=-1)<20)&(angle<np.pi/9)
        assert row['success']==bool(reached.any())
        if 'initial_success' in row:assert row['initial_success']==bool(reached[0])
        row['audited_initial_success']=bool(reached[0])
        assert sum(d['executed_steps'] for d in row['decisions'])==n
        if n:assert not reached[:-1].any() and row['success']==bool(reached[-1])
        if interface=='physical': assert (np.abs(actions)<=1).all()
        if task=='pusht':
            assert sum(d['issued_out_of_bounds_components'] for d in row['decisions'])==int((np.abs(actions)>1).sum())
    for s in read(run/'summary.json'):
        subset=[r for r in rows if r['goal_span']==s['goal_span']]
        assert s['n']==len(subset)==24 and s['successes']==sum(r['success'] for r in subset)
    return dict(config=cfg,rows=rows,artifact_directory=str(run)),np.asarray([r['success'] for r in rows],float)
def counts(group,**kw):
    rows=group['rows'];return dict(**kw,near=sum(r['success'] for r in rows[:24]),far=sum(r['success'] for r in rows[24:]),n_per_tier=24,new_env_steps=sum(r['env_steps'] for r in rows),initial_successes=sum(r['audited_initial_success'] for r in rows))
def main(task):
    bank=ROOT/('20261004-E20-fresh-control-bank48' if task=='nav' else '20261005-E20-pusht-fresh-control-bank48')
    groups=[];totals=[];arrays={};refs=[]
    if task=='nav':
        for s in range(3):
            for interface in ['native','physical']:
                for arm in ['IID-BRANCH','REPLAY-ONLY','MIX','PLAIN','BASE']:
                    run=ROOT/(f'20261005-E20-experience-control-{arm}-s{s}-{interface}-RTX' if arm in ['IID-BRANCH','REPLAY-ONLY','MIX'] else f'20261004-E20-control-{arm}-s{s}-{interface}-RTX')
                    group,arr=verify(run,bank,task,interface)
                    if arm in ['IID-BRANCH','REPLAY-ONLY','MIX']:
                        context=read(run/'training_source.json'); source=ROOT/context['source_training_run']
                        assert context['arm']==arm and context['seed']==s and context['queue_sha256']==sha(WB/'scripts/experience_control_queue.py')
                        assert read(source/'complete.json')==dict(completed=True,arm=arm,seed=s,updates=2000)
                        assert group['config']['model_training_updates']==2000
                        assert group['config']['checkpoint_sha256']==next(v['checkpoint_sha256'] for v in read(source/'summary.json') if v['updates']==2000)
                        group['training_source']=context;groups.append(group)
                    else:refs.append(group)
                    arrays[arm,s,interface]=arr;totals.append(counts(group,arm=arm,seed=s,interface=interface))
                    print('control-audit',task,arm,s,interface,'PASS',flush=True)
    else:
        for arm in ['RELEASED','PLAIN','GLOBAL-SG','CENTER','DET-INVERSE','PROB-INVERSE','AD-REFERENCE']:
            for interface in ['native','physical']:
                run=ROOT/f'20261005-E20-pusht-control-{arm}-{interface}-RTX-s0'
                group,arr=verify(run,bank,task,interface);cfg=group['config']
                assert cfg['method']==arm and cfg['script_sha256']==sha(WB/'scripts/pusht_fresh_control.py') and cfg['controller_sha256']==sha(WB/'scripts/bounded_control.py')
                if arm not in ['RELEASED','AD-REFERENCE']:
                    source=ROOT/f'20261004-E20-joint-pusht-{arm}-RTX-s0'
                    assert read(source/'complete.json')==dict(completed=True,method=arm,seed=0,updates=2000)
                    assert cfg['checkpoint_sha256']==next(v['checkpoint_sha256'] for v in read(source/'summary.json') if v['updates']==2000)
                if arm=='RELEASED':assert cfg['checkpoint_sha256']=='0c095fc4a26856678f67bf299f261506b45f1a25fbdb4cbb8828b4a8281dc048'
                if arm=='AD-REFERENCE':assert cfg['checkpoint_sha256']=='e61130c558de9ed5c9c740a58ecb08a97c5c92473b45fd275a425fb46f281e9e'
                parity=read(run/'native_parity.json');group['native_parity']=parity
                arrays[arm,0,interface]=arr;groups.append(group);totals.append(counts(group,arm=arm,seed=0,interface=interface))
                print('control-audit',task,arm,interface,'PASS',flush=True)
    assert len({g['config']['hardware'] for g in groups+refs})==1
    rng=np.random.default_rng(110000 if task=='nav' else 110100)
    ns=3 if task=='nav' else 1;si=rng.integers(0,ns,(10000,ns));near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],1);effects=[]
    for interface in ['native','physical']:
        arms=['IID-BRANCH','REPLAY-ONLY','MIX'] if task=='nav' else ['PLAIN','GLOBAL-SG','CENTER','DET-INVERSE','PROB-INVERSE','AD-REFERENCE']
        references=['PLAIN','BASE'] if task=='nav' else ['RELEASED','PLAIN']
        for arm in arms:
            for reference in references:
                if arm==reference:continue
                delta=np.stack([arrays[arm,s,interface]-arrays[reference,s,interface] for s in range(ns)])
                for tier,ix in [('all',allix),('near',near),('far',far)]:
                    draws=delta[si[:,:,None],ix[:,None,:]].mean((1,2))
                    values=delta if tier=='all' else delta[:,:24] if tier=='near' else delta[:,24:]
                    effects.append(dict(interface=interface,arm=arm,reference=reference,tier=tier,mean_delta=float(values.mean()),source_deltas=values.mean(1).tolist(),paired_source_anchor_bootstrap_95=np.quantile(draws,[.025,.975]).tolist(),train_sources=ns))
    result=dict(completed=True,task=task,controller_groups=len(groups),episodes=48*len(groups),counts=totals,effects=effects,groups=groups,reference_groups=refs,audit=dict(full_roster_complete=True,all_48_retained=True,all_trace_hashes_initial_states_native_success_recomputed=True,all_checkpoint_training_sources_match=True,same_hardware_and_ledger=True),scope='Development comparisons; shared48tasks, not independent method confirmation. Nav3 independent train sources; Push one transfer trainseed and unknown released pretraining split. Interfaces jointly change initialization coordinate/scale and bounds. Published AD-reference training unmatched. No novel method/science claim.')
    name='20261005-E20-experience-control-audit' if task=='nav' else '20261005-E20-pusht-fresh-control-audit'
    out=ROOT/name;assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');save(out/'result.json',result)
    save(WB/'results'/('E20_20261005_experience_control_results.json' if task=='nav' else 'E20_20261005_pusht_fresh_control_results.json'),result)
    print(json.dumps(totals),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('task',choices=['nav','pusht']);main(p.parse_args().task)
