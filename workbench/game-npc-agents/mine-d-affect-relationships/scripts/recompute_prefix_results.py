#!/usr/bin/env python3
"""Keep full-prefix main and nested recent-context cohorts separate."""
import argparse,json,subprocess,time
from collections import defaultdict
from pathlib import Path
from statistics import mean
from queue_local_judges import wait_done
from summarize_results import arcane,paired_arcane,interval

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;results=scripts.parent/'results';python='/home/xiang/miniconda3/envs/openslime/bin/python';wait_done(root/'runs/D-E09/transport_complete.json')
 main_table=None
 for strict in [False,True]:
  table=arcane(root,'D-E09',strict=strict);path=results/('D-E09-summary-strict.json' if strict else 'D-E09-summary.json');path.write_text(json.dumps(table,ensure_ascii=False,indent=2)+'\n')
  if not strict:assert len(table['details'])==372 and all(g['n_per_response']==47 and g['n_trajectories']==15 for g in table['groups'].values());main_table=table
 subprocess.run([python,str(scripts/'plot_arcane.py'),'--summary',str(results/'D-E09-summary.json'),'--out-prefix',str(results/'figures/D-E09-full-prefix')],cwd=project,check=True)
 # All recent-context rows are already source-qualified by the completed D-E08 table.
 priorfile=results/'D-E08-summary.json'
 while True:
  if priorfile.exists():
   try:
    prior=json.loads(priorfile.read_text())
    if len(prior['details'])==1484:break
   except (ValueError,KeyError):pass
  time.sleep(5)
 probes=set(json.loads((root/'data/arcane_D-E07_v2/preselected_review.json').read_text())['probes'].values());allowed={'Qwen/Qwen3-8B','arcane-8B-dpo'};rows=[r for r in prior['details'] if r['model'] in allowed and r['probe_id'] in probes]+[r for r in main_table['details'] if r['mode']=='prefix_memory' and r['probe_id'] in probes];assert len(rows)==312;grouped=defaultdict(dict)
 for r in rows:grouped[r['model']+'|'+r['mode']][r['judge_id']]=r
 groups={}
 for group,values in grouped.items():
  per_book=defaultdict(lambda:defaultdict(list))
  for r in values.values():
   scores={k:r['scores'][k] for k in ['apf','rpf','rae']} if r['kind']=='per_response' else {'ptf':mean(r['scores'][k] for k in ['ptf_alignment','ptf_direction','ptf_shape'])}
   for key,value in scores.items():per_book[r['novel']][key].append(value)
  books={b:{k:mean(v) for k,v in d.items()} for b,d in per_book.items()};groups[group]=dict(n_per_response=sum(r['kind']=='per_response' for r in values.values()),n_trajectories=sum(r['kind']=='trajectory' for r in values.values()),by_book=books,metrics={m:mean(b[m] for b in books.values()) for m in ['apf','rpf','rae','ptf']})
  assert groups[group]['n_per_response']==20 and groups[group]['n_trajectories']==6
 pairs={}
 for model in sorted(allowed):
  for other in ['vanilla','arc','summary','state_summary','state_summary_step']:pairs[model+'|prefix_memory-'+other]=paired_arcane(grouped,model+'|prefix_memory',model+'|'+other)
 nested=dict(experiment='D-E09',cohort='Nested common 6 complete probes / 20 phase instances / 6 preselected characters and books. Never compare these marginal means with the 15-probe/47-phase main table.',groups=groups,paired_deltas=pairs,source_tables=['D-E08-summary.json','D-E09-summary.json'],details=rows);(results/'D-E09-nested-context-comparison.json').write_text(json.dumps(nested,ensure_ascii=False,indent=2)+'\n')
 print('D-E09 main: 15 complete probes / 47 phases; nested: 6 / 20. New model calls: zero in analysis.',flush=True)
 print(json.dumps({k:v['metrics'] for k,v in main_table['groups'].items()},indent=2),flush=True)
if __name__=='__main__':main()
