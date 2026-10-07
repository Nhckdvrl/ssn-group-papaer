"""Apply eight completed anomaly rechecks without replacing original data or scores."""
import argparse
import collections
import copy
import json
from pathlib import Path

import numpy as np

from data import sha, write_jsonl
from analyze_correct_answer_carry import estimate
from analyze_reconstruction_reward import corr_ci
from analyze_observation_surface_reward import correlation


SEMANTIC = ['positive_retention', 'unsupported_assertion', 'semantic_fidelity',
            'positive_omission', 'positive_contradiction']


def metrics_from_atoms(row):
    labels = collections.defaultdict(list)
    for a in row['atoms']:
        labels[a['source_gold']].append(a['paraphrase_label'])
    def mean(g, predicate):
        return sum(predicate(x) for x in labels[g]) / len(labels[g]) if labels[g] else None
    pos = mean('Yes', lambda x: x == 'ENTAILED')
    over = mean('No', lambda x: x == 'ENTAILED')
    row.update(positive_retention=pos, unsupported_assertion=over,
               semantic_fidelity=None if pos is None or over is None else pos-over,
               positive_omission=mean('Yes', lambda x: x == 'NEITHER'),
               positive_contradiction=mean('Yes', lambda x: x == 'CONTRADICTED'))


def apply_atoms(row, source_text, source_labels, p_labels):
    changed = []
    for a in row['atoms']:
        q = a['question']
        if (source_text, q) in source_labels:
            new = 'Yes' if source_labels[source_text, q] == 'ENTAILED' else 'No'
            if new != a['source_gold']:
                changed.append(dict(question=q, field='source_gold', old=a['source_gold'], new=new))
                a['source_gold'] = new
        if (row['interpretation'], q) in p_labels:
            new = p_labels[row['interpretation'], q]
            if new != a['paraphrase_label']:
                changed.append(dict(question=q, field='paraphrase_label', old=a['paraphrase_label'], new=new))
                a['paraphrase_label'] = new
    metrics_from_atoms(row)
    return changed


def run(cache):
    audit = cache / 'E70/posthoc-semantic-spotcheck-v1'
    summary = json.loads((audit / 'step5/summary.json').read_text())
    assert summary['complete_both'] == 8 and summary['unresolved'] == 0
    annotation = {r['item_id']: r for r in map(json.loads, (audit / 'step5/annotated.jsonl').read_text().splitlines())}
    prior = {r['item_id']: r for r in map(json.loads, (audit / 'old-labels-v1.jsonl').read_text().splitlines())}
    source_labels, p_labels = {}, {}
    for packet in map(json.loads, (audit / 'packets-v1.jsonl').read_text().splitlines()):
        label = annotation[packet['item_id']]['step5_annotation']['label']
        target = source_labels if prior[packet['item_id']]['origin']['kind'] == 'source' else p_labels
        target[packet['sentence'], packet['question']] = label
    for name, old_map_name in [('E91', 'reconstruction-reward-map-v1.json'),
                               ('E92', 'observation-surface-reward-map-v1.json')]:
        root = cache / name
        rows = list(map(json.loads, (root / 'data-v1.jsonl').read_text().splitlines()))
        ledger = []
        for row in rows:
            old = {k: row[k] for k in SEMANTIC}
            source = row['sentence'] if name == 'E91' else row['original_sentence']
            changes = apply_atoms(row, source, source_labels, p_labels)
            if changes:
                ledger.append(dict(item_id=row['item_id'], source_unit=row['source_unit'],
                                   changes=changes, old_metrics=old, new_metrics={k: row[k] for k in SEMANTIC}))
        groups = collections.defaultdict(dict)
        for r in rows:
            groups[r['generator'], r['source_unit']][r['operation']] = r
        original = json.loads((root / old_map_name).read_text())
        records = copy.deepcopy(original['matched_records'])
        for r in records:
            pair = groups[r['generator'], r['source_unit']]
            b, t = pair['BASE_BANK'], pair['TARGET_BANK']
            for k in SEMANTIC:
                r['delta_' + k] = None if b[k] is None or t[k] is None else t[k] - b[k]
        panels = []
        for p in original['panels']:
            rs = [r for r in records if r['grader'] == p['grader'] and r['generator'] == p['generator']
                  and r['condition'] == p['condition']
                  and (p['construction'] == 'ALL' or r['construction'] == p['construction'])]
            assert len(rs) == p['counts']['sources']
            metrics, counts, correlations = {}, {}, {}
            for k, direction in [('semantic_fidelity', 1), ('positive_retention', 1), ('unsupported_assertion', -1),
                                 ('positive_omission', -1), ('positive_contradiction', -1)]:
                selected = [r for r in rs if r['delta_' + k] is not None]
                y = [direction * r['delta_' + k] for r in selected]
                seed = 91 if name == 'E91' else 92
                metrics['delta_' + k] = estimate(selected, [r['delta_' + k] for r in selected], seed=seed)
                versions = ['reward_sum'] if name == 'E91' else ['original', 'alternate']
                alignments = {}
                for version in versions:
                    score_key = 'delta_reward_sum' if name == 'E91' else 'delta_reward_mean_' + version
                    x = [r[score_key] for r in selected]
                    alignment = [float(np.sign(a) * np.sign(b)) for a, b in zip(x, y)]
                    alignments[version] = alignment
                    metrics[version + '_alignment_' + k] = estimate(selected, alignment, seed=seed)
                    metrics[version + '_reward_same_semantic_cohort_' + k] = estimate(selected, x, seed=seed)
                    counts[version + '_' + k] = dict(agrees=sum(a*b > 1e-12 for a, b in zip(x, y)),
                                                     opposes=sum(a*b < -1e-12 for a, b in zip(x, y)),
                                                     semantic_changed=sum(abs(v) > 1e-12 for v in y))
                    correlations[version + '_vs_' + k] = (corr_ci if name == 'E91' else correlation)(selected, x, y)
                if name == 'E92':
                    metrics['alignment_change_' + k] = estimate(selected, [b-a for a, b in zip(alignments['original'], alignments['alternate'])], seed=seed)
            panels.append({k: p[k] for k in ['grader', 'generator', 'construction', 'condition']} |
                          dict(metrics=metrics, counts=counts, correlations=correlations))
        result = dict(label='POST-HOC explicit semantic overlay; original main map unchanged',
                      original_data_sha256=sha(root / 'data-v1.jsonl'), original_map_sha256=sha(root / old_map_name),
                      recheck_annotations_sha256=sha(audit / 'step5/annotated.jsonl'),
                      altered_rows=len(ledger), changes=ledger, panels=panels, matched_records=records,
                      new_model_outputs=0, new_scores=0, new_api_calls=0, gpu_hours=0,
                      limits='Eight anomaly-targeted Step Plan rechecks; not population error estimate or independent human ground truth. Original E92 600-row common-Q eligibility frozen, previously excluded sources not reintroduced. All original scores and complete cohorts retained.')
        out = root / 'posthoc-semantic-overlay-map-v1.json'
        assert not out.exists()
        out.write_text(json.dumps(result, indent=2) + '\n')
        write_jsonl(root / 'data-posthoc-semantic-overlay-v1.jsonl', rows)
        print(json.dumps(dict(experiment=name, path=str(out), sha256=sha(out), changed_rows=len(ledger), panels=len(panels))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, required=True)
    run(parser.parse_args().cache)
