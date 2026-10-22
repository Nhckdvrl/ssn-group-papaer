#!/usr/bin/env python3
"""Restore the meaning of published Monte source-unit IDs without renumbering."""
import argparse,json,hashlib,copy,sys
from pathlib import Path
from prepare_state_summary import SYSTEM

def read(p):return [json.loads(l) for l in Path(p).read_text().splitlines()]
def write(p,rows):assert not p.exists();p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
def first_complete(paths,expected=None):
 index={}
 for p in paths:
  if p.exists():
   for r in read(p):
    if r['finish_reason']=='stop' and r['response'].strip() and (expected is None or r['messages']==expected[r['task_id']]['messages']):index.setdefault(r['task_id'],r)
 return index

def main():
 a=argparse.ArgumentParser();a.add_argument('operation',choices=['map','reduce','compile','actors']);a.add_argument('--asset-root',required=True);args=a.parse_args();root=Path(args.asset_root);out=root/'data/arcane_D-E07_v2';out.mkdir(parents=True,exist_ok=True);original=read(root/'data/arcane_D-E03/tasks.jsonl');monte=[r for r in original if r['trial']['novel']=='Monte_Cristo'];assert len(monte)==13;units=sorted({i for r in monte for i in range(max(1,r['trial']['query_chapter']-4),r['trial']['query_chapter']+1)})
 sys.path.insert(0,str(root/'vendor/ArcANE'));from inference.prompts import SUMMARY_SYSTEM,render_summary_user
 if args.operation=='map':
  from transformers import AutoTokenizer
  from arc_construction.phase0_preprocess import load_and_strip_gutenberg,split_chapters
  raw=load_and_strip_gutenberg(str(root/'vendor/ArcANE/data/novels/Monte_Cristo.txt'));native=split_chapters(raw);assert len(native)==14;backup=root/'vendor/ArcANE/results/arc_extraction/Monte_Cristo/chapters_native_14_backup';tok=AutoTokenizer.from_pretrained(root/'models/Qwen3-32B',local_files_only=True);tasks=[];proof=[]
  for unit,text in native:
   path=backup/f'chapter_{unit:02d}.txt';assert text==path.read_text(),'Do not guess the old native source partition';proof.append(dict(unit=unit,characters=len(text),sha256=hashlib.sha256(text.encode()).hexdigest()))
   if unit not in units:continue
   pieces=[];block=''
   for line in text.splitlines(keepends=True):
    if len(block)+len(line)>16000 and block:pieces.append(block);block=''
    while len(line)>16000:pieces.append(line[:16000]);line=line[16000:]
    block+=line
   if block:pieces.append(block)
   assert ''.join(pieces)==text
   for k,part in enumerate(pieces):
    n=len(tok.encode(part,add_special_tokens=False));assert n<=6000
    tasks.append(dict(task_id=f'Monte_Cristo/unit_{unit}/part_{k+1}',novel='Monte_Cristo',unit=unit,part=k+1,n_parts=len(pieces),source_text_sha256=hashlib.sha256(part.encode()).hexdigest(),messages=[dict(role='system',content='Summarize this contiguous fragment of a novel faithfully in at most 200 words. Preserve concrete events, who did what, character reactions and important changes. Use only this fragment; do not add later plot or outside story knowledge. Return plain text.'),dict(role='user',content=f'Book: Monte_Cristo\nNative narrative unit: {unit}\nFragment: {k+1}/{len(pieces)}\n\n{part}')]))
  assert len(tasks)<=220;write(out/'map_tasks.jsonl',tasks);(out/'source_provenance.json').write_text(json.dumps(dict(native_units=14,required_units=units,source_chunks_match_native_splitter_and_backup=True,all_fragment_texts_cover_each_unit_exactly=True,n_map_tasks=len(tasks),source_units=proof,affected_phases=13,affected_probes=5),ensure_ascii=False,indent=2)+'\n');print('Native source repair maps',len(tasks),'units',units,flush=True)
 elif args.operation=='reduce':
  expected={r['task_id']:r for r in read(out/'map_tasks.jsonl')};index=first_complete([root/'runs/D-E07/source_repair_maps/responses.jsonl',root/'runs/D-E07/source_repair_maps_recovery/responses.jsonl'],expected);assert set(index)==set(expected);tasks=[]
  for unit in units:
   keys=sorted([k for k,v in expected.items() if v['unit']==unit],key=lambda k:expected[k]['part']);text='These are ordered factual summaries covering the complete native narrative unit; integrate them without adding outside plot.\n\n'+'\n\n'.join(f"[Fragment {expected[k]['part']}]\n{index[k]['response']}" for k in keys);tasks.append(dict(task_id=f'Monte_Cristo/unit_{unit}/summary',novel='Monte_Cristo',chapter=unit,messages=[dict(role='system',content=SUMMARY_SYSTEM),dict(role='user',content=render_summary_user('Monte_Cristo',unit,text))]))
  write(out/'reduce_tasks.jsonl',tasks);print('Native unit reducers',len(tasks),flush=True)
 elif args.operation=='compile':
  expected={r['task_id']:r for r in read(out/'reduce_tasks.jsonl')};index=first_complete([root/'runs/D-E07/source_repair_reduce/responses.jsonl',root/'runs/D-E07/source_repair_reduce_recovery/responses.jsonl'],expected);assert set(index)==set(expected);summaries={r['chapter']:index[r['task_id']]['response'] for r in expected.values()};all_summary=[];repair=[];compilers=[]
  for r in original:
   v=copy.deepcopy(r)
   if r['trial']['novel']=='Monte_Cristo':
    chapter=r['trial']['query_chapter'];context='\n\n'.join(f'[Chapter {ch}]\n{summaries[ch]}' for ch in range(max(1,chapter-4),chapter+1));s=v['messages'][0]['content'];prefix,tail=s.split('<context>\n',1);old,suffix=tail.rsplit('\n</context>',1);v['messages'][0]['content']=prefix+'<context>\n'+context+'\n</context>'+suffix;repair.append(v)
   all_summary.append(v);t=v['trial'];context=v['messages'][0]['content'].split('<context>\n',1)[1].rsplit('\n</context>',1)[0];user=f"Book: {t['novel']}\nCharacter: {t['character']}\nAs of source chapter: {t['query_chapter']}\n\nRecent narrative summaries:\n{context}";compilers.append(dict(task_id=r['task_id'].removesuffix('__summary')+'__compiler',source_trial_id=r['task_id'],novel=t['novel'],character=t['character'],query_chapter=t['query_chapter'],messages=[dict(role='system',content=SYSTEM),dict(role='user',content=user)]))
  write(out/'summary_tasks_all.jsonl',all_summary);write(out/'summary_tasks_repaired.jsonl',repair);write(out/'compiler_tasks.jsonl',compilers);expected={r['task_id']:r for r in compilers};cache=first_complete([root/'runs/D-E07/state_compiler/responses.jsonl'],expected);assert all(r['novel']!='Monte_Cristo' for r in cache.values());write(out/'compiler_cached_responses.jsonl',list(cache.values()));remaining=[r for r in compilers if r['task_id'] not in cache];write(out/'compiler_remaining_tasks.jsonl',remaining);(out/'compiler_reuse.json').write_text(json.dumps(dict(n_cached=len(cache),n_new=len(remaining),criterion='Only byte-equal model messages and first nonempty stop; no semantic/score filtering',cached_ids=sorted(cache)),indent=2)+'\n');print('Corrected Summary',len(all_summary),'repair only',len(repair),'compiler cached/new',len(cache),len(remaining),flush=True)
 else:
  expected={r['task_id']:r for r in read(out/'compiler_tasks.jsonl')};index=first_complete([out/'compiler_cached_responses.jsonl',root/'runs/D-E07/state_compiler_v2/responses.jsonl',root/'runs/D-E07/state_compiler_v2_recovery/responses.jsonl'],expected);assert set(index)==set(expected);tasks=[]
  for r in read(out/'summary_tasks_all.jsonl'):
   v=copy.deepcopy(r);key=r['task_id'].removesuffix('__summary')+'__compiler';text=index[key]['response'];prefix,tail=v['messages'][0]['content'].split('<context>\n',1);old,suffix=tail.rsplit('\n</context>',1);v['messages'][0]['content']=prefix+'<context>\nCurrent character state inferred from the supplied recent summaries:\n'+text+'\n</context>'+suffix;v.update(task_id=r['task_id'].removesuffix('__summary')+'__state_summary',mode='state_summary',compiler_response_sha256=hashlib.sha256(text.encode()).hexdigest());assert v['messages'][1:]==r['messages'][1:];tasks.append(v)
  write(out/'tasks.jsonl',tasks);(out/'READY.json').write_text(json.dumps(dict(complete=True,n=81,task_sha256=hashlib.sha256((out/'tasks.jsonl').read_bytes()).hexdigest()),indent=2)+'\n');print('Corrected state-summary actor tasks ready',len(tasks),flush=True)
if __name__=='__main__':main()
