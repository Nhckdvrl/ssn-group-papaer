#!/usr/bin/env python3
"""E54 blind text labels joined after freezing; associations are not mechanisms."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--directory', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    labels_path = a.directory / 'labels_collected.json'
    labels = json.loads(labels_path.read_text()); mapping = json.loads((a.directory / 'private_mapping.json').read_text())
    assert len(mapping) == 720 and set(mapping) <= set(labels)
    sources = {}
    for entry in mapping.values():
        path = entry['source']
        if path not in sources:
            rows = list(map(json.loads, (Path(path) / 'branches.jsonl').read_text().splitlines()))
            sources[path] = {(r['case_id'], r['seed'], r['conv_persona'], r['channel']): r for r in rows
                            if r['control'] == 'none' and r['conv_persona'] == r['down_persona']}
    cells = defaultdict(list)
    for aid, entry in mapping.items():
        label = labels[aid]; index = sources[entry['source']]
        key = (entry['case_id'], entry['seed'], entry['persona'])
        model = Path(entry['source']).name.split('_')[1]
        actual = {ch: index[(*key, ch)]['flags']['request'] for ch in ['00', '10', '01', '11']}
        cells[model, entry['persona'], label['memory']['request_state']].append((key[0], actual, label))
    report = {'native_rows': 720, 'independent_graphs': 40, 'label_sha256': hashlib.sha256(labels_path.read_bytes()).hexdigest(),
              'cells': {}, 'usage': {}, 'scope': 'POST-HOC descriptive associations conditional on generated text; not causal effects of naturally completed memories.'}
    for key, values in sorted(cells.items()):
        grouped = defaultdict(list)
        for cid, actual, _ in values: grouped[cid].append(actual)
        rs = {'rows': len(values), 'graphs': len(grouped), 'stances': dict(Counter(v[2]['stance'] for v in values)),
              'request_rates': {ch: sum(v[1][ch] for v in values) / len(values) for ch in ['00', '10', '01', '11']}}
        rs['both_minus_plan_association'] = estimate([np.mean([float(v['11']) - float(v['10']) for v in vs]) for vs in grouped.values()])
        report['cells']['/'.join(key)] = rs
    metadata = []
    for p in list(a.directory.glob('labels_*')) + list((a.directory / 'recovery_medium64k').glob('labels_*')):
        if p.is_dir() and (p / 'metadata.json').exists(): metadata.append(json.loads((p / 'metadata.json').read_text()))
    report['usage'] = {'requests': len(metadata), 'http_status': dict(Counter(m.get('http_status') for m in metadata)),
        'finish_reason': dict(Counter(m.get('finish_reason') for m in metadata)),
        **{k: sum((m.get('usage') or {}).get(k, 0) for m in metadata) for k in ['prompt_tokens', 'completion_tokens', 'total_tokens']},
        'endpoint': 'https://api.stepfun.com/step_plan/v1/chat/completions', 'model': 'step-5-preview',
        'cash_endpoint_calls': 0, 'npc_cloud_calls': 0}
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'native_rows': 720, 'usage': report['usage'],
        'completed_memory_cells': {k: v for k, v in report['cells'].items() if k.endswith('/completed')}}))


if __name__ == '__main__': main()
