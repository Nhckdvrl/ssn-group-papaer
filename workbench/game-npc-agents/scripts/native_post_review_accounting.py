#!/usr/bin/env python3
"""CPU accounting for the fixed E63/E64 round, including interrupted inference."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


RUNS = {
    'E63_profile': ['e63_32b_dependency_profile'],
    'E63_main': ['e63_32b_dependency_s0', 'e63_32b_dependency_s1',
        'e63_gemma_dependency', 'e63_27b_dependency',
        'e63_27b_dependency_resume_s0', 'e63_27b_dependency_resume_s1',
        'e63_27b_dependency_resume_s2', 'e63_27b_dependency_migrated_s1',
        'e63_27b_dependency_migrated_s2'],
    'E64_profiles': ['e64_27b_reciprocal_profile', 'e64_27b_reciprocal_profile_v2',
        'e64_32b_reciprocal_profile_v2'],
    'E64_main': ['e64_32b_reciprocal_v2', 'e64_27b_reciprocal_v2',
        'e64_27b_reciprocal_v3_resume'],
    'E64_ordinary_guide': ['e64_32b_transmission_guide'],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    rows = []; totals = defaultdict(lambda: defaultdict(float)); seen = set()
    for category, names in RUNS.items():
        for name in names:
            assert name not in seen; seen.add(name)
            d = a.runs/name
            runtime_path = d/'runtime.json'
            if not runtime_path.exists(): runtime_path = d/'interrupted_runtime.json'
            runtime = json.loads(runtime_path.read_text())
            calls = [json.loads(line) for line in (d/'model_calls.jsonl').read_text().splitlines()]
            # Driver runtime's prior_run is accounted by its own unique source
            # directory above, not recursively added a second time.
            assert len(calls) == runtime['calls'], name
            seconds = runtime['wall_seconds'] + runtime.get('model_load_seconds', 0)
            manifest_path = d/'manifest.json'
            row = {'run': name, 'category': category, 'runtime_path': str(runtime_path),
                'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                'single_gpu_seconds': seconds, 'new_inference_calls': len(calls),
                'prompt_tokens': sum(c['prompt_tokens'] for c in calls),
                'completion_tokens': sum(c['completion_tokens'] for c in calls),
                'parse_errors': sum(bool(c['parse_error']) for c in calls),
                'cloud_calls': runtime['cloud_calls']}
            rows.append(row)
            for key in ['single_gpu_seconds', 'new_inference_calls', 'prompt_tokens',
                        'completion_tokens', 'parse_errors', 'cloud_calls']:
                totals[category][key] += row[key]
    total = {key: sum(v[key] for v in totals.values()) for key in next(iter(totals.values()))}
    for values in [*totals.values(), total]: values['gpu_hours'] = values['single_gpu_seconds']/3600
    report = {'runs': rows, 'by_category': dict(totals), 'total': total,
        'main_episode_counts': {'E63': 16200, 'E64': 216, 'E64_ordinary_guide': 54},
        'new_step_requests': 0, 'new_training_runs': 0, 'new_activation_interventions': 0,
        'scope': ['Each listed process used one GPU; sum measured wall+load, not elapsed project time.',
            'Interrupted/partial-group inference and profiles are included even without a final episode.',
            'Old and new inference files are counted once; replayed decisions and copied episodes are not new inference.',
            'Startup/checkpoint measurements have seconds-level uncertainty; CPU-only validation is not GPU time.',
            'Main episode counts require the complete cohort reports; they exclude profiles and copied-prefix duplication.']}
    result_dir = a.out.parent
    for model in ['32b', '27b', 'gemma']:
        x = json.loads((result_dir/f'E63_{model}_dependency.json').read_text())
        assert x['status'] == 'COMPLETE' and x['episodes'] == 5400 and x['complete_worlds'] == 200
    for model in ['32b', '27b']:
        x = json.loads((result_dir/f'E64_{model}_reciprocal.json').read_text())
        assert x['episodes'] == 108 and x['worlds'] == 9
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'total': total, 'main_episode_counts': report['main_episode_counts']}))


if __name__ == '__main__': main()
