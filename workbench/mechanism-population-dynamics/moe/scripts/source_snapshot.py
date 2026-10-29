"""Read frozen historical code from Git; restore its original paths only while needed.

The numerical files are never rewritten. A shared lock serializes restoration
across nodes, and only unchanged files created by this context are removed.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import warnings

WB = Path(__file__).resolve().parents[2]
INDEX = Path(__file__).with_name('frozen_sources.json')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def index():
    data = json.loads(INDEX.read_text())
    if data['version'] != 1:
        raise ValueError('Unsupported historical source index')
    for name in data['files']:
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or path.parts[:2] not in (
                ('moe', 'scripts'), ('heads', 'scripts')):
            raise ValueError('Invalid historical source path: '+name)
    return data


def contents(records):
    """Retrieve exact blobs in one offline Git process, checking length and SHA."""
    repo = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=WB, text=True).strip()
    proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=repo,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        for name, record in records.items():
            proc.stdin.write((record['blob']+'\n').encode()); proc.stdin.flush()
            header = proc.stdout.readline().decode().strip().split()
            if len(header) != 3 or header[1] != 'blob':
                raise RuntimeError('Frozen Git blob unavailable for '+name+
                                   '; fetch the recorded snapshot commit or use the sealed source package in ASSETS.md')
            size = int(header[2]); value = proc.stdout.read(size)
            if proc.stdout.read(1) != b'\n' or size != record['bytes'] or len(value) != size:
                raise ValueError('Historical source length differs: '+name)
            if hashlib.sha256(value).hexdigest() != record['sha256']:
                raise ValueError('Historical source SHA differs: '+name)
            yield name, record, value
    finally:
        proc.stdin.close(); proc.stdout.close()
        if proc.poll() is None:
            proc.terminate()
        proc.wait()


@contextmanager
def restored():
    data = index()
    token = hashlib.sha256(str(WB).encode()).hexdigest()[:16]
    cache = Path.home()/'mechpop_cache/source_snapshots'; cache.mkdir(parents=True, exist_ok=True)
    created = []
    with (cache/(token+'.lock')).open('a+') as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError('Another reproduction is using the historical source paths; no files changed') from error
        missing = {}
        # Validate every existing path before creating any source file.
        for name, record in data['files'].items():
            path = WB/name
            if path.is_symlink():
                raise ValueError('Historical code must be a real file, not a link: '+name)
            if path.exists():
                if not path.is_file() or sha(path) != record['sha256']:
                    raise ValueError('Existing file conflicts with frozen source; left untouched: '+name)
            else:
                missing[name] = record
        try:
            for name, record, value in contents(missing):
                path = WB/name; path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    created.append((path, record['sha256']))
                    stream.write(value)
                path.chmod(record['mode'])
            yield {'snapshot_commit': data['snapshot_commit'], 'temporarily_restored': len(created)}
        finally:
            for path, expected in reversed(created):
                if path.is_file() and not path.is_symlink() and sha(path) == expected:
                    path.unlink()
                elif path.exists():
                    warnings.warn('Preserved a modified historical source file: '+str(path))


def describe(name=None):
    data = index(); records = data['files']
    if name:
        matches = {k:v for k,v in records.items() if k == name or Path(k).name == name}
        if not matches:
            raise ValueError('No historical source named '+name)
        return {'snapshot_commit': data['snapshot_commit'], 'files': matches}
    return {'snapshot_commit': data['snapshot_commit'],
            'files': len(records), 'bytes': sum(v['bytes'] for v in records.values()),
            'groups': {g:sum(v['group'] == g for v in records.values()) for g in ('moe', 'heads')},
            'lookup': 'reproduce.py sources --name e166_core.py',
            'export': 'reproduce.py sources --export /absolute/path/outside/repository'}


def export(destination):
    root = Path(destination).expanduser().resolve()
    repo = Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=WB,text=True).strip())
    if root == repo or repo in root.parents:
        raise ValueError('Export historical source outside the current repository')
    data = index(); created = 0
    for name, record, value in contents(data['files']):
        path = root/name; path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if path.is_symlink() or not path.is_file() or sha(path) != record['sha256']:
                raise FileExistsError('Refuse to overwrite '+str(path))
            continue
        with path.open('xb') as stream:
            stream.write(value)
        path.chmod(record['mode']); created += 1
    return {'snapshot_commit': data['snapshot_commit'], 'destination': str(root), 'exported': created,
            'scope': 'Source inspection/export only. Use the repository reproduction entry for results.'}
