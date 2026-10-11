"""All used deployment precontrols, then both geometry controller families."""
import argparse
import shutil
import subprocess
import sys
import goal_policy_baseline as g
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True,choices=[0,1,2]);a=p.parse_args()
out=g.ROOT/f'20261005-E14-goalpolicy-control-pipeline-s{a.seed}';assert not out.exists();out.mkdir()
recipe=Path(__file__).with_name('goal_policy_control.py');shutil.copy2(recipe,out/'control_used.py');shutil.copy2(__file__,out/'queue_used.py')
commands=[['preflight','--geometry',geometry,'--device',device] for geometry in g.GEOMETRIES for device in ['cpu','cuda']]
commands += [['control','--geometry',geometry] for geometry in g.GEOMETRIES]
g.save(out/'config.json',dict(seed=a.seed,commands=commands,controller_sha256=g.sha(recipe),queue_sha256=g.sha(__file__)))
try:
 for command in commands:subprocess.run([sys.executable,'-u',str(recipe),*command,'--seed',str(a.seed)],check=True)
 g.save(out/'complete.json',dict(completed=True,seed=a.seed,episodes=576))
except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise
