"""E86 complete-only source acceptance and task-contract map; original QA gold."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from current_open_baseline import MODELS, tokenizer
from source_acceptance import prepare
from data_v2 import digest
from analyze_correct_answer_carry import estimate

OPS = ['QA_STRICT', 'QA_RECOVER', 'QA_PLAIN', 'QA_PLAIN-minus-QA_STRICT', 'QA_PLAIN-minus-QA_RECOVER']


def analyze(root, parent, runs):
    data = root / 'data-v1.jsonl'
    rows = list(map(json.loads, data.read_text().splitlines()))
    manifest = json.loads(data.with_suffix('.manifest.json').read_text())
    assert sha(data) == manifest['data_sha256'] and sha(parent / data.name) == manifest['parent_data_sha256']
    qa = [dict(r, cluster_id=r['analysis_cluster_id']) for r in rows if r['task_kind'] == 'QA_PLAIN']
    grammar = [dict(r, cluster_id=r['analysis_cluster_id']) for r in rows if r['task_kind'] == 'GRAM_ACCEPT']
    assert len(qa) == 892 and len(grammar) == 356
    gmeta = {r['source_unit']: r for r in grammar}
    panels, gpanels, provenance, noise, cells, coverage, strata = [], [], [], [], [], [], []
    for model in MODELS:
        ts = prepare(rows, tokenizer(root.parent / 'models' / model))
        expected = {(t['row']['item_id'], t['readout'], t['mapping']): t for t in ts}
        qi, gi, ni = {}, {}, {}
        for run in json.loads((parent / 'runner-pids-v1.json').read_text()):
            if run['model'] != model:
                continue
            out = Path(run['out']);cfg = json.loads((out / 'config.json').read_text())
            assert cfg['predictions_sha256'] == sha(out / 'predictions.jsonl')
            assert cfg['data_sha256'] == sha(parent / data.name)
            assert cfg['model_manifest_sha256'] == sha(root.parent / 'models' / model / 'manifest.json')
            for p in map(json.loads, (out / 'predictions.jsonl').read_text().splitlines()):
                key = p['item_id'], p['readout'], p['mapping']
                op = 'QA_STRICT' if p['operation'] == 'DIRECT' else 'QA_RECOVER'
                assert (*key, op) not in qi
                qi[(*key, op)] = p
        records = [r for r in runs if r['model'] == model];n = records[0]['shards']
        assert {r['shard'] for r in records} == set(range(n))
        for run in records:
            out = Path(run['out']);cfg = json.loads((out / 'config.json').read_text())
            assert cfg['data_sha256'] == sha(data) and cfg['predictions_sha256'] == sha(out / 'predictions.jsonl')
            assert cfg['model_manifest_sha256'] == sha(root.parent / 'models' / model / 'manifest.json')
            sub = {r['item_id'] for r in rows if int(r['sentence_sha256'][:16], 16) % n == run['shard']}
            ps = list(map(json.loads, (out / 'predictions.jsonl').read_text().splitlines()))
            assert len(ps) == cfg['tasks'] == 4 * len(sub)
            assert {p['item_id'] for p in ps} == sub
            for p in ps:
                key = p['item_id'], p['readout'], p['mapping'];assert key not in ni
                t = expected[key]
                assert p['prompt_sha256'] == digest(t['prompt']) and p['candidate_gold'] == t['candidate_gold']
                assert t['parent_prompt_sha256'] == qi[t['row']['original_item_id'], p['readout'], p['mapping'], 'QA_STRICT']['prompt_sha256']
                ni[key] = p
                if t['row']['task_kind'] == 'QA_PLAIN':
                    qi[(*key, 'QA_PLAIN')] = p
                else:
                    gkey = t['row']['source_unit'], p['readout'], p['mapping'];assert gkey not in gi;gi[gkey] = p
            provenance.append(dict(model=model, shard=run['shard'], gpu_hours=cfg['gpu_hours'],
                config_sha256=sha(out / 'config.json'), predictions_sha256=cfg['predictions_sha256'],
                model_manifest_sha256=cfg['model_manifest_sha256'], score_function=cfg['score_function'],
                prefix_full_LP_max_delta=cfg['prefix_full_LP_max_delta'],
                repeat_LP_max_delta=max(x['repeat_LP_max_delta'] for x in cfg['instrument'])))
        assert set(ni) == set(expected)
        assert len(qi) == 892 * 4 * 3 and len(gi) == 356 * 4

        def atom(row, op, ro, metric):
            def raw(k):
                return sum(float(qi[row['item_id'], ro, mp, k][metric]) for mp in [0, 1]) / 2
            if '-minus-' in op:
                a, b = op.split('-minus-');return raw(a) - raw(b)
            return raw(op)

        for ct in ['MVRR', 'NPZ', 'NPS', 'NPVP']:
            for cond in ['gp', 'control']:
                allqa = [r for r in qa if r['construction'] == ct and r['condition'] == cond]
                gg = [r for r in grammar if r['construction'] == ct and r['condition'] == cond]
                groups = collections.defaultdict(list)
                for r in allqa:
                    groups[r['source_unit']].append(r)
                assert set(groups) == {r['source_unit'] for r in gg}
                coverage.append(dict(model=model, construction=ct, condition=cond, QA=len(allqa),
                    sources=len(groups), target_sets=dict(collections.Counter(','.join(sorted({r['analysis_question_target'] for r in g})) for g in groups.values()))))
                for ro in ['words', 'letters']:
                    for target in ['initial', 'final', 'all']:
                        selected = [r for r in allqa if target == 'all' or r['analysis_question_target'] == target]
                        for metric in ['correct', 'p_correct']:
                            for op in OPS:
                                panels.append(dict(model=model, construction=ct, condition=cond, readout=ro,
                                    target=target, metric=metric, operation=op,
                                    **estimate(selected, [atom(r, op, ro, metric) for r in selected], seed=86)))
                    reps = [g[0] for _, g in sorted(groups.items())];joint = {}
                    for uid, group in groups.items():
                        for op in OPS[:3]:
                            joint[uid, op] = sum(all(qi[r['item_id'], ro, mp, op]['correct'] for r in group) for mp in [0, 1]) / 2
                    for op in OPS:
                        if '-minus-' in op:
                            a, b = op.split('-minus-');values = [joint[r['source_unit'], a] - joint[r['source_unit'], b] for r in reps]
                        else:
                            values = [joint[r['source_unit'], op] for r in reps]
                        panels.append(dict(model=model, construction=ct, condition=cond, readout=ro,
                            target='joint_all_registered_QA', metric='correct', operation=op,
                            **estimate(reps, values, seed=86)))
                    for metric in ['correct', 'p_correct']:
                        gpanels.append(dict(model=model, construction=ct, condition=cond, readout=ro,
                            metric=metric, operation='GRAM_ACCEPT',
                            **estimate(gg, [sum(float(gi[r['source_unit'], ro, mp][metric]) for mp in [0, 1]) / 2 for r in gg], seed=86)))
                    for op in OPS[:3]:
                        by_stratum = collections.defaultdict(list)
                        for r in allqa:
                            tag = (r['analysis_question_target'], r['grounded_gold'], r['literal_label'],
                                   r['source_gold_matches_grounding'])
                            by_stratum[tag].extend(qi[r['item_id'], ro, mp, op] for mp in [0, 1])
                        strata.append(dict(model=model, construction=ct, condition=cond, readout=ro,
                            operation=op, descriptive_raw_task_counts=[dict(target=k[0], grounded_gold=k[1],
                                literal_label=k[2], original_gold_matches=k[3], n_mapping_tasks=len(ps),
                                n_correct=sum(p['correct'] for p in ps), sum_p_correct=sum(p['p_correct'] for p in ps))
                                for k, ps in sorted(by_stratum.items())]))
                        noise.append(dict(model=model, construction=ct, condition=cond, readout=ro, operation=op,
                            mapping_flip=sum(abs(float(qi[r['item_id'], ro, 0, op]['correct']) - float(qi[r['item_id'], ro, 1, op]['correct'])) for r in allqa) / len(allqa)))
                        counts = collections.Counter()
                        for uid, group in groups.items():
                            has_positive = any(r['grounded_gold'] == 'Yes' for r in group)
                            for mp in [0, 1]:
                                accepted = bool(gi[uid, ro, mp]['correct'])
                                all_no = all(bool(qi[r['item_id'], ro, mp, op]['correct']) == (r['grounded_gold'] == 'No') for r in group)
                                all_right = all(qi[r['item_id'], ro, mp, op]['correct'] for r in group)
                                counts[f'grammar_{accepted}/has_positive_{has_positive}/all_No_{all_no}/all_QA_right_{all_right}'] += 1
                        cells.append(dict(model=model, construction=ct, condition=cond, readout=ro,
                            operation=op, source_mapping_instances=2 * len(groups), counts=dict(counts)))
                    noise.append(dict(model=model, construction=ct, condition=cond, readout=ro, operation='GRAM_ACCEPT',
                        mapping_flip=sum(abs(float(gi[r['source_unit'], ro, 0]['correct']) - float(gi[r['source_unit'], ro, 1]['correct'])) for r in gg) / len(gg)))
    assert len(panels) == 1680 and len(gpanels) == 96 and len(noise) == 192 and len(cells) == 144
    out = root / 'source-acceptance-map-v1.json';assert not out.exists()
    out.write_text(json.dumps(dict(data_sha256=sha(data), panels=panels, grammar=gpanels, runs=provenance,
        mapping_noise=noise, joint_cells=cells, coverage=coverage, qa_gold_strata=strata,
        statistics='Average mappings/QA within Source; average Source within lexical cluster; 10000 paired bootstrap seed86. Joint cells are descriptive raw Source/mapping counts, not independent sample sizes.',
        limits='Task after Source changes, visible Source prefix stays identical. Grammar behavior is not latent parse. Plain comprehension permits pragmatic interpretation; changes are not automatically source-grounded recovery. Joint covers registered questions only.'), indent=2) + '\n')
    (root / 'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True, shards=len(runs),
        panels=len(panels), grammar=len(gpanels), map_sha256=sha(out), gpu_hours=sum(r['gpu_hours'] for r in provenance)), indent=2) + '\n')
    print('E86 complete', sha(out), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser();p.add_argument('--root', type=Path, required=True);p.add_argument('--parent', type=Path, required=True);p.add_argument('--wait', action='store_true');a = p.parse_args()
    runs = json.loads((a.root / 'runner-pids-v1.json').read_text())
    while a.wait:
        ready = []
        for r in runs:
            path = Path(r['out']) / 'config.json';ready.append(path.exists() and 'predictions_sha256' in json.loads(path.read_text()))
        if all(ready):break
        time.sleep(20)
    analyze(a.root, a.parent, runs)
