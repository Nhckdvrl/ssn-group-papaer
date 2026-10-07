"""E95 actual comparisons of frozen interpretations; existing labels only."""
import argparse
import collections
import json
from pathlib import Path

from data import sha, write_jsonl
from data_v2 import digest


RECOVERY = ('Use the globally correct final grammatical parse of the reference sentence, '
            'rather than selecting an interpretation from its locally plausible prefix.')


def rank(a, b):
    if a is None or b is None:
        return None
    return (b > a + 1e-12) - (b < a - 1e-12)


def choice(order, value):
    if value is None:
        return None
    if value == 0:
        return 'c'
    preferred = 'TARGET_BANK' if value > 0 else 'BASE_BANK'
    return 'a' if order[0] == preferred else 'b'


def prompt(row, tok, mode, order_index):
    order = ['BASE_BANK', 'TARGET_BANK'] if order_index == 0 else ['TARGET_BANK', 'BASE_BANK']
    user = ('Compare two interpretations of the reference sentence only with respect to the '
            'propositions asked by the listed questions. A faithful interpretation preserves '
            'the facts the reference actually asserts and avoids adding facts it does not assert. '
            'Do not prefer an interpretation merely because it repeats more words, is more fluent, '
            'or is longer. Possible unstated events are not automatically denied.\n\n'
            'Reference sentence:\n' + row['sentence'] + '\n\n'
            'Questions defining the comparison:\n' + '\n'.join('- ' + q for q in row['questions']) + '\n\n'
            'A. ' + row['interpretations'][order[0]] + '\n\n'
            'B. ' + row['interpretations'][order[1]] + '\n\n'
            'C. Neither interpretation is more faithful on these registered propositions (tie).\n\n')
    if mode == 'RECOVERY':
        user += RECOVERY + '\n'
    user += 'Write only "Final Answer [X]." and replace [X] with a, b, or c.'
    rendered = tok.apply_chat_template([dict(role='user', content=user)], tokenize=False,
                                      add_generation_prompt=True, enable_thinking=False)
    return dict(row=dict(row, ground_truth=choice(order, row['fidelity_rank'])),
                prompt=rendered, cap=64, candidate_order=order)


def build(root):
    parent = root.parent / 'E91'
    data = parent / 'data-posthoc-semantic-overlay-v1.jsonl'
    rows = list(map(json.loads, data.read_text().splitlines()))
    groups = collections.defaultdict(dict)
    for row in rows:
        groups[row['generator'], row['source_unit']][row['operation']] = row
    out = []
    for (generator, source_unit), pair in sorted(groups.items()):
        b, t = pair['BASE_BANK'], pair['TARGET_BANK']
        assert b['sentence'] == t['sentence'] and b['atoms']
        assert [a['question'] for a in b['atoms']] == [a['question'] for a in t['atoms']]
        assert [a['source_gold'] for a in b['atoms']] == [a['source_gold'] for a in t['atoms']]
        def pattern(r):
            return sum((a['paraphrase_label'] == 'ENTAILED') == (a['source_gold'] == 'Yes') for a in r['atoms']) / len(r['atoms'])
        out.append(dict(item_id='E95:' + digest(str([generator, source_unit])),
                        generator=generator, source_unit=source_unit, sentence=b['sentence'],
                        sentence_sha256=b['sentence_sha256'], cluster_id=b['cluster_id'],
                        construction=b['construction'], condition=b['condition'],
                        questions=[a['question'] for a in b['atoms']],
                        interpretations={k: v['interpretation'] for k, v in pair.items()},
                        interpretation_sha256={k: v['interpretation_sha256'] for k, v in pair.items()},
                        E91_item_ids={k: v['item_id'] for k, v in pair.items()},
                        fidelity_rank=rank(b['semantic_fidelity'], t['semantic_fidelity']),
                        pattern_rank=rank(pattern(b), pattern(t)),
                        identical_interpretations=b['interpretation'] == t['interpretation']))
    assert len(out) == 324 and len({r['source_unit'] for r in out}) == 108
    root.mkdir(exist_ok=True)
    p = root / 'data-v1.jsonl'
    assert not p.exists()
    write_jsonl(p, out)
    manifest = dict(data_sha256=sha(p), parent_corrected_semantic_data_sha256=sha(data),
                    semantic_correction_map_sha256=sha(parent / 'posthoc-semantic-overlay-map-v1.json'),
                    paired_interpretations=len(out), sources=108, tasks_per_grader=len(out)*4,
                    new_api_calls=0, fidelity_eligible=sum(r['fidelity_rank'] is not None for r in out),
                    fidelity_rank_counts=dict(collections.Counter(str(r['fidelity_rank']) for r in out)),
                    pattern_rank_counts=dict(collections.Counter(str(r['pattern_rank']) for r in out)))
    p.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    build(p.parse_args().root)
