"""Download the pinned SST rows and run E121/E123 with a portable cache.

Frozen scientific modules remain unchanged. Cache bytes can differ with the
Arrow writer version, but text/labels/order are checked against pinned JSONL.
"""
import argparse
import hashlib
import importlib
import json
import sys
import urllib.request
from pathlib import Path

REVISION = 'e51bdcd8cd3a30da231967c1a249ba59361279a3'
SPLITS = {
    'train': ('train.jsonl', '46bde4fb5abc93ffbadfa9a9f67de17c08a2f535cfb5756c59188d070434f433', 8544),
    'validation': ('dev.jsonl', '4369df4d4229e736fa734af49b342c7d6002c4d8514d9c206a5aa26edc620b79', 1101),
    'test': ('test.jsonl', '1384216112a34f3d70b6fa210762f3399bb080410c0456ac6e54a5cb413f04b2', 2210),
}


def prepare(cache):
    from datasets import Dataset
    from datasets.arrow_writer import ArrowWriter
    cache.mkdir(parents=True, exist_ok=True)
    audits = {}
    for split, (filename, expected, n) in SPLITS.items():
        source = cache / filename
        url = f'https://huggingface.co/datasets/SetFit/sst5/resolve/{REVISION}/{filename}'
        if not source.exists():
            # Atomic installation; interrupted downloads do not become sources.
            downloaded = urllib.request.urlopen(url, timeout=90).read()
            assert hashlib.sha256(downloaded).hexdigest() == expected, (split, 'download hash')
            source.write_bytes(downloaded)
        data = source.read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected, (split, 'existing source hash')
        records = [json.loads(line) for line in data.splitlines()]
        assert len(records) == n
        path = cache / f'sst5-{split}.arrow'
        if not path.exists():
            dataset = Dataset.from_list(records)
            with ArrowWriter(features=dataset.features, path=str(path)) as writer:
                writer.write_batch(dataset.to_dict())
                writer.finalize()
        decoded = Dataset.from_file(str(path))
        assert [dict(row) for row in decoded] == records, (split, 'ordered row equality')
        audits[split] = {'rows': n, 'source_url': url, 'source_sha256': expected,
                         'arrow_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'ordered_rows_match_pinned_source': True}
    result = {'dataset': 'SetFit/sst5', 'revision': REVISION, 'splits': audits,
              'scope': 'Portable data cache only; scientific selection, scoring and seeds unchanged.'}
    (cache / 'reproduction_provenance.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache-dir', type=Path, required=True)
    ap.add_argument('--experiment', choices=['e121', 'e123'])
    args, remaining = ap.parse_known_args()
    cache = args.cache_dir.expanduser().resolve()
    result = prepare(cache)
    if args.experiment is None:
        assert not remaining, remaining
        print(json.dumps(result, indent=2))
        return
    materials = importlib.import_module('e121_sst_materials')
    materials.CACHE = cache
    module = importlib.import_module({'e121': 'e121_natural_sentiment_mechanism',
                                      'e123': 'e123_natural_source_function_policy'}[args.experiment])
    sys.argv = [module.__file__] + remaining
    module.main()


if __name__ == '__main__':
    main()
