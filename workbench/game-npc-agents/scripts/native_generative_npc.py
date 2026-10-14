#!/usr/bin/env python3
"""E29 local decide adapter for original Penn boil world and native simulation."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/agent-sandbox'))
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seeds',type=int,nargs='+',default=[2901])
    ap.add_argument('--arms',nargs='+',choices=['seeded','control'],default=['seeded'])
    ap.add_argument('--steps',type=int,default=80)
    ap.add_argument('--max-calls',type=int,default=40)
    ap.add_argument('--cognition',choices=['decide','local'],default='decide')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    src_sha=subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip()
    assert src_sha=='d7b872e396df2ef05ff8391de53e0563ca698cf3'
    ga=args.source/'godot-generative-agents'
    sys.path[:0]=[str(args.source),str(ga),str(ga/'backend/penn')]
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',LLM_PROVIDER='mock')
    from backend.run_simulation import simulate
    from backend.penn.penn_world import build_penn_world,WORLD_DATA_BOIL,PENN_ACTION_VERBS
    from backend.penn.experiments.boil_from_memory import _configure,classify_outcome,_RETRIEVAL
    from native_actioncastle import core_state,state_diff
    from native_tool_loop import ToolClient
    from strong_native_baseline import ModelClient
    import numpy as np
    dump=lambda path,value:Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    dump(args.out/'manifest.json',{'source_sha':src_sha,'world':WORLD_DATA_BOIL,
        'world_sha256':hashlib.sha256(Path(WORLD_DATA_BOIL).read_bytes()).hexdigest(),
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'model':str(args.model),'model_revision':args.model.name,'seeds':args.seeds,'arms':args.arms,
        'steps':args.steps,'max_calls':args.max_calls,'cognition':args.cognition,
        'planner':'original LLMPlanner, local' if args.cognition=='local' else 'original MockPlanner',
        'reflector':'original LLMReflector, local' if args.cognition=='local' else None,
        'embedding':None,
        'importance_scoring':'original score_memories, local' if args.cognition=='local' else 'not wired: per-action-only client',
        'decide':'original scoped per-verb tools, local model','source_schedule_commands_forced':False,
        'world_or_recipe_changed':False,'cloud_calls':0})
    start=time.monotonic()
    base=ModelClient(args.model,args.seeds[0],args.out/'unused_model_calls.jsonl')
    class BoundedLocalBrain(ToolClient):
        def call_tools(self,*a,**kw):
            if len(self.base.calls)>=args.max_calls:raise RuntimeError('Local model call budget exhausted')
            return super().call_tools(*a,**kw)
        def chat(self,*a,**kw):
            if len(self.base.calls)>=args.max_calls:raise RuntimeError('Local model call budget exhausted')
            return super().chat(*a,**kw)
    summary=[]
    for seed in args.seeds:
        for arm in args.arms:
            folder=args.out/f'{arm}_s{seed}';folder.mkdir()
            base.seed=seed;base.calls=[];base.trace_file=folder/'model_calls.jsonl'
            random.seed(seed);np.random.seed(seed)
            if args.cognition=='local':
                from local_component_client import LocalComponentClient
                brain=LocalComponentClient(base,args.max_calls,'decide')
                planner_client=LocalComponentClient(base,args.max_calls,'plan')
                reflector_client=LocalComponentClient(base,args.max_calls,'reflect')
            else:
                brain=BoundedLocalBrain(base);planner_client=reflector_client=None
            pw=build_penn_world(world_data=WORLD_DATA_BOIL)
            personas=_configure(pw.personas,seeded=arm=='seeded');name=personas[0]['name']
            captured={};records=[];depth=0;events=[];memories={};plans={};planner_sources={}
            def build_capture(world_map):
                nonlocal depth
                game,chars=pw.build_world_fn(world_map);captured.update(game=game,chars=chars)
                original=game.parser.parse_command
                def parse(command,actor=None,*a,**kw):
                    nonlocal depth
                    current_depth=depth;depth+=1
                    before=core_state(game);before_calls=len(base.calls)
                    try:success=bool(original(command,actor,*a,**kw))
                    finally:depth-=1
                    after=core_state(game)
                    row={'command':command,'actor':getattr(actor,'name',None),'depth':current_depth,
                        'success':success,'material_delta':state_diff(before,after),'model_calls_before':before_calls,
                        'model_calls_after':len(base.calls),'brain_context':copy.deepcopy(brain.context),
                        'failure':None if success else getattr(game.parser,'last_fail_message',None),
                        'before':before,'after':after}
                    records.append(row)
                    with (folder/'parser_calls.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
                    return success
                game.parser.parse_command=parse
                return game,chars
            def stop(game):return classify_outcome(captured['chars'][name])!='neither'
            error=None;frames=[]
            try:
                frames=simulate(pw.world_map,args.steps,personas=personas,build_world_fn=build_capture,
                    llm_client=brain,embedding_client=None,planner_client=planner_client,reflector_client=reflector_client,
                    extra_action_names=PENN_ACTION_VERBS,retrieval=_RETRIEVAL,
                    out_events=events,out_memories=memories,out_plans=plans,out_planner_sources=planner_sources,stop_when=stop)
            except Exception as exc:error=f'{type(exc).__name__}: {exc}'
            char=captured.get('chars',{}).get(name)
            root=[r for r in records if r['depth']==0]
            row={'seed':seed,'arm':arm,'error':error,'outcome':classify_outcome(char) if char is not None else None,
                'raw_drinks':char.get_property('drank_unboiled') if char is not None else None,
                'safe_drinks':char.get_property('drank_safe') if char is not None else None,
                'root_parser_calls':len(root),'root_legal':sum(r['success'] for r in root),
                'root_material_changes':sum(bool(r['material_delta']) for r in root),
                'model_calls':len(base.calls),'prompt_tokens':sum(r['prompt_tokens'] for r in base.calls),
                'completion_tokens':sum(r['completion_tokens'] for r in base.calls),
                'frames':len(frames),'planner_sources':planner_sources,
                'calls_by_tool':{t:sum(r.get('tool',{}).get('name')==t for r in base.calls)
                                for t in sorted({r.get('tool',{}).get('name') for r in base.calls if r.get('tool')})},
                'cloud_calls':0,'scientific_increment':0}
            dump(folder/'frames.json',frames);dump(folder/'events.json',events);dump(folder/'memories.json',memories)
            dump(folder/'plans.json',plans);dump(folder/'summary.json',row)
            dump(folder/'final_plans.json',{
                n:c.agent.plan.to_primitive() for n,c in captured.get('chars',{}).items()
                if getattr(getattr(c,'agent',None),'plan',None) is not None})
            summary.append(row);dump(args.out/'summary.json',summary);print(json.dumps(row,ensure_ascii=False),flush=True)
    dump(args.out/'runtime.json',{'wall_seconds':time.monotonic()-start,'cloud_calls':0})


if __name__=='__main__':main()
