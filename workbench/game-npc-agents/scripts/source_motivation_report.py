#!/usr/bin/env python3
"""Summarize extractive source DATA without turning labels into gold actions."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    collection = json.loads((args.run / 'collection.json').read_text())
    mapping = json.loads((args.run / 'private_mapping.json').read_text())
    labels = json.loads((args.run / 'derived_valid_labels.json').read_text())
    cases = {r['case_id']: r for r in map(json.loads, args.dataset.read_text().splitlines())}
    assert len(labels) == collection['valid_rows'] == len(cases) == 200
    assert not collection['missing_ids']
    assert {mapping[r['annotation_id']] for r in labels} == set(cases)
    joined = []
    for label in labels:
        cid = mapping[label['annotation_id']]
        case = cases[cid]
        joined.append({'case_id': cid, 'graph_sha256': case['graph_sha256'],
                       'goal_kind': case['goal_kind'], 'character': case['quest']['character'],
                       'goal_command': case['goal_command'], 'request_command': case['request_command'],
                       'label_source': collection['label_sources'][label['annotation_id']],
                       'annotation': label})
    counts = {}
    for group in ['all', 'give', 'other_verbs']:
        selected = [r for r in joined if group == 'all' or
                    (r['goal_kind'] == 'give') == (group == 'give')]
        counts[group] = {'worlds': len(selected),
            'motivation_levels': {level: dict(Counter(r['annotation']['motivation_levels'][level]['scope']
                                   for r in selected))
                                   for level in ['short_motivation','mid_motivation','long_motivation']},
            'request_support_claim': dict(Counter(r['annotation']['support_claim'] for r in selected))}
    report = {'source': str(args.run), 'dataset_sha256': hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
              'labels_sha256': hashlib.sha256((args.run / 'derived_valid_labels.json').read_bytes()).hexdigest(),
              'counts': counts, 'cases': joined, 'requests_completed': collection['requests_completed'],
              'provider_total_tokens': collection['total_tokens'],
              'retained_rejected_rows': len(collection['rejected_raw_rows']),
              'layout_normalizations': len(collection['layout_normalizations']),
              'scope': [
                  'Step-5-preview blind extractive text labels; native outcomes and persona/model conditions hidden.',
                  'Every non-unspecified scope is supported by a literal quote; semantic annotation is not independently human-validated.',
                  'Beneficiary categories describe authored purposes, not true utility or a unique correct action.',
                  'Support_claim labels what the requester says, not whether support occurs or private knowledge was legitimately available.',
                  'Same-verb and other-verb populations differ in authored motives and relations; counts are descriptive, not causal group comparisons.',
                  'All 200 fixed worlds retained, original failed responses and explicit layout aliases preserved.'
              ]}
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k in ['counts','requests_completed','provider_total_tokens']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
