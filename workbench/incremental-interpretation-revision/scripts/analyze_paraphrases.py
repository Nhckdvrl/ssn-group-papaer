"""E53 source-paired T4 map; missing labels are explicit, never semantic errors."""
import argparse
import collections
import json
from pathlib import Path

import numpy as np
from data import sha,write_jsonl
from data_v2 import digest
from analyze_reading_map import estimate,load
from paraphrase_map import sentence_parts

PATTERNS={('ENTAILED','CONTRADICTED'):'CORRECT_ROLES',('CONTRADICTED','ENTAILED'):'GP_MISREADING',('NEITHER','NEITHER'):'OTHER'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--metadata',type=Path,required=True)
    ap.add_argument('--data',type=Path,required=True);ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--audits',type=Path,nargs='+',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    metadata={r['item_id']:r for r in load(args.metadata)};sources={r['item_id']:r for r in load(args.data)}
    labels={};audit_reports=[]
    for directory in args.audits:
        step=directory/'step5';assert (step/'summary.json').exists(),'T4 audit incomplete'
        for r in load(step/'annotated.jsonl'):
            assert r['item_id'] not in labels,'Do not select duplicate audit versions'
            labels[r['item_id']]=r
        audit_reports.append(dict(path=str(directory),scope=json.loads((directory/'scope.json').read_text()),
            summary=json.loads((step/'summary.json').read_text()),annotation_sha256=sha(step/'annotated.jsonl')))
    source_quality={};source_pairs={}
    for uid,s in sources.items():
        members=[metadata[k] for k in s['member_ids']]
        assert all(r['sentence_sha256']==s['sentence_sha256'] for r in members)
        def acceptable(r):
            passes=r.get('step5_passes',[])
            return len(passes)==2 and all(a['grammar']=='acceptable' for a in passes) and r.get('step5_annotation',{}).get('grammar','acceptable')=='acceptable'
        source_quality[uid]=all(acceptable(r) for r in members)
        # Collapse duplicate QA for the same source sentence; different source
        # pairs remain visible but their shared lexical cluster is resampled once.
        source_pairs[uid]=sorted({(r.get('analysis_pair_id',r['pair_id']),r.get('subtype') or '',
            r['construction'],r.get('analysis_condition',r['condition']),r.get('analysis_cluster_id',r['cluster_id'])) for r in members})
    raw=[];run_reports=[];counts=collections.Counter();task_keys=set()
    for directory in args.runs:
        config=json.loads((directory/'config.json').read_text());assert config.get('predictions_sha256')==sha(directory/'predictions.jsonl')
        assert config['data_sha256']==sha(args.data)
        model=Path(config['model_path']).name;run_reports.append(dict(path=str(directory),config_sha256=sha(directory/'config.json')))
        for r in load(directory/'predictions.jsonl'):
            uid=r['item_id'];s=sources[uid];assert r['sentence_sha256']==s['sentence_sha256'] and r['text_sha256']==digest(r['text'])
            key=model,uid,r['format'],r['reading'];assert key not in task_keys;task_keys.add(key)
            final=r['text'].rsplit('</think>',1)[-1];packet='SOURCE:\n'+s['sentence']+'\n\nPARAPHRASE:\n'+final
            annotation=labels.get('E53-T4:'+digest(packet));category='UNKNOWN'
            unfinished=('<think>' in r['text'] and '</think>' not in r['text'])
            if not unfinished:assert annotation is not None,'Every final output needs a completed audit record, including explicit annotation failures'
            if annotation is not None and not unfinished and annotation.get('step5_status') in ('agreed','adjudicated'):
                assert annotation['sentence_sha256']==digest(packet)
                category=PATTERNS[tuple(annotation['step5_annotation']['option_labels'])]
            completed=not r['capped'] and not unfinished and bool(final.strip())
            metrics=dict(task_success=float(category=='CORRECT_ROLES' and completed),
                observed_GP_misreading=float(category=='GP_MISREADING' and completed),
                other=float(category=='OTHER' and completed),unknown=float(category=='UNKNOWN'),
                capped=float(r['capped']),unfinished_thinking=float(unfinished),
                automatic_two_sentences=float(len(sentence_parts(r['text']))==2))
            counts[(model,category)]+=1
            for pair,subtype,construction,condition,cluster in source_pairs[uid]:
                raw.append(dict(model=model,format=r['format'],reading=r['reading'],source_id=uid,pair=(pair,subtype),
                    cluster=cluster,construction=construction,condition=condition,quality=source_quality[uid],metrics=metrics))
    reports={};effects=[]
    for model in sorted({r['model'] for r in raw}):
        for construction in sorted({r['construction'] for r in raw}|{'pooled'}):
            for fmt in ('P-A','P-B'):
                for quality in ('acceptable','all_source_grammar'):
                    subset=[r for r in raw if r['model']==model and r['format']==fmt and (construction=='pooled' or r['construction']==construction)
                        and (quality!='acceptable' or r['quality'])]
                    for metric in ('task_success','observed_GP_misreading','other','unknown','capped','unfinished_thinking','automatic_two_sentences'):
                        cells=collections.defaultdict(dict)
                        for r in subset:
                            k=(r['reading'],r['condition'],r['cluster'],r['pair']);cells[k][r['source_id']]=r['metrics'][metric]
                        qcells=collections.defaultdict(dict)
                        for (reading,condition,cluster,pair),values in cells.items():qcells[(reading,condition)][(cluster,pair)]=float(np.mean(list(values.values())))
                        for reading in ('R0','R1','R8'):
                            common=qcells[(reading,'gp')].keys()&qcells[(reading,'control')].keys()
                            for condition in ('gp','control'):qcells[(reading,condition)]={k:v for k,v in qcells[(reading,condition)].items() if k in common}
                        def cluster_mean(values):
                            grouped=collections.defaultdict(list)
                            for (cluster,pair),value in values.items():grouped[cluster].append(value)
                            return {k:float(np.mean(v)) for k,v in grouped.items()}
                        def summarize(values,statistic):
                            values=cluster_mean(values)
                            effects.extend(dict(model=model,construction=construction,format=fmt,stratum=quality,metric=metric,
                                statistic=statistic,cluster_id=k,value=v) for k,v in values.items())
                            return estimate(values)
                        gaps={reading:{k:qcells[(reading,'control')][k]-v for k,v in qcells[(reading,'gp')].items()}
                            for reading in ('R0','R1','R8')}
                        report=dict(cells={f'{reading}/{condition}':summarize(qcells[(reading,condition)],f'cell/{reading}/{condition}')
                            for reading in ('R0','R1','R8') for condition in ('gp','control')},
                            gaps={reading:summarize(values,f'gap/{reading}') for reading,values in gaps.items()},reductions={},gains={})
                        for reading in ('R1','R8'):
                            common=gaps['R0'].keys()&gaps[reading].keys()
                            report['reductions'][reading]=summarize({k:gaps['R0'][k]-gaps[reading][k] for k in common},f'reduction/{reading}')
                            report['gains'][reading]={}
                            for condition in ('gp','control'):
                                a,b=qcells[('R0',condition)],qcells[(reading,condition)];common=a.keys()&b.keys()
                                report['gains'][reading][condition]=summarize({k:b[k]-a[k] for k in common},f'gain/{reading}/{condition}')
                        reports[f'{model}/{construction}/{fmt}/{quality}/{metric}']=report
    effects_path=args.out.with_suffix('.cluster-effects.jsonl');write_jsonl(effects_path,effects)
    report=dict(data_sha256=sha(args.data),metadata_sha256=sha(args.metadata),runs=run_reports,audits=audit_reports,
        source_quality=dict(acceptable=sum(source_quality.values()),all=len(source_quality)),
        format_parser='Number markers removed from every cached output; original raw metrics retained unchanged. Source-paper metric is auxiliary, not T4 gold.',
        counts={f'{m}/{c}':n for (m,c),n in counts.items()},reports=reports,
        cluster_effects_path=str(effects_path),cluster_effects_sha256=sha(effects_path),
        interpretation='Task success uses all preselected inputs; missing/cap/unfinished are explicit and not semantic misreadings. T4 concerns faithful expressed roles, not literal open-world contradiction. Same source sentence is never an independent QA replicate.')
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
