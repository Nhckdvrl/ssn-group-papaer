"""POST-HOC same-function context effects from sealed E150/E151 text data."""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()


def read(experiment):
    p=ROOT/f'results/{experiment}/manifest.json';m=json.loads(p.read_text())
    if m['status']!='complete' or sha(m['raw']['path'])!=m['raw']['sha256']:raise ValueError('Unsealed raw')
    with np.load(m['raw']['path'],allow_pickle=False) as f:a={k:f[k].copy() for k in f.files}
    return a,m,{'manifest':{'path':str(p),'sha256':sha(p)},'raw':m['raw']}


def mean(v,mask):
    if v.shape!=(64,512) or mask.shape!=v.shape or np.any(mask.sum(-1)==0):raise ValueError('Invalid NLL/mask dimensions')
    return np.where(mask,v.astype(np.float64),0).sum(-1)/mask.sum(-1)


def stats(v,rows):
    labels=list(dict.fromkeys((r['source'],r['file_id']) for r in rows))
    groups=[np.array([i for i,r in enumerate(rows) if (r['source'],r['file_id'])==key]) for key in labels]
    sums=np.array([v[g].sum() for g in groups]);counts=np.array([len(g) for g in groups])
    draws=np.random.default_rng(159002).integers(0,len(groups),(1000,len(groups)))
    boot=sums[draws].sum(-1)/counts[draws].sum(-1)
    return {'point':float(v.mean()),'input_file_ci95':np.quantile(boot,[.025,.975]).tolist(),
            'file_clusters':len(groups),'sequences':len(v),'bootstrap_seed':159002}


def main():
    cube,mc,pc=read('e150');zero,mz,pz=read('e151')
    plan=json.loads((ROOT/'results/e150/plan.json').read_text())
    if mc['source_parameter_hashes']!=mz['parameter_hashes'] or mc['source_buffer_hashes']!=mz['buffer_hashes']:
        raise ValueError('Unchanged source function bytes differ')
    if not np.array_equal(cube['valid'],zero['valid']) or not np.array_equal(cube['suffix_valid'],zero['suffix_valid']):
        raise ValueError('Input masks differ')
    if list(cube['fields'])!=list(zero['fields']) or str(cube['fields'][0])!='nll':raise ValueError('Metric axis differs')
    if not np.array_equal(cube['metrics'][...,0,0],cube['metrics'][...,1,0]):raise ValueError('Reference-dependent NLL')
    cases={tuple(int(v) for v in case):i for i,case in enumerate(cube['cases'])}
    if len(cases)!=16:raise ValueError('Incomplete full cube')
    mask=cube['valid'];native=[]
    for b in (0,1):
        old=cube['metrics'][cases[(b,b,b,b)],:,:,0,0];now=zero['metrics'][b,0,:,:,0]
        if not np.array_equal(old[mask],now[mask]):raise ValueError('Native held token replay differs')
        native.append(mean(now,mask))
    rows=plan['selected'];labels={(r['source'],r['file_id']) for r in rows}
    if len(rows)!=64 or len(labels)!=20:raise ValueError('Input unit differs')
    out={'status':'complete_POST_HOC_inherited_only','source_sha256':sha(__file__), 'inputs':{'E150':pc,'E151':pz},
         'new_model_forwards':0,'unit':'equal real-target token means within 64 windows; paired bootstrap of20 input files',
         'real_targets':int(mask.sum()),'scope':'Same source R or S functions in native versus other-source D/G/other-branch background. Does not isolate routed partner from dense/router.',
         'identity':'Removing the transplanted branch leaves the already-measured native zero-branch background; inherited endpoint, not a new forward.',
         'controls':{'parameters_and_buffers_match':True,'native_token_replay_exact':True,'input_masks_same':True},'branches':{}}
    for branch,axis,zero_condition in (('shared',3,2),('routed',2,1)):
        branch_rows={}
        by_background={}
        for b in (0,1):
            values=[]
            for f in (0,1):
                case=[b]*4;case[axis]=f
                full=mean(cube['metrics'][cases[tuple(case)],:,:,0,0],mask)
                removed=mean(zero['metrics'][b,zero_condition,:,:,0],mask)
                values.append(removed-full)
                branch_rows['background_'+'AB'[b]+'_function_'+'AB'[f]]={
                    'full_NLL':stats(full,rows),'removed_NLL_inherited':stats(removed,rows),'removal_delta_NLL':stats(removed-full,rows)}
            by_background[b]=values
        for f in (0,1):
            branch_rows['same_function_'+'AB'[f]+'_background_B_minus_A']=stats(by_background[1][f]-by_background[0][f],rows)
        branch_rows['mean_background_B_minus_A']=stats(np.mean(by_background[1],axis=0)-np.mean(by_background[0],axis=0),rows)
        out['branches'][branch]=branch_rows
    target=ROOT/'results/e159/known_lm_border_posthoc.json'
    target.write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    for branch,rows in out['branches'].items():
        print(branch,{k:v for k,v in rows.items() if 'background_B_minus_A' in k})


if __name__=='__main__':main()
