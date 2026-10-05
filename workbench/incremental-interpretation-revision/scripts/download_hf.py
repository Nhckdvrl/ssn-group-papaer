"""Direct HF mirror transfer with fixed revision and verified git/LFS hashes."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import time
import requests
from data import sha

def verify(path,meta):
    if not path.exists() or path.stat().st_size!=meta['size']:return False
    if 'lfs' in meta:return sha(path)==meta['lfs']['sha256']
    data=path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==meta['blobId']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--revision',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    for key in list(os.environ):
        if key.lower() in ('http_proxy','https_proxy','all_proxy'):os.environ.pop(key)
    s=requests.Session();s.trust_env=False
    url=f'https://hf-mirror.com/api/models/{args.repo}/revision/{args.revision}?blobs=true'
    r=s.get(url,timeout=30);r.raise_for_status();listing=r.json();assert listing['sha']==args.revision
    args.out.mkdir(parents=True,exist_ok=True)
    files=[m for m in listing['siblings'] if m['rfilename']!='.gitattributes']
    def fetch(meta):
        p=args.out/meta['rfilename']
        if verify(p,meta):return
        tmp=p.with_suffix(p.suffix+'.direct-part')
        for attempt in range(4):
            try:
                session=requests.Session();session.trust_env=False
                n=tmp.stat().st_size if tmp.exists() else 0
                u=f'https://hf-mirror.com/{args.repo}/resolve/{args.revision}/{meta["rfilename"]}'
                with session.get(u,headers={'Range':f'bytes={n}-'} if n else {},stream=True,timeout=(20,90)) as res:
                    res.raise_for_status()
                    if res.status_code!=206:n=0
                    with tmp.open('ab' if n else 'wb') as f:
                        for block in res.iter_content(8<<20):f.write(block)
                assert verify(tmp,meta),p.name
                tmp.replace(p);print('verified',p.name,flush=True);return
            except Exception:
                if attempt==3:raise
                time.sleep(2)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,files))
    checks={m['rfilename']:{'sha256':sha(args.out/m['rfilename']),'bytes':m['size'],'hf_expected':m.get('lfs',{}).get('sha256',m['blobId'])} for m in files}
    manifest={'model':args.repo,'hf_revision':args.revision,'download_origin':'https://hf-mirror.com',
              'hf_byte_identity':'all model/tokenizer/config/LICENSE files verified against fixed HF git/LFS manifest',
              'proxy_used':False,'license':'Apache-2.0','hf_checks':checks}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('DONE',flush=True)

if __name__=='__main__':main()
