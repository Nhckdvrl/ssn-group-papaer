"""Eight independent GPU slots; wait for verified mirror assets, retain every failure."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from data import CACHE

MODELS = ['Qwen3-1.7B', 'Qwen3-4B', 'Qwen3-8B', 'Qwen3-14B', 'Qwen3-32B',
          'gemma-3-4b-it', 'gemma-3-12b-it', 'gemma-3-27b-it',
          'Meta-Llama-3.1-8B-Instruct', 'Mistral-Small-24B-Instruct-2501',
          'OLMo-2-1124-13B', 'OLMo-2-1124-13B-Instruct', 'Qwen3-4B-Base', 'gemma-3-4b-pt']


class AdoptedProcess:
    """A coordinator restart must preserve already-running GPU work."""
    def __init__(self, pid, out, completion_field='predictions_sha256'): self.pid, self.out, self.completion_field = pid, out, completion_field
    def poll(self):
        config = self.out/'config.json'
        if config.exists() and json.loads(config.read_text()).get(self.completion_field): return 0
        try:
            command = Path(f'/proc/{self.pid}/cmdline').read_bytes().split(b'\0')
        except FileNotFoundError: return 1
        return None if str(self.out).encode() in command else 1


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, default=CACHE/'E52/runs')
    ap.add_argument('--stage', choices=['legacy', 'map', 'map-unlabelled', 'landmarks', 'thinking', 'surprisal','paraphrase','source-scope'], required=True)
    ap.add_argument('--models', nargs='+')
    ap.add_argument('--calibration-out',type=Path,help='Directory containing completed legacy runs; defaults to --out.')
    ap.add_argument('--dtype',choices=['bfloat16','float16','float32'],default='bfloat16')
    ap.add_argument('--formats',nargs='+',choices=['A','B'],default=['A','B'])
    ap.add_argument('--generation-python',type=Path,default=Path('/data1/xiangding/env/iir-e52-generation/bin/python'))
    args = ap.parse_args()
    completion_field='surprisal_sha256' if args.stage=='surprisal' else 'predictions_sha256'
    output_file='surprisal.jsonl' if args.stage=='surprisal' else 'predictions.jsonl'
    if args.models is None:args.models=MODELS[:5] if args.stage=='thinking' else MODELS
    args.out.mkdir(parents=True, exist_ok=True)
    waiting = list(args.models); running = {}; done = {}; failed = {}
    locks_root = CACHE/'E52/gpu-slots'; locks_root.mkdir(exist_ok=True)
    gpu_locks = [(locks_root/str(gpu)).open('a') for gpu in range(8)]
    script = Path(__file__).with_name({'thinking':'thinking_map.py','surprisal':'disambiguator_surprisal.py','paraphrase':'paraphrase_map.py','source-scope':'source_scope_map.py'}.get(args.stage,'reading_map.py'))
    for procdir in Path('/proc').iterdir():
        if not procdir.name.isdigit(): continue
        try:
            command = procdir.joinpath('cmdline').read_bytes().decode().split('\0')
            if not any(Path(part).name == script.name for part in command) or '--out' not in command: continue
            out = Path(command[command.index('--out')+1])
            ready = next((name for name in waiting if out == args.out/f'{name}-{args.stage}'), None)
            if ready is None: continue
            environment = dict(part.split('=', 1) for part in procdir.joinpath('environ').read_bytes().decode().split('\0') if '=' in part)
            gpu = int(environment['CUDA_VISIBLE_DEVICES']); assert gpu not in running
            fcntl.flock(gpu_locks[gpu], fcntl.LOCK_EX | fcntl.LOCK_NB)
            waiting.remove(ready)
            running[gpu] = (ready, AdoptedProcess(int(procdir.name), out,completion_field), (args.out/f'{ready}-{args.stage}.log').open('a'))
            print('GPU', gpu, ready, 'adopted existing PID', procdir.name, flush=True)
        except (FileNotFoundError, ProcessLookupError): continue
    while waiting or running:
        for gpu, (name, proc, log) in list(running.items()):
            status = proc.poll()
            if status is None: continue
            log.close(); del running[gpu]
            fcntl.flock(gpu_locks[gpu], fcntl.LOCK_UN)
            (done if status == 0 else failed)[name] = status
            print(name, 'completed' if status == 0 else f'FAILED({status})', flush=True)
        for gpu in range(8):
            if gpu in running: continue
            def available(name):
                if not (CACHE/'models'/name/'manifest.json').exists(): return False
                if args.stage == 'legacy': return True
                calibration = (args.calibration_out or args.out)/f'{name}-legacy/config.json'
                return calibration.exists() and bool(json.loads(calibration.read_text()).get('predictions_sha256'))
            ready = next((name for name in waiting if available(name)), None)
            if ready is None: break
            try: fcntl.flock(gpu_locks[gpu], fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError: continue
            waiting.remove(ready); out = args.out/f'{ready}-{args.stage}'
            if (out/'config.json').exists() and json.loads((out/'config.json').read_text()).get(completion_field):
                done[ready] = 0; fcntl.flock(gpu_locks[gpu], fcntl.LOCK_UN); continue
            if out.exists() and (out/output_file).exists():
                failed[ready] = 'Prior incomplete run retained; requires explicit retry version'
                fcntl.flock(gpu_locks[gpu], fcntl.LOCK_UN); continue
            log = (args.out/f'{ready}-{args.stage}.log').open('a')
            executable=str(args.generation_python) if args.stage in ('thinking','paraphrase') else sys.executable
            cmd = [executable, '-u', str(script), '--data', str(args.data),
                   '--model', str(CACHE/'models'/ready), '--out', str(out)]
            if args.stage=='thinking':cmd+=['--cap','2048']
            elif args.stage=='paraphrase':cmd+=['--cap','256']
            else:cmd+=['--batch-size','16']
            if args.stage not in ('thinking','surprisal','paraphrase','source-scope'):cmd+=['--dtype',args.dtype]
            if args.stage == 'legacy': cmd += ['--mode', 'legacy', '--legacy-processed', '--formats', 'A', '--readings', 'R0']
            elif args.stage == 'map-unlabelled': cmd += ['--formats', *args.formats, '--readings', 'R0', 'R1', 'R3', 'R4', 'R5', '--repair']
            elif args.stage == 'landmarks': cmd += ['--formats', *args.formats, '--readings', 'R2']
            elif args.stage=='map': cmd += ['--formats', 'A', 'B', '--readings', 'R0', 'R1', 'R2', 'R3', 'R4', 'R5', '--repair']
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu), HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
            proc = subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT,
                                    pass_fds=(gpu_locks[gpu].fileno(),))
            running[gpu] = (ready, proc, log); print('GPU', gpu, ready, 'started', flush=True)
        state = dict(stage=args.stage, waiting=waiting, running={str(k): v[0] for k, v in running.items()}, done=done, failed=failed)
        (args.out/f'{args.stage}-status.json').write_text(json.dumps(state, indent=2)+'\n')
        if waiting or running: time.sleep(10)
    print(json.dumps(state), flush=True)


if __name__ == '__main__': main()
