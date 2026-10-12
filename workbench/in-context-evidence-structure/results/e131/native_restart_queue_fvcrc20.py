import json,os,subprocess,sys,time
from pathlib import Path
root=Path('/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure')
os.chdir(root)
assert os.uname().nodename=='fvcrc20'
base=root/'results/e131'; deadline=time.monotonic()+7200
while True:
 run=base/'llama70_confirmation_native/run.json'
 if run.exists():
  try:
   if json.loads(run.read_text()).get('matmul_allow_tf32',True) is False:
    print('Original native confirmation finalized before migration; no restart',flush=True);sys.exit(0)
  except json.JSONDecodeError:pass
 ready=(base/'model_identity_llama70_fvcrc20.json').exists()
 rows=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()
 idle=len(rows)==4 and all(float(x.split(',')[1])<128 and float(x.split(',')[2])==0 for x in rows)
 if ready and idle:break
 assert time.monotonic()<deadline
 print('WAIT assets_ready='+str(ready)+' idle_quad='+str(idle),flush=True);time.sleep(30)
print('Checkpoint ready and quad idle; executing reviewed same-protocol migration',flush=True)
sys.exit(subprocess.call([sys.executable,'-u','scripts/e131_native_restart.py','--legacy-parent','2710941','--legacy-worker','2715055']))
