#!/usr/bin/env python3
"""Freeze a stratified official ArcANE probe sample and render native prompts."""
import argparse,json,hashlib,sys
from pathlib import Path
from dataclasses import asdict
from collections import defaultdict,Counter,deque

SLICES={'don_quixote':12,'Benjamin_Franklin':12,'Monte_Cristo':12,'Anna_Kareina':12,'He Knew He Was Right':8,'The Odd Women':8}
SALT='D-E01-public-heldout-2026-10-22-v1'
def h(s):return hashlib.sha256((SALT+'|'+s).encode()).hexdigest()
def write_rows(path,rows):
 with Path(path).open('w') as f:
  for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')

def main():
 a=argparse.ArgumentParser();a.add_argument('--arcane',required=True);a.add_argument('--asset-out',required=True);a.add_argument('--manifest',required=True);args=a.parse_args()
 repo=Path(args.arcane);sys.path.insert(0,str(repo))
 from inference.config import probe_file
 from inference.loaders import load_trials
 from inference.prompts import render_system,render_user
 from inference.context_builders import build_arc
 selected=[];trials_all=[];refs={};source_hash={}
 for novel,quota in SLICES.items():
  strata=defaultdict(list)
  for axes in sorted((repo/'results/arc_extraction'/novel/'final_auto').glob('*_auto_axes.json')):
   slug=axes.name.removesuffix('_auto_axes.json')
   try:pp=probe_file(novel,slug)
   except FileNotFoundError:continue
   source_hash[str(pp.relative_to(repo))]=hashlib.sha256(pp.read_bytes()).hexdigest()
   source_hash[str(axes.relative_to(repo))]=hashlib.sha256(axes.read_bytes()).hexdigest()
   data=json.loads(pp.read_text());trial_index={(t.probe_id,t.phase_idx):t for t in load_trials(novel,slug)}
   for fam in data['families']:
    for p in fam['probes']:
     phases=[ph for ph in p['phase_responses'] if not ph.get('unavailable')]
     if len(phases)<2:continue
     group=[]
     for ph in phases:
      t=trial_index[p['probe_id'],ph['phase_idx']];group.append(t)
      refs[t.trial_id]=dict(scenario=t.scenario,question=t.question,gt_action=ph.get('gt_action'),gt_speech=ph.get('gt_speech'),gt_thought=ph.get('gt_thought'),phase=ph.get('phase_label'))
     strata[slug,p['probe_type']].append((h(p['probe_id']),group))
  queues=[deque(sorted(v)) for k,v in sorted(strata.items(),key=lambda kv:h(str(kv[0])))]
  chosen=[]
  while len(chosen)<quota:
   n=0
   for q in queues:
    if q and len(chosen)<quota:chosen.append(q.popleft()[1]);n+=1
   if not n:raise ValueError('not enough complete probe groups for '+novel)
  for group in chosen:
   t=group[0];selected.append(dict(novel=novel,character_slug=t.character_slug,axis_id=t.axis_id,probe_id=t.probe_id,probe_type=t.probe_type,phase_indices=[t.phase_idx for t in group],query_chapters=[t.query_chapter for t in group]))
   trials_all.extend(group)
 out=Path(args.asset_out);out.mkdir(parents=True,exist_ok=True)
 tasks=[]
 for t in trials_all:
  for mode in ['vanilla','arc']:
   context=build_arc(t) if mode=='arc' else None
   tasks.append(dict(task_id=t.trial_id+'__'+mode,mode=mode,trial=asdict(t),messages=[dict(role='system',content=render_system(t,context)),dict(role='user',content=render_user(t))]))
 assert len({r['task_id'] for r in tasks})==len(tasks)
 write_rows(out/'tasks.jsonl',tasks)
 write_rows(out/'references.jsonl',[dict(trial_id=t.trial_id,reference=refs[t.trial_id]) for t in trials_all])
 (out/'trials.json').write_text(json.dumps([asdict(t) for t in trials_all],indent=2,ensure_ascii=False)+'\n')
 manifest=dict(salt=SALT,selection_rule='Per-novel fixed quota; round-robin character×probe-type strata; SHA256 ordering within stratum; all available phases; no outcome/refusal/large-change filtering',selected=selected,n_probe_groups=len(selected),n_phase_trials=len(trials_all),n_tasks_per_model=len(tasks),n_characters=len({(t.novel,t.character_slug) for t in trials_all}),n_axes=len({(t.novel,t.character_slug,t.axis_id) for t in trials_all}),by_novel=dict(Counter(t.novel for t in trials_all)),by_probe_type=dict(Counter(t.probe_type for t in trials_all)),input_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*') if p.is_file()},source_hashes=source_hash)
 Path(args.manifest).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in manifest.items() if k not in ['selected','source_hashes','input_hashes']},indent=2))

if __name__=='__main__':main()
