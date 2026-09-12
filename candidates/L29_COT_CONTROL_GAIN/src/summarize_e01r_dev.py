"""Apply the frozen early-only E01R instrument gate at the question level."""
import collections,json,pathlib,random,statistics

ROOT=pathlib.Path(__file__).resolve().parents[1]

def quantile(xs,p):
    xs=sorted(xs); pos=(len(xs)-1)*p; i=int(pos)
    return xs[i]+(xs[min(i+1,len(xs)-1)]-xs[i])*(pos-i)

def ci95(xs,seed):
    rng=random.Random(seed)
    boot=[statistics.mean(rng.choices(xs,k=len(xs))) for _ in range(5000)]
    return [quantile(boot,.025),quantile(boot,.975)]

def success(row,semantic):
    key=(semantic+'_strict') if row['family']=='case' else (semantic+'_success')
    return float(row['metrics'][key])

def main():
    cfg=json.loads((ROOT/'configs/e01r.json').read_text()); gate=cfg['gate']
    natural=json.loads((ROOT/'results/raw/e01r_dev_step_0100_natural.json').read_text())
    doc=json.loads((ROOT/'results/raw/e01r_dev_step_0100_rollout.json').read_text())
    assert natural['complete'] and doc['complete']
    report={'status':'EARLY_INSTRUMENT_GATE','natural':{
        'total_questions':len(natural['records']),
        'eligible_questions':sum(r['cut'] is not None for r in natural['records']),
        'answer_by_128':sum(r['has_answer'] for r in natural['records'])},'families':{}}
    passed=[]
    for family,semantics in [('case',('lower','upper')),('tag',('amber','violet'))]:
        rows=[r for r in doc['records'] if r['family']==family]
        grouped=collections.defaultdict(lambda:collections.defaultdict(list))
        attrs={}
        for r in rows:
            grouped[r['question_id']][r['selected']].append(r); attrs[r['question_id']]=r
        perq={}; components={s:[] for s in semantics}
        for q,arms in grouped.items():
            if not all(arms[s] for s in semantics): continue
            comp={}
            for semantic in semantics:
                other=semantics[1-semantics.index(semantic)]
                comp[semantic]=statistics.mean(success(r,semantic) for r in arms[semantic])-statistics.mean(success(r,semantic) for r in arms[other])
                components[semantic].append(comp[semantic])
            perq[q]={'gain':statistics.mean(comp.values()),'components':comp,
                     'template':attrs[q]['template'],'mapping':attrs[q]['mapping']}
        gains=[v['gain'] for v in perq.values()]
        templates={t:statistics.mean(v['gain'] for v in perq.values() if v['template']==t) for t in cfg['templates']}
        mappings={m:statistics.mean(v['gain'] for v in perq.values() if v['mapping']==m) for m in cfg['mappings']}
        action_stop={s:statistics.mean(float(r['answer'] or r['eos']) for r in rows if r['selected']==s) for s in semantics}
        completion=statistics.mean(r['metrics']['sentence_complete'] for r in rows) if family=='case' else None
        meaningful=statistics.mean(r['metrics']['meaningful_continuation'] for r in rows) if family=='tag' else None
        checks={
            'enough_questions':len(perq)>=gate['minimum_eligible_questions'],
            'overall_gain':statistics.mean(gains)>=gate['minimum_overall_directional_gain'],
            'ci_lower':ci95(gains,cfg['bootstrap_seed'])[0]>gate['minimum_bootstrap_ci_lower'],
            'both_semantic_components':all(statistics.mean(v)>=gate['minimum_each_semantic_component_gain'] for v in components.values()),
            'both_templates':all(v>=gate['minimum_each_template_gain'] for v in templates.values()),
            'both_mappings':all(v>=gate['minimum_each_mapping_gain'] for v in mappings.values()),
            'answer_eos_rate':statistics.mean(action_stop.values())<=gate['maximum_answer_or_eos_rate'],
            'answer_eos_balance':max(action_stop.values())-min(action_stop.values())<=gate['maximum_action_answer_or_eos_rate_difference']}
        if family=='case': checks['sentence_completion']=completion>=gate['minimum_case_sentence_completion_rate']
        else: checks['meaningful_continuation']=meaningful>=gate['minimum_tag_meaningful_continuation_rate']
        diagnostics={}
        if family=='case':
            diagnostics['continuous_lower_fraction_gain']=statistics.mean(
                statistics.mean(r['metrics']['lower_fraction'] or 0 for r in grouped[q]['lower'])-
                statistics.mean(r['metrics']['lower_fraction'] or 0 for r in grouped[q]['upper']) for q in perq)
        report['families'][family]={'n_questions':len(perq),'gain':statistics.mean(gains),
            'ci95':ci95(gains,cfg['bootstrap_seed']),'component_gains':{s:statistics.mean(v) for s,v in components.items()},
            'template_gains':templates,'mapping_gains':mappings,'answer_eos_by_action':action_stop,
            'sentence_completion_rate':completion,'meaningful_continuation_rate':meaningful,
            'diagnostics':diagnostics,'checks':checks,'pass':all(checks.values()),'question_results':perq}
        passed.append(all(checks.values()))
    report['gate_pass']=all(passed)
    report['decision']='FREEZE_AND_RUN_E01R_A_B' if report['gate_pass'] else gate['failure_action']
    (ROOT/'results/e01r_dev_gate_summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
