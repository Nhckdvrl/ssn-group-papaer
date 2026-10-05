"""E25 scoped correction versus actor-conditioned or predicate-global carryover."""
import argparse
import collections
import json
from pathlib import Path
import re
import numpy as np
from analyze import estimate
from aspect_reference import read_run
from correction_transfer import load_published
from data import CACHE, sha, write_jsonl
from event_identity import digest


def build(cache, out):
    assert not out.exists()
    p=cache/'E24-material-preparation-v1';fields={r['id']:r for r in json.loads((p/'fields-v3.json').read_text())['rows']}
    published={(r['pair_id'],r['condition']):r['sentence'] for r in load_published(cache) if r['construction']=='NPZ' and r['question_type']=='ambcor'}
    old=list(map(json.loads,(p/'audited-v1.jsonl').read_text().splitlines()));ix={r['item_id']:r for r in old};rows=[]
    for parent in old:
        if parent['readout_frame']!='activity' or parent['target_kind']!='source_np':continue
        sid=parent['pair_id'].split(':')[1];f=fields[sid]
        for actor_mode in ('same_actor','other_actor'):
            a=f if actor_mode=='same_actor' else fields[parent['donor_source_item']]
            actor=a['actor'];cap=actor[0].upper()+actor[1:]
            fact=f[('reference_only' if parent['role_evidence']=='reference_only' else 'initial_only')+'_'+parent['exclusion_style']+'_sentence']
            prefix=published[(parent['pair_id'],parent['condition'])]+' '+fact+' '+cap+' continued a separate '+f['activity_np']+'. '
            for frame in ('activity','neutral_entity'):
                starttext=prefix+('In that new '+f['activity_np']+', '+actor+' '+a['auxiliary']+' '+f['progressive_vp']+' ' if frame=='activity' else cap+' later noticed ')
                for target in ('source_np','other_source_np'):
                    prev=ix[parent['item_id'].rsplit(':',1)[0]+':'+target]
                    phrase=prev['sentence'][prev['target_start_char']:prev['target_stop_char']]
                    text=starttext+phrase+' for a moment.';start,stop=len(starttext),len(starttext)+len(phrase)
                    ww=list(re.finditer(r'\S+',text));span=[i for i,w in enumerate(ww) if w.start()<stop and w.end()>start]
                    assert ' '.join(ww[i].group() for i in span)==phrase
                    r=dict(parent,item_id='E25:'+parent['item_id']+':'+actor_mode+':'+frame+':'+target,
                           sentence=text,episode_anchor=actor_mode+'_separate',readout_actor_mode=actor_mode,
                           readout_frame=frame,target_kind=target,target_start_char=start,target_stop_char=stop,
                           target_span_word_indices=span,target_context_sha256=digest(starttext),target_phrase_sha256=digest(phrase),
                           sentence_sha256=digest(text),authored_followup_start_word=len(prefix.split()),
                           parent_item_id=prev['item_id'],prior_faithful_role=parent['faithful_role_frame'],
                           transformation='Original S1 and original-actor/original-episode only fact exact; fixed continued aspect, separate activity, original or paired published actor. Readout explicitly in new activity or neutral noticed.')
                    for k in list(r):
                        if k.startswith('audit_'):del r[k]
                    rows.append(r)
    assert len(rows)==1536
    write_jsonl(out,rows);return dict(variants=len(rows),source_items=24,verb_families=12,candidate_sha256=sha(out))


def adopt(data,reviews,out):
    ann={}
    for p in reviews:
        j=json.loads(p.read_text());assert j['model']=='gpt-6-luna'
        for a in j['variant_reviews']:
            assert a['id'] not in ann;ann[a['id']]=(a,sha(p))
    rows=list(map(json.loads,data.read_text().splitlines()));assert set(ann)=={r['item_id'] for r in rows}
    for r in rows:
        a,h=ann[r['item_id']];assert a['sentence_sha256']==r['sentence_sha256']
        assert a['grammaticality'] in ('acceptable','marginal','unacceptable')
        assert a['old_fact_preserved'] in (True,False,None)
        assert a['fact_scope'] in ('original_actor_original_activity','broader_or_changed','uncertain')
        assert a['readout_role_requirement'] in ('new_activity_patient','no_original_role','uncertain')
        assert a['actor_identity_clear'] in (True,False,None)
        r.update(audit_annotation=a,audit_review_sha256=h,
                 eligible=a['source_s1_exact'] is True and a['grammaticality']!='unacceptable',
                 acceptable=a['source_s1_exact'] is True and a['grammaticality']=='acceptable')
        r['faithful_scope_actor']=r['eligible'] and r['prior_faithful_role'] and a['old_fact_preserved'] is True and a['fact_scope']=='original_actor_original_activity' and a['actor_identity_clear'] is True and a['readout_role_requirement']==('new_activity_patient' if r['readout_frame']=='activity' else 'no_original_role')
    write_jsonl(out,rows)
    report=dict(variants=len(rows),source_items=24,verb_families=12,candidate_sha256=sha(data),audited_sha256=sha(out),
                eligible=sum(r['eligible'] for r in rows),acceptable=sum(r['acceptable'] for r in rows),faithful_scope_actor=sum(r['faithful_scope_actor'] for r in rows),
                grammar_counts=dict(collections.Counter(r['audit_annotation']['grammaticality'] for r in rows)),scope_counts=dict(collections.Counter(r['audit_annotation']['fact_scope'] for r in rows)),
                review_sha256=[sha(p) for p in reviews],semantic_gold_labels=0)
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');return report


def split(data):
    report=json.loads(data.with_suffix('.audit.json').read_text());assert report['audited_sha256']==sha(data)
    rows=list(map(json.loads,data.read_text().splitlines()));assert len(rows)==1536
    paths=[]
    for mode in ('same_actor','other_actor'):
        sub=[r for r in rows if r['readout_actor_mode']==mode];assert len(sub)==768
        path=data.with_name('audited-'+mode+'-v1.jsonl');assert not path.exists();write_jsonl(path,sub)
        child=dict(report,variants=len(sub),source_items=len({r['pair_id'] for r in sub}),audited_sha256=sha(path),
                   parent_full_audited_sha256=sha(data),actor_shard=mode,
                   eligible=sum(r['eligible'] for r in sub),acceptable=sum(r['acceptable'] for r in sub),
                   faithful_scope_actor=sum(r['faithful_scope_actor'] for r in sub))
        for field,annotation in [('grammar_counts','grammaticality'),('scope_counts','fact_scope')]:child[field]=dict(collections.Counter(r['audit_annotation'][annotation] for r in sub))
        path.with_suffix('.audit.json').write_text(json.dumps(child,indent=2)+'\n');paths.append(str(path))
    return paths


def merge(data,shards,out):
    assert not out.exists();assert len(shards)==2
    source=list(map(json.loads,data.read_text().splitlines()));cfgs=[];rows=[]
    for p in shards:
        c,rr=read_run(p);assert len(rr)==768;cfgs.append(c);rows.extend(rr)
    for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen','git_commit','code_sha256'):
        assert cfgs[0][k]==cfgs[1][k],k
    assert {r['item_id'] for r in rows}=={r['item_id'] for r in source} and len(rows)==1536
    assert {r['readout_actor_mode'] for r in rows}=={'same_actor','other_actor'}
    byid={r['item_id']:r for r in rows};out.mkdir(parents=True)
    write_jsonl(out/'scores.jsonl',[byid[r['item_id']] for r in source])
    cfg=dict(cfgs[0],task_count=1536,source_items=24,data_sha256=sha(data),independent_audit_sha256=sha(data.with_suffix('.audit.json')),
             scores_sha256=sha(out/'scores.jsonl'),wall_seconds=max(c['wall_seconds'] for c in cfgs),
             wall_seconds_definition='Maximum simultaneous independent actor-shard seconds; see both immutable shard configs.',
             gpu_hours=sum(c['gpu_hours'] for c in cfgs),peak_gpu_bytes=max(c['peak_gpu_bytes'] for c in cfgs),
             source_shards=[dict(path=str(p),config_sha256=sha(p/'config.json'),data_sha256=c['data_sha256'],scores_sha256=c['scores_sha256'],task_count=c['task_count'],gpu_hours=c['gpu_hours']) for p,c in zip(shards,cfgs)],merge_code_sha256=sha(Path(__file__)))
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n');return dict(variants=1536,gpu_hours=cfg['gpu_hours'],wall_seconds=cfg['wall_seconds'])


def analyze(cache, path):
    co,old=read_run(cache/'runs/E24');cn,new=read_run(path);assert len(old)==960 and len(new)==1536
    for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):assert co[k]==cn[k],k
    old=[dict(r,readout_actor_mode='original_activity') for r in old if r['target_kind']!='source_reference']
    rows=old+new;assert len(rows)==2304
    result=dict(experiment='E25',physical_tasks=1536,units='bits',bootstrap_unit='12 published verb families; two source items averaged',
                formulas={'M':'bits(other NP)-bits(own NP)','I':'named-minus-generic activity-minus-neutral effect in GP minus same in comma',
                          'event_transfer':'I_same_actor_new_activity - I_original_activity','actor_transfer':'I_other_actor_new_activity - I_same_actor_new_activity'},
                interpretation='Tests where a correction-conditioned likelihood effect transfers. New activities have no semantic gold distinguishing own/other patients; no scope-violation accuracy claim.',
                bootstrap_draws=10000,bootstrap_seed=20261005,scores_sha256={'E24':co['scores_sha256'],'E25':cn['scores_sha256']},analysis_code_sha256=sha(Path(__file__)),cells={},contrasts={},per_family={},cohorts={})
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,verb_families=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    modes=('original_activity','same_actor','other_actor')
    for stratum in ('all','eligible','acceptable','faithful_scope_actor'):
        def qualifies(r):
            if stratum=='all':return True
            if stratum=='faithful_scope_actor':return r['faithful_role_frame'] if r['readout_actor_mode']=='original_activity' else r[stratum]
            return r[stratum]
        ix={(r['pair_id'],r['condition'],r['role_evidence'],r['exclusion_style'],r['readout_frame'],r['readout_actor_mode'],r['target_kind']):r for r in rows if qualifies(r)}
        familyitems=collections.defaultdict(set)
        for r in rows:familyitems[r['verb_family']].add(r['pair_id'])
        keep={f:sorted(sids) for f,sids in familyitems.items() if all((sid,c,e,s,frame,m,t) in ix for sid in sids for c in ('gp','explicit_cue') for e in ('reference_only','initial_patient_only') for s in ('named','generic') for frame in ('activity','neutral_entity') for m in modes for t in ('source_np','other_source_np'))}
        result['cohorts'][stratum]=keep;values={};detail={f:{} for f in keep}
        for mode in modes:
            for frame in ('activity','neutral_entity'):
                for evidence in ('reference_only','initial_patient_only'):
                    for style in ('named','generic'):
                        for condition in ('gp','explicit_cue'):
                            v={}
                            for f,sids in keep.items():
                                obs=[]
                                for sid in sids:
                                    k=(sid,condition,evidence,style,frame,mode);own,other=ix[(*k,'source_np')],ix[(*k,'other_source_np')]
                                    assert own['target_context_sha256']==other['target_context_sha256'];obs.append(other['target_total_bits']-own['target_total_bits'])
                                v[f]=float(np.mean(obs))
                            values[(mode,frame,evidence,style,condition)]=v;result['cells'][f'{stratum}/{mode}/{frame}/{evidence}/{style}/{condition}']=stat(v)
        for evidence in ('reference_only','initial_patient_only'):
            interactions={}
            for mode in modes:
                specific={}
                for condition in ('gp','explicit_cue'):
                    changes={frame:diff(values[(mode,frame,evidence,'named',condition)],values[(mode,frame,evidence,'generic',condition)]) for frame in ('activity','neutral_entity')}
                    for frame,v in changes.items():result['contrasts'][f'{stratum}/named_minus_generic/{mode}/{frame}/{evidence}/{condition}']=stat(v)
                    specific[condition]=diff(changes['activity'],changes['neutral_entity']);result['contrasts'][f'{stratum}/role_specific_change/{mode}/{evidence}/{condition}']=stat(specific[condition])
                interactions[mode]=diff(specific['gp'],specific['explicit_cue']);result['contrasts'][f'{stratum}/I/{mode}/{evidence}']=stat(interactions[mode])
                for f in keep:detail[f][f'I_{mode}_{evidence}']=interactions[mode][f]
            for name,a,b in [('event_transfer','same_actor','original_activity'),('actor_transfer','other_actor','same_actor'),('full_transfer','other_actor','original_activity')]:
                v=diff(interactions[a],interactions[b]);result['contrasts'][f'{stratum}/{name}/{evidence}']=stat(v)
                for f in keep:detail[f][name+'_'+evidence]=v[f]
        result['per_family'][stratum]=[dict(verb_family=f,source_items=keep[f],**detail[f]) for f in sorted(keep)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--out',type=Path,required=True)
    d=s.add_parser('split');d.add_argument('--data',type=Path,required=True)
    m=s.add_parser('merge');m.add_argument('--data',type=Path,required=True);m.add_argument('--shards',type=Path,nargs=2,required=True);m.add_argument('--out',type=Path,required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,default=CACHE);n.add_argument('--run',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.out),indent=2))
    elif args.action=='adopt':print(json.dumps(adopt(args.data,args.reviews,args.out),indent=2))
    elif args.action=='split':print(json.dumps(split(args.data),indent=2))
    elif args.action=='merge':print(json.dumps(merge(args.data,args.shards,args.out),indent=2))
    else:args.out.write_text(json.dumps(analyze(args.cache,args.run),indent=2)+'\n')
