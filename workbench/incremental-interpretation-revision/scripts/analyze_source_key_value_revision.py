"""E84 complete-only K/V map, retaining the parent hierarchical Source estimator."""
import argparse
import collections
import json
from pathlib import Path
from data import sha
from model_identity import manifest_identity
from analyze_source_bank_routes import summarize

OPS = ['BASE_BANK', 'TARGET_BANK', 'KEY_ONLY', 'VALUE_ONLY']
CONTRASTS = [('TARGET_BANK', 'BASE_BANK'), ('KEY_ONLY', 'BASE_BANK'),
             ('VALUE_ONLY', 'BASE_BANK'), ('KEY_ONLY', 'VALUE_ONLY'),
             ('KEY_ONLY', 'TARGET_BANK'), ('VALUE_ONLY', 'TARGET_BANK')]
MODELS = ['Qwen3-8B', 'gemma-3-12b-it', 'Meta-Llama-3.1-8B-Instruct']


def analyze(root, parent):
    data = root / 'data-v1.jsonl'
    meta = {r['item_id']: r for r in map(json.loads, data.read_text().splitlines())}
    runs = json.loads((root / 'runner-pids-v1.json').read_text())
    reports, effects, provenance, coverage, noise = {}, [], [], [], []

    def report(label, values):
        result, clusters = summarize(values, seed=84)
        reports[label] = result
        effects.extend(dict(report=label, cluster_id=k, value=v) for k, v in clusters.items())

    for model in MODELS:
        directory = parent / 'runs-v1' / model
        pcfg = json.loads((directory / 'config.json').read_text())
        parent_identity = manifest_identity(pcfg)
        assert pcfg['data_sha256'] == sha(data)
        assert pcfg['qa_predictions_sha256'] == sha(directory / 'qa-predictions.jsonl')
        index = {}
        for p in map(json.loads, (directory / 'qa-predictions.jsonl').read_text().splitlines()):
            if p['operation'] not in OPS[:2]:
                continue
            key = p['item_id'], p['operation'], p['readout'], p['mapping']
            assert key not in index
            index[key] = p
        ids = {k[0] for k in index}
        rows = [dict(meta[uid], cluster_id=meta[uid]['analysis_cluster_id'],
                     question_target=meta[uid]['analysis_question_target']) for uid in sorted(ids)]
        for r in rows:
            mother = index[r['item_id'], 'BASE_BANK', 'words', 0]
            assert all(r[k] == mother[k] for k in ['cluster_id', 'question_target',
                'source_unit', 'sentence_sha256', 'construction', 'condition'])
        subruns = [r for r in runs if r['model'] == model]
        n = subruns[0]['shards']
        assert {r['shard'] for r in subruns} == set(range(n))
        for run in subruns:
            out = Path(run['out'])
            cfg = json.loads((out / 'config.json').read_text())
            assert cfg['data_sha256'] == sha(data)
            assert cfg['parent_qa_predictions_sha256'] == pcfg['qa_predictions_sha256']
            assert cfg['source_banks_sha256'] == pcfg['source_banks_sha256']
            assert manifest_identity(dict(model_path=str(root.parent / 'models' / model),
                model_manifest_sha256=cfg['model_manifest_sha256'])) == parent_identity
            assert cfg['predictions_sha256'] == sha(out / 'predictions.jsonl')
            ps = list(map(json.loads, (out / 'predictions.jsonl').read_text().splitlines()))
            sub = {uid for uid in ids if int(meta[uid]['sentence_sha256'][:16], 16) % n == run['shard']}
            assert len(ps) == cfg['new_tasks'] == 8 * len(sub)
            assert set(cfg['cohort']) == {meta[uid]['source_unit'] for uid in sub}
            for p in ps:
                key = p['item_id'], p['operation'], p['readout'], p['mapping']
                assert key not in index and p['item_id'] in sub and p['operation'] in OPS[2:]
                base = index[p['item_id'], 'BASE_BANK', p['readout'], p['mapping']]
                assert p['prompt_sha256'] == base['prompt_sha256']
                assert p['candidate_gold'] == base['candidate_gold']
                index[key] = p
            provenance.append(dict(model=model, shard=run['shard'], gpu_hours=cfg['gpu_hours'],
                config_sha256=sha(out / 'config.json'), predictions_sha256=cfg['predictions_sha256'],
                parent_config_sha256=sha(directory / 'config.json'),
                parent_predictions_sha256=pcfg['qa_predictions_sha256'],
                source_banks_sha256=cfg['source_banks_sha256'], instrument=cfg['instrument']))
        assert set(index) == {(uid, op, ro, mp) for uid in ids for op in OPS
                             for ro in ['words', 'letters'] for mp in [0, 1]}
        assert {r['source_unit'] for r in rows} == set(pcfg['cohort'])
        for ct in ['MVRR', 'NPZ', 'NPS', 'NPVP', 'pooled']:
            for cond in ['gp', 'control']:
                selected = [r for r in rows if r['condition'] == cond and (ct == 'pooled' or r['construction'] == ct)]
                groups = collections.defaultdict(list)
                for r in selected:
                    groups[r['source_unit']].append(r)
                coverage.append(dict(model=model, construction=ct, condition=cond, QA=len(selected),
                    source_units=len(groups), lexical_clusters=len({r['cluster_id'] for r in selected}),
                    target_sets=dict(collections.Counter(','.join(sorted({r['question_target'] for r in g})) for g in groups.values()))))
                for ro in ['words', 'letters']:
                    for target in ['initial', 'final', 'other', 'all']:
                        subset = [r for r in selected if target == 'all' or r['question_target'] == target]
                        for metric in ['correct', 'p_correct']:
                            values = {op: [(r, sum(float(index[r['item_id'], op, ro, mp][metric]) for mp in [0, 1]) / 2)
                                           for r in subset] for op in OPS}
                            prefix = f'{model}/{ct}/{cond}/{target}/{ro}/{metric}'
                            for op in OPS:
                                report(prefix + '/' + op, values[op])
                            for a, b in CONTRASTS:
                                report(prefix + '/' + a + '-minus-' + b,
                                       [(r, av - bv) for (r, av), (_, bv) in zip(values[a], values[b])])
                    prefix = f'{model}/{ct}/{cond}/joint_all_registered_QA/{ro}/correct'
                    joint = {op: [(g[0], sum(all(index[r['item_id'], op, ro, mp]['correct'] for r in g)
                                for mp in [0, 1]) / 2) for g in groups.values()] for op in OPS}
                    for op in OPS:
                        report(prefix + '/' + op, joint[op])
                    for a, b in CONTRASTS:
                        report(prefix + '/' + a + '-minus-' + b,
                               [(r, av - bv) for (r, av), (_, bv) in zip(joint[a], joint[b])])
                    for op in OPS:
                        flips = [abs(float(index[r['item_id'], op, ro, 0]['correct']) -
                                     float(index[r['item_id'], op, ro, 1]['correct'])) for r in selected]
                        noise.append(dict(model=model, construction=ct, condition=cond, readout=ro,
                            operation=op, QA=len(selected), mean_mapping_flip=sum(flips) / len(flips) if flips else None))
    assert len(reports) == 5400
    out = root / 'source-key-value-map-v2.json'
    assert not out.exists()
    effect = out.with_suffix('.cluster-effects.jsonl')
    effect.write_text(''.join(json.dumps(r) + '\n' for r in effects))
    out.write_text(json.dumps(dict(data_sha256=sha(data), reports=reports, runs=provenance,
        coverage=coverage, mapping_noise=noise, cluster_effects_sha256=sha(effect),
        statistics='Mappings/QA within Source unit; donors within identical S; sentences within lexical cluster; 10000 paired bootstrap seed84.',
        limits='Fixed BASE Source block replay; K/V consumer projection changes are not pure syntactic variables. Joint covers registered QA only; initial/final coverage explicitly reported. No native propagation or spontaneous parse claim.'), indent=2) + '\n')
    (root / 'complete-map-v2.json').write_text(json.dumps(dict(all_models_complete=True,
        shards=len(runs), reports=len(reports), map_sha256=sha(out), gpu_hours=sum(r['gpu_hours'] for r in provenance)), indent=2) + '\n')
    print('E84 complete', sha(out), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--parent', type=Path, required=True)
    a = p.parse_args()
    analyze(a.root, a.parent)
