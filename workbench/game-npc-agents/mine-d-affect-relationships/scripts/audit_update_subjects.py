#!/usr/bin/env python3
"""Export the completed manual short-description subject audit, not an LLM judge."""
import argparse,json,hashlib
from pathlib import Path
from collections import Counter

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);a.add_argument('--condition',choices=['original','identity_line'],default='original');a.add_argument('--plan-run');args=a.parse_args();root=Path(args.asset_root);refs={r['task_id']:r for r in map(json.loads,(root/'data/update_D-E04/references.jsonl').read_text().splitlines())}
 # All 128 short descriptions were read. These are literal subject findings,
 # not a claim that every other event, trait, or psychological inference is right.
 wrong8={'ew/4d7ae445afb12b3e6f19f28a':'Jim Hawkins','ew/737471600796935619a10443':'Jim Hawkins','ew/9bab3efca4800a942a9c1f10':'Buck','ew/f0a2f100575543084e30bb8c':'Bathsheba Everdene','ew/2916366d5f614a1ee7afd585':'Tertius Lydgate','ew/e056bf36147313011fbef75b':'Cardinal Richelieu','ew/1af8cf99d05af1daefddfdb6':'John Watson'}
 wrong32={k:v for k,v in wrong8.items() if k in ['ew/4d7ae445afb12b3e6f19f28a','ew/737471600796935619a10443','ew/e056bf36147313011fbef75b','ew/1af8cf99d05af1daefddfdb6']}
 if args.condition=='identity_line':
  # All 128 control short descriptions were read before entering these labels.
  wrong8={k:v for k,v in wrong8.items() if k in ['ew/737471600796935619a10443','ew/2916366d5f614a1ee7afd585','ew/e056bf36147313011fbef75b']};wrong32={'ew/737471600796935619a10443':'Jim Hawkins'}
 nonactive={'ew/e056bf36147313011fbef75b':'Source profile says unborn historical comparison, not an active NPC.','ew/1af8cf99d05af1daefddfdb6':'Source profile says deceased ancestor/legend; current scene revisits his legacy.'}
 alias_case='ew/cff53ffb5d34605cdcb6556b';annotations=[]
 specs=[('step5_preview',{})] if args.plan_run else [('qwen3_8b',wrong8),('qwen3_32b',wrong32)]
 # Step's complete 64 selected descriptions were separately read; none explicitly
 # changes the subject. This does not certify the facts in its current state.
 for model,wrong in specs:
  base=root/'runs/D-E04';base=base/'identity_line' if args.condition=='identity_line' else base
  path=Path(args.plan_run)/'selected_responses.jsonl' if args.plan_run else base/model/'responses.jsonl'
  rows=[json.loads(l) for l in path.read_text().splitlines()];assert len(rows)==64
  for r in rows:
   tid=r['task_id'];status='explicit_wrong_subject' if tid in wrong else 'consistent_target_subject'
   if args.condition=='original' and model=='qwen3_8b' and tid==alias_case:status='ambiguous_entity_alias'
   v=dict(task_id=tid,model=model,book_name=r['book_name'],target=r['role'],scene_index=r['scene_index'],status=status,response_sha256=hashlib.sha256(r['response'].encode()).hexdigest(),preselected_case=refs[tid]['preselected_case'])
   if tid in wrong:v['named_output_subject']=wrong[tid]
   if tid in nonactive:v['source_scope_note']=nonactive[tid]
   if tid==alias_case:v['source_alias_note']='Target The Doctor is the anonymous apothecary. Source also tags Dr. Henry Jekyll in the group scene; do not treat the 8B name resolution alone as an unambiguous capability failure.'
   v['definite_current_record_subject_error']=status=='explicit_wrong_subject' and tid not in nonactive
   annotations.append(v)
 result=dict(experiment='D-E05' if args.plan_run else 'D-E04',condition=args.condition,status='POST-HOC manual descriptive audit of all selected short descriptions in this condition',reviewer='Execution agent; no independent blind human coding',criterion='Explicitly writing the description about a different native character. Aliases/unnamed descriptions are not automatically errors. Consistent target subject does not certify event ownership or psychological accuracy. Readable descriptions in malformed JSON are audited as text, not counted as executable outputs.',counts={m:dict(Counter(r['status'] for r in annotations if r['model']==m)) for m,_ in specs},definite_current_record_counts={m:sum(r['definite_current_record_subject_error'] for r in annotations if r['model']==m) for m,_ in specs},denominator_per_model=64,annotations=annotations)
 Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='annotations'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
