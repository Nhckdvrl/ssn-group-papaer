"""Read the complete E64 QA panel while free-output annotation is still pending."""
import argparse
import json
from pathlib import Path
from analyze_source_bank_routes import summarize, load
from data import sha,write_jsonl


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--runs',type=Path,nargs='+',required=True)
    p.add_argument('--references',type=Path,nargs='+',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    metadata={r['item_id']:r for r in load(a.data)};reports={};effects=[];provenance=[];families=set()
    operations=('BASE_BANK','FULL_BANK','TARGET_BANK','CONTEXT_BANK')
    references={Path(json.loads((r/'config.json').read_text())['model_path']).name:r for r in a.references}
    def report(key,values):
        summary,clusters=summarize(values,seed=64);reports[key]=summary
        effects.extend(dict(report=key,cluster_id=k,value=v) for k,v in clusters.items())
    for run in a.runs:
        cfg=json.loads((run/'config.json').read_text());name=Path(cfg['model_path']).name;assert name not in families;families.add(name)
        assert cfg['data_sha256']==sha(a.data) and set(cfg['operations'])==set(operations)
        ref=references[name];refcfg=json.loads((ref/'config.json').read_text());assert cfg['reference_config_sha256']==sha(ref/'config.json') and cfg['cohort']==refcfg['cohort']
        previous=load(ref/'qa-predictions.jsonl');expected={(r['item_id'],r['readout'],r['mapping'],op) for r in previous for op in operations}
        rows=load(run/'qa-predictions.jsonl');indexed={(r['item_id'],r['readout'],r['mapping'],r['operation']):r for r in rows}
        assert len(indexed)==len(rows)==len(expected) and set(indexed)==expected,'Complete QA cohort required; no surviving tasks'
        for r in rows:
            m=metadata[r['item_id']];assert r['question']==m['question'] and r['sentence_sha256']==m['sentence_sha256'] and r['source_unit']==m['source_unit']
        provenance.append(dict(path=str(run),qa_predictions_sha256=sha(run/'qa-predictions.jsonl'),reference_config_sha256=sha(ref/'config.json'),tasks=len(rows)))
        for construction in ('MVRR','NPZ','NPS','NPVP','pooled'):
            for condition in ('gp','control'):
                for target in ('initial','final','all'):
                    for readout in ('words','letters'):
                        for samegold in (False,True):
                            selected=[r for r in rows if r['operation']=='BASE_BANK' and (construction=='pooled' or r['construction']==construction)
                                and r['condition']==condition and (target=='all' or r['question_target']==target) and r['readout']==readout
                                and (not samegold or r['source_gold_matches_grounding'])]
                            prefix=f'{name}/{construction}/{condition}/{target}/{readout}/same_gold{samegold}'
                            for metric in ('correct','p_correct'):
                                for op in operations:
                                    matched=[(b,indexed[(b['item_id'],readout,b['mapping'],op)]) for b in selected]
                                    report(prefix+'/'+metric+'/'+op,[(r,r[metric]) for b,r in matched])
                                    if op!='BASE_BANK':report(prefix+'/'+metric+'/'+op+'-BASE_BANK',[(r,float(r[metric])-float(b[metric])) for b,r in matched])
                                pair=[(indexed[(b['item_id'],readout,b['mapping'],'CONTEXT_BANK')],indexed[(b['item_id'],readout,b['mapping'],'TARGET_BANK')]) for b in selected]
                                report(prefix+'/'+metric+'/TARGET_BANK-CONTEXT_BANK',[(t,float(t[metric])-float(c[metric])) for c,t in pair])
    assert families=={'Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'}
    ep=a.out.with_suffix('.cluster-effects.jsonl');write_jsonl(ep,effects)
    a.out.write_text(json.dumps(dict(data_sha256=sha(a.data),runs=provenance,reports=reports,cluster_effects_sha256=sha(ep),
        scope='Complete fixed E64 QA panel only. Free-role outputs and joint repair are pending and are not interpreted.'),indent=2)+'\n')


if __name__=='__main__':main()
