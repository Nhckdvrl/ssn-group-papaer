"""Fixed E20 crossed pilot endpoints, complete fresh48 on both original interfaces."""
import argparse
import gc
import json
import shutil
import time
from pathlib import Path
from types import SimpleNamespace
import torch
import matched_learning as m
import geometry_experience as g
import lewm_pilot
import bounded_control as b
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--geometry',choices=g.GEOMETRIES,required=True);args=p.parse_args()
 for arm in g.DATA:
  name=f'20261005-E20-geometry-{args.geometry}-{arm}-A100-s0';source=m.ROOT/name
  while not (source/'complete.json').exists():
   if (source/'failure.json').exists() or (Path('/tmp/latent-wm-runs')/name/'failure.json').exists():raise RuntimeError(f'Locked training failed: {name}')
   print('waiting_for_fixed_endpoint',name,flush=True);time.sleep(30)
  assert json.loads((source/'complete.json').read_text())==dict(completed=True,geometry=args.geometry,arm=arm,seed=0,updates=2825)
  cfg=json.loads((source/'config.json').read_text());assert cfg['script_sha256']==m.digest(g.__file__)
  checkpoint=m.HF/name/'u2825.ckpt';assert m.digest(checkpoint)==next(v['checkpoint_sha256'] for v in json.loads((source/'summary.json').read_text()) if v['updates']==2825)
  for interface in ['native','physical']:
   output=Path('/tmp/latent-wm-runs')/f'20261005-E20-geometry-control-{args.geometry}-{arm}-{interface}-RTX-s0'
   original=lewm_pilot.architecture
   def architecture(config):
    model,_=m.make_model(config,0,'ABS');assert not model.residual_target and len(model.state_dict())==303;return model
   lewm_pilot.architecture=architecture
   try:
    b.evaluate(SimpleNamespace(bank='/tmp/latent-wm-runs/20261004-E20-fresh-control-bank48',output=str(output),checkpoint=str(checkpoint),interface=interface))
    context=dict(geometry=args.geometry,arm=arm,seed=0,source_training_run=name,train_checkpoint_sha256=m.digest(checkpoint),loader_sha256=m.digest(__file__),namespace='official AD-WM, explicit ABS303; strict endpoint load',scope='crossed conditional development; geometry priors differ; source0 only; same original fresh48 two interfaces')
    b.save(output/'geometry_loader.json',context);shutil.copy2(output/'geometry_loader.json',m.ROOT/output.name/'geometry_loader.json')
   except Exception as error:
    if output.exists():b.save(output/'failure.json',dict(type=type(error).__name__,message=str(error)))
    raise
   finally:lewm_pilot.architecture=original
   gc.collect();torch.cuda.empty_cache()
