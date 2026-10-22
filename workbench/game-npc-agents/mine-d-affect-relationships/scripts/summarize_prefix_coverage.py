#!/usr/bin/env python3
"""Preserve complete or budget-stopped prefix coverage without scoring survivors."""
import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path


def read(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def summarize(root):
    data = root / 'data/prefix_D-E09'
    run = root / 'runs/D-E09'
    chains = {c['chain_id']: c for c in read(data / 'chains.jsonl')}
    summaries, by_chain, checkpoints = [], {}, set()
    all_attempts, all_states = [], []
    for shard in [0, 1]:
        folder = run / ('memory_shard' + str(shard))
        meta = json.loads((folder / 'metadata.json').read_text())
        if not meta.get('finished_utc'):
            raise RuntimeError('Wait for all producer processes to finish; do not label running cost as final')
        attempts = read(folder / 'responses.jsonl')
        states = read(folder / 'states.jsonl')
        saved_runner = (folder / 'runner_source.py').read_text()
        assert sha(saved_runner) == meta['script_sha256']
        assert hashlib.sha256((data / 'chains.jsonl').read_bytes()).hexdigest() == meta['task_sha256']
        saved_system = next(ast.literal_eval(node.value) for node in ast.parse(saved_runner).body
                            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SYSTEM' for t in node.targets))
        index = {(r['task_id'], r['attempt']): r for r in attempts}
        assert len(index) == len(attempts)
        assert len(attempts) == meta['n_attempts'] and len(states) == meta['n_states']
        previous, positions = {}, Counter()
        for row in attempts:
            assert len(row['generated_token_ids']) == row['usage']['completion_tokens']
            assert sha(row['prior_profile']) == row['prior_profile_sha256']
            block = chains[row['chain_id']]['blocks'][row['step'] - 1]
            assert block['task_id'] == row['task_id'] and block['source_sha256'] == row['source_sha256']
            assert sha(block['passages']) == block['source_sha256']
            chain = chains[row['chain_id']]
            expected_user = f"Book: {chain['novel']}\nCharacter: {chain['character']}\n\nPrevious character profile:\n{row['prior_profile']}\n\nNext source passage in narrative order:\n{block['passages']}"
            assert row['messages'] == [dict(role='system', content=saved_system), dict(role='user', content=expected_user)]
        for state in states:
            chain_id = state['chain_id']
            chain = chains[chain_id]
            assert state['step'] == positions[chain_id] + 1
            positions[chain_id] += 1
            if chain_id in previous:
                assert state['prior_profile_sha256'] == previous[chain_id]
            assert state['profile_sha256'] == sha(state['profile'])
            row = index[state['task_id'], state['selected_attempt']]
            assert state['selected_response_sha256'] == sha(row['response'])
            assert state['profile'] == (row['prior_profile'] if state['carried_previous_after_invalid'] else row['response'])
            previous[chain_id] = state['profile_sha256']
            by_chain[chain_id] = dict(novel=chain['novel'], character_slug=chain['character_slug'],
                                     planned_windows=len(chain['blocks']), committed_windows=state['step'],
                                     complete=state['step'] == len(chain['blocks']),
                                     last_completed_source_unit=state['completed_through_unit'])
            if state['checkpoint'] is not None:
                checkpoints.add((state['novel'], state['character_slug'], state['checkpoint']))
        assert dict(positions) == meta['positions']
        committed_ids = {s['task_id'] for s in states}
        summaries.append(dict(shard=shard, complete=meta['complete'], finished_utc=meta['finished_utc'],
                              wall_s=meta['wall_s'], planned_windows=meta['n_blocks'],
                              attempts=len(attempts), committed_states=len(states),
                              attempts_by_number=dict(Counter(r['attempt'] for r in attempts)),
                              finishes=dict(Counter(r['finish_reason'] for r in attempts)),
                              carried_previous=sum(s['carried_previous_after_invalid'] for s in states),
                              raw_candidate_ids_without_committed_state=sorted({r['task_id'] for r in attempts} - committed_ids),
                              usage={k:sum(r['usage'][k] for r in attempts) for k in ['prompt_tokens', 'completion_tokens']}))
        all_attempts.extend(attempts)
        all_states.extend(states)
    coverage = []
    for task in read(data / 'actor_templates.jsonl'):
        trial = task['trial']
        ready = (trial['novel'], trial['character_slug'], trial['query_chapter']) in checkpoints
        coverage.append(dict(probe_id=trial['probe_id'], phase_idx=trial['phase_idx'],
                             novel=trial['novel'], character_slug=trial['character_slug'],
                             query_source_unit=trial['query_chapter'], committed_checkpoint_available=ready))
    actor_calls = sum(len(read(run / name / 'responses.jsonl')) for name in ['qwen3_8b', 'arcane_8b_dpo'] if (run / name / 'responses.jsonl').exists())
    judge_calls = sum(len(read(p)) for p in run.glob('*judge*/responses.jsonl'))
    return dict(experiment='D-E09', status='COMPLETE_PREFIX' if all(s['complete'] for s in summaries) else 'INCOMPLETE_PREFIX_BUDGET',
                model='Qwen/Qwen3-32B', model_revision='9216db5781bf21249d130ec9da846c4624c16137',
                planned_windows=sum(len(c['blocks']) for c in chains.values()),
                recorded_generation_attempts=len(all_attempts), committed_states=len(all_states),
                completed_planned_character_prefixes=sum(c['complete'] for c in by_chain.values()),
                planned_character_prefixes=len(chains),
                planned_actor_questions=len(coverage), checkpoint_material_available_for_questions=sum(c['committed_checkpoint_available'] for c in coverage),
                actor_calls=actor_calls, judge_calls=judge_calls,
                gpu_process_hours=sum(s['wall_s'] for s in summaries)/3600,
                usage={k:sum(r['usage'][k] for r in all_attempts) for k in ['prompt_tokens','completion_tokens']},
                shards=summaries, by_chain=by_chain, planned_question_coverage=coverage,
                integrity='Every recorded token count, source-window hash, prior-state hash and committed selection verified. Uncommitted raw candidates retained; no synthetic completion.',
                interpretation='Coverage and cost of the frozen ordinary reader pipeline only. Checkpoint material may include registered carry-forward after invalid output. No APF/PTF or survivor-cohort estimate; not a capability verdict on character growth or full-history methods.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asset-root', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    result = summarize(Path(args.asset_root))
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['shards','by_chain','planned_question_coverage']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
