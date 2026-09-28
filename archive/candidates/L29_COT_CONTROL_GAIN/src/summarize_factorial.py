"""Summarize the three-arm behavioral control audit at question level."""
import collections,json,pathlib,random,statistics

ROOT=pathlib.Path(__file__).resolve().parents[1]
STEPS=('step_0100','step_1400','step_2800')
ARMS=('structural','neutral','active')
CONTRASTS={
    'total_refresh_gain':('structural','active'),
    'keyword_cue_gain':('structural','neutral'),
    'explicit_prohibition_increment':('neutral','active'),
}

def quantile(xs,p):
    xs=sorted(xs); pos=(len(xs)-1)*p; i=int(pos)
    return xs[i]+(xs[min(i+1,len(xs)-1)]-xs[i])*(pos-i)

def interval(values,seed=290913):
    if not values:
        return None
    rng=random.Random(seed)
    draws=[statistics.mean(rng.choices(values,k=len(values))) for _ in range(5000)]
    return [quantile(draws,.025),quantile(draws,.975)]

def arm_risks(step,eligible):
    raw=ROOT/'results/raw'
    main=json.loads((raw/(step+'_rollout.json')).read_text())
    structural=json.loads((raw/(step+'_rollout_structural.json')).read_text())
    assert main['complete'] and structural['complete']
    rows=[r for d in (main,structural) for r in d['records'] if r['state_id'] in eligible]
    byq=collections.defaultdict(lambda:collections.defaultdict(list))
    for row in rows:
        byq[row['question_id']][row['arm']].append(float(row['violation32']))
    return {q:{arm:statistics.mean(v[arm]) for arm in ARMS} for q,v in byq.items()
            if all(v[arm] for arm in ARMS)}

def summarize(label,eligible_by_step):
    perstep={step:arm_risks(step,eligible_by_step[step]) for step in STEPS}
    result={'selection':label,'steps':{},'late_minus_early':{}}
    for step,rows in perstep.items():
        contrasts={name:[v[a]-v[b] for v in rows.values()] for name,(a,b) in CONTRASTS.items()}
        result['steps'][step]={
            'n_questions':len(rows),
            'arm_risk32':{arm:statistics.mean(v[arm] for v in rows.values()) for arm in ARMS},
            'contrasts':{name:{'estimate':statistics.mean(vals),'ci95':interval(vals)}
                         for name,vals in contrasts.items()},
            'question_arm_risks':rows,
        }
    early,late=perstep[STEPS[0]],perstep[STEPS[-1]]
    questions=sorted(early.keys()&late.keys())
    for name,(a,b) in CONTRASTS.items():
        diffs=[(late[q][a]-late[q][b])-(early[q][a]-early[q][b]) for q in questions]
        result['late_minus_early'][name]={'n_questions':len(diffs),
            'estimate':statistics.mean(diffs) if diffs else None,
            'ci95':interval(diffs), 'question_differences':dict(zip(questions,diffs))}
    return result

def main():
    raw=ROOT/'results/raw'
    support=json.loads((ROOT/'results/audit_support_summary.json').read_text())
    natural={s:json.loads((raw/(s+'_natural.json')).read_text()) for s in STEPS}
    own={s:{r['state_id'] for r in natural[s]['records'] if r['cut']} for s in STEPS}
    common95=set(support['common_state_ids'])
    common90=set(support['support_sensitivity']['0.9']['state_ids'])
    report={'status':'AUDIT_ONLY_NO_SCIENTIFIC_VERDICT','arms':{
        'structural':'length-matched continuation cue without target word',
        'neutral':'length- and target-word-matched factual problem-location cue',
        'active':'explicit target-word prohibition refresh'},
        'estimands':{
            'total_refresh_gain':'structural risk minus active risk; includes keyword cue and explicit rule',
            'keyword_cue_gain':'structural risk minus factual-cue risk',
            'explicit_prohibition_increment':'factual-cue risk minus active risk'},
        'E01A_common95':summarize('common support at q=.95',{s:common95 for s in STEPS}),
        'E01A_common90':summarize('common support at q=.90',{s:common90 for s in STEPS}),
        'E01B_natural':summarize('checkpoint-own risk-enriched states',own)}
    path=ROOT/'results/audit_factorial_control_summary.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
