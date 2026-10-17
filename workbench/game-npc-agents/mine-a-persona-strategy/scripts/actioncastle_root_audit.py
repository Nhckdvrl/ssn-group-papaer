#!/usr/bin/env python3
"""Post-hoc attribution audit: distinguish parser recursion from model decisions.

Raw parser records are retained. Reconstruct each model-chosen root command
using the pinned author's decision/tool parsers, then match its recorded route.
No behavioral primary score or world consequence is redefined.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--source",type=Path,default=Path("/home/xiang/.cache/game-npc-research/sources/agent-sandbox"))
    args=ap.parse_args()
    sys.path.insert(0,str(args.source))
    from text_adventure_games.npc import _parse_decision,command_from_tool_call
    from native_actioncastle import fresh_game
    parser=fresh_game().parser
    summaries=[]
    for folder in sorted(args.run.iterdir()):
        summary_file=folder/"summary.json"
        if not summary_file.exists():
            continue
        summary=json.loads(summary_file.read_text())
        calls=[json.loads(s) for s in (folder/"model_calls.jsonl").read_text().splitlines()]
        records=[json.loads(s) for s in (folder/f"{summary['name']}_actions.jsonl").read_text().splitlines()]
        cursor,matched,missing,attempts=0,[],[],Counter()
        for call in calls:
            system=call["messages"][0]["content"]
            actor=call.get("context",{}).get("actor")
            if actor is None:
                identity=re.search(r"Persona: I am the (troll|guard|ghost)\b",system)
                if identity:
                    actor=identity.group(1)
            parsed=call.get("parsed")
            if call["kind"]=="native_per_action_tools" and parsed is not None:
                command=command_from_tool_call(parsed['name'],parsed['arguments'],parser)
            elif call["kind"]=="native_choose_action" and parsed is not None:
                command=f"{parsed.get('action','')} {parsed.get('arguments','')}".strip()
            elif call["kind"]=="action":
                _,command,_=_parse_decision(call['response'])
            else:
                command=None
            if not command:
                missing.append({"call_id":call['id'],"reason":"no parseable chosen root command"})
                continue
            indices=[i for i in range(cursor,len(records)) if records[i]['command']==command
                     and records[i]['actor']==actor]
            if not indices:
                missing.append({"call_id":call['id'],"actor":actor,"command":command})
                continue
            index=indices[0]
            root=records[index]
            key=(root['actor'],root['turn'])
            attempt=call.get('context',{}).get('attempt',attempts[key])
            attempts[key]+=1
            matched.append({"call_id":call['id'],"record_index":index,"actor":actor,
                "turn":root['turn'],"attempt":attempt,"command":command,"legal":root['success'],
                "material":bool(root['delta']),"failure_reason":root['failure_reason']})
            cursor=index+1
        summaries.append({"episode":folder.name,"condition":summary['condition'],"seed":summary['seed'],
            "script":summary['name'],"all_npc_parser_records":sum(x['actor']!='The player' for x in records),
            "model_calls":len(calls),"root_matches":len(matched),"missing":missing,
            "root_legal":sum(x['legal'] for x in matched),"root_material":sum(x['material'] for x in matched),
            "first_total":sum(x['attempt']==0 for x in matched),
            "first_legal":sum(x['attempt']==0 and x['legal'] for x in matched),
            "retry_total":sum(x['attempt']>0 for x in matched),
            "retry_legal":sum(x['attempt']>0 and x['legal'] for x in matched),
            "failures":dict(Counter(x['failure_reason'] for x in matched if not x['legal'])),
            "roots":matched})
    args.out.write_text(json.dumps({"analysis":"POST-HOC parser-recursion attribution audit",
        "not_new_primary_behavior_metric":True,"run":str(args.run),"episodes":summaries},ensure_ascii=False,indent=2)+"\n")
    print(json.dumps([{k:v for k,v in x.items() if k not in ['roots','failures']} for x in summaries]),flush=True)


if __name__=="__main__":
    main()
