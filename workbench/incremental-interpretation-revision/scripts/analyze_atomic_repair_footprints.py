"""E70 all-source atomic changes and joint presence; missing labels stay missing."""
import argparse
import collections
import json
from pathlib import Path
from analyze_source_bank_routes import summarize
from data import sha,write_jsonl


def analyze(root,out):
    scope=json.loads((root/'scope-v1.json').read_text());summary=json.loads((root/'step5/summary.json').read_text())
    packets={r['item_id']:r for r in map(json.loads,(root/'packets-v1.jsonl').read_text().splitlines())}
    assert scope['packet_data_sha256']==sha(root/'packets-v1.jsonl')==summary['data_sha256']
    assert summary['items']==len(packets)==scope['distinct_packets'],'Never analyze an empty/partial queue as complete'
    assignments=[json.loads(l) for l in (root/'assignments-v1.jsonl').read_text().splitlines()];assert scope['assignment_sha256']==sha(root/'assignments-v1.jsonl')
    labels={r['item_id']:r for r in map(json.loads,(root/'step5/annotated.jsonl').read_text().splitlines())};assert set(labels)==set(packets)
    observed={}
    for uid,r in labels.items():
        p=packets[uid];assert r['sentence_sha256']==p['sentence_sha256']
        observed[uid]=r['step5_annotation']['label'] if r.get('step5_status') in ('agreed','adjudicated') else None
        if observed[uid] is not None:assert r['step5_annotation']['question_id']==p['question_id']
    models=sorted({r['model'] for r in assignments});idx={(r['model'],r['source_unit'],r['operation']):r for r in assignments};assert len(idx)==len(assignments)
    assert {x[:2] for x in idx if x[2]=='BASE_BANK'}=={x[:2] for x in idx if x[2]=='TARGET_BANK'}
    reports={};effects=[];counts=collections.Counter()
    def report(key,records):
        v,cs=summarize(records,seed=70);reports[key]=v
        effects.extend(dict(report=key,cluster_id=c,value=x) for c,x in cs.items())
    def atom(row,q):
        if row['unfinished_thinking']:return None
        return observed[row['atom_packets'][q['question_id']]]
    def qsubset(row,target,gold):return [q for q in row['questions'] if (target=='all' or q['target']==target) and (gold=='both' or q['source_gold']==gold)]
    def value(row,q,metric):
        x=atom(row,q)
        if x is None:return None
        return float(x=='ENTAILED') if metric=='entailed' else float((x=='ENTAILED')==(q['source_gold']=='Yes'))
    def joint(row):
        vs=[value(row,q,'source_pattern_correct') for q in row['questions']]
        return None if any(x is None for x in vs) else float(all(vs))
    def positive_pair(row):
        initial=qsubset(row,'initial','Yes');final=qsubset(row,'final','Yes')
        if not initial or not final:return 'ineligible'
        i=[atom(row,q) for q in initial];f=[atom(row,q) for q in final]
        if any(x is None for x in i+f):return None
        return (all(x=='ENTAILED' for x in i),all(x=='ENTAILED' for x in f))
    for row in assignments:
        counts[f'{row["model"]}/{row["construction"]}/{row["condition"]}/positive_pair_eligibility/'+str(positive_pair(row)=='ineligible')]+=1
    for model in models:
        for c in ('MVRR','NPZ','NPS','NPVP','pooled'):
            for cond in ('gp','control'):
                base=[r for r in assignments if r['model']==model and r['operation']=='BASE_BANK' and r['condition']==cond and (c=='pooled' or r['construction']==c)]
                for target in ('initial','final','other','all'):
                    for gold in ('Yes','No','both'):
                        for metric in ('entailed','source_pattern_correct'):
                            prefix=f'{model}/{c}/{cond}/{target}/sourceGold{gold}/{metric}/'
                            for op in ('BASE_BANK','TARGET_BANK','TARGET_BANK-BASE_BANK'):
                                records=[]
                                for b in base:
                                    t=idx[model,b['source_unit'],'TARGET_BANK'];assert b['questions']==t['questions']
                                    for q in qsubset(b,target,gold):
                                        x=value(t if op!='BASE_BANK' else b,q,metric)
                                        if op.endswith('-BASE_BANK'):
                                            y=value(b,q,metric);x=None if x is None or y is None else x-y
                                        records.append((b,x))
                                report(prefix+op,records)
                for metric in ('joint_source_pattern','joint_lower','joint_upper'):
                    for op in ('BASE_BANK','TARGET_BANK','TARGET_BANK-BASE_BANK'):
                        records=[]
                        for b in base:
                            t=idx[model,b['source_unit'],'TARGET_BANK'];x=joint(t if op!='BASE_BANK' else b);y=joint(b)
                            if metric!='joint_source_pattern':
                                replace=0.0 if metric=='joint_lower' else 1.0
                                x=replace if x is None else x
                                # Lower effect subtracts the upper baseline, and conversely.
                                y=(1-replace if op.endswith('-BASE_BANK') else replace) if y is None else y
                            if op.endswith('-BASE_BANK'):x=None if x is None or y is None else x-y
                            records.append((b,x))
                        report(f'{model}/{c}/{cond}/{metric}/{op}',records)
                for state,code in [('both',(True,True)),('initial_only',(True,False)),('final_only',(False,True)),('neither',(False,False))]:
                    for op in ('BASE_BANK','TARGET_BANK','TARGET_BANK-BASE_BANK'):
                        records=[]
                        for b in base:
                            t=idx[model,b['source_unit'],'TARGET_BANK'];pb=positive_pair(b);pt=positive_pair(t)
                            assert (pb=='ineligible')==(pt=='ineligible')
                            if pb=='ineligible':continue
                            x=None if (pb if op=='BASE_BANK' else pt) is None else float((pb if op=='BASE_BANK' else pt)==code)
                            if op.endswith('-BASE_BANK'):x=None if pb is None or pt is None else float(pt==code)-float(pb==code)
                            records.append((b,x))
                        report(f'{model}/{c}/{cond}/positive_assertions/{state}/{op}',records)
    e=out.with_suffix('.cluster-effects.jsonl');write_jsonl(e,effects)
    out.write_text(json.dumps(dict(scope_sha256=sha(root/'scope-v1.json'),annotation_sha256=sha(root/'step5/annotated.jsonl'),summary=summary,reports=reports,counts=dict(counts),
        cluster_effects_sha256=sha(e),code_sha256=sha(Path(__file__)),
        interpretation='Semantic entailment of original published questions in generated P, not model QA or latent parse. Missing labels excluded with counts/bounds. Source No not added does not establish a correct positive relation.'),indent=2)+'\n')
    print('E70 complete map',len(reports),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();analyze(a.root,a.out)
