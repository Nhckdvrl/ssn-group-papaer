#!/usr/bin/env python3
"""Copy fixed HF snapshots from shared storage to local NVMe, verify every byte hash."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time


def resolve_local_checkpoint(checkpoint, root='/var/tmp/ssn-game-npc-d/models/local_snapshots'):
    """Use only a completed, source-matched local mirror; otherwise retain the requested path."""
    local=Path(root)/Path(checkpoint).name;manifest=local/'LOCAL_MIRROR.json'
    if manifest.exists():
        try:value=json.loads(manifest.read_text())
        except json.JSONDecodeError:return str(checkpoint),None
        if value.get('complete') and value.get('source_snapshot')==os.path.abspath(checkpoint):
            if not all((local/f['name']).stat().st_size==f['bytes'] for f in value['files']):
                raise ValueError('Local weight mirror changed size')
            return str(local),value
    return str(checkpoint),None


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--root',required=True);a=p.parse_args()
    source=Path(a.source);root=Path(a.root);root.mkdir(parents=True,exist_ok=True)
    dest=root/source.name;dest.mkdir(exist_ok=False);files=[];start=time.monotonic()
    for src in sorted(source.iterdir(),key=lambda f:f.stat().st_size if f.is_file() else 0):
        if not src.is_file():continue
        tmp=dest/(src.name+'.partial');h=hashlib.sha256();n=0;tick=time.monotonic()
        with src.open('rb') as inp,tmp.open('xb') as out:
            try:os.posix_fadvise(inp.fileno(),0,0,os.POSIX_FADV_SEQUENTIAL)
            except (AttributeError,OSError):pass
            while True:
                block=inp.read(16*1024*1024)
                if not block:break
                out.write(block);h.update(block);n+=len(block)
                if time.monotonic()-tick>30:
                    print(src.name,'copied bytes',n,'elapsed_s',round(time.monotonic()-start,1),flush=True);tick=time.monotonic()
            out.flush();os.fsync(out.fileno())
        # HF LFS blob names encode SHA256; verify against the release object, too.
        expected=src.resolve().name
        if len(expected)==64 and h.hexdigest()!=expected:raise ValueError('Source LFS checksum mismatch')
        with tmp.open('rb') as check:
            if hashlib.file_digest(check,'sha256').hexdigest()!=h.hexdigest():raise ValueError('Destination checksum mismatch')
        final=dest/src.name;tmp.rename(final);files.append(dict(name=src.name,bytes=n,sha256=h.hexdigest()))
        print('VERIFIED',src.name,n,flush=True)
    result=dict(source_snapshot=str(source.resolve()),revision=source.name,complete=True,files=files,wall_s=time.monotonic()-start)
    temporary=dest/'LOCAL_MIRROR.json.partial'
    temporary.write_text(json.dumps(result,indent=2)+'\n');temporary.rename(dest/'LOCAL_MIRROR.json')
    print('READY',dest,flush=True)


if __name__=='__main__':main()
