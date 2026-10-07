"""E93 complete native behavior versus candidate reconstruction grades on author Gold."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from data_v2 import digest
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate


def analyze(root, selected_models=None, output_name='belief-r-forward-reconstruction-map-v1.json', manifest_name='complete-map-v1.json'):
    models = MODELS if selected_models is None else selected_models
    assert models and set(models) <= set(MODELS)
    rows = [json.loads(s) for s in (root/'data-v1.jsonl').read_text().splitlines()]
    meta = {r['item_id']: r for r in rows}
    index = {}
    provenance = []
    for run in json.loads((root/'runner-pids-v1.json').read_text()):
        if run['model'] not in models:
            continue
        p = Path(run['out'])
        cfg = json.loads((p/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(p/'predictions.jsonl')
        assert cfg['data_sha256'] == sha(root/'data-v1.jsonl')
        assert cfg['model_manifest_sha256'] == sha(root.parent/'models'/run['model']/'manifest.json')
        ps = [json.loads(s) for s in (p/'predictions.jsonl').read_text().splitlines()]
        assert len(ps) == cfg['rows']*5
        for x in ps:
            r = meta[x['item_id']]
            assert int(digest(r['cluster_id'])[:16], 16) % run['shards'] == run['shard']
            key = run['model'], x['item_id'], x['operation'], x.get('candidate', '')
            assert key not in index
            if x['operation'] == 'RECONSTRUCTION':
                assert abs(sum(x['token_logprobs'])-x['reward_sum']) < 1e-8
            index[key] = x
        provenance.append(dict(model=run['model'], shard=run['shard'],
                               config_sha256=sha(p/'config.json'), predictions_sha256=cfg['predictions_sha256'],
                               code_sha256=cfg['code_sha256'], gpu_hours=cfg['gpu_hours']))
    assert len(index) == len(rows)*5*len(models)
    panels = []
    disagreements = []
    raw = []
    for model in models:
        values = {}
        details = {}
        for r in rows:
            uid = r['item_id']
            scores = {c: index[model, uid, 'RECONSTRUCTION', c] for c in 'abc'}
            assert len({x['observation_tokens'] for x in scores.values()}) == 1
            means = {c: x['reward_mean'] for c, x in scores.items()}
            best = max(means.values())
            top = [c for c in 'abc' if means[c] == best]
            gold = r['ground_truth']
            v = dict(reconstruction_lower_correct=float(top == [gold]),
                     reconstruction_upper_correct=float(gold in top),
                     reconstruction_tie=float(len(top) > 1),
                     reconstruction_gold_margin=means[gold]-max(means[c] for c in 'abc' if c != gold))
            info = dict(reconstruction_choice=top[0], reconstruction_top_set=top,
                        reconstruction_reward_mean=means, ground_truth=gold)
            for mode in ['FORWARD_DIRECT', 'FORWARD_COT']:
                p = index[model, uid, mode, '']
                v[mode+'_lower_correct'] = float(p['lower_correct'])
                v[mode+'_upper_correct'] = float(p['upper_correct'])
                v[mode+'_unknown'] = float(not p['valid'])
                v[mode+'_capped'] = float(p['capped'])
                v[mode+'_output_tokens'] = len(p['output_tokens'])
                v[mode+'_agrees_reconstruction'] = float(p['answer'] in top) if p['valid'] else 0.
                v['reconstruction-minus-'+mode+'_lower'] = v['reconstruction_lower_correct']-v[mode+'_upper_correct']
                v['reconstruction-minus-'+mode+'_upper'] = v['reconstruction_upper_correct']-v[mode+'_lower_correct']
                v[mode+'_correct_reward_wrong'] = float(p['lower_correct'] and gold not in top)
                v[mode+'_wrong_reward_correct'] = float(p['stopped'] and p['valid'] and not p['lower_correct'] and top == [gold])
                info[mode+'_choice'] = p['answer']
                info[mode+'_stopped'] = p['stopped']
            v['COT-minus-DIRECT_lower'] = v['FORWARD_COT_lower_correct']-v['FORWARD_DIRECT_upper_correct']
            v['COT-minus-DIRECT_upper'] = v['FORWARD_COT_upper_correct']-v['FORWARD_DIRECT_lower_correct']
            values[uid] = v
            details[uid] = info
            disagreements.append(dict(model=model, item_id=uid, cluster_id=r['cluster_id'],
                                      modus=r['modus'], transition=r['transition'], **info))
        groups = {'all': rows,
                  'AUTHOR_UPDATE_GOLD_c': [r for r in rows if r['ground_truth'] == 'c'],
                  'AUTHOR_MAINTAIN_GOLD_ab': [r for r in rows if r['ground_truth'] != 'c']}
        for field in ['ground_truth', 'modus', 'types_of_relation', 'transition', 'agreement_lv']:
            for x in sorted({r[field] for r in rows}):
                groups[field+':'+x] = [r for r in rows if r[field] == x]
        for stratum, rs in groups.items():
            for metric in next(iter(values.values())):
                panels.append(dict(model=model, stratum=stratum, metric=metric,
                                   **estimate(rs, [values[r['item_id']][metric] for r in rs], seed=93)))
            for mode in ['FORWARD_DIRECT', 'FORWARD_COT']:
                correct = [r for r in rs if values[r['item_id']][mode+'_lower_correct']]
                panels.append(dict(model=model, stratum=stratum, metric=mode+'_conditional_reward_accuracy_DIAGNOSTIC',
                                   **estimate(correct, [values[r['item_id']]['reconstruction_lower_correct'] for r in correct], seed=93),
                                   scope='Diagnostic conditional analysis only; all complete row cohort remains primary.'))
            raw.append(dict(model=model, stratum=stratum, rows=len(rs),
                            author_Gold_counts=dict(collections.Counter(r['ground_truth'] for r in rs)),
                            counts={m: sum(values[r['item_id']][m] for r in rs)
                                    for m in ['reconstruction_lower_correct', 'reconstruction_upper_correct', 'reconstruction_tie',
                                              'FORWARD_DIRECT_lower_correct', 'FORWARD_DIRECT_upper_correct', 'FORWARD_DIRECT_unknown', 'FORWARD_DIRECT_capped',
                                              'FORWARD_COT_lower_correct', 'FORWARD_COT_upper_correct', 'FORWARD_COT_unknown', 'FORWARD_COT_capped']},
                            forward_choices={mode: dict(collections.Counter(details[r['item_id']][mode+'_choice'] or 'UNKNOWN' for r in rs))
                                             for mode in ['FORWARD_DIRECT', 'FORWARD_COT']},
                            reconstruction_choices=dict(collections.Counter(details[r['item_id']]['reconstruction_choice'] for r in rs))))
        # Author BREU is the equal average of update/maintain, not conditional on initial success.
        for metric in ['reconstruction_lower_correct', 'reconstruction_upper_correct',
                       'FORWARD_DIRECT_lower_correct', 'FORWARD_DIRECT_upper_correct',
                       'FORWARD_COT_lower_correct', 'FORWARD_COT_upper_correct']:
            for operation in ['BREU_POINT_ROW_WEIGHTED']:
                parts = [[values[r['item_id']][metric] for r in groups[s]]
                         for s in ['AUTHOR_UPDATE_GOLD_c', 'AUTHOR_MAINTAIN_GOLD_ab']]
                point = sum(sum(x)/len(x) for x in parts)/2
                panels.append(dict(model=model, stratum='AUTHOR_BREU', metric=metric,
                                   operation=operation, value=point, CI95=[None, None],
                                   clusters=len({r['cluster_id'] for r in rows}), sources=len(rows),
                                   scope='Descriptive author row-weighted macro; per-stratum clustered CI above, no invented macro CI.'))
    out = root/output_name
    assert not out.exists()
    out.write_text(json.dumps(dict(panels=panels, disagreements=disagreements, descriptive_counts=raw, runs=provenance,
                                   data_sha256=sha(root/'data-v1.jsonl'), models=models,
                                   analysis_scope='Full preregistered panel' if selected_models is None else 'INTERIM complete model-family data, hypothesis generation only; original full panel continues.',
                                   statistics='All1744 original author rows; Source then atomic seed cluster bootstrap10000 seed93. Author row-weighted BREU separate; actual answers cap/unknown bounded. Conditional success strata are diagnostic only.',
                                   limits='Author pragmatic suppression Gold is not classical entailment truth. Fixed raw observation-reconstruction analogue; comparison of two prompt orderings does not certify one Bayes joint. Prior21 unmatched records retained, initial labels NA.'), indent=2)+'\n')
    m = dict(map_sha256=sha(out), gpu_hours=sum(r['gpu_hours'] for r in provenance), new_actual_outputs=len(rows)*2*len(models),
             new_reconstruction_scores=len(rows)*3*len(models), new_api_calls=0, panels=len(panels), models=models)
    (root/manifest_name).write_text(json.dumps(m, indent=2)+'\n')
    print('E93 COMPLETE', m, flush=True)


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
