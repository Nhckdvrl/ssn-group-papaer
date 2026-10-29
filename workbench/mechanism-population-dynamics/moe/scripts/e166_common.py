"""Frozen cross-family inputs, source fingerprints and bounded work ledger."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time

import numpy as np
import torch
from transformers import OlmoeForCausalLM
import e165_common as old
from e165_core import hook_fingerprint

WB=Path(__file__).resolve().parents[2]
ROOT=WB/'moe/results/e166'
RAW=Path.home()/'mechpop_cache/e166_gain_transport'
SCRIPTS=Path(__file__).parent
sha=old.sha
read=old.read
write=old.write
record=old.record
save=old.save


def proof():
    pending=['e166_common.py','e166_core.py','e166_run.py','e166_analyze.py',
             'e166_verify.py','e166_selftest.py','e166_finish.py','supervised_process.py']
    result={}
    while pending:
        name=pending.pop()
        if name in result:continue
        p=SCRIPTS/name;result[name]=sha(p)
        for node in ast.walk(ast.parse(p.read_text())):
            names=[a.name for a in node.names] if isinstance(node,ast.Import) else (
                [node.module] if isinstance(node,ast.ImportFrom) and node.module else [])
            for module in names:
                candidate=module.split('.')[0]+'.py'
                if (SCRIPTS/candidate).is_file() and candidate not in result:pending.append(candidate)
    return dict(sorted(result.items()))


def prepare():
    if (ROOT/'plan.json').exists():raise FileExistsError('Preserve E166 plan')
    tests=read(ROOT/'CPU_tests.json')
    if tests['status']!='passed' or tests['source_sha256']!=proof():raise ValueError('Stale CPU controls')
    families={}
    for family,previous in [('emo','e164'),('olmoe','e165')]:
        root=WB/'moe/results'/previous;p=read(root/'plan.json');m=read(root/'manifest.json')
        if m['status']!='complete':raise ValueError('Complete old experiment required')
        spec={'previous_plan':record(root/'plan.json'),'previous_manifest':record(root/'manifest.json'),
              'input':p['fresh_input' if family=='emo' else 'input'],
              'selectors':read(root/'preflight.json')['selectors'],
              'reference':m['raw'],'subjects':p['subjects'][2:] if family=='emo' else p['subjects'],
              'pad_token_id':p['pad_token_id'],'source_records':p['source_records']}
        if family=='olmoe':
            spec['asset_manifest']=p['asset_manifest']
            spec['local_stage']=record(root/'local_staging.json')
        for key in ('input','selectors','reference'):
            if sha(spec[key]['path'])!=spec[key]['sha256']:raise ValueError('Inherited bytes changed')
        families[family]=spec
    if families['emo']['subjects']!=families['olmoe']['subjects']:raise ValueError('Subject alignment differs')
    commit=subprocess.check_output(['git','rev-parse','--short=8','HEAD'],cwd=WB,text=True).strip()
    for name,digest in proof().items():
        committed=subprocess.check_output(['git','show','HEAD:workbench/mechanism-population-dynamics/moe/scripts/'+name],cwd=WB)
        if hashlib.sha256(committed).hexdigest()!=digest:raise ValueError('Commit numerical source first: '+name)
    write(ROOT/'plan.json',{'experiment':'E166','status':'prepared','numerical_source_commit':commit,
          'source_sha256':proof(),'software':old.software(),'CPU_tests':record(ROOT/'CPU_tests.json'),
          'families':families,'bootstrap_seed':166002,'resamples':2000,'calibration_batch_size':2,
          'gpu_limit_seconds':14400,'resource_wait_limit_seconds':7200,'max_concurrent_GPUs':1,
          'user_total_GPU_limit':4,'new_training':False,
          'calibration':'Native P full, same inputs and gates; sqrt(donor/P routed energy), FP32 product FP64 sum.',
          'scope':'Layerwise uniform output gain rival; no loss fitting, mask or gain search; source/cal/input conditional.'})
    print(json.dumps({'status':'prepared','source_files':len(proof()),'plan_sha256':sha(ROOT/'plan.json')}))


def checked_plan():
    plan=read(ROOT/'plan.json')
    if plan['source_sha256']!=proof() or plan['software']!=old.software():raise ValueError('Frozen source/software changed')
    for spec in plan['families'].values():
        for key in ('previous_plan','previous_manifest','input','selectors','reference'):
            if sha(spec[key]['path'])!=spec[key]['sha256']:raise ValueError('Inherited provenance changed: '+key)
    return plan


def load(family,spec):
    if torch.cuda.is_initialized():raise ValueError('Load CPU before CUDA')
    start=time.monotonic();models=[];states=[]
    if family=='emo':
        import e156_loading as loader
        labels=('P','B')
    else:
        labels=('P','A');stage=read(spec['local_stage']['path'])
        if sha(spec['local_stage']['path'])!=spec['local_stage']['sha256'] or stage['host']!=socket.gethostname():
            raise ValueError('Registered OLMoE NVMe stage required')
        assets=read(spec['asset_manifest']['path'])
    for label in labels:
        if family=='emo':model=loader.load_cpu_bf16(label,device='cpu')
        else:
            local=stage['models'][label]
            for name,item in local['files'].items():
                if sha(item['path'])!=assets['models'][label]['files'][name]['sha256']:
                    raise ValueError('Node-local public bytes changed')
            model=OlmoeForCausalLM.from_pretrained(local['directory'],local_files_only=True,
                    dtype=torch.bfloat16,low_cpu_mem_usage=False,attn_implementation='eager').eval().requires_grad_(False)
        state=old.state(model,label);expected=spec['source_records'][label]
        if any(state[k]!=expected[k] for k in ('parameter_hash','buffer_hash')):raise ValueError('Canonical source differs: '+label)
        models.append(model);states.append(state)
        print(json.dumps({'event':'CPU_ready','family':family,'source':label,'seconds':time.monotonic()-start}),flush=True)
    write(ROOT/('CPU_readiness_'+family+'.json'),{'status':'ready','sources':states,
          'seconds':time.monotonic()-start,'CUDA_initialized':False,'host':socket.gethostname()})
    return models,states


def acquire(physical,plan,family):
    start=time.monotonic()
    while True:
        try:
            handle=old.old.gpu_lock(physical)
            write(ROOT/('GPU_wait_'+family+'.json'),{'status':'acquired','physical_gpu':physical,
                  'host':socket.gethostname(),'seconds':time.monotonic()-start})
            return handle
        except (RuntimeError,BlockingIOError) as error:
            if not isinstance(error,BlockingIOError) and 'occupied' not in str(error):raise
            if torch.cuda.is_initialized():raise RuntimeError('CUDA during resource wait')
            if time.monotonic()-start>=plan['resource_wait_limit_seconds']:raise TimeoutError('CPU model wait expired') from error
            write(ROOT/('GPU_wait_'+family+'.json'),{'status':'waiting_with_CPU_models','seconds':time.monotonic()-start,'reason':str(error)})
        time.sleep(10)


class Budget(old.old.Budget):
    def __init__(self,plan,family):
        self.path,self.experiment,self.phase=ROOT/'budget.json','e166',family
        self.limit=plan['gpu_limit_seconds'];self.last_write=0.

    def check(self):
        self.row['gpu_seconds']=time.monotonic()-self.start
        exhausted=self.prior+self.row['gpu_seconds']>=self.limit
        if time.monotonic()-self.last_write>=15 or exhausted:write(self.path,self.state);self.last_write=time.monotonic()
        if exhausted:raise TimeoutError('E166 GPU package exhausted')
