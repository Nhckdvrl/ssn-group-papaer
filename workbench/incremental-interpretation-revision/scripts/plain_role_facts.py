"""E40 remove exhaustivity while preserving E39 entities and continuations."""
import argparse
import json
import re
from pathlib import Path
from data import CACHE, sha, write_jsonl
from event_identity import digest
from named_patient_roles import adopt


def build(cache, directory):
    j = json.loads((directory / 'plain-role-fields-v1.json').read_text())
    assert j['model'] == 'gpt-6-luna'
    ff = {r['id']: r for r in j['rows']}
    parent_fields = {r['id']: r for r in json.loads((cache / 'E39-material-preparation-v1/named-role-fields-v2.json').read_text())['rows']}
    assert ff.keys() == parent_fields.keys() and len(ff) == 24
    parents = [r for r in map(json.loads, (cache / 'E39-material-preparation-v1/probability-audited-v1.jsonl').read_text().splitlines()) if r['fact_realization'] != 'contrast_named']
    assert len(parents) == 1920
    raw, native, packets = [], [], []
    for r in parents:
        sid = r['pair_id'].split(':')[1]
        f, pf = ff[sid], parent_fields[sid]
        for key in ('source_candidate', 'other_candidate', 'identity_intro'):
            assert f[key] == pf[key]
        is_source = r['role_evidence'] == 'source_patient_only'
        role = 'source' if is_source else 'other'
        order = 'first' if r['fact_realization'].endswith('_first') else 'last'
        oldfact = pf['facts'][f'affirmative_{order}_{role}']
        fact = f['facts'][f'plain_{order}_{role}']
        assert not re.search(r'\b(only|not|but|sole|solely|exclusively|exclusive|alone)\b', fact, re.I)
        oldprefix = r['source_anchor'] + ' ' + pf['identity_intro'] + ' ' + oldfact + ' '
        prefix = r['source_anchor'] + ' ' + f['identity_intro'] + ' ' + fact + ' '
        assert r['sentence'].startswith(oldprefix)
        text = prefix + r['sentence'][len(oldprefix):]
        delta = len(prefix) - len(oldprefix)
        start, stop = r['target_start_char'] + delta, r['target_stop_char'] + delta
        phrase = r['sentence'][r['target_start_char']:r['target_stop_char']]
        assert text[start:stop] == phrase
        rid = f'P{len(raw):04d}'
        nr = dict(r, item_id='E40:' + r['item_id'], parent_item_id=r['item_id'], review_id=rid,
                  parent_role_evidence=r['role_evidence'], role_evidence=role + '_patient_stated',
                  fact_realization='plain_mention_' + order, sentence=text, sentence_sha256=digest(text),
                  target_start_char=start, target_stop_char=stop, target_context_sha256=digest(text[:start]),
                  role_context_sha256=digest(prefix.rstrip()),
                  target_span_word_indices=[i for i, w in enumerate(re.finditer(r'\S+', text)) if w.start() < stop and w.end() > start],
                  authored_followup_start_word=r['authored_followup_start_word'] + len(prefix.split()) - len(oldprefix.split()),
                  eligible=False, acceptable=False,
                  transformation='Non-exhaustive affirmative role assertion with unused-entity mention; E39 distinct entities and suffix unchanged.')
        for k in list(nr):
            if k.startswith('audit'):
                del nr[k]
        raw.append(nr)
        packets.append(dict(id=rid, task='probability', text=text, sentence_sha256=digest(text),
                            role_context=prefix.rstrip(), role_context_sha256=digest(prefix.rstrip()), target=phrase,
                            target_phrase_sha256=nr['target_phrase_sha256'], source_candidate=f['source_candidate'], other_candidate=f['other_candidate']))
        if r['readout_actor_mode'] == 'original_activity' and r['readout_frame'] == 'activity' and r['target_kind'] == 'source_np':
            nid = f'N{len(native)//2:04d}'
            question = f['current_question']
            packet = dict(id=nid, task='role_question', passage=prefix.rstrip(), passage_sha256=digest(prefix.rstrip()),
                          question=question, question_sha256=digest(question), source_candidate=f['source_candidate'], other_candidate=f['other_candidate'])
            packets.append(packet)
            for mode in ('base', 'priority'):
                native.append(dict(packet, item_id=nr['item_id'] + ':role_question:' + mode, context_id=nid,
                                   query='current', mode=mode, pair_id=r['pair_id'], verb_family=r['verb_family'],
                                   role_evidence=nr['role_evidence'], fact_realization=nr['fact_realization'],
                                   proposed_answer_class='source_candidate' if is_source else 'other_candidate', gold_answer_class=None, eligible=False))
    assert len(raw) == 1920 and len(native) == 192 and len(packets) == 2016
    write_jsonl(directory / 'probability-candidates-v1.jsonl', raw)
    write_jsonl(directory / 'question-candidates-v1.jsonl', native)
    packets.sort(key=lambda r: digest(r['id']))
    for i in range(2):
        (directory / f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::2]), indent=2) + '\n')
    return dict(raw=1920, native_contexts=96, native_variants=192, fields_sha256=sha(directory / 'plain-role-fields-v1.json'),
                candidate_sha256={k: sha(directory / f'{k}-candidates-v1.jsonl') for k in ('probability', 'question')})


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['build', 'adopt'])
    p.add_argument('--cache', type=Path, default=CACHE)
    p.add_argument('--directory', type=Path, required=True)
    p.add_argument('--reviews', type=Path, nargs='+')
    p.add_argument('--version', type=int, choices=[1, 2], default=1)
    a = p.parse_args()
    print(json.dumps(build(a.cache, a.directory) if a.action == 'build' else adopt(a.directory, a.reviews, 'E40', a.version), indent=2))
