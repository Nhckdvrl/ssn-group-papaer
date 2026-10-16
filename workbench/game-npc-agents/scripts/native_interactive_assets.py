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
                          'initialization_failed': False, 'load_and_inference_timing_available': True,
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
    # Keep zero-inference startup failures in slot accounting. They have no
    # completed runtime/model-load timer, so do not invent a load+infer value.
    failed_attempts = []
    for model in ['gemma', '32b']:
        for metadata_file in sorted(root.glob(f'e80_{model}_s*_init_failed*_launch.json')):
            job = json.loads(metadata_file.read_text())
            assert job['status'] == 'INIT_FAILED_NO_MODEL_CALLS'
            assert job['new_model_calls'] == job['new_episodes'] == 0
            requested = Path(job['cmd'][job['cmd'].index('--out')+1])
            folder = Path(job['artifact_folder'])
            job_key = (str(job['host']), int(job['pid']), float(job['start_epoch']))
            assert job_key not in seen_jobs and folder.resolve() not in folders
            seen_jobs[job_key] = folder.resolve()
            folders.add(folder.resolve())
            for name in ['model_calls.jsonl', 'episodes.jsonl']:
                file = folder/name
                assert not file.exists() or not file.read_text().strip(), (folder, name)
            assert not (folder/'runtime.json').exists()
            end = float(job['end_epoch'])
            assert end >= job['start_epoch']
            files = [metadata_file, folder/'manifest.json', folder.with_suffix('.log')]
            record = {'folder': str(folder), 'requested_output': str(requested), 'model': model,
                      'profile': False, 'initialization_failed': True, 'status': job['status'],
                      'reason': job.get('reason'), 'host': str(job['host']), 'gpu': str(job['gpu']),
                      'pid': int(job['pid']), 'start_epoch': job['start_epoch'], 'end_epoch': end,
                      'end_source': 'failed_launch_metadata.end_epoch',
                      'runtime_worlds': 0, 'runtime_episodes': 0, 'calls': 0,
                      'parse_errors': 0, 'prompt_tokens': 0, 'completion_tokens': 0, 'reused_calls': 0,
                      'distinct_actual_decision_keys_in_job': 0,
                      'load_and_inference_timing_available': False,
                      'load_and_inference_gpu_hours': None,
                      'observed_slot_hours': (end-job['start_epoch'])/3600,
                      'source_sha256': {str(file): file_digest(file) for file in files if file.exists()}}
            failed_attempts.append(record)
            jobs.append(record)
        models[model]['initialization_failed_attempts'] = sum(j['model'] == model for j in failed_attempts)
    for field in ['source_sha256', 'driver_sha256', 'skills_sha256', 'seeds', 'backends']:
        assert all(m[field] == full_manifests[0][field] for m in full_manifests), field
    assert len(full_manifests) == 8
    keys = ['calls', 'parse_errors', 'prompt_tokens', 'completion_tokens', 'reused_calls',
            'load_and_inference_gpu_hours', 'observed_slot_hours'] + ['stage_'+s for s in STAGES]
    totals = {key: sum(job.get(key, 0) for job in jobs if job.get(key) is not None) for key in keys}
    totals['initialization_failed_observed_slot_hours'] = sum(j['observed_slot_hours'] for j in failed_attempts)
    totals['completed_job_observed_slot_hours'] = sum(j['observed_slot_hours'] for j in jobs if not j['initialization_failed'])
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
              'initialization_failed_attempts': len(failed_attempts),
              'models': models, 'jobs': jobs, 'totals': totals, 'peak_gpus': peak,
              'gpu_limit': 8, 'gpu_limit_respected': peak <= 8,
              'all_profiles_completed_before_full_start': profile_before_full,
              'new_cloud_calls': 0,
              'scope': ['Profiles are 48 logical episodes repeated exactly in full jobs, not extra independent worlds or episodes.',
                        'Actual model_calls records counted once per unique physical job; replay/cache-hit trace rows are never new inference calls.',
                        'Distinct real inference calls remain costs even if inputs happen to match across processes.',
                        'No old E75/E77 episodes are reused; source worlds remain the same existing held-item200 cohort.',
                        'Observed slot time includes imports, model loading, inference and logged teardown; load+inference is reported separately.',
                        'Zero-inference initialization failures retain their full observed slot time. Their exact load+infer timer is unavailable; that subtotal covers completed jobs only.',
                        'Final mtimes are the original shared-filesystem artifacts unless explicit source end times are in launch metadata.',
                        'Peak concurrency groups physical slots by host and GPU; all profiles must finish before eight-worker execution.']}
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'totals': totals, 'peak_gpus': peak, 'profiles_before_full': profile_before_full,
                      'profile_matches': profile_matches}))


def read_figure_categories(paths, expected_hashes=None):
    """Read registered-event conjunctions and mutually exclusive final custody.

    The primary report validates full event traces; this helper uses its
    verified flags, checks its source hashes, and reproduces its marginals.
    It does not replace the bound primary with the physical sensitivity.
    """
    from native_interactive_report import owner
    cells, seen, duplicates = {}, {}, 0
    for path in dict.fromkeys(paths):
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for line in handle:
                digest.update(line)
                row = json.loads(line)
                key = episode_key(row)
                goal, given = bool(row['goal_bound_ever']), bool(row['npc_give_request_ever'])
                joint = 'both' if goal and given else 'goal_only' if goal else 'give_only' if given else 'neither'
                aid, bid, original = row['actor_id'], row['requester_id'], row['goal_recipient_id']
                final_owner = owner(row['final_state'], row['goal_item_id'], [aid, bid, original])
                if final_owner == aid:
                    custody = 'npc'
                elif final_owner == bid:
                    custody = 'player'
                elif row['goal_kind'] == 'give' and original is not None and final_owner == original:
                    custody = 'authored_recipient'
                elif row['final_state'][row['goal_item_id']]['container'] == 'VOID':
                    custody = 'VOID'
                else:
                    custody = 'other'
                fingerprint = (joint, custody)
                if key in seen:
                    assert seen[key] == fingerprint, ('Changed plotting categories for one episode', key)
                    duplicates += 1
                    continue
                seen[key] = fingerprint
                cell = cells.setdefault((row['persona'], row['backend']), Counter())
                cell.update(episodes=1)
                cell['joint/'+joint] += 1
                cell['custody/'+custody] += 1
        if expected_hashes is not None:
            assert digest.hexdigest() == expected_hashes[str(path)], ('Report source changed', path)
    for cell in cells.values():
        assert sum(cell['joint/'+k] for k in ['goal_only', 'both', 'give_only', 'neither']) == cell['episodes']
        assert sum(cell['custody/'+k] for k in ['npc', 'player', 'authored_recipient', 'VOID', 'other']) == cell['episodes']
    return cells, seen, duplicates


def figure(results, out, check_only=False):
    """Two primary-event/terminal-state panels and four paired contrasts."""
    import numpy as np
    reports, counts, checks = {}, {}, {}
    for model in ['gemma', '32b']:
        report = json.loads((results/f'E80_{model}_complete.json').read_text())
        # Profiles are for tool/cost checks; this CLI never publishes N=2 plots.
        assert report['status'] == 'COMPLETE' and report['experiment'] == 'E80'
        assert report['worlds'] == 200 and report['episodes'] == 2400
        paths = [Path(p) for p in report['source_sha256'] if Path(p).name == 'episodes.jsonl']
        assert paths
        cells, keys, duplicates = read_figure_categories(paths, report['source_sha256'])
        assert len(keys) == 2400 and len({key[0] for key in keys}) == 200
        for persona in ['firm', 'agreeable']:
            for backend in ['model_steps', 'native_skill']:
                cell = cells[persona, backend]
                assert cell['episodes'] == 600
                primary = report['cells']['all/'+persona+'/'+backend]
                estimates = {
                    'npc_goal_bound_ever': (cell['joint/goal_only']+cell['joint/both'])/600,
                    'npc_source_give_requester_ever': (cell['joint/give_only']+cell['joint/both'])/600,
                    'final_source_ultimate_npc': cell['custody/npc']/600,
                    'final_source_ultimate_requester': cell['custody/player']/600,
                    'final_source_ultimate_original_recipient': cell['custody/authored_recipient']/600,
                    'final_source_VOID': cell['custody/VOID']/600,
                }
                for field, mean in estimates.items():
                    assert np.isclose(mean, primary[field]['mean'], atol=1e-12), (model, persona, backend, field)
        reports[model], counts[model] = report, cells
        checks[model] = {'worlds': 200, 'unique_episodes': 2400,
                         'duplicate_profile_categories_checked': duplicates,
                         'primary_event_and_custody_marginals_match_report': True,
                         'joint_definition': 'Exact bound authored event AND actual NPC source Give to requester; historical events.',
                         'custody_precedence': 'NPC, player B, distinct authored Give recipient A, direct VOID, other.'}
    if check_only:
        print(json.dumps({'status': 'PASS', 'models': checks, 'figures_written': 0}))
        return

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from native_request_precondition_figures import save
    plt.rcParams.update({'font.size': 10, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'game-npc-E80'})
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 8.0), layout='constrained', sharey=True)
    joint_layers = [('goal_only', 'Bound task event only', '#4477AA'),
                    ('both', 'Both registered events', '#55AA99'),
                    ('give_only', 'NPC Give only', '#EE7733'),
                    ('neither', 'Neither registered event', '#BBBBBB')]
    custody_layers = [('npc', 'NPC custody', '#4477AA'), ('player', 'Player B custody', '#EE7733'),
                      ('authored_recipient', 'Authored recipient A custody', '#AA3377'),
                      ('VOID', 'VOID', '#999966'), ('other', 'Other custody', '#CCCCCC')]
    order = [(p, b) for p in ['firm', 'agreeable'] for b in ['model_steps', 'native_skill']]
    x = np.array([0, 1, 3, 4])
    for i, (model, label) in enumerate([('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
        for j, (prefix, layers, title) in enumerate([
            ('joint', joint_layers, 'Registered historical events'),
            ('custody', custody_layers, 'Final source-item custody'),
        ]):
            ax, bottom = axes[i, j], np.zeros(4)
            for field, name, color in layers:
                values = np.array([counts[model][key][prefix+'/'+field]/600 for key in order])*100
                ax.bar(x, values, bottom=bottom, width=.8, color=color, label=name)
                bottom += values
            assert np.allclose(bottom, 100)
            if j == 0:
                vals = [reports[model]['cells']['all/'+p+'/'+b]['npc_goal_bound_ever'] for p, b in order]
                mean = np.array([v['mean'] for v in vals])*100
                lo = np.array([v['graph_bootstrap_95'][0] for v in vals])*100
                hi = np.array([v['graph_bootstrap_95'][1] for v in vals])*100
                ax.errorbar(x, mean, yerr=[mean-lo, hi-mean], color='#222222', fmt='none', capsize=2, lw=1)
            ax.set_xticks(x, ['Steps', 'Skill']*2)
            for center, name in [(.5, 'Firm'), (3.5, 'Agreeable')]:
                ax.text(center, -.09, name, ha='center', va='top', transform=ax.get_xaxis_transform())
            ax.set_title(label+' / '+title+'\nN=200 source graphs')
            ax.set_ylabel('Episodes (%)')
            ax.set_ylim(0, 103)
            ax.grid(axis='y', alpha=.15)
            ax.spines[['top', 'right']].set_visible(False)
            if i == 0:
                ax.legend(loc='lower left', bbox_to_anchor=(0, 1.20), ncol=2, frameon=False, fontsize=8)
    fig.supxlabel('Each backend shares a strong outcome/action/speech selector; every primitive uses one opportunity.\n'
                  'Joint ever events ≠ maintained joint benefit. Neither registered event does not mean no action.\n'
                  'Custody does not identify the acquisition route, survival or welfare. VOID marks source-item consumption/disappearance; actor-specific events remain separate.\n'
                  'Whiskers: graph-bootstrap 95% intervals for the bound task marginal. Player Get/Steal remains legal.',
                  fontsize=9)
    out.mkdir(parents=True, exist_ok=True)
    save(fig, out, 'E80_joint_events_and_final_custody')

    forest, axes = plt.subplots(1, 2, figsize=(12.5, 4.4), layout='constrained', sharey=True)
    contrast_specs = [('all/firm/native_skill_minus_model_steps', 'Skill − Steps / Firm'),
                      ('all/agreeable/native_skill_minus_model_steps', 'Skill − Steps / Agreeable'),
                      ('all/model_steps/agreeable_minus_firm', 'Agreeable − Firm / Steps'),
                      ('all/native_skill/agreeable_minus_firm', 'Agreeable − Firm / Skill')]
    for ax, (model, label) in zip(axes, [('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
        for field, name, color, offset, marker in [
            ('npc_goal_bound_ever', 'Bound authored event', '#4477AA', -.11, 'o'),
            ('npc_source_give_requester_ever', 'Actual NPC Give to B', '#EE7733', .11, 's'),
        ]:
            values = [reports[model]['contrasts'][key][field] for key, _ in contrast_specs]
            mean = np.array([v['mean'] for v in values])*100
            lo = np.array([v['graph_bootstrap_95'][0] for v in values])*100
            hi = np.array([v['graph_bootstrap_95'][1] for v in values])*100
            ax.errorbar(mean, np.arange(4)+offset, xerr=[mean-lo, hi-mean], color=color,
                        fmt=marker, ms=5, capsize=3, label=name)
        ax.axvline(0, color='#444444', lw=1)
        ax.set_yticks(np.arange(4), [name for _, name in contrast_specs])
        ax.set_title(label+' / N=200 source graphs')
        ax.set_xlabel('Paired difference (pp)')
        ax.grid(axis='x', alpha=.15)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].invert_yaxis()
    handles, names = axes[0].get_legend_handles_labels()
    forest.legend(handles, names, loc='outside upper center', ncol=2, frameon=False)
    forest.supxlabel('All three seeds averaged within graph; 4,000 paired graph-bootstrap draws, pointwise 95% intervals.\n'
                     'Historical task and NPC Give events may co-occur; physical/equipment sensitivities remain separate in the complete report.',
                     fontsize=9)
    save(forest, out, 'E80_backend_trait_primary_contrasts')
    (out/'E80_figure_input_checks.json').write_text(json.dumps({'status': 'PASS', 'models': checks}, indent=2)+'\n')
    print(json.dumps({'status': 'PASS', 'models': checks, 'scientific_figures_written': 2,
                      'formats': ['png', 'pdf', 'svg']}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='mode', required=True)
    parser = sub.add_parser('cost')
    parser.add_argument('--runs-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser = sub.add_parser('figure')
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check-only', action='store_true')
    args = ap.parse_args()
    if args.mode == 'cost':
        cost(args.runs_root, args.out)
    else:
        figure(args.results, args.out, args.check_only)


if __name__ == '__main__':
    main()
