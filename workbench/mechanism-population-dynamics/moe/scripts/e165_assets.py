"""Pin a mature OLMoE annealing pair; CPU/network only, no model forwards."""
import hashlib
import json
from pathlib import Path
import shutil
import time

from huggingface_hub import HfApi, hf_hub_download

WB = Path(__file__).resolve().parents[2]
ROOT = WB / 'moe/results/e165'
CACHE = Path.home() / 'mechpop_cache/hf_olmoe_mature'
PIN = {'P': 'b99743a400844e532bec7ce4575d97a3a39dcd4d',
       'A': '6d84c48581ece794365f2b8e9cfb043c68ade9c5'}
REPO = 'allenai/OLMoE-1B-7B-0924'
FILES = ('config.json', 'generation_config.json', 'model.safetensors.index.json',
         'tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json')


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    if (ROOT / 'asset_manifest.json').exists():
        raise FileExistsError('Preserve existing source registration')
    start = time.monotonic()
    result = {'status': 'complete', 'repo': REPO, 'models': {}, 'new_training': 0,
              'no_GPU_used': True, 'new_weight_download_bytes': 0}
    for label, pin in PIN.items():
        info = HfApi().model_info(REPO, revision=pin, files_metadata=True)
        if info.sha != pin:
            raise ValueError('Public pin moved')
        siblings = {s.rfilename: s for s in info.siblings}
        view = CACHE / ('view_' + label + '_' + pin[:8])
        view.mkdir(parents=True, exist_ok=True)
        records = {}
        for name in FILES:
            origin = Path(hf_hub_download(REPO, name, revision=pin, cache_dir=CACHE))
            target = view / name
            if target.exists() and sha(target) != sha(origin):
                raise ValueError('Preserve prior source view: ' + str(target))
            if not target.exists():
                shutil.copyfile(origin, target)
            records[name] = {'path': str(target), 'sha256': sha(target),
                             'size_bytes': target.stat().st_size}
        index = json.loads((view / 'model.safetensors.index.json').read_text())
        for name in sorted(set(index['weight_map'].values())):
            item = siblings[name]
            local = Path.home() / 'mechpop_cache/hf_olmoe/main' / name
            if label == 'A' and local.is_file():
                origin = local
            else:
                origin = Path(hf_hub_download(REPO, name, revision=pin, cache_dir=CACHE))
                result['new_weight_download_bytes'] += origin.stat().st_size
            digest = sha(origin)
            if item.lfs is None or digest != item.lfs.sha256 or origin.stat().st_size != item.lfs.size:
                raise ValueError('Public LFS identity failed: ' + label + '/' + name)
            target = view / name
            if target.is_symlink() and target.resolve() != origin.resolve():
                raise ValueError('Source view points to another weight')
            if not target.exists():
                target.symlink_to(origin.resolve())
            records[name] = {'path': str(target), 'canonical': str(origin.resolve()),
                             'sha256': digest, 'LFS_sha256': item.lfs.sha256,
                             'size_bytes': origin.stat().st_size}
            print(json.dumps({'source_verified': label, 'file': name,
                              'bytes': origin.stat().st_size}), flush=True)
        result['models'][label] = {'pin': pin, 'directory': str(view), 'files': records,
                                   'weight_bytes': index['metadata']['total_size']}
    result['elapsed_CPU_network_seconds'] = time.monotonic() - start
    result['asset_script_sha256'] = sha(__file__)
    (ROOT / 'asset_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['elapsed_CPU_network_seconds'],
                      'new_weight_download_bytes': result['new_weight_download_bytes']}), flush=True)


if __name__ == '__main__':
    main()
