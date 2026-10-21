#!/usr/bin/env python3
"""One fixed same-information instruction control, all original update instances."""
import argparse,json,hashlib,subprocess,os
from pathlib import Path
from queue_local_judges import wait_done

LINE="Keep every update about the specified target character ({role}); distinguish that character's own actions, experiences, relations, and knowledge from those of every other person in the scene."

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--project',required=True);args=a.parse_args();root=Path(args.asset_root);project=Path(args.project);scripts=Path(__file__).resolve().parent;python='/home/xiang/miniconda3/envs/openslime/bin/python';source=root/'data/update_D-E04/tasks.jsonl';tasks=[json.loads(l) for l in source.read_text().splitlines()];assert len(tasks)==64
 for t in tasks:t['messages'][0]['content']+='\n\n'+LINE.format(role=t['role']);t['condition']='one_line_identity'
 frozen=root/'data/update_D-E04/identity_line_tasks.jsonl'
 assert not frozen.exists();frozen.write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in tasks));(root/'data/update_D-E04/identity_line_protocol.json').write_text(json.dumps(dict(line=LINE,n=64,original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),control_sha256=hashlib.sha256(frozen.read_bytes()).hexdigest()),indent=2)+'\n')
 wait_done(root/'runs/D-E02/target_likelihood/metadata.json')
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='2',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
 for name,checkpoint,revision,model in [('qwen3_8b','/home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218','b968826d9c46dd6066d109eabc6255188de91218','Qwen/Qwen3-8B'),('qwen3_32b',str(root/'models/Qwen3-32B'),'9216db5781bf21249d130ec9da846c4624c16137','Qwen/Qwen3-32B')]:
  cmd=[python,'-u',str(scripts/'run_local_text.py'),'--tasks',str(frozen),'--checkpoint',checkpoint,'--revision',revision,'--model',model,'--out',str(root/'runs/D-E04/identity_line'/name),'--max-tokens','8192','--batch-size','4']
  with (root/'logs'/('D-E04-identity-'+name+'.log')).open('w') as log:subprocess.run(cmd,cwd=project,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('Single instruction control complete',flush=True)
if __name__=='__main__':main()
