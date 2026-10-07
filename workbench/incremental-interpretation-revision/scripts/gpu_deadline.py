"""Human-requested GPU release at 2026-10-08 09:00 Asia/Shanghai.

Only this workbench's processes owned by the current Unix user are eligible.
External services and CPU/API annotation workers are left running.
"""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from zoneinfo import ZoneInfo

ROOT=Path('/data1/xiangding/work/incremental-interpretation-revision')
DEADLINE=datetime(2026,10,8,9,0,tzinfo=ZoneInfo('Asia/Shanghai')).timestamp()
STOP=ROOT/'GPU_RELEASE_REQUESTED.json'


def ensure_gpu_allowed():
    if STOP.exists() or time.time() >= DEADLINE:
        raise SystemExit('GPU use stopped by human deadline: 2026-10-08 09:00 Asia/Shanghai')


def gpu_pids():
    p=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stderr.strip())
    return {int(x) for x in p.stdout.splitlines() if x.strip().isdigit()}


def candidates():
    active=gpu_pids();found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit(): continue
        try:
            if p.stat().st_uid!=os.getuid(): continue
            argv=p.joinpath('cmdline').read_bytes().decode().split('\0')
        except (OSError,UnicodeError): continue
        if not any('incremental-interpretation-revision' in s for s in argv): continue
        pid=int(p.name)
        if pid in active or '--gpu' in argv:
            found.append(dict(pid=pid,argv=argv,active_gpu=pid in active))
    return found


def cleanup_weights():
    assert not candidates(), 'Release research GPU workers before removing reloadable weights'
    inventory=[]
    for model in sorted((ROOT/'models').iterdir()):
        if not model.is_dir() or model.is_symlink():continue
        assert (model/'manifest.json').exists(), model
        for p in sorted(model.rglob('*')):
            if p.is_symlink() or not p.is_file():continue
            if p.suffix=='.safetensors' or p.name.startswith('pytorch_model') and p.suffix=='.bin':
                assert p.stat().st_uid==os.getuid()
                inventory.append(dict(path=str(p),bytes=p.stat().st_size,manifest=str(model/'manifest.json')))
    dest=ROOT/'model-weight-release-inventory.json'
    if not dest.exists():dest.write_text(json.dumps(dict(reason='Human resource release request; keep pinned manifests and tokenizer/config metadata; weights reloadable from domestic mirrors',files=inventory),indent=2)+'\n')
    deleted=0
    for r in inventory:
        p=Path(r['path']);p.unlink();deleted+=r['bytes']
    print('Released model weight bytes',deleted,flush=True)


def enforce():
    ROOT.mkdir(exist_ok=True)
    if not STOP.exists():
        STOP.write_text(json.dumps(dict(request='Human hard deadline; no GPU restart without new human authorization',
            deadline='2026-10-08T09:00:00+08:00',enforced_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()),indent=2)+'\n')
    victims=candidates()
    for v in victims:
        try: os.kill(v['pid'],signal.SIGTERM)
        except ProcessLookupError: pass
    if victims:time.sleep(5)
    remaining=candidates()
    for v in remaining:
        # Recheck ownership and exact command immediately before SIGKILL.
        try:
            p=Path('/proc')/str(v['pid'])
            if p.stat().st_uid==os.getuid() and p.joinpath('cmdline').read_bytes().decode().split('\0')==v['argv']:
                os.kill(v['pid'],signal.SIGKILL)
        except (OSError,UnicodeError): pass
    event=dict(time=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),terminated=victims,killed=remaining)
    with (ROOT/'gpu-release-events.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
    print(json.dumps(event),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');p.add_argument('--watch',action='store_true');p.add_argument('--cleanup-weights',action='store_true');a=p.parse_args()
    if a.dry_run:print(json.dumps(dict(deadline='2026-10-08 09:00 Asia/Shanghai',eligible=candidates()),indent=2));raise SystemExit
    enforce()
    if a.cleanup_weights:
        try:cleanup_weights()
        except Exception as e:
            # Disk cleanup must never disable the independent GPU stop monitor.
            print('Cleanup error; GPU monitor continues:',repr(e),flush=True)
    if a.watch:
        # Independent service remains active through deadline to catch queued/restarted workers.
        while time.time()<DEADLINE+120:
            time.sleep(20);enforce()
        print('Final eligible GPU workers:',json.dumps(candidates()),flush=True)
