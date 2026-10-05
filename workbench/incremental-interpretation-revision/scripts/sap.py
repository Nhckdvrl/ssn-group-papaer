"""Published SAP questions/options/gold, with independently pinned source bytes."""
import collections
import hashlib
import json
from pathlib import Path
import pandas as pd
from data import CACHE,SOURCES,record,sha,write_jsonl
from analyze import estimate

FILES=['LICENSE','readme_SAP.txt','Items for all subsets.xlsx','Surprisals/data/items_ClassicGP.csv','SAP_preprocessing.R']

def audit_sap(cache=CACHE):
    root=cache/'upstream/sap-discovery'
    rev=SOURCES['sap'][1]
    assert json.loads((root/'commit.json').read_text())['sha']==rev
    tree=json.loads((root/'tree.json').read_text());assert not tree['truncated']
    blobs={f['path']:f for f in tree['tree'] if f['type']=='blob'}
    files={}
    for name in FILES:
        p=root/name;b=p.read_bytes();git_sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        assert git_sha==blobs[name]['sha'] and len(b)==blobs[name]['size'],name
        files[name]=dict(sha256=sha(p),git_blob_sha1=git_sha,bytes=len(b))
    assert 'MIT License' in (root/'LICENSE').read_text()
    x=pd.read_excel(root/'Items for all subsets.xlsx',sheet_name='NPSNPZMVRR');x=x[x['item'].notna()].copy()
    c=pd.read_csv(root/'Surprisals/data/items_ClassicGP.csv')
    assert len(x)==len(c)==72 and not x.duplicated(['item','condition']).any()
    joined=x.merge(c,on=['item','condition'],suffixes=('_xlsx','_csv'),validate='one_to_one')
    for field in ('Question','Option1','Option0','Answer','ambiguous'):
        assert (joined[field+'_xlsx'].fillna('')==joined[field+'_csv'].fillna('')).all(),field
    assert (joined['Unnamed: 3'].fillna('')==joined['unambiguous'].fillna('')).all()
    def marked(v):return isinstance(v,str) and v.strip()=='X'
    differences=[dict(item=int(r['item']),construction=r['condition'].split('_')[0],
                      xlsx=marked(r['Ambiguity targeted?_xlsx']),csv=marked(r['Ambiguity targeted?_csv']))
                 for _,r in joined.iterrows() if marked(r['Ambiguity targeted?_xlsx'])!=marked(r['Ambiguity targeted?_csv'])]
    report=dict(url=SOURCES['sap'][0],revision=rev,license='MIT',proxy_used=False,files=files,
                subset='72 published ClassicGP paired sentence/questions; no participant or huge fitted-model downloads',
                rows=72,sentence_variants=144,lexical_sets=24,
                constructions=x['condition'].value_counts().to_dict(),source_option1_gold=int((x.Answer==1).sum()),
                source_option0_gold=int((x.Answer==0).sum()),yes_no_questions=int(((x.Option1=='Yes')&(x.Option0=='No')).sum()),
                target_mark_xlsx=sum(marked(v) for v in x['Ambiguity targeted?']),
                target_mark_csv=sum(marked(v) for v in c['Ambiguity targeted?']),target_mark_disagreements=differences,
                canonical='Original Excel; same sentence/question/options/gold in CSV, both target flags retained')
    (root/'audit.json').write_text(json.dumps(report,indent=2)+'\n');return report

def load_sap(cache=CACHE):
    root=cache/'upstream/sap-discovery';a=json.loads((root/'audit.json').read_text())
    assert a['revision']==SOURCES['sap'][1]
    for name,meta in a['files'].items():assert sha(root/name)==meta['sha256']
    x=pd.read_excel(root/'Items for all subsets.xlsx',sheet_name='NPSNPZMVRR');x=x[x['item'].notna()]
    csv_rows=pd.read_csv(root/'Surprisals/data/items_ClassicGP.csv').set_index(['item','condition'])
    rows=[]
    for _,r in x.iterrows():
        i=int(r['item']);family=r['condition'].split('_')[0];other=csv_rows.loc[(r['item'],r['condition'])]
        assert r['Answer'] in (0,1)
        for condition,col,pos in [('gp','ambiguous','disambPositionAmb'),('explicit_cue','Unnamed: 3','disambPositionUnamb')]:
            rows.append(record(item_id=f'sap:{family}:{i}:{condition}',source='sap',construction=family,
                condition=condition,sentence=r[col],question=r['Question'],question_type='published_comprehension',
                gold='Yes' if r['Answer']==1 else 'No',source_row_id=f'NPSNPZMVRR:{family}:{i}',
                pair_id=f'SAP:{i}',cue_type='none' if condition=='gp' else {'NPZ':'comma','NPS':'that','MVRR':'unreduced'}[family],
                disambiguator_index=int(r[pos])-1,source_disambiguator_position_1based=int(r[pos]),
                option1=r['Option1'],option0=r['Option0'],source_answer=int(r['Answer']),
                gold_answer_text=r['Option1'] if r['Answer']==1 else r['Option0'],
                source_target_xlsx=str(r['Ambiguity targeted?']).strip()=='X',
                source_target_csv=str(other['Ambiguity targeted?']).strip()=='X',
                source_yes_no=r['Option1']=='Yes' and r['Option0']=='No',
                gold_status='published_option_choice',probability_semantics='p_yes means P(source Option1), not necessarily literal Yes',
                annotation_scope='Published upstream materials/options/answers; no agent-generated semantic labels'))
    assert len(rows)==144 and len({r['item_id'] for r in rows})==144
    return rows

def tasks_sap(cache,tokenizer):
    from infer import REPAIR
    tasks=[]
    system='Read the supplied sentence and answer its comprehension question. Choose the supplied answer option. Answer only A or B.'
    for order in ('reg','rev'):
        for repair in (False,True):
            for mapping in ('option1_A','option1_B'):
                for row in load_sap(cache):
                    a,b=(row['option1'],row['option0']) if mapping=='option1_A' else (row['option0'],row['option1'])
                    sentence=f'Here is the sentence:\n{row["sentence"]}'
                    query=f'Answer this question:\n{row["question"]}\nA. {a}\nB. {b}'
                    content='\n\n'.join([sentence,query] if order=='reg' else [query,sentence])
                    prompt=tokenizer.apply_chat_template([{'role':'system','content':system+('\n\n'+REPAIR if repair else '')},
                         {'role':'user','content':content}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
                    r=dict(row,query_order=order,repair=repair,option_mapping=mapping,
                           yes_label='A' if mapping=='option1_A' else 'B',no_label='B' if mapping=='option1_A' else 'A')
                    tasks.append((r,f'{order}_{"repair" if repair else "base"}_{mapping}',prompt))
    return tasks

def analyze_sap(rows):
    out={'cells':{},'cue_effects':{},'order_interactions':{},'mapping_effects':{},
         'interpretation':'Published original questions/options; source gold is an option index. Target flags differ in six rows. No mechanistic claim from QA alone.'}
    for family in ('pooled','NPZ','NPS','MVRR'):
        sub=rows if family=='pooled' else [r for r in rows if r['construction']==family]
        for stratum in ('all','target_xlsx','control_xlsx','target_csv','gold_option1','gold_option0'):
            rr=[r for r in sub if stratum=='all' or stratum=='target_xlsx' and r['source_target_xlsx'] or stratum=='control_xlsx' and not r['source_target_xlsx'] or stratum=='target_csv' and r['source_target_csv'] or stratum=='gold_option1' and r['source_answer']==1 or stratum=='gold_option0' and r['source_answer']==0]
            def vals(pid,c,m):
                v=collections.defaultdict(list)
                for r in rr:
                    if r['prompt_id']==pid and r['condition']==c:v[r['pair_id']].append(r[m])
                return {s:sum(vv)/len(vv) for s,vv in v.items()}
            def diff(a,b):return {s:a[s]-b[s] for s in sorted(a.keys()&b.keys())}
            def stat(v):
                if not v:return {'estimate':None,'ci95':None,'n_sets':0,'pair_ids':[]}
                if len(v)==1:return {'estimate':next(iter(v.values())),'ci95':None,'n_sets':1,'pair_ids':sorted(v)}
                return dict(estimate([v[s] for s in sorted(v)]),pair_ids=sorted(v))
            prefix=f'{family}/{stratum}'
            for m in ('correct','p_correct','choice_mass','p_yes'):
                for pid in sorted({r['prompt_id'] for r in rows}):
                    for c in ('gp','explicit_cue'):out['cells'][f'{prefix}/{pid}/{c}/{m}']=stat(vals(pid,c,m))
                    out['cue_effects'][f'{prefix}/{pid}/{m}']=stat(diff(vals(pid,'explicit_cue',m),vals(pid,'gp',m)))
                for repair in ('base','repair'):
                    for mapping in ('option1_A','option1_B'):
                        reg=f'reg_{repair}_{mapping}';rev=f'rev_{repair}_{mapping}'
                        d1=diff(vals(reg,'explicit_cue',m),vals(reg,'gp',m));d2=diff(vals(rev,'explicit_cue',m),vals(rev,'gp',m))
                        out['order_interactions'][f'{prefix}/{repair}/{mapping}/{m}']=stat(diff(d1,d2))
                    for order in ('reg','rev'):
                        for c in ('gp','explicit_cue'):
                            out['mapping_effects'][f'{prefix}/{order}/{repair}/{c}/{m}']=stat(diff(vals(f'{order}_{repair}_option1_A',c,m),vals(f'{order}_{repair}_option1_B',c,m)))
    return out

if __name__=='__main__':
    a=audit_sap();write_jsonl(CACHE/'normalized/sap.jsonl',load_sap());print(json.dumps(a,indent=2))
