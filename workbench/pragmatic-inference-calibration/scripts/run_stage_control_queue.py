#!/usr/bin/env python3
"""E26 finite eight-GPU queue; no replacement or overwrite of prior runs."""
import fcntl,hashlib,json,os,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from run_followup_queue import ROOT,PYTHON,Q25
from run_qwen_stage_queue import BASE
from epitome_data import prepare

def parity():
 from transformers import AutoTokenizer
 rows,_,_=prepare(ROOT)
 b=AutoTokenizer.from_pretrained(ROOT/'models'/BASE[0],local_files_only=True)
 i=AutoTokenizer.from_pretrained(ROOT/'models'/Q25[0],local_files_only=True)
 for name in [BASE[0],Q25[0]]:assert (ROOT/'models'/name/'DOWNLOAD_COMPLETE.json').exists()
 token_lists={}
 for condition in ['bare','format']:
  texts=[]
  for r in rows:
   text=r['prompt']
   if condition=='format':
    text=i.apply_chat_template([{'role':'user','content':'Reply with only one answer from: '+', '.join(r['choices'])+'.\n\n'+text}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
   left=b.encode(text,add_special_tokens=False);right=i.encode(text,add_special_tokens=False)
   assert left==right,(r['key'],condition)
   texts.append(left)
  token_lists[condition]={'n':len(texts),'sha256':hashlib.sha256(json.dumps(texts).encode()).hexdigest()}
 path=ROOT/'runs/E26-tokenizer-parity.json';assert not path.exists();path.write_text(json.dumps(token_lists,indent=2))
 print(json.dumps({'tokenizer_parity':token_lists}),flush=True)

def run(entry):
 gpu,kind,model,interface=entry;checkpoint,mid,sha=model
 name=f'E26-{kind}-{checkpoint}'+('-'+interface if interface else '')
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 script={'atomic':'run_epitome_stage.py','betting':'run_epitome_betting_stage.py','implicaturex':'run_implicaturex_stage.py'}[kind]
 command=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/'+script,'--root',str(ROOT),'--model',str(ROOT/'models'/checkpoint),'--model-id',mid,'--revision',sha,'--output',str(ROOT/'runs'/name)]
 if kind in ['atomic','betting']:command+=['--common-template',str(ROOT/'models/Qwen2.5-3B-Instruct')]
 if interface:command+=['--interface',interface]
 with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  assert not (ROOT/'runs'/name).exists()
  print(json.dumps({'start':name,'gpu':gpu}),flush=True)
  with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
  print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
  return name,code

def main():
 parity()
 ol=json.loads((ROOT/'models/olmoe-stage-manifest.json').read_text())[:2]
 entries=[(0,'atomic',BASE,None),(1,'atomic',Q25,None),(2,'betting',BASE,'bare'),(3,'betting',BASE,'common-chat'),(4,'betting',Q25,'bare'),(5,'betting',Q25,'common-chat')]
 entries += [(gpu,'implicaturex',(m['id'].split('/')[-1],m['id'],m['sha']),'bare') for gpu,m in zip([6,7],ol)]
 failed=[]
 with ThreadPoolExecutor(max_workers=8) as pool:
  for f in as_completed([pool.submit(run,e) for e in entries]):
   try:
    name,code=f.result()
    if code:failed.append(name)
   except Exception as e:failed.append(str(e));print(json.dumps({'failure':str(e)}),flush=True)
 print(json.dumps({'failed':failed}),flush=True)
 raise SystemExit(bool(failed))
if __name__=='__main__':main()
