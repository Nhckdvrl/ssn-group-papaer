"""E20 semantic-exclusive-fact order versus last-mention effects."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze import estimate
from aspect_reference import read_run
from data import sha,write_jsonl
from late_role_evidence import adopt_roles


def adopt_order(data,reviews,idmap,out):
    report=adopt_roles(data,reviews,idmap,out)
    mapping=json.loads(idmap.read_text());facts={}
    for p in reviews:
        for a in json.loads(p.read_text())['variant_reviews']:
            assert a['facts_preserved'] in ('clear','changed','uncertain')
            facts[mapping[a['id']]]=a['facts_preserved']
    rows=list(map(json.loads,out.read_text().splitlines()))
    for r in rows:
        r.update(audit_facts_preserved=facts[r['item_id']],faithful_order=r['clear_role_evidence'] and facts[r['item_id']]=='clear')
    write_jsonl(out,rows)
    report.update(audited_sha256=sha(out),faithful_order=sum(r['faithful_order'] for r in rows))
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def analyze(cache,path,old_experiment='E19',old_order='affirm_then_negate',new_orders=('negate_then_affirm',),new_field=None):
    c0,r0=read_run(cache/'runs'/old_experiment);c1,r1=read_run(path)
    assert len(r1)==168*len(new_orders)
    for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):assert c0[k]==c1[k],k
    rows=[dict(r,fact_order=old_order) for r in r0 if r['episode_anchor']=='same']
    rows += [dict(r,fact_order=r[new_field] if new_field else new_orders[0]) for r in r1]
    assert len(rows)==168*(1+len(new_orders))
    orders=(old_order,*new_orders)
    result=dict(experiment='E20',units='bits',primary='Change in GP-minus-comma history dependence when affirmed rather than negated patient is mentioned last, same exclusive facts.',
        formulas={'R':'bits(own NP) - bits(source reference)','M':'bits(other NP) - bits(own NP)','order_history':'D_negate_then_affirm - D_affirm_then_negate'},
        interpretation='Distinguishes last-mention echo from invariant prior role influence, not hidden-state belief or raw probability-as-accuracy.',
        physical_tasks=len(r1),bootstrap_draws=10000,bootstrap_seed=20261005,cells={},contrasts={},per_source={},
        scores_sha256={old_experiment:c0['scores_sha256'],c1['experiment']:c1['scores_sha256']},analysis_code_sha256=sha(Path(__file__)))
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,pair_ids=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    for stratum in ('all','eligible','acceptable','faithful_order'):
        # Apply the new version's independently defined cohort to both orders.
        keep=set.intersection(*({(r['pair_id'],r['source_np_option'],r['condition'],r['role_evidence'],r['target_kind']) for r in r1 if (not new_field or r[new_field]==order) and (stratum=='all' or r[stratum])} for order in new_orders))
        rr=[r for r in rows if (r['pair_id'],r['source_np_option'],r['condition'],r['role_evidence'],r['target_kind']) in keep]
        ix={(r['pair_id'],r['source_np_option'],r['condition'],r['role_evidence'],r['fact_order'],r['target_kind']):r for r in rr}
        assert len(ix)==len(rr)
        for option in (0,1,'both'):
            prefix=f'{stratum}/option{option}';effects={}
            for measure in ('R','M'):
                ds={};vs={}
                for order in orders:
                    for e in ('reference_only','initial_patient_only'):
                        cells={}
                        for condition in ('gp','explicit_cue'):
                            v={}
                            for sid in {r['pair_id'] for r in rr}:
                                choices=(0,1) if option=='both' else (option,);observations=[]
                                for o in choices:
                                    own=ix.get((sid,o,condition,e,order,'source_np'));other=ix.get((sid,o,condition,e,order,'other_source_np'));ref=ix.get((sid,o,condition,e,order,'source_reference'))
                                    if any(r is None for r in (own,other,ref)):break
                                    assert own['target_context_sha256']==other['target_context_sha256']==ref['target_context_sha256']
                                    observations.append(own['target_total_bits']-ref['target_total_bits'] if measure=='R' else other['target_total_bits']-own['target_total_bits'])
                                if len(observations)==len(choices):v[sid]=float(np.mean(observations))
                            cells[condition]=v
                            result['cells'][f'{prefix}/{measure}/{order}/{e}/{condition}']=stat(v)
                        vs[(order,e)]=cells;ds[(order,e)]=diff(cells['gp'],cells['explicit_cue'])
                        result['contrasts'][f'{prefix}/{measure}/D/{order}/{e}']=stat(ds[(order,e)])
                for e in ('reference_only','initial_patient_only'):
                    for new_order in new_orders:
                        name=f'{prefix}/{measure}/order_history/{e}' if len(new_orders)==1 else f'{prefix}/{measure}/style_history/{new_order}/{e}'
                        result['contrasts'][name]=stat(diff(ds[(new_order,e)],ds[(old_order,e)]))
                for order in orders:
                    for c in ('gp','explicit_cue'):
                        result['contrasts'][f'{prefix}/{measure}/role_effect/{order}/{c}']=stat(diff(vs[(order,'reference_only')][c],vs[(order,'initial_patient_only')][c]))
                effects[measure]=ds
            common=set.intersection(*(set(v) for ds in effects.values() for v in ds.values()))
            result['per_source'][prefix]=[dict(pair_id=k,**{f'{m}_D_{order}_{e}':ds[(order,e)][k] for m,ds in effects.items() for order,e in ds}) for k in sorted(common)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--idmap',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,required=True);n.add_argument('--new',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='adopt':print(json.dumps(adopt_order(args.data,args.reviews,args.idmap,args.out),indent=2))
    else:args.out.write_text(json.dumps(analyze(args.cache,args.new),indent=2)+'\n')
