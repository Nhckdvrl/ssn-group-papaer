#!/usr/bin/env python3
"""Report final-run runtime costs and deduplicated provider-reported DATA usage."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', type=Path, required=True)
    ap.add_argument('--runs', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    endings = {51: 'status_pilot_complete', 52: 'binding_patch', 53: 'direct_status',
               55: 'independent_confirm', 56: 'state_action', 57: 'native_interaction',
               58: 'components', 59: 'fixed_history', 60: 'common_commitment',
               61: 'common_history_direct', 62: 'native_recipient'}
    local, grouped = [], defaultdict(lambda: {'gpu_hours': 0., 'reported_calls': 0})
    files = [f for e, end in endings.items() for f in sorted(args.results.glob(f'E{e}_*_{end}.json'))]
    files += sorted(args.results.glob('E62_*_recipient_probabilities.json'))
    for file in files:
        data = json.loads(file.read_text())
        runtimes = data.get('runtimes', [data.get('runtime', {})])
        seconds = sum(r.get('wall_seconds', 0) + r.get('model_load_seconds', r.get('load_seconds', 0))
                      for r in runtimes)
        calls = sum(r.get('calls', r.get('generation_calls', r.get('probability_readouts', 0)))
                    for r in runtimes)
        row = {'result': str(file), 'gpu_hours': seconds / 3600, 'reported_calls': calls,
               'capture_calls': sum(r.get('capture_calls', 0) for r in runtimes),
               'candidate_score_calls': sum(r.get('candidate_score_calls', 0) for r in runtimes)}
        local.append(row)
        group = file.name.split('_')[0]
        grouped[group]['gpu_hours'] += row['gpu_hours']
        grouped[group]['reported_calls'] += calls
    seen, usage, by_run = set(), [], defaultdict(lambda: {'requests': 0, 'total_tokens': 0})
    for run in sorted(args.runs.iterdir()):
        if not run.is_dir() or not run.name.startswith(('e50_step', 'e54_step', 'e59_', 'e61_source')):
            continue
        for file in sorted(run.rglob('response.json')):
            response = json.loads(file.read_text())
            if not response.get('usage'):
                continue
            identity = response.get('id') or hashlib.sha256(file.read_bytes()).hexdigest()
            if identity in seen:
                continue
            seen.add(identity)
            tokens = response['usage'].get('total_tokens', 0)
            usage.append({'response': str(file), 'provider_response_id': identity,
                          'total_tokens': tokens})
            by_run[run.name]['requests'] += 1
            by_run[run.name]['total_tokens'] += tokens
    report = {'local_final_results': local, 'local_by_experiment': dict(grouped),
              'e51_to_e61_final_gpu_hours': sum(v['gpu_hours'] for k, v in grouped.items() if k != 'E62'),
              'e62_final_gpu_hours': grouped['E62']['gpu_hours'],
              'step_data_usage_by_run': dict(by_run), 'step_responses_with_usage': len(usage),
              'step_provider_total_tokens': sum(r['total_tokens'] for r in usage),
              'step_usage_provenance': usage,
              'scope': [
                  'GPUh uses recorded final-run wall time plus load for single-GPU processes.',
                  'Excludes E50 incomplete/continuation runtime, geometry runs, profiling and failed attempts; not a whole-project GPU-hour total.',
                  'Calls mix generation/decision, independent fact answers, and exact probability readouts; prefill/score calls are separate.',
                  'Step totals deduplicate provider response IDs in recorded DATA runs; include truncation and recovery where usage exists.',
                  'Provider total_tokens is not an independently verified Credit debit or cash invoice.',
                  'No private credential is read or included by this script.'
              ]}
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k in [
        'e51_to_e61_final_gpu_hours', 'e62_final_gpu_hours',
        'step_responses_with_usage', 'step_provider_total_tokens']}))


if __name__ == '__main__':
    main()
