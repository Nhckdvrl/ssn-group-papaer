"""E86 fixed published source, plain comprehension and frozen T3 grammar endpoint."""
import argparse
import collections
import json
from pathlib import Path
from data import sha
from data_v2 import digest
from current_open_baseline import prepare as strict_prepare


def build(parent, root):
    source = parent / 'data-v1.jsonl'
    rows = list(map(json.loads, source.read_text().splitlines()))
    assert len(rows) == 892
    output = [dict(r, task_kind='QA_PLAIN', original_item_id=r['item_id']) for r in rows]
    groups = collections.defaultdict(list)
    for r in rows:
        assert r['step5_grammar_agreed'] is True and r['step5_annotation']['grammar'] == 'acceptable'
        groups[r['source_unit']].append(r)
    assert len(groups) == 356
    for uid, group in sorted(groups.items()):
        r = min(group, key=lambda r: r['item_id'])
        assert len({x['sentence_sha256'] for x in group}) == 1
        assert len({x['analysis_cluster_id'] for x in group}) == 1
        output.append(dict(r, item_id='GRAM:' + uid, task_kind='GRAM_ACCEPT',
            original_item_id=r['item_id'], grounded_gold='Yes',
            question='Is the sentence grammatically acceptable exactly as printed?'))
    root.mkdir(parents=True, exist_ok=True)
    path = root / 'data-v1.jsonl'
    assert not path.exists()
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in output))
    (root / 'data-v1.manifest.json').write_text(json.dumps(dict(data_sha256=sha(path),
        parent_data_sha256=sha(source), QA_PLAIN=892, GRAM_ACCEPT=356,
        grammar_gold='All source members already T3 acceptable and independently agreed; no new label or audit.',
        new_conditions=14976), indent=2) + '\n')
    print('E86 built', sha(path), flush=True)


def prepare(rows, tok):
    originals = {r['original_item_id']: dict(r, item_id=r['original_item_id']) for r in rows if r['task_kind'] == 'QA_PLAIN'}
    parent = {(t['row']['item_id'], t['readout'], t['mapping']): t
              for t in strict_prepare(list(originals.values()), tok) if t['operation'] == 'DIRECT'}
    tasks = []
    for r in rows:
        for ro in ['words', 'letters']:
            for mp, shown in enumerate([['Yes', 'No'], ['No', 'Yes']]):
                old = parent[r['original_item_id'], ro, mp]
                body = 'Read this sentence carefully.\nSentence:\n' + r['sentence'] + '\n\nTask:\n'
                rule = ('Answer the comprehension question according to the supplied sentence.'
                        if r['task_kind'] == 'QA_PLAIN' else 'Judge whether the supplied sentence is grammatically acceptable exactly as printed.')
                body += rule + '\nQuestion:\n' + r['question']
                body += '\n' + '\n'.join(f'{a}. {b}' for a, b in zip(['A', 'B'], shown))
                body += '\nAnswer only ' + ('Yes or No.' if ro == 'words' else 'A or B.')
                prompt = tok.apply_chat_template([dict(role='user', content=body)], tokenize=False,
                    add_generation_prompt=True, enable_thinking=False)
                # Full native template prefix through Source is unchanged, not just source string equality.
                end = prompt.index('\n\nTask:\n')
                oldend = old['prompt'].index('\n\nTask:\n')
                assert prompt[:end] == old['prompt'][:oldend]
                assert tok.encode(prompt[:end], add_special_tokens=False) == tok.encode(old['prompt'][:oldend], add_special_tokens=False)
                if 'Qwen3.8' in tok.name_or_path:
                    assert prompt.endswith('<think>\n\n</think>\n\n')
                elif 'gemma-4' in tok.name_or_path:
                    assert prompt.endswith('<|channel>thought\n<channel|>')
                else:
                    assert prompt.endswith('[/INST]')
                choices = shown if ro == 'words' else ['A', 'B']
                seqs = [tok.encode(prompt + c, add_special_tokens=False) for c in choices]
                common = 0
                for pair in zip(*seqs):
                    if pair[0] != pair[1]:
                        break
                    common += 1
                assert all(len(s) == common + 1 for s in seqs)
                tasks.append(dict(row=r, operation='DIRECT', readout=ro, mapping=mp, prompt=prompt,
                    sequences=seqs, common=common, candidate_gold=shown.index(r['grounded_gold']),
                    parent_prompt_sha256=digest(old['prompt'])))
    return tasks


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--root', type=Path, required=True)
    a = p.parse_args()
    build(a.parent, a.root)
