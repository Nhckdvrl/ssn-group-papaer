#!/usr/bin/env python3
"""Explicit derived Korean recovery: retain complete seeds and verified replay."""
import argparse
import hashlib
import json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,required=True)
args=ap.parse_args()
runs=args.root/'runs'
old=runs/'E07-qwen3-4b-korean'
new=runs/'E07-qwen3-4b-korean-seed2-recovery'
out=runs/'E07-qwen3-4b-korean-joined'
if out.exists():
    raise FileExistsError(out)
read=lambda p:[json.loads(s) for s in p.read_text().splitlines()]
partial=read(old/'seed2.jsonl'); replay=read(new/'seed2.jsonl')
assert len(replay)==300
assert all(a['item_id']==b['item_id'] and a['response']==b['response']
           and a['prediction']==b['prediction'] for a,b in zip(partial,replay))
out.mkdir()
sources=[old/'seed0.jsonl',old/'seed1.jsonl',new/'seed2.jsonl']
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources+[old/'seed2.jsonl']}
for seed,p in enumerate(sources):
    rows=read(p); assert len(rows)==300 and all(r['seed']==seed for r in rows)
    (out/f'seed{seed}.jsonl').write_bytes(p.read_bytes())
cfg=json.loads((old/'config.json').read_text())
cfg.update(derived_complete=True, derivation='two completed original seeds + full verified seed2 replay',
           source_hashes=hashes, verified_replay_prefix=len(partial),
           compute_note='Original partial wall time unavailable; recovery compute in its own config, no fabricated runtime')
(out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
print(json.dumps({'joined':str(out),'replay_matches':len(partial),'responses':900}))
