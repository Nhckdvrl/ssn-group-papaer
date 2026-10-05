"""E41 independent completion/readiness clauses, unchanged E40 continuations."""
import argparse
import json
import re
from pathlib import Path
from data import CACHE, sha, write_jsonl
from event_identity import digest
from named_patient_roles import adopt

POLICIES = ('status_unknown', 'ended_only', 'ended_and_ready')


def build(cache, directory):
    j = json.loads((directory / 'availability-fields-v1.json').read_text())
    assert j['model'] == 'gpt-6-luna'
    ff = {r['id']: r for r in j['rows']}
    assert len(ff) == 24
    parents = [r for r in map(json.loads, (cache / 'E40-material-preparation-v1/probability-audited-v2.jsonl').read_text().splitlines()) if r['readout_actor_mode'] != 'original_activity']
    assert len(parents) == 1536
    raw, native, packets = [], [], []
    for r in parents:
        f = ff[r['pair_id'].split(':')[1]]
        assert f['source_candidate'] == r['source_candidate'] and f['other_candidate'] == r['other_candidate']
        words = list(re.finditer(r'\S+', r['sentence']))
        pos = words[r['authored_followup_start_word']].start()
        prefix = r['sentence'][:pos]
        for policy in POLICIES:
            addition = f['policies'][policy] + ' '
            text = prefix + addition + r['sentence'][pos:]
            start, stop = r['target_start_char'] + len(addition), r['target_stop_char'] + len(addition)
            phrase = r['sentence'][r['target_start_char']:r['target_stop_char']]
            assert text[start:stop] == phrase
            rid = f'P{len(raw):04d}'
            context = (prefix + addition).rstrip()
            nr = dict(r, item_id=f'E41:{policy}:{r["item_id"]}', parent_item_id=r['item_id'], availability_policy=policy,
                      condition=r['condition'] + ':' + policy, sentence=text, sentence_sha256=digest(text),
                      target_start_char=start, target_stop_char=stop, target_context_sha256=digest(text[:start]),
                      role_context_sha256=digest(context),
                      target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',text)) if w.start()<stop and w.end()>start],
                      authored_followup_start_word=r['authored_followup_start_word']+len(addition.split()),
                      review_id=rid, eligible=False, acceptable=False,
                      transformation='Insert matched unknown/completed/completed-and-ready description after the new event bridge; E40 role facts and complete continuation unchanged.')
            for k in list(nr):
                if k.startswith('audit'):
                    del nr[k]
            raw.append(nr)
            packets.append(dict(id=rid, task='probability', text=text, sentence_sha256=digest(text), role_context=context,
                                role_context_sha256=digest(context), target=phrase, target_phrase_sha256=r['target_phrase_sha256'],
                                source_candidate=f['source_candidate'], other_candidate=f['other_candidate'], policy=policy))
            if r['readout_actor_mode']=='other_actor' and r['boundary_marker']=='same_began' and r['readout_frame']=='activity' and r['target_kind']=='source_np':
                for query in ('current','availability'):
                    nid=f'N{len(native)//2:04d}'
                    question=f['current_question' if query=='current' else 'availability_question']
                    packet=dict(id=nid,task='role_question' if query=='current' else 'availability_question',passage=context,
                                passage_sha256=digest(context),question=question,question_sha256=digest(question),
                                source_candidate=f['source_candidate'],other_candidate=f['other_candidate'],policy=policy)
                    packets.append(packet)
                    gold=('source_candidate' if r['role_evidence']=='source_patient_stated' else 'other_candidate') if query=='current' else 'both_ready' if policy=='ended_and_ready' else 'unspecified'
                    for mode in ('base','priority'):
                        native.append(dict(packet,item_id=nr['item_id']+':'+query+':'+mode,context_id=nid,query=query,mode=mode,
                                           pair_id=r['pair_id'],verb_family=r['verb_family'],fact_realization=r['fact_realization'],
                                           availability_policy=policy,role_evidence=r['role_evidence'],proposed_answer_class=gold,gold_answer_class=None,eligible=False))
    assert len(raw)==4608 and len(native)==1152 and len(packets)==5184
    write_jsonl(directory/'probability-candidates-v1.jsonl',raw)
    write_jsonl(directory/'question-candidates-v1.jsonl',native)
    packets.sort(key=lambda r:digest(r['id']))
    for i in range(3):
        (directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::3]),indent=2)+'\n')
    return dict(raw=4608,native_contexts=576,native_variants=1152,fields_sha256=sha(directory/'availability-fields-v1.json'),
                candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


def split(directory):
    rows=list(map(json.loads,(directory/'probability-audited-v1.jsonl').read_text().splitlines()))
    assert len(rows)==4608
    for policy in POLICIES:
        rr=[r for r in rows if r['availability_policy']==policy];assert len(rr)==1536
        path=directory/f'probability-{policy}-audited-v1.jsonl';assert not path.exists()
        write_jsonl(path,rr)
        path.with_suffix('.audit.json').write_text(json.dumps(dict(variants=len(rr),audited_sha256=sha(path),master_sha256=sha(directory/'probability-audited-v1.jsonl')),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt','split']);p.add_argument('--cache',type=Path,default=CACHE)
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    if a.action=='build':print(json.dumps(build(a.cache,a.directory),indent=2))
    elif a.action=='adopt':print(json.dumps(adopt(a.directory,a.reviews,'E41'),indent=2))
    else:split(a.directory)
