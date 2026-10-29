"""Seal completed E164 sources, inputs, raw and public code without weights."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

WB = Path(__file__).resolve().parents[2]
ROOT = WB/'moe/results/e164'
RAW = Path.home()/'mechpop_cache/e164_runtime_routing'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    plan = read(ROOT/'plan.json'); manifest = read(ROOT/'manifest.json')
    end = read(ROOT/'execution_complete.json'); audit = read(ROOT/'independent_audit.json')
    if manifest['status'] != 'complete' or end['status'] != 'complete' or audit['status'] != 'passed':
        raise ValueError('Complete audited E164 execution required')
    for phase in ('chain', 'preflight', 'run'):
        state = read(ROOT/('supervision_'+phase+'.json'))
        if state['status'] != 'complete' or state['returncode'] != 0:
            raise ValueError('Successful durable terminal exit required: '+phase)
    for name in ('plan', 'manifest', 'summary', 'independent_audit'):
        if sha(ROOT/(name+'.json')) != end[name+'_sha256']:
            raise ValueError('Completed scientific artifact changed: '+name)
    for name, digest in plan['source_sha256'].items():
        if sha(WB/'moe/scripts'/name) != digest:
            raise ValueError('Frozen numerical source changed: '+name)
    commit = subprocess.check_output(['git', 'rev-parse', '--short=8', 'HEAD'], cwd=WB, text=True).strip()
    target = RAW/('run_metadata_'+commit+'.tar.gz')
    if target.exists() or (ROOT/'artifact_seal.json').exists():
        raise FileExistsError('Keep the prior E164 package and provenance')
    entries = {}
    for name in (*plan['source_sha256'], 'e164_finish.py', 'e164_plot.py', 'seal_e164.py', 'reproduce.py'):
        entries['repo/moe/scripts/'+name] = WB/'moe/scripts'/name
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix in ('.json', '.log', '.png', '.pdf') and p.name != 'artifact_seal.json':
            entries['repo/moe/results/e164/'+str(p.relative_to(ROOT))] = p
    for p in RAW.rglob('*'):
        if p.is_file() and p.suffix in ('.npz', '.jsonl', '.json', '.py', '.log'):
            entries['raw/'+str(p.relative_to(RAW))] = p
    for key in ('legacy_input', 'legacy_cal_input', 'fresh_input', 'references'):
        item = plan[key]; p = Path(item['path'])
        if sha(p) != item['sha256']:
            raise ValueError('Pinned input changed: '+key)
        entries['inputs/'+key+'/'+p.name] = p
    calibration = plan['source_records']['P']['calibration']; p = Path(calibration['path'])
    if sha(p) != calibration['sha256']:
        raise ValueError('Native real-interface reference changed')
    entries['inputs/P_calibration/'+p.name] = p
    public = {}
    for label, files in plan['public_source_files'].items():
        public[label] = {}
        for name, item in files.items():
            p = Path(item['path']).resolve()
            if not p.is_file() or sha(p) != item['sha256']:
                raise ValueError('Pinned public native source changed')
            entries['public_source/'+label+'/'+name] = p
            public[label][name] = item['sha256']
    for name in ('README.md', 'PAPER_SHAPE.md', 'RESEARCH_DIRECTION.md', 'ASSETS.md'):
        entries['repo/moe/'+name] = WB/'moe'/name
    for name in ('CLAIMS.md', 'PAIN_LOG.md', 'AGENTS.md'):
        entries['repo/'+name] = WB/name
    entries['repo/moe/experiments/E164-runtime-routing-property-transport.md'] = WB/'moe/experiments/E164-runtime-routing-property-transport.md'
    entries['repo/moe/notes/PRIMARY_READING_TRANSFER_2026-10-29.json'] = WB/'moe/notes/PRIMARY_READING_TRANSFER_2026-10-29.json'
    entries['repo/library/FUNCTIONAL_TRANSFER_AND_ROUTING_2026-10-29.md'] = WB.parents[1]/'library/themes/moe-routing/FUNCTIONAL_TRANSFER_AND_ROUTING_2026-10-29.md'
    for name in ('e150/asset_manifest.json', 'e154/asset_manifest.json'):
        entries['repo/moe/results/'+name] = WB/'moe/results'/name
    records = {name: {'path': str(p), 'sha256': sha(p), 'size_bytes': p.stat().st_size} for name, p in entries.items()}
    with tarfile.open(target, 'w:gz', dereference=True) as archive:
        for name, p in entries.items():
            archive.add(p.resolve(), arcname=name, recursive=False)
    with tarfile.open(target, 'r:gz') as archive:
        for member in archive:
            if not member.isfile() or member.issym():
                raise ValueError('Package contains an unresolved link or non-file')
            with archive.extractfile(member) as f:
                digest = hashlib.file_digest(f, 'sha256').hexdigest()
            if digest != records[member.name]['sha256']:
                raise ValueError('Package entry changed: '+member.name)
    seal = {'experiment': 'E164', 'status': 'sealed', 'result_commit': commit,
            'frozen_numerical_commit': plan['numerical_source_commit'], 'plan_sha256': sha(ROOT/'plan.json'),
            'summary_sha256': sha(ROOT/'summary.json'), 'raw': manifest['raw'],
            'source_result_package': {'path': str(target), 'sha256': sha(target), 'size_bytes': target.stat().st_size},
            'entries': records, 'public_source_materialized_sha256': public,
            'gpu_seconds_registered_timer': end['gpu_seconds'], 'new_model_weights_copied': False,
            'source_dependencies_and_original_failures_preserved': True}
    (ROOT/'artifact_seal.json').write_text(json.dumps(seal, indent=2)+'\n')
    print(json.dumps({'status': 'sealed', 'package': seal['source_result_package'], 'entries': len(entries)}, indent=2))


if __name__ == '__main__':
    main()
