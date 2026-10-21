#!/usr/bin/env python3
"""Build official PHASE-Tree judge inputs from completed native actor outputs."""
import argparse,json,hashlib
from pathlib import Path

def read(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def main():
 a=argparse.ArgumentParser();a.add_argument('--assets',required=True);a.add_argument('--responses',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.assets)
 refs={r['question_id']:r for r in read(root/'references.jsonl')};template=json.loads((root/'judge_template.json').read_text());rows=read(args.responses);tasks=[]
 assert len(rows)==256 and len({r['task_id'] for r in rows})==256
 for r in rows:
  sample=refs[r['question_id']]['sample'];prompt=template['prompt'].format(character_profile=sample['profile_text'],context=sample['input'],ground_truth=sample['output'],prediction=r['response'],rubric=template['rubric'])
  tasks.append(dict(task_id=r['task_id'],question_id=r['question_id'],mode=r['mode'],role=r['role'],corpus=r['corpus'],split=r['split'],candidate_sha256=hashlib.sha256(r['response'].encode()).hexdigest(),messages=[dict(role='user',content=prompt)]))
 with Path(args.out).open('w') as f:
  for r in tasks:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 print('Official Char/Sem prompt tasks:',len(tasks))
if __name__=='__main__':main()
