"""E59: project a blind score superset onto finalized, predeclared data eligibility."""
import argparse
import collections
import json
import math
from pathlib import Path

from analyze_reading_map import load
from data import sha, write_jsonl


def qualify(data, run, out):
    metadata = {r['item_id']:r for r in load(data)}
    manifest = json.loads(data.with_suffix('.manifest.json').read_text())
    assert not manifest.get('blind_scoring'), 'Final semantic data required'
    cfg = json.loads((run/'config.json').read_text())
    assert cfg['predictions_sha256'] == sha(run/'predictions.jsonl')
    selected = []
    keys = set()
    counts = collections.Counter()
    for r in load(run/'predictions.jsonl'):
        if r['item_id'] not in metadata:
            counts['ineligible_original_tasks'] += 1
            continue
        m = metadata[r['item_id']]
        assert r['sentence_sha256'] == m['sentence_sha256'] and r['question'] == m['question']
        assert r['condition'] == m.get('analysis_condition',m['condition'])
        gold = m['options'][m['gold']] if r['scope'] == 'O2' else m['grounded_gold'] if r['scope'] == 'G2' else m['world_gold']
        r['candidate_gold'] = r['displayed_options'].index(gold)
        scores = r['candidate_logprobs']
        assert all(math.isfinite(v) for v in scores)
        denominator = max(scores) + math.log(sum(math.exp(v-max(scores)) for v in scores))
        r['correct'] = max(range(len(scores)),key=scores.__getitem__) == r['candidate_gold']
        r['p_correct'] = math.exp(scores[r['candidate_gold']]-denominator)
        r['literal_label'] = m['literal_label']
        r['source_gold_matches_grounding'] = m['source_gold_matches_grounding']
        r['cluster_id'] = m.get('analysis_cluster_id',m['cluster_id'])
        key = r['item_id'],r['scope'],r['readout'],r['reading'],r['mapping']
        assert key not in keys
        keys.add(key)
        selected.append(r)
        counts['qualified_tasks'] += 1
    expected = {(uid,scope,readout,reading,mapping) for uid in metadata for scope in ('O2','G2','W3')
        for readout in ('letters','words') for reading in ('R0','R1','R5')
        for mapping in range(6 if scope == 'W3' else 2)}
    assert keys == expected, 'Missing qualified tasks; never adopt a survivor subset'
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'predictions.jsonl').exists()
    write_jsonl(out/'predictions.jsonl',selected)
    original_cfg = dict(cfg)
    cfg.update(data_sha256=sha(data),tasks=len(selected),predictions_sha256=sha(out/'predictions.jsonl'),
        blind_score_source=dict(path=str(run),config_sha256=sha(run/'config.json'),
            score_data_sha256=original_cfg['data_sha256'],gpu_hours=original_cfg['gpu_hours']),
        qualification=dict(data_manifest_sha256=sha(data.with_suffix('.manifest.json')),
            counts=dict(counts),code_sha256=sha(Path(__file__)),
            policy='Finalized semantic/grammar/pair eligibility only; all model outcomes retained, no performance-based selection.'),
        gpu_hours=0,blind_scoring=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (out/'qualify_source_scope_run.py').write_bytes(Path(__file__).read_bytes())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('data','run','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    qualify(args.data,args.run,args.out)
