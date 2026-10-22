#!/usr/bin/env python3
"""A plain character-state summary of exactly the existing Summary text."""
import argparse,json,hashlib,copy
from pathlib import Path

SYSTEM='''Write a useful, concise current character profile for roleplay from the recent narrative summaries below. Organize what the supplied evidence supports about this character's current beliefs, goals, relationships, characteristic ways of responding, and still-relevant stable identity. Keep unresolved tensions and uncertainty when the evidence is insufficient. Infer the character's stance from events where supported; do not borrow later story events or invent missing experiences. Do not write a story continuation, answer a hypothetical question, or predict a future arc. Use at most 500 words. Return the profile as plain text.'''
def rows(p):return [json.loads(l) for l in p.read_text().splitlines()]
def main():
 a=argparse.ArgumentParser();a.add_argument('operation',choices=['prepare','apply']);a.add_argument('--asset-root',required=True);args=a.parse_args();root=Path(args.asset_root);out=root/'data/arcane_D-E07';out.mkdir(parents=True,exist_ok=True);original=rows(root/'data/arcane_D-E03/tasks.jsonl')
 if args.operation=='prepare':
  assert not (out/'compiler_tasks.jsonl').exists();tasks=[];manifest=[]
  for r in original:
   t=r['trial'];context=r['messages'][0]['content'].split('<context>\n',1)[1].rsplit('\n</context>',1)[0];identity=dict(novel=t['novel'],character=t['character'],query_chapter=t['query_chapter']);user=f"Book: {t['novel']}\nCharacter: {t['character']}\nAs of source chapter: {t['query_chapter']}\n\nRecent narrative summaries:\n{context}"
   tasks.append(dict(task_id=r['task_id'].removesuffix('__summary')+'__compiler',source_trial_id=r['task_id'],**identity,messages=[dict(role='system',content=SYSTEM),dict(role='user',content=user)]));manifest.append(dict(task_id=tasks[-1]['task_id'],identity=identity,source_context_sha256=hashlib.sha256(context.encode()).hexdigest(),allowed_fields=['novel','character','query_chapter','summary_context'],no_probe_or_phase_fields=True))
  assert len(tasks)==81 and len({r['task_id'] for r in tasks})==81;(out/'compiler_tasks.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in tasks));(out/'compiler_provenance.json').write_text(json.dumps(dict(n=81,source='D-E03 exact Summary contexts',details=manifest),ensure_ascii=False,indent=2)+'\n');print('Compiler tasks frozen: 81, no probe, axis, phase label, or gold',flush=True)
 else:
  candidates=rows(root/'runs/D-E07/state_compiler/responses.jsonl');recovery=root/'runs/D-E07/state_compiler_recovery/responses.jsonl'
  if recovery.exists():candidates+=rows(recovery)
  index={}
  for r in candidates:
   if r['finish_reason']=='stop' and r['response'].strip():index.setdefault(r['task_id'],r)
  assert len(index)==81,'Do not silently score incomplete compiled trajectories';tasks=[]
  for r in original:
   v=copy.deepcopy(r);key=r['task_id'].removesuffix('__summary')+'__compiler';text=index[key]['response'];system=r['messages'][0]['content'];prefix,tail=system.split('<context>\n',1);old,suffix=tail.rsplit('\n</context>',1);context='Current character state inferred from the supplied recent summaries:\n'+text;v['messages'][0]['content']=prefix+'<context>\n'+context+'\n</context>'+suffix;assert v['messages'][1:]==r['messages'][1:];v.update(task_id=r['task_id'].removesuffix('__summary')+'__state_summary',mode='state_summary',compiler_response_sha256=hashlib.sha256(text.encode()).hexdigest());tasks.append(v)
  path=out/'tasks.jsonl';assert not path.exists();path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in tasks));print('Compiled actor tasks frozen: 81; only context changed',flush=True)
if __name__=='__main__':main()
