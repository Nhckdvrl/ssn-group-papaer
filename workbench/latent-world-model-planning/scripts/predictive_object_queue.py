"""Geometry-local features and actual precontrols precede both fixed endpoints."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True,choices=['PRED','VALUE']);args=p.parse_args()
s=Path(__file__).with_name('predictive_object.py')
commands=[['features'],['preflight','--device','cpu'],['preflight','--device','cuda']]+[['train','--arm',a] for a in ['DIRECT','LOCAL']]
cache=Path('/tmp/latent-wm-data')/f'E13-object-{args.geometry}-frozen-features'
if (cache/'complete.json').exists():
 import predictive_object as recipe
 recipe.load_data(args.geometry)
 commands=commands[1:]
for command in commands:
 subprocess.run([sys.executable,'-u',str(s),*command,'--geometry',args.geometry],check=True,env=os.environ)
