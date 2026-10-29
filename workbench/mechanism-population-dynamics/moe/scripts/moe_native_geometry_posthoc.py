"""POST-HOC description of already completed E163 native geometry; no new tests."""
import hashlib
import json
from pathlib import Path

import numpy as np

MOE=Path(__file__).resolve().parents[1]


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    path=MOE/'results/e163/manifest.json';manifest=json.loads(path.read_text())
    assert manifest['status']=='complete'
    out={'kind':'POST-HOC descriptive reanalysis; no new model forward, hypothesis test or evidence upgrade',
         'source_manifest_sha256':sha(path),'models':{},
         'aggregation':'Equal mean of16 stored native LM batches; R/S RMS ratio is not a causal contribution share.',
         'unobserved':'Aggregate lacks token positions and does not compare foreign functions on identical inputs. No outlier mechanism or scalar-gain sufficiency inferred.'}
    for label in ('P','A','B','F'):
        item=manifest['raw'][label];assert sha(item['path'])==item['sha256']
        with np.load(item['path'],allow_pickle=False) as z:x=z['native_LM_geometry'].astype(float)
        assert x.shape==(16,3,16,3)
        g=x.mean(0);r=np.sqrt(g[0,:,0]);s=np.sqrt(g[1,:,0])
        out['models'][label]={'raw':item,'stored_shape':list(x.shape),
                              'R_RMS_by_layer':r.tolist(),'S_RMS_by_layer':s.tolist(),
                              'R_to_S_RMS_by_layer':(r/s).tolist(),
                              'median_R_to_S_RMS':float(np.median(r/s))}
    out['source_code_sha256']=sha(__file__)
    target=MOE/'paper/native_geometry_posthoc.json'
    target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':'complete','path':str(target),'new_GPU_work':0}))


if __name__=='__main__':main()
