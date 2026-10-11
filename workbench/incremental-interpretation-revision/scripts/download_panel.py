"""Direct ModelScope panel transfer, immutable per-file revisions and SHA256."""
import argparse
import concurrent.futures
import json
import time
from pathlib import Path
import requests
from data import CACHE, sha


def download(listing, out):
    doc = json.loads(listing.read_text()); assert doc['success']
    repo = doc['repo']; out.mkdir(parents=True, exist_ok=True)
    files = [f for f in doc['data']['Files'] if f['Type'] == 'blob' and
             f['Name'] != '.gitattributes' and not f['Path'].startswith('original/')]
    excluded=[]
    if any(f['Name'].startswith('model-') and f['Name'].endswith('.safetensors') for f in files):
        excluded=[f for f in files if f['Name']=='consolidated.safetensors' or
                  (f['Name'].startswith('pytorch_model') and f['Name'].endswith('.bin'))]
        files=[f for f in files if f not in excluded]
    def fetch(meta):
        path = out/meta['Path']; path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size == meta['Size'] and sha(path) == meta['Sha256']:
            return
        part = path.with_suffix(path.suffix+'.direct-part')
        url = f'https://modelscope.cn/api/v1/models/{repo}/repo'
        for attempt in range(3):
            try:
                session = requests.Session(); session.trust_env = False
                offset = part.stat().st_size if part.exists() else 0
                with session.get(url, params={'Revision': meta['Revision'], 'FilePath': meta['Path']},
                                 headers={'Range': f'bytes={offset}-'} if offset else {},
                                 stream=True, timeout=(15, 90)) as response:
                    response.raise_for_status()
                    if response.status_code != 206: offset = 0
                    with part.open('ab' if offset else 'wb') as stream:
                        for block in response.iter_content(8 << 20): stream.write(block)
                assert part.stat().st_size == meta['Size'], 'size mismatch'
                assert sha(part) == meta['Sha256'], 'SHA256 mismatch'
                part.replace(path)
                print(repo, path.name, 'verified', flush=True); return
            except Exception as error:
                print(repo, path.name, 'attempt', attempt, type(error).__name__, flush=True)
                if attempt == 2: raise
                time.sleep(2)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(fetch, files))
    manifest = dict(model=repo, download_origin='https://modelscope.cn', proxy_used=False,
                    hf_byte_identity='Not independently verified; mirror per-file revision, size and SHA256 pinned.',
                    listing_sha256=sha(listing), files=files,excluded_duplicate_original_formats=excluded)
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(repo, 'DONE', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--listings', type=Path, nargs='+', required=True)
    ap.add_argument('--models', type=Path, default=CACHE/'models'); args = ap.parse_args()
    def one(path):
        repo = json.loads(path.read_text())['repo']
        download(path, args.models/repo.rsplit('/', 1)[-1])
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: list(pool.map(one, args.listings))
