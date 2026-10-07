"""E70 POST-HOC anomaly-targeted source/P recheck, not population accuracy audit."""
import argparse
import collections
import json
from pathlib import Path
import sys

from data import sha, write_jsonl
from data_v2 import digest


def build(root):
    parent = root.parent.parent
    original = parent / 'E52/qualified-v3.jsonl'
    source_rows = list(map(json.loads, original.read_text().splitlines()))
    rows91 = list(map(json.loads, (parent / 'E91/data-v1.jsonl').read_text().splitlines()))
    rows = []
    prior = []
    def add(sentence, question, old_labels, origin):
        uid = 'E70-spot:' + digest(json.dumps([sentence, question]))
        assert uid not in {r['item_id'] for r in rows}
        rows.append(dict(item_id=uid, sentence=sentence, sentence_sha256=digest(sentence),
                         question=question, question_format='yn', options=['Yes', 'No'], needs_revision=True))
        prior.append(dict(item_id=uid, old_labels=old_labels, origin=origin))
    wanted = [
        ('The patient refused the treatment continued causing uncomfortable scenes in the ER.', 'Did someone refuse the treatment to the patient?'),
        ('The patient refused the treatment continued causing uncomfortable scenes in the ER.', 'Did the patient refuse the treatment?'),
        ('The patient refused the treatment continued causing uncomfortable scenes in the ER.', 'Did the treatment cause uncomfortable scenes?'),
        ('While the cleaner mopped the floor was filled with stains.', 'Did the cleaner mop the floor?'),
        ('The corrupt politician handed the bill received unwelcome attention from southern voters.', 'Did someone hand the bill to the politician?'),
    ]
    for sentence, question in wanted:
        hits = [r for r in source_rows if r['sentence'] == sentence and r['question'] == question]
        assert hits
        add(sentence, question, sorted({r['step5_annotation']['label'] for r in hits}),
            dict(kind='source', original_item_ids=[r['item_id'] for r in hits], data_sha256=sha(original)))
    wanted_p = [
        ('While the cleaner mopped, the floor was filled with stains.', 'Did the cleaner mop the floor?'),
        ('While the assistant shaved, the overworked actor watched the sports news.', 'Did the assistant shave himself?'),
        ('The assistant was shaving. The actor, who was overworked, watched the sports news.', 'Did the assistant shave himself?'),
    ]
    for sentence, question in wanted_p:
        hits = [r for r in rows91 if r['interpretation'] == sentence]
        assert hits
        labels = [q['paraphrase_label'] for r in hits for q in r['atoms'] if q['question'] == question]
        assert labels
        add(sentence, question, sorted(set(labels)),
            dict(kind='interpretation', E91_item_ids=[r['item_id'] for r in hits], data_sha256=sha(parent / 'E91/data-v1.jsonl')))
    assert len(rows) == 8
    root.mkdir(parents=True, exist_ok=True)
    assert not (root / 'packets-v1.jsonl').exists()
    write_jsonl(root / 'packets-v1.jsonl', rows)
    write_jsonl(root / 'old-labels-v1.jsonl', prior)
    print(dict(items=8, data_sha256=sha(root / 'packets-v1.jsonl')))


def audit(root, workers):
    import step_gp_audit
    step_gp_audit.EFFORT = 'medium'
    step_gp_audit.PROMPT += '''
Semantic sanity checks: preserve the exact input word order. A final parse may use
licensed implicit grammar, but must not reorder the sentence, change a finite verb
into a participle, or silently add a new main-clause subject. Evaluate only events
asserted in this input; a plausible entity is not automatically an expressed missing
argument. Distinguish lexical reflexive readings from invented participant bindings.
Before assigning ENTAILED, check that the input really identifies the queried
participant/event. A merely possible extra event does not justify CONTRADICTED.
These are general checks, not clues to any particular answer.'''
    sys.argv = [sys.argv[0], '--data', str(root / 'packets-v1.jsonl'), '--out', str(root / 'step5'),
                '--workers', str(workers), '--batch-size', '5']
    step_gp_audit.main()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['build', 'audit'])
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--workers', type=int, choices=range(1, 9), default=2)
    a = p.parse_args()
    build(a.root) if a.mode == 'build' else audit(a.root, a.workers)
