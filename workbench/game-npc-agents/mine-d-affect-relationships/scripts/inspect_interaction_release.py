#!/usr/bin/env python3
"""Describe published MiniMax interaction assets; no generation or new scoring."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import pyarrow
import pyarrow.parquet as pq


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inspect(root, revision):
    result = dict(dataset='MiniMaxAI/role-play-bench', revision=revision,
                  license_declared='apache-2.0', pyarrow_version=pyarrow.__version__,
                  files={}, languages={}, new_model_calls=0)
    for language in ['en', 'zh']:
        tables = {}
        for name in ['seeds', 'dialogues', 'evaluations']:
            path = root / 'data' / language / (name + '.parquet')
            table = pq.read_table(path)
            result['files'][str(path.relative_to(root))] = dict(
                bytes=path.stat().st_size, sha256=sha(path),
                n_rows=table.num_rows, columns=table.column_names)
            tables[name] = table.to_pylist()
        seeds = {r['id'] for r in tables['seeds']}
        key = lambda r: (r['seed_id'], r['model_name'], r['run_id'])
        dialogues = [key(r) for r in tables['dialogues']]
        evaluations = [key(r) for r in tables['evaluations']]
        counts, roles, turns, reported = Counter(), Counter(), Counter(), Counter()
        anomalies = []
        for row in tables['dialogues']:
            reported[row['num_turns']] += 1
            try:
                content = json.loads(row['dialogue'])
            except (ValueError, TypeError):
                counts['unparsed_dialogue'] += 1
                continue
            if not isinstance(content, list) or not all(isinstance(t, dict) for t in content):
                counts['non_list_of_turn_objects'] += 1
                continue
            counts['parsed_dialogues'] += 1
            turns[len(content)] += 1
            counts['metadata_turn_count_mismatch'] += len(content) != row['num_turns']
            nonconsecutive = [t.get('round') for t in content] != list(range(len(content)))
            counts['nonconsecutive_round_numbers'] += nonconsecutive
            if nonconsecutive:
                anomalies.append(dict(key=key(row), kind='nonconsecutive_round_numbers',
                                      dialogue_field_sha256=hashlib.sha256(row['dialogue'].encode()).hexdigest()))
            for turn in content:
                roles[str(turn.get('role'))] += 1
                counts['non_string_turn_text'] += not isinstance(turn.get('text'), str)
        score_columns = [c for c in tables['evaluations'][0] if c.endswith('_score')]
        score_fields = {}
        for column in score_columns:
            values = [r[column] for r in tables['evaluations']]
            numeric = [v for v in values if type(v) in (float, int) and v == v]
            score_fields[column] = dict(n_numeric=len(numeric), minimum=min(numeric), maximum=max(numeric))
        result['languages'][language] = dict(
            n_seed_rows=len(tables['seeds']), n_unique_seeds=len(seeds),
            n_dialogues=len(dialogues), n_evaluations=len(evaluations),
            duplicate_dialogue_keys=len(dialogues)-len(set(dialogues)),
            duplicate_evaluation_keys=len(evaluations)-len(set(evaluations)),
            dialogue_evaluation_keys_equal=set(dialogues) == set(evaluations),
            unknown_seed_ids=sorted({k[0] for k in dialogues+evaluations}-seeds),
            by_model=dict(Counter(k[1] for k in dialogues)),
            runs=sorted({k[2] for k in dialogues}),
            trajectories_per_seed_histogram=dict(Counter(Counter(k[0] for k in dialogues).values())),
            reported_turn_counts=dict(reported), actual_turn_counts=dict(turns),
            turn_roles=dict(roles), structural_counts=dict(counts),
            structural_anomalies=anomalies,
            published_score_fields=score_fields,
        )
    result['scope'] = (
        'Provider-released synthetic model-on-model dialogues and existing scores; '
        'not our model runs, human player traces, or phase-labelled growth ground truth. '
        'Structural integrity only; no semantic failure rate or capability claim.'
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    result = inspect(Path(args.root), args.revision)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: {n: v[n] for n in ['n_unique_seeds', 'n_dialogues', 'actual_turn_counts', 'structural_counts', 'dialogue_evaluation_keys_equal']} for k, v in result['languages'].items()}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
