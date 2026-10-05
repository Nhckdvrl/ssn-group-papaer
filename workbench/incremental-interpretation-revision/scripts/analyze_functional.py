"""Adopt independent E23 semantic judgments without lexical heuristic labels."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from analyze import estimate
from data import sha, write_jsonl


def analyze(run, reviews, idmap, out_cache):
    cfg=json.loads((run/'config.json').read_text()); assert sha(run/'generations.jsonl')==cfg['generations_sha256']
    rows=list(map(json.loads,(run/'generations.jsonl').read_text().splitlines())); assert len(rows)==224==cfg['task_count']
    mapping=json.loads(idmap.read_text()); annotations={}
    for p in reviews:
        j=json.loads(p.read_text()); assert j['model']=='gpt-6-luna'
        for a in j['output_reviews']:
            k=mapping[a['id']]; assert k not in annotations
            assert a['verdict'] in ('consistent','contradiction','uncertain','no_activity')
            assert a['episode_scope'] in ('same_activity','separate_activity','uncertain','no_activity')
            if a['verdict'] in ('consistent','contradiction'): assert a['episode_scope']=='same_activity'
            annotations[k]=(a,sha(p))
    assert set(annotations)=={r['item_id'] for r in rows}
    for r in rows:
        a,h=annotations[r['item_id']]
        assert a['completion_sha256']==r['generated_sha256'] and a['prefix_sha256']==r['prefix_sha256']
        r.update(output_audit=a,output_review_sha256=h,verdict=a['verdict'])
    assert not out_cache.exists(); write_jsonl(out_cache,rows)
    result=dict(experiment='E23',physical_tasks=224,units='percentage points',
                formulas={'observed_violation':'100 * contradiction / all outputs',
                          'possible_violation_upper':'100 * (contradiction + uncertain + no_activity) / all outputs',
                          'clear_judgment':'100 * (consistent + contradiction) / all outputs'},
                interpretation='Independent teacher judgments of first same-activity continuation. Unknown outputs stay in the denominator and are reported as bounds, not falsely graded as correct. Greedy default/recovery protocol is not a general capability verdict.',
                generation_sha256=cfg['generations_sha256'],audited_outputs_sha256=sha(out_cache),
                review_sha256=[sha(p) for p in reviews],analysis_code_sha256=sha(Path(__file__)),
                verdict_counts=dict(collections.Counter(r['verdict'] for r in rows)),
                token_cap_count=sum(r['token_cap_reached'] for r in rows),eos_count=sum(r['eos_reached'] for r in rows),
                bootstrap_draws=10000,bootstrap_seed=20261005,cells={},contrasts={},per_source={},cohorts={})
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,pair_ids=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    for stratum in ('all','eligible','clear_functional_role'):
        ix={(r['pair_id'],r['source_np_option'],r['condition'],r['role_evidence'],r['exclusion_style'],r['mode']):r for r in rows if stratum=='all' or r[stratum]}
        for option in (0,1,'both'):
            prefix=f'{stratum}/option{option}'; choices=(0,1) if option=='both' else (option,)
            # Cohort only uses BEFORE-generation prefix/fact annotation, and
            # requires the complete factorial for both role controls/styles.
            sids=sorted({r['pair_id'] for r in rows if all((r['pair_id'],o,c,e,s,m) in ix for o in choices for c in ('gp','explicit_cue') for e in ('reference_only','initial_patient_only') for s in ('named','generic') for m in ('base','one_instruction'))})
            result['cohorts'][prefix]=sids; source_details={sid:{} for sid in sids}
            for measure in ('observed_violation','possible_violation_upper','clear_judgment'):
                values={}
                for evidence in ('reference_only','initial_patient_only'):
                    for style in ('named','generic'):
                        for mode in ('base','one_instruction'):
                            for condition in ('gp','explicit_cue'):
                                v={}; cell_rows=[]
                                for sid in sids:
                                    rrs=[ix[(sid,o,condition,evidence,style,mode)] for o in choices];cell_rows.extend(rrs)
                                    def metric(r):
                                        if measure=='observed_violation':return r['verdict']=='contradiction'
                                        if measure=='possible_violation_upper':return r['verdict']!='consistent'
                                        return r['verdict'] in ('consistent','contradiction')
                                    v[sid]=float(100*np.mean([metric(r) for r in rrs]))
                                    source_details[sid][f'{measure}_{evidence}_{style}_{mode}_{condition}']=v[sid]
                                values[(evidence,style,mode,condition)]=v
                                counts=dict(collections.Counter(r['verdict'] for r in cell_rows));nclear=counts.get('consistent',0)+counts.get('contradiction',0)
                                result['cells'][f'{prefix}/{measure}/{evidence}/{style}/{mode}/{condition}']=dict(stat(v),output_count=len(cell_rows),verdict_counts=counts,clear_subset_violation_fraction=counts.get('contradiction',0)/nclear if nclear else None)
                    for style in ('named','generic'):
                        ds={}
                        for mode in ('base','one_instruction'):
                            ds[mode]=diff(values[(evidence,style,mode,'gp')],values[(evidence,style,mode,'explicit_cue')])
                            result['contrasts'][f'{prefix}/{measure}/GP_minus_cue/{evidence}/{style}/{mode}']=stat(ds[mode])
                        result['contrasts'][f'{prefix}/{measure}/recovery_history/{evidence}/{style}']=stat(diff(ds['one_instruction'],ds['base']))
                        for condition in ('gp','explicit_cue'):
                            result['contrasts'][f'{prefix}/{measure}/recovery/{evidence}/{style}/{condition}']=stat(diff(values[(evidence,style,'one_instruction',condition)],values[(evidence,style,'base',condition)]))
                    for mode in ('base','one_instruction'):
                        for condition in ('gp','explicit_cue'):
                            result['contrasts'][f'{prefix}/{measure}/named_minus_generic/{evidence}/{mode}/{condition}']=stat(diff(values[(evidence,'named',mode,condition)],values[(evidence,'generic',mode,condition)]))
            result['per_source'][prefix]=[dict(pair_id=sid,**source_details[sid]) for sid in sids]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--reviews',type=Path,nargs='+',required=True);p.add_argument('--idmap',type=Path,required=True);p.add_argument('--audited-out',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.write_text(json.dumps(analyze(a.run,a.reviews,a.idmap,a.audited_out),indent=2)+'\n')
