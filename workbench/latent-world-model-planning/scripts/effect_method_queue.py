import sys,json,gc
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/xiang/ssn-group-papaer/workbench/latent-world-model-planning/scripts')
import effect_training as e
import torch
method=sys.argv[1]
sources=['/home/xiang/.cache/huggingface/latent-wm-trained/E16_data_compute_s0/BASE100_u5650.ckpt','/home/xiang/.cache/huggingface/latent-wm-trained/E16_fixed_data_trainseed_RTX_s1/BASE100_u5650.ckpt','/home/xiang/.cache/huggingface/latent-wm-trained/E16_fixed_data_trainseed_RTX_s2/BASE100_u5650.ckpt']
for seed,checkpoint in enumerate(sources):
 name=f'20261004-E20-joint-{method}-A100-s{seed}'
 args=SimpleNamespace(bank='/tmp/latent-effect-data/20261004-E20-legal-effect-bank44',checkpoint=checkpoint,method=method,seed=seed,output='/tmp/latent-wm-runs/'+name,model_cache='/home/xiang/.cache/huggingface/latent-wm-trained/'+name)
 try:e.run(args)
 except Exception as error:
  out=Path(args.output)
  if out.exists():e.dump(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
  raise
 gc.collect();torch.cuda.empty_cache()
