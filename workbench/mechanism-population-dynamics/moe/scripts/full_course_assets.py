"""Verify and fetch the pinned mature full-course EMO checkpoint, without torch.

Metadata retrieval is a CPU preparation step. Weight retrieval requires the
registered full-course experiment card. Existing checkpoints are never changed.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import os
os.environ['HF_HUB_DISABLE_PROGRESS_BARS']='1'
from huggingface_hub import HfApi, snapshot_download
import e150_prepare_assets as common

ROOT=common.WB/'results/full_course_assets_2026-10-28'
REPO='allenai/Emo_1b14b_1T'
PIN='007852b1e3d22222f8ee03c6a53fa30e47898dcb'


def pin_metadata():
    path=ROOT/'repo_pin.json'
    if path.exists():
        result=json.loads(path.read_text())
    else:
        info=HfApi().model_info(REPO,revision=PIN,files_metadata=True,token=False)
        files=[]
        for file in info.siblings:
            lfs=file.lfs
            files.append({'rfilename':file.rfilename,'size':file.size,'blobId':file.blob_id,
                          'lfs':None if lfs is None else {'sha256':lfs.sha256,'size':lfs.size}})
        result={'id':info.id,'sha':info.sha,'files':files}
        common.write(path,result)
    if result['id']!=REPO or result['sha']!=PIN:raise ValueError('Pinned public identity mismatch')
    return result


def main(mode):
    if mode=='weights':
        cards=list((common.WB/'experiments').glob('E*-full-course-native-division.md'))
        cards+=list((common.WB.parent/'experiments').glob('E*-full-course-native-division.md'))
        if len(cards)!=1:raise ValueError('One registered full-course experiment card required')
    pin=pin_metadata()
    small=[f['rfilename'] for f in pin['files'] if f['rfilename'].endswith(('.json','.py','.txt','.model','.jinja','.md'))]
    weights=[f['rfilename'] for f in pin['files'] if f['rfilename'].endswith('.safetensors')]
    if len(weights)!=11 or sum(f['size'] for f in pin['files'] if f['rfilename'] in weights)!=54275336216:
        raise ValueError('Unexpected model weight package')
    names=small if mode=='metadata' else small+weights
    directory=Path(snapshot_download(REPO,revision=PIN,allow_patterns=names,
                   cache_dir=str(common.CACHE),max_workers=2,token=False))
    report={'status':'metadata_complete' if mode=='metadata' else 'complete',
            'source_sha256':common.sha(__file__),'pin_sha256':common.sha(ROOT/'repo_pin.json'),
            'model_code_executed':False,'training_or_inference_performed':False,
            'model':{'repo_id':REPO,'revision':PIN,'path':str(directory),'files':{}}}
    for remote in pin['files']:
        name=remote['rfilename']
        if name not in names:continue
        path=directory/name;actual=common.sha(path);lfs=remote.get('lfs')
        if path.stat().st_size!=remote['size'] or (lfs and actual!=lfs['sha256']):raise ValueError('Public asset identity mismatch '+name)
        if not lfs:
            data=path.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if blob!=remote['blobId']:raise ValueError('Public Git blob mismatch '+name)
        report['model']['files'][name]={'path':str(path),'sha256':actual,'size_bytes':path.stat().st_size,
            'public_lfs_sha256':None if not lfs else lfs['sha256'],'public_blob_id':remote['blobId']}
        print(json.dumps({'event':'full_course_asset_verified','file':name,'size_bytes':path.stat().st_size}),flush=True)
    report['verified_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    common.write(ROOT/('metadata.json' if mode=='metadata' else 'asset_manifest.json'),report)
    print(json.dumps({'status':report['status'],'file_count':len(report['model']['files'])}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('metadata','weights'));args=parser.parse_args()
    try:main(args.mode)
    except Exception as error:
        message=re.sub(r'https?://\S+','<URL omitted>',str(error))[:400]
        common.write(ROOT/(args.mode+'_failure.json'),{'status':'failed','type':type(error).__name__,'message':message})
        raise SystemExit(f'Full-course {args.mode} failed ({type(error).__name__}); recorded without URL credentials')
