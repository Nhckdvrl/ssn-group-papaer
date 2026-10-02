"""Pinned official pair: only Transformers index shards, no duplicate consolidated weights."""
import argparse,json,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import snapshot_download

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);a=ap.parse_args()
manifest=json.loads((a.root/'models/mistral-stage-manifest.json').read_text())

def download(m):
    p=a.root/'models'/m['id'].split('/')[-1]
    for attempt in range(3):
        try:
            snapshot_download(m['id'],revision=m['sha'],local_dir=p,max_workers=2,
                allow_patterns=['*.json','*.jinja','tokenizer.model*','*.txt','README.md'])
            index=p/'model.safetensors.index.json'
            files=sorted(set(json.loads(index.read_text())['weight_map'].values())) if index.exists() else ['model.safetensors']
            assert all(x.endswith('.safetensors') and 'consolidated' not in x for x in files)
            snapshot_download(m['id'],revision=m['sha'],local_dir=p,max_workers=2,allow_patterns=files)
            assert all((p/f).is_file() and (p/f).stat().st_size>0 for f in files)
            (p/'DOWNLOAD_COMPLETE.json').write_text(json.dumps({'model':m['id'],'revision':m['sha'],
                'selected_weight_files':files,'excluded_duplicate_consolidated':True},indent=2))
            print(json.dumps({'download_complete':m['id']}),flush=True);return
        except Exception as e:
            print(json.dumps({'model':m['id'],'attempt':attempt+1,'error_type':type(e).__name__}),flush=True)
            if attempt==2:raise
            time.sleep(5*(attempt+1))

with ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(download,manifest))
