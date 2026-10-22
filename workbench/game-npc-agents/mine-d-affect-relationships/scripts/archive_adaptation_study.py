#!/usr/bin/env python3
"""After completion, persist raw evidence and final LoRA checkpoints outside Git."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import time


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--experiment',choices=['D-E10','D-E11'],required=True)
    p.add_argument('--destination',required=True);p.add_argument('--sync-main',action='store_true');a=p.parse_args()
    root=Path(a.asset_root);run=root/'runs'/a.experiment
    dependency=run/('finish_status.json' if a.experiment=='D-E10' else 'judges/status.json')
    while True:
        try:status=json.loads(dependency.read_text())
        except (FileNotFoundError,json.JSONDecodeError):time.sleep(30);continue
        if status.get('error'):raise RuntimeError('Results unfinished; retain original assets: '+status['error'])
        if status.get('complete'):break
        time.sleep(30)
    dest=Path(a.destination);dest.mkdir(parents=True,exist_ok=True,mode=0o700)
    archive=dest/'raw-and-final-adapters.tar.gz';temporary=archive.with_suffix('.gz.partial')
    if archive.exists() or temporary.exists():raise FileExistsError('Never replace a research archive')
    files=[]
    for f in run.rglob('*'):
        if not f.is_file() or f.is_symlink():continue
        # Keep only FINAL training weights/optimizer, but retain intermediate
        # checkpoint descriptions and all startup/interruption evidence.
        if f.suffix in ['.pt','.safetensors'] and f.parent.name!='final':continue
        files.append(f)
    data=root/'data'/('evaluation_D-E10' if a.experiment=='D-E10' else 'native_D-E11')
    files.extend(f for f in data.rglob('*') if f.is_file())
    if a.experiment=='D-E10':
        for name in ['manifest.json','entries.jsonl','exclusions.jsonl']:
            f=root/'data/training_D-E10'/name
            if f.exists():files.append(f)
    files.extend(f for f in (root/'logs').glob(a.experiment+'-*') if f.is_file() and 'archive' not in f.name)
    files=sorted(set(files));index={str(f.relative_to(root)):dict(bytes=f.stat().st_size,sha256=sha(f)) for f in files}
    with tarfile.open(temporary,'w:gz',compresslevel=1) as tar:
        for f in files:tar.add(f,arcname=str(f.relative_to(root)),recursive=False)
    with tarfile.open(temporary,'r:gz') as tar:
        members=tar.getmembers()
        if len(members)!=len(index):raise ValueError('Archive membership mismatch')
        for item in members:
            if hashlib.file_digest(tar.extractfile(item),'sha256').hexdigest()!=index[item.name]['sha256']:
                raise ValueError('Archived bytes differ: '+item.name)
    os.chmod(temporary,0o600);temporary.rename(archive)
    repo=Path(__file__).resolve().parents[4]
    manifest=dict(experiment=a.experiment,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        archive_path=str(archive),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,n_files=len(index),
        all_members_verified=True,files=index,research_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
        scope='Full run evidence including failed/interrupted attempts and frozen evaluation inputs. D-E10 includes final LoRA and optimizer/RNG only; intermediate weights and base weights excluded. Training tokens regenerate from fixed original source and manifest. No completed-growth claim implied.')
    file=Path(__file__).resolve().parent.parent/'results'/(a.experiment+'-RAW-MANIFEST.json')
    file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    if a.sync_main:
        if subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()!='main':raise RuntimeError('Archive saved, branch changed')
        relative=str(file.relative_to(repo))
        subprocess.run(['git','add','--',relative],cwd=repo,check=True)
        subprocess.run(['git','commit','--only','-m','核验并登记人物适应实验的持久原始证据与最终适配器','--',relative],cwd=repo,check=True)
        subprocess.run(['git','push','origin','main'],cwd=repo,check=True)
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))


if __name__=='__main__':main()
