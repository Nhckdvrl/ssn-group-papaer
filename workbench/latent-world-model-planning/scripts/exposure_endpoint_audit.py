"""Check the locked exposure endpoint and paired original development ledger."""
import gc
import json
import shutil
from pathlib import Path
import h5py
import numpy as np
import torch
from lewm_pilot import digest,dump

ROOT=Path('/home/xiang/.cache/latent-wm-results')
if __name__=='__main__':
    torch.set_num_threads(4);run=ROOT/'20261004-E16-data-exposure-resume-RTX-s0'
    cfg=json.loads((run/'config.json').read_text());summary=json.loads((run/'summary.json').read_text())[0]
    assert json.loads((run/'complete.json').read_text())==dict(completed=True,snapshots=1,updates=56500,source_immutable=True)
    checkpoint=Path(summary['checkpoint']);assert digest(checkpoint)==summary['checkpoint_sha256']
    c=torch.load(checkpoint,map_location='cpu',weights_only=False)
    assert c['steps']==56500 and c['metadata']['epoch_fraction']==100 and len(c['manifest']['base_episodes'])==1000
    assert len(c['state_dict'])==303 and all(torch.isfinite(v).all() for v in c['state_dict'].values())
    assert len(c['optimizer']['state'])==297 and all(int(v['step'])==56500 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in c['optimizer']['state'].values())
    assert digest(cfg['checkpoint'])==summary['source_sha256'] and digest(cfg['resume_checkpoint'])==summary['resume_checkpoint_sha256']
    with h5py.File(cfg['dataset']) as f:lengths=f['ep_len'][:]
    starts=[];offset=0
    for ep in sorted(c['manifest']['base_episodes']):
        n=int(lengths[ep]);starts.extend(range(offset,offset+n-20));offset+=n
    assert len(starts)==72359
    rng=np.random.default_rng(33000)
    for _ in range(100):rng.permutation(starts)
    assert rng.bit_generator.state==c['numpy_rng']
    rows=json.loads((run/'u56500_evaluation.json').read_text());anchors=np.load(run/'eval_anchors.npz')
    assert len(rows)==48 and [r['anchor'] for r in rows]==list(range(48))
    assert [r['source_episode'] for r in rows]==anchors['episode'].tolist()
    assert sum(r['success'] for r in rows)==summary['successes']==39
    assert not set(anchors['episode'].tolist())&set(c['manifest']['base_episodes'])
    for r in rows:assert 0<=r['env_steps']<=50 and all(np.isfinite(r['planning_seconds']))
    original=ROOT/'20261002-E16-data-compute-RTX-s0';prior=ROOT/'20261003-E16-data-exposure-RTX-s0'
    refs={'BASE1000-u5650':original/'BASE1000/u5650_evaluation.json',
          'BASE1000-u16950':prior/'u16950_evaluation.json',
          'BASE100-u5650':original/'BASE100/u5650_evaluation.json',
          'RELEASED':original/'released_evaluation.json'}
    effects=[];prng=np.random.default_rng(109700);indices=prng.integers(0,48,(10000,48))
    for name,path in refs.items():
        other=json.loads(path.read_text());assert [r['source_episode'] for r in other]==[r['source_episode'] for r in rows]
        delta=np.array([int(a['success'])-int(b['success']) for a,b in zip(rows,other)])
        effects.append(dict(reference=name,reference_successes=sum(r['success'] for r in other),mean_delta=float(delta.mean()),paired_episode_bootstrap_95=np.quantile(delta[indices].mean(1),[.025,.975]).tolist()))
    result=dict(completed=True,summary=summary,config=cfg,rows=rows,effects=effects,
        audit=dict(checkpoint_and_sources_hash_match=True,all_297_optimizer_states_56500_finite=True,sampler_100_epochs_regenerated_exact=True,all_48_ledger_counts_rechecked=True),
        scope='Single source original48 development, approximate equal epochs versus100-data and10x updates; not equal compute, data-only causality, or stable equivalence. Original evaluator did not retain full physical traces; this independently audits counts/accounting, not actual success events.',artifact_directory=str(run))
    out=ROOT/'20261005-E16-exposure-endpoint-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py');dump(out/'result.json',result)
    dump(Path(__file__).resolve().parents[1]/'results/E16_20261005_exposure_endpoint.json',result);print('exposure endpoint audit PASS 39/48',flush=True)
