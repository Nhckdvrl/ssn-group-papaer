"""E00 node-local HDF5 decoding throughput; no GPU or global cache eviction."""
import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import time
import h5py
import hdf5plugin
import numpy as np


def worker(path,seed,barrier,q):
    try:
        rng=np.random.default_rng(seed)
        with h5py.File(path) as f:
            lengths,offsets=f['ep_len'][:],f['ep_offset'][:]
            eligible=np.flatnonzero(lengths>20)
            def read(count):
                ep=rng.choice(eligible,count);starts=offsets[ep]+np.asarray([rng.integers(0,int(lengths[e])-20) for e in ep])
                rows=np.unique((starts[:,None]+np.array([0,5,10,15])).ravel())
                x=f['pixels'][rows]
                return x.nbytes,len(x),int(x[:,0,0,0].astype('int64').sum())
            read(4);barrier.wait(timeout=60);begin=time.perf_counter()
            batches=[];nbytes=0;frames=0;checksum=0
            for _ in range(8):
                t=time.perf_counter();b,n,c=read(16);batches.append(time.perf_counter()-t)
                nbytes+=b;frames+=n;checksum+=c
            q.put({'seed':seed,'seconds':time.perf_counter()-begin,'bytes':nbytes,'frames':frames,
                   'batch_seconds':batches,'checksum':checksum})
    except Exception as e:q.put({'error':type(e).__name__,'message':str(e)})


def run(args):
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    ctx=mp.get_context('fork');results=[]
    for path in args.datasets:
        for repeat,order in enumerate([[1,2,4],[4,2,1]]):
            for n in order:
                barrier=ctx.Barrier(n);q=ctx.Queue()
                jobs=[ctx.Process(target=worker,args=(path,60000+repeat*100+i,barrier,q)) for i in range(n)]
                for job in jobs:job.start()
                rows=[q.get(timeout=120) for _ in jobs]
                for job in jobs:job.join(timeout=60)
                if any('error' in r for r in rows):raise RuntimeError(rows)
                elapsed=max(r['seconds'] for r in rows)
                result={'file':Path(path).name,'repeat':repeat,'workers':n,'rows':rows,
                        'aggregate_frames_per_second':sum(r['frames'] for r in rows)/elapsed,
                        'decoded_mb_per_second':sum(r['bytes'] for r in rows)/elapsed/1e6}
                results.append(result);(out/'rows.json').write_text(json.dumps(results,indent=2)+'\n')
                print(Path(path).name,'repeat',repeat,'workers',n,'frames/s',result['aggregate_frames_per_second'],flush=True)
    metadata={'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'cache_condition':'warmup + uncontrolled OS page cache; node-local HDF5; no cache drop',
              'ambient':'other independent GPU/CPU work active; not a 4-GPU training benchmark'}
    (out/'complete.json').write_text(json.dumps(metadata,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--datasets',nargs='+',required=True);p.add_argument('--output',required=True)
    run(p.parse_args())
