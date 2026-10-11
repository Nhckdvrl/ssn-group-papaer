"""Complete E67 free-role transfer, and source-matched E65 QA coherence."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import sha,write_jsonl
from data_v2 import digest
from analyze_reading_map import estimate,load
from analyze_paraphrases import PATTERNS


def main(a):
    sources={r['item_id']:r for r in load(a.sources)};labels={};audits=[]
    for p in a.audits:
        assert (p/'step5/summary.json').exists()
        for r in load(p/'step5/annotated.jsonl'):
            assert r['item_id'] not in labels;labels[r['item_id']]=r
        audits.append(dict(path=str(p),annotation_sha256=sha(p/'step5/annotated.jsonl'),summary=json.loads((p/'step5/summary.json').read_text())))
    reports={};effects=[];families=set();provenance=[]
    def report(key,records):
        clustered=collections.defaultdict(list);missing=0
        for r,v in records:
            if v is None:missing+=1
            else:clustered[r['cluster_id']].append(float(v))
        values={k:float(np.mean(v)) for k,v in clustered.items()}
        reports[key]=dict(estimate(values,seed=67),n_records=len(records),n_missing=missing)
        effects.extend(dict(report=key,cluster_id=k,value=v) for k,v in values.items())
    for path in a.runs:
        cfg=json.loads((path/'config.json').read_text());model=Path(cfg['model_path']).name;assert model not in families;families.add(model)
        assert cfg['data_sha256']==sha(a.sources) and cfg['predictions_sha256']==sha(path/'predictions.jsonl')
        rows=load(path/'predictions.jsonl');indexed={(r['item_id'],r['reading']):r for r in rows};assert len(indexed)==len(rows)==3*len(sources)
        assert set(indexed)=={(u,g) for u in sources for g in ('NONE','INITIAL','FINAL')}
        for r in rows:
            s=sources[r['item_id']];assert r['text_sha256']==digest(r['text']) and s['sentence_sha256']==r['sentence_sha256']
            packet='SOURCE:\n'+s['sentence']+'\n\nPARAPHRASE:\n'+r['text'].rsplit('</think>',1)[-1]
            label=labels.get('E53-T4:'+digest(packet));unfinished='<think>' in r['text'] and '</think>' not in r['text'];category=None
            if not unfinished:assert label is not None,'Complete output audit coverage is required even for explicit failures'
            if label and not unfinished and label.get('step5_status') in ('agreed','adjudicated'):
                assert label['sentence_sha256']==digest(packet);category=PATTERNS[tuple(label['step5_annotation']['option_labels'])]
            completed=not r['capped'] and not unfinished and bool(r['text'].strip())
            r['metrics']=dict(correct_roles=None if category is None else float(category=='CORRECT_ROLES' and completed),GP_misreading=None if category is None else float(category=='GP_MISREADING' and completed),OTHER=None if category is None else float(category=='OTHER' and completed),unknown=float(category is None),capped=float(r['capped']),automatic_two_sentences=float(r['automatic_two_sentences']),correct_lower=float(category=='CORRECT_ROLES' and completed),correct_upper=float(category=='CORRECT_ROLES' and completed or category is None and completed))
        qa_path=a.qa_root/model;qc=json.loads((qa_path/'config.json').read_text());assert qc['predictions_sha256']==sha(qa_path/'predictions.jsonl')
        assert qc['data_sha256']==json.loads(a.sources.with_suffix('.manifest.json').read_text())['E65_data_sha256'] and qc['model_manifest_sha256']==cfg['model_manifest_sha256']
        qa=load(qa_path/'predictions.jsonl');assert len(qa)==qc['tasks'];assert {r['source_unit'] for r in qa}==set(sources)
        provenance.append(dict(path=str(path),config_sha256=sha(path/'config.json'),qa_config_sha256=sha(qa_path/'config.json'),gpu_hours=cfg['gpu_hours']))
        for c in ('MVRR','NPZ','NPS','NPVP','pooled'):
            for condition in ('gp','control'):
                base=[r for r in rows if r['reading']=='NONE' and r['condition']==condition and (c=='pooled' or r['construction']==c)]
                prefix=f'{model}/{c}/{condition}'
                for metric in base[0]['metrics'] if base else ('correct_roles','GP_misreading','OTHER','unknown','capped','automatic_two_sentences','correct_lower','correct_upper'):
                    for goal in ('NONE','INITIAL','FINAL'):
                        pairs=[(b,indexed[(b['item_id'],goal)]) for b in base]
                        report(prefix+'/'+metric+'/'+goal,[(r,r['metrics'][metric]) for b,r in pairs])
                        if goal!='NONE':report(prefix+'/'+metric+'/'+goal+'-NONE',[(r,None if b['metrics'][metric] is None or r['metrics'][metric] is None else r['metrics'][metric]-b['metrics'][metric]) for b,r in pairs])
                for readout in ('words','letters'):
                    for same_gold in (False,True):
                        cells=collections.defaultdict(list)
                        for q in qa:
                            if q['condition']==condition and q['readout']==readout and (c=='pooled' or q['construction']==c) and (not same_gold or q['source_gold_matches_grounding']):cells[(q['source_unit'],q['operation'],q['mapping'])].append(q)
                        joint={}
                        for (uid,goal,mapping),group in cells.items():joint[uid,goal,mapping]=all(q['correct'] for q in group)
                        for metric in ('QA_all_questions_correct','QA_and_roles_correct'):
                            for goal in ('NONE','INITIAL','FINAL'):
                                values=[];delta=[]
                                for (uid,g,mapping),success in joint.items():
                                    if g!=goal:continue
                                    r=indexed[(uid,goal)];role=r['metrics']['correct_roles'];v=float(success) if metric=='QA_all_questions_correct' else None if role is None else float(success and role)
                                    rb=indexed[(uid,'NONE')];brole=rb['metrics']['correct_roles'];b=float(joint[uid,'NONE',mapping]) if metric=='QA_all_questions_correct' else None if brole is None else float(joint[uid,'NONE',mapping] and brole)
                                    values.append((r,v));delta.append((r,None if v is None or b is None else v-b))
                                p=prefix+f'/{readout}/same_gold{same_gold}/'+metric+'/'
                                report(p+goal,values)
                                if goal!='NONE':report(p+goal+'-NONE',delta)
    assert families=={'Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'}
    effect=a.out.with_suffix('.cluster-effects.jsonl');write_jsonl(effect,effects)
    a.out.write_text(json.dumps(dict(sources_sha256=sha(a.sources),runs=provenance,audits=audits,reports=reports,cluster_effects=str(effect),cluster_effects_sha256=sha(effect),interpretation='All registered sources/families/goals; blind T4-v2 complete first. Major role preservation and explicit initial-parse additions measured separately. QA-role joint is behavioral cross-use, not proof of a unique latent parse; QA reference remains original E65.'),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--audits',type=Path,nargs='+',required=True);p.add_argument('--qa-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);main(p.parse_args())
