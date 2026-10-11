"""E98 all registered actual QA/role/joint uses; complete outputs only, unknown bounds."""
import argparse
import collections
import json
from pathlib import Path

from data import sha
from data_v2 import digest
from current_open_baseline import MODELS
from query_guidance_fidelity import MODES
from analyze_correct_answer_carry import estimate
from analyze_paraphrases import PATTERNS


def load(p):
    return list(map(json.loads, p.read_text().splitlines()))


def analyze(root, selected_models=None, output_name='query-guidance-fidelity-map-v1.json'):
    models = MODELS if selected_models is None else selected_models
    assert models and set(models) <= set(MODELS)
    rows = load(root/'data-v1.jsonl')
    annotations = {r['item_id']: r for r in load(root/'step5/annotated.jsonl')}
    assignments = {(r['model'], r['item_id'], r['mode']): r for r in load(root/'assignments-v1.jsonl')}
    runs = json.loads((root/'runner-pids-v1.json').read_text())
    panels, records, provenance, counts = [], [], [], []
    for model in models:
        index = {}
        for run in [r for r in runs if r['model'] == model]:
            out = Path(run['out'])
            cfg = json.loads((out/'config.json').read_text())
            assert cfg['data_sha256'] == sha(root/'data-v1.jsonl')
            assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
            ps = load(out/'predictions.jsonl')
            assert len(ps) == cfg['tasks'] == cfg['rows']*6
            provenance.append(dict(model=model, shard=run['shard'], config_sha256=sha(out/'config.json'),
                                   predictions_sha256=cfg['predictions_sha256'], gpu_hours=cfg['gpu_hours']))
            for p in ps:
                key = p['item_id'], p['mode'], p['readout']
                assert key not in index
                assert p['text_sha256'] == digest(p['text'])
                index[key] = p
        assert set(index) == {(r['item_id'], mode, readout) for r in rows for mode in MODES for readout in ['QA', 'PARAPHRASE']}
        values = {}
        for r in rows:
            for mode in MODES:
                qa, p = [index[r['item_id'], mode, ro] for ro in ['QA', 'PARAPHRASE']]
                assert qa['sentence_sha256'] == p['sentence_sha256'] == r['sentence_sha256']
                a = assignments[model, r['item_id'], mode]
                assert a['text_sha256'] == p['text_sha256']
                z = annotations.get(a['audit_id'])
                category = None
                if z and z.get('step5_status') in ['agreed', 'adjudicated'] and not a['unfinished_thinking']:
                    category = PATTERNS[tuple(z['step5_annotation']['option_labels'])]
                p_known = p['stopped'] and bool(p['text'].strip()) and category is not None
                q_known = qa['stopped'] and qa['answer'] is not None and r['goal_gold'] is not None
                qlo = float(q_known and qa['answer'] == r['goal_gold'])
                qhi = float(not q_known or qlo)
                v = dict(QA_lower=qlo, QA_upper=qhi, QA_unknown=float(not q_known),
                         QA_capped=float(qa['capped']), P_unknown=float(not p_known), P_capped=float(p['capped']))
                for role in ['CORRECT_ROLES', 'GP_MISREADING', 'OTHER']:
                    lo = float(p_known and category == role)
                    hi = float(not p_known or lo)
                    v[role+'_lower'], v[role+'_upper'] = lo, hi
                    if role != 'OTHER':
                        v['QA_correct_and_'+role+'_lower'] = qlo*lo
                        v['QA_correct_and_'+role+'_upper'] = qhi*hi
                values[r['item_id'], mode] = v
                records.append(dict(model=model, item_id=r['item_id'], mode=mode, cluster_id=r['cluster_id'],
                    construction=r['construction'], condition=r['condition'], goal_origin=r['goal_origin'],
                    goal_gold=r['goal_gold'], QA_answer=qa['answer'], role=category, metrics=v))
        groups = {'ALL': rows}
        for field in ['construction', 'condition', 'goal_gold', 'goal_origin']:
            for x in sorted({str(r[field]) for r in rows}):
                groups[field+':'+x] = [r for r in rows if str(r[field]) == x]
        # All construction/side/truth/origin cells, including structural NA.
        for ct in sorted({r['construction'] for r in rows}):
            for side in ['gp', 'control']:
                for gold in ['ALL', 'Yes', 'No', 'NA']:
                    for origin in ['ALL', 'E67_INITIAL', 'ORIGINAL_Q_FALLBACK']:
                        key = '/'.join([ct, side, gold, origin])
                        groups[key] = [r for r in rows if r['construction'] == ct and r['condition'] == side
                            and (gold == 'ALL' or (r['goal_gold'] or 'NA') == gold)
                            and (origin == 'ALL' or r['goal_origin'] == origin)]
        for group, selected in groups.items():
            counts.append(dict(model=model, group=group, sources=len(selected),
                pairs=len({r['cluster_id'] for r in selected}), goal_gold=dict(collections.Counter(r['goal_gold'] or 'NA' for r in selected))))
            metrics = next(iter(values.values()))
            for mode in MODES:
                for metric in metrics:
                    panels.append(dict(model=model, group=group, mode=mode, metric=metric,
                        **estimate(selected, [values[r['item_id'], mode][metric] for r in selected], seed=98)))
            for before, after in [('NATIVE', 'GOAL'), ('GOAL', 'QUESTION_ONLY')]:
                for metric in metrics:
                    # Bound differences retain unknown outcomes; never complete-case select.
                    if metric.endswith('_lower') or metric.endswith('_upper'):
                        prefix, bound = metric.rsplit('_', 1)
                        opposite = prefix+('_upper' if bound == 'lower' else '_lower')
                    else:
                        opposite = metric
                    deltas = [values[r['item_id'], after][metric]-values[r['item_id'], before][opposite] for r in selected]
                    panels.append(dict(model=model, group=group, mode=after+'-minus-'+before, metric=metric,
                        **estimate(selected, deltas, seed=98)))
    out = root/output_name
    assert not out.exists()
    out.write_text(json.dumps(dict(models=models, data_sha256=sha(root/'data-v1.jsonl'),
        annotation_sha256=sha(root/'step5/annotated.jsonl'), assignment_sha256=sha(root/'assignments-v1.jsonl'),
        panels=panels, records=records, counts=counts, runs=provenance,
        scope='Full preregistered three-family cohort' if selected_models is None else 'INTERIM complete-family hypothesis generation; full cohort continues',
        statistics='Source then original pair cluster mean; paired10000 bootstrap seed98; unknown/cap bounds, empty cells NA.',
        limits='Behavioral cross-use, not one unique latent parse. Goal support only frozen original source-Q labels. Fallback goal provenance separate. No RL outcome inference.'), indent=2)+'\n')
    manifest = dict(map_sha256=sha(out), actual_outputs=600*len(models), panels=len(panels),
                    models=models, gpu_hours=sum(p['gpu_hours'] for p in provenance))
    (root/(output_name+'.manifest.json')).write_text(json.dumps(manifest, indent=2)+'\n')
    print('E98 map sealed', manifest, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    analyze(p.parse_args().root)
