"""Fresh balanced-binary local interventions for the one-shot E01R reconstruction."""
import re

FAMILIES=('case','tag')
SEMANTICS={'case':('lower','upper'),'tag':('amber','violet')}

def base_prompt(q):
    options='\n'.join(f'{chr(65+i)}) {x}' for i,x in enumerate(q['options']))
    return ('Solve the following problem step by step. The last line of your response should be '
            'the answer to the problem in the form Answer: X, where X is the chosen option letter.\n'
            +q['question']+'\n'+options+'\nRemember to put your answer on its own line after "Answer:". '
            'First, reason through the question step by step, then provide your final answer.\n\n')

def has_answer(text):
    return bool(re.search(r'(?im)^\s*(?:final\s+)?answer\s*:',text))

def _boundary(ids,n,tokenizer):
    prefix=tokenizer.decode(ids[:n],skip_special_tokens=False)
    full=tokenizer.decode(ids,skip_special_tokens=False)
    if prefix.endswith('\n'):
        return True
    if not re.search(r'[.!?]\s*$',prefix):
        return False
    return len(full)>len(prefix) and full[len(prefix)].isspace()

def choose_natural_prefix(ids,tokenizer,min_tokens=32,max_tokens=96):
    for n in range(min_tokens,min(max_tokens,len(ids))+1):
        text=tokenizer.decode(ids[:n],skip_special_tokens=False)
        if has_answer(text):
            return None
        if sum(c.isalpha() for c in text)>=20 and _boundary(ids,n,tokenizer):
            return n
    return None

def _definitions(family,mapping):
    if family=='case':
        values={'lower':'write every alphabetic letter in lowercase',
                'upper':'write every alphabetic letter in uppercase'}
    elif family=='tag':
        values={'amber':'begin with the exact tag [amber]',
                'violet':'begin with the exact tag [violet]'}
    else:
        raise ValueError(family)
    first,second=SEMANTICS[family]
    if mapping=='swapped':
        first,second=second,first
    elif mapping!='identity':
        raise ValueError(mapping)
    return {'1':(first,values[first]),'2':(second,values[second])}

def intervention(family,template,mapping,selected):
    definitions=_definitions(family,mapping)
    selected_label=next(label for label,(meaning,_) in definitions.items() if meaning==selected)
    d1,d2=definitions['1'][1],definitions['2'][1]
    if template=='A':
        text=(f'\n\nLOCAL CONTROL CODEBOOK — next reasoning sentence only:\n'
              f'Rule 1: {d1}.\nRule 2: {d2}.\n'
              f'Do not discuss the codebook. Execute Rule {selected_label} now.\n\n')
    elif template=='B':
        text=(f'\n\nFor only your next reasoning sentence, use this control codebook:\n'
              f'Rule 1 means: {d1}.\nRule 2 means: {d2}.\n'
              f'Without explaining the codebook, follow Rule {selected_label} now.\n\n')
    else:
        raise ValueError(template)
    return {'text':text,'selected':selected,'selected_label':selected_label,
            'definitions':{k:v[0] for k,v in definitions.items()}}

def first_sentence(ids,tokenizer):
    for n in range(1,len(ids)+1):
        text=tokenizer.decode(ids[:n],skip_special_tokens=True)
        if has_answer(text):
            return text.split('Answer:',1)[0],False,n
        if sum(c.isalpha() for c in text)>=8 and _boundary(ids,n,tokenizer):
            return text,True,n
    return tokenizer.decode(ids,skip_special_tokens=True),False,len(ids)

def case_metrics(text,complete):
    letters=[c for c in text if c.isalpha()]
    lower=sum(c.islower() for c in letters)
    upper=sum(c.isupper() for c in letters)
    denom=lower+upper
    return {'alphabetic_chars':denom,'lower_fraction':lower/denom if denom else None,
            'lower_strict':bool(complete and denom>=8 and lower==denom),
            'upper_strict':bool(complete and denom>=8 and upper==denom),
            'sentence_complete':complete}

def tag_metrics(text):
    match=re.match(r'^\s*\[(amber|violet)\](?=\s|[^A-Za-z]|$)',text,re.I)
    tag=match.group(1).lower() if match else None
    remainder=text[match.end():] if match else text
    meaningful=sum(c.isalpha() for c in remainder)>=8
    return {'leading_tag':tag,'meaningful_continuation':meaningful,
            'amber_success':tag=='amber' and meaningful,
            'violet_success':tag=='violet' and meaningful}
