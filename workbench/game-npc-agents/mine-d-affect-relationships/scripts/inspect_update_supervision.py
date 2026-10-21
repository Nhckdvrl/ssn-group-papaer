#!/usr/bin/env python3
"""Readiness inventory of released Character Agent update supervision, no inference."""
import argparse,json,re,hashlib
from pathlib import Path
from collections import Counter

def main():
 a=argparse.ArgumentParser();a.add_argument('--data',required=True);a.add_argument('--out',required=True);args=a.parse_args();path=Path(args.data);rows=json.loads(path.read_text());flags=Counter();shape=Counter();bad=[];profiles=[]
 for i,row in enumerate(rows):
  conv=row['conversations'];shape[str([c['from'] for c in conv])]+=1
  user=next(c['value'] for c in conv if c['from']=='human');target=next(c['value'] for c in conv if c['from']=='assistant')
  try:
   o=json.loads(target);assert isinstance(o.get('profile_updated'),bool)
   flags[str(o['profile_updated'])]+=1;profiles.append(len(o.get('updated_profile') or ''))
   if o['profile_updated'] and not isinstance(o.get('updated_profile'),str):bad.append(i)
   if not o['profile_updated'] and o.get('updated_profile') is not None:bad.append(i)
  except Exception:bad.append(i)
  for section in ['Scene Scenario','Scene Interactions','Current Profile','Hidden Tracker','Current Motivation']:
   flags['has_'+section]+=int(('## '+section) in user)
  flags['explicit_lookahead_section_in_input']+=int('## LOOKAHEAD' in user or '## Lookahead' in user)
 result=dict(n_rows=len(rows),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),counts=dict(flags),conversation_roles=dict(shape),format_or_flag_mismatch_count=len(bad),task_file_has_book_metadata=any('details' in r or 'book_name' in r for r in rows),provenance_note='Task-level ShareGPT release strips details; full all_tasks_with_details and extracted per-book assets are separate. Counts describe training supervision, not held-out model performance or unique psychological truth.',input_note='Observed scene plus scene-start profile/tracker/motivation; actor thoughts from others are masked by native transformer. Construction may use later evidence for labels; this is distinct from explicit lookahead input.')
 Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
