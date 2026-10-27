#!/usr/bin/env python3
"""Sequentially stage pinned, verified native model files onto temporary NVMe."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import time
import uuid

BASE = Path(__file__).resolve().parents[2]
ROOT = Path('/tmp/xiang-moe-20261028/mature_emo_pab')
DETAIL = Path('/home/xiang/mechpop_cache/emo_local_staging_20261028.json')
REPORT = BASE / 'moe/results/native_local_staging_2026-10-28.json'
RESERVE = 64_000_000_000
CHUNK = 8 * 1024 * 1024


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(CHUNK), b''):
            h.update(b)
    return h.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.partial')
    with tmp.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main():
    started = time.monotonic()
    manifests = [BASE / 'moe/results/e154/asset_manifest.json', BASE / 'moe/results/e150/asset_manifest.json']
    d1, d2 = [json.loads(p.read_text()) for p in manifests]
    models = {'P': d1['model'], 'A': d2['models']['StdMoE_1b14b_1T'], 'B': d2['models']['StdMoE_1b14b_1T_EmoAnnealed']}
    ROOT.mkdir(parents=True, exist_ok=True)
    entries = []
    for label, model in models.items():
        for name, info in sorted(model['files'].items()):
            rel = Path(name)
            if rel.is_absolute() or '..' in rel.parts:
                raise ValueError('unsafe manifest path')
            if info['public_lfs_sha256'] and info['public_lfs_sha256'] != info['sha256']:
                raise ValueError('LFS digest mismatch')
            entries.append((label, name, info))
    pending = sum(x[2]['size_bytes'] for x in entries)
    result = {'status': 'running', 'host': socket.gethostname(), 'temporary_local_root': str(ROOT), 'source_nfs_retained': True, 'reserve_bytes': RESERVE, 'source_manifests': {str(p): digest(p) for p in manifests}, 'models': {k: {'repo_id': v['repo_id'], 'revision': v['revision'], 'source_root': v['path'], 'execution_root': str(ROOT / k), 'files': {}} for k, v in models.items()}}
    copied = reused = 0
    try:
        for label, model in models.items():
            print(f'{label}: staging {model["repo_id"]}@{model["revision"]}', flush=True)
            for lab, name, info in (x for x in entries if x[0] == label):
                target = ROOT / lab / name
                target.parent.mkdir(parents=True, exist_ok=True)
                expected = info['sha256']; size = info['size_bytes']
                if target.exists() or target.is_symlink():
                    if target.is_symlink() or not target.is_file() or target.stat().st_size != size or digest(target) != expected:
                        raise RuntimeError(f'existing destination differs: {target}')
                    reused += size
                    method = 'verified_existing'
                else:
                    free = shutil.disk_usage(ROOT).free
                    if free < pending + RESERVE:
                        raise RuntimeError(f'insufficient free space: {free} < {pending}+{RESERVE}')
                    partial = target.with_name(target.name + '.' + uuid.uuid4().hex + '.partial')
                    h = hashlib.sha256(); count = 0
                    try:
                        with Path(info['path']).open('rb') as src, partial.open('xb') as dst:
                            while True:
                                data = src.read(CHUNK)
                                if not data: break
                                if shutil.disk_usage(ROOT).free < RESERVE + len(data):
                                    raise RuntimeError('free space fell below reserve during copy')
                                dst.write(data); h.update(data); count += len(data)
                            dst.flush(); os.fsync(dst.fileno())
                        if count != size or h.hexdigest() != expected or digest(partial) != expected:
                            raise RuntimeError(f'copy verification failed: {name}')
                        os.link(partial, target)  # exclusive publication; never replace an existing file
                        partial.unlink()
                    except BaseException:
                        if partial.exists(): partial.unlink()
                        raise
                    copied += size
                    method = 'copied_and_independently_rehashed'
                pending -= size
                result['models'][lab]['files'][name] = {'source_path': info['path'], 'resolved_source_path': str(Path(info['path']).resolve()), 'local_path': str(target), 'size_bytes': size, 'sha256': expected, 'public_lfs_sha256': info['public_lfs_sha256'], 'verification': method}
            print(f'{label}: verified', flush=True)
        result['status'] = 'complete'
    except BaseException as exc:
        result['status'] = 'failed'
        result['error'] = repr(exc)
        raise
    finally:
        result.update(elapsed_cpu_io_seconds=round(time.monotonic() - started, 3), copied_bytes=copied, reused_bytes=reused, remaining_bytes=pending, final_free_bytes=shutil.disk_usage(ROOT).free, gpu_calls=0)
        write_json(DETAIL, result)
        write_json(ROOT / 'localstaging_manifest.json', result)
        write_json(REPORT, {k: v for k, v in result.items() if k != 'models'} | {'models': {k: {key: val for key, val in m.items() if key != 'files'} | {'verified_files': len(m['files'])} for k, m in result['models'].items()}, 'detailed_manifest': str(DETAIL), 'detailed_manifest_sha256': digest(DETAIL), 'note': 'Temporary NVMe staging; durable source NFS retained.'})


if __name__ == '__main__':
    main()
