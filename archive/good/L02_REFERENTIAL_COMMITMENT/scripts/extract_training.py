"""Reproduce the selected original release members from the archived outer tar."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def extract(archive_path, output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = []
    with tarfile.open(archive_path) as outer:
        data = outer.extractfile('Semeval2010Task10TrainingFN.tar.gz').read()
    with tarfile.open(fileobj=io.BytesIO(data)) as inner:
        for member in inner:
            if not member.isfile() or not ('/tiger/' in member.name or
                    'guideline' in member.name.lower() or 'readme' in member.name.lower()):
                continue
            destination = (output / member.name).resolve()
            if not destination.is_relative_to(output):
                raise ValueError(f'Unsafe archive path: {member.name}')
            content = inner.extractfile(member).read()
            digest = hashlib.sha256(content).hexdigest()
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
                    raise ValueError(f'Existing member differs: {member.name}')
            else:
                with destination.open('xb') as handle:
                    handle.write(content)
            records.append({'member': member.name, 'bytes': len(content), 'sha256': digest})
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-existing', action='store_true')
    args = parser.parse_args()
    base = ROOT / 'data/raw/semeval2010'
    records = extract(base / 'train.zip', base / 'extracted')
    manifest = base / 'train_members_manifest.json'
    if manifest.exists():
        if records != json.loads(manifest.read_text()):
            raise ValueError('Member manifest differs')
    else:
        manifest.write_text(json.dumps(records, indent=2) + '\n')
    print(f'Verified {len(records)} members; original bytes preserved')
