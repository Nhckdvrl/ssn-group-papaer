"""Stage E12's eight public VLMEvalKit TSVs with source-pinned MD5 checks.

The OpenCompass host's TLS certificate had expired on 2026-10-02. For this
public-only fetch we permit that transport exception and require every file to
match the checksum embedded in the pinned VLMEvalKit source before use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import time
import urllib.request
from pathlib import Path


DATASETS = {
    "HallusionBench": ("VLMEval", "0c23ac0dc9ef46832d7a24504f2a0c7c"),
    "LLaVABench": ("VLMEval", "d382a093f749a697820d3dadd61c8428"),
    "MMBench": ("benchmarks/MMBench", "4115aea3383f3dd0083be6a633e0f820"),
    "MMMU_DEV_VAL": ("VLMEval", "585e8ad75e73f75dcad265dfd0417d64"),
    "MMStar": ("VLMEval", "e1ecd2140806c1b1bbf54b43372efb9e"),
    "MMVet": ("VLMEval", "748aa6d4aa9d4de798306a63718455e3"),
    "MathVista_MINI": ("VLMEval", "f199b98e178e5a2a20e7048f5dcb0464"),
    "OCRBench": ("VLMEval", "e953d98a987cc6e26ef717b61260b778"),
}


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    args.root.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    report = {}
    context = ssl._create_unverified_context()  # checksum-pinned public TSVs only
    for name, (subdir, expected) in DATASETS.items():
        dest = args.root / f"{name}.tsv"
        url = f"https://opencompass.openxlab.space/utils/{subdir}/{name}.tsv"
        if not dest.exists() or md5sum(dest) != expected:
            tmp = dest.with_suffix(".tsv.part")
            with urllib.request.urlopen(url, context=context, timeout=120) as response, tmp.open("wb") as f:
                while block := response.read(8 * 1024 * 1024):
                    f.write(block)
            found = md5sum(tmp)
            if found != expected:
                tmp.unlink(missing_ok=True)
                raise ValueError(f"{name}: MD5 {found} != source-pinned {expected}")
            tmp.replace(dest)
        report[name] = {"url": url, "bytes": dest.stat().st_size, "md5": expected}
        print(f"verified {name}: {dest.stat().st_size} bytes", flush=True)
    report["wall_seconds"] = round(time.monotonic() - start, 1)
    (args.root / "e12_eval_download.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
