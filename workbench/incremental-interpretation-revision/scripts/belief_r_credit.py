"""E93 author Belief-R data, unchanged pragmatic labels, two native forward modes."""
import argparse
import collections
import csv
import json
from pathlib import Path
import re
from data import sha, write_jsonl
from data_v2 import digest


MARKER = '\n\nWhat necessarily'
FORMAT = 'Begin! Reminder to write your final answer as "Final Answer [X]." and fill [X] with either a, b, or c.'
COT = 'Let’s think step by step.'


def canonical(s):
    # Only metadata linking; never applied to model-visible text or author Gold.
    s = s.strip().rstrip('.').replace('’', "'")
    for old, new in [("doesn't", 'does not'), ("don't", 'do not'), ("didn't", 'did not'),
                     ("isn't", 'is not'), ("aren't", 'are not'), ("can't", 'cannot'),
                     ("wasn't", 'was not'), ("weren't", 'were not'), ("hasn't", 'has not'),
                     ("haven't", 'have not'), ("won't", 'will not')]:
        s = s.replace(old, new)
    return ' '.join(s.split())


def build(root):
    upstream = root.parent/'upstream/belief-r/dataset/belief_r'
    basic = list(csv.DictReader((upstream/'basic_time_t.csv').open()))
    revised = list(csv.DictReader((upstream/'queries_time_t1.csv').open()))
    index = collections.defaultdict(list)
    for i, x in enumerate(basic):
        assert MARKER in x['questions'] and x['ground_truth'] in 'abc'
        old = x['questions'].split(MARKER)[0]
        key = x['modus'], canonical(old), *(canonical(x[k]) for k in 'abc')
        index[key].append((i, x))
    rows = []
    for i, x in enumerate(revised):
        assert MARKER in x['questions'] and x['ground_truth'] in 'abc'
        source, question = x['questions'].split(MARKER, 1)
        lines = source.splitlines()
        assert len(lines) == 3, (i, lines)
        prior, observation = '\n'.join(lines[:2]), lines[2]
        goal = ('What necessarily'+question).split('\n(a)')[0]
        assert goal and observation and all(x[k] for k in 'abc')
        key = x['modus'], canonical(prior), *(canonical(x[k]) for k in 'abc')
        linked = index.get(key, [])
        initial = {old['ground_truth'] for _, old in linked}
        assert len(initial) <= 1
        initial_gold = next(iter(initial)) if initial else None
        uid = 'E93:'+digest(str([i, x['questions'], x['ground_truth']]))
        rows.append(dict(x, item_id=uid, source_unit=uid, sentence=source,
                         sentence_sha256=digest(source), question=x['questions'], original_row_index=i,
                         cluster_id='Belief-R-atomic:'+x['atomic_idx'], initial_premises=prior,
                         new_observation=observation, goal=goal,
                         options={k: x[k] for k in 'abc'}, initial_gold=initial_gold,
                         initial_linked_indices=[j for j, _ in linked],
                         transition='UNKNOWN_PRIOR' if initial_gold is None else
                                    ('MAINTAIN' if initial_gold == x['ground_truth'] else 'UPDATE')))
    assert len(rows) == 1744
    root.mkdir(exist_ok=True)
    p = root/'data-v1.jsonl'
    assert not p.exists()
    write_jsonl(p, rows)
    manifest = dict(data_sha256=sha(p), author_basic_sha256=sha(upstream/'basic_time_t.csv'),
                    author_revised_sha256=sha(upstream/'queries_time_t1.csv'), rows=len(rows),
                    seed_groups=len({r['cluster_id'] for r in rows}),
                    transitions=dict(collections.Counter(r['transition'] for r in rows)),
                    author_gold=dict(collections.Counter(r['ground_truth'] for r in rows)),
                    new_actual_outputs=len(rows)*2*3, new_reconstruction_scores=len(rows)*3*3,
                    new_api_calls=0, author_questions_options_and_Gold_unchanged=True,
                    Gold_never_supplied_to_model=True,
                    task='Author human suppression/pragmatic labels; not a classical entailment oracle.')
    p.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(manifest, flush=True)


def forward(row, tok, mode):
    body = row['question']+'\n\n'+FORMAT
    if mode == 'FORWARD_COT':
        body += '\n\n'+COT
    prompt = tok.apply_chat_template([dict(role='user', content=body)], tokenize=False,
                                    add_generation_prompt=True, enable_thinking=mode == 'FORWARD_COT')
    return dict(row=row, mode=mode, prompt=prompt,
                cap=64 if mode == 'FORWARD_DIRECT' else 256)


def reconstruction(row, candidate, tok):
    prefix = ('Global Instruction: Maintain a concise faithful interpretation of observed premises.\n'
              'Goal: '+row['goal']+'\n'
              'Your new belief state is: <belief>'+row['options'][candidate]+'</belief>\n'
              'Your past belief state was: <belief>'+row['initial_premises']+'</belief>\n'
              'Your past action: <action>Read the newly provided premise.</action>\n'
              'Your past environment feedback: <environment>\n')
    text = prefix+row['new_observation']
    e = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    positions = [i for i, (a, b) in enumerate(e['offset_mapping']) if b > len(prefix)]
    assert positions and positions[0] > 0 and e['offset_mapping'][positions[0]][0] == len(prefix)
    assert e['input_ids'][:positions[0]] == tok.encode(prefix, add_special_tokens=False)
    return dict(row=row, candidate=candidate, ids=e['input_ids'], target_positions=positions,
                context_sha256=digest(prefix), prompt_sha256=digest(text))


def parse_answer(text):
    # Fixed before any scientific generation; only an explicit final choice or bare choice.
    found = re.findall(r'final\s*answer\s*[:：]?\s*\[?\s*([abc])\b', text, flags=re.I)
    if found:
        return found[-1].lower(), 'explicit_final_answer'
    match = re.fullmatch(r'\s*\[?([abc])\]?\s*[.。]?\s*', text, flags=re.I)
    return (match.group(1).lower(), 'bare_choice') if match else (None, 'UNKNOWN')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    build(p.parse_args().root)
