#!/usr/bin/env python3
"""Record checksums for ignored CPC18 raw artifacts without committing them."""

import hashlib
import json
from pathlib import Path

from cpc18_common import CONFIG, ROOT


def describe(path):
    digest = hashlib.sha256()
    rows = 0
    with path.open("rb") as handle:
        for line in handle:
            digest.update(line)
            rows += 1
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "rows": rows,
        "sha256": digest.hexdigest(),
    }


def main():
    result_dir = ROOT / CONFIG["result_dir"]
    paths = sorted((result_dir / "raw").glob("*.jsonl"))
    paths += sorted((result_dir / "raw" / "control").glob("*.jsonl"))
    manifest = {
        "note": "Raw JSONL artifacts are intentionally excluded from Git.",
        "artifacts": [describe(path) for path in paths],
    }
    output = result_dir / "raw_manifest.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
