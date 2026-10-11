"""E85 complete-only published coherence map and paired ambiguity contrasts."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from current_open_baseline import MODELS, tokenizer
from lexical_semantic_recovery import CONDITIONS, prepare
from data_v2 import digest
from analyze_correct_answer_carry import estimate

OPS = ['DIRECT', 'ONE_RECOVER', 'ONE_RECOVER-minus-DIRECT']


def analyze(root, runs):
    path = root / 'data-v1.jsonl'
    rows = list(map(json.loads, path.read_text().splitlines()))
    assert len(rows) == 192 and sha(path) == json.loads(path.with_suffix('.manifest.json').read_text())['data_sha256']
    panels, provenance, noise, lengths = [], [], [], []
    expected = {(r['item_id'], op, ro, mp) for r in rows for op in OPS[:2]
                for ro in ['words', 'letters'] for mp in [0, 1]}
    by_id = {r['item_id']: r for r in rows}
    frames = collections.defaultdict(dict)
    for r in rows:
        frames[r['item']][r['condition']] = r
    assert len(frames) == 48 and all(set(v) == set(CONDITIONS) for v in frames.values())
    for model in MODELS:
        ts = prepare(rows, tokenizer(root.parent / 'models' / model))
        prompts = {(t['row']['item_id'], t['operation'], t['readout'], t['mapping']): t for t in ts}
        records = [r for r in runs if r['model'] == model]
        n = records[0]['shards']
        assert {r['shard'] for r in records} == set(range(n))
        index = {}
        for run in records:
            out = Path(run['out'])
            cfg = json.loads((out / 'config.json').read_text())
            assert cfg['data_sha256'] == sha(path)
            assert cfg['predictions_sha256'] == sha(out / 'predictions.jsonl')
            assert cfg['model_manifest_sha256'] == sha(root.parent / 'models' / model / 'manifest.json')
            sub = {r['item_id'] for r in rows if int(r['sentence_sha256'][:16], 16) % n == run['shard']}
            ps = list(map(json.loads, (out / 'predictions.jsonl').read_text().splitlines()))
            assert len(ps) == cfg['tasks'] == 8 * len(sub)
            assert {p['item_id'] for p in ps} == sub
            for p in ps:
                key = p['item_id'], p['operation'], p['readout'], p['mapping']
                assert key not in index
                task = prompts[key]
                assert p['prompt_sha256'] == digest(task['prompt'])
                assert p['candidate_gold'] == task['candidate_gold']
                index[key] = p
            provenance.append(dict(model=model, shard=run['shard'], gpu_hours=cfg['gpu_hours'],
                predictions_sha256=cfg['predictions_sha256'], config_sha256=sha(out / 'config.json'),
                model_manifest_sha256=cfg['model_manifest_sha256'],
                prefix_full_LP_max_delta=cfg['prefix_full_LP_max_delta'], score_function=cfg['score_function'],
                repeat_LP_max_delta=max(x['repeat_LP_max_delta'] for x in cfg['instrument'])))
        assert set(index) == expected

        def value(row, op, ro, metric):
            def raw(condition):
                return sum(float(index[row['item_id'], condition, ro, mp][metric]) for mp in [0, 1]) / 2
            return raw('ONE_RECOVER') - raw('DIRECT') if op == OPS[2] else raw(op)

        for condition in CONDITIONS:
            selected = [r for r in rows if r['condition'] == condition]
            for ro in ['words', 'letters']:
                for metric in ['correct', 'p_correct']:
                    for op in OPS:
                        panels.append(dict(model=model, condition=condition, readout=ro, metric=metric,
                            operation=op, **estimate(selected, [value(r, op, ro, metric) for r in selected], seed=85)))
                for op in OPS[:2]:
                    noise.append(dict(model=model, condition=condition, readout=ro, operation=op,
                        mean_mapping_flip=sum(abs(float(index[r['item_id'], op, ro, 0]['correct']) -
                                                  float(index[r['item_id'], op, ro, 1]['correct'])) for r in selected) / 48))
                    sizes = [index[r['item_id'], op, ro, mp]['prompt_tokens'] for r in selected for mp in [0, 1]]
                    lengths.append(dict(model=model, condition=condition, readout=ro, operation=op,
                        mean_tokens=sum(sizes) / len(sizes), max_tokens=max(sizes)))
        for ro in ['words', 'letters']:
            for metric in ['correct', 'p_correct']:
                for op in OPS:
                    pairs = [(g['coherent_unambiguous'], g['coherent_ambiguous']) for _, g in sorted(frames.items())]
                    panels.append(dict(model=model, condition='coherent_unambiguous-minus-ambiguous',
                        readout=ro, metric=metric, operation=op,
                        **estimate([a for a, b in pairs],
                            [value(a, op, ro, metric) - value(b, op, ro, metric) for a, b in pairs], seed=85)))
    assert len(panels) == 180 and len(noise) == len(lengths) == 48
    out = root / 'lexical-semantic-recovery-map-v1.json'
    assert not out.exists()
    out.write_text(json.dumps(dict(data_sha256=sha(path), panels=panels, runs=provenance,
        mapping_noise=noise, prompt_lengths=lengths,
        statistics='48 original lexical frames; average mappings per sentence; paired cluster bootstrap10000 seed85.',
        limits='Original coherence gold, not logical entailment or direct sense identity. Human initial dominance is not model commitment. Comparison with E82 is descriptive across different tasks; no automatic mechanism or ability claim.'), indent=2) + '\n')
    (root / 'complete-map-v1.json').write_text(json.dumps(dict(all_models_complete=True,
        shards=len(runs), panels=len(panels), map_sha256=sha(out),
        gpu_hours=sum(r['gpu_hours'] for r in provenance)), indent=2) + '\n')
    print('E85 complete', sha(out), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
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
    analyze(a.root, runs)
