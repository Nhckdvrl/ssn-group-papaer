"""Complete E95 dispatch audit and explicitly post-hoc rule-profile analysis."""
import argparse, hashlib, itertools, json, math
from pathlib import Path
from e95_source_grouping import CELLS, records, world, estimate, analyze


def key(r):
    return (r['mode'],r['context'],r['pa'],r['cb'],r['pb'],r['kind'],r['query'])


def joint_profiles(cs, rows):
    result={}
    for mode in sorted({r['mode'] for r in rows}):
        profiles=[]
        for c in cs:
            rr=[r for r in rows if r['mode']==mode and r['context']==c['context'] and r['kind'] in ('native','probe')]
            if not rr: continue
            for pa,cb,pb in itertools.product((1,-1),(0,1),(1,-1)):
                ds=world(c,pa,cb,pb); fit=[]; pred=[]
                for role,kind in ((0,'native'),(1,'probe')):
                    rs=sorted([r for r in rr if (r['pa'],r['cb'],r['pb'],r['kind'])==(pa,cb,pb,kind)],key=lambda r:r['query'])
                    assert len(rs)==4
                    vals=[r['score']['class'] for r in rs]; pred.append(vals)
                    fit.append([(cc,pp) for cc in (0,1) for pp in (1,-1)
                        if all(pp*d['x'][cc]==d['y'] for d in ds if d['role']==role)
                        and all(pp*x[cc]==v for x,v in zip(CELLS,vals))])
                local=all(fit); joint=any(a[0]==b[0] for a,b in itertools.product(*fit))
                profiles.append({'context':c['context'],'pa':pa,'cb':cb,'pb':pb,'predA':pred[0],'predB':pred[1],
                    'local_functions':fit,'locally_valid':local,'jointly_valid':joint,
                    'locally_valid_but_jointly_invalid':local and not joint,
                    'unresolved_profile':any(v==0 for v in pred[0]+pred[1])})
        ids=sorted({r['context'] for r in profiles}); out={'n_worlds':len(profiles),'profiles':profiles}
        for k in ('locally_valid','jointly_valid','locally_valid_but_jointly_invalid','unresolved_profile'):
            out[k]=estimate([sum(r[k] for r in profiles if r['context']==ci)/8 for ci in ids])
        result[mode]=out
    return {'analysis_type':'POST-HOC; full frozen world profiles, not new model evidence', 'modes':result}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',default='results/e95/qwen35_discovery'); a=ap.parse_args()
    p=Path(a.source); pre=json.loads((p/'preflight.json').read_text()); args=pre['args']
    cs=[json.loads(s) for s in (p/'contexts.jsonl').read_text().splitlines()]; original=records(cs)
    expected={('direct',r['context'],r['pa'],r['cb'],r['pb'],r['kind'],r['query']):r for r in original}
    expected.update({('thinking',r['context'],r['pa'],r['cb'],r['pb'],r['kind'],r['query']):r for r in original
        if r['context']<args['thinking_n'] and r['kind'] in ('native','criterion','probe')})
    rows=[json.loads(s) for s in (p/'behavior.jsonl').read_text().splitlines()]; shard_runs=[]; batch_ids=[]
    transition=json.loads((p/'serial_dispatch_transition.json').read_text()); retained=transition['skip_batches']
    assert len(rows)==544+8*retained
    for i in range(3):
        q=p.parent/f'qwen35_thinking_part{i}'; run=json.loads((q/'run.json').read_text()); dispatch=json.loads((q/'dispatch.json').read_text())
        rr=[json.loads(s) for s in (q/'behavior.jsonl').read_text().splitlines()]
        assert len(rr)==run['n_rows']==dispatch['n_rows']
        assert run['source_script_sha256']==transition['original_engine_sha256']
        assert run['contexts_sha256']==hashlib.sha256((p/'contexts.jsonl').read_bytes()).hexdigest()
        rows+=rr; shard_runs.append(run); batch_ids+=run['batch_indices']
    assert sorted(list(range(retained))+batch_ids)==list(range(18))
    lut={key(r):r for r in rows}; assert len(lut)==len(rows)==len(expected)==688
    assert set(lut)==set(expected)
    for k,r in lut.items():
        assert all(r[f]==expected[k][f] for f in ('gold','discordant','kind','query','pa','pb','cb'))
        if r['mode']=='direct': assert math.isfinite(r['score']['z'])
        else: assert len(r['score']['token_ids'])<=3072
    order={k:i for i,k in enumerate(expected)}; rows.sort(key=lambda r:order[key(r)])
    (p/'behavior_merged.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (p/'analysis.json').write_text(json.dumps(analyze(rows),indent=2)+'\n')
    (p/'joint_rule_audit_posthoc.json').write_text(json.dumps(joint_profiles(cs,rows),indent=2)+'\n')
    tr=[r for r in rows if r['mode']=='thinking']
    audit={'n_rows':len(rows),'unique_keys':len(lut),'direct_rows':544,'thinking_rows':len(tr),'all_frozen_records_retained':True,
        'all_frozen_batches_covered':True,'initially_censored':sum(r['score']['initial_censored'] for r in tr),
        'still_censored':sum(r['score']['still_censored'] for r in tr),'unresolved':sum(not r['score']['valid'] for r in tr),
        'source_script_sha256':transition['original_engine_sha256'],'analyzer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'audit_type':'executing-agent completeness check, not independent scientific review'}
    (p/'completeness_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    # Serial stop interrupted unscored work; use the full loaded-phase interval conservatively.
    serial_upper=(p/'serial_dispatch_transition.json').stat().st_mtime-(p/'preflight.json').stat().st_mtime
    run={'original_args':args,'actual_model_type':shard_runs[0]['actual_model_type'],'serial_transition':transition,
        'original_serial_exit':'intentional interruption after retaining complete written batches',
        'serial_loaded_phase_seconds_upper_bound':serial_upper,'shard_gpu_hours':sum(r['gpu_hours'] for r in shard_runs),
        'total_gpu_hours_upper_bound':serial_upper/3600+sum(r['gpu_hours'] for r in shard_runs),'shard_runs':shard_runs,
        'n_rows':len(rows),'training':False,'precision':'bfloat16','attention':'sdpa'}
    (p/'run.json').write_text(json.dumps(run,indent=2)+'\n'); print(json.dumps(audit))


if __name__=='__main__': main()
