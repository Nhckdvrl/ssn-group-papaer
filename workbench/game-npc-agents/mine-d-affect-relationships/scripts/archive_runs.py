#!/usr/bin/env python3
"""Persist completed unique outputs outside Git and verify every archived byte."""
import argparse,json,hashlib,tarfile,datetime,subprocess,socket,os
from pathlib import Path

def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--destination',required=True);a.add_argument('--manifest',required=True);args=a.parse_args();root=Path(args.asset_root);dest=Path(args.destination);dest.mkdir(parents=True,exist_ok=True,mode=0o700);archive=dest/'raw-runs-and-frozen-inputs.tar.gz';assert not archive.exists(),'Do not overwrite an existing research archive'
 required=['D-E01/qwen3_8b','D-E01/arcane_8b_dpo','D-E01/local_qwen32_judge','D-E02/qwen25_7b','D-E02/qwen3_32b_judge','D-E02/target_likelihood','D-E03/summary_teacher','D-E03/qwen3_8b','D-E03/arcane_8b_dpo','D-E03/qwen3_32b','D-E03/local_qwen32_judge','D-E03/local_qwen32_capacity_judge','D-E04/qwen3_8b','D-E04/qwen3_32b','D-E04/identity_line/qwen3_8b','D-E04/identity_line/qwen3_32b','D-E04/puf_judge','D-E05/step5','D-E05/puf_judge']
 for name in required:assert (root/'runs'/name/'metadata.json').exists(),'Registered run not started: '+name
 metas=list((root/'runs').rglob('metadata.json'));assert metas
 for path in metas:
  m=json.loads(path.read_text())
  if path.parent.name.startswith('step5_judge') or m.get('transport')=='step_plan':
   stopped=path.parent/'CALIBRATION.json'
   assert m.get('finished_utc') or (stopped.exists() and json.loads(stopped.read_text()).get('stopped_utc')),'API transport must have a finished/stopped record before archiving'
  else:assert m.get('complete') and m.get('finished_utc'),'Still running/failed: '+str(path)
 parts=['runs','logs','data/arcane_D-E01','data/arcane_D-E03','data/phase_D-E02','data/update_D-E04'];files=sorted(p for part in parts for p in (root/part).rglob('*') if p.is_file());assert files
 if (root/'environment.json').exists():files.append(root/'environment.json')
 index={str(p.relative_to(root)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in files}
 def clean(info):info.uid=info.gid=0;info.uname=info.gname='';return info
 with tarfile.open(archive,'w:gz',compresslevel=6) as tar:
  for p in files:tar.add(p,arcname=str(p.relative_to(root)),recursive=False,filter=clean)
 os.chmod(archive,0o600)
 with tarfile.open(archive,'r:gz') as tar:
  assert len(tar.getmembers())==len(index)
  for item in tar:
   stream=tar.extractfile(item);assert stream is not None;assert hashlib.file_digest(stream,'sha256').hexdigest()==index[item.name]['sha256'],'Archive verification failed: '+item.name
 result=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),host=socket.gethostname(),research_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),nvme_asset_root=str(root),persistent_archive=str(archive),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),all_members_verified=True,n_files=len(index),uncompressed_bytes=sum(v['bytes'] for v in index.values()),scope='Unique outputs, complete frozen prompts/references, run configs/source snapshots/token IDs/logs. Excludes model weights, vendor checkouts, complete third-party corpora. Step partial/calibration remain separate and incomplete by design; no cross-judge score merging.',files=index)
 Path(args.manifest).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
if __name__=='__main__':main()
