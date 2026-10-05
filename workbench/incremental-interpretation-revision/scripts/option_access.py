"""E10 separates question placement from answer-option placement on original SAP."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
from data import CACHE,sha,write_jsonl
from analyze import estimate
from sap import load_sap

def tasks_access(cache,tokenizer,mixed_only=True):
    from infer import REPAIR
    system='Read the supplied sentence and answer its comprehension question. Choose the supplied answer option. Answer only A or B.'
    tasks=[]
    for qpos in ('pre','post'):
        for opos in ('pre','post'):
            if mixed_only and qpos==opos:continue
            for repair in (False,True):
                for mapping in ('option1_A','option1_B'):
                    for row in load_sap(cache):
                        a,b=(row['option1'],row['option0']) if mapping=='option1_A' else (row['option0'],row['option1'])
                        sentence=f'Here is the sentence:\n{row["sentence"]}'
                        question=f'Answer this question:\n{row["question"]}'
                        options=f'A. {a}\nB. {b}'
                        if qpos==opos:
                            query=question+'\n'+options
                            content='\n\n'.join([query,sentence] if qpos=='pre' else [sentence,query])
                        else:content='\n\n'.join([question,sentence,options] if qpos=='pre' else [options,sentence,question])
                        prompt=tokenizer.apply_chat_template([{'role':'system','content':system+('\n\n'+REPAIR if repair else '')},
                            {'role':'user','content':content}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
                        r=dict(row,question_position=qpos,option_position=opos,repair=repair,option_mapping=mapping,
                               yes_label='A' if mapping=='option1_A' else 'B',no_label='B' if mapping=='option1_A' else 'A')
                        pid=f'q_{qpos}_o_{opos}_{"repair" if repair else "base"}_{mapping}'
                        tasks.append((r,pid,prompt))
    return tasks

def combine(parent,mixed,out):
    assert not out.exists(),'immutable combined run'
    source=[];configs=[]
    for path,is_parent in ((parent,True),(mixed,False)):
        c=json.loads((path/'config.json').read_text());p=path/'predictions.jsonl'
        assert c['predictions_sha256']==sha(p)
        rr=[json.loads(l) for l in p.read_text().splitlines()];assert len(rr)==c['task_count']==1152
        configs.append(c)
        for row in rr:
            r=dict(row)
            if is_parent:
                qpos='post' if r['query_order']=='reg' else 'pre'
                r.update(question_position=qpos,option_position=qpos,reused_from_experiment='E09',
                         reused_predictions_sha256=c['predictions_sha256'])
                r['prompt_id']=f'q_{qpos}_o_{qpos}_{"repair" if r["repair"] else "base"}_{r["option_mapping"]}'
            source.append(r)
    assert len(source)==2304 and len({(r['item_id'],r['prompt_id']) for r in source})==2304
    out.mkdir(parents=True);write_jsonl(out/'predictions.jsonl',source)
    c=dict(experiment='E10',task_count=2304,new_inference_tasks=1152,reused_E09_tasks=1152,
           inference_subruns=configs,predictions_sha256=sha(out/'predictions.jsonl'),
           merge_code_sha256=sha(Path(__file__)),reuse='E09 endpoints verified byte-identical before new inference; no values invented')
    (out/'config.json').write_text(json.dumps(c,indent=2)+'\n')

def analyze_access(rows):
    out={'cells':{},'placement_effects':{},'placement_by_cue':{},'factor_interactions':{},
         'interpretation':'Questions and options moved independently; original content/gold unchanged; E09 identical corners reused.'}
    for family in ('pooled','NPZ','NPS','MVRR'):
        sub=rows if family=='pooled' else [r for r in rows if r['construction']==family]
        for stratum in ('all','target_xlsx','control_xlsx'):
            rr=[r for r in sub if stratum=='all' or (stratum=='target_xlsx')==r['source_target_xlsx']]
            def vals(q,o,repair,mapping,c,metric):
                v=collections.defaultdict(list)
                for r in rr:
                    if (r['question_position'],r['option_position'],r['repair'],r['option_mapping'],r['condition'])==(q,o,repair,mapping,c):v[r['pair_id']].append(r[metric])
                return {s:sum(vv)/len(vv) for s,vv in v.items()}
            def diff(a,b):return {s:a[s]-b[s] for s in sorted(a.keys()&b.keys())}
            def stat(v):
                if not v:return {'estimate':None,'ci95':None,'n_sets':0,'pair_ids':[]}
                if len(v)==1:return {'estimate':next(iter(v.values())),'ci95':None,'n_sets':1,'pair_ids':sorted(v)}
                return dict(estimate([v[s] for s in sorted(v)]),pair_ids=sorted(v))
            for repair in (False,True):
                for mapping in ('option1_A','option1_B'):
                    prefix=f'{family}/{stratum}/{"repair" if repair else "base"}/{mapping}'
                    for metric in ('correct','p_correct','choice_mass','p_yes'):
                        for q in ('pre','post'):
                            for o in ('pre','post'):
                                for c in ('gp','explicit_cue'):out['cells'][f'{prefix}/q_{q}_o_{o}/{c}/{metric}']=stat(vals(q,o,repair,mapping,c,metric))
                        effects={f'q_pre_minus_post/o_{o}':('pre',o,'post',o) for o in ('pre','post')}
                        effects.update({f'o_pre_minus_post/q_{q}':(q,'pre',q,'post') for q in ('pre','post')})
                        ds={}
                        for name,(q1,o1,q2,o2) in effects.items():
                            d={c:diff(vals(q1,o1,repair,mapping,c,metric),vals(q2,o2,repair,mapping,c,metric)) for c in ('gp','explicit_cue')}
                            ds[name]=d
                            for c in d:out['placement_effects'][f'{prefix}/{name}/{c}/{metric}']=stat(d[c])
                            out['placement_by_cue'][f'{prefix}/{name}/GP_minus_cue/{metric}']=stat(diff(d['gp'],d['explicit_cue']))
                        for c in ('gp','explicit_cue'):
                            out['factor_interactions'][f'{prefix}/question_by_options/{c}/{metric}']=stat(diff(ds['q_pre_minus_post/o_pre'][c],ds['q_pre_minus_post/o_post'][c]))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,default=CACHE/'runs/E09')
    p.add_argument('--mixed',type=Path,default=CACHE/'runs/E10-mixed');p.add_argument('--out',type=Path,default=CACHE/'runs/E10');a=p.parse_args();combine(a.parent,a.mixed,a.out)
