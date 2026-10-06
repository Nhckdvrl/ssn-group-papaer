"""Complete E63 QA/role map; role annotation failures remain missing, not errors."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from analyze_reading_map import estimate,load
from analyze_paraphrases import PATTERNS
from data import sha,write_jsonl
from data_v2 import digest


def summarize(records):
    """Mean mappings/questions within unit, donors within identical S, then clusters."""
    units=collections.defaultdict(list);missing=0
    for r,v in records:
        if v is None:missing+=1;continue
        units[(r['cluster_id'],r['sentence_sha256'],r['source_unit'])].append(float(v))
    sentences=collections.defaultdict(list)
    for (cluster,sentence,unit),v in units.items():sentences[(cluster,sentence)].append(float(np.mean(v)))
    clusters=collections.defaultdict(list)
    for (cluster,sentence),v in sentences.items():clusters[cluster].append(float(np.mean(v)))
    values={k:float(np.mean(v)) for k,v in clusters.items()}
    return dict(estimate(values,seed=63),n_records=len(records),n_missing=missing,n_source_units=len(units),n_sentences=len(sentences)),values


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--sources',type=Path,required=True)
    ap.add_argument('--runs',type=Path,nargs='+',required=True);ap.add_argument('--audits',type=Path,nargs='+',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    sources={r['item_id']:r for r in load(args.sources)};metadata={r['item_id']:r for r in load(args.data)}
    labels={};audit_reports=[]
    for p in args.audits:
        assert (p/'step5/summary.json').exists(),'T4 audit must finish before any outcome analysis'
        for r in load(p/'step5/annotated.jsonl'):
            assert r['item_id'] not in labels,'Never select duplicate label versions';labels[r['item_id']]=r
        audit_reports.append(dict(path=str(p),scope=json.loads((p/'scope.json').read_text()),summary=json.loads((p/'step5/summary.json').read_text()),annotation_sha256=sha(p/'step5/annotated.jsonl')))
    reports={};effects=[];runs=[];counts=collections.Counter();families=set()
    def report(label,records):
        result,values=summarize(records);reports[label]=result
        effects.extend(dict(report=label,cluster_id=k,value=v) for k,v in values.items())
    for p in args.runs:
        cfg=json.loads((p/'config.json').read_text());model=Path(cfg['model_path']).name
        assert model not in families;families.add(model)
        assert cfg['data_sha256']==sha(args.data)
        assert cfg['predictions_sha256']==sha(p/'predictions.jsonl') and cfg['qa_predictions_sha256']==sha(p/'qa-predictions.jsonl')
        qa=load(p/'qa-predictions.jsonl');roles=load(p/'predictions.jsonl')
        assert len(qa)==cfg['qa_tasks'] and len(roles)==cfg['role_tasks']==2*len(cfg['cohort'])
        qi={(r['item_id'],r['readout'],r['mapping'],r['operation']):r for r in qa};assert len(qi)==len(qa)
        assert {k[:-1] for k in qi if k[-1]=='BASE'}=={k[:-1] for k in qi if k[-1]=='PAIR'}
        ri={}
        for r in roles:
            key=r['item_id'],r['reading'];assert key not in ri
            s=sources[r['item_id']];assert s['sentence_sha256']==r['sentence_sha256'] and r['text_sha256']==digest(r['text'])
            packet='SOURCE:\n'+s['sentence']+'\n\nPARAPHRASE:\n'+r['text'].rsplit('</think>',1)[-1]
            annotation=labels.get('E53-T4:'+digest(packet));category=None
            unfinished=('<think>' in r['text'] and '</think>' not in r['text'])
            if not unfinished:assert annotation is not None,'Every output requires completed audit coverage, including explicit failures'
            if not unfinished and annotation and annotation.get('step5_status') in ('agreed','adjudicated'):
                assert annotation['sentence_sha256']==digest(packet)
                category=PATTERNS[tuple(annotation['step5_annotation']['option_labels'])]
            rr=dict(r,source_unit=r['item_id'],category=category,metrics={
                'correct_roles':None if category is None else float(category=='CORRECT_ROLES'),
                'GP_misreading':None if category is None else float(category=='GP_MISREADING'),
                'OTHER':None if category is None else float(category=='OTHER'),
                'task_success':None if category is None else float(category=='CORRECT_ROLES' and not r['capped'] and bool(r['text'].strip())),
                'annotation_missing':float(category is None),'capped':float(r['capped']),
                'automatic_two_sentences':float(r['automatic_two_sentences'])})
            ri[key]=rr;counts[(model,category or 'UNKNOWN')]+=1
        assert {u for u,op in ri if op=='BASE'}=={u for u,op in ri if op=='PAIR'}==set(cfg['cohort'])
        for r in qa:
            s=metadata[r['item_id']]
            assert r['sentence_sha256']==s['sentence_sha256'] and r['question']==s['question'] and r['source_unit']==s['source_unit']
            assert r['source_unit'] in cfg['cohort']
        runs.append(dict(path=str(p),config_sha256=sha(p/'config.json'),gpu_hours=cfg['gpu_hours'],cohort=cfg['cohort']))
        for c in ('MVRR','NPZ','NPS','NPVP','pooled'):
            for condition in ('gp','control'):
                rr=[r for r in ri.values() if r['condition']==condition and (c=='pooled' or r['construction']==c)]
                for metric in ('correct_roles','GP_misreading','OTHER','task_success','annotation_missing','capped','automatic_two_sentences'):
                    prefix=f'{model}/{c}/{condition}/roles/{metric}'
                    for op in ('BASE','PAIR'):report(prefix+'/'+op,[(r,r['metrics'][metric]) for r in rr if r['reading']==op])
                    pairs=[(ri[(r['item_id'],'BASE')],r) for r in rr if r['reading']=='PAIR']
                    report(prefix+'/PAIR-BASE',[(a,None if a['metrics'][metric] is None or b['metrics'][metric] is None else a['metrics'][metric]-b['metrics'][metric]) for b,a in pairs])
                for target in ('initial','final','all'):
                    for readout in ('words','letters'):
                        for same_gold in (False,True):
                            sub=[r for r in qa if r['condition']==condition and r['readout']==readout and (c=='pooled' or r['construction']==c) and (target=='all' or r['question_target']==target) and (not same_gold or r['source_gold_matches_grounding'])]
                            prefix=f'{model}/{c}/{condition}/QA/{target}/{readout}/same_gold{same_gold}'
                            for metric in ('correct','p_correct'):
                                for op in ('BASE','PAIR'):report(prefix+'/'+metric+'/'+op,[(r,r[metric]) for r in sub if r['operation']==op])
                                pairs=[(qi[(r['item_id'],r['readout'],r['mapping'],'BASE')],r) for r in sub if r['operation']=='PAIR']
                                report(prefix+'/'+metric+'/PAIR-BASE',[(a,float(a[metric])-float(b[metric])) for b,a in pairs])
                            if sub:
                                transitions=collections.Counter()
                                joint=[]
                                for b,a in pairs:
                                    # pairs here contain the same rows for both metrics; hard transitions precede averaging.
                                    transitions[('right' if b['correct'] else 'wrong')+'->'+('right' if a['correct'] else 'wrong')]+=1
                                    rb,ra=ri[(a['source_unit'],'BASE')],ri[(a['source_unit'],'PAIR')]
                                    value=None if rb['category'] is None or ra['category'] is None else float(not b['correct'] and a['correct'] and rb['category']!='CORRECT_ROLES' and ra['category']=='CORRECT_ROLES')
                                    joint.append((a,value))
                                reports[prefix+'/hard_transitions']=dict(n_tasks=len(pairs),counts=dict(transitions))
                                report(prefix+'/joint_QA_role_repair',joint)
    assert families=={'Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'},'Full predetermined family panel required'
    effect=args.out.with_suffix('.cluster-effects.jsonl');write_jsonl(effect,effects)
    args.out.write_text(json.dumps(dict(data_sha256=sha(args.data),sources_sha256=sha(args.sources),runs=runs,audits=audit_reports,reports=reports,
        counts={m+'/'+c:n for (m,c),n in counts.items()},cluster_effects_path=str(effect),cluster_effects_sha256=sha(effect),
        interpretation='Shared task-unknown source prefix, identical donor per use. Model-specific input-only cohorts. Annotation unknown is missing in semantic estimates, separately reported. Reverse control PAIR is an opposite intervention, not same-treatment collateral damage. Whole-vector functional transfer does not establish relation-specific mediator or original GP knowledge. No automatic promotion.'),ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
