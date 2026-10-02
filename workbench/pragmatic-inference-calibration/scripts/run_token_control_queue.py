#!/usr/bin/env python3
"""E27 corrected common tokenizer; finite Base/SFT/DPO dependency queue."""
import fcntl,hashlib,json,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from run_followup_queue import ROOT,PYTHON

def audit():
 from transformers import AutoTokenizer
 from epitome_data import prepare as ep
 from run_implicaturex import prepare as ix
 b=AutoTokenizer.from_pretrained(ROOT/'models/OLMoE-1B-7B-0125',local_files_only=True)
 s=AutoTokenizer.from_pretrained(ROOT/'models/OLMoE-1B-7B-0125-SFT',local_files_only=True)
 ei,_,_=ep(ROOT);ii,_=ix(ROOT)
 hu=[json.loads(l) for l in (ROOT/'data/hu.jsonl').read_text().splitlines()]
 sources={'hu':[r['prompt'] for r in hu],'epitome':[r['prompt'] for r in ei],'implicaturex':[r['system_prompt']+'\n\n'+r['prompt'] for r in ii]}
 out={'issue':'Same Jinja template with different tokenizer BOS and special-token map does not imply same input.', 'base_bos':b.bos_token_id,'sft_bos':s.bos_token_id,'bare_parity':{}}
 for name,texts in sources.items():
  ids=[b.encode(t,add_special_tokens=False) for t in texts];right=[s.encode(t,add_special_tokens=False) for t in texts]
  assert ids==right,(name,'bare-token mismatch')
  out['bare_parity'][name]={'n':len(texts),'sha256':hashlib.sha256(json.dumps(ids).encode()).hexdigest()}
 p=ROOT/'runs/E27-tokenizer-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)

def run(gpu,m,spec):
 cp,mid,sha=m;kind,bos=spec;name=f'E27-{kind}-{cp}'+(f'-bos{bos}' if bos is not None else '')
 marker=ROOT/'models'/cp/'DOWNLOAD_COMPLETE.json'
 for _ in range(1440):
  if marker.exists():break
  time.sleep(5)
 else:raise TimeoutError(str(marker))
 scripts={'implicaturex':'run_implicaturex_token_control.py','implicaturex-bare':'run_implicaturex_token_control.py','atomic':'run_epitome_token_control.py','betting':'run_epitome_betting_token_control.py','hu-chat':'run_hu_token_control.py','hu-bare':'run_hu_token_control.py'}
 cmd=[PYTHON,'workbench/pragmatic-inference-calibration/scripts/'+scripts[kind],'--root',str(ROOT),'--model',str(ROOT/'models'/cp),'--model-id',mid,'--revision',sha,'--output',str(ROOT/'runs'/name)]
 template=str(ROOT/'models/OLMoE-1B-7B-0125-SFT')
 if kind.startswith('implicaturex'):
  cmd+=['--common-tokenizer',template,'--interface','bare' if kind.endswith('bare') else 'common-chat']
  if bos is not None:cmd+=['--bos-token-id',str(bos)]
 else:cmd+=['--common-template',template]
 if kind=='betting':cmd+=['--interface','common-chat']
 if kind.startswith('hu'):cmd+=['--task','hu','--hu-readout',kind[3:],'--dtype','float32','--no-special-tokens','--numerical-gate','--batch-size','8']
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 with (ROOT/'gpu-locks'/f'{gpu}.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not (ROOT/'runs'/name).exists()
  print(json.dumps({'start':name,'gpu':gpu}),flush=True)
  with (ROOT/(name+'.log')).open('w') as log:code=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
  print(json.dumps({'done':name,'gpu':gpu,'exit':code}),flush=True)
  if code:raise RuntimeError(name)

def sequence(gpu,m,specs):
 for spec in specs:run(gpu,m,spec)

def main():
 audit();models=[(m['id'].split('/')[-1],m['id'],m['sha']) for m in json.loads((ROOT/'models/olmoe-stage-manifest.json').read_text())]
 base,sft,dpo=models
 entries=[(0,base,[('implicaturex',50279)]),(1,sft,[('implicaturex',50279)]),(2,base,[('implicaturex',0)]),(3,sft,[('implicaturex',0)]),(4,base,[('atomic',None)]),(5,sft,[('atomic',None)]),(6,base,[('betting',None),('hu-chat',None)]),(7,sft,[('betting',None),('hu-chat',None)])]
 entries += [(0,dpo,[('implicaturex',50279),('implicaturex-bare',None),('hu-bare',None),('hu-chat',None)]),(2,dpo,[('implicaturex',0),('atomic',None),('betting',None)])]
 failed=[]
 with ThreadPoolExecutor(max_workers=10) as ex:
  for f in as_completed([ex.submit(sequence,*e) for e in entries]):
   try:f.result()
   except Exception as e:failed.append(str(e));print(json.dumps({'failure':str(e)}),flush=True)
 print(json.dumps({'failed':failed}),flush=True);raise SystemExit(bool(failed))
if __name__=='__main__':main()
