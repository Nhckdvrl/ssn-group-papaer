"""Finish every registered E34 seed at 300, then fixed E36/E37/E39 readouts."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    scripts=Path(__file__).resolve().parent
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    def ready(seed):
        for route in ['full','no_consist']:
            folder=args.runs/f'e34_cpu_s{seed}_{route}/checkpoint_0300'
            try:meta=json.loads((folder/'manifest.json').read_text())
            except (FileNotFoundError,json.JSONDecodeError):return False
            if meta['completed_iterations']!=300 or not (folder/'training_state.pt').exists():return False
        return True
    def run(name,filename,extra):
        with (args.out/f'{name}.log').open('w') as f:
            result=subprocess.run([sys.executable,str(scripts/filename),'--runs',str(args.runs),*extra],
                                  env=env,stdout=f,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError(f'{name}: inspect {args.out/f"{name}.log"}')
        print(json.dumps({'finished':name}),flush=True)
    def one_seed(seed):
        while not ready(seed):time.sleep(15)
        folder=args.runs/f'e34_eval_s{seed}_i300'
        if not (folder/'summary.json').exists():
            run(f'e34_{seed}','pcsp_checkpoint_evaluate.py',['--seed',str(seed),'--iteration','300','--out',str(folder)])
        return seed
    with ThreadPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(one_seed,s) for s in [42,43,44]]):
            print(json.dumps({'seed_complete':future.result(),'iteration':300}),flush=True)
    for name,filename,folder in [('e36','pcsp_latent_response.py','e36_response_i300'),
                                 ('e37','pcsp_matched_functional_response.py','e37_matched_i300'),
                                 ('e39','pcsp_direction_transport.py','e39_transport_i300')]:
        path=args.runs/folder
        if not (path/'summary.json').exists():run(name,filename,['--iteration','300','--out',str(path)])
    result={'all_training_seeds':[42,43,44],'iteration':300,'fixed_readouts':['native','semantic','interest','E36','E37','E39'],
            'best_seed_or_iteration_selection':False,'cloud_calls':0}
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
