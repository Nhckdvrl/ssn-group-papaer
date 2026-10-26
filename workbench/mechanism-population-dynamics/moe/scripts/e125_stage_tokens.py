"""Copy a fixed token manifest to node-local storage, preserving all content hashes."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    a = p.parse_args()
    source = a.manifest.resolve()
    spec = json.loads(source.read_text())
    a.destination.mkdir(parents=True, exist_ok=True)
    total = 0
    for split in ("train", "held"):
        directory = a.destination / split
        directory.mkdir(exist_ok=True)
        for i, row in enumerate(spec[split]):
            original = (source.parent / row["path"]).resolve()
            target = directory / f"file_{i:03d}.npy"
            expected = row["sha256"]
            if not target.exists() or sha(target) != expected:
                partial = target.with_suffix(".partial")
                shutil.copyfile(original, partial)
                if sha(partial) != expected:
                    raise ValueError(f"Copied content hash differs: {original}")
                partial.replace(target)
            row["origin_path"] = row.get("origin_path", str(original))
            row["path"] = str(target.resolve())
            total += target.stat().st_size
    spec["canonical_manifest"] = str(source)
    spec["canonical_manifest_sha256"] = sha(source)
    output = a.destination / "manifest.json"
    partial = output.with_suffix(".partial")
    partial.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
    partial.replace(output)
    print(json.dumps({"manifest": str(output), "copied_bytes": total}))


if __name__ == "__main__":
    main()
