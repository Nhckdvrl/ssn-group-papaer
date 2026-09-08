"""Read pinned cached weights sequentially to reduce shared-filesystem mmap stalls.

No downloaded/copied/modified weights; only OS page cache is warmed. Four readers
bound shared-storage load. This does not affect prompts or model arithmetic.
"""
import concurrent.futures, itertools, json, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):
    t=time.monotonic();n=0
    with p.open('rb') as f:
        while data:=f.read(16*1024*1024):n+=len(data)
    return {'path':str(p),'bytes':n,'seconds':time.monotonic()-t}
if __name__=='__main__':
    proto=json.loads((ROOT/'experiments/E001a_interpretation/protocol.json').read_text())
    models=[sorted(Path(s['path']).glob('*.safetensors')) for s in proto['models'].values()]
    paths=[p for row in itertools.zip_longest(*models) for p in row if p is not None]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for r in pool.map(read,paths):print(json.dumps(r),flush=True)
