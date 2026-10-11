"""All actual precontrols precede independent seed endpoints; preserve failed pipelines."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
import predictive_object_repeat as r

p=argparse.ArgumentParser();p.add_argument('--geometry',required=True,choices=['PRED','VALUE']);p.add_argument('--seed',required=True,type=int,choices=[1,2]);args=p.parse_args();r.set_seed(args.seed)
run=r.m.ROOT/f'20261005-E13-object-{args.geometry}-pipeline-s{args.seed}';assert not run.exists();run.mkdir()
shutil.copy2(__file__,run/'queue_used.py');shutil.copy2(r.__file__,run/'recipe_used.py')
r.m.dump(run/'config.json',dict(vars(args),recipe_sha256=r.m.digest(r.__file__),queue_sha256=r.m.digest(__file__)))
commands=[['features'],['preflight','--device','cpu'],['preflight','--device','cuda']]+[['train','--arm',arm] for arm in r.ARMS]
try:
    for command in commands:
        subprocess.run([sys.executable,'-u',str(Path(r.__file__)),*command,'--geometry',args.geometry,'--seed',str(args.seed)],check=True)
    r.m.dump(run/'complete.json',dict(completed=True,geometry=args.geometry,seed=args.seed,training_runs=2))
except Exception as error:
    r.m.dump(run/'failure.json',dict(type=type(error).__name__,message=str(error),current_phase=command));raise
