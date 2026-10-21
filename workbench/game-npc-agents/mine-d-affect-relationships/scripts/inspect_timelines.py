#!/usr/bin/env python3
"""Inspect released chronology tags and serialized persona evolution, no new prompts."""
import argparse,json,re
from pathlib import Path
from collections import Counter

def load(p):return json.loads(Path(p).read_text())
def ep(s):
 m=re.fullmatch(r'S(\d+)E(\d+)',str(s))
 return (int(m[1]),int(m[2])) if m else None

def main():
 a=argparse.ArgumentParser();a.add_argument('--dataset',required=True);a.add_argument('--selection',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.dataset)/'processed';selected=load(args.selection)['selected'];result={}
 for corpus in ['Friends','TheOffice','HPD','StarTrek_TNG']:
  base=root/corpus/'intermediate';dialogues={r['question_id']:r for r in load(base/'all_dialogues.json')};moments={}
  moment_files=[base/'all_dialogues_long_term_moments.json'] if (base/'all_dialogues_long_term_moments.json').exists() else [base/(s+'_long_term_moments.json') for s in ['train','random_test','ood_test']]
  for mp in moment_files:
   for qid,value in load(mp).items():
    if qid in moments:assert moments[qid]==value, 'Conflicting published moment versions'
    moments[qid]=value
  snapshots=load(base/'evolution/persona_snapshots.json');tags=[]
  for s in selected:
   if s['corpus']!=corpus:continue
   r=dialogues.get(s['question_id'],{});m=moments.get(s['question_id'],{});book=r.get('_season') if r.get('_season') is not None else r.get('_book');chapter=r.get('_episode')
   if chapter is None:
    match=re.search(r'chapter(\d+)',str(r.get('_position','')),re.I);chapter=int(match[1]) if match else None
   target=(int(book),int(chapter)) if book is not None and chapter is not None else None;source=ep(m.get('_persona_from_episode'))
   tags.append(dict(question_id=s['question_id'],target_episode=target,persona_source_episode=source,ordering='strictly_earlier' if source and target and source<target else 'not_earlier' if source and target else 'fallback_or_missing'))
  transitions=Counter();versions={};edge_count=0
  for role,states in snapshots.items():
   ordered=sorted(((ep(k),v) for k,v in states.items() if ep(k)),key=lambda x:x[0]);versions[role]=len(ordered)
   for (_,old),(_,new) in zip(ordered,ordered[1:]):
    before=old.get('tree',{}).get('persona',{});after=new.get('tree',{}).get('persona',{});edge_count+=1
    for field in set(before)|set(after):
     if field in ['version','updated_at','timestamp']:continue
     if before.get(field)!=after.get(field):transitions[field]+=1
  result[corpus]=dict(n_dialogues=len(dialogues),n_moment_records=len(moments),snapshot_counts=versions,n_snapshot_edges=edge_count,serialized_persona_field_changes=dict(transitions),selected_source_tag_counts=dict(Counter(r['ordering'] for r in tags)),selected_source_tags=tags)
 Path(args.out).write_text(json.dumps(dict(corpora=result,warning='Source tags and field byte changes are asset facts. They do not certify all content is temporally knowable or that a textual rewrite is a semantic trait change.'),indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({k:{x:v[x] for x in ['n_dialogues','n_moment_records','n_snapshot_edges','serialized_persona_field_changes','selected_source_tag_counts']} for k,v in result.items()},indent=2))
if __name__=='__main__':main()
