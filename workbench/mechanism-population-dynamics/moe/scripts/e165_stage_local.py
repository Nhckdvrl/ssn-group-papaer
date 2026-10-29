"""Resource-only local OLMoE view; public SHA checked, durable sources kept."""
import hashlib
import json
from pathlib import Path
import shutil
import socket
import time

WB=Path(__file__).resolve().parents[2]
ROOT=WB/'moe/results/e165'
DEST=Path('/tmp/xiang-moe-20261029/e165_mature')


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    if (ROOT/'local_staging.json').exists():raise FileExistsError('Keep prior local stage')
    assets=json.loads((ROOT/'asset_manifest.json').read_text());start=time.monotonic()
    DEST.mkdir(exist_ok=True,parents=True)
    if shutil.disk_usage(DEST).free<32_000_000_000:raise RuntimeError('Need32GB free local space')
    result={'status':'complete','host':socket.gethostname(),'models':{},'source_sha256':sha(__file__),
            'asset_manifest_sha256':sha(ROOT/'asset_manifest.json'),'durable_sources_retained':True}
    for label,item in assets['models'].items():
        directory=DEST/label;directory.mkdir(exist_ok=True);files={}
        for name,record in item['files'].items():
            target=directory/name;source=Path(record['path'])
            legacy=Path('/tmp/xiang-moe-20261025/olmoe')/name
            if not target.exists():
                if label=='A' and name.endswith('.safetensors') and legacy.exists() and sha(legacy)==record['sha256']:
                    target.symlink_to(legacy)
                else:
                    temporary=target.with_name(target.name+'.partial')
                    shutil.copyfile(source,temporary);temporary.replace(target)
            if target.stat().st_size!=record['size_bytes'] or sha(target)!=record['sha256']:
                raise ValueError('Local copy differs from durable public source')
            files[name]={'path':str(target),'sha256':record['sha256'],'size_bytes':record['size_bytes'],
                         'durable_source':str(source),'resolved':str(target.resolve())}
            print(json.dumps({'local_verified':label,'file':name,'seconds':time.monotonic()-start}),flush=True)
        result['models'][label]={'directory':str(directory),'files':files}
    result['elapsed_CPU_IO_seconds']=time.monotonic()-start
    (ROOT/'local_staging.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'complete','seconds':result['elapsed_CPU_IO_seconds']}),flush=True)


if __name__=='__main__':main()
