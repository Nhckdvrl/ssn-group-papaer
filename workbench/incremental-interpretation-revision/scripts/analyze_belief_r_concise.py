"""E97 concise actual answers versus exactly the original E93 reconstruction scores."""
import argparse
import collections
import json
from pathlib import Path
import time

from data import sha
from data_v2 import digest
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate


def analyze(root, selected_models=None, output_name='belief-r-concise-map-v1.json', manifest_name='complete-map-v1.json'):
    models = MODELS if selected_models is None else selected_models
    assert models and set(models) <= set(MODELS)
    data = root/'data-v1.jsonl'
    assert sha(data) == sha(root.parent/'E93/data-v1.jsonl')
    rows = list(map(json.loads, data.read_text().splitlines()))
    meta = {r['item_id']: r for r in rows}
    indices, provenance = {}, []
    for name in ['E93', 'E97']:
        parent = root.parent/name
        index = {}
        for run in json.loads((parent/'runner-pids-v1.json').read_text()):
            if run['model'] not in models:
                continue
            out = Path(run['out'])
            cfg = json.loads((out/'config.json').read_text())
            assert cfg['data_sha256'] == sha(data) and cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
            assert cfg['model_manifest_sha256'] == sha(root.parent/'models'/run['model']/'manifest.json')
            ps = list(map(json.loads, (out/'predictions.jsonl').read_text().splitlines()))
            assert len(ps) == cfg['rows']*(5 if name == 'E93' else 1)
            for p in ps:
                r = meta[p['item_id']]
                assert int(digest(r['cluster_id'])[:16], 16) % run['shards'] == run['shard']
                key = run['model'], p['item_id'], p['operation'], p.get('candidate', '')
                assert key not in index
                if p['operation'] == 'RECONSTRUCTION':
                    assert abs(sum(p['token_logprobs'])-p['reward_sum']) < 1e-8
                index[key] = p
            provenance.append(dict(experiment=name, model=run['model'], shard=run['shard'],
                predictions_sha256=cfg['predictions_sha256'], config_sha256=sha(out/'config.json'),
                code_sha256=cfg['code_sha256'], gpu_hours=cfg['gpu_hours']))
        assert len(index) == len(rows)*len(models)*(5 if name == 'E93' else 1)
        indices[name] = index
    panels, records, counts = [], [], []
    for model in models:
        values = {}
        for r in rows:
            uid, gold = r['item_id'], r['ground_truth']
            scores = {c: indices['E93'][model, uid, 'RECONSTRUCTION', c] for c in 'abc'}
            assert len({s['observation_tokens'] for s in scores.values()}) == 1
            best = max(s['reward_mean'] for s in scores.values())
            top = [c for c in 'abc' if scores[c]['reward_mean'] == best]
            p = indices['E97'][model, uid, 'FORMAT_ONLY', '']
            lo = float(p['stopped'] and p['answer'] == gold)
            hi = float(not p['stopped'] or p['answer'] is None or p['answer'] == gold)
            rawlo, rawhi = float(top == [gold]), float(gold in top)
            v = dict(format_lower_correct=lo, format_upper_correct=hi, format_unknown=float(p['answer'] is None),
                     format_capped=float(p['capped']), format_output_tokens=len(p['output_tokens']),
                     reconstruction_lower_correct=rawlo, reconstruction_upper_correct=rawhi,
                     reconstruction_tie=float(len(top)>1), reconstruction_minus_format_lower=rawlo-hi,
                     reconstruction_minus_format_upper=rawhi-lo,
                     format_correct_reward_wrong=float(lo and gold not in top),
                     format_wrong_reward_correct=float(p['stopped'] and p['valid'] and not lo and top == [gold]))
            for mode in ['FORWARD_DIRECT', 'FORWARD_COT']:
                old = indices['E93'][model, uid, mode, '']
                v[mode+'_lower_correct'] = float(old['lower_correct'])
                v[mode+'_upper_correct'] = float(old['upper_correct'])
                v[mode+'_unknown'] = float(not old['valid'])
                v[mode+'_capped'] = float(old['capped'])
                v['FORMAT-minus-'+mode+'_lower'] = lo-float(old['upper_correct'])
                v['FORMAT-minus-'+mode+'_upper'] = hi-float(old['lower_correct'])
            values[uid] = v
            records.append(dict(model=model, item_id=uid, cluster_id=r['cluster_id'],
                modus=r['modus'], transition=r['transition'], ground_truth=gold,
                format_choice=p['answer'], stopped=p['stopped'], reconstruction_top_set=top, metrics=v))
        groups = {'all': rows, 'AUTHOR_UPDATE_GOLD_c': [r for r in rows if r['ground_truth']=='c'],
                  'AUTHOR_MAINTAIN_GOLD_ab': [r for r in rows if r['ground_truth']!='c']}
        for field in ['ground_truth', 'modus', 'types_of_relation', 'transition', 'agreement_lv']:
            for x in sorted({r[field] for r in rows}):
                groups[field+':'+x] = [r for r in rows if r[field] == x]
        for group, rs in groups.items():
            for metric in next(iter(values.values())):
                panels.append(dict(model=model, group=group, metric=metric,
                    **estimate(rs, [values[r['item_id']][metric] for r in rs], seed=97)))
            counts.append(dict(model=model, group=group, rows=len(rs),
                author_Gold=dict(collections.Counter(r['ground_truth'] for r in rs)),
                format_answers=dict(collections.Counter(indices['E97'][model,r['item_id'],'FORMAT_ONLY','']['answer'] or 'UNKNOWN' for r in rs)),
                format_unknown=sum(values[r['item_id']]['format_unknown'] for r in rs),
                format_capped=sum(values[r['item_id']]['format_capped'] for r in rs)))
        for metric in ['format_lower_correct', 'format_upper_correct', 'reconstruction_lower_correct', 'reconstruction_upper_correct']:
            point = sum(sum(values[r['item_id']][metric] for r in groups[g])/len(groups[g])
                        for g in ['AUTHOR_UPDATE_GOLD_c','AUTHOR_MAINTAIN_GOLD_ab'])/2
            panels.append(dict(model=model, group='AUTHOR_BREU', metric=metric, value=point, CI95=None,
                scope='Author row-weighted macro descriptive; clustered per-class intervals above.'))
    out = root/output_name
    assert not out.exists()
    out.write_text(json.dumps(dict(data_sha256=sha(data), models=models, panels=panels, records=records,
        counts=counts, runs=provenance,
        analysis_scope='Full fixed three-family panel' if selected_models is None else 'INTERIM complete family cohort for hypothesis generation only; full fixed panel continues.',
        statistics='All original1744 rows; Source then atomic seed group10000 bootstrap seed97; all cap/unknown bounds preserved.',
        limits='Original human suppression/pragmatic Gold, not a classical entailment oracle. Concise output instruction changes only response requirements. Raw E93 observation reconstruction reused without rescoring. Different interfaces do not certify one Bayes joint.'), indent=2)+'\n')
    report = dict(map_sha256=sha(out), models=models, new_actual_outputs=len(rows)*len(models), new_scores=0,
                  new_api_calls=0, gpu_hours=sum(r['gpu_hours'] for r in provenance if r['experiment']=='E97'), panels=len(panels))
    (root/manifest_name).write_text(json.dumps(report, indent=2)+'\n')
    print('E97 COMPLETE', report, flush=True)


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
            time.sleep(20)
    analyze(a.root)
