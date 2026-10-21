#!/usr/bin/env python3
"""Inventory public assets and native benchmark units without any model/API call."""
import argparse,json,sys,hashlib
from pathlib import Path
from collections import Counter,defaultdict


def main():
 a=argparse.ArgumentParser();a.add_argument('--arcane',required=True);a.add_argument('--out',required=True);args=a.parse_args()
 repo=Path(args.arcane);sys.path.insert(0,str(repo))
 from inference.config import probe_file
 from inference.loaders import load_trials
 from inference.context_builders import _curate_axes
 novels={};samplemeta=[];counts=Counter()
 for nd in sorted((repo/'results/arc_extraction').iterdir()):
  if not nd.is_dir():continue
  stat=Counter();chars=[]
  for axispath in sorted((nd/'final_auto').glob('*_auto_axes.json')):
   slug=axispath.name.removesuffix('_auto_axes.json');raw=json.loads(axispath.read_text())
   axes=raw.get('intrapersonal_axes',[])+raw.get('relational_axes',[]);stat['character_files']+=1
   if not axes:stat['empty_axis_files']+=1
   else:stat['characters_with_nonempty_axes']+=1
   stat['axes']+=len(axes)
   try:pp=probe_file(nd.name,slug)
   except FileNotFoundError:stat['missing_probe_files']+=1;continue
   probe=json.loads(pp.read_text());trials=load_trials(nd.name,slug);stat['characters_with_probes']+=1
   stat['probes']+=sum(len(f['probes']) for f in probe.get('families',[]));stat['phase_trials']+=len(trials)
   for t in trials:
    stat['trials_'+t.probe_type]+=1
    curated=_curate_axes(raw,t.query_chapter)
    kept=[ph for k in ['intrapersonal_axes','relational_axes'] for ax in curated[k] for ph in ax.get('trajectory',[])]
    if any((ph.get('chapter_range') or [0,0])[-1]>t.query_chapter for ph in kept):stat['trials_with_retained_phase_spanning_after_query']+=1
   chars.append(dict(slug=slug,character=probe.get('character'),axes=len(axes),probes=sum(len(f['probes']) for f in probe.get('families',[])),trials=len(trials),probe_path=str(pp.relative_to(repo)),probe_sha256=hashlib.sha256(pp.read_bytes()).hexdigest()))
  novels[nd.name]=dict(counts=dict(stat),characters=chars);counts.update(stat)
 out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(dict(counts=dict(counts),novels=novels,warning='Retained phase range extending after query is an input-boundary fact, not proof of future-event leakage or outcome inflation.'),indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(dict(counts=dict(counts),by_novel={k:v['counts'] for k,v in novels.items()}),indent=2))

if __name__=='__main__':main()
