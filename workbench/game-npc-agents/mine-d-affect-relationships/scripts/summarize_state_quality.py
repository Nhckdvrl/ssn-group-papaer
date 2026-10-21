#!/usr/bin/env python3
"""PUF's native merit/demerit arithmetic, separate from update-label agreement."""
import argparse,json,re,math,hashlib,random
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean

def parse_puf(text):
 s=text.strip();clean=s
 if clean.startswith('```'):clean='\n'.join(l for l in clean.splitlines() if not l.strip().startswith('```')).strip()
 strict=True;obj=None
 try:obj=json.loads(clean)
 except ValueError:
  strict=False;prefix=re.sub(r'^```(?:json)?\s*','',s).lstrip()
  try:obj,end=json.JSONDecoder().raw_decode(prefix)
  except ValueError:pass
 ok=isinstance(obj,dict) and all(k in obj and isinstance(obj[k],list) for k in ['merits','demerits'])
 if ok:
  entries=obj['merits']+obj['demerits'];ok=all(isinstance(e,dict) and type(e.get('points')) in [int,float] and math.isfinite(e['points']) for e in entries)
 if not ok:return dict(parse_ok=False,native_json=False)
 merits=sum(abs(e['points']) for e in obj['merits']);demerits=sum(abs(e['points']) for e in obj['demerits'])
 return dict(parse_ok=True,native_json=strict,score=min(100,max(0,50+merits-demerits)),merits_sum=merits,demerits_sum=demerits,n_merits=len(obj['merits']),n_demerits=len(obj['demerits']),all_points_within_prompt_range=all(1<=abs(e['points'])<=10 for e in entries),reasoning_sha256=hashlib.sha256(str(obj.get('reasoning','')).encode()).hexdigest())

def ci(v):
 v=list(v);rng=random.Random(0);s=sorted(mean(rng.choices(v,k=len(v))) for _ in range(20000));return [s[499],s[19499]]
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);read=lambda p:[json.loads(l) for l in p.read_text().splitlines()];qual=json.loads((root/'data/update_D-E04/puf_tasks.qualification.json').read_text());rows=[]
 for name in ['puf_judge','puf_judge_recovery']:
  p=root/'runs/D-E04'/name/'responses.jsonl'
  if p.exists():rows+=read(p)
 valid={};invalid=[]
 for r in rows:
  p=parse_puf(r['response'])
  if not p['parse_ok']:invalid.append(r['task_id']);continue
  if r['task_id'] in valid:continue
  valid[r['task_id']]=dict({k:r[k] for k in ['task_id','question_id','actor_model','condition','book_name','role','scene_index','finish_reason','candidate_sha256']},**p)
 bucket=defaultdict(lambda:defaultdict(list));by_question=defaultdict(dict)
 for r in valid.values():bucket[r['actor_model']+'|'+r['condition']][r['book_name']].append(r);by_question[r['actor_model'],r['question_id']][r['condition']]=r
 groups={}
 for group,books in bucket.items():
  by_book={b:mean(r['score'] for r in rs) for b,rs in books.items()};groups[group]=dict(n=sum(map(len,books.values())),by_book=by_book,book_macro=mean(by_book.values()),descriptive_book_bootstrap95=ci(by_book.values()))
 paired={}
 for model in ['qwen3_8b','qwen3_32b']:
  changes=[dict(question_id=q,book_name=v['original']['book_name'],delta=v['identity_line']['score']-v['original']['score']) for (m,q),v in by_question.items() if m==model and set(v)=={'original','identity_line'}];b=defaultdict(list)
  for r in changes:b[r['book_name']].append(r['delta'])
  if b:
   ds={book:mean(v) for book,v in b.items()};paired[model]=dict(n_common_valid=len(changes),book_mean_delta=mean(ds.values()),by_book=ds,descriptive_book_bootstrap95=ci(ds.values()),win_tie_loss=[sum(r['delta']>0 for r in changes),sum(r['delta']==0 for r in changes),sum(r['delta']<0 for r in changes)],changes=changes)
 result=dict(experiment='D-E04',metric='Native PUF criterion and score formula, full-before-state single-character adapter; local Qwen3-32B judge, same-model actor bias possible; no gold flag/profile in judge input.',n_candidates=qual['n_candidates'],n_structural_candidates=qual['n_qualified'],n_judge_attempts=len(rows),n_valid_judgments=len(valid),invalid_judge_ids=sorted(set(invalid)-set(valid)),groups=groups,paired_instruction_effect=paired,point_range_diagnostic=dict(Counter(r['all_points_within_prompt_range'] for r in valid.values())),native_json_count=sum(r['native_json'] for r in valid.values()),finishes=dict(Counter(r['finish_reason'] for r in rows)),usage={k:sum(r['usage'][k] for r in rows) for k in ['prompt_tokens','completion_tokens']},details=list(valid.values()),qualification=qual['details'])
 Path(args.out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(groups,indent=2))
if __name__=='__main__':main()
