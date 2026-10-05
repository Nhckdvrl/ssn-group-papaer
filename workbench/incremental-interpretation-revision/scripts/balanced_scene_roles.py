"""E44 ordinary scene mentions, matched names and optional new-event readiness."""
import argparse
import json
import re
from pathlib import Path
from data import CACHE,sha,write_jsonl
from event_identity import digest
from named_patient_roles import adopt


def build(cache,directory):
    fields=json.loads((directory/'scene-role-fields-v1.json').read_text());assert fields['model']=='gpt-6-luna'
    ff={r['id']:r for r in fields['rows']};assert len(ff)==24
    pf={r['id']:r for r in json.loads((cache/'E43-material-preparation-v1/minimal-role-fields-v1.json').read_text())['rows']}
    parents=list(map(json.loads,(cache/'E43-material-preparation-v1/probability-audited-v1.jsonl').read_text().splitlines()));assert len(parents)==960
    raw,native,packets=[],[],[]
    for r in parents:
        sid=r['pair_id'].split(':')[1];f=ff[sid];p=pf[sid];role='source' if r['role_evidence']=='source_patient_stated' else 'other'
        for k in ('source_candidate','other_candidate'):assert f[k]==p[k]
        oldprefix=p['facts']['minimal_'+role]+' ';assert r['sentence'].startswith(oldprefix)
        for order in ('first','last'):
            prefix=f['facts'][f'balanced_{order}_{role}']+' '
            base_text=prefix+r['sentence'][len(oldprefix):]
            delta=len(prefix)-len(oldprefix)
            start0=r['target_start_char']+delta;stop0=r['target_stop_char']+delta
            followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(oldprefix.split())
            pos=list(re.finditer(r'\S+',base_text))[followup_start_word].start()
            for policy in (('no_protocol',) if r['readout_actor_mode']=='original_activity' else ('no_protocol','ready')):
                addition=f['ready_description']+' ' if policy=='ready' else ''
                text=base_text[:pos]+addition+base_text[pos:]
                start=start0+len(addition);stop=stop0+len(addition)
                target=r['sentence'][r['target_start_char']:r['target_stop_char']];assert text[start:stop]==target
                context=text[:pos+len(addition)].rstrip();rid=f'P{len(raw):04d}'
                nr=dict(r,item_id=f'E44:{order}:{policy}:{r["item_id"]}',parent_item_id=r['item_id'],fact_realization='balanced_mention_'+order,
                        scene_policy=policy,condition=r['condition']+':'+policy,sentence=text,sentence_sha256=digest(text),target_start_char=start,target_stop_char=stop,
                        target_context_sha256=digest(text[:start]),role_context_sha256=digest(context),
                        target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',text)) if w.start()<stop and w.end()>start],
                        authored_followup_start_word=followup_start_word+len(addition.split()),review_id=rid,eligible=False,acceptable=False,
                        transformation='Balanced ordinary presence mention plus original minimal role assertion; optional completion/readiness after new bridge only. Names and target-bearing continuation unchanged.')
                for k in list(nr):
                    if k.startswith('audit'):del nr[k]
                raw.append(nr)
                packets.append(dict(id=rid,task='probability',text=text,sentence_sha256=digest(text),role_context=context,role_context_sha256=digest(context),
                                    target=target,target_phrase_sha256=r['target_phrase_sha256'],source_candidate=f['source_candidate'],other_candidate=f['other_candidate'],policy=policy))
                old=r['readout_actor_mode']=='original_activity'
                primary_ready=policy=='ready' and r['readout_actor_mode']=='other_actor' and r['boundary_marker']=='same_began'
                if (old or primary_ready) and r['readout_frame']=='activity' and r['target_kind']=='source_np':
                    for query in (('current',) if old else ('current','availability')):
                        nid=f'N{len(native)//2:04d}';question=f['current_question' if query=='current' else 'availability_question']
                        packet=dict(id=nid,task='role_question' if query=='current' else 'availability_question',passage=context,passage_sha256=digest(context),
                                    question=question,question_sha256=digest(question),source_candidate=f['source_candidate'],other_candidate=f['other_candidate'],policy=policy);packets.append(packet)
                        gold=('source_candidate' if role=='source' else 'other_candidate') if query=='current' else 'both_ready'
                        for mode in ('base','priority'):
                            native.append(dict(packet,item_id=nr['item_id']+':'+query+':'+mode,context_id=nid,query=query,mode=mode,pair_id=r['pair_id'],verb_family=r['verb_family'],
                                               fact_realization=nr['fact_realization'],scene_policy=policy,role_evidence=r['role_evidence'],proposed_answer_class=gold,gold_answer_class=None,eligible=False))
    assert len(raw)==3456 and len(native)==576 and len(packets)==3744
    write_jsonl(directory/'probability-candidates-v1.jsonl',raw);write_jsonl(directory/'question-candidates-v1.jsonl',native)
    packets.sort(key=lambda r:digest(r['id']))
    for sh in range(3):(directory/f'review-packets-{sh}.json').write_text(json.dumps(dict(packets=packets[sh::3]),indent=2)+'\n')
    return dict(raw=3456,native_contexts=288,native_variants=576,fields_sha256=sha(directory/'scene-role-fields-v1.json'),candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


def split(directory):
    rr=list(map(json.loads,(directory/'probability-audited-v1.jsonl').read_text().splitlines()));assert len(rr)==3456
    for policy,n in [('no_protocol',1920),('ready',1536)]:
        r=[a for a in rr if a['scene_policy']==policy];assert len(r)==n
        p=directory/f'probability-{policy}-audited-v1.jsonl';assert not p.exists();write_jsonl(p,r)
        p.with_suffix('.audit.json').write_text(json.dumps(dict(variants=n,audited_sha256=sha(p),master_sha256=sha(directory/'probability-audited-v1.jsonl')),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt','split']);p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    if a.action=='build':print(json.dumps(build(a.cache,a.directory),indent=2))
    elif a.action=='adopt':print(json.dumps(adopt(a.directory,a.reviews,'E44'),indent=2))
    else:split(a.directory)
