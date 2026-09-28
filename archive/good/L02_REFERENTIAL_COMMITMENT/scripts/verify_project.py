"""Verify offline reproduction, source provenance, and parser tests in L02 only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(args):
    result = subprocess.run([sys.executable, '-B', *args], cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return {'command': args, 'exit_code': result.returncode, 'output': result.stdout + result.stderr}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    report_path = ROOT / 'experiments/E000_data_audit/verification.json'
    if report_path.exists():
        raise FileExistsError(report_path)
    checks = [run(['-m', 'unittest', 'discover', '-s', 'tests', '-v']),
              run(['scripts/extract_training.py', '--verify-existing']),
              run(['scripts/build_review_packet.py'])]
    reproduction = run(['scripts/run_data_audit.py', '--run-id', args.run_id])
    original = ROOT / 'runs/E000_20260908_v1'
    replay = ROOT / 'runs' / args.run_id
    original_manifest = json.loads((original / 'manifest.json').read_text())
    for name, expected in original_manifest['artifacts'].items():
        if digest(original / name) != expected:
            raise ValueError(f'Original artifact changed: {name}')
    compared = {name: digest(original / name) == digest(replay / name)
                for name in original_manifest['artifacts']}
    if not all(compared.values()):
        raise ValueError(f'Reproduction differs: {compared}')
    provenance = []
    manifests = sorted((ROOT / 'data').glob('*manifest.json')) + sorted((ROOT / 'literature').glob('manifest*.json'))
    for manifest_path in manifests:
        for record in json.loads(manifest_path.read_text()):
            if 'path' in record and 'sha256' in record:
                p = ROOT / record['path']
                if digest(p) != record['sha256']:
                    raise ValueError(f'Source hash changed: {p}')
                provenance.append(record['path'])
    report = {'checks': checks, 'reproduction_command': reproduction['command'],
              'original_artifact_hashes_valid': True, 'replayed_artifacts_identical': compared,
              'raw_source_hashes_checked': provenance,
              'model_calls': 0, 'note': 'No semantic-gold validation is implied by passing software checks.'}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'software_checks': len(checks), 'identical_artifacts': len(compared),
                      'raw_sources_verified': len(provenance), 'model_calls': 0}, indent=2))
