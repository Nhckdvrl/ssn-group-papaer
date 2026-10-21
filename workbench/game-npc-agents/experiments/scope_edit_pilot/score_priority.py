#!/usr/bin/env python3
"""Offline E03 review packets and audited metrics; compiler calls never become trials."""
import argparse,json,copy
from pathlib import Path
from collections import Counter
import scope_probe as p
from analyze_baseline import read_responses,normalized_reply
from alignment_audit import score,lint


def gather(root,model):
    if model=='qwen':
        tasks=p.read_jsonl(root/'qwen_stage1_tasks.jsonl')+p.read_jsonl(root/'qwen_stage2_tasks.jsonl')
        rows=read_responses(root/'qwen_stage1')+read_responses(root/'qwen_stage2')
    else:
        tasks=p.read_jsonl(root/'step_tasks.jsonl');rows=read_responses(root/'step5')
    tasks=[t for t in tasks if not t['task_id'].startswith('compile/')]
    rows=[r for r in rows if not r['task_id'].startswith('compile/')]
    assert len({r['task_id'] for r in rows})==len(rows),'Duplicate responses disqualify run'
    assert {r['task_id'] for r in rows}=={t['task_id'] for t in tasks}
    index={r['task_id']:r for r in rows}
    return tasks,[index[t['task_id']] for t in tasks]


def packet(root,model):
    tasks,rows=gather(root,model);fixture=p.read_json(root/'fixtures_v2.json')
    actions={(s['story_id'],c['case_id']):c['actions'] for s in fixture['stories'] for c in s['cases']}
    packet=[]
    for i,(t,r) in enumerate(zip(tasks,rows)):
        a,u=normalized_reply(r.get('raw',''))
        packet.append(dict(index=i,task_id=t['task_id'],action=a,action_meaning=actions[t['story_id'],t['case_id']].get(a),utterance=u,flags=lint(u),raw=r.get('raw','')))
    p.write_jsonl(root/(model+'_review_packet.jsonl'),packet)
    print('Review packet',model,len(packet))


def evaluate(root,model):
    tasks,rows=gather(root,model);ann=p.read_jsonl(root/(model+'_annotations.jsonl'))
    result=score(tasks,rows,ann)
    result['strict_json_valid']=sum(p.parse_reply(r.get('raw',''))[0] in t['allowed_actions'] for t,r in zip(tasks,rows))
    result['finish_reasons']=dict(Counter(r.get('finish_reason') for r in rows))
    result['requested_decisions']=len(tasks)
    result['usage_decisions']={k:sum(r.get('usage',{}).get(k,0) for r in rows) for k in ['prompt_tokens','completion_tokens']}
    (root/(model+'_analysis.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# '+model+'：全部决策与言行审阅','', '逐条同执行agent描述性审阅；非真人盲评。unclear不自动算通过。','', '| task | action | oracle | alignment | utterance |','|---|---|---|---|---|']
    for d in result['details']:
        cells=[d['task_id'],d['action'],str(d['oracle_match']),d['alignment'],d['utterance']]
        lines.append('| '+' | '.join(str(x).replace('|','\\|').replace('\n','<br>') for x in cells)+' |')
    (root/(model+'_CASEBOOK.md')).write_text('\n'.join(lines)+'\n')
    for mode,s in result['summary'].items():
        print(model,mode,'n',s['n'],'action',s['action_matches'],'joint',s['effective_lower'],s['effective_upper'],'buckets',s['by_scope'],'labels',s['alignment'])


def historical(root):
    old=root.parent;tasks=p.read_jsonl(root/'historical_audit_tasks.jsonl');wanted={t['task_id'] for t in tasks};rows=[]
    for run in ['e01/qwen3_8b','e02/stage1','e02/stage2']:
        for r in read_responses(old/run):
            tid=('direct/'+r['task_id']) if run.startswith('e01') else r['task_id']
            if tid in wanted:rows.append(dict(r,task_id=tid))
    report=score(tasks,rows,p.read_jsonl(root/'historical_audit_annotations.jsonl'))
    (root/'historical_audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')


def main():
    a=argparse.ArgumentParser();a.add_argument('cmd',choices=['packet','score','historical']);a.add_argument('--root',required=True);a.add_argument('--model',choices=['qwen','step5']);args=a.parse_args();root=Path(args.root)
    if args.cmd=='historical':historical(root)
    elif args.cmd=='packet':packet(root,args.model)
    else:evaluate(root,args.model)

if __name__=='__main__':main()
