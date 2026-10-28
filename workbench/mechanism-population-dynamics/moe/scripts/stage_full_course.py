"""Fetch pinned F on node-local NVMe, then publish verified bytes to durable HF cache.

CPU I/O only. Existing complete cache objects are checked, never replaced.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import time


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main(local_root):
    start=time.monotonic();local_root=Path(local_root);local_root.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(local_root).free < 2*54275336216+64*1024**3:
        raise RuntimeError('Insufficient temporary disk space including reserve')
    os.environ['HF_XET_CACHE']=str(local_root/'xet')
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS']='1'
    from huggingface_hub import snapshot_download
    from filelock import FileLock
    import full_course_assets as source
    pin=source.pin_metadata()
    requested=[r for r in pin['files'] if r['rfilename'].endswith(('.json','.py','.txt','.model','.jinja','.md','.safetensors'))]
    expected_total=sum(r['size'] for r in requested)
    snapshot=Path(snapshot_download(source.REPO,revision=source.PIN,allow_patterns=[r['rfilename'] for r in requested],
                  cache_dir=str(local_root/'hf_cache'),max_workers=2,token=False))
    fetched=time.monotonic();repo_dir='models--'+source.REPO.replace('/','--')
    destination=source.common.CACHE/repo_dir;durable_snapshot=destination/'snapshots'/source.PIN
    (destination/'blobs').mkdir(parents=True,exist_ok=True);durable_snapshot.mkdir(parents=True,exist_ok=True)
    lock_root=source.common.CACHE/'.locks'/repo_dir;lock_root.mkdir(parents=True,exist_ok=True)
    report={'status':'complete','source_sha256':sha(__file__),'asset_transport_source':{'path':str(Path(__file__).resolve()),'sha256':sha(__file__)},
            'pin_sha256':sha(source.ROOT/'repo_pin.json'),'model_code_executed':False,'training_or_inference_performed':False,
            'model':{'repo_id':source.REPO,'revision':source.PIN,'path':str(durable_snapshot),
                     'execution_root':str(snapshot),'execution_host':socket.gethostname(),'files':{}}}
    copied=0
    for remote in requested:
        name=remote['rfilename'];path=snapshot/name;lfs=remote.get('lfs');digest=sha(path)
        if path.stat().st_size!=remote['size'] or (lfs and digest!=lfs['sha256']):raise ValueError('Local public LFS mismatch '+name)
        if not lfs:
            data=path.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if blob!=remote['blobId']:raise ValueError('Local public Git blob mismatch '+name)
        object_name=lfs['sha256'] if lfs else remote['blobId'];target=destination/'blobs'/object_name
        with FileLock(str(lock_root/(object_name+'.lock')),timeout=120):
            if target.exists():
                if target.stat().st_size!=remote['size'] or sha(target)!=digest:raise ValueError('Existing complete durable object differs')
            else:
                temporary=target.with_name(target.name+'.e162-copy-'+socket.gethostname()+'.partial')
                with path.open('rb') as src,temporary.open('xb') as dst:
                    shutil.copyfileobj(src,dst,length=16*1024**2);dst.flush();os.fsync(dst.fileno())
                if temporary.stat().st_size!=remote['size'] or sha(temporary)!=digest:raise ValueError('Durable copy SHA differs')
                os.replace(temporary,target);copied+=remote['size']
            link=durable_snapshot/name
            if link.exists():
                if sha(link)!=digest:raise ValueError('Existing snapshot object differs')
            else:link.symlink_to(os.path.relpath(target,link.parent))
        report['model']['files'][name]={'path':str(link),'sha256':digest,'size_bytes':remote['size'],
            'public_lfs_sha256':None if not lfs else lfs['sha256'],'public_blob_id':remote['blobId']}
        print(json.dumps({'event':'F_durable_asset_verified','file':name,'bytes':remote['size'],'copied_so_far':copied}),flush=True)
    report.update(verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        staging={'host':socket.gethostname(),'local_root':str(local_root),'download_seconds':fetched-start,
                 'publish_verify_seconds':time.monotonic()-fetched,'total_seconds':time.monotonic()-start,
                 'requested_bytes':expected_total,'new_durable_bytes':copied,'free_local_bytes':shutil.disk_usage(local_root).free})
    source.common.write(source.ROOT/'asset_manifest.json',report)
    source.common.write(Path.home()/'mechpop_cache/e162_full_course_native/transport_stage.json',report)
    print(json.dumps({'status':'complete','files':len(requested),'download_seconds':report['staging']['download_seconds'],
                      'publish_verify_seconds':report['staging']['publish_verify_seconds']}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-root',type=Path,required=True);args=parser.parse_args()
    try:main(args.local_root)
    except Exception as error:
        path=Path.home()/'mechpop_cache/e162_full_course_native/transport_failure.json'
        path.parent.mkdir(exist_ok=True,parents=True)
        path.write_text(json.dumps({'status':'failed','type':type(error).__name__,
            'message':re.sub(r'https?://\S+','<URL omitted>',str(error))[:400]},indent=2)+'\n')
        raise SystemExit('Pinned F transport failed; see durable transport_failure.json')
