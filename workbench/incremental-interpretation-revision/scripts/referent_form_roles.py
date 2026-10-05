"""E48 frozen name/description crossover; semantic judgments stay external."""
import argparse
import itertools
import json
import re
from pathlib import Path
from data import CACHE, sha, write_jsonl
from event_identity import digest
from named_patient_roles import adopt

FORMS = ('name', 'description')


def build(cache, directory):
    author = json.loads((directory/'alias-role-fields-v2.json').read_text())
    assert author['model'] == 'gpt-6-luna'
    ff = {r['id']: r for r in author['rows']}
    def fields(ex, version, filename):
        return {r['id']: r for r in json.loads((cache/f'{ex}-material-preparation-v{version}'/filename).read_text())['rows']}
    minimal = fields('E43', 1, 'minimal-role-fields-v1.json')
    inventory = fields('E47', 2, 'identity-status-fields-v2.json')
    parents = [r for r in map(json.loads, (cache/'E46-material-preparation-v1/probability-audited-v1.jsonl').read_text().splitlines()) if r['scaffold_cell']=='I0R0E0']
    assert len(parents)==1152 and len(ff)==24 and ff.keys()==minimal.keys()==inventory.keys()
    raw, native, packets = [], [], []
    def question(packet, parent, gold, realization, **metadata):
        packets.append(packet)
        for mode in ('base', 'priority'):
            native.append(dict(packet, item_id='E48:'+packet['id']+':'+mode, context_id=packet['id'], mode=mode,
                               pair_id=parent['pair_id'], verb_family=parent['verb_family'],
                               role_evidence=parent['role_evidence'], fact_realization=realization,
                               proposed_answer_class=gold, gold_answer_class=None, eligible=False, **metadata))
    for fact_form, target_form, roster in itertools.product(FORMS, FORMS, (0,1)):
        for r in parents:
            sid=r['pair_id'].split(':')[1]; f,m,inv=ff[sid],minimal[sid],inventory[sid]
            for role in ('source','other'):
                assert f[role+'_candidate']==m[role+'_candidate']==inv[role+'_candidate']
                assert f['facts']['minimal_'+role]==m['facts']['minimal_'+role]
            role='source' if r['role_evidence']=='source_patient_stated' else 'other'
            unused='other' if role=='source' else 'source'; order=r['fact_order']
            old_role=m['facts']['minimal_'+role]; old_nearby=f[unused+'_candidate']+' was nearby.'
            old_prefix=' '.join((old_nearby,old_role) if order=='first' else (old_role,old_nearby))+' '
            assert r['sentence'].startswith(old_prefix)
            new_role=f['facts']['minimal_'+('desc_' if fact_form=='description' else '')+role]
            unused_phrase=f[unused+('_description' if fact_form=='description' else '_candidate')]
            nearby=unused_phrase[0].upper()+unused_phrase[1:]+' was nearby.'
            fact=' '.join((nearby,new_role) if order=='first' else (new_role,nearby))
            prefix=' '.join([f['alias_intro']]+([inv['name_inventory']] if roster else [])+[fact])+' '
            a0,b0=r['target_start_char'],r['target_stop_char']
            target_role='source' if r['target_kind']=='source_np' else 'other'
            assert r['sentence'][a0:b0]==f[target_role+'_candidate']
            target=f[target_role+('_description' if target_form=='description' else '_candidate')]
            before=prefix+r['sentence'][len(old_prefix):a0]
            text=before+target+r['sentence'][b0:]; a=len(before); b=a+len(target)
            rid=f'P{len(raw):05d}'; realization=f'{fact_form}_to_{target_form}_I{roster}_{order}'
            nr=dict(r,item_id='E48:'+realization+':'+r['item_id'],parent_item_id=r['item_id'],review_id=rid,
                    fact_form=fact_form,target_form=target_form,inventory_present=roster,fact_realization=realization,
                    sentence=text,sentence_sha256=digest(text),target_start_char=a,target_stop_char=b,
                    target_context_sha256=digest(text[:a]),target_phrase_sha256=digest(target),role_context_sha256=digest(prefix.rstrip()),
                    target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',text)) if w.start()<b and w.end()>a],
                    authored_followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(old_prefix.split()),
                    fields_sha256=sha(directory/'alias-role-fields-v2.json'),eligible=False,acceptable=False,
                    transformation='Preserve actors, old/new scope and readout frames; independently authored alias mapping, crossed fact/readout names versus anchored descriptions, optional frozen E47 inventory. No exclusive role gold.')
            for k in list(nr):
                if k.startswith('audit'): del nr[k]
            raw.append(nr)
            shared={k:f[k] for k in ('source_candidate','other_candidate','source_description','other_description','alias_intro')}
            packets.append(dict(id=rid,task='probability',text=text,sentence_sha256=digest(text),role_context=prefix.rstrip(),role_context_sha256=digest(prefix.rstrip()),
                                target=target,target_phrase_sha256=digest(target),**shared))
            if target_form=='name' and r['readout_actor_mode']=='original_activity' and r['readout_frame']=='activity' and r['target_kind']=='source_np':
                q=f['current_question']; nid=f'N{len(native)//2:04d}'
                question(dict(id=nid,task='role_question',query='current',passage=prefix.rstrip(),passage_sha256=digest(prefix.rstrip()),question=q,question_sha256=digest(q),**shared),
                         r,role+'_candidate',f'{fact_form}_I{roster}_{order}',fact_form=fact_form,inventory_present=roster,fact_order=order)
    for sid,f in ff.items():
        r=next(r for r in parents if r['pair_id'].split(':')[1]==sid)
        for role in ('source','other'):
            q=f['alias_question_'+role]; passage=f['alias_intro']; nid=f'N{len(native)//2:04d}'
            shared={k:f[k] for k in ('source_candidate','other_candidate','source_description','other_description','alias_intro')}
            question(dict(id=nid,task='role_question',query='alias',passage=passage,passage_sha256=digest(passage),question=q,question_sha256=digest(q),**shared),
                     dict(r,role_evidence=role+'_patient_stated'),role+'_candidate','alias_mapping',fact_form='alias',inventory_present=0,fact_order='none')
    assert len(raw)==9216 and len(native)==864 and len(packets)==9648, (len(raw),len(native),len(packets))
    assert len({r['item_id'] for r in raw})==len(raw) and len({r['item_id'] for r in native})==len(native)
    write_jsonl(directory/'probability-candidates-v1.jsonl',raw);write_jsonl(directory/'question-candidates-v1.jsonl',native)
    packets.sort(key=lambda r:digest(r['id']))
    for i in range(3):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::3]),indent=2)+'\n')
    return dict(raw=len(raw),native_variants=len(native),full_audit_packets=len(packets),fields_sha256=sha(directory/'alias-role-fields-v2.json'),
                candidate_sha256={k:sha(directory/f'{k}-candidates-v1.jsonl') for k in ('probability','question')})


def split(directory):
    path=directory/'probability-audited-v1.jsonl';rows=list(map(json.loads,path.read_text().splitlines()));assert len(rows)==9216
    for fact,target in itertools.product(FORMS,repeat=2):
        rr=[r for r in rows if r['fact_form']==fact and r['target_form']==target];assert len(rr)==2304
        out=directory/f'probability-{fact}-to-{target}-audited-v1.jsonl';assert not out.exists();write_jsonl(out,rr)
        j=json.loads(path.with_suffix('.audit.json').read_text());j.update(variants=len(rr),audited_sha256=sha(out),parent_audited_sha256=sha(path),eligible=sum(r['eligible'] for r in rr))
        out.with_suffix('.audit.json').write_text(json.dumps(j,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','adopt','split']);p.add_argument('--cache',type=Path,default=CACHE)
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+');a=p.parse_args()
    if a.action=='build': print(json.dumps(build(a.cache,a.directory),indent=2))
    elif a.action=='adopt': print(json.dumps(adopt(a.directory,a.reviews,'E48'),indent=2))
    else: split(a.directory)
