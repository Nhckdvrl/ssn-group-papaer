#!/usr/bin/env python3
"""POST-HOC E75-to-E77 off-diagonal prediction; no models, no tuned parameters.

Added after the first E77 profile, not an original preregistered endpoint.
Prepare reads only E75; score requires all four full E77 runtimes completed.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

import native_dialogue_outcome_report as reviewer

PERSONAS = ['firm', 'agreeable']
MODELS = ['gemma', '32b']
SEEDS = [7501, 7502, 7503]
LABELS = ['no_successful_get', 'get_then_physical_goal', 'get_then_request',
          'get_then_other_source_give', 'get_without_decisive_use']
PREDICTORS = ['current_exec_trait', 'dialogue_source_trait', 'equal_mixture']
ALPHA = 0.5
BOOTSTRAPS = 4000
BOOTSTRAP_SEED = 770075
DESIGN = {
    'status': 'FIXED_POST_HOC',
    'registration_timing': 'After the first E77 profile and full launch; before reading full E77 off-diagonal outcomes for this analysis.',
    'source': 'Per-model/per-world/per-trait E75 retrieval_baseline three-seed diagonal five-category frequencies only.',
    'labels': LABELS, 'dirichlet_alpha_each_category': ALPHA,
    'probability': '(category_count + 0.5) / (3 + 5*0.5)',
    'predictors': {'current_exec_trait': 'Use the old diagonal distribution of the current execution trait.',
                   'dialogue_source_trait': 'Use the old diagonal distribution of the donor conversation trait.',
                   'equal_mixture': 'Arithmetic mean of those two old diagonal distributions, weights fixed at 0.5/0.5.'},
    'scored_data': 'Only the two E77 free off-diagonals: donor != exec trait, all three original seeds.',
    'primary_explanatory_subset': 'All dataset rows except the first row used in the E77 profile; exclusion depends only on source order.',
    'additional_descriptive_subset': 'All 102 source graphs, including the profile graph.',
    'groups': ['all', 'source_give', 'source_use'],
    'loss': {'brier': 'sum over five categories of (p_k - indicator_k)^2, range 0..2, lower is better',
             'log_loss': '-log(p_observed) using natural logarithm, lower is better'},
    'aggregation': 'Average the two off-diagonals and three seeds within source graph, then average graphs.',
    'uncertainty': '4000 paired source-graph bootstrap samples, percentile 95% pointwise intervals, seed 770075.',
    'interpretation': 'Prediction of new C x current-trait combinations on already seen worlds; not new-world generalization, neural modularity, or independent replication.',
    'no_tuning': 'No optimization, fitted mixture weights, selected seeds, outcome-based exclusion, or E77 parameter fitting.'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label(row):
    """Reuse the reviewer's source-bound physical sensitivity verbatim."""
    v = reviewer.metrics(row)
    values = [1-v['retrieved'], v['physical_goal'], v['request'],
              v['other_source_give'], v['physical_retrieved_without_decisive']]
    assert sum(values) == 1 and all(x in [0, 1] for x in values)
    assert not (v['physical_goal'] or v['request'] or v['other_source_give']) or v['retrieved']
    return values.index(1)


def sources(args):
    data = args.runs_root / 'e75_native_retrieval_qualification/snapshots.jsonl'
    rows = list(map(json.loads, data.open()))
    assert len(rows) == 102
    cids = [r['case']['case_id'] for r in rows]
    kinds = {r['case']['case_id']: r['case']['goal_kind'] for r in rows}
    assert Counter(kinds.values()) == Counter(give=71, wear=12, eat=9, drink=10)
    originals, hashes, distributions = {}, {str(data): sha(data)}, {}
    for model in MODELS:
        old = {}
        for shard in ['s0', 's1']:
            folder = args.runs_root / f'e75_{model}_{shard}'
            assert (folder / 'runtime.json').exists()
            manifest = json.loads((folder / 'manifest.json').read_text())
            assert manifest['experiment'] == 'E75' and not manifest['profile']
            assert manifest['data_sha256'] == sha(data)
            for filename in ['episodes.jsonl', 'manifest.json', 'runtime.json']:
                hashes[str(folder / filename)] = sha(folder / filename)
            for row in map(json.loads, (folder / 'episodes.jsonl').open()):
                if row['condition'] != 'retrieval_baseline':
                    continue
                key = row['case_id'], row['seed'], row['persona']
                assert key not in old
                old[key] = row
        assert set(old) == {(c, s, p) for c in cids for s in SEEDS for p in PERSONAS}
        originals[model] = old
        distributions[model] = {}
        for cid in cids:
            distributions[model][cid] = {}
            for persona in PERSONAS:
                counts = [0] * len(LABELS)
                for seed in SEEDS:
                    counts[label(old[cid, seed, persona])] += 1
                probs = [(n + ALPHA) / (len(SEEDS) + len(LABELS)*ALPHA) for n in counts]
                assert abs(sum(probs)-1) < 1e-12 and min(probs) > 0
                distributions[model][cid][persona] = {'counts': counts, 'probabilities': probs}
    return cids, kinds, originals, hashes, distributions


def payload(args, cids, kinds, hashes, distributions):
    predictions = {}
    for model in MODELS:
        predictions[model] = {}
        for cid in cids:
            predictions[model][cid] = {}
            for exec_trait in PERSONAS:
                donor_trait = next(p for p in PERSONAS if p != exec_trait)
                ep = distributions[model][cid][exec_trait]['probabilities']
                cp = distributions[model][cid][donor_trait]['probabilities']
                predictions[model][cid][exec_trait] = {
                    'conv_persona': donor_trait,
                    'probabilities': {'current_exec_trait': ep, 'dialogue_source_trait': cp,
                                      'equal_mixture': [(a+b)/2 for a, b in zip(ep, cp)]}}
    return {'design': DESIGN, 'design_sha256': hashlib.sha256(canonical(DESIGN).encode()).hexdigest(),
            'script_sha256': sha(Path(__file__)), 'review_metrics_sha256': sha(Path(reviewer.__file__)),
            'source_sha256': hashes, 'case_ids_in_original_order': cids, 'goal_kinds': kinds,
            'profile_case_excluded_from_primary_explanation': cids[0],
            'source_distributions': distributions, 'fixed_offdiagonal_predictions': predictions}


def interval(point, draws):
    return {'estimate': float(point), 'ci95': [float(x) for x in np.quantile(draws, [.025, .975])]}


def summarize(scores, observed, cids):
    matrix = np.asarray([scores[c] for c in cids], dtype=float)
    assert matrix.shape == (len(cids), 3, 2)
    ix = np.random.default_rng(BOOTSTRAP_SEED).integers(0, len(cids), (BOOTSTRAPS, len(cids)))
    result = {'worlds': len(cids), 'offdiagonal_episodes': len(cids)*6,
              'observed_category_counts': dict(Counter(LABELS[y] for c in cids for y in observed[c])),
              'predictor_losses': {}, 'paired_loss_contrasts': {}}
    for i, predictor in enumerate(PREDICTORS):
        result['predictor_losses'][predictor] = {
            field: interval(matrix[:, i, j].mean(), matrix[ix, i, j].mean(axis=1))
            for j, field in enumerate(['brier', 'log_loss'])}
    for ai, bi in [(0, 1), (2, 0), (2, 1)]:
        delta = matrix[:, ai] - matrix[:, bi]
        result['paired_loss_contrasts'][PREDICTORS[ai] + '_minus_' + PREDICTORS[bi]] = {
            field: interval(delta[:, j].mean(), delta[ix, j].mean(axis=1))
            for j, field in enumerate(['brier', 'log_loss'])}
    return result


def score(args, frozen, originals):
    result, hashes = {}, {}
    cids = frozen['case_ids_in_original_order']; kinds = frozen['goal_kinds']
    for model in MODELS:
        rows = {}; total = 0
        for shard in ['s0', 's1']:
            folder = args.runs_root / f'e77_{model}_{shard}'
            if not (folder / 'runtime.json').exists():
                return None, {'awaiting_runtime': str(folder / 'runtime.json')}
            manifest = json.loads((folder / 'manifest.json').read_text())
            assert manifest['experiment'] == 'E77' and not manifest['profile']
            for filename in ['episodes.jsonl', 'manifest.json', 'runtime.json']:
                hashes[str(folder / filename)] = sha(folder / filename)
            for row in map(json.loads, (folder / 'episodes.jsonl').open()):
                total += 1
                if row['assigned_outcome'] is not None or row['conv_persona'] == row['persona']:
                    continue
                cid, seed, p = (row[k] for k in ['case_id', 'seed', 'persona'])
                assert row['condition'] == 'dialogue_' + row['conv_persona']
                assert row['conversation'] == originals[model][cid, seed, row['conv_persona']]['conversation']
                ref = originals[model][cid, seed, p]
                for field in ['goal_item_id', 'actor_id', 'native_goal_identity', 'goal_kind', 'state', 'support']:
                    assert row[field] == ref[field]
                key = cid, seed, p
                assert key not in rows; rows[key] = row
        assert total == 2448
        assert set(rows) == {(c, s, p) for c in cids for s in SEEDS for p in PERSONAS}
        scores, observed = {}, {}
        for cid in cids:
            losses = []; outcomes = []
            for seed in SEEDS:
                for p in PERSONAS:
                    y = label(rows[cid, seed, p]); outcomes.append(y)
                    onehot = np.eye(len(LABELS))[y]
                    predictions = frozen['fixed_offdiagonal_predictions'][model][cid][p]['probabilities']
                    losses.append([[float(np.sum((np.asarray(predictions[m])-onehot)**2)),
                                    float(-np.log(predictions[m][y]))] for m in PREDICTORS])
            scores[cid] = np.mean(losses, axis=0)
            observed[cid] = outcomes
        result[model] = {}
        for subset, ids in [('all_102_descriptive', cids), ('exclude_profile_101_primary_explanatory', cids[1:])]:
            result[model][subset] = {}
            for group, selected in [('all', ids), ('source_give', [c for c in ids if kinds[c] == 'give']),
                                    ('source_use', [c for c in ids if kinds[c] != 'give'])]:
                result[model][subset][group] = summarize(scores, observed, selected)
    return result, hashes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['prepare', 'score'])
    ap.add_argument('--runs-root', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[1] / 'results/E77_dialogue_outcome_predictions_POST_HOC.json')
    args = ap.parse_args()
    frozen_path = args.runs_root / 'e77_dialogue_outcome_predictions_frozen.json'
    cids, kinds, originals, hashes, distributions = sources(args)
    frozen = payload(args, cids, kinds, hashes, distributions)
    if frozen_path.exists():
        saved = json.loads(frozen_path.read_text())
        created = saved.pop('created_utc')
        assert saved == frozen, 'Frozen design/source/metrics/script changed; do not silently update after seeing E77 outcomes.'
    else:
        assert args.mode == 'prepare', 'Prepare source-only predictions before scoring.'
        created = datetime.now(timezone.utc).isoformat()
        frozen_path.write_text(json.dumps({**frozen, 'created_utc': created}, ensure_ascii=False, indent=2)+'\n')
    report = {'status': 'SOURCE_PREDICTIONS_FROZEN_AWAITING_COMPLETE_E77', 'analysis': 'POST-HOC fixed competing predictions for E77 free off-diagonals',
        'model_calls': 0, 'gpu_hours': 0, 'design': DESIGN, 'design_sha256': frozen['design_sha256'],
        'frozen_cache_path': str(frozen_path), 'frozen_cache_sha256': sha(frozen_path),
        'frozen_created_utc': created, 'source_worlds': len(cids),
        'source_diagonal_episodes_per_model': 612,
        'profile_graph': cids[0], 'profile_exclusion_rule': 'First original data row, fixed before reading full E77 outcomes for this analysis.',
        'source_sha256': hashes, 'script_sha256': frozen['script_sha256'],
        'review_metrics_sha256': frozen['review_metrics_sha256'],
        'scope': ['Added after E77 initial profile; not an original preregistered primary endpoint or independent experiment.',
                  'Same source worlds and seeds; predictions address new intervention combinations, not new-world generalization.',
                  'Pure exec/C predictors are deliberately restrictive descriptive alternatives; winning either does not identify a brain module or exclusive causal mechanism.',
                  'Equal mixture has no optimized weight; alpha=0.5 fixed uniformly for all five categories.',
                  'Physical consumption secondary is reused from the review report; exact bound-goal main endpoint remains unchanged elsewhere.',
                  'Three source seeds produce noisy predictive distributions; score differences remain paired and pointwise, not an automatic scientific decision rule.']}
    if args.mode == 'score':
        scored, evaluation_hashes = score(args, frozen, originals)
        if scored is None:
            report['awaiting_completion'] = evaluation_hashes
        else:
            report.update(status='COMPLETE_POST_HOC', results=scored, evaluation_source_sha256=evaluation_hashes)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': report['status'], 'profile_graph': cids[0], 'frozen': str(frozen_path), 'out': str(args.out)}))


if __name__ == '__main__':
    main()
