#!/usr/bin/env python3
"""Freeze a book-balanced native state-update residency sample, no rewritten inputs."""
import argparse,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from index_update_provenance import array_items

def h(x):return hashlib.sha256(x.encode()).hexdigest()
def canonical(c):return h(json.dumps(c,sort_keys=True,ensure_ascii=False))
def main():
 a=argparse.ArgumentParser();a.add_argument('--source',required=True);a.add_argument('--task-only',required=True);a.add_argument('--out',required=True);a.add_argument('--manifest',required=True);args=a.parse_args();root=Path(args.out);root.mkdir(parents=True,exist_ok=True)
 rows=[json.loads(l) for l in Path(args.source).read_text().splitlines()];assert len(rows)==24977
 counter=Counter(canonical(r['conversations']) for r in rows)
 other=Counter(canonical(r['conversations']) for r in array_items(args.task_only));assert counter==other,'Mixed and task-only releases must agree'
 by=defaultdict(lambda:defaultdict(list))
 for r in rows:
  flag=json.loads(r['conversations'][-1]['value'])['profile_updated'];by[r['details']['book_name']][flag].append(r)
 def rank(x):return h('D-E04-fixed-native|'+x)
 books=sorted((b for b,v in by.items() if all(len(v[k])>=4 for k in [True,False])),key=rank)[:8];assert len(books)==8
 selected=[]
 for book in books:
  for flag in [True,False]:
   chars=defaultdict(list)
   for r in by[book][flag]:chars[r['details']['character']].append(r)
   for char,rs in chars.items():rs.sort(key=lambda r:rank(json.dumps(r['details'],sort_keys=True)))
   ordered=sorted(chars,key=lambda c:rank(book+'|'+str(flag)+'|'+c));choice=[]
   for index in range(max(map(len,chars.values()))):
    for char in ordered:
     if len(chars[char])>index:choice.append(chars[char][index])
     if len(choice)==4:break
    if len(choice)==4:break
   selected.extend(choice)
 tasks=[];refs=[];manifest=[];case_seen=set()
 for r in selected:
  d=r['details'];tid='ew/'+h(json.dumps(d,sort_keys=True))[:24];conv=r['conversations'];assert [c['from'] for c in conv]==['system','human','assistant'];target=json.loads(conv[-1]['value']);case=(d['book_name'],target['profile_updated']);review=case not in case_seen;case_seen.add(case)
  tasks.append(dict(task_id=tid,book_name=d['book_name'],role=d['character'],scene_index=d['scene_index'],messages=[dict(role='system',content=conv[0]['value']),dict(role='user',content=conv[1]['value'])]))
  refs.append(dict(task_id=tid,details=d,target=target,preselected_case=review))
  manifest.append(dict(task_id=tid,details=d,reference_profile_updated=target['profile_updated'],preselected_case=review,input_sha256=canonical(tasks[-1]['messages']),reference_sha256=canonical(target)))
 tasks.sort(key=lambda t:rank(t['task_id']));assert len(tasks)==64 and len(case_seen)==16
 for name,rr in [('tasks',tasks),('references',refs)]:
  (root/(name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
 result=dict(n_scenes=64,n_books=8,n_characters=len({(r['details']['book_name'],r['details']['character']) for r in refs}),books=books,counts=dict(Counter(str(r['target']['profile_updated']) for r in refs)),selection='Fixed SHA256 book selection, class balanced within each book, character round-robin within class; no model outcomes used.',mixed_equals_task_only=True,task_file_sha256=hashlib.file_digest((root/'tasks.jsonl').open('rb'),'sha256').hexdigest(),cases=manifest)
 Path(args.manifest).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
