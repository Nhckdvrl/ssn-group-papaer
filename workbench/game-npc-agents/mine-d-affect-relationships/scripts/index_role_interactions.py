#!/usr/bin/env python3
"""Extract published first role turns from the fixed mixed-task source."""
import argparse,json,hashlib
from pathlib import Path
from collections import Counter
from index_update_provenance import array_items

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);args=a.parse_args();root=Path(args.asset_root);books=set(json.loads((Path(__file__).resolve().parents[1]/'results/D-E04-selection.json').read_text())['books']);out=root/'data/EvolvingWorld/first_role_interactions.jsonl';assert not out.exists();counts=Counter();alltasks=Counter()
 with out.open('w') as f:
  for r in array_items(root/'data/EvolvingWorld/train/all_tasks_with_details.json'):
   d=r['details'];alltasks[d['task']]+=1
   if d['task']!='interaction_generation' or d['book_name'] not in books or d.get('segment_start')!=0:continue
   if d['character']=='Environment':counts['excluded_environment']+=1;continue
   c=r['conversations'];assert [v['from'] for v in c[:3]]==['system','human','assistant'];s=c[0]['value'];marker='## Your Character State\n';start=s.index(marker)+len(marker);tail=s[start:];padding=len(tail)-len(tail.lstrip());state,end=json.JSONDecoder().raw_decode(tail.lstrip());start+=padding
   if list(state)!=[d['character']]:counts['multi_or_mismatched_target']+=1;continue
   v=dict(details=d,conversations=c[:3],source_conversation_sha256=hashlib.sha256(json.dumps(c,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),n_source_turns=len(c),state=state[d['character']],state_json_start=start,state_json_end=start+end)
   f.write(json.dumps(v,ensure_ascii=False)+'\n');counts[d['book_name']]+=1
 meta=dict(source_sha256='2f9dd6b90c7ed6870916cce91fc5d8ec6ac218f3c0ec6a225736c095bf751e07',all_task_counts=dict(alltasks),selected_first_segments=dict(counts),file_sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest());out.with_suffix('.inventory.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps(meta,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
