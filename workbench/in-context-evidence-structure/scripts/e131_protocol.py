"""Fixed cross-size mechanism chain; no new scientific observation or model selection."""
import argparse,contextlib,gc,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL_NAMES={'qwen3':'Qwen3-8B','llama':'Llama-3.1-8B','qwen32':'Qwen3-32B','llama70':'Llama-3.1-70B'}
STAGES={'mechanism':{'conditions':43,'discovery_seed':121001,'confirmation_seed':131102},
 'native':{'conditions':64,'discovery_seed':120001,'confirmation_seed':131101},
 'function':{'conditions':85,'discovery_seed':123001,'confirmation_seed':131103}}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record_worker(args,resident,label,complete,error=None):
 now=time.time()
 occupancy={'family':args.family,'host':os.uname().nodename,'model':args.model,
  'started_at':resident['started_at'],'last_observed_at':now,
  'num_devices':resident['num_devices'],'resident_device_hours_so_far':(now-resident['started_at'])/3600*resident['num_devices'],
  'scope':'continuous residency from first model loading through completed or failed stage, including material generation, analysis, interstage and floor waiting; excludes pre-load imports',
  'last_stage':label,'worker_complete':complete,'failed':error is not None,'error':error}
 (ROOT/'results/e131'/('worker_'+args.family+'_'+'_'.join(args.phases)+'.json')).write_text(json.dumps(occupancy,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--family',choices=MODEL_NAMES,required=True)
 ap.add_argument('--model',required=True);ap.add_argument('--phases',nargs='+',choices=['discovery','confirmation'],required=True)
 ap.add_argument('--preflight-only',action='store_true');args=ap.parse_args()
 assert Path(args.model).name==MODEL_NAMES[args.family]
 assert args.family in ['qwen32','llama70'] or args.phases==['confirmation']
 manifest=json.loads((ROOT/'results/e131/engine_parent_manifest.json').read_text())
 for stage,m in manifest.items():
  assert digest(ROOT/'scripts'/m['engine'])==m['engine_sha256']
  assert digest(ROOT/'scripts'/m['parent'])==m['parent_sha256']
 sys.path.insert(0,str(ROOT/'scripts'))
 modules={}
 for stage in STAGES:
  path=ROOT/'scripts'/manifest[stage]['engine'];spec=importlib.util.spec_from_file_location('ices_e131_'+stage,path)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);modules[stage]=module
 if not args.preflight_only:
  review=ROOT/'results/e131/independent_pre_score_review_2026-10-12.json';assert review.exists()
  # Frozen protocol, dispatch, and effective sources must all already be committed.
  commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
  for name in ['e131_protocol.py','e131_dispatch.py']+[m['engine'] for m in manifest.values()]:
   path=ROOT/'scripts'/name
   assert subprocess.check_output(['git','show',commit+':workbench/in-context-evidence-structure/scripts/'+name],cwd=ROOT)==path.read_bytes()
  if args.family in ['qwen32','llama70']:
   identity=ROOT/'results/e131'/('model_identity_'+args.family+'_'+os.uname().nodename+'.json')
   j=json.loads(identity.read_text());assert j['all_weights_sha256_passed'] and j['target']==args.model
  import torch
  # Restoring this function keeps sequential protocols independent despite reuse of frozen weights.
  from transformers.models.qwen3 import modeling_qwen3
  from transformers.models.llama import modeling_llama
  model_module=modeling_qwen3 if 'Qwen' in args.model else modeling_llama
  native_eager=model_module.eager_attention_forward
  from e131_dispatch import _MODELS,_RESIDENCY,scale_num_devices,scale_revision
 for phase in args.phases:
  for stage,settings in STAGES.items():
   n=16 if phase=='discovery' else 32;seed=settings[phase+'_seed'];materials='discovery' if phase=='discovery' else 'validation'
   label=args.family+'_'+phase+'_'+stage
   dest=ROOT/'results/e131'/('preflight_'+label if args.preflight_only else label)
   dest.mkdir(parents=True,exist_ok=True);assert not (dest/'behavior.jsonl').exists()
   if not args.preflight_only:
    preflight=ROOT/'results/e131'/('preflight_'+label);assert (preflight/'preflight.json').exists()
    wait_start=time.time()
    if args.family in ['qwen32','llama70'] and phase=='confirmation':
     first=ROOT/'results/e131'/(args.family+'_discovery_'+stage)/'behavior.jsonl'
     while True:
      if first.exists():
       lines=first.read_text().splitlines()
       if lines:
        r=json.loads(lines[0]);assert len(r['conditions'])==settings['conditions'];break
      if time.time()-wait_start>7200:raise TimeoutError('No numerically valid fixed discovery context')
      time.sleep(5)
    reused=args.model in _MODELS
    launch={'stage':stage,'phase':phase,'n':n,'seed':seed,'materials':materials,'frozen_commit':commit,
     'family':args.family,'model':args.model,'model_revision':scale_revision(args.model),'host':os.uname().nodename,
     'visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),'model_reused':reused,
     'engine_sha256':manifest[stage]['engine_sha256'],'dispatch_sha256':digest(ROOT/'scripts/e131_dispatch.py'),
     'protocol_sha256':digest(Path(__file__)),'selection':'All fixed models, protocols and phases; numerical floor only',
     'waiting_seconds':time.time()-wait_start}
    (dest/'operational_launch.json').write_text(json.dumps(launch,indent=2)+'\n')
   sys.argv=[str(ROOT/'scripts'/manifest[stage]['engine']),'--model',args.model,'--out',str(dest),'--n',str(n),'--seed',str(seed),'--materials',materials]
   if args.preflight_only:sys.argv.append('--preflight-only')
   with (dest/('cpu.log' if args.preflight_only else 'run.log')).open('w',buffering=1) as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    try:modules[stage].main()
    except BaseException as exc:
     if not args.preflight_only and args.model in _RESIDENCY:
      record_worker(args,_RESIDENCY[args.model],label,False,repr(exc))
     raise
    finally:
     if not args.preflight_only:model_module.eager_attention_forward=native_eager
   if not args.preflight_only:
    assert (dest/'contexts.jsonl').read_bytes()==(preflight/'contexts.jsonl').read_bytes()
    run=json.loads((dest/'run.json').read_text());model=_MODELS[args.model]
    run.update({'stage':stage,'experiment':'E131','parent_engine':manifest[stage]['parent'],
     'parent_engine_sha256':manifest[stage]['parent_sha256'],'dispatch_sha256':digest(ROOT/'scripts/e131_dispatch.py'),
     'protocol_sha256':digest(Path(__file__)),'num_layers':len(model.model.layers),
     'model_device_map':model.hf_device_map,'model_reused':reused,'num_GPU_devices':scale_num_devices(model),
     'matmul_allow_tf32':torch.backends.cuda.matmul.allow_tf32,
     'gpu_hours_scope':'scientific stage wall timer multiplied by actual distinct GPUs; includes model load only when first used, excludes protocol imports/floor wait/interstage gaps',
     'model_run_wall_hours':run['elapsed_seconds']/3600})
    (dest/'run.json').write_text(json.dumps(run,indent=2)+'\n');gc.collect();torch.cuda.empty_cache()
    record_worker(args,_RESIDENCY[args.model],label,phase==args.phases[-1] and stage==list(STAGES)[-1])
   print(label,'complete','CPU' if args.preflight_only else 'GPU',flush=True)
if __name__=='__main__':main()
