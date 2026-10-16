#!/usr/bin/env python3
"""Actual E80 inference/slot costs and exact profile reuse; no model launches."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


STAGES = ['npc_choice', 'npc_primitive', 'player']


def episode_key(row):
    return tuple(row[k] for k in ['case_id', 'seed', 'persona', 'backend'])


def canonical_digest(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_digest(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def cost(root, out):
    """Read completed profile/full jobs, counting actual calls exactly once.

    model_calls.jsonl contains actual new inference, while reused_calls.jsonl
    records cache hits without new inference. Repeated metadata for the same
    physical host/PID/start is deduplicated; distinct real calls remain real
    costs even if their inputs happen to match another process's input.
    """
    jobs, models, seen_jobs, folders, duplicate_metadata = [], {}, {}, set(), 0
    profile_matches = 0
    full_manifests = []
    for model in ['gemma', '32b']:
        model_jobs, model_manifests = [], []
        for suffix in ['profile_launch', 'launch']:
            metadata_file = root/f'e80_{model}_{suffix}.json'
            metadata = json.loads(metadata_file.read_text())
            for job in metadata if isinstance(metadata, list) else [metadata]:
                requested = Path(job['cmd'][job['cmd'].index('--out')+1])
                folder = Path(job.get('artifact_folder', job.get('local_out', str(requested))))
                if not folder.exists() and (root/folder.name).exists():
                    folder = root/folder.name
                job_key = (str(job['host']), int(job['pid']), float(job['start_epoch']))
                if job_key in seen_jobs:
                    assert seen_jobs[job_key] == folder.resolve()
                    duplicate_metadata += 1
                    continue
                assert folder.resolve() not in folders, ('One output folder assigned to multiple jobs', folder)
                seen_jobs[job_key] = folder.resolve()
                folders.add(folder.resolve())
                manifest = json.loads((folder/'manifest.json').read_text())
                runtime = json.loads((folder/'runtime.json').read_text())
                assert manifest['experiment'] == 'E80'
                assert bool(manifest['profile']) == suffix.startswith('profile')
                assert runtime['new_cloud_calls'] == manifest['new_cloud_calls'] == 0
                model_manifests.append(manifest)
                counts, decision_keys, trace_records = Counter(), set(), 0
                for row in map(json.loads, (folder/'model_calls.jsonl').open()):
                    assert row['stage'] in STAGES
                    counts.update(calls=1, parse_errors=int(bool(row.get('parse_error'))),
                                  prompt_tokens=row['prompt_tokens'], completion_tokens=row['completion_tokens'])
                    counts['stage_'+row['stage']] += 1
                    # SharedPrefixClient guarantees at most one actual call
                    # per exact decision key in a single process.
                    assert row['decision_key'] not in decision_keys
                    decision_keys.add(row['decision_key'])
                    trace_records += 1
                assert trace_records == runtime['calls']
                replay = folder/'reused_calls.jsonl'
                cache_hits = sum(1 for _ in replay.open()) if replay.exists() else 0
                assert cache_hits == runtime['reused_calls']
                if 'end_epoch' in job:
                    end, end_source = float(job['end_epoch']), 'launch_metadata.end_epoch'
                elif 'artifact_source_end_epoch' in job:
                    end, end_source = float(job['artifact_source_end_epoch']), 'launch_metadata.artifact_source_end_epoch'
                else:
                    end = (folder/'runtime.json').stat().st_mtime
                    log = folder.with_suffix('.log')
                    if log.exists():
                        end = max(end, log.stat().st_mtime)
                    end_source = 'shared_original_runtime_or_log_mtime'
                assert end >= job['start_epoch']
                record = {'folder': str(folder), 'requested_output': str(requested), 'model': model,
                          'profile': bool(manifest['profile']), 'host': str(job['host']),
                          'gpu': str(job['gpu']), 'pid': int(job['pid']),
                          'start_epoch': job['start_epoch'], 'end_epoch': end, 'end_source': end_source,
                          'runtime_worlds': runtime['worlds'], 'runtime_episodes': runtime['episodes'],
                          **dict(counts), 'reused_calls': cache_hits,
                          'distinct_actual_decision_keys_in_job': len(decision_keys),
                          'load_and_inference_gpu_hours': (runtime['wall_seconds']+runtime['model_load_seconds'])/3600,
                          'observed_slot_hours': (end-job['start_epoch'])/3600,
                          'source_sha256': {str(folder/name): file_digest(folder/name)
                                            for name in ['manifest.json', 'runtime.json', 'model_calls.jsonl', 'episodes.jsonl']}}
                jobs.append(record)
                model_jobs.append(record)
                if not manifest['profile']:
                    full_manifests.append(manifest)
        assert model_manifests
        first_manifest = model_manifests[0]
        for field in ['model', 'source_sha256', 'driver_sha256', 'skills_sha256', 'seeds', 'personas', 'backends']:
            assert all(m[field] == first_manifest[field] for m in model_manifests), (model, field)
        profiles = {}
        for job in model_jobs:
            if not job['profile']:
                continue
            count = 0
            for row in map(json.loads, (Path(job['folder'])/'episodes.jsonl').open()):
                key = episode_key(row)
                assert key not in profiles
                profiles[key] = canonical_digest(row)
                count += 1
            assert count == job['runtime_episodes']
        assert len(profiles) == 24
        full_keys, world_ids, matched_profiles = set(), set(), set()
        for job in model_jobs:
            if job['profile']:
                continue
            count = 0
            for row in map(json.loads, (Path(job['folder'])/'episodes.jsonl').open()):
                key = episode_key(row)
                assert key not in full_keys
                full_keys.add(key)
                world_ids.add(row['case_id'])
                if key in profiles:
                    assert canonical_digest(row) == profiles[key], ('Profile/full record differs', key)
                    matched_profiles.add(key)
                count += 1
            assert count == job['runtime_episodes']
        assert len(world_ids) == 200 and len(full_keys) == 2400
        expected = {(cid, seed, p, b) for cid in world_ids for seed in first_manifest['seeds']
                    for p in first_manifest['personas'] for b in first_manifest['backends']}
        assert full_keys == expected and matched_profiles == set(profiles)
        profile_matches += len(matched_profiles)
        models[model] = {'source_worlds': len(world_ids), 'logical_execution_episodes': len(full_keys),
                         'new_logical_execution_episodes': len(full_keys),
                         'old_E75_E77_episodes_reused': 0,
                         'profile_episodes_exactly_reused': len(matched_profiles),
                         'full_worker_jobs': sum(not j['profile'] for j in model_jobs)}
    for field in ['source_sha256', 'driver_sha256', 'skills_sha256', 'seeds', 'backends']:
        assert all(m[field] == full_manifests[0][field] for m in full_manifests), field
    assert len(full_manifests) == 8
    keys = ['calls', 'parse_errors', 'prompt_tokens', 'completion_tokens', 'reused_calls',
            'load_and_inference_gpu_hours', 'observed_slot_hours'] + ['stage_'+s for s in STAGES]
    totals = {key: sum(job.get(key, 0) for job in jobs) for key in keys}
    events = sorted([(job['start_epoch'], 1, (job['host'], job['gpu'])) for job in jobs]
                    + [(job['end_epoch'], -1, (job['host'], job['gpu'])) for job in jobs])
    active, peak = Counter(), 0
    for _, direction, slot in events:
        active[slot] += direction
        assert active[slot] >= 0
        peak = max(peak, sum(v > 0 for v in active.values()))
    profile_before_full = (max(j['end_epoch'] for j in jobs if j['profile'])
                           <= min(j['start_epoch'] for j in jobs if not j['profile']))
    result = {'status': 'COMPLETE', 'experiment': 'E80', 'source_worlds': 200,
              'logical_execution_episodes': 4800, 'new_logical_execution_episodes': 4800,
              'old_E75_E77_episodes_reused': 0, 'profile_exactly_reused_episodes': profile_matches,
              'duplicate_launch_metadata_deduplicated': duplicate_metadata,
              'models': models, 'jobs': jobs, 'totals': totals, 'peak_gpus': peak,
              'gpu_limit': 8, 'gpu_limit_respected': peak <= 8,
              'all_profiles_completed_before_full_start': profile_before_full,
              'new_cloud_calls': 0,
              'scope': ['Profiles are 48 logical episodes repeated exactly in full jobs, not extra independent worlds or episodes.',
                        'Actual model_calls records counted once per unique physical job; replay/cache-hit trace rows are never new inference calls.',
                        'Distinct real inference calls remain costs even if inputs happen to match across processes.',
                        'No old E75/E77 episodes are reused; source worlds remain the same existing held-item200 cohort.',
                        'Observed slot time includes imports, model loading, inference and logged teardown; load+inference is reported separately.',
                        'Final mtimes are the original shared-filesystem artifacts unless explicit source end times are in launch metadata.',
                        'Peak concurrency groups physical slots by host and GPU; all profiles must finish before eight-worker execution.']}
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'totals': totals, 'peak_gpus': peak, 'profiles_before_full': profile_before_full,
                      'profile_matches': profile_matches}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='mode', required=True)
    parser = sub.add_parser('cost')
    parser.add_argument('--runs-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    cost(args.runs_root, args.out)


if __name__ == '__main__':
    main()
