"""Pre-outcome selection of original unanimous meaning contrasts within a question."""
import csv,hashlib,json
from collections import defaultdict,Counter

CATEGORIES=['Yes','Probably yes / sometimes yes','Yes, subject to some conditions','No',
            'Probably no','In the middle, neither yes nor no','I am not sure how X will interpret Y’s answer','Other']
CONTRASTS=[('negative-strength','No','Probably no',None),
           ('positive-probability-or-frequency','Yes','Probably yes / sometimes yes',64),
           ('conditional-commitment','Yes','Yes, subject to some conditions',128)]

def stable(value):return hashlib.sha256(value.encode()).hexdigest()

def prepare(root):
    path=root/'upstream/circa/circa-data.tsv'
    rows=list(csv.DictReader(path.open(),delimiter='\t'))
    assert len(rows)==34268 and len({r['id'] for r in rows})==34268
    grouped=defaultdict(list);lengths=Counter();incomplete=[]
    for r in rows:
        judges=r['judgements'].split('#');lengths[len(judges)]+=1
        assert len(judges) in [4,5]
        if len(judges)!=5:incomplete.append(r['id'])
        assert all(j in CATEGORIES for j in judges)
        c=Counter(judges);majority=max(c,key=c.get)
        assert r['goldstandard1']==(majority if c[majority]>=3 else 'NA')
        if len(judges)==5 and len(c)==1:grouped[r['context'],r['question-X']].append(r)
    pairs=[];selected={};audit={}
    for name,left,right,limit in CONTRASTS:
        eligible=[k for k,rs in grouped.items() if any(r['goldstandard1']==left for r in rs)
                  and any(r['goldstandard1']==right for r in rs)]
        eligible.sort(key=lambda k:stable(json.dumps(k,ensure_ascii=False)))
        chosen=eligible if limit is None else eligible[:limit]
        audit[name]={'eligible_questions':len(eligible),'selected_questions':len(chosen)}
        for key in chosen:
            picks=[min((r for r in grouped[key] if r['goldstandard1']==label),key=lambda r:stable(r['id'])) for label in [left,right]]
            group=stable(json.dumps(key,ensure_ascii=False))
            pairs.append({'contrast':name,'question_group':group,'left_id':picks[0]['id'],'right_id':picks[1]['id'],
                          'left_label':left,'right_label':right})
            for r in picks:selected[r['id']]={**r,'question_group':group}
    chosen_rows=sorted(selected.values(),key=lambda r:int(r['id']))
    return chosen_rows,pairs,{'data_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'all_source_majority_labels_match':True,'human_count_distribution':dict(lengths),
        'incomplete_human_count_ids':incomplete,'selected_all_five_unanimous':True,
        'contrasts':audit,'n_unique_rows':len(chosen_rows),
        'n_pairs':len(pairs),'n_question_groups':len({r['question_group'] for r in chosen_rows})}

def prompt(row,order):
    options=CATEGORIES if order==0 else list(reversed(CATEGORIES))
    return ('Read the short dialogue in a cooperative and casual conversation.\n'
            'Context: '+row['context']+'\nX: '+row['question-X']+'\nY: '+row['answer-Y']+'\n\n'
            'How will X interpret Y\'s answer? X will think that Y means:\n'
            +'\n'.join(f'{i+1}. {x}' for i,x in enumerate(options))+'\n'
            'Reply with only the number of the selected interpretation.\nAnswer:')

def render(tok,row,order,interface):
    p=prompt(row,order)
    return p if interface=='bare' else tok.apply_chat_template([{'role':'user','content':p}],
        tokenize=False,add_generation_prompt=True,enable_thinking=False)
