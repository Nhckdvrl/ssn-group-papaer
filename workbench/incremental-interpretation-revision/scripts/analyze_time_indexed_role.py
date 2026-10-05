"""E37 independent short-answer grades; new-event natural defaults stay qualified."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import CACHE,sha
from analyze_source_ablation import stat,diff


def analyze(cache,reviews,cross=None):
    annotations={}
    for path in reviews:
        j=json.loads(path.read_text());assert j['model']=='gpt-6-luna'
        for a in j['reviews']:
            assert a['id'] not in annotations;annotations[a['id']]=a
    assert len(annotations)==1056
    rows=[];configs=[]
    for q,n in [('current',432),('initial',192),('new',432)]:
        p=cache/f'runs/E37-{q}';c=json.loads((p/'config.json').read_text());assert sha(p/'generations.jsonl')==c['generations_sha256'];rr=list(map(json.loads,(p/'generations.jsonl').read_text().splitlines()));assert len(rr)==n==c['task_count']
        for r in rr:
            a=annotations[r['item_id']]
            for k in ('passage_sha256','question_sha256','answer_sha256'):assert a[k]==r[k]
            assert a['correct'] in (True,False,None) and a['certainty'] in ('clear','uncertain','invalid')
            r['response_audit']=a
        rows.extend(rr);configs.append(c)
    for c in configs[1:]:
        for k in ('model_manifest','dtype','tf32','attention','seed','frozen','thinking','do_sample','max_new_tokens','base_instruction','priority_instruction','batch_size'):assert c[k]==configs[0][k]
    out=dict(experiment='E37',tasks=1056,actual_gpu_hours=sum(c['gpu_hours'] for c in configs),bootstrap_unit='12 verb families, two sources averaged',bootstrap_draws=10000,bootstrap_seed=20261005,
             input_audit_sha256=configs[0]['audit_sha256'],scores_sha256=[c['generations_sha256'] for c in configs],response_review_sha256=[sha(p) for p in reviews],
             grading_caveat='First two reviewers use textual-support grading. New who/whom queries can invite natural reflexive/reciprocal defaults, so their low support agreement is not an ability error or evidence of lingering false belief. Cross-audit and ambiguous cases retained.',
             cells={},contrasts={},joint={},per_family={},cohorts={})
    wb=Path(__file__).resolve().parents[1];parent=wb/'results/E34-summary.json';pc=json.loads(parent.read_text())['nli']['cohorts'];out['parent_cohorts_sha256']=sha(parent)
    for co,keep in pc.items():
        out['cohorts'][co]=keep;v={};per={f:{} for f in keep}
        for query in ('current','initial','new'):
            for status in ('factual_report','hypothetical_example'):
                for conflict in (False,True):
                    for final in ('balanced','reference_only','initial_patient_only'):
                        for mode in (('base',) if query=='initial' else ('base','priority')):
                            rr=[r for r in rows if r['context']=='history' and r['query']==query and r['initial_status']==status and r['history_conflict']==conflict and (final=='balanced' or r['final_role']==final) and r['mode']==mode]
                            for measure in ('correct','cap_reached','source_answer','reference_answer','explicit_none_answer','uncertain_grade'):
                                vv={}
                                for f,sids in keep.items():
                                    obs=[r for r in rr if r['pair_id'] in sids];assert len(obs)==(4 if final=='balanced' else 2)
                                    if measure=='correct':a=[r['response_audit']['correct'] is True and r['response_audit']['certainty']=='clear' for r in obs]
                                    elif measure=='cap_reached':a=[r['cap_reached'] for r in obs]
                                    elif measure=='uncertain_grade':a=[r['response_audit']['certainty']!='clear' for r in obs]
                                    else:
                                        cls={'source_answer':'source_patient','reference_answer':'reference_patient','explicit_none_answer':'explicit_none'}[measure];a=[r['response_audit']['answer_class']==cls for r in obs]
                                    vv[f]=100*float(np.mean(a))
                                key=f'{query}/{status}/conflict{int(conflict)}/{final}/{mode}/{measure}';v[key]=vv;out['cells'][co+'/'+key]=stat(vv)
                                if measure=='correct':
                                    for f in keep:per[f][key]=vv[f]
        for query in ('current','new'):
            for status in ('factual_report','hypothetical_example'):
                for conflict in (False,True):
                    for final in ('balanced','reference_only','initial_patient_only'):
                        stem=f'{query}/{status}/conflict{int(conflict)}/{final}';out['contrasts'][f'{co}/priority_minus_base/{stem}/correct']=stat(diff(v[stem+'/priority/correct'],v[stem+'/base/correct']))
        for query in ('current','new'):
            rr=[r for r in rows if r['context']=='anchor' and r['query']==query]
            vv={f:100*float(np.mean([r['response_audit']['correct'] is True for r in rr if r['pair_id'] in sids])) for f,sids in keep.items()};out['cells'][f'{co}/anchor/{query}/correct']=stat(vv)
        for a,b in [('current','initial'),('current','new')]:
            index={(r['pair_id'],r['initial_status'],r['initial_role'],r['final_role'],r['query']):r for r in rows if r['context']=='history' and r['mode']=='base'}
            vv={}
            for f,sids in keep.items():
                aa=[]
                for sid in sids:
                    for status in ('factual_report','hypothetical_example'):
                        for prior in ('reference_only','initial_patient_only'):
                            for final in ('reference_only','initial_patient_only'):
                                aa.append(all(index[sid,status,prior,final,q]['response_audit']['correct'] is True for q in (a,b)))
                vv[f]=100*float(np.mean(aa))
            out['joint'][f'{co}/{a}_and_{b}/correct']=stat(vv)
        out['per_family'][co]=[dict(verb_family=f,**per[f]) for f in sorted(keep)]
    if cross:
        j=json.loads(cross.read_text());assert j['model']=='gpt-6-luna';ix={r['item_id']:r for r in rows if r['query']=='new'};assert len(j['reviews'])==len(ix)==432
        assert {a['id'] for a in j['reviews']}==set(ix)
        for a in j['reviews']:
            r=ix[a['id']]
            for k in ('passage_sha256','question_sha256','answer_sha256'):assert a[k]==r[k]
        out['new_event_cross_audit']=dict(review_sha256=sha(cross),rows=432,correct_counts=dict(collections.Counter(str(a['correct']) for a in j['reviews'])),certainty=dict(collections.Counter(a['certainty'] for a in j['reviews'])),binding_counts=dict(collections.Counter(a['entity_binding'] for a in j['reviews'])),
                                         interpretation='Independent natural-default/binding audit does not replace the original textual-support grades; no filtering of uncertain responses.')
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--reviews',type=Path,nargs='+',required=True);p.add_argument('--cross',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.cache,a.reviews,a.cross),indent=2)+'\n')
