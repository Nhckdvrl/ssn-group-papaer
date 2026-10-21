#!/usr/bin/env python3
"""Fixed same-information controls, registered after E01 and before E02 execution."""
import argparse,copy,json,re
from pathlib import Path
import scope_probe as p
from analyze_baseline import normalized_reply, analyze, read_responses

ONE_LINE = ('Treat the rehearsal correction as an exception to the existing character: '
            'generalize only where the relevant circumstances are supported, and retain '
            'the original behavior in unrelated situations.')


def prepare(e01,out):
    tasks=p.read_jsonl(e01/'tasks.jsonl');new=[]
    situated=[t for t in tasks if t['mode']=='situated']
    for kind in ['no_persona','one_line']:
        for t in situated:
            q=copy.deepcopy(t);q['source_task_id']=t['task_id'];q['control']=kind
            q['task_id']=kind+'/'+t['task_id']
            text=q['messages'][1]['content']
            if kind=='no_persona':
                q['messages'][1]['content']='AUTHOR FEEDBACK'+text.split('\n\nAUTHOR FEEDBACK',1)[1]
            else:q['messages'][0]['content']+=' '+ONE_LINE
            new.append(q)
    for sid in sorted({t['story_id'] for t in situated}):
        source=next(t for t in situated if t['story_id']==sid)
        evidence=source['messages'][1]['content'].split('\n\nCURRENT SCENE:',1)[0]
        new.append(dict(task_id='rewrite/'+sid,story_id=sid,control='rewrite',max_new_tokens=1024,messages=[
            {'role':'system','content':'Update a fictional character card using only the provided background and rehearsal feedback. Integrate the revision into a complete standalone card, retaining unaffected traits and rules. Do not invent new events or facts. Return only JSON with a single key profile containing the updated card as a string.'},
            {'role':'user','content':evidence}]))
    p.write_jsonl(out/'stage1_tasks.jsonl',new)


def apply_rewrites(e01,out):
    tasks=p.read_jsonl(e01/'tasks.jsonl');rows=read_responses(out/'stage1')
    cards={}
    for r in rows:
        if not r['task_id'].startswith('rewrite/'):continue
        raw=r['raw'];m=re.fullmatch(r'\s*```(?:json)?\s*\n(.*?)\n```\s*',raw,flags=re.S)
        obj=json.loads(m.group(1) if m else raw)
        assert isinstance(obj['profile'],str) and obj['profile'].strip()
        cards[r['task_id'].split('/',1)[1]]=obj['profile']
    assert len(cards)==4
    new=[]
    for t in tasks:
        if t['mode']!='situated':continue
        q=copy.deepcopy(t);q['source_task_id']=t['task_id'];q['control']='profile_rewrite'
        q['task_id']='profile_rewrite/'+t['task_id']
        scene=q['messages'][1]['content'].split('\n\nCURRENT SCENE:',1)[1]
        q['messages'][1]['content']='CHARACTER BACKGROUND:\n'+cards[t['story_id']]+'\n\nCURRENT SCENE:'+scene
        new.append(q)
    p.write_jsonl(out/'stage2_tasks.jsonl',new)
    (out/'rewritten_cards.json').write_text(json.dumps(cards,indent=2,ensure_ascii=False)+'\n')


def summarize(e01,out):
    tasks=p.read_jsonl(e01/'tasks.jsonl')
    baseline=read_responses(e01/'qwen3_8b')
    responses=read_responses(out/'stage1')+read_responses(out/'stage2')
    result={'new_model_requests':len(responses),'reused_baseline_requests':60,'controls':{}}
    base,_=analyze(tasks,baseline)
    result['baseline_situated']=base['modes']['situated']
    for kind in ['no_persona','one_line','profile_rewrite']:
        rows=[dict(r,task_id=r['task_id'].split('/',1)[1]) for r in responses if r['task_id'].startswith(kind+'/')]
        assert len(rows)==20
        combined=[r for r in baseline if not r['task_id'].endswith('/situated')]+rows
        report,normalized=analyze(tasks,combined)
        control=report['modes']['situated']
        before={r['task_id']:normalized_reply(r['raw'])[0] for r in baseline}
        control['changes_from_baseline']=[dict(task_id=r['task_id'],before=before[r['task_id']],after=r['action_id'],utterance=r['utterance']) for r in normalized if r['task_id'].endswith('/situated') and r['action_id']!=before[r['task_id']]]
        control['normalization_note']=report['normalization']
        result['controls'][kind]=control
    result['usage']={k:sum(r.get('usage',{}).get(k,0) for r in responses) for k in ['prompt_tokens','completion_tokens']}
    (out/'analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))


def main():
    a=argparse.ArgumentParser();a.add_argument('cmd',choices=['prepare','apply','summarize']);a.add_argument('--e01',required=True);a.add_argument('--out',required=True)
    args=a.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    {'prepare':prepare,'apply':apply_rewrites,'summarize':summarize}[args.cmd](Path(args.e01),out)

if __name__=='__main__':main()
