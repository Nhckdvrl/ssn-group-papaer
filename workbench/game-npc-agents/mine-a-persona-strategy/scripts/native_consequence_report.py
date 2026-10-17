#!/usr/bin/env python3
"""E74 complete graph-paired physical forecasts, value substitution and outcomes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np

from native_consequence_choice import KINDS
from native_request_precondition_report import metrics as action_metrics
from native_rule_cross_report import summarize
from native_request_precondition_execution import SEEDS


def prediction_metrics(row):
    pred = row['prediction']; truth = row['truth']; layout = row['layout']
    result = {'protocol_ok': float(pred is not None), 'all_sequences_correct': float(pred == truth)}
    for kind in KINDS:
        q = next(q for q, k in layout.items() if k == kind)
        expected = truth[q]; actual = pred.get(q, {}) if isinstance(pred, dict) else {}
        result[kind+'/exact'] = float(actual == expected)
        for field in ['owner', 'equipped', 'authored_give_executed']:
            result[kind+'/'+field] = float(actual.get(field) == expected[field])
    result['remove_and_goal_path_correct'] = result['remove/exact']*result['remove_give_A/exact']
    for field in ['owner', 'equipped', 'authored_give_executed']:
        result['mean_'+field+'_accuracy'] = np.mean([result[k+'/'+field] for k in KINDS])
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, nargs='+', required=True)
    ap.add_argument('--baseline-run', type=Path, required=True)
    ap.add_argument('--candidate-runs', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    forecasts = {}; episodes = {}; hashes = {}; calls = Counter(); runtime_hours = 0.
    model = json.loads((args.runs[0]/'manifest.json').read_text())['model']
    confusions = {}
    for folder in args.runs:
        assert (folder/'runtime.json').exists()
        assert json.loads((folder/'manifest.json').read_text())['model'] == model
        rt = json.loads((folder/'runtime.json').read_text())
        runtime_hours += (rt['wall_seconds']+rt['model_load_seconds'])/3600
        for row in map(json.loads, (folder/'predictions.jsonl').open()):
            k = row['case_id'], row['seed'], row['persona'], row['information']
            assert k not in forecasts; forecasts[k] = row
            label = row['persona']+'/'+row['information']; bucket = confusions.setdefault(label, {})
            for q, kind in row['layout'].items():
                actual = row['prediction'].get(q, {}) if isinstance(row['prediction'], dict) else {}
                for field, truth in row['truth'][q].items():
                    key = kind+'/'+field+'/'+json.dumps(truth)+'->'+json.dumps(actual.get(field))
                    bucket[key] = bucket.get(key, 0)+1
        for row in map(json.loads, (folder/'episodes.jsonl').open()):
            k = row['case_id'], row['seed'], row['persona'], row['condition']
            assert k not in episodes; episodes[k] = row
        for row in map(json.loads, (folder/'model_calls.jsonl').open()):
            calls.update(count=1, parse_errors=int(bool(row['parse_error'])), prompt_tokens=row['prompt_tokens'],
                         completion_tokens=row['completion_tokens'])
        for name in ['predictions.jsonl', 'episodes.jsonl', 'model_calls.jsonl']:
            hashes[str(folder/name)] = hashlib.sha256((folder/name).read_bytes()).hexdigest()
    cids = sorted({k[0] for k in forecasts}); assert len(cids) == 117
    assert len(forecasts) == len(episodes) == 1404
    context_sources = [('divert_initial_feedback', [args.baseline_run]),
                       ('divert_valid_candidates', args.candidate_runs)]
    baseline = {}
    for condition, folders in context_sources:
        for folder in folders:
            assert json.loads((folder/'manifest.json').read_text())['model'] == model
            for row in map(json.loads, (folder/'episodes.jsonl').open()):
                if row['condition'] != condition: continue
                k = row['case_id'], row['seed'], row['persona'], condition
                assert k not in baseline; baseline[k] = row
            hashes[str(folder/'episodes.jsonl')] = hashlib.sha256((folder/'episodes.jsonl').read_bytes()).hexdigest()
    assert len(baseline) == 1404
    for cid in cids:
        for seed in SEEDS:
            for p in ['firm', 'agreeable']:
                for info in ['divert_no_information', 'divert_initial_feedback']:
                    f = forecasts[cid, seed, p, info]
                    ref = baseline[cid, seed, p, 'divert_initial_feedback']
                    assert f['conversation'] == ref['conversation']
                for condition in ['divert_self_forecast', 'divert_native_forecast']:
                    assert episodes[cid, seed, p, condition]['conversation'] == ref['conversation']
    pvals = {k: prediction_metrics(row) for k, row in forecasts.items()}
    avals = {k: action_metrics(row) for k, row in episodes.items()}
    avals.update({k: action_metrics(row) for k, row in baseline.items()})
    def estimate(lookup, terms):
        fields = list(next(iter(lookup.values())))
        arrays = [np.mean([[sum(w*lookup[cid,s,p,c][f] for w,p,c in terms) for f in fields]
                           for s in SEEDS],axis=0) for cid in cids]
        return summarize(arrays, fields)
    pcells = {}; pcontrasts = {}; acells = {}; acontrasts = {}
    for info in ['divert_no_information', 'divert_initial_feedback']:
        for p in ['firm', 'agreeable']: pcells[p+'/'+info] = estimate(pvals, [(1,p,info)])
        pcontrasts['A_minus_F/'+info] = estimate(pvals, [(1,'agreeable',info),(-1,'firm',info)])
    for p in ['firm', 'agreeable']:
        pcontrasts[p+'/feedback_minus_none'] = estimate(pvals, [(1,p,'divert_initial_feedback'),(-1,p,'divert_no_information')])
    for condition in ['divert_initial_feedback','divert_valid_candidates','divert_self_forecast','divert_native_forecast']:
        for p in ['firm', 'agreeable']: acells[p+'/'+condition] = estimate(avals, [(1,p,condition)])
        acontrasts['A_minus_F/'+condition] = estimate(avals, [(1,'agreeable',condition),(-1,'firm',condition)])
    for p in ['firm','agreeable']:
        for a,b in [('native_forecast','self_forecast'),('native_forecast','initial_feedback'),('self_forecast','initial_feedback')]:
            acontrasts[p+'/'+a+'_minus_'+b] = estimate(avals, [(1,p,'divert_'+a),(-1,p,'divert_'+b)])
    acontrasts['persona_x_native_minus_self'] = estimate(avals, [(1,'agreeable','divert_native_forecast'),(-1,'firm','divert_native_forecast'),
                                                               (-1,'agreeable','divert_self_forecast'),(1,'firm','divert_self_forecast')])
    joint = {}; table_matches = 0
    for info in ['divert_no_information','divert_initial_feedback']:
        ref = 'divert_valid_candidates' if info == 'divert_no_information' else info
        for p in ['firm','agreeable']:
            count = Counter()
            for cid in cids:
                for seed in SEEDS:
                    good = bool(pvals[cid,seed,p,info]['remove_and_goal_path_correct'])
                    a = avals[cid,seed,p,ref]
                    outcome = next(label for field,label in [('to_goal','goal'),('to_competitor','peer'),('to_other','other'),('no_transfer','no_transfer')] if a[field])
                    count[('correct_path' if good else 'wrong_path')+'/'+outcome] += 1
                    count[('correct_path' if good else 'wrong_path')+'/first_remove' if a['first_necessary_step'] else
                          ('correct_path' if good else 'wrong_path')+'/no_first_remove'] += 1
            joint[p+'/'+info] = dict(count)
    for cid in cids:
        for seed in SEEDS:
            for p in ['firm','agreeable']:
                f = forecasts[cid,seed,p,'divert_initial_feedback']
                if f['prediction'] == f['truth']:
                    table_matches += 1
                    a = episodes[cid,seed,p,'divert_self_forecast']; b = episodes[cid,seed,p,'divert_native_forecast']
                    assert a['history'] == b['history'], ('equal tables produced different paths',cid,seed,p)
    result = {'status':'COMPLETE','experiment':'E74','model':model,'worlds':117,
              'prediction_contexts':1404,'new_execution_branches':1404,
              'prediction_cells':pcells,'prediction_contrasts':pcontrasts,
              'execution_cells':acells,'execution_contrasts':acontrasts,
              'joint_forecast_and_unmodified_baseline':joint,'forecast_field_confusions':confusions,
              'identical_self_native_tables_and_paths':table_matches,'actual_calls':dict(calls),
              'shard_runtime_gpu_hours':runtime_hours,'source_sha256':hashes,
              'scope':['Forecasts are elicited physical predictions, not direct measurements of hidden belief.',
                       'Self/native substitution keeps commands, labels, structure and order fixed; only prediction values change.',
                       'No-table baseline comparison includes extra action-chain salience and scaffolding.',
                       'Joint correctness/outcome slices are descriptive and do not identify a causal preference among survivors.',
                       'Same 117 explored worlds, three seeds; first exact-source-item Give, not total private utility.']}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','worlds','prediction_contexts','new_execution_branches','actual_calls','identical_self_native_tables_and_paths']}))


if __name__ == '__main__': main()
