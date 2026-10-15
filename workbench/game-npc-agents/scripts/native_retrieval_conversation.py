#!/usr/bin/env python3
"""E75 POST-HOC descriptive conversation/actual-action readback, no model calls."""
import argparse
from collections import Counter
import json
from pathlib import Path
from native_retrieval_report import metrics


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runs-root',type=Path,required=True)
    ap.add_argument('--data',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();sources={r['case']['case_id']:r for r in map(json.loads,a.data.open())};models={}
    for model in ['gemma','32b']:
        rows={}
        for shard in [0,1]:
            folder=a.runs_root/f'e75_{model}_s{shard}';assert (folder/'runtime.json').exists()
            for r in map(json.loads,(folder/'episodes.jsonl').open()):
                key=r['case_id'],r['seed'],r['persona'],r['condition'];assert key not in rows;rows[key]=r
        cells={}
        for r in rows.values():
            group='source_give' if r['goal_kind']=='give' else 'source_use'
            m=metrics(r);label=next(k for k in ['goal','request','other_source_give','no_decisive_event'] if m[k])
            stance=(r['conversation'] or {}).get('stance','invalid')
            first=r['history'][0] if r['history'] else None
            action=('invalid/' if first and not first['legal'] else '')+(first['event_type'] if first else 'none')
            for g in ['all',group]:
                bucket=cells.setdefault(g+'/'+r['persona']+'/'+r['condition'],Counter())
                bucket.update(episodes=1);bucket['stance/'+stance]+=1;bucket['first_event/'+action]+=1
                bucket['stance_x_outcome/'+stance+'/'+label]+=1
        examples={}
        for wanted in ['A_get_F_not','F_get_A_not','both_get_different_use']:
            for cid,seed in sorted({(r['case_id'],r['seed']) for r in rows.values()}):
                f=rows[cid,seed,'firm','retrieval_baseline'];b=rows[cid,seed,'agreeable','retrieval_baseline']
                fm,bm=metrics(f),metrics(b)
                eligible=(bm['first_retrieve'] and not fm['first_retrieve'] if wanted=='A_get_F_not' else
                          fm['first_retrieve'] and not bm['first_retrieve'] if wanted=='F_get_A_not' else
                          f['goal_kind']!='give' and fm['retrieved'] and bm['retrieved'] and fm['goal'] and bm['request'])
                if not eligible:continue
                c=sources[cid]['case'];examples[wanted]={'case_id':cid,'seed':seed,'goal_kind':c['goal_kind'],
                    'goal_command':c['goal_command'],'request_command':c['request_command'],
                    'author_character':c['quest']['character'],'author_persona':c['quest']['persona'],
                    'author_motivations':{k:c['quest'][k] for k in ['short_motivation','mid_motivation','long_motivation']},
                    'selection':'First lexicographic case_id/seed meeting the stated POST-HOC category.',
                    'trajectories':{p:{'conversation':r['conversation'],
                        'commands':[h['command'] for h in r['history']],
                        'native_success':[bool(h['legal'] and h.get('executed') and not h.get('stochastic_failure')) for h in r['history']],
                        'metrics':metrics(r)} for p,r in [('firm',f),('agreeable',b)]}}
                break
            examples.setdefault(wanted,None)
        models[model]={'cells':cells,'illustrative_cases':examples}
    result={'analysis':'POST-HOC','experiment':'E75','models':models,'new_model_calls':0,
            'scope':['Structured stance is not an unconditional promise or a latent-preference measurement.',
                     'Support arms share exactly the same conversation; descriptive joint counts identify no mediation effect.',
                     'Examples include a reverse-direction case and do not replace all-world statistics.']}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'models':list(models),'new_model_calls':0}))


if __name__=='__main__':main()
