"""E59 paired scope/response map; three-way absolute scores are not two-way scores."""
import argparse
import collections
import json
from pathlib import Path

import numpy as np
from analyze_reading_map import load,estimate
from data import sha,write_jsonl


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    reports={};effects=[];run_reports=[];seen_models=set()
    for directory in args.runs:
        cfg=json.loads((directory/'config.json').read_text());assert cfg.get('predictions_sha256')==sha(directory/'predictions.jsonl')
        model=Path(cfg['model_path']).name;assert model not in seen_models;seen_models.add(model)
        rows=load(directory/'predictions.jsonl');run_reports.append(dict(path=str(directory),config_sha256=sha(directory/'config.json')))
        assert len({(r['item_id'],r['scope'],r['readout'],r['reading'],r['mapping']) for r in rows})==len(rows)
        for construction in sorted({r['construction'] for r in rows}|{'pooled'}):
            for target in ('initial','final'):
                for label in ('ALL','ENTAILED','CONTRADICTED','NEITHER'):
                    for readout in ('letters','words'):
                        for comparable in (False,True):
                            subset=[r for r in rows if (construction=='pooled' or r['construction']==construction) and r['question_target']==target
                                and (label=='ALL' or r['literal_label']==label) and r['readout']==readout
                                and (not comparable or r['source_gold_matches_grounding'])]
                            for metric in ('correct','p_correct'):
                                items=collections.defaultdict(list)
                                for r in subset:
                                    q=r['cluster_id'],r['pair_id'],r['question']
                                    items[(r['scope'],r['reading'],r['condition'],q,r['item_id'])].append(float(r[metric]))
                                cells=collections.defaultdict(lambda:collections.defaultdict(list))
                                for (scope,reading,condition,q,item),v in items.items():cells[(scope,reading,condition)][q].append(np.mean(v))
                                cells={k:{q:float(np.mean(v)) for q,v in group.items()} for k,group in cells.items()}
                                for scope in ('O2','G2','W3'):
                                    for reading in ('R0','R1','R5'):
                                        a,b=cells.get((scope,reading,'gp'),{}),cells.get((scope,reading,'control'),{})
                                        common=a.keys()&b.keys()
                                        for condition,values in [('gp',a),('control',b)]:cells[(scope,reading,condition)]={q:v for q,v in values.items() if q in common}
                                def summarize(values,statistic):
                                    groups=collections.defaultdict(list)
                                    for (cluster,pair,question),value in values.items():groups[cluster].append(value)
                                    clustered={k:float(np.mean(v)) for k,v in groups.items()}
                                    effects.extend(dict(model=model,construction=construction,target=target,literal_label=label,readout=readout,
                                        same_gold_only=comparable,metric=metric,statistic=statistic,cluster_id=k,value=v) for k,v in clustered.items())
                                    return estimate(clustered)
                                gaps={}
                                for scope in ('O2','G2','W3'):
                                    for reading in ('R0','R1','R5'):
                                        a,b=cells[(scope,reading,'gp')],cells[(scope,reading,'control')]
                                        gaps[(scope,reading)]={q:b[q]-a[q] for q in a}
                                report=dict(cells={'/'.join(k):summarize(v,'cell/'+'/'.join(k)) for k,v in cells.items()},
                                    gaps={'/'.join(k):summarize(v,'gap/'+'/'.join(k)) for k,v in gaps.items()},grounding_gains={},grounding_gap_reduction={},reading_reductions={})
                                if comparable:
                                    for reading in ('R0','R1','R5'):
                                        report['grounding_gains'][reading]={}
                                        for condition in ('gp','control'):
                                            a,b=cells[('O2',reading,condition)],cells[('G2',reading,condition)];common=a.keys()&b.keys()
                                            report['grounding_gains'][reading][condition]=summarize({q:b[q]-a[q] for q in common},f'grounding_gain/{reading}/{condition}')
                                        a,b=gaps[('O2',reading)],gaps[('G2',reading)];common=a.keys()&b.keys()
                                        report['grounding_gap_reduction'][reading]=summarize({q:a[q]-b[q] for q in common},f'grounding_reduction/{reading}')
                                for scope in ('O2','G2','W3'):
                                    for reading in ('R1','R5'):
                                        a,b=gaps[(scope,'R0')],gaps[(scope,reading)];common=a.keys()&b.keys()
                                        report['reading_reductions'][scope+'/'+reading]=summarize({q:a[q]-b[q] for q in common},f'reading_reduction/{scope}/{reading}')
                                reports[f'{model}/{construction}/{target}/{label}/{readout}/same_gold{comparable}/{metric}']=report
    effects_path=args.out.with_suffix('.cluster-effects.jsonl');write_jsonl(effects_path,effects)
    args.out.write_text(json.dumps(dict(runs=run_reports,reports=reports,cluster_effects_path=str(effects_path),
        cluster_effects_sha256=sha(effects_path),
        interpretation='Grounding versus original compares same-gold two-option tasks only; W3 absolute accuracy/probability is not directly compared with O2/G2. Literal category and answer bias must be inspected separately. No automatic account selection.'),indent=2)+'\n')


if __name__=='__main__':main()
