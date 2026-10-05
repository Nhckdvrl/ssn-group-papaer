"""E27 only adds an explicitly allowed participant, identical E26 questions."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze import estimate
from data import CACHE,sha,write_jsonl
from event_identity import digest


def build(cache,out):
    assert not out.exists()
    fs={r['id']:r for r in json.loads((cache/'E24-material-preparation-v1/fields-v3.json').read_text())['rows']}
    old=list(map(json.loads,(cache/'E26-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()));rows=[]
    for r in old:
        if r['scope']!='original_activity' or r['readout_kind']!='scope_compatibility':continue
        f=fs[r['pair_id'].split(':')[1]];allowed=f['reference_phrase'] if r['role_evidence']=='reference_only' else f['source_core_patient_np']
        proposition='In that original '+f['activity_np']+', '+f['actor']+' '+f['auxiliary']+' '+f['progressive_vp']+' '+allowed+'.'
        nr=dict(r,item_id='E27:'+r['item_id'],parent_item_id=r['item_id'],proposition=proposition,proposition_sha256=digest(proposition),
                gold=None,proposed_gold='Yes' if r['question_polarity']=='consistent' else 'No',participant_status='allowed',
                semantics='Same original actor/activity as explicit only fact, allowed participant substituted; unchanged comparative question.')
        for k in list(nr):
            if k.startswith('audit'):del nr[k]
        rows.append(nr)
    assert len(rows)==384
    write_jsonl(out,rows);return dict(variants=len(rows),candidate_sha256=sha(out))


def analyze(cache,path):
    c=json.loads((path/'config.json').read_text());assert c['predictions_sha256']==sha(path/'predictions.jsonl')
    new=list(map(json.loads,(path/'predictions.jsonl').read_text().splitlines()));assert len(new)==768==c['task_count']
    old=[]
    for mode in ('base','repair'):
        p=cache/f'runs/E26-{mode}';cfg=json.loads((p/'config.json').read_text());assert cfg['predictions_sha256']==sha(p/'predictions.jsonl')
        for k in ('model_manifest','dtype','attention','seed','tf32','thinking','torch','transformers','batch_size'):assert cfg[k]==c[k],k
        old+=[dict(r,participant_status='excluded') for r in map(json.loads,(p/'predictions.jsonl').read_text().splitlines()) if r['scope']=='original_activity' and r['readout_kind']=='scope_compatibility']
    rows=old+new;assert len(rows)==1536
    result=dict(experiment='E27',physical_tasks=768,units='percentage points',bootstrap_unit='12 same-verb families',
                interpretation='Matched positive control separates constant No, proposition verification replacing comparison, and correct comparative polarity. No new scope-capacity claim.',
                scores_sha256=c['predictions_sha256'],analysis_code_sha256=sha(Path(__file__)),cells={},contrasts={},per_family={})
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,verb_families=sorted(v))
    for stratum in ('clear_gold','prior_faithful_clear_gold'):
        sub=[r for r in rows if r['gold'] is not None and (stratum=='clear_gold' or r['prior_faithful'])]
        familyitems={r['verb_family']:{x['pair_id'] for x in sub if x['verb_family']==r['verb_family']} for r in sub}
        ix={(r['pair_id'],r['condition'],r['role_evidence'],r['exclusion_style'],r['mode'],r['participant_status'],r['question_polarity']):r for r in sub}
        keep={f:sids for f,sids in familyitems.items() if len(sids)==2 and all((sid,c,e,s,m,p,q) in ix for sid in sids for c in ('gp','explicit_cue') for e in ('reference_only','initial_patient_only') for s in ('named','generic') for m in ('base','repair') for p in ('allowed','excluded') for q in ('consistent','contradict'))}
        details={f:{} for f in keep}
        for mode in ('base','repair'):
            for condition in ('gp','explicit_cue'):
                for participant in ('allowed','excluded'):
                    for question in ('consistent','contradict'):
                        for measure in ('correct','p_yes','choice_mass'):
                            v={f:float(100*np.mean([ix[(sid,condition,e,s,mode,participant,question)][measure] for sid in sids for e in ('reference_only','initial_patient_only') for s in ('named','generic')])) for f,sids in keep.items()}
                            result['cells'][f'{stratum}/{participant}/{question}/{measure}/{mode}/{condition}']=stat(v)
                            for f in keep:details[f][f'{participant}_{question}_{measure}_{mode}_{condition}']=v[f]
                    for pattern in ('both_yes','both_no','correct_comparison'):
                        v={}
                        for f,sids in keep.items():
                            obs=[]
                            for sid in sids:
                                for e in ('reference_only','initial_patient_only'):
                                    for s in ('named','generic'):
                                        a=ix[(sid,condition,e,s,mode,participant,'consistent')];b=ix[(sid,condition,e,s,mode,participant,'contradict')]
                                        obs.append(100*int(a['p_yes']>.5 and b['p_yes']>.5) if pattern=='both_yes' else 100*int(a['p_yes']<=.5 and b['p_yes']<=.5) if pattern=='both_no' else 100*int(a['correct'] and b['correct']))
                            v[f]=float(np.mean(obs))
                        result['contrasts'][f'{stratum}/{participant}/{pattern}/{mode}/{condition}']=stat(v)
        result['per_family'][stratum]=[dict(verb_family=f,**details[f]) for f in sorted(keep)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('analyze');a.add_argument('--cache',type=Path,default=CACHE);a.add_argument('--run',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    x=p.parse_args()
    if x.action=='build':print(json.dumps(build(x.cache,x.out),indent=2))
    else:x.out.write_text(json.dumps(analyze(x.cache,x.run),indent=2)+'\n')
