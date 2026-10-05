"""E24 independent published frames, cache-only shared-schema loader."""
import argparse
import collections
import csv
import json
from pathlib import Path
import re
import numpy as np
from analyze import estimate
from aspect_reference import read_run
from data import CACHE, record, sha, write_jsonl
from event_identity import digest


def load_published(cache):
    root=cache/'upstream/cehakova2025';report=json.loads((root/'audit.json').read_text())
    assert report['revision']['record_id']==16358492
    assert sha(root/'Stimuli.zip')==report['sha256']=='a6aefcd55945e195c26912bb386b3980272ab2b034fcf152911ce3e1b4fcd25d'
    for f in report['files']: assert sha(root/'stimuli'/f['name'])==f['sha256']
    assert report['task_encoding']['mapping']=={'0':'Yes','1':'No'}
    raw=list(csv.DictReader((root/'stimuli/exp_items.csv').open()));rows=[]
    for i,r in enumerate(raw):
        family,gp,qtype=r['condition'].split('-'); condition='gp' if gp=='gp' else 'explicit_cue'
        rows.append(record(item_id=f'cehakova2025:{i}',source='cehakova2025',construction=family,condition=condition,
                           sentence=r['sentence'],question_type=qtype,question=r['question'],gold={'0':'Yes','1':'No'}[r['correct']],
                           cue_type='comma' if family=='NPZ' and condition=='explicit_cue' else 'unreduced' if family=='MVRR' and condition=='explicit_cue' else 'none',
                           source_row_id=r['item']+':'+r['condition'],pair_id='Cehakova:'+r['item'],source_group=r['group'],
                           gold_status='published_answer_index_not_entailment_certificate',source_revision='16358492:v1'))
    assert len(rows)==384 and len({r['pair_id'] for r in rows})==48
    return rows


def build(cache, fields_path, out):
    assert not out.exists()
    fields=json.loads(fields_path.read_text());assert fields['model']=='gpt-6-luna'
    fs={r['id']:r for r in fields['rows']};assert len(fs)==24
    families=collections.defaultdict(list)
    for f in fs.values():families[f['source_past_vp']].append(f['id'])
    assert len(families)==12 and all(len(v)==2 for v in families.values())
    raw=[r for r in load_published(cache) if r['construction']=='NPZ' and r['question_type']=='ambcor'];assert len(raw)==48
    rows=[]
    for parent in raw:
        sid=parent['source_row_id'].split(':')[0];f=fs[sid];own=f['source_core_patient_np']
        assert parent['sentence'].count(own)==1 and parent['sentence'].count(f['source_full_subject_np'])==1
        otherid=next(k for k in families[f['source_past_vp']] if k!=sid);other=fs[otherid]['source_core_patient_np'];assert own!=other
        actor=f['actor'][0].upper()+f['actor'][1:]
        for evidence,key in [('reference_only','reference_only'),('initial_patient_only','initial_only')]:
            for style in ('named','generic'):
                fact=f[key+'_'+style+'_sentence']
                prefix=parent['sentence']+' '+fact+' '+actor+' continued that particular '+f['activity_np']+'. '
                for frame in ('activity','neutral_entity'):
                    targets=[('source_np',own),('other_source_np',other)]
                    if frame=='activity':targets.append(('source_reference',f['reference_phrase']))
                    starttext=prefix+('In that same '+f['activity_np']+', '+f['actor']+' '+f['auxiliary']+' '+f['progressive_vp']+' ' if frame=='activity' else actor+' later noticed ')
                    for kind,phrase in targets:
                        sentence=starttext+phrase+' for a moment.';start,stop=len(starttext),len(starttext)+len(phrase)
                        words=list(re.finditer(r'\S+',sentence));span=[i for i,w in enumerate(words) if w.start()<stop and w.end()>start]
                        assert ' '.join(words[i].group() for i in span)==phrase
                        r=dict(parent,item_id='E24:'+parent['item_id']+':'+evidence+':'+style+':'+frame+':'+kind,
                               question=None,question_type='followup_probability',gold=None,source_np_option=0,episode_anchor='same',
                               role_evidence=evidence,exclusion_style=style,readout_frame=frame,target_kind=kind,sentence=sentence,
                               source_sentence_sha256=digest(parent['sentence']),target_start_char=start,target_stop_char=stop,
                               target_span_word_indices=span,target_context_sha256=digest(starttext),target_phrase_sha256=digest(phrase),
                               sentence_sha256=digest(sentence),authored_followup_start_word=len(prefix.split()),
                               verb_family=f['source_past_vp'],donor_source_item=otherid,fields_sha256=sha(fields_path),
                               eligible=True,semantic_gold_status='none_constructed_exclusive_fact_not_original_entailment',
                               transformation='Published S1 exact; external fields supply same-event only fact and activity continuation versus neutral noticing. Other NP is from the other published item in the same verb family, not presumed previously introduced.')
                        rows.append(r)
    assert len(rows)==960
    write_jsonl(out,rows)
    return dict(variants=len(rows),source_items=24,bootstrap_clusters=12,candidate_sha256=sha(out),fields_sha256=sha(fields_path))


def adopt(data,reviews,out):
    annotations={}
    for p in reviews:
        j=json.loads(p.read_text());assert j['model']=='gpt-6-luna'
        for a in j['variant_reviews']:
            assert a['id'] not in annotations;annotations[a['id']]=(a,sha(p))
    rows=list(map(json.loads,data.read_text().splitlines()));assert set(annotations)=={r['item_id'] for r in rows}
    for r in rows:
        a,h=annotations[r['item_id']];assert a['sentence_sha256']==r['sentence_sha256']
        assert a['grammaticality'] in ('acceptable','marginal','unacceptable')
        assert a['role_fact_status'] in ('clear','uncertain','changed')
        assert a['readout_role_requirement'] in ('same_activity_patient','no_original_role','uncertain')
        assert a['selectional_status'] in ('plausible','odd','uncertain')
        assert type(a['source_s1_exact']) is bool
        r.update(audit_annotation=a,audit_review_sha256=h,eligible=a['source_s1_exact'] and a['grammaticality']!='unacceptable',
                 acceptable=a['source_s1_exact'] and a['grammaticality']=='acceptable')
        r['faithful_role_frame']=r['eligible'] and a['role_fact_status']=='clear' and a['readout_role_requirement']==('same_activity_patient' if r['readout_frame']=='activity' else 'no_original_role')
    write_jsonl(out,rows)
    report=dict(variants=len(rows),source_items=24,bootstrap_clusters=12,candidate_sha256=sha(data),audited_sha256=sha(out),
                eligible=sum(r['eligible'] for r in rows),acceptable=sum(r['acceptable'] for r in rows),
                faithful_role_frame=sum(r['faithful_role_frame'] for r in rows),review_sha256=[sha(p) for p in reviews],semantic_gold_labels=0,
                grammar_counts=dict(collections.Counter(r['audit_annotation']['grammaticality'] for r in rows)),
                role_fact_counts=dict(collections.Counter(r['audit_annotation']['role_fact_status'] for r in rows)),
                selectional_counts=dict(collections.Counter(r['audit_annotation']['selectional_status'] for r in rows)))
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');return report


def analyze(path):
    cfg,rows=read_run(path);assert len(rows)==960 and len({r['pair_id'] for r in rows})==24
    result=dict(experiment='E24',physical_tasks=960,source_items=24,units='bits',bootstrap_unit='12 published verb families, two original items per family',
                prediction='Named-minus-generic relation-minus-neutral patient preference should be more negative after GP than comma if E22 structure transfers.',
                formulas={'M':'bits(other-family-author NP) - bits(own NP)','R':'bits(own NP) - bits(source reference)',
                          'history_role_specific_change':'[(M_named-M_generic)_GP - (M_named-M_generic)_cue]_activity minus neutral'},
                interpretation='Independent frames and more explicit activity readout; not semantic accuracy or hidden-state mechanism. Same-verb item pairs are clustered before bootstrap.',
                bootstrap_draws=10000,bootstrap_seed=20261005,scores_sha256=cfg['scores_sha256'],analysis_code_sha256=sha(Path(__file__)),cells={},contrasts={},per_family={},cohorts={})
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,verb_families=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    for stratum in ('all','eligible','acceptable','faithful_role_frame'):
        ix={(r['pair_id'],r['condition'],r['role_evidence'],r['exclusion_style'],r['readout_frame'],r['target_kind']):r for r in rows if stratum=='all' or r[stratum]}
        familyitems=collections.defaultdict(set)
        for r in rows:familyitems[r['verb_family']].add(r['pair_id'])
        keep={f:sorted(sids) for f,sids in familyitems.items() if all((sid,c,e,s,frame,t) in ix for sid in sids for c in ('gp','explicit_cue') for e in ('reference_only','initial_patient_only') for s in ('named','generic') for frame in ('activity','neutral_entity') for t in (('source_np','other_source_np','source_reference') if frame=='activity' else ('source_np','other_source_np')))}
        result['cohorts'][stratum]=keep;vectors={};details={f:{} for f in keep}
        for frame in ('activity','neutral_entity'):
            for evidence in ('reference_only','initial_patient_only'):
                for style in ('named','generic'):
                    for condition in ('gp','explicit_cue'):
                        v={}
                        for family,sids in keep.items():
                            obs=[]
                            for sid in sids:
                                own=ix[(sid,condition,evidence,style,frame,'source_np')];other=ix[(sid,condition,evidence,style,frame,'other_source_np')]
                                assert own['target_context_sha256']==other['target_context_sha256'];obs.append(other['target_total_bits']-own['target_total_bits'])
                            v[family]=float(np.mean(obs));details[family][f'M_{frame}_{evidence}_{style}_{condition}']=v[family]
                        vectors[(frame,evidence,style,condition)]=v;result['cells'][f'{stratum}/M/{frame}/{evidence}/{style}/{condition}']=stat(v)
        for evidence in ('reference_only','initial_patient_only'):
            specific={}
            for condition in ('gp','explicit_cue'):
                changes={frame:diff(vectors[(frame,evidence,'named',condition)],vectors[(frame,evidence,'generic',condition)]) for frame in ('activity','neutral_entity')}
                for frame,v in changes.items():result['contrasts'][f'{stratum}/named_minus_generic/{frame}/{evidence}/{condition}']=stat(v)
                specific[condition]=diff(changes['activity'],changes['neutral_entity']);result['contrasts'][f'{stratum}/role_specific_change/{evidence}/{condition}']=stat(specific[condition])
            h=diff(specific['gp'],specific['explicit_cue']);result['contrasts'][f'{stratum}/history_role_specific_change/{evidence}']=stat(h)
            for f in keep:details[f]['history_role_specific_change_'+evidence]=h[f]
        for style in ('named','generic'):
            for condition in ('gp','explicit_cue'):
                values={}
                for evidence in ('reference_only','initial_patient_only'):
                    v={}
                    for family,sids in keep.items():
                        obs=[]
                        for sid in sids:
                            own=ix[(sid,condition,evidence,style,'activity','source_np')];ref=ix[(sid,condition,evidence,style,'activity','source_reference')]
                            assert own['target_context_sha256']==ref['target_context_sha256'];obs.append(own['target_total_bits']-ref['target_total_bits'])
                        v[family]=float(np.mean(obs))
                    result['cells'][f'{stratum}/R/{evidence}/{style}/{condition}']=stat(v);values[evidence]=v
                result['contrasts'][f'{stratum}/R/role_effect/{style}/{condition}']=stat(diff(values['reference_only'],values['initial_patient_only']))
        result['per_family'][stratum]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--fields',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--out',type=Path,required=True)
    n=s.add_parser('analyze');n.add_argument('--run',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.fields,args.out),indent=2))
    elif args.action=='adopt':print(json.dumps(adopt(args.data,args.reviews,args.out),indent=2))
    else:args.out.write_text(json.dumps(analyze(args.run),indent=2)+'\n')
