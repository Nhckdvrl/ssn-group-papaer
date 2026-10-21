#!/usr/bin/env python3
"""Render all native ArcANE judgments for one uniform local evaluator."""
import argparse,json,sys,hashlib
from pathlib import Path
from collections import defaultdict

def read(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def main():
 a=argparse.ArgumentParser();a.add_argument('--arcane',required=True);a.add_argument('--references',required=True);a.add_argument('--sources',nargs='+',required=True);a.add_argument('--out',required=True);args=a.parse_args();sys.path.insert(0,args.arcane)
 from evaluation.per_response.prompt import EvalTrial,render_evaluator_messages as single
 from evaluation.trajectory.prompt import PhaseRef,render_evaluator_messages as trajectory
 refs={r['trial_id']:r['reference'] for r in read(args.references)};expected=defaultdict(set)
 for tid in refs:
  probe,phase=tid.rsplit('__p',1);expected[probe].add(int(phase))
 inputs=[]
 for source in args.sources:
  rs=read(Path(source)/'responses.jsonl');assert len(rs)==len({r['task_id'] for r in rs});inputs.extend(rs)
 tasks=[];groups=defaultdict(list)
 for r in inputs:
  ref=refs[r['probe_id']+'__p'+str(r['phase_idx'])];text=r.get('response') or '[empty response — model returned nothing]'
  meta=dict(actor_model=r['model'],mode=r['mode'],novel=r['novel'],character_slug=r['character_slug'],probe_id=r['probe_id'])
  tasks.append(dict(meta,task_id='per_response/'+r['trial_id'],kind='per_response',phase_idx=r['phase_idx'],candidate_sha256=hashlib.sha256(text.encode()).hexdigest(),messages=single(EvalTrial(**ref),text,scale=100,include_thought=True)))
  groups[r['model'],r['mode'],r['novel'],r['character_slug'],r['probe_id']].append((r,ref,text))
 for (model,mode,novel,char,probe),items in groups.items():
  assert {r['phase_idx'] for r,_,_ in items}==expected[probe], 'Never score incomplete phase trajectories'
  items.sort(key=lambda x:x[0]['phase_idx']);first=items[0][1]
  phases=[PhaseRef(r['phase_idx'],ref['phase'],ref['gt_action'],ref['gt_speech'],ref['gt_thought'],text) for r,ref,text in items]
  tasks.append(dict(task_id='trajectory/'+model+'/'+mode+'/'+probe,actor_model=model,mode=mode,novel=novel,character_slug=char,probe_id=probe,kind='trajectory',n_phases=len(phases),messages=trajectory(first['scenario'],first['question'],phases,scale=100,include_thought=True)))
 tasks.sort(key=lambda t:hashlib.sha256(('D-local-judge|'+t['task_id']).encode()).hexdigest());assert len(tasks)==len({t['task_id'] for t in tasks})
 with Path(args.out).open('w') as f:
  for t in tasks:f.write(json.dumps(t,ensure_ascii=False)+'\n')
 print('Full uniform local judge tasks',len(tasks))
if __name__=='__main__':main()
