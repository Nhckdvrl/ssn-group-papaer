"""E83 complete-only post-hoc map: existing Source evidence segmented at input T2."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from joint_relation_use import MODELS
from analyze_correct_answer_carry import estimate
from goal_conditioned_reading import prepare as native_prepare
from data_v2 import digest

OPS = ['NATIVE', 'WHOLE_EVIDENCE', 'LATE_EVIDENCE', 'LATE_EVIDENCE-minus-WHOLE_EVIDENCE',
       'LATE_EVIDENCE-minus-NATIVE', 'WHOLE_EVIDENCE-minus-NATIVE']


def analyze(root, parent, runs):
    data = root / 'data-v1.jsonl'
    rows = list(map(json.loads, data.read_text().splitlines()))
    ids = {r['item_id'] for r in rows}
    assert len(ids) == len(rows) and sha(parent / data.name) == json.loads(data.with_suffix('.manifest.json').read_text())['parent_data_sha256']
    for r in rows:
        r['cluster_id'] = r['analysis_cluster_id']
    expected = {(uid, op, ro, mp) for uid in ids for op in OPS[:3]
                for ro in ['words', 'letters'] for mp in [0, 1]}
    panels, provenance, lengths, noise = [], [], [], []
    for model in MODELS:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(root.parent / 'models' / model, local_files_only=True)
        native_tasks = {(t['row']['item_id'], t['readout'], t['mapping']): t
                        for t in native_prepare(rows, tok) if t['operation'] == 'NONE'}
        base = parent / 'runs-v1' / model
        bcfg = json.loads((base / 'config.json').read_text())
        assert bcfg['data_sha256'] == sha(parent / data.name)
        assert bcfg['predictions_sha256'] == sha(base / 'predictions.jsonl')
        index = {}
        for p in map(json.loads, (base / 'predictions.jsonl').read_text().splitlines()):
            if p['operation'] == 'NONE' and p['item_id'] in ids:
                key = p['item_id'], 'NATIVE', p['readout'], p['mapping']
                assert key not in index
                task = native_tasks[p['item_id'], p['readout'], p['mapping']]
                assert p['prompt_sha256'] == digest(task['prompt'])
                index[key] = dict(p, prompt_tokens=task['encoded'][1])
        records = [r for r in runs if r['model'] == model]
        n = records[0]['shards']
        assert {r['shard'] for r in records} == set(range(n))
        for run in records:
            directory = Path(run['out'])
            cfg = json.loads((directory / 'config.json').read_text())
            assert cfg['data_sha256'] == sha(data)
            assert cfg['predictions_sha256'] == sha(directory / 'predictions.jsonl')
            assert cfg['model_manifest_sha256'] == bcfg['model_manifest_sha256']
            assert cfg['parent_predictions_sha256'] == bcfg['predictions_sha256']
            sub = {r['item_id'] for r in rows
                   if int(r['sentence_sha256'][:16], 16) % n == run['shard']}
            ps = list(map(json.loads, (directory / 'predictions.jsonl').read_text().splitlines()))
            assert len(ps) == cfg['tasks'] == 8 * len(sub)
            assert {p['item_id'] for p in ps} == sub
            for p in ps:
                key = p['item_id'], p['operation'], p['readout'], p['mapping']
                assert key not in index
                index[key] = p
            provenance.append(dict(model=model, shard=run['shard'],
                gpu_hours=cfg['gpu_hours'], config_sha256=sha(directory / 'config.json'),
                predictions_sha256=cfg['predictions_sha256'],
                native_predictions_sha256=bcfg['predictions_sha256'],
                inherited_parent_LP_max_delta=max(c['parent_LP_max_delta'] for c in cfg['instrument']),
                score_reconstruction_max_error=cfg['score_reconstruction_max_error']))
        assert set(index) == expected
        for r in rows:
            for op in OPS[:3]:
                for ro in ['words', 'letters']:
                    for mp, shown in enumerate([['Yes', 'No'], ['No', 'Yes']]):
                        assert index[r['item_id'], op, ro, mp]['candidate_gold'] == shown.index(r['grounded_gold'])

        def atom(r, op, ro, metric):
            def value(k):
                return sum(float(index[r['item_id'], k, ro, mp][metric]) for mp in [0, 1]) / 2
            if '-minus-' in op:
                a, b = op.split('-minus-')
                return value(a) - value(b)
            return value(op)

        for ct in ['MVRR', 'NPZ', 'NPS', 'NPVP']:
            for cond in ['gp', 'control']:
                selected_all = [r for r in rows if r['construction'] == ct and r['condition'] == cond]
                for op in OPS[:3]:
                    ts = [index[r['item_id'], op, ro, mp]['prompt_tokens']
                          for r in selected_all for ro in ['words', 'letters'] for mp in [0, 1]]
                    lengths.append(dict(model=model, construction=ct, condition=cond,
                        operation=op, mean_tokens=sum(ts) / len(ts), max_tokens=max(ts), tasks=len(ts)))
                for ro in ['words', 'letters']:
                    for target in ['initial', 'final', 'all']:
                        selected = [r for r in selected_all if target == 'all' or r['analysis_question_target'] == target]
                        for metric in ['correct', 'p_correct']:
                            for op in OPS:
                                panels.append(dict(model=model, construction=ct, condition=cond,
                                    readout=ro, target=target, metric=metric, operation=op,
                                    **estimate(selected, [atom(r, op, ro, metric) for r in selected], seed=83)))
                    groups = collections.defaultdict(list)
                    for r in selected_all:
                        groups[r['source_unit']].append(r)
                    reps = [g[0] for _, g in sorted(groups.items())]
                    joint = {}
                    for uid, group in groups.items():
                        for op in OPS[:3]:
                            joint[uid, op] = sum(all(index[r['item_id'], op, ro, mp]['correct'] for r in group)
                                                 for mp in [0, 1]) / 2
                    for op in OPS:
                        if '-minus-' in op:
                            a, b = op.split('-minus-')
                            vs = [joint[r['source_unit'], a] - joint[r['source_unit'], b] for r in reps]
                        else:
                            vs = [joint[r['source_unit'], op] for r in reps]
                        panels.append(dict(model=model, construction=ct, condition=cond,
                            readout=ro, target='joint_all_questions', metric='correct', operation=op,
                            **estimate(reps, vs, seed=83)))
                    for op in OPS[:3]:
                        noise.append(dict(model=model, construction=ct, condition=cond,
                            readout=ro, operation=op, mean_QA_correct_flip=sum(abs(
                                float(index[r['item_id'], op, ro, 0]['correct']) -
                                float(index[r['item_id'], op, ro, 1]['correct'])) for r in selected_all) / len(selected_all)))
    assert len(panels) == 2016 and len(lengths) == 72 and len(noise) == 144
    out = root / 'disambiguation-evidence-map-v1.json'
    assert not out.exists()
    out.write_text(json.dumps(dict(data_sha256=sha(data), panels=panels, runs=provenance,
        prompt_lengths=lengths, mapping_noise=noise,
        statistics='Mean mappings per QA; mean QA per Source; lexical cluster paired bootstrap10000 seed83. Joint all originalQA per mapping then Source.',
        limits='POST-HOC E81 readout; input-only existing T2 subset, missing/conflicting sources preserved in manifest. Candidate labels condition Source encoding. Suffix evidence is not native parse or a neural causal intervention.'), indent=2) + '\n')
    (root / 'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,
        shards=len(runs), panels=len(panels), map_sha256=sha(out),
        gpu_hours=sum(r['gpu_hours'] for r in provenance)), indent=2) + '\n')
    print('E83 complete', sha(out), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--wait', action='store_true')
    a = p.parse_args()
    runs = json.loads((a.root / 'runner-pids-v1.json').read_text())
    while a.wait:
        ready = []
        for r in runs:
            path = Path(r['out']) / 'config.json'
            ready.append(path.exists() and 'predictions_sha256' in json.loads(path.read_text()))
        if all(ready):
            break
        time.sleep(20)
    analyze(a.root, a.parent, runs)
