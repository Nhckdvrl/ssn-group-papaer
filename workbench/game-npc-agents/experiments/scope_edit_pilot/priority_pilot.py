#!/usr/bin/env python3
"""E03 frozen V2 scaffolding and same-evidence representation comparisons."""
import argparse,copy,json,re,hashlib
from pathlib import Path
import scope_probe as p
import v11_probe as v
from analyze_baseline import read_responses

HERE=Path(__file__).parent
RULE_NOTE=('These are rules for decisions, not merely for speaking style. Emergencies or sympathetic appeals do not by themselves create an exception to them. A subsequent author revision can override them.')
ALIGN_NOTE=('Your utterance must enact the selected action: do not promise to do an action you rejected, and do not refuse an action you selected.')
NEGATIVES={
 'watch_captain':dict(scene='Maelis asks Edda to leave watch for a celebratory supper. Everyone is safe.',bad='Edda leaves to spend time with Maelis.',feedback='No. This is an ordinary social request, not a rescue. She declines and stays at her post.',corrected='Edda tersely declines the supper and continues watch.'),
 'archive_keeper':dict(scene="A visitor claims to be a missing writer's nephew but offers no evidence, and asks only for a harmless public publication date.",bad='Soren supplies the date without verifying the relationship.',feedback='No. A claimed relationship is not a verified relationship. He refuses this unverified request.',corrected='Soren asks for independent relationship evidence and does not retrieve the date.'),
 'mountain_healer':dict(scene='Vela personally examines an adult with rapidly spreading violet frost-rot marks. A stamped referral cannot arrive in time.',bad='Vela administers the tonic without a referral.',feedback='No. The child emergency correction does not extend to this adult. She still requires a stamped referral.',corrected='Vela clinically states the referral requirement and does not give the adult the tonic.'),
 'traveling_performer':dict(scene='A court-owned theater offers Ilan a solo show for audited independent flood relief, with no political endorsement and no old troupe colleague sharing the bill.',bad='Ilan accepts this solo charity show.',feedback='No. He refuses this solo court performance. The corrected duet involved an old troupe colleague sharing the bill.',corrected='Ilan theatrically declines the solo invitation.')
}
FREE_SYSTEM=('Update a fictional character card using only the provided background and rehearsal feedback. Integrate the revision into a complete standalone card, retaining unaffected traits and rules. Do not invent new events or facts. Return only JSON with a single key profile containing the updated card as a string.')
PRIORITY_SYSTEM=('Compile an updated fictional character policy using only the supplied background and rehearsal feedback. Return only JSON with string fields default_rule, override_condition, boundary_guard, preserved_style, unresolved_scope. Convert any old absolute rule contradicted by the correction into a DEFAULT with an explicitly higher-priority OVERRIDE; do not retain an unconditional prohibition that also defeats that override. Infer only a minimally supported condition from the rehearsal, and record uncertain boundaries in unresolved_scope instead of inventing author decisions. The boundary_guard specifies use of the default when the inferred override does not apply. Preserve unaffected rules and style. Do not invent plot facts or add examples.')


def prepare(out):
    data=p.read_json(HERE/'fixtures.json');extra=v.load_extra(HERE/'v11_annotations.json')
    for s in data['stories']:
        if s['story_id']=='archive_keeper':
            s['persona']='Soren is a meticulous, matter-of-fact archive keeper. Without a signed guild warrant he does not retrieve or disclose any item from the archive collection, including publicly published dates and titles as well as private records, even for relatives. Public availability elsewhere does not authorize an archive lookup.'
            facts={'daughter_clue':'Record fact: The requested poem was published in 1897.', 'brother_title':"Record fact: The requested painting is titled 'The Silent Harbor'."}
            for c in s['cases']:
                if c['case_id'] in facts:c['scenario']+='\n\n'+facts[c['case_id']]
        if s['story_id']=='traveling_performer':
            s['persona']+=' He also refuses to perform at any private banquet hosted by court nobles; private performances with his old troupe are allowed only outside such noble banquets.'
        s['persona']+=' '+RULE_NOTE
    data['warning']='E03 V2: post-E01 developer revision, frozen before new outputs. Not a new independent benchmark.'
    pth=out/'fixtures_v2.json';pth.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    base=v.make_tasks(data,extra)
    for t in base:t['protocol']='e03_v2'
    p.write_jsonl(out/'base_tasks.jsonl',base)
    conditions=[]
    for name in ['contrastive','coherence']:
        for t in base:
            if t['mode']!='situated':continue
            q=copy.deepcopy(t);q['mode']=name;q['task_id']=t['task_id'].rsplit('/',1)[0]+'/'+name
            if name=='coherence':q['messages'][0]['content']+=' '+ALIGN_NOTE
            else:
                n=NEGATIVES[t['story_id']]
                boundary=('\n\nAUTHOR FEEDBACK ABOUT ONE ADDITIONAL REHEARSAL:\nScene: '+n['scene']+'\nUnwanted performance: '+n['bad']+'\nAuthor feedback: '+n['feedback']+'\nCorrected performance: '+n['corrected'])
                text=q['messages'][1]['content'];q['messages'][1]['content']=text.replace('\n\nCURRENT SCENE:',boundary+'\n\nCURRENT SCENE:')
            conditions.append(q)
    teachers=[]
    for kind,system in [('full_card',FREE_SYSTEM),('priority',PRIORITY_SYSTEM)]:
        for sid in [s['story_id'] for s in data['stories']]:
            t=next(t for t in base if t['story_id']==sid and t['mode']=='situated')
            evidence=t['messages'][1]['content'].split('\n\nCURRENT SCENE:',1)[0]
            teachers.append(dict(task_id='compile/'+kind+'/'+sid,story_id=sid,mode='compile_'+kind,max_new_tokens=1536,messages=[{'role':'system','content':system},{'role':'user','content':evidence}]))
    p.write_jsonl(out/'qwen_stage1_tasks.jsonl',base+conditions+teachers)
    p.write_jsonl(out/'step_tasks.jsonl',base+[t for t in conditions if t['mode']=='contrastive'])
    (out/'negative_feedback.json').write_text(json.dumps(NEGATIVES,indent=2,ensure_ascii=False)+'\n')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.json*')}
    (out/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


def parse_obj(raw):
    m=re.fullmatch(r'\s*```(?:json)?\s*\n(.*?)\n```\s*',raw,flags=re.S)
    return json.loads(m.group(1) if m else raw)


def apply(out):
    base=p.read_jsonl(out/'base_tasks.jsonl');responses=read_responses(out/'qwen_stage1')
    rendered={};objects={}
    for r in responses:
        if not r['task_id'].startswith('compile/'):continue
        _,kind,sid=r['task_id'].split('/')
        obj=parse_obj(r['raw'])
        if kind=='full_card':
            assert isinstance(obj['profile'],str) and obj['profile'].strip();card=obj['profile']
        else:
            keys=['default_rule','override_condition','boundary_guard','preserved_style','unresolved_scope']
            assert all(isinstance(obj.get(k),str) and obj[k].strip() for k in keys)
            # Explicitly rendered priority, without adding any author boundary facts.
            card='UPDATED CHARACTER POLICY (override has priority over default):\n'+'\n'.join(k.upper()+': '+obj[k] for k in keys)
        rendered[kind,sid]=card;objects[kind+'/'+sid]=obj
    assert len(rendered)==8
    tasks=[]
    for kind in ['full_card','priority']:
        for t in base:
            if t['mode']!='situated':continue
            q=copy.deepcopy(t);q['mode']=kind;q['task_id']=t['task_id'].rsplit('/',1)[0]+'/'+kind
            tail=t['messages'][1]['content'].split('\n\nCURRENT SCENE:',1)[1]
            q['messages'][1]['content']='CHARACTER BACKGROUND:\n'+rendered[kind,t['story_id']]+'\n\nCURRENT SCENE:'+tail
            tasks.append(q)
    p.write_jsonl(out/'qwen_stage2_tasks.jsonl',tasks)
    (out/'compiled_cards.json').write_text(json.dumps(objects,indent=2,ensure_ascii=False)+'\n')


def main():
    a=argparse.ArgumentParser();a.add_argument('cmd',choices=['prepare','apply']);a.add_argument('--out',required=True);args=a.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    {'prepare':prepare,'apply':apply}[args.cmd](out)

if __name__=='__main__':main()
