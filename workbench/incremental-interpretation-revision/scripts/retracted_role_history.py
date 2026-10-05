"""E34: crossed initial role, provenance, and verified final role.

Constructed inputs require independent row-level annotation before inference.
Raw-text and native relation judgments have different epistemic meanings.
"""
import argparse
import collections
import json
from pathlib import Path
import re
import numpy as np
from data import CACHE,sha,write_jsonl
from event_identity import digest
from aspect_reference import read_run
from analyze_source_ablation import stat,diff

STATUSES=('factual_report','hypothetical_example')
ROLES=('reference_only','initial_patient_only')
TRANSITION='That initial description has been superseded. The verified account of what actually happened is as follows: '


def initial_description(fact,status):
    kind='a factual account' if status=='factual_report' else 'a hypothetical example'
    return 'Initially, the following description was presented as '+kind+': "'+fact+'"'


def build(cache,out):
    assert not out.exists();out.mkdir(parents=True)
    fields={r['id']:r for r in json.loads((cache/'E24-material-preparation-v1/fields-v3.json').read_text())['rows']}
    paths={'P29':cache/'E29-material-preparation-v2/probability-audited-v2.jsonl',
           'P31':cache/'E31-material-preparation-v1/probability-audited-v1.jsonl',
           'N29':cache/'E29-material-preparation-v2/nli-audited-v2.jsonl',
           'N31':cache/'E31-material-preparation-v1/nli-audited-v1.jsonl'}
    parents={k:list(map(json.loads,p.read_text().splitlines())) for k,p in paths.items()}
    fact_keys={'reference_only':'reference_only_named_sentence','initial_patient_only':'initial_only_named_sentence'}
    raws=[];native=[];packets=[];mapping={}
    def transform(r,task,status,prior,phase,kind):
        f=fields[r['pair_id'].split(':')[1]];oldfact=f[fact_keys[r['role_evidence']]]
        oldprefix=r['source_anchor']+' '+oldfact+' '
        text=r['sentence'] if task=='probability' else r['passage'];assert text.startswith(oldprefix)
        initial=initial_description(f[fact_keys[prior]],status)
        prefix=r['source_anchor']+' '+initial+' '+(TRANSITION+oldfact+' ' if phase=='post_update' else '')
        newtext=prefix+text[len(oldprefix):]
        row=dict(r,item_id=f'E34:{r["item_id"]}:{phase}:{status}:{prior}',parent_item_id=r['item_id'],
                 phase=phase,initial_status=status,initial_role=prior,final_role=r['role_evidence'] if phase=='post_update' else None,
                 history_conflict=None if phase=='pre_update' else prior!=r['role_evidence'],
                 condition=phase+':'+status+':'+prior,initial_description_sha256=digest(initial),verified_transition_sha256=digest(TRANSITION),
                 sentence_sha256=digest(newtext),eligible=False,faithful_history=False,
                 transformation='Same event anchor/role bodies/targets/readout. Prior role and presented factual versus hypothetical provenance crossed; identical supersession/verified-final transition for both consistent and conflicting histories.')
        for k in list(row):
            if k.startswith('audit'):del row[k]
        if task=='probability':
            delta=len(prefix)-len(oldprefix);start=r['target_start_char']+delta;stop=r['target_stop_char']+delta
            phrase=text[r['target_start_char']:r['target_stop_char']];assert newtext[start:stop]==phrase
            row.update(sentence=newtext,target_start_char=start,target_stop_char=stop,
                       target_span_word_indices=[i for i,w in enumerate(re.finditer(r'\S+',newtext)) if w.start()<stop and w.end()>start],
                       target_context_sha256=digest(newtext[:start]),authored_followup_start_word=r['authored_followup_start_word']+len(prefix.split())-len(oldprefix.split()),
                       role_evidence=r['role_evidence'] if phase=='post_update' else prior,readout_kind=kind)
            if phase=='pre_update':assert r['role_evidence']==prior
            raws.append(row);key=f'P{len(raws)-1:04d}'
            packet=dict(id=key,task=task,text=newtext,target=phrase,target_phrase_sha256=row['target_phrase_sha256'])
        else:
            row.update(passage=newtext,readout_kind=kind,gold_relation=None,parent_relation=r['gold_relation'])
            native.append(row);key=f'N{len(native)-1:04d}'
            packet=dict(id=key,task=task,text=newtext,proposition=r['proposition'],proposition_sha256=r['proposition_sha256'])
        packet.update(sentence_sha256=row['sentence_sha256'],phase=phase,initial_description=initial,
                      final_fact=oldfact if phase=='post_update' else None)
        packets.append(packet);mapping[key]=row['item_id']
    pold=[r for r in parents['P29'] if r['exclusion_style']=='named' and r['readout_actor_mode']=='original_activity']
    pnew=[r for r in parents['P31'] if r['exclusion_style']=='named' and r['boundary_marker']=='same_began' and r['readout_actor_mode']=='other_actor']
    assert len(pold)==len(pnew)==192
    for r in pold+pnew:
        kind='old_activity' if r['readout_actor_mode']=='original_activity' else 'other_actor_new_activity'
        for status in STATUSES:
            for prior in ROLES:transform(r,'probability',status,prior,'post_update',kind)
    for r in pold:
        for status in STATUSES:transform(r,'probability',status,r['role_evidence'],'pre_update','old_activity')
    nold=[r for r in parents['N29'] if r['exclusion_style']=='named' and r['readout_kind'] in ('old_supported','old_excluded','unrelated_unknown_control')]
    nnew=[r for r in parents['N31'] if r['exclusion_style']=='named' and r['boundary_marker']=='same_began' and r['readout_kind']=='other_actor_new_activity']
    assert len(nold)==144 and len(nnew)==48
    for r in nold+nnew:
        kind=r['readout_kind']
        if kind in ('old_supported','old_excluded'):
            is_source=(kind=='old_supported')==(r['role_evidence']=='initial_patient_only')
            kind='old_source_patient' if is_source else 'old_reference_patient'
        for status in STATUSES:
            for prior in ROLES:transform(r,'nli',status,prior,'post_update',kind)
    assert len(raws)==1920 and len(native)==768 and len(packets)==2688
    for task,rows in [('probability',raws),('nli',native)]:write_jsonl(out/f'{task}-candidates-v1.jsonl',rows)
    (out/'review-id-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    for shard in range(3):
        pp=packets[shard::3];assert len(pp)==896
        (out/f'review-packets-{shard}.json').write_text(json.dumps(dict(packets=pp),indent=2)+'\n')
    return dict(probability_variants=len(raws),nli_variants=len(native),sources=24,families=12,
                initial_frame='Initially, the following description was presented as [a factual account/a hypothetical example]: "[same role words]"',
                verified_transition=TRANSITION,parent_sha256={k:sha(p) for k,p in paths.items()},
                candidate_sha256={task:sha(out/f'{task}-candidates-v1.jsonl') for task in ('probability','nli')})


def adopt(directory,reviews,version=1):
    mapping=json.loads((directory/'review-id-map.json').read_text());annotations={}
    for path in reviews:
        j=json.loads(path.read_text());assert j['model']=='gpt-6-luna'
        for a in j['reviews']:
            key=mapping[a['id']];assert key not in annotations;annotations[key]=(a,sha(path))
    assert set(annotations)==set(mapping.values())
    reports={}
    for task in ('probability','nli'):
        data=directory/f'{task}-candidates-v1.jsonl';rows=list(map(json.loads,data.read_text().splitlines()))
        for r in rows:
            a,h=annotations[r['item_id']];assert a['sentence_sha256']==r['sentence_sha256']
            assert a['grammaticality'] in ('acceptable','marginal','unacceptable')
            assert a['initial_evidence_status'] in (*STATUSES,'uncertain')
            assert a['final_fact_priority'] in ('verified_supersedes_initial','uncertain','not_applicable')
            assert a['event_scope'] in ('local_old_activity','uncertain','changed')
            eligible=a['grammaticality']!='unacceptable'
            faithful=eligible and a['initial_evidence_status']==r['initial_status'] and a['event_scope']=='local_old_activity' and a['final_fact_priority']==('verified_supersedes_initial' if r['phase']=='post_update' else 'not_applicable')
            if task=='probability':
                assert a['target_phrase_sha256']==r['target_phrase_sha256']
                assert a['target_role'] in ('old_activity_patient','new_activity_patient','neutral_entity','uncertain')
                expect='neutral_entity' if r['readout_frame']=='neutral_entity' else 'old_activity_patient' if r['readout_kind']=='old_activity' else 'new_activity_patient'
                faithful=faithful and a['target_role']==expect
            else:
                assert a['proposition_sha256']==r['proposition_sha256']
                assert a['relation'] in ('entailed','contradicted','undetermined',None) and a['certainty'] in ('clear','interpretation_dependent','invalid')
                r['gold_relation']=a['relation'] if a['certainty']=='clear' else None
            r.update(history_audit=a,history_review_sha256=h,eligible=eligible,faithful_history=faithful)
        out=directory/f'{task}-audited-v{version}.jsonl';assert not out.exists();write_jsonl(out,rows)
        report=dict(variants=len(rows),source_items=24,verb_families=12,candidate_sha256=sha(data),audited_sha256=sha(out),eligible=sum(r['eligible'] for r in rows),faithful_history=sum(r['faithful_history'] for r in rows),
                    grammar_counts=dict(collections.Counter(r['history_audit']['grammaticality'] for r in rows)),review_sha256=[sha(p) for p in reviews],
                    annotation_policy='Independent status/scope/priority/relations before inference; pre-update report contents are not asserted-world truth gold. All rows scored.')
        if task=='nli':report.update(clear_gold=sum(r['gold_relation'] is not None for r in rows),agreement_with_parent=sum(r['gold_relation']==r['parent_relation'] for r in rows),relation_counts=dict(collections.Counter(r['gold_relation'] for r in rows)))
        out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');reports[task]=report
    return reports


def analyze(cache,rawpath,nlibase,nlirepair):
    cfg,rows=read_run(rawpath);assert len(rows)==1920
    sources=collections.defaultdict(set)
    for r in rows:sources[r['verb_family']].add(r['pair_id'])
    configs=[];nrows=[]
    for path,count in [(nlibase,2304),(nlirepair,768)]:
        c=json.loads((path/'config.json').read_text());assert sha(path/'predictions.jsonl')==c['predictions_sha256']
        rr=list(map(json.loads,(path/'predictions.jsonl').read_text().splitlines()));assert len(rr)==count==c['task_count'];nrows.extend(rr);configs.append(c)
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','frozen'):assert cfg[k]==c[k],k
        assert cfg['batch_size']==4 and c['batch_size']==8
    control=json.loads((cache/'runs/E29-nli/config.json').read_text())
    for c in configs:
        for k in ('base_definition','scope_repair','mapping_policy','thinking','batch_size'):assert c[k]==control[k],k
        assert c['class_labels'].keys()==control['class_labels'].keys()
        assert all(set(c['class_labels'][k])==set(control['class_labels'][k]) for k in c['class_labels'])
    wb=Path(__file__).resolve().parents[1];parent=wb/'results/E31-summary.json';pc=json.loads(parent.read_text())['probability']['cohorts']
    out=dict(experiment='E34',raw_tasks=len(rows),native_tasks=len(nrows),actual_gpu_hours=cfg['gpu_hours']+sum(c['gpu_hours'] for c in configs),bootstrap_unit='12 verb families, two original sources averaged',bootstrap_draws=10000,bootstrap_seed=20261005,
             analysis_code_sha256=sha(Path(__file__)),registered_parent_cohorts_sha256=sha(parent),scores_sha256=dict(raw=cfg['scores_sha256'],native=[c['predictions_sha256'] for c in configs]),
             probability=dict(units='bits',cohorts={},cells={},contrasts={},per_family={}),nli=dict(units='percentage points',cohorts={},cells={},contrasts={},per_family={}),
             interpretation='Crossed provenance and initial/final roles, with explicit supersession; status dependence is not proof of an initial latent belief or a general updating algorithm.')
    def qualifies(r,co):
        if co=='all':return True
        if co=='eligible':return r['eligible']
        if co=='faithful_history':return r['faithful_history']
        return True
    for co in ('all','eligible','faithful_history','anchor_cross_clear','anchor_cross_acceptable','prior_and_ablation_faithful'):
        chosen=[r for r in rows if qualifies(r,co)];counts=collections.Counter(r['pair_id'] for r in chosen)
        keep={f:sorted(sids) for f,sids in sources.items() if all(counts[sid]==80 for sid in sids)}
        if co in pc:keep={f:sids for f,sids in keep.items() if f in pc[co]}
        out['probability']['cohorts'][co]=keep;details={f:{} for f in keep}
        ix={(r['pair_id'],r['phase'],r['initial_status'],r['initial_role'],r['final_role'],r['readout_kind'],r['readout_frame'],r['target_kind']):r for r in chosen};assert len(ix)==len(chosen)
        values={}
        def record(store,key,v):
            out['probability'][store][co+'/'+key]=stat(v)
            for f in keep:details[f][key]=v[f]
        for phase,kinds,finals in [('pre_update',('old_activity',),(None,)),('post_update',('old_activity','other_actor_new_activity'),ROLES)]:
            for status in STATUSES:
                for prior in ROLES:
                    for final in finals:
                        for kind in kinds:
                            for frame in ('activity','neutral_entity'):
                                v={}
                                for f,sids in keep.items():
                                    mm=[]
                                    for sid in sids:
                                        k=(sid,phase,status,prior,final,kind,frame);a,b=ix[(*k,'source_np')],ix[(*k,'other_source_np')];assert a['target_context_sha256']==b['target_context_sha256'];mm.append(b['target_total_bits']-a['target_total_bits'])
                                    v[f]=float(np.mean(mm))
                                values[phase,status,prior,final,kind,frame]=v;record('cells',f'M/{phase}/{status}/{prior}/{final}/{kind}/{frame}',v)
                            v=diff(values[phase,status,prior,final,kind,'activity'],values[phase,status,prior,final,kind,'neutral_entity']);values[phase,status,prior,final,kind,'J']=v
                            record('cells',f'M/{phase}/{status}/{prior}/{final}/{kind}/J',v)
        effects={}
        for status in STATUSES:
            for kind in ('old_activity','other_actor_new_activity'):
                for measure in ('activity','neutral_entity','J'):
                    for final in ROLES:
                        v=diff(values['post_update',status,'initial_patient_only',final,kind,measure],values['post_update',status,'reference_only',final,kind,measure]);effects['H',status,final,kind,measure]=v
                        record('cells',f'H/{status}/{final}/{kind}/{measure}',v)
                    for prior in ROLES:
                        v=diff(values['post_update',status,prior,'initial_patient_only',kind,measure],values['post_update',status,prior,'reference_only',kind,measure]);effects['D',status,prior,kind,measure]=v
                        record('cells',f'D/{status}/{prior}/{kind}/{measure}',v)
                    for effect in ('H','D'):
                        v={f:float(np.mean([effects[effect,status,role,kind,measure][f] for role in ROLES])) for f in keep};effects[effect,status,'balanced',kind,measure]=v;record('cells',f'{effect}/{status}/balanced/{kind}/{measure}',v)
                    v=diff(effects['H',status,'initial_patient_only',kind,measure],effects['H',status,'reference_only',kind,measure]);record('contrasts',f'prior_by_final/{status}/{kind}/{measure}',v)
            for measure in ('activity','neutral_entity','J'):
                v=diff(values['pre_update',status,'initial_patient_only',None,'old_activity',measure],values['pre_update',status,'reference_only',None,'old_activity',measure]);effects['preH',status,'none','old_activity',measure]=v;record('cells',f'preH/{status}/{measure}',v)
        for effect in ('H','D'):
            for role in (*ROLES,'balanced'):
                for kind in ('old_activity','other_actor_new_activity'):
                    for measure in ('activity','neutral_entity','J'):
                        v=diff(effects[effect,'factual_report',role,kind,measure],effects[effect,'hypothetical_example',role,kind,measure]);record('contrasts',f'factual_minus_hypothetical/{effect}/{role}/{kind}/{measure}',v)
            for status in STATUSES:
                for measure in ('activity','neutral_entity','J'):
                    v=diff(effects[effect,status,'balanced','other_actor_new_activity',measure],effects[effect,status,'balanced','old_activity',measure]);record('contrasts',f'new_minus_old/{effect}/{status}/{measure}',v)
        for measure in ('activity','neutral_entity','J'):
            record('contrasts',f'factual_minus_hypothetical/preH/{measure}',diff(effects['preH','factual_report','none','old_activity',measure],effects['preH','hypothetical_example','none','old_activity',measure]))
        out['probability']['per_family'][co]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
        chosen=[r for r in nrows if qualifies(r,co) and r['gold_relation'] is not None];counts=collections.Counter(r['pair_id'] for r in chosen)
        nk={f:sids for f,sids in keep.items() if all(counts[sid]==128 for sid in sids)};out['nli']['cohorts'][co]=nk;nd={f:{} for f in nk};nv={}
        for label,mode,maps in [('base_all','base',(0,1,2)),('base_map0','base',(0,)),('base_map1','base',(1,)),('base_map2','base',(2,)),('repair_map0','repair',(0,))]:
            for status in STATUSES:
                for conflict in (False,True):
                    for kind in ('old_source_patient','old_reference_patient','other_actor_new_activity','unrelated_unknown_control'):
                        rr=[r for r in chosen if r['mode']==mode and r['mapping_shift'] in maps and r['initial_status']==status and r['history_conflict']==conflict and r['readout_kind']==kind]
                        for measure in ('correct','p_correct','p_entailed','p_contradicted','p_undetermined','choice_mass','greedy_label_valid'):
                            v={}
                            for f,sids in nk.items():
                                obs=[r for r in rr if r['pair_id'] in sids];assert len(obs)==4*len(maps)
                                v[f]=100*float(np.mean([r['p_relation'][measure[2:]] if measure.startswith('p_') and measure!='p_correct' else r[measure] for r in obs]))
                            key=f'{status}/conflict{int(conflict)}/{kind}/{label}/{measure}';out['nli']['cells'][co+'/'+key]=stat(v);nv[status,conflict,kind,label,measure]=v
                            if measure in ('correct','p_correct'):
                                for f in nk:nd[f][key]=v[f]
                for kind in ('old_source_patient','old_reference_patient','other_actor_new_activity','unrelated_unknown_control'):
                    v=diff(nv[status,True,kind,label,'correct'],nv[status,False,kind,label,'correct']);out['nli']['contrasts'][f'{co}/conflicting_minus_consistent/{status}/{kind}/{label}/correct']=stat(v)
            for kind in ('old_source_patient','old_reference_patient','other_actor_new_activity','unrelated_unknown_control'):
                for conflict in (False,True):
                    out['nli']['contrasts'][f'{co}/factual_minus_hypothetical/conflict{int(conflict)}/{kind}/{label}/correct']=stat(diff(nv['factual_report',conflict,kind,label,'correct'],nv['hypothetical_example',conflict,kind,label,'correct']))
        for status in STATUSES:
            for conflict in (False,True):
                for kind in ('old_source_patient','old_reference_patient','other_actor_new_activity','unrelated_unknown_control'):
                    out['nli']['contrasts'][f'{co}/repair_minus_base_map0/{status}/conflict{int(conflict)}/{kind}/correct']=stat(diff(nv[status,conflict,kind,'repair_map0','correct'],nv[status,conflict,kind,'base_map0','correct']))
        # Directional role carryover uses a fixed source-patient proposition;
        # unlike correct, it distinguishes which prior/final role is reused.
        for status in STATUSES:
            for label,mode,maps in [('base_all','base',(0,1,2)),('base_map0','base',(0,)),('base_map1','base',(1,)),('base_map2','base',(2,)),('repair_map0','repair',(0,))]:
                for kind in ('old_source_patient','other_actor_new_activity'):
                    rr=[r for r in chosen if r['initial_status']==status and r['mode']==mode and r['mapping_shift'] in maps and r['readout_kind']==kind]
                    for factor,other in [('initial_role','final_role'),('final_role','initial_role')]:
                        v={}
                        for f,sids in nk.items():
                            obs=[r for r in rr if r['pair_id'] in sids]
                            a=[r for r in obs if r[factor]=='initial_patient_only'];b=[r for r in obs if r[factor]=='reference_only']
                            v[f]=50*(np.mean([r['p_relation']['entailed'] for r in a])-np.mean([r['p_relation']['entailed'] for r in b])+np.mean([r['p_relation']['contradicted'] for r in b])-np.mean([r['p_relation']['contradicted'] for r in a]))
                        out['nli']['cells'][f'{co}/signed_{factor}/{status}/{kind}/{label}']=stat(v)
        out['nli']['per_family'][co]=[dict(verb_family=f,source_items=nk[f],**nd[f]) for f in sorted(nk)]
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--directory',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--version',type=int,choices=[1,2],default=1)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,default=CACHE);n.add_argument('--raw',type=Path,required=True);n.add_argument('--base',type=Path,required=True);n.add_argument('--repair',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.action=='build':print(json.dumps(build(a.cache,a.out),indent=2))
    elif a.action=='adopt':print(json.dumps(adopt(a.directory,a.reviews,a.version),indent=2))
    else:a.out.write_text(json.dumps(analyze(a.cache,a.raw,a.base,a.repair),indent=2)+'\n')
