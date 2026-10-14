"""E35 fixed natural repeats, one local model load, independent worlds/calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seeds',type=int,nargs='+',default=[3502,3503])
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',LLM_PROVIDER='mock')
    from strong_native_baseline import ModelClient
    import strong_native_baseline
    import native_penn_social
    before=time.monotonic()
    base=ModelClient(args.model,args.seeds[0],args.out/'unused_initial_trace.jsonl')
    load=time.monotonic()-before
    origin={'seeds':args.seeds,'model':str(args.model),'load_seconds_once':load,
        'world_and_memory_reset_per_seed':True,'new_calls_list_per_seed':True,
        'sampling_seed_explicit_per_call':True,'cloud_calls':0,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.out/'batch_manifest.json').write_text(json.dumps(origin,indent=2)+'\n')
    def cached_model(model,seed,trace_file):
        assert Path(model)==args.model
        base.seed=seed;base.calls=[];base.trace_file=Path(trace_file)
        return base
    strong_native_baseline.ModelClient=cached_model
    summaries={}
    for seed in args.seeds:
        folder=args.out/f'seed{seed}'
        sys.argv=['native_penn_social.py','--backend','local','--model',str(args.model),
                  '--seed',str(seed),'--steps','1200','--max-calls','0','--out',str(folder)]
        native_penn_social.main()
        summaries[str(seed)]=json.loads((folder/'summary.json').read_text())
        (args.out/'summary.json').write_text(json.dumps({'batch':origin,'episodes':summaries},indent=2)+'\n')


if __name__=='__main__':main()
