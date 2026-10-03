"""Lossless transport audit only; never search prose for probability numbers."""
import json
import math
import re


def normalize(text, task):
    fenced=re.fullmatch(r'\s*```(?:json)?[ \t]*\r?\n(.*?)\r?\n```\s*',text,re.DOTALL|re.IGNORECASE)
    body=fenced.group(1) if fenced else text
    try:value=json.loads(body)
    except (TypeError,ValueError):return None
    n=3 if task=='listener' else 4
    if not isinstance(value,list) or len(value)!=n:return None
    converted=[]
    for x in value:
        if type(x) is int:y=x
        elif type(x) is float and math.isfinite(x) and x.is_integer():y=int(x)
        elif type(x) is str and re.fullmatch(r'(?:0|[1-9][0-9]*)',x):y=int(x)
        else:return None
        if not 0<=y<=100:return None
        converted.append(y)
    return converted if sum(converted)==100 else None


def checks():
    positives=['[0,100,0]','```json\n[0,100,0]\n```','["0","100","0"]','[0.0,100.0,0.0]',
               '```json\n["0",100.0,0]\n```']
    negatives=['Explanation [0,100,0]','[0,100,0] explanation','[0,100,0]\n[0,100,0]',
        '[true,99,0]','[0,99,0]','[0,101,-1]','[0.5,99.5,0]','[NaN,100,0]',
        '["0%","100","0"]','["00","100","0"]','{"points":[0,100,0]}','[[0,100,0]]',
        '```json\n[0,100,0]\n``` explanation','```json\n[0,100,0]\n', '[0,100,0,0]']
    assert all(normalize(s,'listener')==[0,100,0] for s in positives)
    assert all(normalize(s,'listener') is None for s in negatives)
    assert normalize('[0,0,50,50]','speaker')==[0,0,50,50]
    return {'positive_cases':len(positives)+1,'negative_cases':len(negatives),'pass':True}


if __name__=='__main__':print(json.dumps(checks()))
