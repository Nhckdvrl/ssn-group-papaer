"""Wait for every E70 item status; empty queue cannot produce a scientific map."""
import json
from pathlib import Path
import subprocess
import sys
import time
from data import sha

root=Path(sys.argv[1]);scope=json.loads((root/'scope-v1.json').read_text());assert scope['distinct_packets']>0
while True:
    try:s=json.loads((root/'step5/summary.json').read_text());ready=s['items']==scope['distinct_packets'] and s['data_sha256']==scope['packet_data_sha256']
    except (OSError,json.JSONDecodeError):ready=False
    if ready:break
    time.sleep(10)
out=root/'atomic-repair-map-v1.json'
subprocess.run([sys.executable,str(Path(__file__).with_name('analyze_atomic_repair_footprints.py')),'--root',str(root),'--out',str(out)],check=True)
(root/'complete-map-v1.json').write_text(json.dumps(dict(path=str(out),sha256=sha(out)),indent=2)+'\n');print('E70 full semantic footprint ready',flush=True)
