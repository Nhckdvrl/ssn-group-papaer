"""E52 secondary word unexpectedness/response association, never conflict awareness."""
import argparse
import collections
import json
from pathlib import Path

import numpy as np
from analyze_reading_map import load
from data import sha


def association(values):
    if len(values) < 3:
        return dict(status='Too few lexical clusters',n_clusters=len(values),correlation=None,ci95=None)
    xy=np.array([values[k] for k in sorted(values)],dtype=float)
    x,y=xy[:,0],xy[:,1]
    if np.std(x)<1e-12 or np.std(y)<1e-12:
        return dict(status='No predictor or response variation',n_clusters=len(values),correlation=None,ci95=None)
    observed=float(np.corrcoef(x,y)[0,1])
    rng=np.random.default_rng(52);draws=[];invalid=0
    for _ in range(100):
        sampled=xy[rng.integers(0,len(xy),size=(100,len(xy)))]
        centered=sampled-sampled.mean(axis=1,keepdims=True)
        numerator=(centered[:,:,0]*centered[:,:,1]).sum(axis=1)
        denominator=np.sqrt((centered[:,:,0]**2).sum(axis=1)*(centered[:,:,1]**2).sum(axis=1))
        usable=denominator>1e-12
        draws.extend((numerator[usable]/denominator[usable]).tolist());invalid+=int((~usable).sum())
    return dict(status='Descriptive Pearson association',n_clusters=len(values),correlation=observed,
        ci95=np.quantile(draws,[.025,.975]).tolist() if draws else None,
        valid_bootstrap_draws=len(draws),undefined_bootstrap_draws=invalid)


def analyze(data, answer_runs, word_runs, out):
    metadata={r['item_id']:r for r in load(data)}
    words={};word_cfg={};answers=collections.defaultdict(lambda:collections.defaultdict(list));references=[]
    for directory in word_runs:
        cfg=json.loads((directory/'config.json').read_text())
        assert cfg['surprisal_sha256']==sha(directory/'surprisal.jsonl')
        model=Path(cfg['model_path']).name;assert model not in words
        word_cfg[model]=cfg;words[model]={}
        references.append(dict(kind='word',path=str(directory),configuration_sha256=sha(directory/'config.json')))
        for r in load(directory/'surprisal.jsonl'):
            m=metadata[r['item_id']];assert r['sentence_sha256']==m['sentence_sha256']
            assert m['disamb_word_index'] is not None
            assert r['displayed_word']==m['sentence'].split()[m['disamb_word_index']]
            words[model][r['item_id']]=r
    seen=set();answer_dtypes={}
    for directory in answer_runs:
        cfg=json.loads((directory/'config.json').read_text())
        assert cfg['predictions_sha256']==sha(directory/'predictions.jsonl')
        model=Path(cfg['model_path']).name
        if model not in words:continue
        assert cfg['model_manifest_sha256']==word_cfg[model]['model_manifest_sha256']
        dtype=cfg['arguments']['dtype'];assert answer_dtypes.setdefault(model,dtype)==dtype
        references.append(dict(kind='answer',path=str(directory),configuration_sha256=sha(directory/'config.json')))
        for r in load(directory/'predictions.jsonl'):
            if r['mode']!='sequence' or r['reading']!='R0' or r['repair'] or not r['matched_question_exact']:continue
            assert r['sentence_sha256']==metadata[r['item_id']]['sentence_sha256']
            key=(model,r['item_id'],r['format'],r['order'],r['prompt_index'],r['mapping'])
            assert key not in seen;seen.add(key)
            for metric in ('correct','p_correct'):
                if r[metric] is not None:answers[(model,r['format'],metric)][r['item_id']].append(float(r[metric]))
    groups=collections.defaultdict(list)
    for r in metadata.values():groups[(r.get('analysis_pair_id',r['pair_id']),r['question'])].append(r)
    reports={};exclusions=collections.Counter()
    for (model,fmt,metric),scores in sorted(answers.items()):
        for construction in ('NPZ','NPS','MVRR','NPVP'):
            for stratum in ('genuine','NEITHER','initial_all'):
                def eligible(m):
                    if m['construction']!=construction:return False
                    if stratum=='genuine':return m['genuine']
                    if m.get('analysis_question_target',m['question_target'])!='initial':return False
                    return stratum=='initial_all' or m['semantic_stratum']=='NEITHER'
                for word_metric in ('raw_bits','wt_bits'):
                    values=collections.defaultdict(list)
                    for group in groups.values():
                        if not all(eligible(m) and m['item_id'] in scores and m['item_id'] in words[model] for m in group):continue
                        if {m.get('analysis_condition',m['condition']) for m in group}!={'gp','control'}:continue
                        observed=[words[model][m['item_id']] for m in group]
                        if len({r['displayed_word'] for r in observed})!=1:
                            exclusions['Different word bytes/punctuation']+=1;continue
                        if any(r['sentence_final_word'] or r['contains_terminal_punctuation'] for r in observed):
                            exclusions['Terminal-word boundary convention']+=1;continue
                        cells=collections.defaultdict(list)
                        for m in group:
                            condition=m.get('analysis_condition',m['condition']);uid=m['item_id']
                            cells[condition].append((words[model][uid][word_metric],float(np.mean(scores[uid]))))
                        gp=np.mean(cells['gp'],axis=0);control=np.mean(cells['control'],axis=0)
                        cluster=group[0].get('analysis_cluster_id',group[0]['cluster_id'])
                        values[cluster].append((float(gp[0]-control[0]),float(1-gp[1]),float(control[1]-gp[1])))
                    clustered={k:np.mean(v,axis=0) for k,v in values.items()}
                    for outcome,index in [('GP_response_error',1),('control_minus_GP_response',2)]:
                        key='/'.join((model,construction,fmt,stratum,metric,word_metric,outcome))
                        reports[key]=association({k:(v[0],v[index]) for k,v in clustered.items()})
    out.write_text(json.dumps(dict(data_sha256=sha(data),runs=references,reports=reports,
        exclusion_counts_across_analysis_slices=dict(exclusions),answer_dtypes=answer_dtypes,
        word_dtypes={m:cfg.get('dtype','bfloat16') for m,cfg in word_cfg.items()},
        interpretation='Secondary within-construction association across linked lexical clusters. Word scores use raw sentence prefixes; responses use their declared task. NEITHER/initial_all responses are published-convention agreement. Unexpectedness is not conflict awareness, correlation is not a causal revision mechanism, and absent/constant data is not zero association.'),indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--answer-runs',type=Path,nargs='+',required=True)
    parser.add_argument('--word-runs',type=Path,nargs='+',required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    analyze(args.data,args.answer_runs,args.word_runs,args.out)
