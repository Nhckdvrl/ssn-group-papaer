#!/usr/bin/env python3
"""E85 CPU-only cost ledger and figures from the verified complete reports.

No model or environment execution. All ten launches remain in resource costs;
only the recovered complete reports provide plotted outcomes.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


MODELS = [('gemma', 'Gemma 3 12B', '#4477AA'),
          ('32b', 'Qwen3 32B', '#AA3377')]
CONTRASTS = [
    ('real_claim_minus_claim_only/normal', 'npc_gave_Y_to_player',
     'Actual transfer − claim only (normal)\nNPC Give Y to player'),
    ('real_claim_minus_claim_only/check', 'npc_gave_Y_to_player',
     'Actual transfer − claim only (fact check)\nNPC Give Y to player'),
    ('claim_only_minus_pending_truth/normal', 'npc_gave_Y_to_player',
     'Claim only − truthful pending (normal)\nNPC Give Y to player'),
    ('claim_only_minus_pending_truth/check', 'npc_gave_Y_to_player',
     'Claim only − truthful pending (fact check)\nNPC Give Y to player'),
    ('withdraw_minus_continue', 'post_revision_npc_gave_X_to_player',
     'Withdraw − continue (after common first response)\nNew NPC Give X to player, turns ≥ 2'),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def read_reports(results):
    reports, sources = {}, {}
    for model, _, _ in MODELS:
        path = results / f'E85_{model}_complete.json'
        report = json.loads(path.read_text())
        assert report['experiment'] == 'E85' and report['status'] == 'COMPLETE'
        assert (report['logical_branches'], report['histories'], report['independent_graphs']) == (288, 18, 9)
        assert report['source_and_fork_compatibility']['partial_outcomes_used'] is False
        reports[model] = report
        sources[model] = {'path': str(path.resolve()), 'sha256': sha(path)}
    assert len({d['data_sha256'] for d in reports.values()}) == 1
    audit_path = results / 'E85_statistical_independent_review.json'
    audit = json.loads(audit_path.read_text())
    assert audit['status'] == 'PASS' and audit['total_numeric_fields_matched'] == 2782
    sources['independent_numeric_review'] = {'path': str(audit_path.resolve()), 'sha256': sha(audit_path)}
    return reports, sources, audit


def accounting(reports, sources, audit, out):
    launches, run_paths, per_model, counters = [], set(), {}, Counter()
    for model, _, _ in MODELS:
        report = reports[model]
        counts = Counter()
        observed_hours = 0.0
        for run in report['cost']['per_run']:
            folder = Path(run['run'])
            assert folder.resolve() not in run_paths, 'A launch must not be costed twice'
            run_paths.add(folder.resolve())
            launcher_path = Path(run['launch_metadata'])
            launcher = json.loads(launcher_path.read_text())
            assert launcher['start_epoch'] == run['launch_epoch']
            assert launcher['end_epoch'] == run['wrapper_end_epoch']
            assert launcher['exit_code'] == run['wrapper_exit_code']
            assert run['observed_occupied_slot_endpoint'] == 'wrapper_observed_child_exit'
            seconds = launcher['end_epoch'] - launcher['start_epoch']
            assert seconds >= 0 and abs(seconds - run['observed_occupied_slot_seconds']) < 1e-9
            observed_hours += seconds / 3600
            calls_path = folder / 'model_calls.jsonl'
            assert sha(calls_path) == report['source_sha256'][str(calls_path)]
            recorded = Counter()
            with calls_path.open() as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    response = json.loads(line)
                    recorded.update(calls=1, prompt_tokens=response['prompt_tokens'],
                                    completion_tokens=response['completion_tokens'],
                                    parse_errors=int(bool(response['parse_error'])))
            assert recorded['calls'] == run['calls']
            counts.update(recorded)
            launches.append({
                'model_key': model, 'model': report['model'], **run,
                'recorded_prompt_tokens': recorded['prompt_tokens'],
                'recorded_completion_tokens': recorded['completion_tokens'],
                'recorded_parse_errors': recorded['parse_errors'],
                'launcher_sha256': sha(launcher_path), 'model_calls_sha256': sha(calls_path),
            })
        for field in ['calls', 'prompt_tokens', 'completion_tokens', 'parse_errors']:
            assert counts[field] == report['cost'][field], (model, field)
        assert abs(observed_hours - report['cost']['observed_occupied_GPU_slot_hours']) < 1e-12
        counters.update(counts)
        per_model[model] = {'model': report['model'], **dict(counts),
                            'recorded_total_tokens': counts['prompt_tokens'] + counts['completion_tokens'],
                            'observed_occupied_GPU_slot_hours': observed_hours,
                            'launches': len(report['cost']['per_run']),
                            'logical_outcome_branches': report['logical_branches']}
    assert len(launches) == 10
    hours = sum(v['observed_occupied_GPU_slot_hours'] for v in per_model.values())
    assert counters['calls'] == audit['total_actual_calls_all_launches']
    assert abs(hours - audit['total_observed_GPU_slot_hours_all_launches']) < 1e-12
    totals = {**dict(counters),
              'recorded_total_tokens': counters['prompt_tokens'] + counters['completion_tokens'],
              'observed_occupied_GPU_slot_hours': hours, 'launches': len(launches),
              'wrapper_exit_observed_launches': len(launches), 'runtime_mtime_fallback_launches': 0,
              'logical_outcome_branches': sum(d['logical_branches'] for d in reports.values()),
              'new_cloud_calls': 0}
    result = {
        'experiment': 'E85', 'status': 'COMPLETE', 'kind': 'Derived verified resource accounting',
        'assets_script_sha256': sha(__file__), 'report_sources': sources,
        'totals': totals, 'per_model': per_model, 'launches': launches,
        'scope': [
            'Count all ten launches once: two original profiles, four legacy full queues and four faithful recoveries. Legacy outcomes do not add outcome N.',
            'Calls and tokens are complete serialized model-response records. Aborted workers may have in-flight generations that never returned or were never serialized; their counts/tokens are UNKNOWN, not imputed as zero.',
            'Occupied GPU-slot hours use wrapper start_epoch through observed child-exit end_epoch, including preparation/loading/CPU waits/in-flight work/teardown; they are not GPU-active or inference-only hours.',
            'All ten launch endpoints are observed; no runtime-mtime approximation is used. Missing aborted load/run sub-timers remain unknown in the source reports.',
            'Exact cache reuse is not another inference call or independent outcome sample. Reports preserve actual-input cache lineage and original source purposes.',
        ],
        'asset_generation_new_model_calls': 0, 'asset_generation_new_API_calls': 0,
        'asset_generation_new_GPU_jobs': 0,
    }
    write_json(out, result)
    return totals


def figures(reports, sources, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
                         'svg.hashsalt': 'game-npc-E85-primary'})
    figure_input = []
    fig, ax = plt.subplots(figsize=(12.5, 6.3))
    fig.subplots_adjust(left=.47, right=.97, bottom=.28, top=.79)
    for index, (model, label, color) in enumerate(MODELS):
        means, lower, upper = [], [], []
        for row, (contrast, metric, text) in enumerate(CONTRASTS):
            value = reports[model]['paired_contrasts'][contrast]['metrics'][metric]
            assert value['independent_graphs'] == 9
            assert value['known_history_seed_pairs'] == 36 and value['unknown_history_seed_pairs'] == 0
            mean = value['mean'] * 100
            lo, hi = [v * 100 for v in value['graph_bootstrap_95']]
            assert lo <= mean <= hi
            means.append(mean); lower.append(mean - lo); upper.append(hi - mean)
            figure_input.append({'model_key': model, 'model': label, 'row': row,
                'label': text, 'contrast': contrast, 'metric': metric,
                'report_json_pointer': f'/paired_contrasts/{contrast.replace("/", "~1")}/metrics/{metric}',
                'estimate_proportion': value['mean'], 'estimate_pp': mean,
                'graph_bootstrap_95_proportion': value['graph_bootstrap_95'],
                'graph_bootstrap_95_pp': [lo, hi],
                'independent_graphs': value['independent_graphs'],
                'known_history_seed_pairs': value['known_history_seed_pairs']})
        positions = [row + (-.12 if index == 0 else .12) for row in range(len(CONTRASTS))]
        ax.errorbar(means, positions, xerr=[lower, upper], fmt='o' if index == 0 else 's',
                    color=color, markersize=6, capsize=3, linewidth=1.6, label=label)
    ax.axvline(0, color='#555555', linestyle='--', linewidth=1, zorder=0)
    ax.axhline(3.5, color='#BBBBBB', linewidth=.8)
    ax.set_yticks(range(len(CONTRASTS)), [text for _, _, text in CONTRASTS])
    ax.tick_params(axis='y', length=0, pad=12)
    ax.set_ylim(len(CONTRASTS) - .5, -.5)
    ax.set_xlim(-65, 55)
    ax.set_xticks([-60, -40, -20, 0, 20, 40])
    ax.set_xlabel('Difference in action occurrence (percentage points)', labelpad=10)
    ax.grid(axis='x', alpha=.18)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    fig.suptitle('E85 · Actual transfers, claims, and changed requests', y=.97, fontsize=14)
    fig.text(.5, .916, 'Action differences, not cooperation quality', ha='center', fontsize=11)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5, .875), ncol=2, frameon=False)
    fig.text(.5, .115,
             '9 source graphs · 18 source histories · 2 fixed seeds; paired differences before equal graph averaging.\n'
             'Pointwise 95% graph-bootstrap intervals (4,000 draws). First four rows: full responsive continuation, initial-treatment ITT.\n'
             'Last row: new Give X only after the identical first NPC response and changed request (turns ≥ 2).',
             ha='center', va='center', fontsize=9, linespacing=1.5)
    fig.text(.5, .035,
             'X is the player-transferred item; Y is the NPC-held item sought by the player. Neither receipt nor Give certifies the full role purpose.',
             ha='center', va='center', fontsize=8.6, color='#444444')
    stem = 'E85_primary_contrasts'
    for ext in ['png', 'pdf', 'svg']:
        path = out / f'{stem}.{ext}'
        metadata = {'Date': None} if ext == 'svg' else {'CreationDate': None, 'ModDate': None} if ext == 'pdf' else None
        fig.savefig(path, dpi=180, metadata=metadata)
        if ext == 'svg':
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
    plt.close(fig)
    write_json(out / 'E85_figure_input_checks.json', {
        'experiment': 'E85', 'status': 'PASS', 'assets_script_sha256': sha(__file__),
        'report_sources': sources, 'points': figure_input,
        'checks': {'points_read_directly_from_complete_verified_reports': len(figure_input),
                   'independent_graphs_for_every_point': 9, 'history_seed_pairs_for_every_point': 36,
                   'no_new_CI_or_outcome_estimation': True,
                   'withdrawal_metric_excludes_common_turn0_and_counts_turns_greater_equal_2': True},
        'figures': [{'path': str((out / f'{stem}.{ext}').resolve()),
                     'sha256': sha(out / f'{stem}.{ext}')} for ext in ['png', 'pdf', 'svg']],
        'scope': 'Action occurrence differences, not universal cooperation quality, welfare or capability. Interval endpoints and estimates are copied without recalculation from the paired nine-graph bootstrap reports.',
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--figures-out', type=Path)
    parser.add_argument('--cost-out', type=Path)
    args = parser.parse_args()
    reports, sources, audit = read_reports(args.results)
    totals = accounting(reports, sources, audit, args.cost_out or args.results / 'E85_cost_accounting.json')
    figures(reports, sources, args.figures_out or args.results / 'figures')
    print(json.dumps({'status': 'COMPLETE', **totals, 'new_model_calls_for_assets': 0}))


if __name__ == '__main__':
    main()
