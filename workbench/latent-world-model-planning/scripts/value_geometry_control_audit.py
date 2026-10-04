"""Complete value repetition and crossed-geometry controller matrices."""
import argparse
import json
import shutil
from pathlib import Path
import numpy as np
from experience_transfer_control_audit import ROOT,WB,verify,counts,sha,read,save

def main(mode):
 bank=ROOT/'20261004-E20-fresh-control-bank48';groups=[];totals=[];arrays={};effects=[]
 if mode=='value':
  roster=[(arm,s) for s in range(3) for arm in ['ABS','VGIQL-JOINT','VGIQL-SEPARATE']]
  for arm,s in roster:
   for interface in ['native','physical']:
    old=arm=='ABS' or s==0
    name=(f'20261004-matched-control-{arm}-s{s}-{interface}-RTX' if old else f'20261005-value-repeat-control-{arm}-s{s}-{interface}-RTX')
    group,arr=verify(ROOT/name,bank,'nav',interface);context=read(ROOT/name/'matched_loader.json');source=ROOT/context['source_training_run']
    assert context['arm']==arm and context['seed']==s and group['config']['model_training_updates']==5650
    assert group['config']['checkpoint_sha256']==context['train_checkpoint_sha256']==read(source/'summary.json')['checkpoint_sha256']
    assert read(source/'complete.json')==dict(completed=True,training_updates=5650,simulator_episodes=0)
    assert context['loader_sha256']==sha(WB/'scripts'/('matched_control_queue.py' if old else 'value_seed_control_queue.py'))
    arrays[arm,s,interface]=arr;groups.append(group);totals.append(counts(group,arm=arm,seed=s,interface=interface));print('value control audit',arm,s,interface,'PASS',flush=True)
  ns=3;contrasts=[('VGIQL-JOINT','ABS'),('VGIQL-SEPARATE','ABS'),('VGIQL-SEPARATE','VGIQL-JOINT')]
 else:
  ns=1;contrasts=[('PRED-MIX','PRED-FACT'),('VALUE-MIX','VALUE-FACT'),('VALUE-FACT','PRED-FACT'),('VALUE-MIX','PRED-MIX')]
  for geometry in ['PRED','VALUE']:
   for arm in ['FACT','MIX']:
    for interface in ['native','physical']:
     name=f'20261005-E20-geometry-control-{geometry}-{arm}-{interface}-RTX-s0'
     group,arr=verify(ROOT/name,bank,'nav',interface);context=read(ROOT/name/'geometry_loader.json');source=ROOT/context['source_training_run']
     assert context['geometry']==geometry and context['arm']==arm and context['seed']==0 and context['loader_sha256']==sha(WB/'scripts/geometry_control_queue.py')
     assert group['config']['model_training_updates']==2825 and group['config']['checkpoint_sha256']==context['train_checkpoint_sha256']==next(v['checkpoint_sha256'] for v in read(source/'summary.json') if v['updates']==2825)
     assert read(source/'complete.json')==dict(completed=True,geometry=geometry,arm=arm,seed=0,updates=2825)
     arrays[f'{geometry}-{arm}',0,interface]=arr;groups.append(group);totals.append(counts(group,geometry=geometry,arm=arm,seed=0,interface=interface));print('geometry control audit',geometry,arm,interface,'PASS',flush=True)
 assert len({g['config']['hardware'] for g in groups})==1
 rng=np.random.default_rng(112100 if mode=='value' else 112200);si=rng.integers(0,ns,(10000,ns));near=rng.integers(0,24,(10000,24));far=rng.integers(24,48,(10000,24));allix=np.concatenate([near,far],1)
 for interface in ['native','physical']:
  for arm,reference in contrasts:
   delta=np.stack([arrays[arm,s,interface]-arrays[reference,s,interface] for s in range(ns)])
   for tier,ix in [('all',allix),('near',near),('far',far)]:
    values=delta if tier=='all' else delta[:,:24] if tier=='near' else delta[:,24:]
    draws=delta[si[:,:,None],ix[:,None,:]].mean((1,2));effects.append(dict(interface=interface,arm=arm,reference=reference,tier=tier,mean_delta=float(values.mean()),source_deltas=values.mean(1).tolist(),paired_source_anchor_bootstrap_95=np.quantile(draws,[.025,.975]).tolist(),train_sources=ns))
  if mode=='geometry':
   interaction=(arrays['VALUE-MIX',0,interface]-arrays['VALUE-FACT',0,interface])-(arrays['PRED-MIX',0,interface]-arrays['PRED-FACT',0,interface])
   for tier,ix in [('all',allix),('near',near),('far',far)]:
    values=interaction if tier=='all' else interaction[:24] if tier=='near' else interaction[24:]
    effects.append(dict(interface=interface,contrast='(VALUE MIX-FACT)-(PRED MIX-FACT)',tier=tier,mean_delta=float(values.mean()),paired_anchor_bootstrap_95=np.quantile(interaction[ix].mean(1),[.025,.975]).tolist(),train_sources=1))
 result=dict(completed=True,mode=mode,controller_groups=len(groups),episodes=48*len(groups),counts=totals,effects=effects,groups=groups,audit=dict(all_48_retained=True,all_trace_hashes_initial_states_native_success_recomputed=True,train_eval_checkpoint_and_loaders_match=True,same_hardware_and_ledger=True),scope='Development only, same48 tasks shared across independent value3 train sources or geometry1 source. Sep already known in Value-GuidedJEPA. Geometry prior objectives and5650/2825 budgets differ, dynamic init common reset; within-geometry data differences conditional, extra branch interaction costs differ. Interfaces also differ in initialization scale and bounds. Not original paper replication or novel method confirmation.')
 out=ROOT/('20261005-E14-three-seed-control-audit' if mode=='value' else '20261005-E20-geometry-control-audit');assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');save(out/'result.json',result)
 for group in groups:
  rows=group.pop('rows');group['summary_from_audited_rows']=[dict(goal_span=v,n=24,successes=sum(r['goal_span']==v and r['success'] for r in rows),new_env_steps=sum(r['env_steps'] for r in rows if r['goal_span']==v)) for v in [25,75]]
 result['full_audit_artifact']=str(out/'result.json');save(WB/'results'/('E14_20261005_three_seed_control_results.json' if mode=='value' else 'E20_20261005_geometry_control_results.json'),result);print(json.dumps(totals),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['value','geometry']);main(p.parse_args().mode)
