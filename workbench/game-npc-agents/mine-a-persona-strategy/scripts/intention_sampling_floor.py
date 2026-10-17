#!/usr/bin/env python3
"""E15: repeated independent I/A sampling at replay-verified native snapshots."""
import argparse
from collections import Counter
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import time

from light_npc_episodes import (CACHE, ViewerHost, actor_for, execute, material_state,
                               observation, chosen_command)
from light_native_gate import load_event_modules
from native_actioncastle import dump


def snapshots(run, modules):
    OOGraph,events,ErrorEvent=modules
    cases=json.loads((run/"source_cases.json").read_text())
    result=[]
    for case in cases:
        folder=run/f"demo{case['demo_index']}_s901"
        turns=json.loads((folder/"episode.json").read_text())
        calls=[json.loads(s) for s in (folder/"model_calls.jsonl").read_text().splitlines()]
        for target in [0,min(3,len(turns)-1)]:
            graph=OOGraph.from_json(case["npc_quest"]["graph"])
            npc=actor_for(graph,case["npc_quest"]["character"])
            human=actor_for(graph,case["demo"]["human_persona"]["name"])
            host=ViewerHost(graph)
            random.seed(901)
            for step in range(target+1):
                row=execute(host,human,turns[step]["human"]["command"],events,ErrorEvent)
                assert material_state(graph)==turns[step]["human"]["after"],(case['demo_index'],step,'human')
                observation(host,npc,events,ErrorEvent)
                if step==target:
                    break
                row=execute(host,npc,turns[step]["npc"]["command"],events,ErrorEvent)
                assert material_state(graph)==turns[step]["npc"]["after"],(case['demo_index'],step,'npc')
            # Capture the exact already-used provider-neutral messages/schema,
            # including local action envelope and original intention question.
            i_call,a_call=calls[1+2*target],calls[2+2*target]
            assert i_call['kind']==a_call['kind']=='native_choose_action'
            assert i_call['schema']==a_call['schema']
            result.append({"case":case,"step":target,"graph":graph,"actor_id":npc.node_id,
                "rng_state":random.getstate(),"I":i_call,"A":a_call,"menu":turns[target]['menu']})
    return result


def js(left,right):
    import numpy as np
    keys=sorted(set(left)|set(right))
    p=np.asarray([left.get(k,0) for k in keys],dtype=float);p/=p.sum()
    q=np.asarray([right.get(k,0) for k in keys],dtype=float);q/=q.sum()
    m=(p+q)/2
    return float(.5*np.sum(p[p>0]*np.log(p[p>0]/m[p>0]))+.5*np.sum(q[q>0]*np.log(q[q>0]/m[q>0])))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run',type=Path,default=CACHE/'runs/e14_qwen35_12graphs')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--mode',choices=['cpu','model'],required=True)
    ap.add_argument('--model',type=Path)
    ap.add_argument('--limit',type=int,default=24)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    modules=load_event_modules(CACHE/'sources/LIGHT')
    frozen=snapshots(args.run,modules)[:args.limit]
    dump(args.out/'manifest.json',{'model':str(args.model),'source_run':str(args.run),
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'calls_per_snapshot':48,'sample_seed_base':150000,'cloud_calls':0,
        'native_rng':'common fixed native snapshot RNG per counterfactual fork',
        'snapshot_ids':[(s['case']['demo_index'],s['step']) for s in frozen]})
    if args.mode=='cpu':
        dump(args.out/'cpu_replay.json',{'snapshots':len(frozen),'all_material_replays_matched':True,
            'fork_clones_match':all(material_state(copy.deepcopy(s['graph']))==material_state(s['graph']) for s in frozen)})
        print('CPU snapshots and graph clones matched',len(frozen),flush=True)
        return
    from strong_native_baseline import ModelClient
    from vllm import SamplingParams
    from vllm.sampling_params import StructuredOutputsParams
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_DATASETS_OFFLINE='1')
    client=ModelClient(args.model,150000,args.out/'unused.jsonl')
    start=time.monotonic();stats=[]
    for index,snapshot in enumerate(frozen):
        requests=[]
        for draw in range(16):
            for mode in ['A1','A2','I']:
                source=snapshot['I' if mode=='I' else 'A']
                seed=150000+index*1000+len(requests)
                prompt=client.tokenizer.apply_chat_template(source['messages'],tokenize=False,
                    add_generation_prompt=True,enable_thinking=False)
                assert hashlib.sha256(prompt.encode()).hexdigest()==source['prompt_sha256']
                requests.append({'mode':mode,'draw':draw,'seed':seed,'prompt':prompt,
                    'messages':source['messages'],'schema':source['schema']})
        results=[]
        # Each batch mixes all three conditions, with independent seeds and
        # identical sampling/decoding. The batching rule never depends on output.
        for offset in range(0,len(requests),16):
            batch=requests[offset:offset+16]
            sampled=client.llm.generate([r['prompt'] for r in batch],[SamplingParams(
                max_tokens=128,temperature=.7,seed=r['seed'],structured_outputs=StructuredOutputsParams(
                    json=r['schema'])) for r in batch],use_tqdm=False)
            for request,result in zip(batch,sampled):
                completion=result.outputs[0]
                try:choice=json.loads(completion.text);error=None
                except Exception as exc:choice=None;error=f'{type(exc).__name__}: {exc}'
                row={k:v for k,v in request.items() if k!='prompt'}
                row.update(response=completion.text,choice=choice,parse_error=error,
                    finish_reason=completion.finish_reason,prompt_tokens=len(result.prompt_token_ids),
                    completion_tokens=len(completion.token_ids))
                if choice is not None and request['mode'].startswith('A'):
                    graph=copy.deepcopy(snapshot['graph']);host=ViewerHost(graph)
                    actor=graph.get_node(snapshot['actor_id'])
                    random.setstate(snapshot['rng_state'])
                    row['native']=execute(host,actor,chosen_command(choice),modules[1],modules[2])
                results.append(row)
        folder=args.out/f"demo{snapshot['case']['demo_index']}_step{snapshot['step']}"
        folder.mkdir();dump(folder/'draws.json',results)
        counts={mode:dict(Counter(r['choice']['action'] for r in results if r['mode']==mode
            and r['choice'] is not None)) for mode in ['A1','A2','I']}
        j_ia,j_aa=js(counts['I'],counts['A1']),js(counts['A2'],counts['A1'])
        row={'demo_index':snapshot['case']['demo_index'],'step':snapshot['step'],'counts':counts,
            'JS_I_A1':j_ia,'JS_A2_A1':j_aa,'paired_difference':j_ia-j_aa,
            'invalid_JSON':sum(r['choice'] is None for r in results),
            'native_action_draws':sum('native' in r for r in results),
            'native_legal':sum(r.get('native',{}).get('legal',False) for r in results),
            'native_material':sum(r.get('native',{}).get('material_changed',False) for r in results),
            'prompt_tokens':sum(r['prompt_tokens'] for r in results),
            'completion_tokens':sum(r['completion_tokens'] for r in results)}
        stats.append(row);dump(args.out/'summary.json',stats)
        print(json.dumps(row),flush=True)
    import numpy as np
    graph_ids=sorted(set(r['demo_index'] for r in stats))
    graph_means=np.asarray([np.mean([r['paired_difference'] for r in stats if r['demo_index']==gid]) for gid in graph_ids])
    rng=np.random.default_rng(151515)
    boot=[float(np.mean(rng.choice(graph_means,len(graph_means),replace=True))) for _ in range(2000)]
    dump(args.out/'analysis.json',{'graphs':len(graph_ids),'snapshots':len(stats),
        'mean_JS_difference':float(graph_means.mean()),'graph_bootstrap_95':np.quantile(boot,[.025,.975]).tolist(),
        'scope':'conditional discovery snapshots, not a population or persona causal claim',
        'wall_seconds':time.monotonic()-start,'scientific_increment':0})


if __name__=='__main__':main()
