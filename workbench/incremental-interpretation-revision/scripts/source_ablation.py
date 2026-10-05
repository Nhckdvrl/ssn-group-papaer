"""E29: event-only source ablation, retaining correction and readout verbatim.

This removes the whole S1, not only ambiguity. Independent review determines
whether the event anchor and later roles remain interpretable. No source gold
or earlier annotation is overwritten.
"""
import argparse
import collections
import json
from pathlib import Path
import re
from data import CACHE, sha, write_jsonl
from event_identity import digest
from correction_transfer import load_published


def build(cache, out):
    assert not out.exists()
    out.mkdir(parents=True)
    fields = {r['id']: r for r in json.loads((cache/'E24-material-preparation-v1/fields-v3.json').read_text())['rows']}
    source = {(r['pair_id'], r['condition']): r['sentence'] for r in load_published(cache) if r['construction']=='NPZ' and r['question_type']=='ambcor'}
    probability = []
    for ex in ('E24', 'E25'):
        for r in map(json.loads, (cache/f'{ex}-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()):
            if r['condition']!='gp' or r['target_kind']=='source_reference':
                continue
            f = fields[r['pair_id'].split(':')[1]]
            article = 'an' if f['activity_np'].startswith(('act of ', 'embrace')) else 'a'
            anchor = f['actor'][0].upper()+f['actor'][1:]+' took part in '+article+' '+f['activity_np']+'.'
            old = source[(r['pair_id'],r['condition'])]
            assert r['sentence'].startswith(old+' ')
            text = anchor+r['sentence'][len(old):]
            delta = len(anchor)-len(old)
            start, stop = r['target_start_char']+delta, r['target_stop_char']+delta
            words = list(re.finditer(r'\S+', text))
            indices = [i for i,w in enumerate(words) if w.start()<stop and w.end()>start]
            assert text[start:stop]==r['sentence'][r['target_start_char']:r['target_stop_char']]
            row = dict(r, item_id='E29:'+r['item_id'], parent_item_id=r['item_id'], parent_experiment=ex,
                       sentence=text, condition='event_anchor_only', source_anchor=anchor,
                       source_anchor_sha256=digest(anchor), sentence_sha256=digest(text),
                       target_start_char=start, target_stop_char=stop, target_span_word_indices=indices,
                       target_context_sha256=digest(text[:start]),
                       authored_followup_start_word=r['authored_followup_start_word']+len(anchor.split())-len(old.split()),
                       readout_actor_mode='original_activity' if ex=='E24' else r['readout_actor_mode'],
                       prior_faithful=r['faithful_role_frame'] if ex=='E24' else r['faithful_scope_actor'],
                       eligible=False, acceptable=False, faithful_ablation=False,
                       transformation='Replace full source S1 with actor/activity-only existential episode anchor; keep correction/bridge/readout/target verbatim. This also removes the source patient mention and matrix proposition.')
            for k in list(row):
                if k.startswith('audit'): del row[k]
            probability.append(row)
    nli = []
    for r in map(json.loads,(cache/'E28-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()):
        if r['condition']!='gp': continue
        f = fields[r['pair_id'].split(':')[1]]
        article = 'an' if f['activity_np'].startswith(('act of ', 'embrace')) else 'a'
        anchor = f['actor'][0].upper()+f['actor'][1:]+' took part in '+article+' '+f['activity_np']+'.'
        old = source[(r['pair_id'],r['condition'])]
        assert r['passage'].startswith(old+' ')
        passage = anchor+r['passage'][len(old):]
        row = dict(r, item_id='E29:'+r['item_id'], parent_item_id=r['item_id'],
                   passage=passage, condition='event_anchor_only', source_anchor=anchor,
                   source_anchor_sha256=digest(anchor), sentence_sha256=digest(passage),
                   gold_relation=None, prior_relation=r['gold_relation'], eligible=False,
                   faithful_ablation=False)
        for k in list(row):
            if k.startswith('audit'): del row[k]
        nli.append(row)
    assert len(probability)==1152 and len(nli)==480
    write_jsonl(out/'probability-candidates-v1.jsonl',probability)
    write_jsonl(out/'nli-candidates-v1.jsonl',nli)
    packets=[]; mapping={}
    for task,rows in (('probability',probability),('nli',nli)):
        for i,r in enumerate(rows):
            key=('P' if task=='probability' else 'N')+f'{i:04d}'
            mapping[key]=r['item_id']
            p=dict(id=key,task=task,text=r['sentence'] if task=='probability' else r['passage'],
                   sentence_sha256=r['sentence_sha256'],anchor=r['source_anchor'])
            if task=='probability':p.update(target=r['sentence'][r['target_start_char']:r['target_stop_char']],target_phrase_sha256=r['target_phrase_sha256'],readout_frame=r['readout_frame'])
            else:p.update(proposition=r['proposition'],proposition_sha256=r['proposition_sha256'])
            packets.append(p)
    (out/'review-id-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    # Equal task composition in two independent audit shards, with opaque IDs.
    for shard in (0,1):
        pp=[p for i,p in enumerate(packets) if i%2==shard]
        assert len(pp)==816
        (out/f'review-packets-{shard}.json').write_text(json.dumps(dict(packets=pp),indent=2)+'\n')
    return dict(probability_variants=1152,nli_variants=480,source_items=24,verb_families=12,
                probability_sha256=sha(out/'probability-candidates-v1.jsonl'),nli_sha256=sha(out/'nli-candidates-v1.jsonl'))


def adopt(directory,reviews):
    mapping=json.loads((directory/'review-id-map.json').read_text());ann={}
    for path in reviews:
        j=json.loads(path.read_text());assert j['model']=='gpt-6-luna'
        for r in j['reviews']:
            key=mapping[r['id']];assert key not in ann;ann[key]=(r,sha(path))
    assert len(ann)==1632
    reports={}
    for task in ('probability','nli'):
        data=directory/f'{task}-candidates-v1.jsonl';rows=list(map(json.loads,data.read_text().splitlines()))
        for r in rows:
            a,h=ann[r['item_id']];assert a['sentence_sha256']==r['sentence_sha256']
            assert a['grammaticality'] in ('acceptable','marginal','unacceptable')
            assert a['old_fact_scope'] in ('local_old_activity','broader_or_changed','uncertain')
            assert a['anchor_coherent'] in (True,False,None)
            r.update(audit=a,audit_review_sha256=h,eligible=a['grammaticality']!='unacceptable' and a['anchor_coherent'] is True,
                     acceptable=a['grammaticality']=='acceptable' and a['anchor_coherent'] is True,
                     faithful_ablation=a['old_fact_scope']=='local_old_activity' and a['anchor_coherent'] is True and a['grammaticality']!='unacceptable')
            if task=='nli':
                assert a['proposition_sha256']==r['proposition_sha256']
                assert a['relation'] in ('entailed','contradicted','undetermined',None)
                assert a['certainty'] in ('clear','interpretation_dependent','invalid')
                r['gold_relation']=a['relation'] if a['certainty']=='clear' else None
            else:
                assert a['target_phrase_sha256']==r['target_phrase_sha256']
                assert a['target_role'] in ('old_activity_patient','new_activity_patient','neutral_entity','uncertain')
                expect='neutral_entity' if r['readout_frame']=='neutral_entity' else 'old_activity_patient' if r['readout_actor_mode']=='original_activity' else 'new_activity_patient'
                r['faithful_ablation']=r['faithful_ablation'] and a['target_role']==expect
        path=directory/f'{task}-audited-v1.jsonl';assert not path.exists();write_jsonl(path,rows)
        report=dict(variants=len(rows),source_items=24,verb_families=12,candidate_sha256=sha(data),audited_sha256=sha(path),
                    eligible=sum(r['eligible'] for r in rows),acceptable=sum(r['acceptable'] for r in rows),
                    faithful_ablation=sum(r['faithful_ablation'] for r in rows),
                    grammar_counts=dict(collections.Counter(r['audit']['grammaticality'] for r in rows)),
                    review_sha256=[sha(p) for p in reviews])
        if task=='nli':report.update(clear_gold=sum(r['gold_relation'] is not None for r in rows),relation_agreement_with_parent=sum(r['gold_relation']==r['prior_relation'] for r in rows))
        path.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');reports[task]=report
    return reports


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--directory',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True)
    x=p.parse_args();print(json.dumps(build(x.cache,x.out) if x.action=='build' else adopt(x.directory,x.reviews),indent=2))
