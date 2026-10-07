"""E92 complete unchanged-interpretation reward contrast on paired observations."""
import argparse
import collections
import json
from pathlib import Path
import time
import numpy as np
from data import sha
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate


def correlation(rows, x, y):
    groups = collections.defaultdict(list)
    for r, a, b in zip(rows, x, y):
        groups[r['cluster_id']].append((a, b))
    pairs = np.array([np.mean(v, axis=0) for _, v in sorted(groups.items())])
    if not len(pairs):
        return dict(value=None, CI95=[None, None], clusters=0, sources=0, valid_bootstrap=0)
    def calculate(p):
        a, b = p[..., 0], p[..., 1]
        a, b = a-a.mean(axis=-1, keepdims=True), b-b.mean(axis=-1, keepdims=True)
        den = np.sqrt((a*a).sum(-1)*(b*b).sum(-1))
        return np.divide((a*b).sum(-1), den, out=np.full_like(den, np.nan), where=den > 1e-12)
    point = float(calculate(pairs))
    idx = np.random.default_rng(92).integers(0, len(pairs), size=(10000, len(pairs)))
    values = calculate(pairs[idx])
    values = values[np.isfinite(values)]
    return dict(value=point if np.isfinite(point) else None,
                CI95=np.quantile(values, [.025, .975]).tolist() if len(values) else [None, None],
                clusters=len(pairs), sources=len(rows), valid_bootstrap=len(values))


def analyze(root):
    rows = [json.loads(s) for s in (root/'data-v1.jsonl').read_text().splitlines()]
    meta = {r['item_id']: r for r in rows}
    all_scores = {}
    provenance = []
    for version, path in [('original', root.parent/'E91'), ('alternate', root)]:
        scores = {}
        for run in json.loads((path/'runner-pids-v1.json').read_text()):
            p = Path(run['out'])
            cfg = json.loads((p/'config.json').read_text())
            assert cfg['predictions_sha256'] == sha(p/'predictions.jsonl')
            assert cfg['data_sha256'] == sha(path/'data-v1.jsonl')
            assert cfg['model_manifest_sha256'] == sha(root.parent/'models'/run['model']/'manifest.json')
            ps = [json.loads(s) for s in (p/'predictions.jsonl').read_text().splitlines()]
            assert len(ps) == cfg['tasks']
            for x in ps:
                if x['item_id'] not in meta:
                    assert version == 'original'
                    continue
                key = run['model'], x['item_id']
                assert key not in scores
                scores[key] = x
            if version == 'alternate':
                provenance.append(dict(model=run['model'], shard=run['shard'], config_sha256=sha(p/'config.json'),
                                       predictions_sha256=cfg['predictions_sha256'], gpu_hours=cfg['gpu_hours']))
        assert len(scores) == len(rows)*3
        all_scores[version] = scores
    groups = collections.defaultdict(dict)
    for r in rows:
        groups[r['generator'], r['source_unit']][r['operation']] = r
    assert len(groups) == 300
    records = []
    for grader in MODELS:
        for (generator, uid), g in sorted(groups.items()):
            b, t = g['BASE_BANK'], g['TARGET_BANK']
            rec = dict(grader=grader, generator=generator, source_unit=uid,
                       sentence_sha256=b['original_sentence_sha256'], cluster_id=b['cluster_id'],
                       construction=b['construction'], condition=b['condition'],
                       original_sentence=b['original_sentence'], alternate_sentence=b['sentence'])
            for version in ['original', 'alternate']:
                pb, pt = [all_scores[version][grader, r['item_id']] for r in [b, t]]
                assert pb['observation_tokens'] == pt['observation_tokens']
                rec[version+'_observation_tokens'] = pb['observation_tokens']
                rec['delta_reward_mean_'+version] = pt['reward_mean']-pb['reward_mean']
                rec['delta_reward_sum_'+version] = pt['reward_sum']-pb['reward_sum']
                def clip(x):
                    return max(min(x, -.9), -5)
                rec['delta_code_clipped_mean_'+version] = clip(pt['reward_mean'])-clip(pb['reward_mean'])
                if version == 'alternate':
                    for r, x in [(b, pb), (t, pt)]:
                        assert x['context_sha256'] == all_scores['original'][grader, r['item_id']]['context_sha256']
            rec['surface_interaction_mean'] = rec['delta_reward_mean_alternate']-rec['delta_reward_mean_original']
            for key in ['positive_retention', 'unsupported_assertion', 'semantic_fidelity',
                        'positive_omission', 'positive_contradiction']:
                rec['delta_'+key] = None if b[key] is None or t[key] is None else t[key]-b[key]
            records.append(rec)
    panels = []
    for grader in MODELS:
        for generator in sorted({r['generator'] for r in rows}):
            for ct in ['NPZ', 'MVRR', 'NPS', 'ALL']:
                for cond in ['gp', 'control']:
                    rs = [r for r in records if r['grader'] == grader and r['generator'] == generator
                          and (ct == 'ALL' or r['construction'] == ct) and r['condition'] == cond]
                    if not rs:
                        continue
                    metrics = {key: estimate(rs, [r[key] for r in rs], seed=92)
                               for key in ['delta_reward_mean_original', 'delta_reward_mean_alternate',
                                           'delta_reward_sum_original', 'delta_reward_sum_alternate', 'surface_interaction_mean']}
                    cors = {}
                    counts = dict(sources=len(rs), raw_original_ties=sum(abs(r['delta_reward_mean_original']) < 1e-12 for r in rs),
                                  raw_alternate_ties=sum(abs(r['delta_reward_mean_alternate']) < 1e-12 for r in rs),
                                  code_original_ties=sum(abs(r['delta_code_clipped_mean_original']) < 1e-12 for r in rs),
                                  code_alternate_ties=sum(abs(r['delta_code_clipped_mean_alternate']) < 1e-12 for r in rs))
                    for key, direction in [('semantic_fidelity', 1), ('positive_retention', 1), ('unsupported_assertion', -1)]:
                        sub = [r for r in rs if r['delta_'+key] is not None]
                        y = [direction*r['delta_'+key] for r in sub]
                        metrics['delta_'+key] = estimate(sub, [r['delta_'+key] for r in sub], seed=92)
                        align = {}
                        for version in ['original', 'alternate']:
                            x = [r['delta_reward_mean_'+version] for r in sub]
                            cors[version+'_vs_'+key] = correlation(sub, x, y)
                            align[version] = [float(np.sign(a)*np.sign(b)) for a, b in zip(x, y)]
                            metrics[version+'_alignment_'+key] = estimate(sub, align[version], seed=92)
                            counts[version+'_'+key+'_agree'] = sum(a*b > 1e-12 for a, b in zip(x, y))
                            counts[version+'_'+key+'_oppose'] = sum(a*b < -1e-12 for a, b in zip(x, y))
                        metrics['alignment_change_'+key] = estimate(sub, [b-a for a, b in zip(align['original'], align['alternate'])], seed=92)
                        counts[key+'_changed'] = sum(abs(v) > 1e-12 for v in y)
                    panels.append(dict(grader=grader, generator=generator, construction=ct, condition=cond,
                                       metrics=metrics, correlations=cors, counts=counts))
    out = root/'observation-surface-reward-map-v1.json'
    assert not out.exists()
    out.write_text(json.dumps(dict(panels=panels, matched_records=records, runs=provenance,
                                   data_sha256=sha(root/'data-v1.jsonl'), statistics='Input common-Q same-Gold scope, all models/conditions. Source then lexical cluster; 10000 paired bootstrap seed92; mean-token LP interaction is primary, sum retained.',
                                   limits='Published cue/GP pairing preserves only registered common-Q support, not certified complete semantic identity. Fixed untrained raw reconstruction analogue, not RL-trained ABBEL replication.'), indent=2)+'\n')
    m = dict(map_sha256=sha(out), gpu_hours=sum(r['gpu_hours'] for r in provenance), new_scores=len(rows)*3,
             new_api_calls=0, panels=len(panels), matched_pairs=len(records))
    (root/'complete-map-v1.json').write_text(json.dumps(m, indent=2)+'\n')
    print('E92 COMPLETE', m, flush=True)


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
