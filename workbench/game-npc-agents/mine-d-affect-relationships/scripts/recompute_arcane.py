#!/usr/bin/env python3
"""Recompute frozen ArcANE tables, strict sensitivity, overlap, and figures offline."""
import argparse,json,subprocess
from pathlib import Path
from queue_local_judges import wait_done
from summarize_results import parse_arcane_local

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;results=scripts.parent/'results';python='/home/xiang/miniconda3/envs/openslime/bin/python'
 for experiment,name in [('D-E01','local_qwen32_judge'),('D-E03','local_qwen32_judge'),('D-E03','local_qwen32_capacity_judge')]:
  run=root/'runs'/experiment/name;wait_done(run/'metadata.json');rows=[json.loads(l) for l in (run/'responses.jsonl').read_text().splitlines()]
  if any(not parse_arcane_local(r)['parse_ok'] for r in rows):wait_done(run.with_name(name+'_recovery')/'metadata.json')
 def call(argv):subprocess.run([python]+list(map(str,argv)),cwd=project,check=True)
 for experiment in ['D-E01','D-E03']:
  for strict in [False,True]:
   out=results/(experiment+('-summary-strict.json' if strict else '-summary.json'));cmd=[scripts/'summarize_results.py','--asset-root',root,'--experiment',experiment,'--out',out]
   if strict:cmd+=['--strict-native-json']
   call(cmd)
  call([scripts/'plot_arcane.py','--summary',results/(experiment+'-summary.json'),'--out-prefix',results/'figures'/(experiment+'-native-arcane')])
 call([scripts/'summarize_results.py','--asset-root',root,'--experiment','D-E01','--judge','step5','--out',results/'D-E01-Step5-partial.json'])
 call([scripts/'compare_judges.py','--asset-root',root,'--out',results/'D-E01-cross-judge.json'])
 print('ArcANE tables and figures recomputed without model calls',flush=True)
if __name__=='__main__':main()
