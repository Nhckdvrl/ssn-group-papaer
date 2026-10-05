"""E45: fixed E40 scaffolding, independently checked proper-name substitution."""
import argparse
import json
import re
from pathlib import Path
from data import CACHE, sha, write_jsonl
from event_identity import digest
from named_patient_roles import adopt


def build(cache, directory):
    field_path = directory / 'scaffold-name-fields-v1.json'
    fields = json.loads(field_path.read_text())
    assert fields['model'] == 'gpt-6-luna'
    ff = {r['id']: r for r in fields['rows']}
    original = {r['id']: r for r in json.loads((cache / 'E40-material-preparation-v1/plain-role-fields-v1.json').read_text())['rows']}
    names = {r['id']: r for r in json.loads((cache / 'E43-material-preparation-v1/minimal-role-fields-v1.json').read_text())['rows']}
    assert ff.keys() == original.keys() == names.keys() and len(ff) == 24
    parents = list(map(json.loads, (cache / 'E40-material-preparation-v1/probability-audited-v2.jsonl').read_text().splitlines()))
    assert len(parents) == 1920
    raw, native, packets = [], [], []
    for r in parents:
        sid = r['pair_id'].split(':')[1]
        f, p, n = ff[sid], original[sid], names[sid]
        for key in ('source_candidate', 'other_candidate'):
            assert f[key] == n[key] and f['original_' + key] == p[key]
        role = 'source' if r['role_evidence'] == 'source_patient_stated' else 'other'
        order = 'first' if r['fact_realization'].endswith('_first') else 'last'
        key = 'plain_' + order + '_' + role
        # Semantic authoring is independent; this guard verifies only literal
        # substitutions, not equivalence of descriptions and proper names.
        def substitute(s):
            return s.replace(p['source_candidate'], '\x00SOURCE\x00').replace(p['other_candidate'], '\x00OTHER\x00').replace('\x00SOURCE\x00', f['source_candidate']).replace('\x00OTHER\x00', f['other_candidate'])
        assert f['identity_intro'] == substitute(p['identity_intro'])
        assert f['facts'][key] == substitute(p['facts'][key])
        assert f['current_question'] == p['current_question']
        oldprefix = r['source_anchor'] + ' ' + p['identity_intro'] + ' ' + p['facts'][key] + ' '
        prefix = r['source_anchor'] + ' ' + f['identity_intro'] + ' ' + f['facts'][key] + ' '
        assert r['sentence'].startswith(oldprefix)
        suffix = r['sentence'][len(oldprefix):]
        a, b = r['target_start_char'] - len(oldprefix), r['target_stop_char'] - len(oldprefix)
        oldtarget = suffix[a:b]
        assert oldtarget == p['source_candidate' if r['target_kind'] == 'source_np' else 'other_candidate']
        target = f['source_candidate' if r['target_kind'] == 'source_np' else 'other_candidate']
        text = prefix + suffix[:a] + target + suffix[b:]
        start, stop = len(prefix) + a, len(prefix) + a + len(target)
        assert text[start:stop] == target
        rid = f'P{len(raw):04d}'
        nr = dict(r, item_id='E45:' + r['item_id'], parent_item_id=r['item_id'],
                  source_candidate=f['source_candidate'], other_candidate=f['other_candidate'],
                  sentence=text, sentence_sha256=digest(text), target_start_char=start, target_stop_char=stop,
                  target_context_sha256=digest(text[:start]), target_phrase_sha256=digest(target),
                  target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',text)) if w.start()<stop and w.end()>start],
                  authored_followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(oldprefix.split()),
                  role_context_sha256=digest(prefix.rstrip()), review_id=rid, eligible=False, acceptable=False,
                  transformation='Replace the two E40 descriptive patient NPs with frozen E43 proper names, preserving E40 account/identity/report/event scaffolding and every other suffix word. This changes descriptive attributes and is not semantic equivalence.')
        for k in list(nr):
            if k.startswith('audit'): del nr[k]
        raw.append(nr)
        packets.append(dict(id=rid, task='probability', text=text, sentence_sha256=digest(text),
                            role_context=prefix.rstrip(), role_context_sha256=digest(prefix.rstrip()), target=target,
                            target_phrase_sha256=digest(target), source_candidate=f['source_candidate'], other_candidate=f['other_candidate']))
        if r['readout_actor_mode']=='original_activity' and r['readout_frame']=='activity' and r['target_kind']=='source_np':
            nid=f'N{len(native)//2:04d}'
            packet=dict(id=nid, task='role_question', passage=prefix.rstrip(), passage_sha256=digest(prefix.rstrip()),
                        question=f['current_question'], question_sha256=digest(f['current_question']),
                        source_candidate=f['source_candidate'], other_candidate=f['other_candidate'])
            packets.append(packet)
            for mode in ('base','priority'):
                native.append(dict(packet, item_id=nr['item_id']+':role_question:'+mode, context_id=nid, query='current', mode=mode,
                                   pair_id=r['pair_id'], verb_family=r['verb_family'], role_evidence=r['role_evidence'], fact_realization=r['fact_realization'],
                                   proposed_answer_class=role+'_candidate', gold_answer_class=None, eligible=False))
    assert len(raw)==1920 and len(native)==192 and len(packets)==2016
    write_jsonl(directory/'probability-candidates-v1.jsonl', raw)
    write_jsonl(directory/'question-candidates-v1.jsonl', native)
    packets.sort(key=lambda r:digest(r['id']))
    for i in range(3):
        (directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::3]),indent=2)+'\n')
    return dict(raw=1920, native_contexts=96, native_variants=192, fields_sha256=sha(field_path),
                candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt']);p.add_argument('--cache',type=Path,default=CACHE)
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    print(json.dumps(build(a.cache,a.directory) if a.action=='build' else adopt(a.directory,a.reviews,'E45'),indent=2))
