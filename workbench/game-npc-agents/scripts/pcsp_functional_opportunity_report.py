"""POST-HOC E37 interpretation, preserving original readouts and all seeds."""
import argparse
import csv
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    stages = [i for i in [30, 100, 300] if (args.runs/f'e37_matched_i{i}/summary.json').exists()]
    arrays = {i: np.load(args.runs/f'e37_matched_i{i}/per_state.npz') for i in stages}
    first = arrays[stages[0]]; ids = first['pair_ids']
    r0, r1 = first['reward_original'], first['reward_edited']
    shared = ((r0 == r0.max(-1, keepdims=True)) & (r1 == r1.max(-1, keepdims=True))).any(-1)
    regret0 = r0.max(-1) - np.take_along_axis(r0, r1.argmax(-1)[..., None], -1)[..., 0]
    regret1 = r1.max(-1) - np.take_along_axis(r1, r0.argmax(-1)[..., None], -1)[..., 0]
    groups = [401, 421, 441, 461, 481]
    opportunities = []
    for g in groups:
        mask = (ids >= g) & (ids < g+20)
        opportunities.append({'archetype_first_id': g, 'personas': len(set(ids[mask])),
            'pair_states': int(mask.sum()*shared.shape[1]), 'no_shared_immediate_optimum': int((~shared[mask]).sum()),
            'fraction': float((~shared[mask]).mean()), 'original_reward_regret_of_edited_greedy_action': float(regret0[mask].mean()),
            'edited_reward_regret_of_original_greedy_action': float(regret1[mask].mean())})
    rows = []
    for stage, data in arrays.items():
        assert np.array_equal(data['reward_original'], r0) and np.array_equal(data['reward_edited'], r1)
        for seed in [42, 43, 44]:
            for route in ['no', 'full']:
                for g in groups:
                    mask = (ids >= g) & (ids < g+20)
                    row = {'iteration': stage, 'seed': seed, 'route': route, 'archetype_first_id': g}
                    for direction in ['alias', 'C_edit']:
                        for mode in ['natural', '1.0']:
                            key = f'{seed}_{route}_{direction}_{mode}'
                            cells = data[key+'_reward_cells'][mask]
                            dd = cells[..., 3]-cells[..., 2]-cells[..., 1]+cells[..., 0]
                            row[f'{direction}_{mode}_js'] = float(data[key+'_js'][mask].mean())
                            row[f'{direction}_{mode}_reward_dd'] = float(dd.mean())
                            row[f'{direction}_{mode}_original_goal_change'] = float((cells[..., 1]-cells[..., 0]).mean())
                            row[f'{direction}_{mode}_edited_goal_change'] = float((cells[..., 3]-cells[..., 2]).mean())
                    rows.append(row)
    with (args.out/'archetype_readouts.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    result = {'analysis_status': 'POST-HOC descriptive interpretation of existing E37 arrays',
        'opportunities': opportunities, 'readouts': rows, 'training_stages': stages,
        'exact_optimum_definition': 'Sets attaining the original source immediate reward maximum, without a scientific cutoff.',
        'scope': 'One-step reward opportunities are not long-term goal equivalence; actor objectives and multiple optimal trajectories remain relevant.',
        'all_training_seeds_retained': True, 'world_or_reward_modified': False, 'new_model_calls': 0}
    (args.out/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.3), layout='constrained')
    x = np.arange(len(groups)); colors = {'no': '#3565a6', 'full': '#c45b32'}
    axes[0].bar(x, [o['fraction'] for o in opportunities], color='#668576')
    axes[0].set(ylabel='Fraction without a shared greedy action', ylim=(0, 1.08), title='Original game reward opportunities')
    for ax in axes:
        ax.set_xticks(x, [str(g) for g in groups]); ax.set_xlabel('Held-out archetype (20 occupations each)')
        ax.spines[['top', 'right']].set_visible(False)
    markers = {30: 'o', 100: '^', 300: 's'}
    for row in rows:
        xx = groups.index(row['archetype_first_id']) + (row['seed']-43)*.045
        xx += {'no': -.13, 'full': .13}[row['route']]
        axes[1].scatter(xx, row['C_edit_natural_reward_dd'], c=colors[row['route']], marker=markers[row['iteration']], s=22, alpha=.7)
    for stage in stages:
        d = arrays[stage]
        for seed in [42, 43, 44]:
            logratio = np.log((d[f'{seed}_full_C_edit_1.0_js']+1e-15)/(d[f'{seed}_full_alias_1.0_js']+1e-15))
            logratio -= np.log((d[f'{seed}_no_C_edit_1.0_js']+1e-15)/(d[f'{seed}_no_alias_1.0_js']+1e-15))
            for i, g in enumerate(groups):
                mask=(ids>=g)&(ids<g+20)
                axes[2].scatter(i+(seed-43)*.06, logratio[mask].mean(), marker=markers[stage], color='#5d528e', s=25, alpha=.7)
    axes[1].set(ylabel='Expected immediate reward orientation', title='Natural C-text edit: all routes / seeds')
    axes[2].set(ylabel='Full minus No: log(C / alias response)', title='Matched displacement: directional response')
    for ax in axes[1:]: ax.axhline(0, color='grey', linewidth=.7)
    for route, color in colors.items(): axes[1].scatter([], [], color=color, label=route)
    for stage in stages: axes[2].scatter([], [], marker=markers[stage], color='#5d528e', label=f'{stage} iterations')
    axes[1].legend(frameon=False); axes[2].legend(frameon=False)
    fig.suptitle('E37 exploratory functional analysis: reward structure, action response and utility direction')
    fig.savefig(args.out/'functional_opportunities.svg'); fig.savefig(args.out/'functional_opportunities.png', dpi=170)
    print(json.dumps({'stages': stages, 'opportunities': opportunities, 'rows': len(rows)}))


if __name__ == '__main__':
    main()
