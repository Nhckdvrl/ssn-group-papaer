"""Pinned current models via domestic ModelScope routes, never HF/CDN fallback."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import time
from urllib.parse import urljoin, urlsplit
import requests
from data import sha

REPOS=['Qwen/Qwen3.8-27B','google/gemma-4-31B-it','mistralai/Ministral-3-14B-Instruct-2512']


def domestic_get(session, url, **kwargs):
    for _ in range(6):
        parsed=urlsplit(url)
        assert parsed.scheme=='https' and (parsed.hostname=='modelscope.cn' or parsed.hostname.endswith('.modelscope.cn'))
        response=session.get(url,allow_redirects=False,**kwargs)
        if response.status_code not in [301,302,303,307,308]:return response
        target=urljoin(url,response.headers['Location']);response.close();url=target
    raise RuntimeError('Too many domestic redirects')


def download(root, models):
    jobs=[]; manifests={}
    for repo in REPOS:
        listing=root/(repo.replace('/','--')+'-modelscope-files.json')
        doc=json.loads(listing.read_text());assert doc['Success']
        hf=json.loads((root/(repo.split('/')[-1]+'-metadata.json')).read_text())
        hm={x['rfilename']:x for x in hf['siblings']}
        files=[x for x in doc['Data']['Files'] if x['Type']=='blob' and x['Path']!='.gitattributes'
               and not x['Path'].startswith('original/') and not x['Path'].endswith(('.bin','.pth','.pt','.gguf'))]
        excluded=[]
        if any(x['Path'].startswith('model-') and x['Path'].endswith('.safetensors') for x in files):
            excluded=[x for x in files if x['Path']=='consolidated.safetensors']
            files=[x for x in files if x not in excluded]
        out=models/repo.split('/')[-1];out.mkdir(parents=True,exist_ok=True)
        for meta in files:
            assert isinstance(meta['Revision'],str) and len(meta['Revision'])==40
            assert len(meta['Sha256'])==64
            if meta['Path'] in hm and 'lfs' in hm[meta['Path']]:
                assert meta['Sha256']==hm[meta['Path']]['lfs']['sha256']
            jobs.append((repo,out,meta))
        manifests[repo]=dict(model=repo,download_origin='https://modelscope.cn',proxy_used=False,
            allowed_asset_hosts='modelscope.cn and subdomains only; overseas redirects rejected',
            hf_reference_revision=hf['sha'],listing_sha256=sha(listing),files=files,
            excluded_duplicate_original_formats=excluded,
            hf_byte_identity='Used LFS files matched fixed hf-mirror metadata before transfer; all used files pinned by ModelScope revision/size/SHA256.')
    # Interleave models; global four transfers rather than nested per-model pools.
    jobs.sort(key=lambda j:(j[2]['Path'].endswith('.safetensors'),j[2]['Path'],j[0]))
    def fetch(job):
        repo,out,meta=job;path=out/meta['Path'];path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.stat().st_size==meta['Size'] and sha(path)==meta['Sha256']:return
        part=path.with_suffix(path.suffix+'.domestic-part')
        for attempt in range(4):
            try:
                offset=part.stat().st_size if part.exists() else 0
                with requests.Session() as session:
                    session.trust_env=False
                    req=requests.Request('GET','https://modelscope.cn/api/v1/models/'+repo+'/repo',
                        params={'Revision':meta['Revision'],'FilePath':meta['Path']}).prepare()
                    with domestic_get(session,req.url,headers={'Range':f'bytes={offset}-'} if offset else {},
                                      stream=True,timeout=(15,90)) as response:
                        response.raise_for_status()
                        if response.status_code!=206:offset=0
                        with part.open('ab' if offset else 'wb') as f:
                            for block in response.iter_content(8<<20):f.write(block)
                assert part.stat().st_size==meta['Size'] and sha(part)==meta['Sha256']
                part.replace(path);print(repo,path.name,'verified',meta['Size'],flush=True);return
            except Exception as e:
                print(repo,path.name,'attempt',attempt,type(e).__name__,flush=True)
                if attempt==3:raise
                time.sleep(2)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,jobs))
    for repo,manifest in manifests.items():
        out=models/repo.split('/')[-1]
        assert all((out/m['Path']).stat().st_size==m['Size'] for m in manifest['files'])
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(repo,'COMPLETE',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--metadata',type=Path,required=True)
    p.add_argument('--models',type=Path,required=True);a=p.parse_args();download(a.metadata,a.models)
