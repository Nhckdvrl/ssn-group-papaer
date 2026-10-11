import sys,gc,json
from types import SimpleNamespace
from pathlib import Path
sys.path.insert(0,'/home/xiang/ssn-group-papaer/workbench/latent-world-model-planning/scripts')
import bounded_control as b
import torch
seed=int(sys.argv[1]);hf=Path('/home/xiang/.cache/huggingface');root=Path('/home/xiang/.cache/latent-wm-results')
directory=['E16_data_compute_s0','E16_fixed_data_trainseed_RTX_s1','E16_fixed_data_trainseed_RTX_s2'][seed]
sources=[(f'BASE-s{seed}',hf/'latent-wm-trained'/directory/'BASE100_u5650.ckpt')]
if seed==0:sources.insert(0,('RELEASED',hf/'latent-wm-derived/lewm-tworoom-object.ckpt'))
for method in ['PLAIN','GLOBAL-SG','CENTER','DET-INVERSE','PROB-INVERSE']:
 run=f'20261004-E20-joint-{method}-A100-s{seed}';assert json.loads((root/run/'complete.json').read_text())['completed']
 sources.append((f'{method}-s{seed}',hf/'latent-wm-trained'/run/'u2000.ckpt'))
for name,checkpoint in sources:
 run=f'20261004-E20-control-{name}-physical-A100'
 args=SimpleNamespace(bank='/tmp/latent-control-data/20261004-E20-fresh-control-bank48',output='/tmp/latent-wm-runs/'+run,checkpoint=str(checkpoint),interface='physical')
 try:b.evaluate(args)
 except Exception as error:
  out=Path(args.output)
  if out.exists():b.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
  raise
 gc.collect();torch.cuda.empty_cache()
