"""Fetch the ARDS selected-index file referenced by pinned Curation-Bench."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from html import unescape

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--downloader-source", type=Path, required=True)
    parser.add_argument("--dest", type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("e12_vendor_download_llava", args.downloader_source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load source downloader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    file_id = module.DEFAULTS["ARDS_SELECTION_GDRIVE_ID"]
    session = requests.Session()
    landing = session.get(
        "https://drive.google.com/uc",
        params={"export": "download", "id": file_id},
        timeout=60,
    )
    landing.raise_for_status()
    if "text/html" in landing.headers.get("content-type", ""):
        # Google's large-file virus-scan confirmation is a form with a
        # per-request uuid. The pinned vendor downloader does not handle it.
        form = re.search(r'<form[^>]*action="([^"]+)"', landing.text)
        fields = {
            key: unescape(value)
            for key, value in re.findall(
                r'<input[^>]*name="([^"]+)"[^>]*value="([^"]+)"', landing.text
            )
        }
        if form is None or fields.get("id") != file_id or fields.get("confirm") != "t":
            raise RuntimeError("Unrecognized Google Drive confirmation page")
        response = session.get(unescape(form.group(1)), params=fields, timeout=120, stream=True)
    else:
        response = landing
    response.raise_for_status()
    if "application/octet-stream" not in response.headers.get("content-type", ""):
        raise RuntimeError(f"Not a binary ARDS download: {response.headers.get('content-type')}")
    tmp = args.dest.with_suffix(args.dest.suffix + ".part")
    with tmp.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            handle.write(chunk)
    expected_length = int(response.headers.get("content-length", "0"))
    if expected_length and tmp.stat().st_size != expected_length:
        raise RuntimeError(f"ARDS download incomplete: {tmp.stat().st_size} != {expected_length}")
    tmp.replace(args.dest)
    raw = args.dest.read_bytes()
    rows = json.loads(raw)
    if not isinstance(rows, list) or not rows or "global_id" not in rows[0]:
        raise ValueError("Downloaded ARDS file is not a nonempty global_id list")
    report = {
        "source": f"gdrive://{module.DEFAULTS['ARDS_SELECTION_GDRIVE_ID']}",
        "source_code": str(args.downloader_source),
        "path": str(args.dest),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "rows": len(rows),
        "unique_global_ids": len({str(r["global_id"]) for r in rows}),
    }
    out = args.dest.with_suffix(".manifest.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
