"""Entire nine-run experience control audit; held branch outcomes are evaluation only."""
import gc
import json
import shutil
from pathlib import Path
import numpy as np
import torch
import experience_utilization as u


if __name__ == '__main__':
    torch.set_num_threads(4); records=[];arrays={}
    for seed in range(3):
        reference=u.ROOT/f'20261004-E20-joint-PLAIN-A100-s{seed}'
        base=json.loads((reference/'queries_u0.json').read_text())
        plain=json.loads((reference/'queries_u2000.json').read_text())
        arrays[('GROUPED-PLAIN',seed)]=np.array([r['success'] for r in plain],dtype=float)
        for arm in u.ARMS:
            name=f'20261005-E20-experience-{arm}-A100-s{seed}';run=u.ROOT/name
            assert json.loads((run/'complete.json').read_text())==dict(completed=True,arm=arm,seed=seed,updates=2000)
            assert not (run/'failure.json').exists()
            cfg=json.loads((run/'config.json').read_text());accounting=json.loads((run/'accounting.json').read_text())
            assert cfg['script_sha256']==u.e.digest(u.__file__) and cfg['loss_helper_sha256']==u.e.digest(u.e.__file__)
            assert cfg['source_checkpoint_sha256']==u.e.digest(u.SOURCES[seed])
            assert cfg['train_anchors']==list(range(32)) and cfg['query_anchors']==list(range(32,44))
            assert json.loads((run/'queries_u0.json').read_text())==base
            branch_items=64000 if arm=='IID-BRANCH' else 0 if arm=='REPLAY-ONLY' else 32000
            assert accounting['branch_items']==branch_items and accounting['replay_items']==64000-branch_items
            first=json.loads((run/'first_batch.json').read_text())
            assert set(first['branch_anchors'])<=set(range(32)) and 1 not in first['branch_ids']
            checkpoint=u.HF/name/'u2000.ckpt';summaries=json.loads((run/'summary.json').read_text())
            assert u.e.digest(checkpoint)==next(r['checkpoint_sha256'] for r in summaries if r['updates']==2000)
            c=torch.load(checkpoint,map_location='cpu',weights_only=False)
            assert c['steps']==2000 and len(c['state_dict'])==303 and len(c['optimizer']['state'])==297
            assert all(torch.isfinite(v).all() for v in c['state_dict'].values())
            assert all(int(v['step'])==2000 and torch.isfinite(v['exp_avg']).all() and torch.isfinite(v['exp_avg_sq']).all() for v in c['optimizer']['state'].values())
            assert c['rng']['branch']==accounting['final_branch_rng'] and c['rng']['replay']==accounting['final_replay_rng']
            data_cache=Path('/tmp/latent-wm-data/E16-base100-trainseed-cache')
            assert c['manifest']==json.loads((data_cache/'data_manifest.json').read_text())
            assert c['config']==json.loads((data_cache/'architecture.json').read_text())
            layout=json.loads((data_cache/'cache_manifest.json').read_text())['layout']
            for ix in first['replay_cache_starts']:
                assert any(ep['cache_row']<=ix and ix+35<ep['cache_row']+ep['frames'] for ep in layout)
            rows=json.loads((run/'queries_u2000.json').read_text())
            assert [r['anchor'] for r in rows]==list(range(32,44))
            for row,ref in zip(rows,plain):
                assert row['actual_distances']==ref['actual_distances'] and row['goal_candidate']==ref['goal_candidate']
                assert np.isfinite(row['predicted_scores']).all() and row['selected']==int(np.argmin(row['predicted_scores']))
                assert row['physical_distance']==row['actual_distances'][row['selected']]
                assert row['success']==(row['physical_distance']<16) and row['best_distance']==min(row['actual_distances'])==0
            assert sum(r['success'] for r in rows)==next(r['successes'] for r in summaries if r['updates']==2000)
            arrays[(arm,seed)]=np.array([r['success'] for r in rows],dtype=float)
            records.append(dict(arm=arm,source_seed=seed,successes=sum(r['success'] for r in rows),n=12,
                checkpoint_sha256=u.e.digest(checkpoint),configuration=cfg,accounting=accounting,rows=rows,artifact_directory=str(run)))
            del c;gc.collect();print('experience result audit',arm,seed,'PASS',flush=True)
    rng=np.random.default_rng(108500);si=rng.integers(0,3,(10000,3));ai=rng.integers(0,12,(10000,12));effects=[]
    for arm in u.ARMS:
        delta=np.stack([arrays[(arm,s)]-arrays[('GROUPED-PLAIN',s)] for s in range(3)])
        draws=delta[si[:,:,None],ai[:,None,:]].mean((1,2))
        effects.append(dict(arm=arm,comparison='GROUPED-PLAIN',mean_delta=float(delta.mean()),paired_source_anchor_bootstrap_95=np.quantile(draws,[.025,.975]).tolist(),source_deltas=delta.mean(1).tolist()))
    result=dict(completed=True,training_runs=9,records=records,effects=effects,
        original_grouped_plain_successes=[int(arrays[('GROUPED-PLAIN',s)].sum()) for s in range(3)],
        audit=dict(all_sources_and_initial_queries_match=True,all_optimizer_states_fresh2000=True,all_query_selections_and_success_recomputed=True,branch_replay_exposure_accounting_checked=True),
        scope='Whole nine-run held new-branch development; source episodes are WM-seen and original replay includes those episodes. Only three independent train sources, same12 physical queries; not36 independent tasks. Closed-loop/new-goal matrix still pending. These are mature experience-use controls, not novelty confirmation.')
    out=u.ROOT/'20261005-E20-experience-result-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'audit_used.py')
    u.e.dump(out/'result.json',result);u.e.dump(Path(__file__).resolve().parents[1]/'results/E20_20261005_experience_candidate_results.json',result)
