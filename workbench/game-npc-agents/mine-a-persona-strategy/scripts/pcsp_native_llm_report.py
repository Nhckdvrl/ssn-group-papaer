"""Archive every registered E42 condition; keep both authored goal effects.

This is a baseline report, not a new psychometric construct or a pass/fail test.
"""
import argparse
import hashlib
import json
from pathlib import Path


def classify(x, y):
    if x == 0 and y == 0:
        return 'exact_tie'
    if x >= 0 and y <= 0:
        return 'preference_crossover'
    if x <= 0 and y >= 0:
        return 'reverse_crossover'
    return 'high_input_dominates' if x > 0 else 'low_input_dominates'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    entries = {}
    for model in ['27b', '32b']:
        for peer in ['no', 'full']:
            for prompt in ['persona', 'preference_cue']:
                name = f'e42_{model}_{peer}_{prompt}'
                folder = args.runs/name
                d = json.loads((folder/'summary.json').read_text())
                assert d['episode_count'] == 30 and d['calls'] == 6000
                assert len(d['episodes']) == 30
                assert all(e['cycles'] == 200 and e['physical_parity'] for e in d['episodes'])
                assert len({(e['id'], e['world_seed'], e['input_C']) for e in d['episodes']}) == 30
                cells = []
                for pid in [401, 421, 441, 461, 481]:
                    means = {}
                    world_rows = []
                    for world in [33011, 33012, 33013]:
                        pair = {e['input_C']: e for e in d['episodes']
                                if e['id'] == pid and e['world_seed'] == world}
                        assert set(pair) == {'high', 'low'}
                        row = {f'J_{goal}_given_{inp}': pair[inp][f'J_{goal}']
                               for goal in ['high', 'low'] for inp in ['high', 'low']}
                        row['world_seed'] = world
                        world_rows.append(row)
                    for goal in ['high', 'low']:
                        for inp in ['high', 'low']:
                            k = f'J_{goal}_given_{inp}'
                            means[k] = sum(w[k] for w in world_rows)/3
                    high = means['J_high_given_high']-means['J_high_given_low']
                    low = means['J_low_given_high']-means['J_low_given_low']
                    cells.append(dict(id=pid, **means, high_goal_effect=high,
                                      low_goal_effect=low, DD=high-low,
                                      descriptive_class=classify(high, low), worlds=world_rows))
                entries[name] = {'model': model, 'peer_policy': peer, 'prompt': prompt,
                    'episode_count': 30, 'calls': d['calls'], 'random_fallbacks': d['random_fallbacks'],
                    'load_seconds': d['load_seconds'], 'wall_seconds': d['wall_seconds'],
                    'greedy_duplicate_response_equal': d['greedy_duplicate_response_equal'],
                    'observation_roundtrip_byte_equal': d['observation_roundtrip_byte_equal'],
                    'four_cells': cells, 'raw': str(folder),
                    'summary_sha256': hashlib.sha256((folder/'summary.json').read_bytes()).hexdigest()}
    first_outputs = {}
    for model in ['27b', '32b']:
        for prompt in ['persona', 'preference_cue']:
            rows = {}
            for peer in ['no', 'full']:
                p = args.runs/f'e42_{model}_{peer}_{prompt}'/'model_calls.jsonl'
                with p.open() as f:
                    initial = []
                    for line in f:
                        r = json.loads(line)
                        if r['cycle'] != 0:
                            break
                        initial.append(r)
                rows[peer] = {(r['id'], r['world_seed'], r['input_C']): r for r in initial}
            assert set(rows['no']) == set(rows['full']) and len(rows['no']) == 30
            first_outputs[f'{model}_{prompt}'] = {
                'first_focal_messages_equal': all(rows['no'][k]['messages'] == rows['full'][k]['messages'] for k in rows['no']),
                'first_focal_executed_actions_equal_count': sum(rows['no'][k]['executed_action'] == rows['full'][k]['executed_action'] for k in rows['no']),
                'comparisons': 30,
                'scope': 'Initial focal decision precedes peer actions. Later worlds naturally diverge; this is not whole-episode parity.'}
    gain = []
    for model in ['27b', '32b']:
        for peer in ['no', 'full']:
            a = entries[f'e42_{model}_{peer}_persona']['four_cells']
            b = entries[f'e42_{model}_{peer}_preference_cue']['four_cells']
            gain.append({'model': model, 'peer_policy': peer,
                'per_base_both_goals_and_inputs_mean_difference': [
                    {'id': x['id'], 'cue_minus_persona': sum(y[k]-x[k] for k in
                     ['J_high_given_high', 'J_high_given_low', 'J_low_given_high', 'J_low_given_low'])/4}
                    for x, y in zip(a, b)]})
    result = {'conditions': entries, 'first_decision_controls': first_outputs,
        'ordinary_preference_information_comparison': gain,
        'total_unique_episodes': 240, 'total_local_model_calls': 48000,
        'total_random_fallbacks': sum(x['random_fallbacks'] for x in entries.values()),
        'unique_physical_actor_actions': 768000, 'dual_goal_world_engine_steps': 1536000,
        'cloud_calls': 0, 'all_registered_conditions_retained': True,
        'interpretation': 'Source hand-authored goals and fixed five held-out backgrounds. DD alone does not distinguish goal tradeoffs from changes that improve both goals. No population psychometric or novel-method claim. Two models share Qwen lineage; cue adds authored information and length.',
        'uncertainty': 'All three world results and all five backgrounds retained. No population confidence interval inferred from these fixed configurations.',
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['conditions', 'ordinary_preference_information_comparison']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
