"""Preflight every used geometry before fixed-endpoint goal policy training."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path
import goal_policy_baseline as g
p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True,choices=[0,1,2]);args=p.parse_args()
out=g.ROOT/f'20261005-E14-goalpolicy-pipeline-s{args.seed}';assert not out.exists();out.mkdir()
shutil.copy2(__file__,out/'queue_used.py');shutil.copy2(g.__file__,out/'trainer_used.py')
shutil.copy2(g.VENDOR/'idm/model.py',out/'official_model_used.py');shutil.copy2(g.VENDOR/'idm/dataset.py',out/'official_dataset_used.py')
commands=[]
for geometry in g.GEOMETRIES:
    commands += [['preflight','--geometry',geometry,'--device',device] for device in ['cpu','cuda']]
    commands += [['train','--geometry',geometry,'--arm',arm] for arm in g.ARMS]
g.save(out/'config.json',dict(seed=args.seed,script_sha256=g.sha(g.__file__),queue_sha256=g.sha(__file__),commands=commands))
try:
    for command in commands:
        subprocess.run([sys.executable,'-u',g.__file__,*command,'--seed',str(args.seed)],check=True)
    g.save(out/'complete.json',dict(completed=True,seed=args.seed,training_runs=6))
except Exception as error:
    g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise
