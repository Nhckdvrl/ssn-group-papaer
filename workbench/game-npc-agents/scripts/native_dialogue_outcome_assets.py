#!/usr/bin/env python3
"""E77 exact profile reuse, actual local resource accounting and static figures."""
import argparse
from collections import Counter
import json
from pathlib import Path

from native_dialogue_outcome_report import row_key


def cost(root, out):
    jobs, models, profile_checks = [], {}, 0
    seen_folders = set()
    for model in ['gemma', '32b']:
        model_jobs = []
        for suffix in ['profile_launch', 'launch']:
            metadata = json.loads((root/f'e77_{model}_{suffix}.json').read_text())
            for job in metadata if isinstance(metadata, list) else [metadata]:
                folder = Path(job['cmd'][job['cmd'].index('--out')+1])
                assert folder not in seen_folders
                seen_folders.add(folder)
                manifest = json.loads((folder/'manifest.json').read_text())
                rt = json.loads((folder/'runtime.json').read_text())
                assert manifest['experiment'] == 'E77'
                assert bool(manifest['profile']) == suffix.startswith('profile')
                counts = Counter()
                for row in map(json.loads, (folder/'model_calls.jsonl').open()):
                    assert row['stage'] == 'exec'
                    counts.update(calls=1, parse_errors=int(bool(row['parse_error'])),
                                  prompt_tokens=row['prompt_tokens'], completion_tokens=row['completion_tokens'])
                    counts['stage_'+row['stage']] += 1
                assert counts['calls'] == rt['calls']
                assert rt['new_cloud_calls'] == rt['new_conversation_calls'] == 0
                end = (folder/'runtime.json').stat().st_mtime
                log = folder.with_suffix('.log')
                if log.exists():
                    end = max(end, log.stat().st_mtime)
                assert end >= job['start_epoch']
                record = {'folder': str(folder), 'model': model, 'profile': bool(manifest['profile']),
                          'gpu': job['gpu'], 'pid': job['pid'], 'host': job['host'],
                          'start_epoch': job['start_epoch'], 'end_epoch': end,
                          **dict(counts), 'reused_calls': rt['reused_calls'],
                          'load_and_inference_gpu_hours': (rt['wall_seconds']+rt['model_load_seconds'])/3600,
                          'observed_slot_hours': (end-job['start_epoch'])/3600}
                jobs.append(record)
                model_jobs.append(record)
        full, profiles = {}, []
        for job in model_jobs:
            rows = list(map(json.loads, (Path(job['folder'])/'episodes.jsonl').open()))
            if job['profile']:
                profiles.extend(rows)
            else:
                for row in rows:
                    key = row_key(row)
                    assert key not in full
                    full[key] = row
        assert len(full) == 2448 and len(profiles) == 24
        for row in profiles:
            assert full[row_key(row)] == row
            profile_checks += 1
        diagonals = sum(r['assigned_outcome'] is None and r['conv_persona'] == r['persona']
                        for r in full.values())
        assert diagonals == 612
        models[model] = {'logical_execution_records': len(full), 'old_diagonals_exactly_reused': diagonals,
                         'new_logical_execution_branches': len(full)-diagonals,
                         'profile_records_exactly_reused': len(profiles)}
    keys = ['calls', 'parse_errors', 'prompt_tokens', 'completion_tokens', 'stage_conv', 'stage_exec',
            'reused_calls', 'load_and_inference_gpu_hours', 'observed_slot_hours']
    totals = {key: sum(job.get(key, 0) for job in jobs) for key in keys}
    events = sorted([(job['start_epoch'], 1, (job['host'], job['gpu'])) for job in jobs]
                    + [(job['end_epoch'], -1, (job['host'], job['gpu'])) for job in jobs])
    active, peak = Counter(), 0
    for _, direction, slot in events:
        active[slot] += direction
        assert active[slot] >= 0
        peak = max(peak, sum(v > 0 for v in active.values()))
    result = {'status': 'COMPLETE', 'experiment': 'E77', 'source_worlds': 102,
              'logical_execution_records': 4896, 'old_diagonal_records_exactly_reused': 1224,
              'new_logical_execution_branches': 3672, 'profile_exactly_reused_branches': profile_checks,
              'models': models, 'jobs': jobs, 'totals': totals, 'peak_gpus': peak,
              'new_conversation_calls': 0, 'new_cloud_calls': 0,
              'scope': ['New profile calls counted once; full-job exact reuse adds no new inference calls.',
                        'Old E75 diagonals are 1224 reused records, not new physical branches.',
                        'Observed GPU-slot hours include startup, imports, model loading, inference and logged teardown.',
                        'Peak GPU count derives from overlapping job intervals grouped by host and physical GPU.']}
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'totals': totals, 'peak_gpus': peak, 'new_branches': 3672}))


def figure(results, out, group='source_use'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from native_request_precondition_figures import save
    plt.rcParams.update({'font.size': 10, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'game-npc-E77'})
    from matplotlib.lines import Line2D
    fig, axes = plt.subplots(2, 3, figsize=(16.5, 8.3), layout='constrained')
    layers = [('physical_goal', 'Physical task consequence', '#4477AA'), ('request', 'Give to requester', '#EE7733'),
              ('other_source_give', 'Other source Give', '#AA3377'),
              ('physical_retrieved_without_decisive', 'Get, no decisive physical use', '#88CCAA'),
              ('physical_no_get_without_decisive', 'No source Get', '#CCCCCC')]
    for i, (model, label) in enumerate([('gemma', 'Gemma 3 12B'), ('32b', 'Qwen3 32B')]):
        result = json.loads((results/f'E77_{model}_complete.json').read_text())
        data = result['groups'][group]
        contrasts = data['panel_A']['contrasts']
        panel_b = data['panel_B']
        for j, (names, labels, title) in enumerate([
            (['C_A_minus_F/given_exec_'+p for p in ['firm', 'agreeable']],
             ['Execution F', 'Execution A'], 'Dialogue A minus F'),
            (['exec_A_minus_F/given_C_'+p for p in ['firm', 'agreeable']],
             ['Dialogue F', 'Dialogue A'], 'Execution A minus F'),
        ]):
            ax = axes[i, j]
            for field, color, offset in [('physical_goal', '#4477AA', -.16),
                                         ('request', '#EE7733', 0), ('retrieved', '#228833', .16)]:
                values = [contrasts[name][field] for name in names]
                mean = np.array([v['mean'] for v in values])*100
                lower = np.array([v['graph_bootstrap_95'][0] for v in values])*100
                upper = np.array([v['graph_bootstrap_95'][1] for v in values])*100
                ax.errorbar(np.arange(2)+offset, mean, yerr=[mean-lower, upper-mean],
                            fmt='o', color=color, capsize=3, ms=5)
            # The exact-event primary is retained visibly, even when a native
            # Ingest produces the same physical consequence by another event.
            ax.plot(np.arange(2)-.16, [contrasts[n]['goal']['mean']*100 for n in names],
                    'D', color='#111111', ms=3, markerfacecolor='none')
            ax.set_xticks(np.arange(2), labels)
            ax.axhline(0, color='#444444', lw=1)
            ax.set_ylabel('Paired difference (pp)')
            ax.set_title(label+' / '+title+f'\nN={data["worlds"]} source graphs')
            ax.grid(axis='y', alpha=.15)
            ax.spines[['top', 'right']].set_visible(False)
        ax = axes[i, 2]
        cells = ([panel_b['matched_free_cells'][p+'/matched_to_goal'] for p in ['firm', 'agreeable']]
                 + [panel_b['assigned_cells'][p+'/assigned_'+t]
                    for t in ['goal', 'request'] for p in ['firm', 'agreeable']])
        x = np.array([3*k+n for k in range(3) for n in range(2)])
        bottom = np.zeros(len(cells))
        for field, name, color in layers:
            values = np.array([cell[field]['mean'] for cell in cells])*100
            ax.bar(x, values, bottom=bottom, width=.85, color=color, label=name)
            bottom += values
        assert np.allclose(bottom, 100)
        means = np.array([cell['physical_goal']['mean'] for cell in cells])*100
        lower = np.array([cell['physical_goal']['graph_bootstrap_95'][0] for cell in cells])*100
        upper = np.array([cell['physical_goal']['graph_bootstrap_95'][1] for cell in cells])*100
        ax.errorbar(x, means, yerr=[means-lower, upper-means], fmt='none', color='#222222', capsize=2, lw=1)
        ax.plot(x, [cell['goal']['mean']*100 for cell in cells], 'D', color='#111111',
                ms=3, markerfacecolor='none')
        ax.set_xticks(x, ['F', 'A']*3)
        for k, text in enumerate(['Free choice', 'Assigned task', 'Assigned request']):
            ax.text(3*k+.5, -.09, text, ha='center', va='top', transform=ax.get_xaxis_transform())
        ax.set_ylim(0, 103)
        ax.set_ylabel('First decisive physical consequence (%)')
        ax.set_title(label+' / Same donor dialogue'+f'\nN={data["worlds"]} source graphs')
        ax.grid(axis='y', alpha=.15)
        ax.spines[['top', 'right']].set_visible(False)
    handles, names = axes[0, 2].get_legend_handles_labels()
    handles += [Line2D([], [], marker='o', color='#228833', lw=0),
                Line2D([], [], marker='D', color='#111111', markerfacecolor='none', lw=0)]
    names += ['Any source Get (contrasts)', 'Exact authored event (primary)']
    fig.legend(handles, names, loc='outside upper center', ncol=4, frameon=False, fontsize=9)
    title = {'all': 'All original tasks', 'source_give': 'Give tasks',
             'source_use': 'Wear / Eat / Drink tasks'}[group]
    fig.supxlabel(title+'. Original floor states; all three seeds per source graph. F/A labels on bars: current execution trait.\n'
                  'Physical sensitivity counts source-item consumption including Ingest; diamonds retain the exact authored-event primary.\n'
                  'Assigned/free bars share a prespecified donor dialogue. Whiskers: pointwise graph-cluster 95% intervals; assignment changes priorities.',
                  fontsize=9)
    out.mkdir(parents=True, exist_ok=True)
    save(fig, out, 'E77_dialogue_and_assigned_outcomes_'+group)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('cost')
    p.add_argument('--runs-root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('figure')
    p.add_argument('--results', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--group', choices=['all', 'source_give', 'source_use'], default='source_use')
    a = ap.parse_args()
    if a.mode == 'cost':
        cost(a.runs_root, a.out)
    else:
        figure(a.results, a.out, a.group)


if __name__ == '__main__':
    main()
