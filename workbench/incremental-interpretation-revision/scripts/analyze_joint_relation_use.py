"""Complete E72 shards, canonicalize question order, report the entire paired map."""
import argparse
import collections
import json
from pathlib import Path
import time

import numpy as np
from data import sha
from joint_relation_use import MODELS, METRICS


def measurements(probabilities, best, gold):
    i, f = [0 if x == 'Yes' else 1 for x in gold]
    return dict(joint_correct=float(best == 2*i+f), p_joint_correct=probabilities[2*i+f],
        initial_correct=float(best//2 == i), initial_p_correct=sum(probabilities[2*i:2*i+2]),
        final_correct=float(best%2 == f), final_p_correct=probabilities[f]+probabilities[f+2])


def estimate(rows, values):
    sources = collections.defaultdict(list)
    for r, v in zip(rows, values): sources[(r['cluster_id'], r['sentence_sha256'])].append(float(v))
    clusters = collections.defaultdict(list)
    for (c, s), vs in sources.items(): clusters[c].append(float(np.mean(vs)))
    x = np.array([np.mean(clusters[c]) for c in sorted(clusters)])
    if not len(x): return dict(value=None, CI95=None, clusters=0, sources=0)
    rng = np.random.default_rng(72)
    boot = x[rng.integers(len(x), size=(10000, len(x)))].mean(-1)
    return dict(value=float(x.mean()), CI95=list(map(float, np.quantile(boot, [.025, .975]))),
        clusters=len(x), sources=len(sources))


def analyze(root, run_manifest):
    path = root/'data-v1.jsonl'; rows = [json.loads(s) for s in path.read_text().splitlines()]
    ids = {r['item_id'] for r in rows}
    assert len(ids) == len(rows)
    expected = {(uid, op, order) for uid in ids for op in ['JOINT', 'SEPARATE'] for order in [0, 1]}
    panels = []; provenance = []; order_noise = []
    for model in MODELS:
        all_predictions = []; records = [x for x in run_manifest if x['model'] == model]
        shards = records[0]['shards']
        assert {x['shard'] for x in records} == set(range(shards))
        for run in records:
            directory = Path(run['out']); cfg = json.loads((directory/'config.json').read_text())
            assert cfg['data_sha256'] == sha(path) and cfg['predictions_sha256'] == sha(directory/'predictions.jsonl')
            part = [json.loads(s) for s in (directory/'predictions.jsonl').read_text().splitlines()]
            input_ids = {r['item_id'] for r in rows if int(r['sentence_sha256'][:16], 16) % shards == run['shard']}
            assert len(part) == cfg['tasks'] == 4*len(input_ids)
            assert {p['item_id'] for p in part} == input_ids
            all_predictions.extend(part)
            provenance.append(dict(model=model, shard=run['shard'], config_sha256=sha(directory/'config.json'),
                predictions_sha256=cfg['predictions_sha256'], gpu_hours=cfg['gpu_hours']))
        index = {(p['item_id'], p['operation'], p['order']): p for p in all_predictions}
        assert len(index) == len(all_predictions) == len(expected) and set(index) == expected
        outcomes = {}; ordered = {}
        for r in rows:
            uid = r['item_id']; p0 = index[uid, 'SEPARATE', 0]['probabilities']; p1 = index[uid, 'SEPARATE', 1]['probabilities']
            assert len(p0) == len(p1) == 2
            separate = [a*b for a in p0 for b in p1]
            best = 2*max(range(2), key=p0.__getitem__)+max(range(2), key=p1.__getitem__)
            outcomes[uid, 'SEPARATE'] = measurements(separate, best, r['gold'])
            joint = []
            for order in [0, 1]:
                raw = index[uid, 'JOINT', order]['probabilities']; assert len(raw) == 4 and abs(sum(raw)-1) < 1e-6
                best_raw = max(range(4), key=raw.__getitem__)
                canonical = raw if order == 0 else [raw[0], raw[2], raw[1], raw[3]]
                best = best_raw if order == 0 else 2*(best_raw%2)+best_raw//2
                joint.append(measurements(canonical, best, r['gold']))
            ordered[uid] = joint
            outcomes[uid, 'JOINT'] = {m: float(np.mean([x[m] for x in joint])) for m in METRICS}
        for construct in ['MVRR', 'NPZ', 'NPS', 'NPVP']:
            for pattern in ['all', 'Yes/Yes', 'Yes/No', 'No/Yes', 'No/No']:
                cell = {}
                for condition in ['gp', 'control']:
                    selected = [r for r in rows if r['construction'] == construct and r['condition'] == condition
                                and (pattern == 'all' or '/'.join(r['gold']) == pattern)]
                    for metric in METRICS:
                        for operation in ['SEPARATE', 'JOINT', 'JOINT-minus-SEPARATE']:
                            values = [(outcomes[r['item_id'], 'JOINT'][metric]-outcomes[r['item_id'], 'SEPARATE'][metric])
                                      if operation == 'JOINT-minus-SEPARATE' else outcomes[r['item_id'], operation][metric] for r in selected]
                            panels.append(dict(model=model, construction=construct, condition=condition, pattern=pattern,
                                metric=metric, operation=operation, **estimate(selected, values)))
                        cell[condition, metric] = (selected, [outcomes[r['item_id'], 'JOINT'][metric]-outcomes[r['item_id'], 'SEPARATE'][metric] for r in selected])
                    if pattern == 'all':
                        order_noise.append(dict(model=model, construction=construct, condition=condition, sources=len(selected),
                            mean_absolute_order_difference={m: float(np.mean([abs(ordered[r['item_id']][0][m]-ordered[r['item_id']][1][m]) for r in selected])) if selected else None for m in METRICS}))
                for metric in METRICS:
                    # Exact paired source contrast before lexical-cluster aggregation.
                    paired = collections.defaultdict(dict)
                    for condition in ['gp', 'control']:
                        selected, vs = cell[condition, metric]
                        for r, v in zip(selected, vs): paired[r['pair_id']][condition] = r, v
                    selected = []; values = []
                    for pid, g in sorted(paired.items()):
                        assert set(g) == {'gp', 'control'}
                        selected.append(g['gp'][0]); values.append(g['gp'][1]-g['control'][1])
                    panels.append(dict(model=model, construction=construct, condition='gp-minus-cue', pattern=pattern,
                        metric=metric, operation='interaction', **estimate(selected, values)))
    assert len(panels) == 2520
    report = dict(data_sha256=sha(path), input_manifest=json.loads(path.with_suffix('.manifest.json').read_text()),
        runs=provenance, panels=panels, order_noise=order_noise,
        statistics='Question-order average, same-source mean, lexical-cluster paired bootstrap 10000 seed72',
        limits='Original source support answer-vector choice. Joint format changes consumer task; no latent full-parse or free-generation ability certification.')
    output = root/'joint-relation-use-map-v1.json'; assert not output.exists()
    output.write_text(json.dumps(report, indent=2)+'\n')
    (root/'complete-map-v1.json').write_text(json.dumps(dict(map_sha256=sha(output), all_models_complete=True,
        shards=len(run_manifest), panels=len(panels), gpu_hours=sum(p['gpu_hours'] for p in provenance)), indent=2)+'\n')
    print('E72 complete', len(panels), sha(output), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--root', type=Path, required=True); parser.add_argument('--wait', action='store_true')
    args = parser.parse_args(); runs = json.loads((args.root/'runner-pids-v1.json').read_text())
    while args.wait:
        ready = []
        for r in runs:
            p = Path(r['out'])/'config.json'
            ready.append(p.exists() and 'predictions_sha256' in json.loads(p.read_text()))
        if all(ready): break
        time.sleep(20)
    analyze(args.root, runs)
