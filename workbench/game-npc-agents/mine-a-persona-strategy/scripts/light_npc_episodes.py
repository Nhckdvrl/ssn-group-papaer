#!/usr/bin/env python3
"""E14 own authored LIGHT goal, original human script, native events/views.

Local LLM replaces the archived bot; no original learned Soul or DM is loaded.
Both private goals come from independently authored quests on the exact same
graph. Physics, probability, parsing, canonical action menu and views remain
the pinned upstream implementations. This is a task binding, not a new world.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import tarfile
import time
from types import SimpleNamespace

from light_native_gate import EventHost, load_event_modules, parse_event
from native_actioncastle import dump

CACHE = Path("/home/xiang/.cache/game-npc-research")


class ViewerHost(EventHost):
    def __init__(self, graph):
        super().__init__(graph)
        from light.world.views import WorldViewer
        self.view = WorldViewer(self)
        self.purgatory = SimpleNamespace(node_id_to_soul={})

    # Read-only legacy accessors required by the original WorldViewer. Same
    # delegations as World; no physical rules or learned agent callbacks here.
    def get_prop(self, node_id, prop, default=None):
        node = self.oo_graph.get_node(node_id)
        return "ErrorNodeNotFound" if node is None else node.get_prop(prop, default)

    def has_prop(self, node_id, prop):
        return self.oo_graph.get_node(node_id).has_prop(prop)

    def node_contains(self, node_id):
        return [x.node_id for x in self.oo_graph.get_node(node_id).get_contents()]

    def node_to_desc(self, node_id, from_id=False, use_the=False, drop_prefix=False):
        return self.view.get_node_desc_id(node_id, from_id, use_the, drop_prefix)

    def node_to_desc_raw(self, node_id, from_id=False):
        from light.graph.elements.graph_nodes import GraphRoom
        node = self.oo_graph.get_node(node_id)
        if from_id and isinstance(node, GraphRoom) and isinstance(self.oo_graph.get_node(from_id), GraphRoom):
            path = self.view.path_to_desc_id(node_id, from_id)
            if path is not False:
                return path
        return node.name

    def display_node(self, node_id):
        return self.node_to_desc(node_id)

    def broadcast_to_all_agents(self, event):
        self.broadcast_to_agents(event, list(self.oo_graph.agents.values()))


def load_cases(limit=12):
    joins = json.loads((CACHE/"light_npc_human_join.json").read_text())
    groups = json.loads((CACHE/"light_multiactor_source_audit.json").read_text())["multiactor_graphs"]
    group_index = {x["file"]:i for i,g in enumerate(groups) for x in g}
    demos = json.loads((CACHE/"light_quests_human_demos.json").read_text())
    selected, seen = [], set()
    for row in joins:
        group = group_index[row["quest_file"]]
        if group in seen:
            continue
        seen.add(group)
        npc = min(row["npc_goals"], key=lambda x:int(x["file"].split(".")[0]))
        selected.append({**row, "npc_quest_file":npc["file"], "demo":demos[row["demo_index"]]})
        if len(selected)==limit:
            break
    required = {r[k] for r in selected for k in ["quest_file","npc_quest_file"]}
    data = {}
    with tarfile.open(CACHE/"quest_stems.tar.gz", "r|gz") as archive:
        for member in archive:
            filename = member.name.split("/")[-1]
            if filename in required:
                data[filename] = json.load(archive.extractfile(member))["data"]
    for row in selected:
        row["human_quest"], row["npc_quest"] = data[row["quest_file"]], data[row["npc_quest_file"]]
        assert row["human_quest"]["graph"] == row["npc_quest"]["graph"]
    return selected


def actor_for(graph, name):
    key = name.lower().removeprefix("the ")
    matches = [x for x in graph.agents.values() if x.name.lower().removeprefix("the ")==key
               or x.get_prefix_view().lower().removeprefix("the ")==key]
    assert len(matches)==1, (name,[x.name for x in matches])
    return matches[0]


def material_state(graph):
    result = {}
    for node_id,node in graph.all_nodes.items():
        parent = node.get_container()
        row = {"name":node.name,"container":parent.node_id if parent is not None else None}
        for prop in ["health","dead","equipped","food","drink","size"]:
            if node.has_prop(prop):
                row[prop]=node.get_prop(prop)
        if node.agent:
            row["following"] = node.get_following().node_id if node.get_following() else None
            row["blocking"] = node.get_blocking().node_id if node.get_blocking() else None
        result[node_id]=row
    return result


def legal_commands(graph, actor):
    from light.graph.events.all_events_list import ALL_EVENTS_LIST
    return sorted(set(e.to_canonical_form() for cls in ALL_EVENTS_LIST
                      for e in cls.get_valid_actions(graph,actor)))


def execute(host, actor, command, events, error_type):
    before = material_state(host.oo_graph)
    start = len(host.messages)
    event = parse_event(host.oo_graph,actor,command,events,error_type)
    row = {"actor":actor.node_id,"command":command,"legal":not isinstance(event,error_type),
           "before":before, "event_type":type(event).__name__}
    if row["legal"]:
        event.execute(host)
        row.update(executed=event.executed, stochastic_failure=getattr(event,"failed",False))
    else:
        row["error"] = event.view_as(actor)
    row.update(after=material_state(host.oo_graph),messages=host.messages[start:])
    row["material_changed"] = row["before"]!=row["after"]
    return row


def observation(host, actor, events, error_type):
    texts=[]
    for command in ["look","inventory"]:
        row = execute(host,actor,command,events,error_type)
        assert row["legal"] and row["executed"]
        texts.extend(m["text"] for m in row["messages"] if m["viewer"]==actor.node_id)
    return "\n".join(texts)


def system_message(quest):
    return ("You are a non-player character in the LIGHT fantasy game. Act for your own authored "
            "motivations while interacting with the other character. Dialogue is a legitimate choice.\n"
            f"Your character: {quest['character']}\nPersona: {quest['persona']}\n"
            + "\n".join(f"{key}: {quest[key]}" for key in
                ["short_motivation","mid_motivation","long_motivation","goal"]))


def choose(client, messages, menu, seed, allow_speech=True):
    schema = {"type":"object","properties":{
        "action":{"type":"string","enum":menu+(["say"] if allow_speech else [])},
        "utterance":{"type":"string","description":"Speech text if action is say; otherwise empty"},
        "reasoning":{"type":"string","description":"One brief reason based on own goals and visible facts"}},
        "required":["action","utterance","reasoning"],"additionalProperties":False}
    client.seed = seed-len(client.calls)  # probes never perturb the action RNG
    response = client.native_tool(messages,{"name":"choose_action","parameters":schema})
    return response


def chosen_command(choice):
    if choice["action"]=="say":
        return "say "+choice["utterance"]
    # LIGHT exposes a speech template alongside concrete physical commands.
    # Its payload must be rendered, never executed as literal <SOMETHING>.
    return choice["action"].replace("<SOMETHING>",choice["utterance"])


def run_case(case, seed, out, modules, client=None):
    OOGraph,events,ErrorEvent = modules
    graph = OOGraph.from_json(case["npc_quest"]["graph"])
    npc = actor_for(graph,case["npc_quest"]["character"])
    human = actor_for(graph,case["demo"]["human_persona"]["name"])
    host = ViewerHost(graph)
    random.seed(seed)
    private_history, turns = [], []
    goal_executed = False
    header = system_message(case["npc_quest"])
    if client:
        client.seed = seed+50_000-len(client.calls)
        expression = client.chat([{"role":"system","content":header},{"role":"user",
            "content":"Introduce yourself in two sentences, describing your values and motivations."}],
            max_tokens=128,kind="expression_shadow")
    else:
        expression = None
    for step,event_data in enumerate(x for x in case["demo"]["dialogue"] if x["id"]=="human"):
        if step>=8 or npc.get_prop("dead") or human.get_prop("dead"):
            break
        command = "say "+event_data["text"] if event_data["type"]=="speech" else event_data["text"]
        human_action=execute(host,human,command,events,ErrorEvent)
        obs = observation(host,npc,events,ErrorEvent)
        heard = [m["text"] for m in human_action["messages"] if m["viewer"]==npc.node_id]
        menu = legal_commands(graph,npc)
        # Same actor-scoped native observation/menu for the two independent calls.
        context=obs+"\nAuthored goal event previously legally executed (check feedback for outcome): "+str(goal_executed)
        context+="\nRecent visible interaction:\n"+"\n".join((private_history+heard)[-12:])
        context+="\nLegal commands:\n"+"\n".join(menu)
        messages=[{"role":"system","content":header},{"role":"user","content":context}]
        if client:
            intention=choose(client,[messages[0],{"role":"user","content":context+
                "\nIn an independent hypothetical check, which next action do you currently intend?"}],
                menu,seed+step*100+5)
            choice=choose(client,messages,menu,seed+step*100+17)
            if choice is None:
                raise RuntimeError("Action JSON truncated or invalid; no scripted fallback")
            command = chosen_command(choice)
        else:
            intention,choice=None,None
            command="wait"
        # Pure parse of the authored event before action. Match class/targets,
        # not presentation aliases; keep literal goal readout separately below.
        expected = parse_event(graph,npc,case["npc_quest"]["goal"],events,ErrorEvent)
        chosen_event = parse_event(graph,npc,command,events,ErrorEvent)
        same_event = (not isinstance(expected,ErrorEvent) and type(expected)==type(chosen_event)
            and [x.node_id for x in expected.target_nodes]==[x.node_id for x in chosen_event.target_nodes])
        npc_action=execute(host,npc,command,events,ErrorEvent)
        if same_event and npc_action.get("executed") and not npc_action.get("stochastic_failure"):
            goal_executed=True
        private_history.extend(heard+["Your chosen action: "+command])
        private_history.extend(m["text"] for m in npc_action["messages"] if m["viewer"]==npc.node_id)
        turns.append({"step":step,"human_source":event_data,"human":human_action,
            "observation":context,"menu":menu,"intention":intention,"choice":choice,"npc":npc_action,
            "native_goal_event_match":same_event,"goal_executed":goal_executed})
    summary={"demo_index":case["demo_index"],"human_quest_file":case["quest_file"],
        "npc_quest_file":case["npc_quest_file"],"seed":seed,"npc_name":npc.name,
        "human_goal":case["human_quest"]["goal"],"npc_goal":case["npc_quest"]["goal"],
        "turns":len(turns),"npc_legal":sum(r["npc"]["legal"] for r in turns),
        "npc_material":sum(r["npc"]["material_changed"] for r in turns),
        "human_legal":sum(r["human"]["legal"] for r in turns),
        "npc_exact_goal_actions":sum(r["npc"]["command"].lower()==case["npc_quest"]["goal"].lower() for r in turns),
        "native_goal_event_executed":goal_executed,
        "intention_action_agreement":sum(r["intention"] is not None and r["choice"] is not None
            and r["intention"]["action"]==r["choice"]["action"] for r in turns),
        "expression_shadow":expression,"final_state":material_state(graph)}
    dump(out/"episode.json",turns)
    dump(out/"summary.json",summary)
    return summary


def cpu_qualification(cases, modules, out):
    OOGraph,events,ErrorEvent=modules
    checks=[]
    for speech_action in ["say",'tell boar "<SOMETHING>"','whisper boar "<SOMETHING>"']:
        assert "<SOMETHING>" not in chosen_command({"action":speech_action,"utterance":"I have the coal."})
    assert chosen_command({"action":"give coal to boar","utterance":""})=="give coal to boar"
    for case in cases:
        graph=OOGraph.from_json(case["npc_quest"]["graph"])
        npc=actor_for(graph,case["npc_quest"]["character"])
        host=ViewerHost(graph)
        before=material_state(graph)
        bad=execute(host,npc,"get definitely_missing_item",events,ErrorEvent)
        assert not bad["legal"] and material_state(graph)==before
        obs=observation(host,npc,events,ErrorEvent)
        menu=legal_commands(graph,npc)
        parse_errors=[]
        for command in menu:
            candidate=parse_event(graph,npc,command,events,ErrorEvent)
            if isinstance(candidate,ErrorEvent):
                parse_errors.append({"command":command,"error":candidate.view_as(npc)})
        # Use a fresh graph because the positive action changes ownership/etc.
        goal=execute(host,npc,case["npc_quest"]["goal"],events,ErrorEvent)
        checks.append({"demo_index":case["demo_index"],"authored_goal":case["npc_quest"]["goal"],
            "invalid_rejected_without_change":True,"native_observation":obs,"menu_count":len(menu),
            "canonical_menu_parse_errors":parse_errors,"goal":goal})
    dump(out/"qualification.json",checks)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=["cpu","model"],required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--model",type=Path)
    ap.add_argument("--limit",type=int,default=12)
    ap.add_argument("--seeds",nargs="+",type=int,default=[901,902,903])
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    modules=load_event_modules(CACHE/"sources/LIGHT")
    cases=load_cases(args.limit)
    manifest={"source_sha":"71a06cae8573048b1af41507ac52fe33b650fab3",
        "scope":"local NPC task binding with authored counterpart goals; no original RL/Soul/scorer",
        "harness_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "model":str(args.model),"seeds":args.seeds,"cloud_calls":0,
        "cases":[{k:r[k] for k in ["demo_index","quest_file","npc_quest_file"]} for r in cases]}
    dump(args.out/"manifest.json",manifest)
    dump(args.out/"source_cases.json",cases)
    client=None
    if args.mode=="cpu":
        cpu_qualification(cases,modules,args.out)
    if args.mode=="model":
        from strong_native_baseline import ModelClient
        os.environ.update(HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",HF_DATASETS_OFFLINE="1")
        client=ModelClient(args.model,901,args.out/"unused.jsonl")
    start=time.monotonic()
    summaries=[]
    for seed in args.seeds:
        for case in cases:
            folder=args.out/f"demo{case['demo_index']}_s{seed}"
            folder.mkdir()
            if client:
                client.calls,client.trace_file=[],folder/"model_calls.jsonl"
            row=run_case(case,seed,folder,modules,client)
            if client:
                row.update(model_calls=len(client.calls),prompt_tokens=sum(x["prompt_tokens"] for x in client.calls),
                    completion_tokens=sum(x["completion_tokens"] for x in client.calls))
            summaries.append(row)
            dump(args.out/"summary.json",summaries)
            print(json.dumps({k:v for k,v in row.items() if k not in ["final_state","expression_shadow"]}),flush=True)
    dump(args.out/"runtime.json",{"wall_seconds":time.monotonic()-start})


if __name__=="__main__":
    main()
