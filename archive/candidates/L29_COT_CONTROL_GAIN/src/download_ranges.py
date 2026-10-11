"""Resume pinned weight downloads in verified HTTP ranges; SHA256 check final files."""
import argparse,concurrent.futures,hashlib,json,pathlib,time,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'configs/models.json').read_text())
CHUNK=32*1024*1024

def fetch(job):
    step,name,sha,start,end=job; dst=TMP/(step+'_'+name+f'.{start}')
    if dst.exists() and dst.stat().st_size==end-start+1: return dst
    url=f'https://huggingface.co/{m["model_id"]}/resolve/{sha}/{name}?download=true&l29chunk={start}'
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
            with urllib.request.urlopen(req,timeout=120) as r:
                if r.status!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/'): raise RuntimeError('Range not respected: '+str(r.headers))
                data=r.read()
            if len(data)!=end-start+1: raise RuntimeError('Incomplete range')
            dst.write_bytes(data); return dst
        except Exception:
            if attempt==3: raise
            time.sleep(2**attempt)

ap=argparse.ArgumentParser()
ap.add_argument('--steps',nargs='+',default=['step_0100','step_1400','step_2800'])
ap.add_argument('--workers',type=int,default=24)
ap.add_argument('--output-root',type=pathlib.Path,default=pathlib.Path('/home/xiang/.cache/l29'))
ap.add_argument('--chunk-root',type=pathlib.Path,default=pathlib.Path('/tmp/l29-download'))
args=ap.parse_args()
TMP=args.chunk_root
TMP.mkdir(exist_ok=True,parents=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
    # Finish earliest checkpoint first so its no-claim natural-state audit can start.
    for step in args.steps:
        folder=args.output_root/step
        folder.mkdir(exist_ok=True,parents=True)
        for info in m['files'][step]:
            name=info['rfilename']; dst=folder/name; sha=m['revisions'][step]
            if dst.exists(): continue
            if not name.endswith('.safetensors'):
                with urllib.request.urlopen(f'https://huggingface.co/{m["model_id"]}/resolve/{sha}/{name}',timeout=120) as r: dst.write_bytes(r.read())
                continue
            size=info['lfs']['size']; tmp=dst.with_suffix(dst.suffix+'.part')
            start=tmp.stat().st_size if tmp.exists() else 0
            jobs=[(step,name,sha,i,min(i+CHUNK-1,size-1)) for i in range(start,size,CHUNK)]
            print('resuming',step,name,start,'/',size,flush=True)
            paths=list(ex.map(fetch,jobs))
            digest=hashlib.sha256()
            if tmp.exists():
                with tmp.open('rb') as old:
                    while block:=old.read(8*1024*1024): digest.update(block)
            with tmp.open('ab') as out:
                for p in paths:
                    with p.open('rb') as f:
                        while block:=f.read(8*1024*1024):
                            digest.update(block); out.write(block)
            if digest.hexdigest()!=info['lfs']['sha256']: raise RuntimeError('Hash mismatch '+str(tmp))
            tmp.rename(dst)
            for p in paths: p.unlink()
            print('verified',dst,flush=True)
        (folder/'L29_DOWNLOAD_COMPLETE').write_text(sha+'\n')
        print('checkpoint ready',step,flush=True)
