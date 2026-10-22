#!/usr/bin/env python3
"""Create a byte-verified local overlay of existing inference dependencies, without upgrades."""
import argparse
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import hashlib
import json
from pathlib import Path
import shutil
import time

PACKAGES={'torch','torchvision','torchvision.libs','numpy','numpy.libs','nvidia','triton',
          'transformers','tokenizers','huggingface_hub','safetensors','accelerate','sympy','mpmath',
          'networkx','jinja2','markupsafe','requests','urllib3','certifi','charset_normalizer','idna',
          'regex','tqdm','yaml','psutil','PIL','pillow.libs','scipy','scipy.libs','sklearn',
          'scikit_learn.libs','joblib','threadpoolctl.py','typing_extensions.py','fsspec','filelock',
          'packaging','bitsandbytes'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
    p.add_argument('--venv-site',required=True);a=p.parse_args();src=Path(a.source);out=Path(a.out)
    tmp=out.with_name(out.name+'.partial');tmp.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    roots=[]
    for x in src.iterdir():
        dist=x.name.split('-',1)[0].lower()
        if x.name in PACKAGES or (x.name.endswith('.dist-info') and (dist in PACKAGES or dist.startswith('nvidia_') or dist in ['pillow','pyyaml','scikit_learn','typing_extensions','threadpoolctl'])):
            roots.append(x)
    def files():
        seen=set()
        # Do not scan tens of thousands of remote headers before copying the
        # shared libraries that current imports are waiting to read.
        for name in ['libtorch_global_deps.so','libtorch_cpu.so','libtorch_cuda.so','libtorch_python.so','libc10.so','libc10_cuda.so']:
            f=src/'torch/lib'/name;seen.add(f);yield f
        for x in sorted(roots,key=lambda x:(x.name not in ['nvidia','torch'],x.name)):
            candidates=[x] if x.is_file() else x.rglob('*')
            for f in candidates:
                if f not in seen and '__pycache__' not in f.parts and f.is_file():
                    seen.add(f);yield f
    def copy(srcfile):
        relative=srcfile.relative_to(src);dst=tmp/relative;dst.parent.mkdir(parents=True,exist_ok=True)
        h=hashlib.sha256()
        with srcfile.open('rb') as inp,dst.open('xb') as target:
            while block:=inp.read(8*1024*1024):target.write(block);h.update(block)
        shutil.copymode(srcfile,dst)
        with dst.open('rb') as check:
            if hashlib.file_digest(check,'sha256').hexdigest()!=h.hexdigest():raise ValueError('Copy mismatch: '+str(relative))
        size=dst.stat().st_size
        if size>50*1024*1024:print('VERIFIED LIBRARY',relative,size,flush=True)
        return dict(path=str(relative),bytes=size,sha256=h.hexdigest())
    records=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending=set()
        for f in files():
            pending.add(pool.submit(copy,f))
            if len(pending)>=16:
                finished,pending=wait(pending,return_when=FIRST_COMPLETED)
                records.extend(f.result() for f in finished)
                if len(records)%500<16:print('VERIFIED files',len(records),flush=True)
        records.extend(f.result() for f in pending)
    records.sort(key=lambda r:r['path'])
    manifest=dict(source=str(src),n_files=len(records),bytes=sum(r['bytes'] for r in records),files=records,
                  elapsed_s=time.monotonic()-start,package_upgrades=False,
                  note='Original dependency bytes copied; existing local PEFT/torchao are not overwritten. All files verified before .pth activation.')
    (tmp/'RUNTIME_MIRROR.json').write_text(json.dumps(manifest,indent=2)+'\n');tmp.rename(out)
    activation=Path(a.venv_site)/'game_npc_local_runtime.pth'
    temporary=activation.with_suffix('.pth.partial')
    temporary.write_text('import sys; sys.path.insert(0, '+repr(str(out))+')\n');temporary.rename(activation)
    print('ACTIVATED',out,manifest['n_files'],manifest['bytes'],flush=True)


if __name__=='__main__':main()
