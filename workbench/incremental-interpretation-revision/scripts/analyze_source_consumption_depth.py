"""E60 same-source-computation, equal-budget early/late access contrasts."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np

from analyze_reading_map import estimate,load
from data import sha,write_jsonl
from source_consumption_depth import OPERATIONS

COMPARISONS=[(o,'BASE') for o in OPERATIONS[1:]]+[
    ('CUT_EARLY_QUARTER','CUT_LATE_QUARTER'),('CUT_EARLY_HALF','CUT_LATE_HALF')]


def key(r):return r['item_id'],r['readout'],r['mapping']


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--runs',type=Path,nargs='+',required=True);ap.add_argument('--e54-runs',type=Path,nargs='+',required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    data={r['item_id']:r for r in load(args.data)}
    expected={(uid,readout,mapping) for uid in data for readout in ('words','letters') for mapping in (0,1)}
    previous={}
    for directory in args.e54_runs:
        cfg=json.loads((directory/'config.json').read_text());assert cfg.get('predictions_sha256')==sha(directory/'predictions.jsonl')
        name=Path(cfg['model_path']).name;assert name not in previous
        previous[name]=(cfg,{key(r):r for r in load(directory/'predictions.jsonl') if r['operation']=='CAUSAL'})
    reports={};effects=[];runs=[];diagnostics={};seen=set()
    for directory in args.runs:
        cfg=json.loads((directory/'config.json').read_text());assert cfg.get('predictions_sha256')==sha(directory/'predictions.jsonl')
        assert cfg['data_sha256']==sha(args.data)
        model=Path(cfg['model_path']).name;assert model not in seen;seen.add(model)
        old_cfg,old=previous[model];assert cfg['model_manifest_sha256']==old_cfg['model_manifest_sha256']
        rows=load(directory/'predictions.jsonl');assert len(rows)==cfg['tasks']==len(expected)*len(OPERATIONS)
        index={(r['operation'],*key(r)):r for r in rows};assert len(index)==len(rows)
        for operation in OPERATIONS:assert {key(r) for r in rows if r['operation']==operation}==expected
        for r in rows:
            original=data[r['item_id']]
            assert r['question']==original['question'] and r['sentence_sha256']==original['sentence_sha256']
            assert r['cut_layers']==cfg['cut_layers'][r['operation']]
        for a,b in COMPARISONS[-2:]:
            assert len(cfg['cut_layers'][a])==len(cfg['cut_layers'][b])
            for k in expected:
                assert index[(a,*k)]['removed_edges_per_cut_layer']==index[(b,*k)]['removed_edges_per_cut_layer']
        changes=[];flips=0;p_changes=[]
        for k in expected:
            r=index[('BASE',*k)];before=old[k]
            assert r['prompt_sha256']==before['prompt_sha256'] and r['candidate_gold']==before['candidate_gold']
            changes.extend(abs(a-b) for a,b in zip(r['candidate_logprobs'],before['candidate_logprobs']))
            p_changes.append(abs(r['p_correct']-before['p_correct']));flips+=r['correct']!=before['correct']
        checks=json.loads((directory/'instrument.json').read_text())
        assert all(v['every_position_within_tolerance'] for v in checks['checks'].values())
        diagnostics[model]=dict(instrument=checks,baseline_e54_max_lp_delta=max(changes),baseline_e54_hard_flips=flips,
                                baseline_e54_max_probability_delta=max(p_changes))
        runs.append(dict(path=str(directory),config_sha256=sha(directory/'config.json'),gpu_hours=cfg['gpu_hours']))
        for construction in ('MVRR','NPZ','NPS','NPVP','pooled'):
            for target in ('initial','final'):
                for readout in ('words','letters'):
                    for same_gold in (False,True):
                        subset=[r for r in rows if (construction=='pooled' or r['construction']==construction)
                                and r['question_target']==target and r['readout']==readout
                                and (not same_gold or r['source_gold_matches_grounding'])]
                        cells=collections.defaultdict(dict)
                        for r in subset:cells[r['operation']][key(r)]=r
                        for metric in ('correct','p_correct'):
                            label=f'{model}/{construction}/{target}/{readout}/same_gold{same_gold}/{metric}'
                            def summarize(raw,statistic):
                                by_question=collections.defaultdict(list)
                                for r,value in raw:by_question[(r['cluster_id'],r['pair_id'],r['question'])].append(float(value))
                                by_cluster=collections.defaultdict(list)
                                for (cluster,pair,question),values in by_question.items():by_cluster[cluster].append(float(np.mean(values)))
                                clustered={k:float(np.mean(v)) for k,v in by_cluster.items()}
                                effects.extend(dict(report=label,statistic=statistic,cluster_id=k,value=v) for k,v in clustered.items())
                                return dict(estimate(clustered,seed=60),n_tasks=len(raw),n_question_pairs=len(by_question))
                            report=dict(cells={},contrasts={})
                            for operation,group in cells.items():
                                for condition in ('gp','control'):
                                    report['cells'][operation+'/'+condition]=summarize([(r,r[metric]) for r in group.values() if r['condition']==condition],'cell/'+operation+'/'+condition)
                            for operation,reference in COMPARISONS:
                                a,b=cells.get(operation,{}),cells.get(reference,{});common=a.keys() & b.keys()
                                contrast=operation+'-'+reference;gains={};transitions={}
                                for condition in ('gp','control'):
                                    local=[k for k in common if a[k]['condition']==condition]
                                    gains[condition]=summarize([(a[k],float(a[k][metric])-float(b[k][metric])) for k in local],contrast+'/gain/'+condition)
                                    if metric=='correct':
                                        transitions[condition]=dict(n_tasks=len(local),counts=dict(collections.Counter(('right' if b[k]['correct'] else 'wrong')+'->'+('right' if a[k]['correct'] else 'wrong') for k in local)),
                                            wrong_to_right=summarize([(a[k],not b[k]['correct'] and a[k]['correct']) for k in local],contrast+'/wrong_to_right/'+condition),
                                            right_to_wrong=summarize([(a[k],b[k]['correct'] and not a[k]['correct']) for k in local],contrast+'/right_to_wrong/'+condition))
                                paired=collections.defaultdict(dict)
                                for k in common:
                                    r=a[k];q=(r['cluster_id'],r['pair_id'],r['question'],r['mapping'])
                                    paired[q][r['condition']]=(r,float(a[k][metric])-float(b[k][metric]))
                                reduction=[(v['gp'][0],v['gp'][1]-v['control'][1]) for v in paired.values() if {'gp','control'} <= v.keys()]
                                report['contrasts'][contrast]=dict(gains=gains,transitions=transitions,gap_reduction=summarize(reduction,contrast+'/gap_reduction'))
                            reports[label]=report
    assert seen==set(previous),'Predetermined full family panel required'
    effect_path=args.out.with_suffix('.cluster-effects.jsonl');write_jsonl(effect_path,effects)
    args.out.write_text(json.dumps(dict(data_sha256=sha(args.data),runs=runs,diagnostics=diagnostics,reports=reports,
        cluster_effects_path=str(effect_path),cluster_effects_sha256=sha(effect_path),
        interpretation='Source states unchanged under verified downstream-only edge removal; equal-count early/late windows. All windows, families, targets/readouts and damage reported. Source comprehension is not evidence of a particular internal parse. No automatic claim promotion or winning-window selection.'),indent=2)+'\n')


if __name__=='__main__':main()
