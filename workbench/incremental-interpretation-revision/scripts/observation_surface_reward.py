"""E92 one alternate published observation per unchanged E91 interpretation."""
import argparse
import collections
import json
from pathlib import Path
from data import sha, write_jsonl
from reconstruction_reward import context


def build(root):
    parent = root.parent/'E91'
    rows = [json.loads(s) for s in (parent/'data-v1.jsonl').read_text().splitlines()]
    sources = {r['sentence_sha256']: r for r in map(json.loads, (root.parent/'E63/sources-v1.jsonl').read_text().splitlines())}
    questions = {r['sentence_sha256']: {a['question']: a['source_gold'] for a in r['atoms']} for r in rows}
    excluded = []
    eligibility = {}
    for sh, q in questions.items():
        target = sources[sh]['donor_sentence_sha256']
        assert sources[target]['donor_sentence_sha256'] == sh
        other = questions[target]
        common = q.keys() & other.keys()
        assert common
        conflicts = [x for x in sorted(common) if q[x] != other[x]]
        record = dict(source_unit=sources[sh]['item_id'], source_sha256=sh, alternate_sha256=target,
                      common_questions=sorted(common), conflicting_questions=conflicts,
                      unique_original_questions=sorted(q.keys()-other.keys()),
                      unique_alternate_questions=sorted(other.keys()-q.keys()))
        eligibility[sh] = record
        if conflicts:
            excluded.append(record)
    out = []
    for r in rows:
        e = eligibility[r['sentence_sha256']]
        if e['conflicting_questions']:
            continue
        paired = sources[e['alternate_sha256']]
        atoms = [a for a in r['atoms'] if a['question'] in e['common_questions']]
        labels = collections.defaultdict(list)
        for a in atoms:
            labels[a['source_gold']].append(a['paraphrase_label'])
        def mean(g, predicate):
            return sum(predicate(x) for x in labels[g])/len(labels[g]) if labels[g] else None
        pos = mean('Yes', lambda x: x == 'ENTAILED')
        over = mean('No', lambda x: x == 'ENTAILED')
        new = dict(r, original_sentence=r['sentence'], original_sentence_sha256=r['sentence_sha256'],
                   sentence=paired['sentence'], sentence_sha256=paired['sentence_sha256'],
                   alternate_source_unit=paired['item_id'], all_original_atoms=r['atoms'], atoms=atoms,
                   original_positive_retention=r['positive_retention'],
                   original_unsupported_assertion=r['unsupported_assertion'],
                   original_semantic_fidelity=r['semantic_fidelity'],
                   positive_retention=pos, unsupported_assertion=over,
                   semantic_fidelity=None if pos is None or over is None else pos-over,
                   positive_omission=mean('Yes', lambda x: x == 'NEITHER'),
                   positive_contradiction=mean('Yes', lambda x: x == 'CONTRADICTED'),
                   meaning_scope='Only common original published Q with identical existing source-support Gold; full semantic equivalence not certified.')
        assert context(new) == context(r)
        out.append(new)
    assert len(out) == 600 and len(excluded) == 8
    root.mkdir(exist_ok=True)
    p = root/'data-v1.jsonl'
    assert not p.exists()
    write_jsonl(p, out)
    write_jsonl(root/'input-eligibility-v1.jsonl', [eligibility[x] for x in sorted(eligibility)])
    write_jsonl(root/'excluded-source-v1.jsonl', excluded)
    manifest = dict(data_sha256=sha(p), parent_E91_sha256=sha(parent/'data-v1.jsonl'),
                    rows=len(out), scores=len(out)*3, new_api_calls=0, source_units=100,
                    excluded_sources=len(excluded), excluded_pairs=4,
                    semantic_readout='Recomputed solely on matched common-Q atoms, existing blind P labels and original Gold; original all-atom metrics retained.',
                    interpretation_sha_unchanged=True, context_bytes_unchanged=True)
    p.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(manifest, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    build(p.parse_args().root)
