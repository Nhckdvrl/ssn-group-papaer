"""Pure transformations for D-E10; never insert a reference into a learned path."""
import copy
import json
import re


def sections(text):
    matches=list(re.finditer(r'^## ([^\n]+)\n',text,re.M)); result={}
    for i,m in enumerate(matches):
        title=m[1]
        if title in result:raise ValueError('Duplicate section: '+title)
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        result[title]=(m.end(),end,text[m.end():end].strip())
    return result


def replace_sections(text, values):
    info=sections(text)
    for title in values:
        if title not in info:raise ValueError('Missing section: '+title)
    for title in sorted(values,key=lambda t:info[t][0],reverse=True):
        start,end,_=info[title];text=text[:start]+values[title].strip()+'\n\n'+text[end:]
    return text.rstrip()


def messages(conversations):
    roles={'system':'system','human':'user','assistant':'assistant'}
    return [{'role':roles[c['from']],'content':c['value']} for c in conversations]


def json_object(text):
    text=text.strip()
    if text.startswith('```'):
        text=re.sub(r'^```(?:json)?\s*','',text)
        text=re.sub(r'\s*```$','',text)
    value=json.loads(text)
    if not isinstance(value,dict):raise ValueError('Expected an object')
    return value


def decode_state(text, before):
    try:
        v=json_object(text)
        if type(v.get('profile_updated')) is not bool:return None
        for key in ['updated_profile','hidden_tracker','short_description']:
            if key not in v:return None
        if v['profile_updated'] and not (isinstance(v['updated_profile'],str) and v['updated_profile'].strip()):return None
        if not isinstance(v['short_description'],str):return None
        return dict(profile=v['updated_profile'] if v['profile_updated'] else before['profile'],
            hidden_tracker=v['hidden_tracker'],short_description=v['short_description'],
            profile_updated=v['profile_updated'])
    except (ValueError,TypeError):return None


def decode_motivation(text):
    try:
        v=json_object(text).get('motivation')
        return v if isinstance(v,str) and v.strip() else None
    except (ValueError,TypeError):return None


def tracker_text(value):
    if value is None or value=='':return '(Empty)'
    return str(value)


def motivation_messages(episode,state,full_evidence=False):
    m=copy.deepcopy(episode['motivation_input'])
    m[1]['content']=replace_sections(m[1]['content'],{
        'Current Profile':state['profile'],
        'Hidden Tracker':tracker_text(state['hidden_tracker']),
        'Current Short Description':state.get('short_description','') or '(No current description supplied)'})
    if full_evidence:
        m[1]['content']+='\n\n## Completed prior experience\nThe following snapshot and scene happened BEFORE the new scene. Use it to interpret the character now.\n'+episode['update_input'][1]['content']
    return m


def actor_messages(episode,query,state,motivation,full_evidence=False):
    m=copy.deepcopy(query['messages']);s=m[0]['content']
    marker='## Your Character State\n';start=s.index(marker)+len(marker)
    skip=len(s[start:])-len(s[start:].lstrip());start+=skip
    old,end=json.JSONDecoder().raw_decode(s[start:])
    if list(old)!=[episode['role']]:raise ValueError('Actor subject changed')
    replacement=copy.deepcopy(old)
    replacement[episode['role']].update(profile=state['profile'],hidden_tracker=state['hidden_tracker'],motivation=motivation or '')
    m[0]['content']=s[:start]+json.dumps(replacement,ensure_ascii=False,indent=2)+s[start+end:]
    if full_evidence:
        m[0]['content']+='\n\n## Completed prior experience\nThis snapshot and experience preceded the CURRENT scene; use them to interpret the character now.\n'+episode['update_input'][1]['content']
    return m
