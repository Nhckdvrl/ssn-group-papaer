"""Check actual mirror bytes against the pinned HF git/LFS manifest, without proxy."""
import hashlib
import json
import os
from pathlib import Path
import requests
from data import CACHE, sha

REVISION='b968826d9c46dd6066d109eabc6255188de91218'
if __name__=='__main__':
    s=requests.Session();s.trust_env=False
    r=s.get(f'https://hf-mirror.com/api/models/Qwen/Qwen3-8B/revision/{REVISION}?blobs=true',timeout=30)
    r.raise_for_status();info=r.json();assert info['sha']==REVISION
    root=CACHE/'models/Qwen3-8B';checks={}
    for meta in info['siblings']:
        name=meta['rfilename']
        if name=='.gitattributes':continue
        p=root/name
        if not p.exists():
            r=s.get(f'https://hf-mirror.com/Qwen/Qwen3-8B/resolve/{REVISION}/{name}',timeout=60)
            r.raise_for_status();p.write_bytes(r.content)
        assert p.stat().st_size==meta['size'],name
        if 'lfs' in meta:
            expected=meta['lfs']['sha256'];actual=sha(p);kind='LFS SHA256'
        else:
            data=p.read_bytes();actual=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
            expected=meta['blobId'];kind='git blob SHA1'
        assert actual==expected,(name,actual,expected)
        checks[name]={'sha256':sha(p),'hf_expected':expected,'verified_by':kind,'bytes':p.stat().st_size}
    manifest=json.loads((root/'manifest.json').read_text())
    manifest.update(hf_revision=REVISION,hf_byte_identity='verified all model/tokenizer/config/LICENSE bytes against pinned HF git/LFS manifest via hf-mirror.com',
                    hf_metadata_origin='https://hf-mirror.com',hf_checks=checks)
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Verified',len(checks),'files against HF',REVISION)
