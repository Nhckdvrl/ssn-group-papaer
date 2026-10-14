"""E41 registered unbound-code control: all three seeds and fixed stages."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runs',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--control',choices=['unbound','goal_only'],default='unbound')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    scripts=Path(__file__).resolve().parent
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    def run(name,entry,extra):
        with (args.out/f'{name}.log').open('w') as log:
            r=subprocess.run([sys.executable,str(scripts/entry),*extra],env=env,stdout=log,stderr=subprocess.STDOUT)
        if r.returncode:raise RuntimeError(f'{name} failed; preserved log')
    def one(stage,seed):
        checkpoint=args.runs/f'e41_s{seed}_{args.control}/checkpoint_{stage:04d}'
        while not (checkpoint/'manifest.json').exists():time.sleep(15)
        meta=json.loads((checkpoint/'manifest.json').read_text())
        assert meta['seed']==seed and meta['completed_iterations']==stage
        out=args.runs/f'e41_eval_s{seed}_{args.control}_i{stage}'
        if not (out/'summary.json').exists():
            run(f'eval_{stage}_{seed}','pcsp_checkpoint_evaluate.py',
                ['--runs',str(args.runs),'--seed',str(seed),'--iteration',str(stage),
                 '--reference-directory',str(args.runs/f'e34_cpu_s{seed}_no_consist/checkpoint_{stage:04d}'),
                 '--alternative-directory',str(checkpoint),'--comparison-name',f'{args.control}_vs_original_no_infoNCE',
                 '--out',str(out)])
        print(json.dumps({'stage':stage,'seed':seed,'completed':args.control}),flush=True)
        return str(out)
    for stage in [30,100,300]:
        with ThreadPoolExecutor(max_workers=3) as pool:
            evaluations=[f.result() for f in as_completed([pool.submit(one,stage,s) for s in [42,43,44]])]
        policy_manifest={str(s):{'original':str(args.runs/f'e34_cpu_s{s}_no_consist/checkpoint_{stage:04d}'),
                                args.control:str(args.runs/f'e41_s{s}_{args.control}/checkpoint_{stage:04d}')} for s in [42,43,44]}
        path=args.out/f'policies_i{stage}.json';path.write_text(json.dumps(policy_manifest,indent=2)+'\n')
        out=args.runs/f'e41_functional_{args.control}_i{stage}'
        if not (out/'summary.json').exists():
            run(f'functional_{stage}','pcsp_matched_functional_response.py',
                ['--runs',str(args.runs),'--iteration',str(stage),'--policy-manifest',str(path),'--out',str(out)])
        result={'stage':stage,'evaluations':evaluations,'functional_raw':str(out),'selection':False,
                'interpretation':'Natural endpoints share the primary E41 measurement. Matched angles are within original/unbound comparison; do not compare magnitude-matched values across different comparison pools.'}
        (args.out/f'stage_{stage}_complete.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'stage_complete':stage}),flush=True)
    (args.out/'summary.json').write_text(json.dumps({'all_stages':[30,100,300],'all_seeds':[42,43,44],
                'control':args.control,'cloud_calls':0,'selection':False},indent=2)+'\n')


if __name__=='__main__':main()
