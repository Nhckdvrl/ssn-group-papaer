"""Direct-only ModelScope mirror download; pin every file and verify SHA256."""
import concurrent.futures
import json
import os
from pathlib import Path
import time
import requests
from data import CACHE, sha

REVISION='26028140be3ee69b82b1d1450179ab71bb1121b9'

def fetch(meta):
    p=CACHE/'models/Qwen3-8B'/meta['Path'];p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists() and p.stat().st_size==meta['Size'] and sha(p)==meta['Sha256']:
        return meta
    url=f'https://modelscope.cn/api/v1/models/Qwen/Qwen3-8B/repo?Revision={REVISION}&FilePath={meta["Path"]}'
    tmp=p.with_suffix(p.suffix+'.direct-part')
    for attempt in range(4):
        try:
            session=requests.Session();session.trust_env=False
            n=tmp.stat().st_size if tmp.exists() else 0
            with session.get(url,headers={'Range':f'bytes={n}-'} if n else {},stream=True,timeout=(20,90)) as r:
                r.raise_for_status()
                if r.status_code!=206:n=0
                with tmp.open('ab' if n else 'wb') as f:
                    for block in r.iter_content(8<<20):f.write(block)
            assert tmp.stat().st_size==meta['Size'], (p.name,tmp.stat().st_size,meta['Size'])
            assert sha(tmp)==meta['Sha256'],f'SHA mismatch {p}'
            tmp.replace(p);print('verified',p.name,meta['Size'],flush=True)
            return meta
        except Exception:
            if attempt==3:raise
            time.sleep(2)

if __name__=='__main__':
    for key in list(os.environ):
        if key.lower() in ('http_proxy','https_proxy','all_proxy'):os.environ.pop(key)
    s=requests.Session();s.trust_env=False
    r=s.get(f'https://modelscope.cn/api/v1/models/Qwen/Qwen3-8B/repo/files?Revision={REVISION}&Recursive=true',timeout=30)
    r.raise_for_status();listing=r.json();assert listing['Success']
    files=[x for x in listing['Data']['Files'] if x['Type']=='blob' and x['Name']!='.gitattributes']
    manifest={'model':'Qwen/Qwen3-8B','download_origin':'https://modelscope.cn/Qwen/Qwen3-8B',
              'mirror_revision':REVISION,'hf_reference_revision':'b968826d9c46dd6066d109eabc6255188de91218',
              'hf_byte_identity':'not independently verified; actual files fixed by mirror SHA256',
              'proxy_used':False,'license':'Apache-2.0','files':files}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,files))
    (CACHE/'models/Qwen3-8B/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('DONE',flush=True)
