"""Run the published clean CNN trainer unchanged, with origin metadata."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time
import traceback


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seed',type=int,required=True)
    ap.add_argument('--mode',choices=['full','no_consist'],required=True)
    ap.add_argument('--total-steps',type=int,default=500000)
    ap.add_argument('--collective-reward-alpha',type=float,default=0.)
    ap.add_argument('--persona-cache',type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',JAX_PLATFORMS='cpu',TF_CPP_MIN_LOG_LEVEL='2')
    root=args.source/'research/meltingpot';entry=root/'scripts/run_pcsp_meltingpot_clean.py'
    embedding=args.persona_cache or args.source/'results/embeddings/persona_emb_qwen_emb.pt'
    sys.path[:0]=[str(root/'upstream'),str(root/'scripts')]
    argv=[str(entry),'--seed',str(args.seed),'--total-env-steps',str(args.total_steps),
          '--device','cuda','--run-dir',str(args.out),
          '--collective-reward-alpha',str(args.collective_reward_alpha),'--persona-cache',str(embedding)]
    if args.mode=='no_consist':argv.append('--ablation-no-infonce')
    manifest={'source_sha':subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip(),
        'source_script_sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),'source_entry':str(entry),
        'original_argv':argv,'seed':args.seed,'mode':args.mode,'pid':os.getpid(),
        'visible_gpu':os.environ.get('CUDA_VISIBLE_DEVICES'),'conda_python':sys.executable,
        'embedding_sha256':hashlib.sha256(embedding.read_bytes()).hexdigest(),
        'versions':{p:importlib.metadata.version(p) for p in ['torch','dmlab2d','tensorflow-cpu','numpy']},
        'engine_seed_scope':'Original trainer seeds numpy/torch. Python builder RNG is not explicitly seeded; native bit determinism not assumed.',
        'encoding_provenance':'Original instruction and recipe numerically verified in E38; explicit cache override identifies corrected last-real pooling.',
        'embedding_path':str(embedding),'embedding_override':args.persona_cache is not None,
        'trainer_modified':False,'world_or_reward_modified':False,
        'collective_reward_alpha':args.collective_reward_alpha,'cloud_calls':0,
        'raw_environment_reward_modified':False,'training_reward_formula':'raw_r_i + author_alpha * mean_j(raw_r_j)',
        'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    assert manifest['source_sha']=='5420f7b4fa0fdb6110e131402af9f5386ce2d0cf'
    (args.out/'training_origin.json').write_text(json.dumps(manifest,indent=2)+'\n')
    sys.argv=argv;start=time.monotonic();error=None
    try:runpy.run_path(str(entry),run_name='__main__')
    except BaseException:
        error=traceback.format_exc();raise
    finally:
        (args.out/'completion.json').write_text(json.dumps({'error':error,'wall_seconds':time.monotonic()-start,
            'policy_exists':(args.out/'policy.pt').exists(),'cloud_calls':0},indent=2)+'\n')


if __name__=='__main__':main()
