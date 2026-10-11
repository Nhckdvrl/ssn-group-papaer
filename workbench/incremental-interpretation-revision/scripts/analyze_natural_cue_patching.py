"""E55 complete finite patch map; all layers/positions and both directions retained."""
import argparse
import collections
import json
from pathlib import Path

import numpy as np

from analyze_reading_map import estimate,load
from data import sha,write_jsonl


def key(r):
    return r['item_id'],r['readout'],r['mapping']


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--runs',type=Path,nargs='+',required=True)
    parser.add_argument('--e54-runs',type=Path,nargs='+',required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    metadata={r['item_id']:r for r in load(args.data)}
    source_targets=collections.defaultdict(set)
    for r in metadata.values():
        if r['condition']=='gp':source_targets[(r['source'],r['sentence_sha256'])].add(r['analysis_question_target'])
    multi={k for k,v in source_targets.items() if {'initial','final'} <= v}
    multi_pairs={(r.get('analysis_pair_id',r['pair_id']),r['question']) for r in metadata.values()
                 if r['condition']=='gp' and (r['source'],r['sentence_sha256']) in multi}
    old={}
    for directory in args.e54_runs:
        cfg=json.loads((directory/'config.json').read_text())
        assert cfg.get('predictions_sha256')==sha(directory/'predictions.jsonl')
        name=Path(cfg['model_path']).name;assert name not in old
        old[name]=({key(r):r for r in load(directory/'predictions.jsonl') if r['operation']=='CAUSAL'},cfg)
    reports={};effects=[];runs=[];diagnostics={};seen=set()
    for directory in args.runs:
        cfg=json.loads((directory/'config.json').read_text())
        assert cfg.get('predictions_sha256')==sha(directory/'predictions.jsonl'),'Incomplete/modified run'
        assert cfg['data_sha256']==sha(args.data)
        assert cfg['source_cache_sha256']==sha(directory/'source-cache.pt')
        model=Path(cfg['model_path']).name;assert model not in seen;seen.add(model)
        previous,prior_cfg=old[model]
        assert prior_cfg['model_manifest_sha256']==cfg['model_manifest_sha256']
        rows=load(directory/'predictions.jsonl')
        assert len(rows)==cfg['tasks']
        excluded={r['item_id'] for r in load(directory/'tokenization-excluded.jsonl')}
        eligible=metadata.keys()-excluded
        assert len(eligible)==cfg['eligible_qa']
        base={key(r):r for r in rows if r['operation']=='BASE'}
        expected={(uid,readout,mapping) for uid in eligible for readout in ('words','letters') for mapping in (0,1)}
        assert base.keys()==expected
        index={(r['operation'],r['layer'],r['region'],*key(r)):r for r in rows}
        assert len(index)==len(rows)
        assert len(rows)==len(expected)*(1+len(cfg['layers'])*len(cfg['regions']))
        for layer in cfg['layers']:
            for region in cfg['regions']:
                assert {key(r) for r in rows if r['operation']=='PAIR' and r['layer']==layer and r['region']==region}==expected
        deltas=[];flips=0;p_deltas=[]
        for k,r in base.items():
            original=previous[k]
            assert r['prompt_sha256']==original['prompt_sha256']
            assert r['candidate_gold']==original['candidate_gold']
            deltas.extend(abs(a-b) for a,b in zip(r['candidate_logprobs'],original['candidate_logprobs']))
            flips+=r['correct']!=original['correct'];p_deltas.append(abs(r['p_correct']-original['p_correct']))
        paired_eligible=collections.defaultdict(set)
        for uid in eligible:
            r=metadata[uid];paired_eligible[(r.get('analysis_pair_id',r['pair_id']),r['question'])].add(r['condition'])
        assert all(v=={'gp','control'} for v in paired_eligible.values())
        diagnostics[model]=dict(e54_baseline_max_lp_delta=max(deltas),e54_baseline_hard_flips=flips,
            e54_baseline_max_probability_delta=max(p_deltas),instrument=json.loads((directory/'instrument.json').read_text()),
            eligible_qa=len(eligible),excluded_qa=len(excluded),tokenization_exclusion_sha256=sha(directory/'tokenization-excluded.jsonl'))
        runs.append(dict(path=str(directory),config_sha256=sha(directory/'config.json'),gpu_hours=cfg['gpu_hours']))
        for construction in ('MVRR','NPZ','NPS','NPVP','pooled'):
            for target in ('initial','final'):
                for readout in ('words','letters'):
                    for same_gold in (False,True):
                        for coverage in ('all','multiple_uses'):
                            subset=[r for r in rows if (construction=='pooled' or r['construction']==construction)
                                and r['question_target']==target and r['readout']==readout
                                and (not same_gold or r['source_gold_matches_grounding'])
                                and (coverage=='all' or (r['pair_id'],r['question']) in multi_pairs)]
                            cells=collections.defaultdict(dict)
                            for r in subset:cells[(r['operation'],r['layer'],r['region'])][key(r)]=r
                            for metric in ('correct','p_correct'):
                                label=f'{model}/{construction}/{target}/{readout}/same_gold{same_gold}/{coverage}/{metric}'
                                def summarize(raw,statistic):
                                    by_question=collections.defaultdict(list)
                                    for r,value in raw:by_question[(r['cluster_id'],r['pair_id'],r['question'])].append(float(value))
                                    by_cluster=collections.defaultdict(list)
                                    for (cluster,pair,question),values in by_question.items():by_cluster[cluster].append(float(np.mean(values)))
                                    values={k:float(np.mean(v)) for k,v in by_cluster.items()}
                                    effects.extend(dict(report=label,statistic=statistic,cluster_id=k,value=v) for k,v in values.items())
                                    return dict(estimate(values,seed=55),n_tasks=len(raw),n_question_pairs=len(by_question))
                                reference=cells.get(('BASE',None,None),{})
                                report=dict(baseline={condition:summarize([(r,r[metric]) for r in reference.values() if r['condition']==condition],'BASE/'+condition)
                                                     for condition in ('gp','control')},patches={})
                                for layer in cfg['layers']:
                                    for region in cfg['regions']:
                                        patch=cells.get(('PAIR',layer,region),{})
                                        common=patch.keys() & reference.keys();patch_label=f'{layer}/{region}'
                                        gains={};transitions={}
                                        for condition in ('gp','control'):
                                            local=[k for k in common if patch[k]['condition']==condition]
                                            gains[condition]=summarize([(patch[k],float(patch[k][metric])-float(reference[k][metric])) for k in local],patch_label+'/gain/'+condition)
                                            if metric=='correct':
                                                counts=collections.Counter(('right' if reference[k]['correct'] else 'wrong')+'->'+('right' if patch[k]['correct'] else 'wrong') for k in local)
                                                transitions[condition]=dict(counts=dict(counts),n_tasks=len(local),
                                                    wrong_to_right=summarize([(patch[k],not reference[k]['correct'] and patch[k]['correct']) for k in local],patch_label+'/wrong_to_right/'+condition),
                                                    right_to_wrong=summarize([(patch[k],reference[k]['correct'] and not patch[k]['correct']) for k in local],patch_label+'/right_to_wrong/'+condition))
                                        paired=collections.defaultdict(dict)
                                        for k in common:
                                            r=patch[k];q=(r['cluster_id'],r['pair_id'],r['question'],r['mapping'])
                                            paired[q][r['condition']]=(r,float(patch[k][metric])-float(reference[k][metric]))
                                        reduction=[(v['gp'][0],v['gp'][1]-v['control'][1]) for v in paired.values() if {'gp','control'} <= v.keys()]
                                        report['patches'][patch_label]=dict(gains=gains,transitions=transitions,
                                            gap_reduction=summarize(reduction,patch_label+'/gap_reduction'))
                                reports[label]=report
    assert seen==set(old),'Predetermined three-family panel required'
    effect_path=args.out.with_suffix('.cluster-effects.jsonl');write_jsonl(effect_path,effects)
    args.out.write_text(json.dumps(dict(runs=runs,diagnostics=diagnostics,reports=reports,data_sha256=sha(args.data),
        cluster_effects_path=str(effect_path),cluster_effects_sha256=sha(effect_path),
        interpretation='All predetermined layers/positions and two directions; complete qualification only. No best-layer selection. PAIR uses cue->GP and GP->cue as reciprocal interventions; cue loss here is not the collateral damage of the same repair treatment. Check preserved GP final/correct relations separately; gap reduction cannot certify selective repair. Mapping-level transitions precede question/cluster averaging; same-source multiple original questions are not independent downstream-task generalization. Weak cue and narrow NPZ coverage retained.'),indent=2)+'\n')


if __name__=='__main__':main()
