#!/usr/bin/env python3
"""Wait for the registered measurements and reconstruct new tables offline."""
import argparse,json,subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue_local_judges import wait_done

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;results=scripts.parent/'results';python='/home/xiang/miniconda3/envs/openslime/bin/python'
 def call(argv):subprocess.run([python]+list(map(str,argv)),cwd=project,check=True)
 def measure(exp):
  if exp=='D-E06':
   for name in ['baselines','teacher_forced','recursive_native','recursive_summary']:wait_done(root/'runs/D-E06'/('likelihood_'+name)/'metadata.json')
   for consumer in ['arcane_8b_dpo','qwen3_32b']:wait_done(root/'runs/D-E06'/('consumer_'+consumer)/'likelihood/metadata.json')
   paths=[]
   for consumer in ['qwen3_8b','arcane_8b_dpo','qwen3_32b']:
    p=results/('D-E06-'+consumer+'-summary.json');call([scripts/'summarize_closed_behavior.py','--asset-root',root,'--consumer',consumer,'--out',p]);assert json.loads(p.read_text())['status']=='COMPLETE';paths.append(p)
   call([scripts/'plot_closed_behavior.py','--summaries']+paths+['--out-prefix',results/'figures/D-E06-state-behavior'])
  else:
   wait_done(root/'runs/D-E07/transport_complete.json')
   if exp=='D-E08':wait_done(root/'runs/D-E08/transport_complete.json')
   for strict in [False,True]:
    p=results/(exp+('-summary-strict.json' if strict else '-summary.json'));cmd=[scripts/'summarize_results.py','--asset-root',root,'--experiment',exp,'--out',p]
    if strict:cmd+=['--strict-native-json']
    call(cmd);data=json.loads(p.read_text())
    if not strict:assert len(data['details'])==(1272 if exp=='D-E07' else 1484) and all(g['n_per_response']==81 and g['n_trajectories']==25 for g in data['groups'].values())
   call([scripts/'plot_arcane.py','--summary',results/(exp+'-summary.json'),'--out-prefix',results/'figures'/(exp+'-character-state')])
  print('OFFLINE ANALYSIS COMPLETE',exp,flush=True)
 with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(measure,['D-E06','D-E07','D-E08']))
 call([scripts/'collect_continuation_costs.py','--asset-root',root,'--out',results/'D-CONTINUATION-RUN-LEDGER.json','--include-strong-compiler','--require-complete'])
 print('All registered continuation tables complete; semantic review and source audit still required',flush=True)
if __name__=='__main__':main()
