#!/usr/bin/env python3
"""Freeze complete native source prefixes, never crossing a query checkpoint."""
import argparse,copy,hashlib,json,sys
from pathlib import Path

def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def read(path):return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
def pack_prefix(units,checkpoints,max_chars=32000):
 blocks=[];segments=[];n=0;completed=0
 def flush(checkpoint=None):
  nonlocal segments,n
  if segments:blocks.append(dict(segments=segments,completed_through_unit=completed,checkpoint=checkpoint));segments=[];n=0
 for unit,text in units:
  offset=0
  for line in text.splitlines(keepends=True):
   for start in range(0,len(line),max_chars):
    piece=line[start:start+max_chars]
    if n+len(piece)>max_chars:flush()
    if segments and segments[-1]['unit']==unit:
     assert segments[-1]['end_char']==offset;segments[-1]['text']+=piece;segments[-1]['end_char']+=len(piece)
    else:segments.append(dict(unit=unit,start_char=offset,end_char=offset+len(piece),text=piece))
    offset+=len(piece);n+=len(piece)
  assert offset==len(text);completed=unit
  if unit in checkpoints:flush(unit)
 flush()
 assert {b['checkpoint'] for b in blocks if b['checkpoint'] is not None}==set(checkpoints)
 for unit,text in units:
  actual=[s for b in blocks for s in b['segments'] if s['unit']==unit];assert ''.join(s['text'] for s in actual)==text
 for i,b in enumerate(blocks):
  if b['checkpoint'] is not None:assert max(s['unit'] for prior in blocks[:i+1] for s in prior['segments'])==b['checkpoint']
 return blocks

def render_passages(block):
 return '\n\n'.join(f"[Source unit {s['unit']}; characters {s['start_char']}:{s['end_char']}]\n{s['text']}" for s in block['segments'])

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);args=a.parse_args();root=Path(args.asset_root);out=root/'data/prefix_D-E09';out.mkdir(exist_ok=True);assert not (out/'chains.jsonl').exists()
 selected=set(json.loads((root/'data/arcane_D-E07_v2/preselected_review.json').read_text())['probes'].values());d7=read(root/'data/arcane_D-E07_v2/tasks.jsonl');characters={(r['trial']['novel'],r['trial']['character_slug']) for r in d7 if r['trial']['probe_id'] in selected};d1=[r for r in read(root/'data/arcane_D-E01/tasks.jsonl') if r['mode']=='arc' and (r['trial']['novel'],r['trial']['character_slug']) in characters];assert len(d1)==47 and len({r['trial']['probe_id'] for r in d1})==15
 sys.path.insert(0,str(root/'vendor/ArcANE'));from arc_construction.phase0_preprocess import load_and_strip_gutenberg,split_chapters
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained(root/'models/Qwen3-32B',local_files_only=True);chains=[];manifest=[]
 for novel,slug in sorted(characters):
  tasks=[r for r in d1 if r['trial']['novel']==novel and r['trial']['character_slug']==slug];checkpoints=sorted({r['trial']['query_chapter'] for r in tasks});raw=load_and_strip_gutenberg(str(root/'vendor/ArcANE/data/novels'/f'{novel}.txt'));units=split_chapters(raw);folder=root/'vendor/ArcANE/results/arc_extraction'/novel/('chapters_native_14_backup' if novel=='Monte_Cristo' else 'chapters');unit_proof=[]
  for i,text in units:
   assert (folder/f'chapter_{i:02d}.txt').read_text()==text,(novel,i)
   if i<=max(checkpoints):unit_proof.append(dict(unit=i,characters=len(text),sha256=digest(text)))
  units=[u for u in units if u[0]<=max(checkpoints)];blocks=pack_prefix(units,checkpoints);chain_id='prefix/'+slug
  for j,b in enumerate(blocks):
   b['step']=j+1;b['task_id']=chain_id+'/step'+str(j+1);b['passages']=render_passages(b);b['source_sha256']=digest(b['passages']);b['source_tokens']=len(tok.encode(b['passages'],add_special_tokens=False));assert b['source_tokens']<=12000
  chain=dict(chain_id=chain_id,novel=novel,character=tasks[0]['trial']['character'],character_slug=slug,checkpoints=checkpoints,blocks=blocks);chains.append(chain);manifest.append(dict(chain_id=chain_id,novel=novel,character=chain['character'],n_probes=len({r['trial']['probe_id'] for r in tasks}),n_phase_trials=len(tasks),checkpoints=checkpoints,n_blocks=len(blocks),max_source_tokens=max(b['source_tokens'] for b in blocks),total_source_tokens=sum(b['source_tokens'] for b in blocks),native_unit_proof=unit_proof))
 assert sum(len(c['blocks']) for c in chains)<=700
 # Balance only frozen source workload, never any generated result.
 loads=[0,0]
 for c in sorted(chains,key=lambda c:(-sum(b['source_tokens']+2400 for b in c['blocks']),c['chain_id'])):
  shard=min(range(2),key=lambda i:(loads[i],i));c['shard']=shard;loads[shard]+=sum(b['source_tokens']+2400 for b in c['blocks'])
 for m in manifest:m['shard']=next(c['shard'] for c in chains if c['chain_id']==m['chain_id'])
 for name,rows in [('chains.jsonl',chains),('actor_templates.jsonl',d1)]:
  (out/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
 refs=[r for r in read(root/'data/arcane_D-E01/references.jsonl') if r['trial_id'] in {t['trial']['probe_id']+'__p'+str(t['trial']['phase_idx']) for t in d1}];assert len(refs)==47;(out/'references.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in refs))
 result=dict(experiment='D-E09',n_roles=6,n_probes=15,n_phase_trials=47,n_blocks=sum(len(c['blocks']) for c in chains),shard_loads=loads,source_partition='Native source IDs; Monte fourteen-unit backup; all source text through each checkpoint preserved',packing='Contiguous source units may share a block up to 32000 raw characters, but every frozen query unit forces a block end. No future query text/phase/gold used by the compiler.',chains=manifest)
 (out/'selection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='chains'},ensure_ascii=False,indent=2));print([(c['character_slug'],c['shard'],len(c['blocks'])) for c in chains])
if __name__=='__main__':main()
