"""Push exact native deployment guards, then all three known policy baselines."""
import subprocess
import sys
import shutil
from pathlib import Path
import goal_policy_baseline as g
recipe=Path(__file__).with_name('goal_policy_pusht_control.py')
out=g.ROOT/'20261005-E14-goalpolicy-pusht-control-pipeline-s0';assert not out.exists();out.mkdir()
assert g.read(g.WB/'results/E14_20261005_pusht_goal_policy_endpoint_audit.json')['completed']
shutil.copy2(__file__,out/'queue_used.py');shutil.copy2(recipe,out/'controller_used.py')
commands=[['preflight','--device',d] for d in ['cpu','cuda']]+[['control']]
g.save(out/'config.json',dict(seed=0,commands=commands,controller_sha256=g.sha(recipe),queue_sha256=g.sha(__file__)))
try:
 for command in commands:subprocess.run([sys.executable,'-u',str(recipe),*command],check=True)
 g.save(out/'complete.json',dict(completed=True,seed=0,episodes=288))
except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error),phase=command));raise
