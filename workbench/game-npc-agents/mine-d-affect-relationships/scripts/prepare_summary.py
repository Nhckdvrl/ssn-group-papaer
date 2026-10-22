#!/usr/bin/env python3
"""Prepare native recent-chapter Summary baseline on a fixed nested character sample."""
import argparse,json,sys,hashlib,re
from pathlib import Path

def read(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def wr(p,rs):
 with Path(p).open('w') as f:
  for r in rs:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def main():
 a=argparse.ArgumentParser();a.add_argument('cmd',choices=['prepare','apply']);a.add_argument('--arcane',required=True);a.add_argument('--base-assets',required=True);a.add_argument('--assets',required=True);a.add_argument('--manifest',required=True);a.add_argument('--teacher-responses');args=a.parse_args();repo=Path(args.arcane);out=Path(args.assets);out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(repo))
 from inference.loaders import Trial,read_chapter
 from inference.prompts import SUMMARY_SYSTEM,render_summary_user,render_system,render_user
 from inference.context_builders import build_summary
 from inference import config
 if args.cmd=='prepare':
  # Published Monte_Cristo axes refer to 14 native narrative chunks. Never
  # silently replace their IDs with the 117 literary chapter numbers.
  n_monte=len(list(config.chapter_dir('Monte_Cristo').glob('chapter_*.txt')))
  if n_monte!=14:raise RuntimeError('Monte source-unit mismatch: published arcs use 14 native chunks; use the explicit source-repair pipeline, never renumber to 117 literary chapters')
  tasks=read(Path(args.base_assets)/'tasks.jsonl');groups={}
  for t in tasks:
   if t['mode']!='vanilla':continue
   tr=t['trial'];k=(tr['novel'],tr['character_slug']);groups.setdefault(k,{}).setdefault(tr['probe_id'],[]).append(tr)
  selected=[]
  for k,probes in sorted(groups.items()):
   probe=min(probes,key=lambda s:hashlib.sha256(('D-E03-v1|'+s).encode()).hexdigest())
   selected.extend(probes[probe])
  needed=sorted({(t['novel'],ch) for t in selected for ch in range(max(1,t['query_chapter']-4),t['query_chapter']+1)})
  teachers=[];source_hashes={}
  for novel,ch in needed:
   text=read_chapter(novel,ch);source_hashes[novel+'/'+str(ch)]=hashlib.sha256(text.encode()).hexdigest()
   teachers.append(dict(task_id=novel+'/chapter_'+str(ch),novel=novel,chapter=ch,messages=[dict(role='system',content=SUMMARY_SYSTEM),dict(role='user',content=render_summary_user(novel,ch,text))]))
  wr(out/'teacher_tasks.jsonl',teachers);(out/'selected_trials.json').write_text(json.dumps(selected,indent=2,ensure_ascii=False)+'\n')
  refs={r['trial_id']:r for r in read(Path(args.base_assets)/'references.jsonl')}
  wr(out/'references.jsonl',[refs[t['probe_id']+'__p'+str(t['phase_idx'])] for t in selected])
  manifest=dict(n_characters=len(groups),n_probes=len(groups),n_phase_trials=len(selected),n_chapter_summaries=len(needed),selection='One SHA256-minimum already-selected D-E01 probe per character, all its phases; no score filtering',source_hashes=source_hashes,teacher_tasks_sha256=hashlib.sha256((out/'teacher_tasks.jsonl').read_bytes()).hexdigest(),source_repair='Monte_Cristo source-edition body indentation; verified numbered 1..117. Other novels use native preprocessor indexing, not independently canonical literary chapter numbering.')
  Path(args.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');print({k:v for k,v in manifest.items() if k!='source_hashes'})
 else:
  selected=json.loads((out/'selected_trials.json').read_text());teachers=read(out/'teacher_tasks.jsonl');responses=read(args.teacher_responses);index={r['task_id']:r for r in responses};assert len(index)==len(teachers)
  for t in teachers:
   r=index[t['task_id']];assert r['finish_reason']=='stop' and r['response'].strip(), 'Do not hide missing or truncated summaries'
   path=config.summary_path(t['novel'],t['chapter']);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(r['response'].strip())
  tasks=[]
  for row in selected:
   tr=Trial(**row);context=build_summary(tr);assert context and '[note] Missing' not in context
   tasks.append(dict(task_id=tr.trial_id+'__summary',mode='summary',trial=row,messages=[dict(role='system',content=render_system(tr,context)),dict(role='user',content=render_user(tr))]))
  wr(out/'tasks.jsonl',tasks);print('Native Summary tasks',len(tasks))
if __name__=='__main__':main()
