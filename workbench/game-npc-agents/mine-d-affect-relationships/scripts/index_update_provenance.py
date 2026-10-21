#!/usr/bin/env python3
"""Recover released update provenance without loading the 4GB mixed-task array."""
import argparse,json,hashlib,re
from pathlib import Path
from collections import Counter,defaultdict

def array_items(path):
 decoder=json.JSONDecoder();buffer='';started=False;finished=False
 with Path(path).open() as f:
  while True:
   chunk=f.read(2**20)
   if not chunk:break
   buffer+=chunk
   while True:
    buffer=buffer.lstrip()
    if not started:
     assert buffer.startswith('[');buffer=buffer[1:];started=True;continue
    buffer=buffer.lstrip(', \r\n\t')
    if buffer.startswith(']'):finished=True;buffer=buffer[1:];break
    try:obj,end=decoder.raw_decode(buffer)
    except ValueError:break
    yield obj;buffer=buffer[end:]
   if finished:
    assert not buffer.strip() and not f.read().strip();break
 assert started and finished,'Incomplete source JSON'

def digest(text):return hashlib.sha256(str(text).encode()).hexdigest()
def section(text,title,next_title):
 return text.split('## '+title+'\n',1)[1].split('\n\n## '+next_title+'\n',1)[0]

def main():
 a=argparse.ArgumentParser();a.add_argument('--source',required=True);a.add_argument('--out',required=True);a.add_argument('--local-updates',required=True);args=a.parse_args();tasks=Counter();books=Counter();stats=defaultdict(Counter);tracks=defaultdict(list);fieldtypes=defaultdict(Counter);n=0;details=[]
 with Path(args.local_updates).open('w') as out:
  for row in array_items(args.source):
   n+=1;d=row['details'];tasks[d['task']]+=1
   if d['task']!='character_state_update':continue
   user=next(c['value'] for c in row['conversations'] if c['from']=='human');target=json.loads(next(c['value'] for c in row['conversations'] if c['from']=='assistant'))
   profile=section(user,'Current Profile (State At Scene Start)','Hidden Tracker (State At Scene Start)');tracker=section(user,'Hidden Tracker (State At Scene Start)','Current Motivation (State At Scene Start)')
   for k,v in target.items():fieldtypes[k][type(v).__name__]+=1
   after=target['updated_profile'] if target['profile_updated'] else profile
   meta=dict(d,input_profile_sha256=digest(profile),output_profile_sha256=digest(after),input_tracker_sha256=digest(tracker),output_tracker_sha256=digest(target['hidden_tracker'] or '(Empty)'),profile_updated=target['profile_updated'],input_chars=len(user),target_chars=len(next(c['value'] for c in row['conversations'] if c['from']=='assistant')))
   books[d['book_name']]+=1;stats[d['book_name']][str(target['profile_updated'])]+=1;tracks[d['book_name'],d['character']].append(meta)
   out.write(json.dumps(row,ensure_ascii=False)+'\n');details.append(meta)
 continuation=Counter();lengths=Counter();changed=Counter()
 for (book,char),rows in tracks.items():
  rows.sort(key=lambda r:r['scene_index']);assert len(rows)==len({r['scene_index'] for r in rows})
  lengths[len(rows)]+=1;changed[sum(r['profile_updated'] for r in rows)]+=1
  for prev,nxt in zip(rows,rows[1:]):
   continuation['adjacent_character_appearances']+=1
   continuation['profile_exact_continuity']+=prev['output_profile_sha256']==nxt['input_profile_sha256']
   continuation['tracker_exact_continuity']+=prev['output_tracker_sha256']==nxt['input_tracker_sha256']
   continuation['both_exact_continuity']+=(prev['output_profile_sha256']==nxt['input_profile_sha256'] and prev['output_tracker_sha256']==nxt['input_tracker_sha256'])
 sourcehash=hashlib.file_digest(Path(args.source).open('rb'),'sha256').hexdigest()
 result=dict(source_sha256=sourcehash,n_all_tasks=n,tasks=dict(tasks),n_update_rows=len(details),n_books=len(books),n_book_characters=len(tracks),target_field_types={k:dict(v) for k,v in fieldtypes.items()},by_book={b:dict(n=v,flags=dict(stats[b])) for b,v in sorted(books.items())},trajectory_length_histogram=dict(sorted(lengths.items())),updates_per_character_histogram=dict(sorted(changed.items())),continuation=dict(continuation),note='Source training records, not a new held-out benchmark. Continuity hashes use native f-string representation of tracker dicts. Byte continuity only; labels and initial states may be constructed with later story evidence. No model performance or exact psychological truth inferred.')
 Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');Path(args.local_updates+'.index.json').write_text(json.dumps(details,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['by_book','trajectory_length_histogram','updates_per_character_histogram']},indent=2))
if __name__=='__main__':main()
