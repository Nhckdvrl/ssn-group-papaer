"""POST-HOC E91 additive token regions; no new scoring or syntax boundaries."""
import argparse
import collections
import json
from pathlib import Path

import numpy as np

from data import sha
from analyze_correct_answer_carry import estimate


def analyze(root):
    original = root / 'reconstruction-reward-map-v1.json'
    source = json.loads(original.read_text())
    index = {}
    for run in json.loads((root / 'runner-pids-v1.json').read_text()):
        p = Path(run['out'])
        cfg = json.loads((p / 'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(p / 'predictions.jsonl')
        for r in map(json.loads, (p / 'predictions.jsonl').read_text().splitlines()):
            k = run['model'], r['item_id']
            assert k not in index
            index[k] = r
    records = []
    regions = ['full', 'first_token', 'rest', 'q1', 'q2', 'q3', 'q4']
    for r in source['matched_records']:
        b = index[r['grader'], r['base_item_id']]['token_logprobs']
        t = index[r['grader'], r['target_item_id']]['token_logprobs']
        assert len(b) == len(t) and len(b) >= 4
        d = np.asarray(t) - np.asarray(b)
        assert abs(float(d.sum()) - r['delta_reward_sum']) < 1e-7
        cuts = [i * len(d) // 4 for i in range(5)]
        deltas = dict(full=float(d.sum()), first_token=float(d[0]), rest=float(d[1:].sum()))
        deltas.update({f'q{i+1}': float(d[cuts[i]:cuts[i+1]].sum()) for i in range(4)})
        assert abs(sum(deltas[f'q{i}'] for i in range(1, 5)) - deltas['full']) < 1e-7
        assert abs(deltas['first_token'] + deltas['rest'] - deltas['full']) < 1e-7
        records.append({**r, 'observation_tokens': len(d), 'regions': deltas})
    panels = []
    for grader in sorted({r['grader'] for r in records}):
        for generator in sorted({r['generator'] for r in records}):
            for construction in ['ALL', 'NPZ', 'MVRR', 'NPS']:
                for condition in ['gp', 'control']:
                    rs = [r for r in records if r['grader'] == grader and r['generator'] == generator
                          and r['condition'] == condition
                          and (construction == 'ALL' or r['construction'] == construction)]
                    if not rs:
                        continue
                    metrics = {}
                    for region in regions:
                        semantic = [r for r in rs if r['delta_semantic_fidelity'] is not None]
                        changed = [r for r in semantic if abs(r['delta_semantic_fidelity']) > 1e-12]
                        metrics[region] = dict(
                            reward_delta=estimate(rs, [r['regions'][region] for r in rs], seed=9108),
                            reward_delta_same_semantic_cohort=estimate(semantic, [r['regions'][region] for r in semantic], seed=9108),
                            alignment=estimate(semantic, [float(np.sign(r['regions'][region]) * np.sign(r['delta_semantic_fidelity'])) for r in semantic], seed=9108),
                            changed_semantic_sources=len(changed),
                            agrees=sum(r['regions'][region] * r['delta_semantic_fidelity'] > 1e-12 for r in changed),
                            opposes=sum(r['regions'][region] * r['delta_semantic_fidelity'] < -1e-12 for r in changed),
                            ties=sum(abs(r['regions'][region]) <= 1e-12 for r in changed))
                    panels.append(dict(grader=grader, generator=generator, construction=construction,
                                       condition=condition, sources=len(rs), metrics=metrics))
    result = dict(label='POST-HOC exploratory diagnosis; original main metrics unchanged',
                  original_map_sha256=sha(original), data_sha256=sha(root / 'data-v1.jsonl'),
                  scope='All original 972 pairs; no outcome filtering. Position quartiles are not syntactic boundaries.',
                  new_scores=0, new_api_calls=0, new_gpu_hours=0, records=records, panels=panels)
    out = root / 'posthoc-token-region-map-v1.json'
    assert not out.exists()
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(out=str(out), sha256=sha(out), panels=len(panels), records=len(records))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    analyze(parser.parse_args().root)
