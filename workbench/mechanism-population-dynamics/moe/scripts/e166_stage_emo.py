"""Path-only EMO recovery: sequential NFS reads into verified node NVMe, no GPU."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import socket
import time

WB=Path(__file__).resolve().parents[2]
ROOT=WB/'moe/results/e166'
TARGET=Path('/tmp/xiang-moe-20261029/e166_emo')


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    if (ROOT/'emo_local_staging.json').exists():raise FileExistsError('Preserve prior staging record')
    start=time.monotonic();models={
        'P':json.loads((WB/'moe/results/e154/asset_manifest.json').read_text())['model'],
        'B':json.loads((WB/'moe/results/e150/asset_manifest.json').read_text())['models']['StdMoE_1b14b_1T_EmoAnnealed']}
    TARGET.mkdir(parents=True,exist_ok=True)
    required=sum(item['size_bytes'] for model in models.values() for item in model['files'].values())
    if shutil.disk_usage(TARGET).free<required+2**30:raise RuntimeError('Insufficient free node NVMe')
    first=next(item for name,item in models['B']['files'].items() if name.endswith('.safetensors'))
    probe=TARGET/'bounded_probe.bin';t=time.monotonic()
    with Path(first['path']).open('rb') as src,probe.open('xb') as dst:
        for _ in range(32):dst.write(src.read(8*2**20))
    probe_seconds=time.monotonic()-t;probe_bytes=probe.stat().st_size;probe.unlink()
    print(json.dumps({'event':'bounded_sequential_probe','bytes':probe_bytes,'seconds':probe_seconds}),flush=True)
    def copy(item):
        label,name,source=item;dest=TARGET/label/name;dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():
            temporary=dest.with_name(dest.name+'.part')
            with Path(source['path']).open('rb') as src,temporary.open('xb') as dst:
                shutil.copyfileobj(src,dst,8*2**20)
            temporary.rename(dest)
        if dest.stat().st_size!=source['size_bytes'] or sha(dest)!=source['sha256']:raise ValueError('NVMe byte mismatch: '+str(dest))
        return label,name,{'path':str(dest),'size_bytes':dest.stat().st_size,'sha256':source['sha256']}
    items=[(label,name,item) for label,model in models.items() for name,item in model['files'].items()]
    staged={label:{'directory':str(TARGET/label),'files':{}} for label in models}
    with ThreadPoolExecutor(max_workers=2) as pool:
        for label,name,item in pool.map(copy,items):
            staged[label]['files'][name]=item
            if name.endswith('.safetensors'):print(json.dumps({'event':'verified_local_shard','label':label,'file':name}),flush=True)
    record={'status':'complete','host':socket.gethostname(),'models':staged,'total_bytes':required,
            'seconds':time.monotonic()-start,'GPU_seconds':0,'script_sha256':sha(__file__),
            'plan_sha256':sha(ROOT/'plan.json'),'probe_bytes':probe_bytes,'probe_seconds':probe_seconds,
            'scope':'Identical existing public FP32 bytes, materialized files; original native loader and canonical fingerprints retained.'}
    (ROOT/'emo_local_staging.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'status':'complete','seconds':record['seconds'],'bytes':required}),flush=True)


if __name__=='__main__':main()
