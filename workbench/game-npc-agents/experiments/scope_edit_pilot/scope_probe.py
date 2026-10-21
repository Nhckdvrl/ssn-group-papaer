#!/usr/bin/env python3
"""Small, dependency-free character-edit-scope evaluation harness. Not research evidence."""
from __future__ import annotations
import argparse, json, os, pathlib, time, urllib.request
from collections import defaultdict

def read_json(path):
    with open(path, encoding="utf-8") as f: return json.load(f)

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def write_jsonl(path, rows):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False) + "\n")

def validate(data):
    if data.get("version") != 1 or not data.get("stories"): raise ValueError("expected nonempty fixture version=1")
    stories, cases, counts = set(), set(), defaultdict(int)
    for s in data["stories"]:
        sid = s["story_id"]
        if sid in stories: raise ValueError("duplicate story: "+sid)
        stories.add(sid)
        for k in ("persona","author_edit","name"):
            if not s.get(k): raise ValueError("missing character field "+k)
        within = defaultdict(int)
        for c in s["cases"]:
            key = sid+"/"+c["case_id"]
            if key in cases: raise ValueError("duplicate case "+key)
            cases.add(key)
            scope = c["scope"]
            if scope not in ("change","preserve"): raise ValueError("invalid scope "+key)
            if not c.get("scenario") or not c.get("editor_rationale"): raise ValueError("missing scene/rationale "+key)
            options = set(c["actions"])
            before, after = set(c["expected_before"]), set(c["expected_after"])
            if len(options)<2 or not before or not after or not before<=options or not after<=options: raise ValueError("invalid gold "+key)
            if (scope=="change") == (before==after): raise ValueError("scope/gold mismatch "+key)
            within[scope]+=1; counts[scope]+=1
        if not within["change"] or not within["preserve"]: raise ValueError("each story needs both scopes")
    return {"stories":len(stories),"cases":len(cases),"change":counts["change"],"preserve":counts["preserve"]}

def render(data):
    validate(data)
    sysmsg = ("Act as the original RPG character. Choose exactly one of the AVAILABLE ACTIONS and speak in character. "
              'Return only JSON with {"action_id":"<option>","utterance":"<in-character line>"}. '
              "Do not invent actions or reveal reasoning.")
    out=[]
    for s in data["stories"]:
        for c in s["cases"]:
            choices="\n".join(k+": "+v for k,v in c["actions"].items())
            for when in ("before","after"):
                profile=s["persona"]+("\n\nAUTHOR'S NEW CHARACTER REVISION:\n"+s["author_edit"] if when=="after" else "")
                message=f"Character:\n{profile}\n\nCurrent scene:\n{c['scenario']}\n\nAvailable actions:\n{choices}"
                out.append({"task_id":f"{s['story_id']}/{c['case_id']}/{when}","story_id":s["story_id"],"case_id":c["case_id"],
                  "scope":c["scope"],"condition":when,"expected_actions":c["expected_"+when],
                  "allowed_actions":list(c["actions"]),"messages":[{"role":"system","content":sysmsg},{"role":"user","content":message}]})
    return out

def parse_reply(raw):
    try:
        val=json.loads(raw)
        if isinstance(val,dict) and isinstance(val.get("action_id"),str) and isinstance(val.get("utterance"),str):
            return val["action_id"],val["utterance"]
    except (ValueError,TypeError): pass
    return None,None

def run(tasks,args):
    url=args.endpoint.rstrip("/")
    if not url.endswith("/chat/completions"): url+="/chat/completions"
    answers=[]
    for t in tasks:
        start=time.monotonic()
        payload={"model":args.model,"messages":t["messages"],"temperature":args.temperature,"max_tokens":args.max_tokens}
        req=urllib.request.Request(url,json.dumps(payload).encode("utf-8"),method="POST",
              headers={"Content-Type":"application/json","Authorization":"Bearer "+os.environ.get("OPENAI_API_KEY","EMPTY")})
        try:
            with urllib.request.urlopen(req,timeout=args.timeout) as response: body=json.load(response)
            raw=body["choices"][0]["message"].get("content") or ""
            action,utterance=parse_reply(raw)
            answer={"task_id":t["task_id"],"model":args.model,"raw":raw,"action_id":action,"utterance":utterance,
                    "usage":body.get("usage",{}),"latency_s":round(time.monotonic()-start,3)}
        except Exception as exc:
            answer={"task_id":t["task_id"],"model":args.model,"action_id":None,"utterance":None,
                    "error":type(exc).__name__+": "+str(exc),"latency_s":round(time.monotonic()-start,3)}
        answers.append(answer)
        write_jsonl(args.out,answers)
    return answers

def score(tasks,responses):
    if len({x["task_id"] for x in tasks})!=len(tasks): raise ValueError("duplicate task ids")
    answer={}
    for x in responses:
        if x["task_id"] in answer: raise ValueError("duplicate response id "+x["task_id"])
        answer[x["task_id"]]=x
    if set(answer)-{x["task_id"] for x in tasks}: raise ValueError("unknown response id")
    checked={}
    for t in tasks:
        response=answer.get(t["task_id"],{})
        action=response.get("action_id")
        if action is None and isinstance(response.get("raw"),str): action,_=parse_reply(response["raw"])
        valid=action in t["allowed_actions"]
        checked[t["task_id"]]={"action":action,"valid":valid,"correct":bool(valid and action in t["expected_actions"])}
    pairs=[]
    for t in tasks:
        if t["condition"]!="before": continue
        pre=checked[t["task_id"]]
        afterid=t["task_id"].rsplit("/",1)[0]+"/after"
        if afterid not in checked: raise ValueError("missing after task")
        post=checked[afterid]
        pairs.append({"story_id":t["story_id"],"case_id":t["case_id"],"scope":t["scope"],
                      "pre_correct":pre["correct"],"post_correct":post["correct"],
                      "paired_both_correct":pre["correct"] and post["correct"],
                      "observed_action_changed":pre["valid"] and post["valid"] and pre["action"]!=post["action"]})
    groups={}
    for scope in ("change","preserve"):
        values=[p for p in pairs if p["scope"]==scope]
        groups[scope]={"n_cases":len(values),"pre_correct":sum(p["pre_correct"] for p in values),
              "post_correct":sum(p["post_correct"] for p in values),
              "paired_both_correct":sum(p["paired_both_correct"] for p in values),
              "action_changed":sum(p["observed_action_changed"] for p in values)}
    by_story={s:{"cases":sum(p["story_id"]==s for p in pairs),
                  "paired_both_correct":sum(p["paired_both_correct"] for p in pairs if p["story_id"]==s)}
              for s in sorted({p["story_id"] for p in pairs})}
    return {"disclaimer":"hand-authored smoke-test only; 4 independent stories, NOT 16 independent scenarios or research evidence",
            "stories":len(by_story),"pairs":len(pairs),"valid_responses":sum(x["valid"] for x in checked.values()),
            "required_responses":len(checked),"groups":groups,"by_story":by_story,"details":pairs}

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="cmd",required=True)
    for cmd in ("validate","render"):
        a=sub.add_parser(cmd);a.add_argument("--fixtures",required=True)
        if cmd=="render":a.add_argument("--out",required=True)
    a=sub.add_parser("run")
    for flag in ("tasks","out","endpoint","model"): a.add_argument("--"+flag,required=True)
    a.add_argument("--temperature",type=float,default=0);a.add_argument("--max-tokens",type=int,default=300)
    a.add_argument("--timeout",type=float,default=120)
    a=sub.add_parser("score");a.add_argument("--tasks",required=True);a.add_argument("--responses",required=True);a.add_argument("--out")
    a=p.parse_args()
    if a.cmd=="validate": print(json.dumps(validate(read_json(a.fixtures)),ensure_ascii=False,indent=2))
    elif a.cmd=="render":
        tasks=render(read_json(a.fixtures));write_jsonl(a.out,tasks);print("rendered",len(tasks))
    elif a.cmd=="run": print("ran",len(run(read_jsonl(a.tasks),a)))
    else:
        obj=score(read_jsonl(a.tasks),read_jsonl(a.responses))
        txt=json.dumps(obj,ensure_ascii=False,indent=2)
        if a.out:pathlib.Path(a.out).write_text(txt+"\n",encoding="utf-8")
        else:print(txt)

if __name__=="__main__": main()
