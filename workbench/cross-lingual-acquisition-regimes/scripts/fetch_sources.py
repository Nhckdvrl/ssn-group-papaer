"""Cache the primary papers and extract searchable PDF text."""
import argparse
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = {
    "jgp": "https://aclanthology.org/2025.acl-long.1602.pdf",
    "monoweb": "https://aclanthology.org/2026.acl-long.1706.pdf",
    "openseal": "https://arxiv.org/pdf/2602.02266",
    "transwebedu": "https://aclanthology.org/2025.emnlp-main.1426.pdf",
    "false_friends": "https://aclanthology.org/2025.findings-emnlp.1153.pdf",
    "macaroni": "https://arxiv.org/pdf/2609.30535",
    "bilingual_babylm": "https://arxiv.org/pdf/2603.29552",
    "translation_multilinguality": "https://openreview.net/pdf/4d0a5f089a519b7f2490ec759292c2c55ec7fa91.pdf",
    "nmT5": "https://aclanthology.org/2021.acl-short.87.pdf",
    "rosetta_unification": "https://arxiv.org/pdf/2508.11017",
    "token_alignment_heads": "https://proceedings.iclr.cc/paper_files/paper/2026/file/5ae1e0307c6df2ec27904c3615a86658-Paper-Conference.pdf",
    "limited_utility_parallel": "https://arxiv.org/pdf/2603.29026v1",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--papers", nargs="+", choices=sorted(PAPERS), default=list(PAPERS))
    args = parser.parse_args()
    folder = ROOT / "sources"
    folder.mkdir(exist_ok=True)
    manifest = folder / "manifest.json"
    records = {r["paper"]: r for r in json.loads(manifest.read_text())} if manifest.exists() else {}
    for name in args.papers:
        url = PAPERS[name]
        pdf = folder / f"{name}.pdf"
        try:
            if not pdf.exists():
                request = urllib.request.Request(url, headers={"User-Agent": "research-source-audit/1.0"})
                with urllib.request.urlopen(request, timeout=90) as response:
                    payload = response.read()
                if not payload.startswith(b"%PDF"):
                    raise ValueError("Response is not a PDF")
                pdf.write_bytes(payload)
            subprocess.run(["pdftotext", "-layout", str(pdf), str(pdf.with_suffix(".txt"))], check=True)
            record = {"paper": name, "url": url, "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "status": "ok"}
        except Exception as error:
            record = {"paper": name, "url": url, "status": "failed", "error": str(error)}
        records[name] = record
        print(json.dumps(record), flush=True)
    manifest.write_text(json.dumps(list(records.values()), indent=2) + "\n")


if __name__ == "__main__":
    main()
