"""E32: identical fact tokens, opposite affirmative/negative block order.

All new inputs are reviewed before inference; old E29/E31 scores stay frozen.
"""
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


def build(cache, out):
    assert not out.exists()
    out.mkdir(parents=True)
    fields = {r['id']: r for r in json.loads((cache/'E24-material-preparation-v1/fields-v3.json').read_text())['rows']}
    parents = []
    for ex, path in [('E29', cache/'E29-material-preparation-v2/probability-audited-v2.jsonl'),
                     ('E31', cache/'E31-material-preparation-v1/probability-audited-v1.jsonl')]:
        for r in map(json.loads, path.read_text().splitlines()):
            if r['exclusion_style']=='named' and (ex=='E31' or r['readout_actor_mode']=='original_activity'):
                parents.append((ex, r))
    assert len(parents)==960
    rows=[]; packets=[]; mapping={}
    for i,(ex,r) in enumerate(parents):
        f=fields[r['pair_id'].split(':')[1]]
        old=f['reference_only_named_sentence'] if r['role_evidence']=='reference_only' else f['initial_only_named_sentence']
        pre,tail=old.split(' not ')
        excluded,allowed=tail[:-1].split(' but only ')
        new=pre+' only '+allowed+' but not '+excluded+'.'
        assert sorted(old[:-1].split())==sorted(new[:-1].split())
        assert r['sentence'].count(old)==1
        start0=r['target_start_char'];prefix=r['sentence'][:start0]
        assert prefix.count(old)==1
        prefix=prefix.replace(old,new);text=prefix+r['sentence'][start0:]
        phrase=r['sentence'][start0:r['target_stop_char']];start=len(prefix);stop=start+len(phrase)
        marker=r['boundary_marker'] if ex=='E31' else 'original'
        row=dict(r,item_id='E32:'+r['item_id'],parent_item_id=r['item_id'],parent_experiment=ex,
                 boundary_marker=marker,condition=marker,fact_order='affirm_then_negate',
                 sentence=text,sentence_sha256=digest(text),target_start_char=start,target_stop_char=stop,
                 target_span_word_indices=[j for j,w in enumerate(re.finditer(r'\S+',text)) if w.start()<stop and w.end()>start],
                 target_context_sha256=digest(prefix),old_fact_text=old,new_fact_text=new,
                 transformation='Same old-event role fact and exact token multiset; V not X but only Y becomes V only Y but not X. Actor, bridge, readout and target unchanged.')
        for k in list(row):
            if k.startswith('audit'): del row[k]
        assert text[start:stop]==phrase
        key=f'P{i:04d}';mapping[key]=row['item_id'];rows.append(row)
        packets.append(dict(id=key,text=text,previous_text=r['sentence'],sentence_sha256=row['sentence_sha256'],
                            target=phrase,target_phrase_sha256=row['target_phrase_sha256'],old_fact=old,new_fact=new,
                            readout_frame=r['readout_frame'],readout_actor_mode=r['readout_actor_mode']))
    write_jsonl(out/'candidates-v1.jsonl',rows)
    (out/'review-id-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    for shard in (0,1):
        pp=packets[shard::2];assert len(pp)==480
        (out/f'review-packets-{shard}.json').write_text(json.dumps(dict(packets=pp),indent=2)+'\n')
    return dict(variants=len(rows),sha256=sha(out/'candidates-v1.jsonl'))


def adopt(directory,reviews):
    mapping=json.loads((directory/'review-id-map.json').read_text());ann={}
    for path in reviews:
        report=json.loads(path.read_text());assert report['model']=='gpt-6-luna'
        for r in report['reviews']:
            key=mapping[r['id']];assert key not in ann;ann[key]=(r,sha(path))
    assert set(ann)==set(mapping.values())
    rows=list(map(json.loads,(directory/'candidates-v1.jsonl').read_text().splitlines()))
    for r in rows:
        a,h=ann[r['item_id']]
        assert a['sentence_sha256']==r['sentence_sha256'] and a['target_phrase_sha256']==r['target_phrase_sha256']
        assert a['grammaticality'] in ('acceptable','marginal','unacceptable')
        assert a['facts_preserved'] in ('clear','changed','uncertain')
        assert a['old_fact_scope'] in ('local_old_activity','broader_or_changed','uncertain')
        expect='neutral_entity' if r['readout_frame']=='neutral_entity' else 'old_activity_patient' if r['readout_actor_mode']=='original_activity' else 'new_activity_patient'
        assert a['target_role'] in ('neutral_entity','old_activity_patient','new_activity_patient','uncertain')
        r.update(order_audit=a,order_review_sha256=h,
                 order_eligible=a['grammaticality']!='unacceptable',
                 order_acceptable=a['grammaticality']=='acceptable',
                 order_faithful=a['facts_preserved']=='clear' and a['old_fact_scope']=='local_old_activity' and a['target_role']==expect and a['grammaticality']!='unacceptable')
    out=directory/'audited-v1.jsonl';assert not out.exists();write_jsonl(out,rows)
    report=dict(variants=len(rows),source_items=24,verb_families=12,audited_sha256=sha(out),candidate_sha256=sha(directory/'candidates-v1.jsonl'),
                reviewer_sha256=[sha(p) for p in reviews],order_eligible=sum(r['order_eligible'] for r in rows),
                order_acceptable=sum(r['order_acceptable'] for r in rows),order_faithful=sum(r['order_faithful'] for r in rows),
                grammar_counts=dict(collections.Counter(r['order_audit']['grammaticality'] for r in rows)),
                facts_counts=dict(collections.Counter(r['order_audit']['facts_preserved'] for r in rows)),
                policy='All scored; preserve parent flags and independent new order flags. No patient correctness gold.')
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');return report


def analyze(cache,newpath):
    freshcfg,new=read_run(newpath);old=[];configs={}
    for ex in ('E29','E31'):
        c,rr=read_run(cache/f'runs/{ex}-probability');configs[ex]=c
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):
            assert c[k]==freshcfg[k],k
        old.extend(dict(r,boundary_marker=r['boundary_marker'] if ex=='E31' else 'original',fact_order='negate_then_affirm') for r in rr if r['exclusion_style']=='named' and (ex=='E31' or r['readout_actor_mode']=='original_activity'))
    assert len(new)==len(old)==960
    oldids={r['item_id'] for r in old};assert oldids=={r['parent_item_id'] for r in new}
    out=dict(experiment='E32',units='bits',physical_raw_tasks=len(new),actual_gpu_hours=freshcfg['gpu_hours'],
             bootstrap_unit='12 verb families, two sources averaged',bootstrap_draws=10000,bootstrap_seed=20261005,
             analysis_code_sha256=sha(Path(__file__)),input_scores_sha256=dict(new=freshcfg['scores_sha256'],**{k:c['scores_sha256'] for k,c in configs.items()}),
             interpretation='Fact block order intervention; contrast/focus changes with linear position. Not a pure token-distance or semantic mechanism intervention.',
             cohorts={},cells={},contrasts={},per_family={})
    def qualifies(r,co):
        if co=='all': return True
        if co=='eligible': return r['eligible'] and r['order_eligible']
        if co=='anchor_cross_clear': return r['anchor_cross_semantics_clear'] is True
        if co=='anchor_cross_acceptable': return r['anchor_cross_grammaticality']=='acceptable'
        if co=='order_faithful': return r['order_faithful']
        return r['prior_faithful'] and r['faithful_ablation'] and r['order_faithful']
    families=collections.defaultdict(set)
    for r in new:families[r['verb_family']].add(r['pair_id'])
    branches=[('original','original_activity'),('same_began','same_actor'),('same_began','other_actor'),('different_began','same_actor'),('different_began','other_actor')]
    for cohort in ('all','eligible','anchor_cross_clear','anchor_cross_acceptable','prior_and_ablation_faithful','order_faithful'):
        chosen=[r for r in new if qualifies(r,cohort)];counts=collections.Counter(r['pair_id'] for r in chosen)
        keep={f:sorted(sids) for f,sids in families.items() if all(counts[sid]==40 for sid in sids)}
        out['cohorts'][cohort]=keep;selected={r['parent_item_id'] for r in chosen};rr=chosen+[r for r in old if r['item_id'] in selected]
        ix={(r['pair_id'],r['fact_order'],r['boundary_marker'],r['readout_actor_mode'],r['role_evidence'],r['readout_frame'],r['target_kind']):r for r in rr}
        assert len(ix)==len(rr)
        vv={};details={f:{} for f in keep}
        def record(store,key,vector):
            out[store][cohort+'/'+key]=stat(vector)
            for f in keep:details[f][key]=vector[f]
        for order in ('negate_then_affirm','affirm_then_negate'):
            for marker,mode in branches:
                for frame in ('activity','neutral_entity'):
                    vector={}
                    for f,sids in keep.items():
                        vals=[]
                        for sid in sids:
                            mm={}
                            for e in ('reference_only','initial_patient_only'):
                                k=(sid,order,marker,mode,e,frame);a,b=ix[(*k,'source_np')],ix[(*k,'other_source_np')]
                                assert a['target_context_sha256']==b['target_context_sha256']
                                mm[e]=b['target_total_bits']-a['target_total_bits']
                            vals.append(mm['initial_patient_only']-mm['reference_only'])
                        vector[f]=float(np.mean(vals))
                    vv[order,marker,mode,frame]=vector;record('cells',f'D/{order}/{marker}/{mode}/{frame}',vector)
                vector=diff(vv[order,marker,mode,'activity'],vv[order,marker,mode,'neutral_entity'])
                vv[order,marker,mode,'J']=vector;record('cells',f'J/{order}/{marker}/{mode}',vector)
            for mode in ('same_actor','other_actor'):
                for measure in ('activity','neutral_entity','J'):
                    vector=diff(vv[order,'different_began',mode,measure],vv[order,'same_began',mode,measure])
                    vv[order,'predicate_difference',mode,measure]=vector;record('contrasts',f'different_minus_same/{order}/{mode}/{measure}',vector)
            for marker in ('same_began','different_began'):
                vector=diff(vv[order,marker,'same_actor','J'],vv[order,marker,'other_actor','J'])
                record('contrasts',f'actor_match/{order}/{marker}/J',vector)
        for marker,mode in branches+[('predicate_difference','same_actor'),('predicate_difference','other_actor')]:
            for measure in ('activity','neutral_entity','J'):
                vector=diff(vv['affirm_then_negate',marker,mode,measure],vv['negate_then_affirm',marker,mode,measure])
                record('contrasts',f'order_change/{marker}/{mode}/{measure}',vector)
        out['per_family'][cohort]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--directory',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,default=CACHE);n.add_argument('--new',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.action=='build': print(json.dumps(build(a.cache,a.out),indent=2))
    elif a.action=='adopt': print(json.dumps(adopt(a.directory,a.reviews),indent=2))
    else:a.out.write_text(json.dumps(analyze(a.cache,a.new),indent=2)+'\n')
