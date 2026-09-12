"""Audit support before continuation outcomes; bootstrap scientific questions."""
import argparse,collections,hashlib,json,pathlib,random,statistics
ROOT=pathlib.Path(__file__).resolve().parents[1]

def quantile(xs,p):
    xs=sorted(xs); pos=(len(xs)-1)*p; i=int(pos)
    return xs[i]+(xs[min(i+1,len(xs)-1)]-xs[i])*(pos-i)

def max_window_mean(xs,width=16):
    width=min(width,len(xs))
    return max(statistics.mean(xs[i:i+width]) for i in range(len(xs)-width+1))

def length_reference(rows,length,p):
    refs=[r['reference_all']['token_nll'][:length] for r in rows if 'reference_all' in r and len(r['reference_all']['token_nll'])>=length]
    if not refs: return None
    return {'n':len(refs),'mean_nll':quantile([statistics.mean(x) for x in refs],p),
            'max_window16_nll':quantile([max_window_mean(x) for x in refs],p)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--phase',choices=['natural','support','effects'],required=True); args=ap.parse_args()
    raw=ROOT/'results/raw'; cfg=json.loads((ROOT/'configs/audit.json').read_text())
    docs={s:json.loads((raw/(s+'_natural.json')).read_text()) for s in cfg['model_steps']}
    assert all(d['complete'] for d in docs.values())
    states={r['state_id']:r for d in docs.values() for r in d['records'] if r['cut']}
    report={'status':'AUDIT_ONLY_NO_SCIENTIFIC_VERDICT','state_counts':{},'thresholds':{}}
    for s,d in docs.items():
        report['state_counts'][s]={}; report['thresholds'][s]={}
        for f in cfg['families']:
            rows=[r for r in d['records'] if r['family']==f]
            report['state_counts'][s][f]={'total':len(rows),'legal_forks':sum(r['cut'] is not None for r in rows),'compliant32':sum(r['initial_32_compliant'] for r in rows),'compliant128':sum(r['initial_128_compliant'] for r in rows),'answer_by128':sum(r['has_answer'] for r in rows)}
            ref=[r['reference32'] for r in rows if 'reference32' in r]
            report['thresholds'][s][f]={k:quantile([v[k] for v in ref],cfg['support_quantile']) for k in cfg['support_statistics']} if ref else None
    if args.phase in ['support','effects']:
        scores={s:{r['state_id']:r for r in json.loads((raw/(s+'_score.json')).read_text())['records']} for s in cfg['model_steps']}
        report['length_matched_support']={}
        def supported_ids(p,save_thresholds=False):
            accepted=[]
            for sid,state in states.items():
                f=state['family']; good=True
                for s in cfg['model_steps']:
                    rows=[r for r in docs[s]['records'] if r['family']==f]
                    cut=length_reference(rows,state['cut'],p)
                    if save_thresholds:
                        report['length_matched_support'].setdefault(sid,{})[s]=cut
                    if cut is None or any(scores[s][sid]['support'][k]>cut[k] for k in cfg['support_statistics']): good=False
                if good: accepted.append(sid)
            return accepted
        common=supported_ids(cfg['support_quantile'],save_thresholds=True)
        report['common_state_ids']=sorted(common)
        report['common_counts']=dict(collections.Counter(states[sid]['family'] for sid in common))
        report['common_questions']=len(set(states[sid]['question']['id'] for sid in common))
        report['common_sources']=dict(collections.Counter(states[sid]['source_step'] for sid in common))
        report['support_sensitivity']={}
        for p in cfg['support_sensitivity_quantiles']:
            ids=supported_ids(p)
            report['support_sensitivity'][str(p)]={'n_states':len(ids),
                'n_questions':len(set(states[sid]['question']['id'] for sid in ids)),
                'sources':dict(collections.Counter(states[sid]['source_step'] for sid in ids)),
                'state_ids':sorted(ids)}
        plan={s:sorted(set(common)|{sid for sid,state in states.items() if state['source_step']==s}) for s in cfg['model_steps']}
        if args.phase=='support':
            (ROOT/'configs/audit_rollout_states.json').write_text(json.dumps(plan,indent=2)+'\n')
        report['rollout_state_counts']={s:len(v) for s,v in plan.items()}
        # Score summaries are audit diagnostics, not significance tests or a selection rule.
        report['next_token_mass_gain']={}
        for s in cfg['model_steps']:
            report['next_token_mass_gain'][s]={}
            for f in ['lowercase','uppercase']:
                for leg,ids in [('A',common),('B',[sid for sid in states if states[sid]['source_step']==s])]:
                    xs=[scores[s][sid]['suffix']['neutral']['next_token_bad_mass']-scores[s][sid]['suffix']['active']['next_token_bad_mass'] for sid in ids if states[sid]['family']==f]
                    report['next_token_mass_gain'][s][leg+'_'+f]={'n_states':len(xs),'mean':statistics.mean(xs) if xs else None}
    if args.phase=='effects':
        rolls={s:json.loads((raw/(s+'_rollout.json')).read_text()) for s in cfg['model_steps']}
        assert all(x['complete'] for x in rolls.values())
        report['effects']={}; qeffects={}
        for leg in ['A','B']:
            report['effects'][leg]={}; qeffects[leg]={}
            for s in cfg['model_steps']:
                eligible=set(common) if leg=='A' else {sid for sid,st in states.items() if st['source_step']==s}
                rows=[r for r in rolls[s]['records'] if r['state_id'] in eligible]
                table={}; qe={}
                for f in cfg['families']:
                    fr=[r for r in rows if r['family']==f]; perq=collections.defaultdict(lambda:collections.defaultdict(list))
                    for r in fr: perq[r['question_id']][r['arm']].append(float(r['violation32']))
                    gains={q:statistics.mean(v['neutral'])-statistics.mean(v['active']) for q,v in perq.items() if v['neutral'] and v['active']}
                    table[f]={'n_questions':len(gains),'gain':statistics.mean(gains.values()) if gains else None,
                              'answer_rate':statistics.mean(r['answer'] for r in fr) if fr else None,'eos_rate':statistics.mean(r['eos'] for r in fr) if fr else None,
                              'arms':{arm:{'risk32':statistics.mean(r['violation32'] for r in fr if r['arm']==arm),
                                            'answer_rate':statistics.mean(r['answer'] for r in fr if r['arm']==arm),
                                            'eos_rate':statistics.mean(r['eos'] for r in fr if r['arm']==arm),
                                            'meta_discussion_rate':statistics.mean(r['meta_discussion'] for r in fr if r['arm']==arm)}
                                      for arm in ['neutral','active']} if fr else {}}
                    qe[f]=gains
                report['effects'][leg][s]=table; qeffects[leg][s]=qe
        # Overall only mixes question-family cells present at ALL checkpoints.
        for leg in ['A','B']:
            cells=set.intersection(*[{(f,q) for f,v in qeffects[leg][step].items() for q in v} for step in cfg['model_steps']])
            for step in cfg['model_steps']:
                agg=collections.defaultdict(list)
                for f,q in cells: agg[q].append(qeffects[leg][step][f][q])
                qeffects[leg][step]['overall_common_cells']={q:statistics.mean(v) for q,v in agg.items()}
                report['effects'][leg][step]['overall_common_cells']={'n_questions':len(agg),'n_question_family_cells':len(cells),
                    'gain':statistics.mean(qeffects[leg][step]['overall_common_cells'].values()) if agg else None}
        report['paired_late_minus_early']={}
        early,late=cfg['model_steps'][0],cfg['model_steps'][-1]
        for leg in ['A','B']:
            report['paired_late_minus_early'][leg]={}
            for f in cfg['families']+['overall_common_cells']:
                a=qeffects[leg][early][f]; b=qeffects[leg][late][f]; ids=sorted(a.keys()&b.keys()); diffs=[b[i]-a[i] for i in ids]
                if diffs:
                    rng=random.Random(cfg['bootstrap_seed']); boot=[statistics.mean(rng.choices(diffs,k=len(diffs))) for _ in range(5000)]
                    result={'n_questions':len(diffs),'change':statistics.mean(diffs),'ci95':[quantile(boot,.025),quantile(boot,.975)],'question_differences':dict(zip(ids,diffs))}
                else: result={'n_questions':0,'change':None,'ci95':None}
                report['paired_late_minus_early'][leg][f]=result
    out=ROOT/'results'/('audit_'+args.phase+'_summary.json'); out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
