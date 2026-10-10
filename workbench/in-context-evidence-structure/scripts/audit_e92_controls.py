"""Complete the registered E92 control summaries; not an independent reviewer."""
import argparse,json,math
from pathlib import Path


def main():
    a=argparse.ArgumentParser();a.add_argument('path');p=Path(a.parse_args().path)
    cs=[json.loads(s) for s in (p/'contexts.jsonl').read_text().splitlines()]
    rr=[json.loads(s) for s in (p/'behavior.jsonl').read_text().splitlines()]
    analysis=json.loads((p/'analysis.json').read_text());run=json.loads((p/'run.json').read_text())
    assert len(cs)==len(rr)==run['args']['n']
    out={'independent_scientific_audit':False,'n_contexts':len(rr),'registered_control_readouts':{},'rule_response_recompute_max':0.}
    for c,r in zip(cs,rr):
        assert c['context']==r['context'] and len(r['conditions'])==34
        for role in (0,1):assert sum(d['role']==role for d in c['demos'])==8
        for q in c['queries']:assert q['text'] not in {d['text'] for d in c['demos']}
        for rel in ('same','different'):
            for world in ('base','flip'):
                cb=c['base_b_criterion']^(world=='flip');ca=cb^(rel=='different')
                assert r['gold'][rel+'_'+world]==[(q['food'],q['service'])[ca] for q in c['queries']]
            for ns in ('shared','far'):
                for mode in ('native','gate','instruction'):
                    b=r['conditions'][f'{rel}_{ns}_base_{mode}']['z'];f=r['conditions'][f'{rel}_{ns}_flip_{mode}']['z'];g=r['gold'][rel+'_base']
                    inds=[i for i,q in enumerate(c['queries']) if q['food']!=q['service']]
                    response=sum(g[i]*(b[i]-f[i]) for i in inds)/(2*len(inds))
                    saved=analysis['criterion_responses'][f'{rel}_{ns}_{mode}']['context_responses'][c['context']]
                    out['rule_response_recompute_max']=max(out['rule_response_recompute_max'],abs(response-saved))
        assert all(math.isfinite(z) for v in r['conditions'].values() for z in v['z'])
    for k in rr[0]['conditions']:
        if not k.startswith(('oracle_','probe_','single_')):continue
        totals={'discordant_correct':0,'discordant_n':0,'concordant_correct':0,'concordant_n':0,'argmax_correct':0,'valid':0,'n':0}
        for c,r in zip(cs,rr):
            if k.startswith('oracle_'):_,rel,w=k.split('_');g=r['gold'][rel+'_'+w]
            elif k.startswith('probe_'):_,ns,w=k.split('_');g=r['b_gold'][w]
            else:g=r['gold'][k.removeprefix('single_')+'_base']
            score=r['conditions'][k]
            for i,q in enumerate(c['queries']):
                typ='discordant' if q['food']!=q['service'] else 'concordant'
                totals[typ+'_n']+=1;totals[typ+'_correct']+=int((score['z'][i]>0)==(g[i]>0))
                totals['n']+=1;totals['valid']+=int(score['argmax_class'][i]!=0);totals['argmax_correct']+=int(score['argmax_class'][i]==g[i])
        out['registered_control_readouts'][k]=totals
    out['single_source_pair_average_discordant_accuracy']=.5
    out['single_source_note']='Both criterion worlds have identical A-only inputs and opposite discordant gold; .5 is a design identity, not observed inability.'
    assert out['rule_response_recompute_max']<1e-10
    (p/'registered_controls_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print('All rows/conditions, gold and original response metrics recomputed; max',out['rule_response_recompute_max'])


if __name__=='__main__':main()
