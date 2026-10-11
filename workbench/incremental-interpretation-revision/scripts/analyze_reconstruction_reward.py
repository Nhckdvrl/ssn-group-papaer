"""E91 complete matched reward/semantic deltas; all frozen source strata retained."""
import argparse
import collections
import json
from pathlib import Path
import time
import numpy as np
from data import sha
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate


def corr_ci(rows, x, y):
    groups = collections.defaultdict(list)
    for r, a, b in zip(rows, x, y):
        groups[r['cluster_id']].append((a, b))
    pairs = np.array([np.mean(v, axis=0) for _, v in sorted(groups.items())])
    def corr(p):
        a, b = p[..., 0], p[..., 1]
        a = a-a.mean(axis=-1, keepdims=True)
        b = b-b.mean(axis=-1, keepdims=True)
        den = np.sqrt((a*a).sum(axis=-1)*(b*b).sum(axis=-1))
        return np.divide((a*b).sum(axis=-1), den,
                         out=np.full_like(den, np.nan), where=den > 1e-12)
    if not len(pairs):
        return dict(value=None, CI95=[None, None], clusters=0, sources=0, valid_bootstrap=0)
    point = float(corr(pairs))
    rng = np.random.default_rng(91)
    idx = rng.integers(0, len(pairs), size=(10000, len(pairs)))
    values = corr(pairs[idx])
    valid = values[np.isfinite(values)]
    return dict(value=point if np.isfinite(point) else None,
                CI95=np.quantile(valid, [.025, .975]).tolist() if len(valid) else [None, None],
                clusters=len(pairs), sources=len(rows), valid_bootstrap=len(valid))


def analyze(root):
    rows = [json.loads(s) for s in (root/'data-v1.jsonl').read_text().splitlines()]
    meta = {r['item_id']: r for r in rows}
    index = {}
    provenance = []
    runs = json.loads((root/'runner-pids-v1.json').read_text())
    for run in runs:
        p = Path(run['out'])
        cfg = json.loads((p/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(p/'predictions.jsonl')
        assert cfg['data_sha256'] == sha(root/'data-v1.jsonl')
        assert cfg['model_manifest_sha256'] == sha(root.parent/'models'/run['model']/'manifest.json')
        ps = [json.loads(s) for s in (p/'predictions.jsonl').read_text().splitlines()]
        assert len(ps) == cfg['tasks']
        for x in ps:
            r = meta[x['item_id']]
            assert x['operation'] == r['operation'] and x['generator'] == r['generator']
            assert int(r['sentence_sha256'][:16], 16) % run['shards'] == run['shard']
            key = run['model'], x['item_id']
            assert key not in index
            assert abs(sum(x['token_logprobs'])-x['reward_sum']) < 1e-8
            index[key] = x
        provenance.append(dict(model=run['model'], shard=run['shard'],
                               config_sha256=sha(p/'config.json'), predictions_sha256=cfg['predictions_sha256'],
                               gpu_hours=cfg['gpu_hours'], code_sha256=cfg['code_sha256']))
    assert len(index) == len(rows)*3
    groups = collections.defaultdict(dict)
    for r in rows:
        groups[r['generator'], r['source_unit']][r['operation']] = r
    assert len(groups) == 324
    records = []
    for grader in MODELS:
        for (generator, uid), g in sorted(groups.items()):
            b, t = g['BASE_BANK'], g['TARGET_BANK']
            pb, pt = index[grader, b['item_id']], index[grader, t['item_id']]
            assert b['sentence'] == t['sentence']
            assert pb['observation_tokens'] == pt['observation_tokens']
            r = dict(grader=grader, generator=generator, source_unit=uid,
                     cluster_id=b['cluster_id'], sentence_sha256=b['sentence_sha256'],
                     construction=b['construction'], condition=b['condition'],
                     base_item_id=b['item_id'], target_item_id=t['item_id'],
                     base_reward_sum=pb['reward_sum'], target_reward_sum=pt['reward_sum'],
                     base_reward_mean=pb['reward_mean'], target_reward_mean=pt['reward_mean'],
                     base_interpretation_tokens=pb['interpretation_tokens'], target_interpretation_tokens=pt['interpretation_tokens'],
                     identical_interpretation=b['interpretation'] == t['interpretation'],
                     clipped_tie=pb['reward_clipped'] == pt['reward_clipped'])
            for key in ['reward_sum', 'reward_mean', 'reward_clipped']:
                r['delta_'+key] = pt[key]-pb[key]
            for key in ['positive_retention', 'unsupported_assertion', 'semantic_fidelity',
                        'positive_omission', 'positive_contradiction']:
                r['delta_'+key] = None if b[key] is None or t[key] is None else t[key]-b[key]
            records.append(r)
    panels = []
    for grader in MODELS:
        for generator in sorted({r['generator'] for r in rows}):
            for ct in ['NPZ', 'MVRR', 'NPS', 'ALL']:
                for cond in ['gp', 'control']:
                    rs = [r for r in records if r['grader'] == grader and r['generator'] == generator
                          and (ct == 'ALL' or r['construction'] == ct) and r['condition'] == cond]
                    if not rs:
                        continue
                    metrics = {}
                    for key in ['reward_sum', 'reward_mean', 'reward_clipped', 'positive_retention',
                                'unsupported_assertion', 'semantic_fidelity', 'positive_omission', 'positive_contradiction']:
                        sub = [r for r in rs if r['delta_'+key] is not None]
                        metrics['delta_'+key] = estimate(sub, [r['delta_'+key] for r in sub], seed=91)
                    correlations = {}
                    counts = dict(sources=len(rs), identical_interpretations=sum(r['identical_interpretation'] for r in rs),
                                  raw_reward_ties=sum(abs(r['delta_reward_sum']) < 1e-12 for r in rs),
                                  clipped_reward_ties=sum(r['clipped_tie'] for r in rs))
                    for key, direction in [('semantic_fidelity', 1), ('positive_retention', 1), ('unsupported_assertion', -1)]:
                        sub = [r for r in rs if r['delta_'+key] is not None]
                        for score in ['reward_sum', 'reward_clipped']:
                            x = [r['delta_'+score] for r in sub]
                            y = [direction*r['delta_'+key] for r in sub]
                            correlations[score+'_vs_'+key] = corr_ci(sub, x, y)
                            agreement = [float(np.sign(a)*np.sign(b)) for a, b in zip(x, y)]
                            metrics[score+'_alignment_'+key] = estimate(sub, agreement, seed=91)
                        counts[key+'_changed'] = sum(abs(r['delta_'+key]) > 1e-12 for r in sub)
                        counts[key+'_reward_agrees'] = sum(r['delta_reward_sum']*direction*r['delta_'+key] > 1e-12 for r in sub)
                        counts[key+'_reward_opposes'] = sum(r['delta_reward_sum']*direction*r['delta_'+key] < -1e-12 for r in sub)
                    panels.append(dict(grader=grader, generator=generator, construction=ct, condition=cond,
                                       metrics=metrics, correlations=correlations, counts=counts))
    out = root/'reconstruction-reward-map-v1.json'
    assert not out.exists()
    out.write_text(json.dumps(dict(panels=panels, matched_records=records, runs=provenance,
                                   data_sha256=sha(root/'data-v1.jsonl'), statistics='Source means then frozen lexical cluster; 10000 bootstrap seed91. Correlations over cluster-mean paired deltas, no outcome-selected primary cohort.',
                                   limits='Frozen raw observation-reconstruction analogue, not ABBEL trained trajectory evaluation. Source support is measured only on original registered atoms. Clipped sum follows paper Algorithm4 wording; code equivalence not assumed.'), indent=2)+'\n')
    result = dict(map_sha256=sha(out), gpu_hours=sum(r['gpu_hours'] for r in provenance),
                  new_scores=len(index), new_api_calls=0, panels=len(panels), matched_pairs=len(records))
    (root/'complete-map-v1.json').write_text(json.dumps(result, indent=2)+'\n')
    print('E91 COMPLETE', result, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--wait', action='store_true')
    a = p.parse_args()
    if a.wait:
        while True:
            runs = json.loads((a.root/'runner-pids-v1.json').read_text())
            if all((Path(r['out'])/'config.json').exists() and 'predictions_sha256' in json.loads((Path(r['out'])/'config.json').read_text()) for r in runs):
                break
            time.sleep(10)
    analyze(a.root)
