"""E43 minimal affirmative event facts, independently chosen patient names."""
import argparse
import json
import re
from pathlib import Path
from data import CACHE, sha, write_jsonl
from event_identity import digest
from named_patient_roles import adopt


def build(cache,directory):
    fields=json.loads((directory/'minimal-role-fields-v1.json').read_text());assert fields['model']=='gpt-6-luna'
    ff={r['id']:r for r in fields['rows']};assert len(ff)==24
    pf={r['id']:r for r in json.loads((cache/'E40-material-preparation-v1/plain-role-fields-v1.json').read_text())['rows']}
    parents=[r for r in map(json.loads,(cache/'E40-material-preparation-v1/probability-audited-v2.jsonl').read_text().splitlines()) if r['fact_realization']=='plain_mention_first']
    assert len(parents)==960
    raw,native,packets=[],[],[]
    for r in parents:
        sid=r['pair_id'].split(':')[1];f=ff[sid];p=pf[sid];role='source' if r['role_evidence']=='source_patient_stated' else 'other'
        oldprefix=r['source_anchor']+' '+p['identity_intro']+' '+p['facts']['plain_first_'+role]+' '
        assert r['sentence'].startswith(oldprefix)
        prefix=f['facts']['minimal_'+role]+' ';suffix=r['sentence'][len(oldprefix):]
        oldphrase=r['sentence'][r['target_start_char']:r['target_stop_char']]
        target=f['source_candidate' if r['target_kind']=='source_np' else 'other_candidate']
        relative_start=r['target_start_char']-len(oldprefix);relative_stop=r['target_stop_char']-len(oldprefix)
        assert suffix[relative_start:relative_stop]==oldphrase
        text=prefix+suffix[:relative_start]+target+suffix[relative_stop:]
        start=len(prefix)+relative_start;stop=start+len(target);assert text[start:stop]==target
        rid=f'P{len(raw):04d}'
        nr=dict(r,item_id='E43:'+r['item_id'],parent_item_id=r['item_id'],fact_realization='minimal_plain',
                source_candidate=f['source_candidate'],other_candidate=f['other_candidate'],sentence=text,sentence_sha256=digest(text),
                target_start_char=start,target_stop_char=stop,target_context_sha256=digest(text[:start]),target_phrase_sha256=digest(target),
                target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',text)) if w.start()<stop and w.end()>start],
                authored_followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(oldprefix.split()),
                role_context_sha256=digest(prefix.rstrip()),review_id=rid,eligible=False,acceptable=False,
                transformation='Minimal past-progressive assertion with independently authored proper names, no identity/candidate/report/exclusive scaffold. Original event bridge and readout frame retained; target phrase replaced by name.')
        for k in list(nr):
            if k.startswith('audit'):del nr[k]
        raw.append(nr)
        packets.append(dict(id=rid,task='probability',text=text,sentence_sha256=digest(text),role_context=prefix.rstrip(),role_context_sha256=digest(prefix.rstrip()),
                            target=target,target_phrase_sha256=digest(target),source_candidate=f['source_candidate'],other_candidate=f['other_candidate']))
        if r['readout_actor_mode']=='original_activity' and r['readout_frame']=='activity' and r['target_kind']=='source_np':
            nid=f'N{len(native)//2:04d}';question=f['current_question'];passage=prefix.rstrip()
            packet=dict(id=nid,task='role_question',passage=passage,passage_sha256=digest(passage),question=question,question_sha256=digest(question),source_candidate=f['source_candidate'],other_candidate=f['other_candidate']);packets.append(packet)
            for mode in ('base','priority'):
                native.append(dict(packet,item_id=nr['item_id']+':role_question:'+mode,context_id=nid,query='current',mode=mode,pair_id=r['pair_id'],verb_family=r['verb_family'],
                                   role_evidence=r['role_evidence'],fact_realization='minimal_plain',proposed_answer_class='source_candidate' if role=='source' else 'other_candidate',gold_answer_class=None,eligible=False))
    assert len(raw)==960 and len(native)==96 and len(packets)==1008
    write_jsonl(directory/'probability-candidates-v1.jsonl',raw);write_jsonl(directory/'question-candidates-v1.jsonl',native)
    packets.sort(key=lambda r:digest(r['id']))
    for i in range(2):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::2]),indent=2)+'\n')
    return dict(raw=960,native_contexts=48,native_variants=96,fields_sha256=sha(directory/'minimal-role-fields-v1.json'),candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt']);p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    print(json.dumps(build(a.cache,a.directory) if a.action=='build' else adopt(a.directory,a.reviews,'E43'),indent=2))
