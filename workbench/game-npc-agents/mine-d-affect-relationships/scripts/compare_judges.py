#!/usr/bin/env python3
"""Compare identical native prompts across complete local and partial Plan judges."""
import argparse,json,math
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean
from summarize_results import parse_arcane_local,first_valid

def read(p):return [json.loads(l) for l in p.read_text().splitlines()]
def pearson(x,y):
 if len(x)<2:return None
 a=mean(x);b=mean(y);den=math.sqrt(sum((v-a)**2 for v in x)*sum((v-b)**2 for v in y));return sum((u-a)*(v-b) for u,v in zip(x,y))/den if den else None
def ranks(values):
 order=sorted(range(len(values)),key=lambda i:values[i]);out=[0]*len(values);i=0
 while i<len(order):
  j=i+1
  while j<len(order) and values[order[j]]==values[order[i]]:j+=1
  for k in order[i:j]:out[k]=(i+j-1)/2
  i=j
 return out
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);step=first_valid(read(root/'runs/D-E01/step5_judge/judgments.jsonl'),'judge_id');local={};source={}
 for name in ['local_qwen32_judge','local_qwen32_judge_recovery']:
  path=root/'runs/D-E01'/name/'responses.jsonl'
  if not path.exists():continue
  for r in read(path):
   p=parse_arcane_local(r)
   if p['parse_ok'] and p['judge_id'] not in local:local[p['judge_id']]=p;source[p['judge_id']]=r
 data=defaultdict(list);ids=[]
 for s in step:
  if s['judge_id'] not in local:continue
  l=local[s['judge_id']];assert s['request']['messages']==source[s['judge_id']]['messages'],'Different evaluator inputs cannot be called a cross-judge replicate';ids.append(s['judge_id'])
  dims=['apf','rpf','rae'] if s['kind']=='per_response' else ['ptf_alignment','ptf_direction','ptf_shape']
  for d in dims:data[d].append((s['scores'][d],l['scores'][d]))
  data['per_response_mean' if s['kind']=='per_response' else 'ptf_mean'].append((mean(s['scores'][d] for d in dims),mean(l['scores'][d] for d in dims)))
 metrics={}
 for d,pairs in data.items():
  x=[p[0] for p in pairs];y=[p[1] for p in pairs];metrics[d]=dict(n=len(pairs),pearson=pearson(x,y),spearman=pearson(ranks(x),ranks(y)),step_mean=mean(x),local_mean=mean(y),mean_local_minus_step=mean(v-u for u,v in pairs),mean_absolute_difference=mean(abs(v-u) for u,v in pairs))
 result=dict(n_step_valid=len(step),n_matched=len(ids),all_matched_messages_byte_equal=True,interpretation='Partial Step Plan resource-interrupted overlap only; no score merging, no complete independent model ranking, no independent human validity or mechanism proof. Responses/phases/probes share novels.',metrics=metrics,matched_judge_ids=ids)
 Path(args.out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
