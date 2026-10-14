"""Summarize existing E49 artifacts. No engine, model, network or GPU calls."""
import argparse
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def segments(frames, actor):
    result = []
    for index, frame in enumerate(frames):
        activity = frame[actor]['act']
        if not result or result[-1]['activity'] != activity:
            result.append({'start': index, 'end': index, 'activity': activity})
        else:
            result[-1]['end'] = index
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--allow-partial', action='store_true')
    args = ap.parse_args()
    branches, frame_banks, comparisons, workers = {}, {}, {}, {}
    actors = {'diego': 'Diego Torres', 'sofia': 'Sofia Ramirez'}
    for slug, actor in actors.items():
        for style in ['original', 'contrast']:
            for channel in ['keep', 'block']:
                worker_id = f'{slug}_{style}_{channel}'
                worker = args.root/f'e49_{worker_id}'
                if (worker/'worker_summary.json').exists():
                    workers[worker_id] = read(worker/'worker_summary.json')
                for seed in [3501, 3502, 3503]:
                    branch = worker/f'seed{seed}'/'grounded'
                    if not (branch/'summary.json').exists():
                        continue
                    summary = read(branch/'summary.json')
                    assert summary['frames'] == 1200 and summary['error'] is None
                    rows = [json.loads(line) for line in (branch/'model_calls.jsonl').read_text().splitlines()]
                    assert len(rows) == summary['new_local_calls']
                    frames = read(branch/'frames.json')
                    key = f'{worker_id}_s{seed}'
                    frame_banks[key] = frames
                    outcomes, errors = [], []
                    for row in rows:
                        if row.get('parse_error'):
                            errors.append({'call_id': row['id'], 'context': row['context'],
                                'tool': (row.get('tool') or {}).get('name'),
                                'parse_error': row['parse_error'], 'finish_reason': row['finish_reason']})
                        if (row.get('tool') or {}).get('name') == 'conversation_outcome':
                            speaker = next((name for name in frames[0]
                                if f'Persona: I am {name},' in row['messages'][0]['content']), None)
                            outcomes.append({'call_id': row['id'], 'step': row['context'].get('turn'),
                                'actor_declared_in_prompt': speaker, 'outcome': row['parsed'],
                                'parse_error': row.get('parse_error')})
                    events = []
                    for event in read(branch/'revision_events.json'):
                        events.append({k: event[k] for k in ['step', 'actor', 'reason', 'detail',
                            'urgency', 'blocked', 'changed', 'immediate_next', 'cursor_before', 'cursor_after']}
                            | {'stops_before': event['plan_before']['stops'],
                               'stops_after': event['plan_after']['stops']})
                    roots = [row for row in read(branch/'parser_calls.json')
                             if row['depth'] == 0 and row['step'] >= summary['fork_step']]
                    verification = args.root/f'e49_verified_{key}.json'
                    branches[key] = {'summary': summary, 'actor_activity_segments':
                        {name: segments(frames, name) for name in frames[0]},
                        'intention_extractions': outcomes, 'revision_events': events,
                        'all_parse_errors': errors, 'suffix_root_parser_calls': len(roots),
                        'suffix_root_legal': sum(row['success'] for row in roots),
                        'suffix_material_changes': [row for row in roots if row['material_delta']],
                        'inference_seconds': sum(row['wall_seconds'] for row in rows),
                        'prompt_tokens': sum(row['prompt_tokens'] for row in rows),
                        'completion_tokens': sum(row['completion_tokens'] for row in rows),
                        'independent_replay': read(verification) if verification.exists() else None,
                        'raw': str(branch)}
    for slug in actors:
        for seed in [3501, 3502, 3503]:
            pairs = [(f'{slug}_original_{channel}_s{seed}', f'{slug}_contrast_{channel}_s{seed}')
                     for channel in ['keep', 'block']]
            pairs += [(f'{slug}_{style}_keep_s{seed}', f'{slug}_{style}_block_s{seed}')
                      for style in ['original', 'contrast']]
            for a, b in pairs:
                if a not in frame_banks or b not in frame_banks:
                    continue
                first, second = frame_banks[a], frame_banks[b]
                comparisons[a+'__vs__'+b] = {
                    'identical_full_frames': sum(u == v for u, v in zip(first, second)),
                    'same_tile_position_frames': {name: sum(
                        all(u[name][k] == v[name][k] for k in ['x', 'y'])
                        for u, v in zip(first, second)) for name in first[0]},
                    'same_activity_text_frames': {name: sum(u[name]['act'] == v[name]['act']
                        for u, v in zip(first, second)) for name in first[0]},
                    'same_position_activity_frames': {name: sum(
                        all(u[name][k] == v[name][k] for k in ['x', 'y', 'act'])
                        for u, v in zip(first, second)) for name in first[0]}}
    complete = len(branches) == 24 and len(workers) == 8
    independently_verified = sum(b['independent_replay'] is not None for b in branches.values())
    if not args.allow_partial:
        assert complete and independently_verified == 24
    result = {'complete': complete, 'registered_cases': 6, 'registered_branches': 24,
        'completed_branches': len(branches), 'independently_verified_branches': independently_verified,
        'new_local_calls': sum(b['summary']['new_local_calls'] for b in branches.values()),
        'new_suffix_frames': sum(1200-b['summary']['fork_step'] for b in branches.values()),
        'model_load_seconds': sum(c['model_load_seconds'] for w in workers.values() for c in w['completed_cases']),
        'branches': branches, 'comparisons': comparisons, 'cloud_calls': 0,
        'scope': 'Three shared natural histories, two different role-description contrasts, one model. '
            'Not 24 independent natural samples. Later sampling indices and peer behaviour can diverge. '
            'Activity text and agenda states do not prove physical task completion.'}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['branches', 'comparisons']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
