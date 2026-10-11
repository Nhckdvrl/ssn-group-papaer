"""Strict manifest identity, allowing only a verified empty metadata addition."""
import hashlib
import json
from pathlib import Path

from data import sha


def manifest_identity(config):
    path=Path(config['model_path'])/'manifest.json'
    current=json.loads(path.read_text())
    recorded=config['model_manifest_sha256']
    if sha(path)!=recorded:
        # A downloader revision added this EMPTY field to three completed models.
        # Reconstruct the complete old bytes, including every file revision/hash;
        # filenames or model names alone never authorize merging predictions.
        assert current.get('excluded_duplicate_original_formats')==[], 'Model manifest changed beyond an empty metadata addition'
        old=dict(current);old.pop('excluded_duplicate_original_formats')
        old_digest=hashlib.sha256((json.dumps(old,indent=2)+'\n').encode()).hexdigest()
        assert old_digest==recorded, 'Recorded manifest cannot be reconstructed exactly'
    normalized=dict(current)
    if normalized.get('excluded_duplicate_original_formats')==[]:
        normalized.pop('excluded_duplicate_original_formats')
    return hashlib.sha256((json.dumps(normalized,indent=2)+'\n').encode()).hexdigest()
