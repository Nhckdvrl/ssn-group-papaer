"""E98 same-source-prefix actual QA and interpretation, original community questions."""
import argparse
import json
from pathlib import Path

from data import sha, write_jsonl
from data_v2 import digest
from paraphrase_map import INSTRUCTION

MODES = ['NATIVE', 'GOAL', 'QUESTION_ONLY']
SYSTEM = 'Read the supplied text carefully and follow the task.'
QUESTION_ONLY = 'The reading goal is a question, not evidence; base your interpretation only on the sentence.'
QA_RULE = ('Answer Yes only if the sentence explicitly entails a yes answer to the question. '
           'Answer No if that answer is unasserted or contradicted. A plausible or merely compatible '
           'extra event is insufficient for Yes. Write only Yes or No.')


def prepare(row, tok, mode, readout):
    body = 'Read this sentence carefully.\n'
    if mode != 'NATIVE':
        body += 'Reading goal:\n'+row['reading_goal']+'\n'
    if mode == 'QUESTION_ONLY':
        body += QUESTION_ONLY+'\n'
    body += 'Sentence:\n'+row['sentence']+'\n\nTask:\n'
    task = INSTRUCTION if readout == 'PARAPHRASE' else 'Question:\n'+row['reading_goal']+'\n'+QA_RULE
    rendered = tok.apply_chat_template([dict(role='system', content=SYSTEM), dict(role='user', content=body+task)],
                                      tokenize=False, add_generation_prompt=True, enable_thinking=False)
    assert rendered.count(row['sentence']) == 1
    start = rendered.index(row['sentence'])
    end = start+len(row['sentence'])
    enc = tok(rendered, add_special_tokens=False, return_offsets_mapping=True)
    positions = [i for i, (a, b) in enumerate(enc['offset_mapping']) if a < end and b > start]
    assert positions
    return dict(row=row, mode=mode, readout=readout, prompt=rendered,
                source_prefix_tokens=enc['input_ids'][:max(positions)+1], cap=96 if readout == 'PARAPHRASE' else 64)


def build(root):
    parent = root.parent/'E96'
    pairs = list(map(json.loads, (parent/'data-v1.jsonl').read_text().splitlines()))
    original = list(map(json.loads, (root.parent/'E67/sources-v1.jsonl').read_text().splitlines()))
    goals = {r['sentence_sha256']: r for r in original}
    assert len(goals) == len(original), 'Source SHA must identify one original reading goal.'
    known = {}
    corrected = root.parent/'E91/data-posthoc-semantic-overlay-v1.jsonl'
    for r in map(json.loads, corrected.read_text().splitlines()):
        for q in r['atoms']:
            key = r['source_unit'], q['question']
            if key in known:
                assert known[key] == q['source_gold']
            known[key] = q['source_gold']
    rows = []
    for pair in pairs:
        for side in ['gp', 'control']:
            s = pair['sources'][side]
            old = goals.get(s['sentence_sha256'])
            if old:
                assert old['sentence'] == s['sentence']
                goal = old['reading_goals']['initial']
            else:
                # Fixed question-ID order, never select by Gold or observed output.
                goal = min(s['questions'], key=lambda q: q['question_id'])['question']
            rows.append(dict(item_id=s['source_unit'], pair_id=pair['item_id'], sentence=s['sentence'],
                sentence_sha256=s['sentence_sha256'], cluster_id=s['cluster_id'], construction=s['construction'],
                condition=side, original_E67_item_id=old['item_id'] if old else None,
                goal_origin='E67_INITIAL' if old else 'ORIGINAL_Q_FALLBACK',
                reading_goal=goal, goal_gold=known.get((s['source_unit'], goal)),
                goal_support=known.get((s['source_unit'], goal), 'UNKNOWN')))
    assert len(rows) == 100 and len({r['item_id'] for r in rows}) == 100
    root.mkdir(exist_ok=True)
    path = root/'data-v1.jsonl'
    assert not path.exists()
    write_jsonl(path, rows)
    counts = __import__('collections').Counter(r['goal_support'] for r in rows)
    m = dict(data_sha256=sha(path), original_E67_sources_sha256=sha(root.parent/'E67/sources-v1.jsonl'),
             fixed_E96_eligibility_sha256=sha(parent/'data-v1.jsonl'), corrected_E91_support_sha256=sha(corrected),
             sources=100, pairs=50, goal_support=dict(counts),
             goal_origin=dict(__import__('collections').Counter(r['goal_origin'] for r in rows)), actual_outputs=1800,
             new_source_annotation_calls=0, question_texts_original_and_unchanged=True,
             scope='Full fixed native sources. Goal support exact prior annotation match only; NA never guessed.')
    path.with_suffix('.manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    print(m)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    build(p.parse_args().root)
