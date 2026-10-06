"""Compare frozen runs with public scores or another precision, without filtering."""
import argparse
import collections
import csv
import json
import math
from pathlib import Path
import sys
import numpy as np
from data import CACHE, sha


def predictions(directory):
    config = json.loads((directory/'config.json').read_text())
    assert config['predictions_sha256'] == sha(directory/'predictions.jsonl')
    return config, [json.loads(line) for line in (directory/'predictions.jsonl').read_text().splitlines()]


def compare(values):
    if not values: return {'n': 0}
    delta = np.array([abs(a-b) for a, b in values])
    return dict(n=len(values), flips=sum((a > .5) != (b > .5) for a, b in values),
                mean_abs_probability_delta=float(delta.mean()), max_abs_probability_delta=float(delta.max()),
                quantiles=dict(zip(('p50', 'p90', 'p99'), map(float, np.quantile(delta, [.5, .9, .99])))))


def public(directory, data):
    config, records = predictions(directory)
    metadata = {r['item_id']: r for r in data}
    model = Path(config['model_path']).name
    reference = collections.defaultdict(list)
    invalid_public = collections.Counter()
    csv.field_size_limit(sys.maxsize)
    for path in sorted((CACHE/'upstream/amouyal/results/llm_results').glob('*.csv')):
        with path.open(newline='') as stream:
            for r in csv.DictReader(stream):
                if r['model'].split('/')[-1] != model or r['compute_type'] != 'regular': continue
                key = r['sentence'], r['question'], r['order'], int(r['prompt_index'])
                try:
                    score = float(r['correct']);incorrect=float(r['incorrect'])
                    if not math.isfinite(score+incorrect) or score+incorrect==0:score=float('nan')
                except (ValueError, TypeError): score = float('nan')
                if not math.isfinite(score): invalid_public[key] += 1
                else: reference[key].append(score)
    values = []; unmatched = 0; missing = 0; ambiguous = 0
    per_construction = collections.defaultdict(list)
    for record in records:
        row = metadata[record['item_id']]
        key = row['sentence'], row['question'], record['order'], record['prompt_index']
        matches = reference.get(key)
        if not matches: unmatched += 1; continue
        if record['p_correct'] is None: missing += 1; continue
        if len(set(matches)) > 1: ambiguous += 1
        # Preserve all published matching observations; don't select a favorable one.
        for score in matches:
            pair = record['p_correct'], score
            values.append(pair); per_construction[row['construction']].append(pair)
    return dict(model=model, configuration_sha256=sha(directory/'config.json'),
                overall=compare(values), construction={k: compare(v) for k, v in per_construction.items()},
                unmatched_predictions=unmatched, missing_model_scores=missing, ambiguous_public_matches=ambiguous,
                invalid_published_scores=sum(invalid_public.values()),
                limitation='Public generate() may sample up to 3 tokens. This comparator uses the first processed step; missing first-step aliases and unavailable sampled prefixes remain instrument failures.')


def precision(a, b, subset=False):
    config_a, records_a = predictions(a); config_b, records_b = predictions(b)
    assert config_a['data_sha256'] == config_b['data_sha256']
    fields = ('item_id', 'format', 'reading', 'order', 'prompt_index', 'mapping', 'repair', 'prompt_sha256')
    def keyed(rows):
        out = {tuple(r[f] for f in fields): r for r in rows}
        assert len(out) == len(rows), 'Duplicate prediction keys'
        return out
    aa, bb = keyed(records_a), keyed(records_b)
    assert bb.keys() <= aa.keys() if subset else aa.keys() == bb.keys()
    values = [(aa[k]['p_correct'], bb[k]['p_correct']) for k in bb if aa[k]['p_correct'] is not None and bb[k]['p_correct'] is not None]
    construction = collections.defaultdict(list)
    for k in bb:
        if aa[k]['p_correct'] is not None and bb[k]['p_correct'] is not None:
            construction[bb[k]['construction']].append((aa[k]['p_correct'], bb[k]['p_correct']))
    return dict(overall=compare(values), construction={k:compare(v) for k,v in construction.items()},
                missing=len(bb)-len(values), baseline_other_tasks=len(aa)-len(bb),
                configurations=[sha(a/'config.json'), sha(b/'config.json')])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--runs', type=Path, nargs='+', required=True)
    parser.add_argument('--data', type=Path); parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--precision', action='store_true')
    parser.add_argument('--subset', action='store_true', help='Second run is a preregistered task subset of the first.')
    args = parser.parse_args()
    if args.precision:
        assert len(args.runs) == 2
        result = precision(*args.runs, subset=args.subset)
    else:
        data = [json.loads(line) for line in args.data.read_text().splitlines()]
        result = [public(r, data) for r in args.runs]
    args.out.write_text(json.dumps(result, indent=2)+'\n'); print(json.dumps(result))
