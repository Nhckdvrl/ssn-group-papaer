"""E52 secondary reuse of every released model; no paid model calls.

Published processed-choice scores retain their protocol limitations. They do not
stand in for our native candidate scoring or generated final-answer accuracy.
"""
import argparse
import collections
import csv
import json
import math
from pathlib import Path
import sys

from analyze_reading_map import estimate, load
from data import CACHE, sha


def analyze(data, root, out):
    metadata = [r for r in load(data) if r['source'] == 'amouyal']
    lookup = collections.defaultdict(list)
    for row in metadata:
        lookup[(row['sentence'], row['question'], row['source_sent_type'],
                row['source_question_type'])].append(row)
    assert all(len(rows) == 1 for rows in lookup.values()), 'Ambiguous source match'
    scores = collections.defaultdict(list)
    counts = collections.Counter()
    files = []
    csv.field_size_limit(sys.maxsize)
    for path in sorted(root.glob('*.csv')):
        files.append(dict(path=str(path), sha256=sha(path)))
        with path.open(newline='') as stream:
            for index, record in enumerate(csv.DictReader(stream)):
                counts['released_rows'] += 1
                key = (record['sentence'], record['question'], record['sent_type'],
                       record['quest_type'])
                matches = lookup.get(key)
                if not matches:
                    counts['unmatched_source_rows'] += 1
                    continue
                try:
                    correct, incorrect = float(record['correct']), float(record['incorrect'])
                    valid = (math.isfinite(correct + incorrect) and
                             0 <= correct <= 1 and 0 <= incorrect <= 1 and
                             correct + incorrect > 0)
                except (ValueError, TypeError):
                    valid = False
                if not valid:
                    counts['invalid_or_zero_choice_mass'] += 1
                    continue
                row = matches[0]
                scores[(record['model'], record['compute_type'], row['item_id'])].append(
                    dict(correct=float(correct > incorrect),
                         p_correct=correct / (correct + incorrect)))
                counts['valid_matched_rows'] += 1
    pairs = collections.defaultdict(list)
    for row in metadata:
        pairs[(row.get('analysis_pair_id', row['pair_id']), row['question'])].append(row)
    summaries = {}
    for model, compute in sorted({(m, c) for m, c, _ in scores}):
        panel = {}
        for construction in sorted({r['construction'] for r in metadata}):
            for stratum in ('genuine', 'NEITHER', 'initial_all', 'final', 'nonrevision'):
                def eligible(row):
                    if row['construction'] != construction:
                        return False
                    target = row.get('analysis_question_target', row['question_target'])
                    if stratum == 'genuine':
                        return row['genuine']
                    if stratum == 'NEITHER':
                        return target == 'initial' and row['semantic_stratum'] == 'NEITHER'
                    if stratum == 'initial_all':
                        return target == 'initial'
                    if stratum == 'final':
                        return target == 'final'
                    return not row['needs_revision']
                selected = []
                for group in pairs.values():
                    if not all(eligible(r) and (model, compute, r['item_id']) in scores
                               for r in group):
                        continue
                    if {r.get('analysis_condition', r['condition']) for r in group} != {'gp', 'control'}:
                        continue
                    selected.append(group)
                for metric in ('correct', 'p_correct'):
                    cluster_cells = collections.defaultdict(lambda: collections.defaultdict(list))
                    for group in selected:
                        question_cells = collections.defaultdict(list)
                        for row in group:
                            values = scores[(model, compute, row['item_id'])]
                            condition = row.get('analysis_condition', row['condition'])
                            question_cells[condition].append(sum(v[metric] for v in values) / len(values))
                        cluster = group[0].get('analysis_cluster_id', group[0]['cluster_id'])
                        for condition in ('gp', 'control'):
                            cluster_cells[condition][cluster].append(
                                sum(question_cells[condition]) / len(question_cells[condition]))
                    cells = {condition: {cluster: sum(v) / len(v) for cluster, v in groups.items()}
                             for condition, groups in cluster_cells.items()}
                    common = cells.get('gp', {}).keys() & cells.get('control', {}).keys()
                    gap = {k: cells['control'][k] - cells['gp'][k] for k in common}
                    panel[f'{construction}/{stratum}/{metric}'] = dict(
                        question_pairs=len(selected),
                        cells={c: estimate(v) for c, v in cells.items()}, gap=estimate(gap))
        summaries[f'{model}/{compute}'] = panel
    report = dict(data_sha256=sha(data), source_files=files, counts=dict(counts),
                  models=summaries,
                  protocol='Released processed-choice scores; all matching observations retained. Ties count as no strict correct-choice preference.',
                  interpretation='Secondary published convention map. NEITHER/initial_all are task agreement, not literal semantic accuracy; no native-score replication or causal inference is claimed.')
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=CACHE/'upstream/amouyal/results/llm_results')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    analyze(args.data, args.root, args.out)
