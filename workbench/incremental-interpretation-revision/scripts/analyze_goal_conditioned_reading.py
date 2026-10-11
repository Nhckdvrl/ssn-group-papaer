"""Complete E65 goal-by-later-question matrix, without choosing successful goals."""
import argparse
import collections
import json
from pathlib import Path
from analyze_shared_source_cross_use import summarize, load
from data import sha, write_jsonl


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True);parser.add_argument('--runs',type=Path,nargs='+',required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--seed',type=int,default=65);args=parser.parse_args();metadata={r['item_id']:r for r in load(args.data)}
    reports={};effects=[];provenance=[];families=set()
    def report(key,records):
        # Same unit->sentence->lexical-cluster weighting as the E63 map.
        import numpy as np
        from analyze_reading_map import estimate
        grouped=collections.defaultdict(list)
        for row,value in records:grouped[(row['cluster_id'],row['sentence_sha256'],row['source_unit'])].append(float(value))
        sentences=collections.defaultdict(list)
        for (cluster,sentence,unit),values in grouped.items():sentences[(cluster,sentence)].append(float(np.mean(values)))
        clusters=collections.defaultdict(list)
        for (cluster,sentence),values in sentences.items():clusters[cluster].append(float(np.mean(values)))
        values={cluster:float(np.mean(v)) for cluster,v in clusters.items()}
        reports[key]=dict(estimate(values,seed=args.seed),n_records=len(records),n_source_units=len(grouped),n_sentences=len(sentences))
        effects.extend(dict(report=key,cluster_id=k,value=v) for k,v in values.items())
    for run in args.runs:
        cfg=json.loads((run/'config.json').read_text());model=Path(cfg['model_path']).name
        assert model not in families;families.add(model)
        assert cfg['data_sha256']==sha(args.data) and cfg['predictions_sha256']==sha(run/'predictions.jsonl')
        rows=load(run/'predictions.jsonl');assert len(rows)==cfg['tasks']==12*len(metadata)
        expected={(i,op,readout,mapping) for i in metadata for op in ('NONE','INITIAL','FINAL') for readout in ('words','letters') for mapping in (0,1)}
        indexed={(r['item_id'],r['operation'],r['readout'],r['mapping']):r for r in rows};assert set(indexed)==expected and len(indexed)==len(rows)
        for r in rows:
            m=metadata[r['item_id']];assert r['question']==m['question'] and r['sentence_sha256']==m['sentence_sha256']
            assert r['primed_question']==(None if r['operation']=='NONE' else m['reading_goals'][r['operation'].lower()])
        provenance.append(dict(path=str(run),config_sha256=sha(run/'config.json'),gpu_hours=cfg['gpu_hours']))
        for construction in ('MVRR','NPZ','NPS','NPVP','pooled'):
            for condition in ('gp','control'):
                for target in ('initial','final','all'):
                    for readout in ('words','letters'):
                        for same_gold in (False,True):
                            base=[r for r in rows if r['operation']=='NONE' and (construction=='pooled' or r['construction']==construction)
                                and r['condition']==condition and (target=='all' or r['question_target']==target) and r['readout']==readout
                                and (not same_gold or r['source_gold_matches_grounding'])]
                            prefix=f'{model}/{construction}/{condition}/{target}/{readout}/same_gold{same_gold}'
                            for metric in ('correct','p_correct'):
                                for op in ('NONE','INITIAL','FINAL'):
                                    paired=[(b,indexed[(b['item_id'],op,readout,b['mapping'])]) for b in base]
                                    report(prefix+'/'+metric+'/'+op,[(a,a[metric]) for b,a in paired])
                                    if op!='NONE':report(prefix+'/'+metric+'/'+op+'-NONE',[(a,float(a[metric])-float(b[metric])) for b,a in paired])
                                pair=[(indexed[(b['item_id'],'INITIAL',readout,b['mapping'])],indexed[(b['item_id'],'FINAL',readout,b['mapping'])]) for b in base]
                                report(prefix+'/'+metric+'/FINAL-INITIAL',[(f,float(f[metric])-float(i[metric])) for i,f in pair])
                            for op in ('INITIAL','FINAL'):
                                paired=[(b,indexed[(b['item_id'],op,readout,b['mapping'])]) for b in base]
                                for name,selector in [('wrong_to_right',lambda b,a:not b['correct'] and a['correct']),('right_to_wrong',lambda b,a:b['correct'] and not a['correct'])]:
                                    report(prefix+'/'+name+'/'+op,[(a,selector(b,a)) for b,a in paired])
                                for exact in (False,True):
                                    eligible=[(b,a) for b,a in paired if a['exact_primed_question']==exact]
                                    report(prefix+f'/exact_primed_question{exact}/correct/{op}-NONE',[(a,float(a['correct'])-float(b['correct'])) for b,a in eligible])
        # Strict joint success across both targets, for each option mapping before averaging.
        for condition in ('gp','control'):
            for construction in ('MVRR','NPZ','NPS','NPVP','pooled'):
                for readout in ('words','letters'):
                    source_groups=collections.defaultdict(list)
                    for r in rows:
                        if r['condition']==condition and r['readout']==readout and (construction=='pooled' or r['construction']==construction):source_groups[(r['source_unit'],r['mapping'],r['operation'])].append(r)
                    for op in ('NONE','INITIAL','FINAL'):
                        successes=[];deltas=[]
                        for (unit,mapping,operation),group in source_groups.items():
                            if operation!=op:continue
                            assert {'initial','final'}<={r['question_target'] for r in group}
                            success=all(r['correct'] for r in group);baseline=all(r['correct'] for r in source_groups[(unit,mapping,'NONE')])
                            successes.append((group[0],success));deltas.append((group[0],float(success)-float(baseline)))
                        prefix=f'{model}/{construction}/{condition}/{readout}/joint_all_questions_correct'
                        report(prefix+'/'+op,successes)
                        if op!='NONE':report(prefix+'/'+op+'-NONE',deltas)
    assert families=={'Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'}
    effects_path=args.out.with_suffix('.cluster-effects.jsonl');write_jsonl(effects_path,effects)
    args.out.write_text(json.dumps(dict(data_sha256=sha(args.data),runs=provenance,reports=reports,cluster_effects_path=str(effects_path),cluster_effects_sha256=sha(effects_path),
        interpretation='Complete fixed goal-by-evaluation matrix; same_goldFalse means all source gold strata. Original sentences/questions preserved. Other-target effects differ from same-question repetition. Joint answers are behavioral coherence, not proof of a single hidden parse. No automatic idea qualification.'),ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
