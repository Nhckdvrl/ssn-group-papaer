"""E33: pre-audited action paraphrases, both fact orders, fixed controls."""
import argparse
import collections
import json
from pathlib import Path
import re
import numpy as np
from data import CACHE, sha, write_jsonl
from event_identity import digest
from aspect_reference import read_run
from analyze_source_ablation import stat, diff


def build(cache,fields_path,out):
    assert not out.exists();out.mkdir(parents=True)
    original=cache/'E24-material-preparation-v1/fields-v3.json'
    fields=json.loads(fields_path.read_text());assert fields['model']=='gpt-6-luna' and fields['source_fields_sha256']==sha(original)
    paras={r['verb_family']:r for r in fields['rows']};assert len(paras)==12==len(fields['rows'])
    source={r['id']:r for r in json.loads(original.read_text())['rows']}
    jobs=[('E29',cache/'E29-material-preparation-v2/probability-audited-v2.jsonl'),('E31',cache/'E31-material-preparation-v1/probability-audited-v1.jsonl'),('E32',cache/'E32-material-preparation-v1/audited-v1.jsonl')]
    parents=[]
    for ex,p in jobs:
        for r in map(json.loads,p.read_text().splitlines()):
            if r['exclusion_style']=='named' and (r['readout_actor_mode']=='original_activity' if ex=='E29' else r['boundary_marker']=='same_began'):
                parents.append((ex,r))
    assert len(parents)==960
    rows=[];packets=[];mapping={}
    for i,(ex,r) in enumerate(parents):
        f=source[r['pair_id'].split(':')[1]];g=paras[r['verb_family']]
        assert g['original_activity_np']==f['activity_np'] and g['original_progressive_vp']==f['progressive_vp']
        fact=r['new_fact_text'] if ex=='E32' else f['reference_only_named_sentence'] if r['role_evidence']=='reference_only' else f['initial_only_named_sentence']
        prefix0=r['source_anchor']+' '+fact+' ';assert r['sentence'].startswith(prefix0)
        start0=r['target_start_char'];prefix=r['sentence'][:start0];assert prefix.startswith(prefix0)
        tail=prefix[len(prefix0):]
        if ex!='E29':
            needle=' began a separate '+f['activity_np']+'.';assert tail.count(needle)==1
            tail=tail.replace(needle,' began a separate '+g['para_activity_np']+'.')
        if r['readout_frame']=='activity':
            needle='In that '+('new ' if ex!='E29' else 'same ')+f['activity_np']+', ';assert tail.count(needle)==1
            tail=tail.replace(needle,'In that '+('new ' if ex!='E29' else 'same ')+g['para_activity_np']+', ')
            needle=' '+f['progressive_vp']+' ';assert tail.count(needle)==1
            tail=tail.replace(needle,' '+g['para_progressive_vp']+' ')
        # No original activity word form remains in the changed causal tail.
        checked_tail=tail
        if ex=='E29':
            # The old-event control retains its explicit original-type identity
            # bridge; only the subsequent activity readout is paraphrased.
            needle=' continued that particular '+f['activity_np']+'.'
            assert tail.count(needle)==1;checked_tail=tail.split(needle)[1]
        assert f['progressive_vp'] not in checked_tail
        assert f['activity_np'] not in checked_tail
        prefix=prefix0+tail;phrase=r['sentence'][start0:r['target_stop_char']]
        text=prefix+r['sentence'][start0:];start=len(prefix);stop=start+len(phrase)
        order='affirm_then_negate' if ex=='E32' else 'negate_then_affirm';marker='original' if ex=='E29' else 'same_began'
        row=dict(r,item_id='E33:'+r['item_id'],parent_item_id=r['item_id'],parent_experiment=ex,
                 sentence=text,sentence_sha256=digest(text),condition=marker+':'+order,fact_order=order,boundary_marker=marker,
                 target_start_char=start,target_stop_char=stop,target_context_sha256=digest(prefix),
                 target_span_word_indices=[j for j,w in enumerate(re.finditer(r'\S+',text)) if w.start()<stop and w.end()>start],
                 authored_followup_start_word=r['authored_followup_start_word'],
                 para_fields_sha256=sha(fields_path),proposed_activity_match=g['proposed_match'],
                 old_fact_prefix_sha256=digest(prefix0),exact_unchanged_control=text==r['sentence'],
                 transformation='Old anchor/role fact exact; new-event bridge noun and readout noun/progressive replaced by one independently authored paraphrase per family. Target alternatives unchanged.')
        # Followup word origin shifts when the activity bridge has changed length.
        if ex!='E29':
            old_bridge=' began a separate '+f['activity_np']+'.';new_bridge=' began a separate '+g['para_activity_np']+'.'
            row['authored_followup_start_word']+=len(new_bridge.split())-len(old_bridge.split())
        for k in list(row):
            if k.startswith('audit'):del row[k]
        assert text[start:stop]==phrase and text.startswith(prefix0)
        key=f'P{i:04d}';mapping[key]=row['item_id'];rows.append(row)
        packets.append(dict(id=key,text=text,previous_text=r['sentence'],sentence_sha256=row['sentence_sha256'],target=phrase,target_phrase_sha256=row['target_phrase_sha256'],
                            old_fact=fact,original_progressive_vp=f['progressive_vp'],original_activity_np=f['activity_np'],para_progressive_vp=g['para_progressive_vp'],para_activity_np=g['para_activity_np'],
                            readout_frame=r['readout_frame'],readout_actor_mode=r['readout_actor_mode']))
    write_jsonl(out/'candidates-v1.jsonl',rows)
    (out/'review-id-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    for shard in (0,1):
        (out/f'review-packets-{shard}.json').write_text(json.dumps(dict(packets=packets[shard::2]),indent=2)+'\n')
    return dict(variants=len(rows),candidate_sha256=sha(out/'candidates-v1.jsonl'),field_sha256=sha(fields_path),unchanged_controls=sum(r['exact_unchanged_control'] for r in rows))


def adopt(directory,reviews):
    mapping=json.loads((directory/'review-id-map.json').read_text());ann={}
    for path in reviews:
        report=json.loads(path.read_text());assert report['model']=='gpt-6-luna'
        for r in report['reviews']:
            key=mapping[r['id']];assert key not in ann;ann[key]=(r,sha(path))
    assert set(ann)==set(mapping.values())
    rows=list(map(json.loads,(directory/'candidates-v1.jsonl').read_text().splitlines()))
    for r in rows:
        a,h=ann[r['item_id']];assert a['sentence_sha256']==r['sentence_sha256'] and a['target_phrase_sha256']==r['target_phrase_sha256']
        assert a['grammaticality'] in ('acceptable','marginal','unacceptable')
        assert a['old_fact_preserved'] in ('clear','changed','uncertain')
        assert a['activity_match'] in ('clear','related_but_changed','changed','uncertain')
        assert a['activity_available_before_target'] in (True,False,None)
        assert a['event_identity'] in ('old_activity','distinct_new_activity','uncertain')
        expect='neutral_entity' if r['readout_frame']=='neutral_entity' else 'old_activity_patient' if r['readout_actor_mode']=='original_activity' else 'new_activity_patient'
        assert a['target_role'] in ('neutral_entity','old_activity_patient','new_activity_patient','uncertain')
        r.update(para_audit=a,para_review_sha256=h,
                 para_eligible=a['grammaticality']!='unacceptable' and a['old_fact_preserved']=='clear' and a['target_role']==expect,
                 para_basic_clear=a['activity_match']=='clear' and a['activity_available_before_target'] is True and a['event_identity']==('old_activity' if r['readout_actor_mode']=='original_activity' else 'distinct_new_activity'))
    out=directory/'audited-v1.jsonl';assert not out.exists();write_jsonl(out,rows)
    report=dict(variants=len(rows),source_items=24,verb_families=12,audited_sha256=sha(out),candidate_sha256=sha(directory/'candidates-v1.jsonl'),review_sha256=[sha(p) for p in reviews],
                para_eligible=sum(r['para_eligible'] for r in rows),para_basic_clear=sum(r['para_basic_clear'] for r in rows),
                grammar_counts=dict(collections.Counter(r['para_audit']['grammaticality'] for r in rows)),activity_match_counts=dict(collections.Counter(r['para_audit']['activity_match'] for r in rows)),
                unchanged_controls=sum(r['exact_unchanged_control'] for r in rows),policy='Score all reviewed rows; semantic/grammar flags independent of inference and construction proposal.')
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');return report


def analyze(cache,newpath):
    cfg,new=read_run(newpath);assert len(new)==960
    wb=Path(__file__).resolve().parents[1]
    summaries={ex:json.loads((wb/f'results/{ex}-summary.json').read_text()) for ex in ('E31','E32')}
    original={};oldconfigs={}
    for ex in ('E29','E31','E32'):
        c,rr=read_run(cache/f'runs/{ex}-probability');oldconfigs[ex]=c
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):assert cfg[k]==c[k],k
        original.update({r['item_id']:r for r in rr})
    assert all(r['parent_item_id'] in original for r in new)
    duplicates=[abs(r['target_total_bits']-original[r['parent_item_id']]['target_total_bits']) for r in new if r['exact_unchanged_control']]
    assert len(duplicates)==96 and max(duplicates)<1e-4
    out=dict(experiment='E33',units='bits',physical_raw_tasks=len(new),actual_gpu_hours=cfg['gpu_hours'],bootstrap_unit='Verb family with two original sources averaged',bootstrap_draws=10000,bootstrap_seed=20261005,
             analysis_code_sha256=sha(Path(__file__)),input_scores_sha256=dict(new=cfg['scores_sha256'],**{k:c['scores_sha256'] for k,c in oldconfigs.items()}),
             parent_summary_sha256={ex:sha(wb/f'results/{ex}-summary.json') for ex in summaries},unchanged_control_max_drift_bits=max(duplicates),unchanged_controls=len(duplicates),
             interpretation='Same-basic-action strata independently defined before scores; not strict synonym identity or a latent semantic mechanism.',cohorts={},cells={},contrasts={},per_family={})
    families=collections.defaultdict(set)
    for r in new:families[r['verb_family']].add(r['pair_id'])
    ix={(r['pair_id'],r['fact_order'],r['boundary_marker'],r['readout_actor_mode'],r['role_evidence'],r['readout_frame'],r['target_kind']):r for r in new};assert len(ix)==len(new)
    branches=[('negate_then_affirm','original','original_activity')]+[(order,'same_began',mode) for order in ('negate_then_affirm','affirm_then_negate') for mode in ('same_actor','other_actor')]
    def qualifies(r,co):
        if co=='all':return True
        if co=='eligible':return r['para_eligible']
        if co=='basic_action_clear':return r['para_eligible'] and r['para_basic_clear']
        if co=='anchor_cross_clear':return r['anchor_cross_semantics_clear'] is True
        if co=='anchor_cross_acceptable':return r['anchor_cross_grammaticality']=='acceptable'
        return True
    def stat_record(co,store,key,v,details):
        out[store][co+'/'+key]=stat(v)
        for f in v:details[f][key]=v[f]
    for co in ('all','eligible','basic_action_clear','anchor_cross_clear','anchor_cross_acceptable','prior_and_ablation_faithful'):
        counts=collections.Counter(r['pair_id'] for r in new if qualifies(r,co))
        keep={f:sorted(sids) for f,sids in families.items() if all(counts[sid]==40 for sid in sids)}
        if co=='prior_and_ablation_faithful':keep={f:sids for f,sids in keep.items() if f in summaries['E31']['probability']['cohorts'][co]}
        out['cohorts'][co]=keep;details={f:{} for f in keep};vvs={}
        base31={r['verb_family']:r for r in summaries['E31']['probability']['per_family']['all']}
        base32={r['verb_family']:r for r in summaries['E32']['per_family']['all']}
        for order,marker,mode in branches:
            for frame in ('activity','neutral_entity'):
                vec={}
                for f,sids in keep.items():
                    vals=[]
                    for sid in sids:
                        mm={}
                        for e in ('reference_only','initial_patient_only'):
                            k=(sid,order,marker,mode,e,frame);a,b=ix[(*k,'source_np')],ix[(*k,'other_source_np')]
                            assert a['target_context_sha256']==b['target_context_sha256']
                            mm[e]=b['target_total_bits']-a['target_total_bits']
                        vals.append(mm['initial_patient_only']-mm['reference_only'])
                    vec[f]=float(np.mean(vals))
                vvs[order,marker,mode,frame]=vec;stat_record(co,'cells',f'D/paraphrase/{order}/{marker}/{mode}/{frame}',vec,details)
            vec=diff(vvs[order,marker,mode,'activity'],vvs[order,marker,mode,'neutral_entity']);vvs[order,marker,mode,'J']=vec
            stat_record(co,'cells',f'J/paraphrase/{order}/{marker}/{mode}',vec,details)
            for measure in ('activity','neutral_entity','J'):
                base=base31 if order=='negate_then_affirm' else base32
                def key(m):
                    if order=='negate_then_affirm':return f'J/{m}/{mode}/named' if measure=='J' else f'D/{m}/{mode}/named/{measure}'
                    return f'J/{order}/{m}/{mode}' if measure=='J' else f'D/{order}/{m}/{mode}/{measure}'
                for control in (('original',) if marker=='original' else ('same_began','different_began')):
                    vector={f:base[f][key(control)] for f in keep};label='same_action_original_words' if control!='different_began' else 'fixed_different_action'
                    stat_record(co,'cells',f'{measure}/{label}/{order}/{marker}/{mode}',vector,details)
                    stat_record(co,'contrasts',f'paraphrase_minus_{label}/{order}/{marker}/{mode}/{measure}',diff(vvs[order,marker,mode,measure],vector),details)
        for mode in ('same_actor','other_actor'):
            for measure in ('activity','neutral_entity','J'):
                vec=diff(vvs['affirm_then_negate','same_began',mode,measure],vvs['negate_then_affirm','same_began',mode,measure])
                stat_record(co,'contrasts',f'order_change/paraphrase/{mode}/{measure}',vec,details)
        out['per_family'][co]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--fields',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--directory',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,default=CACHE);n.add_argument('--new',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.action=='build':print(json.dumps(build(a.cache,a.fields,a.out),indent=2))
    elif a.action=='adopt':print(json.dumps(adopt(a.directory,a.reviews),indent=2))
    else:a.out.write_text(json.dumps(analyze(a.cache,a.new),indent=2)+'\n')
