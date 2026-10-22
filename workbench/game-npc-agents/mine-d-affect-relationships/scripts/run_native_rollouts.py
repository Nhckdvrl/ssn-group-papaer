#!/usr/bin/env python3
"""D-E11: upstream EvolvingWorld simulation with a fully recorded local transport."""
import argparse
import contextlib
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
from types import SimpleNamespace

from cache_local_weights import resolve_local_checkpoint
from run_adaptation_pipeline import Q8

REVISION='1de26550ccfff105f3ffe9f4b386716446291341'
SOURCE_SHA='d7eb96d5d59e5ac9cedf190738f033d23780576b025f5441f73c8def11240e8f'
INPUT_KEYS=['book_name','scene_index','world_state','character_states','previous_scene']


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def select_snapshots(values):
    selected=[]
    for book in sorted({v['book_name'] for v in values}):
        candidates=[(i,v) for i,v in enumerate(values) if v['book_name']==book]
        index,snapshot=min(candidates,key=lambda x:hashlib.sha256(('D-E11-native-rollout-v1|'+str(x[0])).encode()).hexdigest())
        # Future reference scenes never enter the simulator, even as unused fields.
        selected.append(dict(source_index=index,input={k:copy.deepcopy(snapshot[k]) for k in INPUT_KEYS}))
    return selected


def uses_adapter(system,owner,task):
    return owner=='character' and (system=='multitask_sft' or system=='update_sft' and task=='character_update')


class LocalClient:
    def __init__(self,backend,owner):
        self.backend=backend;self.owner=owner;self.task_name=None
        self.config=SimpleNamespace(mode='local',base_url='local-transformers',model_name=backend.system+'/'+owner)

    def chat(self,messages,max_tokens=4096,temperature=.7,extra_body=None,**kwargs):
        b=self.backend
        if time.monotonic()-b.started>=b.max_seconds:raise TimeoutError('Registered D-E11 process budget exhausted')
        inputs=b.tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False,
                                               return_tensors='pt',return_dict=True).to('cuda')
        n=inputs['input_ids'].shape[-1]
        if n+max_tokens>32768:raise ValueError(f'No truncation: {n} input + {max_tokens} output exceeds 32768')
        adapter=uses_adapter(b.system,self.owner,self.task_name)
        setting=dict(do_sample=True,temperature=.7,top_p=.8,top_k=0,max_new_tokens=max_tokens,pad_token_id=b.tokenizer.pad_token_id)
        if extra_body and 'repetition_penalty' in extra_body:setting['repetition_penalty']=extra_body['repetition_penalty']
        with (b.model.disable_adapter() if b.has_adapter and not adapter else contextlib.nullcontext()),b.torch.inference_mode():
            t=time.monotonic();out=b.model.generate(**inputs,**setting);b.torch.cuda.synchronize()
        ids=out[0,n:].tolist();text=b.tokenizer.decode(ids,skip_special_tokens=True)
        record=dict(call_index=b.calls,snapshot_index=b.snapshot_index,owner=self.owner,task=self.task_name,
                    adapter_active=adapter,messages=messages,response=text,prompt_token_ids=inputs['input_ids'][0].tolist(),
                    completion_token_ids=ids,usage=dict(prompt_tokens=n,completion_tokens=len(ids)),
                    finish_reason='stop' if ids and ids[-1] in b.eos_ids else 'length',generation=setting,
                    requested_temperature=temperature,wall_s=time.monotonic()-t)
        with b.raw.open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
        b.calls+=1
        return text


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True)
    p.add_argument('--system',choices=['base','update_sft','multitask_sft'],default='base')
    p.add_argument('--prepare-only',action='store_true');p.add_argument('--max-hours',type=float,default=3)
    a=p.parse_args();root=Path(a.asset_root);repo=Path(__file__).resolve().parents[4]
    data=root/'data/native_D-E11';source=root/'data/EvolvingWorld/test/test_snapshots_ood.json'
    if digest(source)!=SOURCE_SHA:raise ValueError('Changed upstream snapshot file')
    selected=select_snapshots(json.loads(source.read_text()));assert len(selected)==6
    data.mkdir(exist_ok=True)
    frozen=json.dumps(selected,ensure_ascii=False,indent=2)+'\n';input_path=data/'snapshots.json'
    if input_path.exists() and input_path.read_text()!=frozen:raise ValueError('Frozen cohort changed')
    if not input_path.exists():input_path.write_text(frozen)
    selection=dict(experiment='D-E11',source_sha256=SOURCE_SHA,input_sha256=digest(input_path),n_books=6,
                   snapshots=[dict(source_index=x['source_index'],book=x['input']['book_name'],scene=x['input']['scene_index'],
                                   n_characters=len(x['input']['character_states'])) for x in selected],
                   future_reference_fields_passed_to_model=False)
    if a.prepare_only:
        print(json.dumps(selection,ensure_ascii=False,indent=2));return
    vendor=root/'vendor/EvolvingWorld';observed=subprocess.check_output(['git','rev-parse','HEAD'],cwd=vendor,text=True).strip()
    if observed!=REVISION:raise ValueError('Changed upstream simulator revision')
    sys.path.insert(0,str(vendor))
    from simulation.simulator import StorySimulator,SimulationConfig
    from simulation.utils import setup_logger,split_result_views
    out=root/'runs/D-E11'/a.system;out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();meta=dict(experiment='D-E11',system=a.system,complete=False,error=None,
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),selection=selection,
        vendor_revision=observed,upstream_files={str(f.relative_to(vendor)):digest(f) for f in (vendor/'simulation').glob('*.py')},
        runner_sha256=digest(__file__),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
        max_hours=a.max_hours,seed=42,max_scenes=3,max_turns_per_scene=12,processed_snapshots=[])
    def save(): (out/'metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    save();(out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
    try:
        import torch,transformers
        from transformers import AutoModelForCausalLM,AutoTokenizer,set_seed
        torch.set_num_threads(8);checkpoint,mirror=resolve_local_checkpoint(Q8)
        tok=AutoTokenizer.from_pretrained(checkpoint,local_files_only=True)
        if tok.pad_token_id is None:tok.pad_token_id=tok.eos_token_id
        model=AutoModelForCausalLM.from_pretrained(checkpoint,local_files_only=True,dtype=torch.bfloat16,
                                                 attn_implementation='sdpa',device_map={'':0}).eval()
        adapter=None
        if a.system!='base':
            mode='update' if a.system=='update_sft' else 'multitask'
            train=json.loads((root/'runs/D-E10'/('train_'+mode+'_v2/metadata.json')).read_text())
            if not train.get('complete'):raise ValueError('Only complete final training checkpoints may enter D-E11')
            adapter=Path(train['final_checkpoint'])
            from peft import PeftModel
            model=PeftModel.from_pretrained(model,str(adapter),is_trainable=False).eval()
            meta['adapter_files']={f.name:digest(f) for f in adapter.glob('*') if f.suffix in ['.json','.safetensors']}
        meta.update(checkpoint=Q8,resolved_checkpoint=checkpoint,local_weight_mirror=mirror,adapter=str(adapter) if adapter else None,
                    generation_config=model.generation_config.to_dict(),
                    torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(0))
        save();eos=model.generation_config.eos_token_id
        backend=SimpleNamespace(system=a.system,tokenizer=tok,model=model,torch=torch,has_adapter=adapter is not None,
                                started=started,max_seconds=a.max_hours*3600,raw=out/'raw.jsonl',calls=0,snapshot_index=None,
                                eos_ids=set(eos if isinstance(eos,list) else [eos]))
        world=LocalClient(backend,'world');character=LocalClient(backend,'character')
        class RoutedSimulator(StorySimulator):
            def call_model(self,task_name,*args,**kwargs):
                world.task_name=character.task_name=task_name
                return super().call_model(task_name,*args,**kwargs)
        for item in selected:
            if time.monotonic()-started>=backend.max_seconds:
                meta['stop_reason']='registered_budget';break
            set_seed(42);backend.snapshot_index=item['source_index']
            target=out/('snapshot_'+str(item['source_index']));target.mkdir()
            setup_logger('simulation',target/'simulation.log')
            sim=RoutedSimulator(world,character,SimulationConfig(max_scenes=3,max_turns_per_scene=12,max_tokens=4096))
            def persist(result,trace):
                (target/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
                (target/'trace.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n')
            result,trace=sim.run_snapshot(copy.deepcopy(item['input']),on_progress=persist);persist(result,trace)
            views=split_result_views(result)
            for name,value in views.items():(target/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
            meta['processed_snapshots'].append(dict(source_index=item['source_index'],book=item['input']['book_name'],
                stop_reason=result['stop_reason'],error=result.get('error'),n_scenes=len(result['scenes']),
                n_interactions=sum(len(x['interactions']) for x in result['scenes'])))
            meta['recorded_generation_attempts']=backend.calls;save()
        else:meta['complete']=True
    except BaseException as e:
        meta['error']=repr(e);raise
    finally:
        meta['wall_s']=time.monotonic()-started;meta['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()


if __name__=='__main__':main()
