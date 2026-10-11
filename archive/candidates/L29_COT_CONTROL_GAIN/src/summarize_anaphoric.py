"""Question-level summary for the target-free anaphoric reminder audit."""
import collections,json,pathlib,random,statistics

ROOT=pathlib.Path(__file__).resolve().parents[1]
STEPS=('step_0100','step_1400','step_2800')

def quantile(xs,p):
    xs=sorted(xs); pos=(len(xs)-1)*p; i=int(pos)
    return xs[i]+(xs[min(i+1,len(xs)-1)]-xs[i])*(pos-i)

def interval(xs):
    if not xs: return None
    rng=random.Random(290913)
    boot=[statistics.mean(rng.choices(xs,k=len(xs))) for _ in range(5000)]
    return [quantile(boot,.025),quantile(boot,.975)]

def risks(step,eligible):
    doc=json.loads((ROOT/'results/raw'/(step+'_rollout_anaphoric.json')).read_text())
    assert doc['complete']
    byq=collections.defaultdict(lambda:collections.defaultdict(list))
    for row in doc['records']:
        if row['state_id'] in eligible:
            byq[row['question_id']][row['arm']].append(float(row['violation32']))
    return {q:{a:statistics.mean(v[a]) for a in ('anaphoric_neutral','anaphoric_active')}
            for q,v in byq.items() if v['anaphoric_neutral'] and v['anaphoric_active']}

def summarize(eligible_by_step):
    per={s:risks(s,eligible_by_step[s]) for s in STEPS}; out={'steps':{},'late_minus_early':{}}
    for s,rows in per.items():
        gains=[v['anaphoric_neutral']-v['anaphoric_active'] for v in rows.values()]
        out['steps'][s]={'n_questions':len(rows),
            'neutral_risk32':statistics.mean(v['anaphoric_neutral'] for v in rows.values()),
            'active_risk32':statistics.mean(v['anaphoric_active'] for v in rows.values()),
            'gain':statistics.mean(gains),'gain_ci95':interval(gains),'question_arm_risks':rows}
    early,late=per[STEPS[0]],per[STEPS[-1]]; qs=sorted(early.keys()&late.keys())
    diffs=[(late[q]['anaphoric_neutral']-late[q]['anaphoric_active'])-
           (early[q]['anaphoric_neutral']-early[q]['anaphoric_active']) for q in qs]
    out['late_minus_early']={'n_questions':len(diffs),'estimate':statistics.mean(diffs) if diffs else None,
        'ci95':interval(diffs),'question_differences':dict(zip(qs,diffs))}
    return out

def main():
    support=json.loads((ROOT/'results/audit_support_summary.json').read_text())
    common95=set(support['common_state_ids']); common90=set(support['support_sensitivity']['0.9']['state_ids'])
    own={}
    for s in STEPS:
        doc=json.loads((ROOT/'results/raw'/(s+'_natural.json')).read_text())
        own[s]={r['state_id'] for r in doc['records'] if r['cut']}
    out={'status':'AUDIT_ONLY_NO_SCIENTIFIC_VERDICT',
         'active':'Keep following the forbidden-word requirement stated earlier.',
         'neutral':'Keep reasoning with the relevant information stated earlier.',
         'target_word_repeated_in_suffix':False,
         'E01A_common95':summarize({s:common95 for s in STEPS}),
         'E01A_common90':summarize({s:common90 for s in STEPS}),
         'E01B_natural':summarize(own)}
    (ROOT/'results/audit_anaphoric_summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
