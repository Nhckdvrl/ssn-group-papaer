"""E96 current native writers, original paired community sentences, no new source Gold."""
import argparse
import json
from pathlib import Path

from data import sha, write_jsonl
from data_v2 import digest
from paraphrase_map import INSTRUCTION, EXAMPLES


def prompt(row, side, tok):
    user = EXAMPLES + '\nSentence: ' + row['sources'][side]['sentence'] + '\nSplitted:\n'
    return tok.apply_chat_template([dict(role='system', content=INSTRUCTION), dict(role='user', content=user)],
                                   tokenize=False, add_generation_prompt=True, enable_thinking=False)


def build(root):
    parent = root.parent / 'E92'
    data = parent / 'data-posthoc-semantic-overlay-v1.jsonl'
    sources = {}
    for r in map(json.loads, data.read_text().splitlines()):
        source = dict(source_unit=r['source_unit'], sentence=r['original_sentence'],
                      sentence_sha256=r['original_sentence_sha256'], condition=r['condition'],
                      cluster_id=r['cluster_id'], construction=r['construction'],
                      other_unit=r['alternate_source_unit'],
                      questions=[{k: a[k] for k in ['question_id', 'question', 'source_gold']} for a in r['atoms']])
        if source['source_unit'] in sources:
            assert source == sources[source['source_unit']]
        sources[source['source_unit']] = source
    rows = []
    for uid, s in sorted(sources.items()):
        if s['condition'] != 'gp':
            continue
        other = sources[s['other_unit']]
        assert other['condition'] == 'control' and other['other_unit'] == uid
        assert s['questions'] == other['questions'] and s['cluster_id'] == other['cluster_id']
        for source in [s, other]:
            assert digest(source['sentence']) == source['sentence_sha256']
        rows.append(dict(item_id='E96:' + digest(str(sorted([uid, s['other_unit']]))),
                         cluster_id=s['cluster_id'], sentence_sha256=s['sentence_sha256'],
                         construction=s['construction'], sources={'gp': s, 'control': other},
                         questions=s['questions']))
    assert len(rows) == 50 and len({r['item_id'] for r in rows}) == 50
    root.mkdir(exist_ok=True)
    dest = root / 'data-v1.jsonl'
    assert not dest.exists()
    write_jsonl(dest, rows)
    report = dict(data_sha256=sha(dest), parent_corrected_E92_sha256=sha(data),
                  corrected_E92_map_sha256=sha(parent / 'posthoc-semantic-overlay-map-v1.json'),
                  frozen_eligibility_sha256=sha(parent / 'input-eligibility-v1.jsonl'),
                  pairs=50, sources=100, actual_outputs=300, self_reconstruction_scores=600,
                  prompt='Original E53 author instruction and four examples; native nonthinking, fixed96 cap.',
                  questions_per_model=sum(2*len(r['questions']) for r in rows),
                  scope='No source re-audit, all prior common-Q eligibility fixed; new outputs alone are annotated.')
    dest.with_suffix('.manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    build(p.parse_args().root)
