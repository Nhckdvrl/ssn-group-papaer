"""POST-HOC E65/E66 input-defined goal truth; original matrix is never replaced."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import sha,write_jsonl
from analyze_reading_map import load,estimate


def main(a):
    data=load(a.data);groups=collections.defaultdict(list)
    for r in data:groups[r['source_unit']].append(r)
    truth={}
    for uid,g in groups.items():
        truth[uid]={}
        for target in ('initial','final'):
            gold={r['grounded_gold'] for r in g if r['question']==g[0]['reading_goals'][target]};assert len(gold)==1
            truth[uid][target]=next(iter(gold))
    reports={};effects=[];provenance=[]
    def report(key,records):
        sentences=collections.defaultdict(list)
        for r,v in records:sentences[(r['cluster_id'],r['sentence_sha256'])].append(float(v))
        clusters=collections.defaultdict(list)
        for (cluster,s),values in sentences.items():clusters[cluster].append(float(np.mean(values)))
        values={c:float(np.mean(v)) for c,v in clusters.items()}
        reports[key]=dict(estimate(values,seed=68),n_records=len(records),n_sentences=len(sentences))
        effects.extend(dict(report=key,cluster_id=c,value=v) for c,v in values.items())
    for p in a.runs:
        cfg=json.loads((p/'config.json').read_text());assert cfg['predictions_sha256']==sha(p/'predictions.jsonl') and cfg['data_sha256']==sha(a.data)
        model=Path(cfg['model_path']).name;rows=load(p/'predictions.jsonl');indexed={(r['item_id'],r['operation'],r['readout'],r['mapping']):r for r in rows};assert len(indexed)==len(rows)==12*len(data)
        provenance.append(dict(path=str(p),config_sha256=sha(p/'config.json')))
        for c in ('MVRR','NPZ','NPS','NPVP','pooled'):
            for cond in ('gp','control'):
                for stratum,allowed in [('all',set(groups)),('initialNo_finalYes',{u for u,g in truth.items() if g=={'initial':'No','final':'Yes'}}),('initialYes',{u for u,g in truth.items() if g['initial']=='Yes'}),('finalNo',{u for u,g in truth.items() if g['final']=='No'})]:
                    subset=[r for r in rows if r['operation']=='NONE' and r['condition']==cond and r['source_unit'] in allowed and (c=='pooled' or r['construction']==c)]
                    for read in ('words','letters'):
                        for target in ('initial','final'):
                            for gold in ('Yes','No','both'):
                                # Grounded gold is identified from immutable input item ID.
                                base=[r for r in subset if r['readout']==read and r['question_target']==target and r['source_gold_matches_grounding'] and (gold=='both' or a.metadata[r['item_id']]['grounded_gold']==gold)]
                                for metric in ('correct','p_correct'):
                                    for goal in ('NONE','INITIAL','FINAL'):
                                        pairs=[(b,indexed[(b['item_id'],goal,read,b['mapping'])]) for b in base];prefix=f'{model}/{c}/{cond}/{stratum}/{target}/{read}/evalGold{gold}/{metric}/'
                                        report(prefix+goal,[(r,r[metric]) for b,r in pairs])
                                        if goal!='NONE':report(prefix+goal+'-NONE',[(r,r[metric]-b[metric]) for b,r in pairs])
                    for read in ('words','letters'):
                        qgroups=collections.defaultdict(list)
                        for r in rows:
                            if r['condition']==cond and r['source_unit'] in allowed and r['readout']==read and (c=='pooled' or r['construction']==c):qgroups[(r['source_unit'],r['operation'],r['mapping'])].append(r)
                        for goal in ('NONE','INITIAL','FINAL'):
                            values=[];deltas=[]
                            for (u,g,m),rs in qgroups.items():
                                if g!=goal:continue
                                v=float(all(r['correct'] for r in rs));b=float(all(r['correct'] for r in qgroups[u,'NONE',m]));values.append((rs[0],v));deltas.append((rs[0],v-b))
                            prefix=f'{model}/{c}/{cond}/{stratum}/{read}/joint/'
                            report(prefix+goal,values)
                            if goal!='NONE':report(prefix+goal+'-NONE',deltas)
    e=a.out.with_suffix('.cluster-effects.jsonl');write_jsonl(e,effects)
    count=collections.Counter((g[0]['construction'],g[0]['condition'],truth[u]['initial'],truth[u]['final']) for u,g in groups.items())
    a.out.write_text(json.dumps(dict(timing='Strata defined POST-HOC after E65 effects, before E66/E67 full interpretation. Actual experiment runs identified in provenance; not the original primary analysis.',policy='Original source/Q/gold/cohort/registered matrix unchanged. Input-only truth strata, including opposite/noncanonical goals, all reported; not success-selected.',data_sha256=sha(a.data),runs=provenance,goal_truth_counts={str(k):v for k,v in count.items()},reports=reports,cluster_effects_sha256=sha(e)),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.metadata={r['item_id']:r for r in load(a.data)};main(a)
