#!/usr/bin/env python3
"""Reuse an evaluator idle interval; stop only our verified waiting orchestrator."""
import argparse,datetime,json,os,signal,subprocess,time
from pathlib import Path
from queue_local_judges import wait_done
from summarize_results import parse_arcane_local

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);a.add_argument('--old-judge-orchestrator-pid',type=int,required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;base=root/'runs/D-E07';python='/home/xiang/miniconda3/envs/openslime/bin/python'
 wait_done(base/'local_qwen32_judge/metadata.json');raw=[json.loads(l) for l in (base/'local_qwen32_judge/responses.jsonl').read_text().splitlines()];assert len(raw)==248;missing={r['task_id'] for r in raw if not parse_arcane_local(r)['parse_ok']}
 if missing:wait_done(base/'local_qwen32_judge_recovery/metadata.json')
 pid=args.old_judge_orchestrator_pid;proc=Path('/proc')/str(pid);cmd=(proc/'cmdline').read_bytes().decode().replace('\0',' ');assert 'queue_corrected_judges.py' in cmd and '--capacity-only' not in cmd and str(root) in cmd
 for _ in range(10):
  children=(proc/'task'/str(pid)/'children').read_text().strip()
  if not children:break
  time.sleep(1)
 assert not children,'Never interrupt a model process';assert not (base/'local_qwen32_capacity_judge/metadata.json').exists();os.kill(pid,signal.SIGINT)
 ready=base/'primary_judge_transport_complete.json';ready.write_text(json.dumps(dict(complete=True,n=248))+'\n');(base/'gpu3_handoff.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),stopped_waiting_pid=pid,interrupted_model_calls=0,sequence=['D-E07 primary 248 plus uniform recovery','D-E08 two actors and 212 judges plus uniform recovery','D-E07 capacity 124 plus uniform recovery'],reason='Use GPU3 during capacity actor dependency wait; D-E08 frozen inputs and all decoding unchanged.'),indent=2)+'\n');print('GPU3 dependency handoff completed; no model call interrupted',flush=True)
 subprocess.run([python,'-u',str(scripts/'queue_strong_compiler.py'),'--asset-root',str(root),'--project',str(project),'--gpu','3','--after',str(ready)],cwd=project,check=True)
 subprocess.run([python,'-u',str(scripts/'queue_corrected_judges.py'),'--asset-root',str(root),'--project',str(project),'--capacity-only'],cwd=project,check=True)
 print('GPU3 registered measurements complete',flush=True)
if __name__=='__main__':main()
