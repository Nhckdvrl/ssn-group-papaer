"""P0 evaluation text: seven domains as in Li & Merrill (2606.20936) §3 / App. A.1.

Writes data/docs_<domain>.jsonl ({"doc": i, "text": ...}) and results/data_manifest.json
(source repo, file, sha256, docs, chars). Sampling is seeded; ~TARGET_CHARS per domain
(~1M Olmo tokens at ~4 chars/token for prose; code is denser).
"""
import hashlib, json, os, random
import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_CHARS = 4_000_000
SOURCES = {
    "pg19": ("emozilla/pg19-test", "data/test-00000-of-00001-29a571947c0b5ccc.parquet", "text", None),
    "ccnews": ("vblagoje/cc_news", "plain_text/train-00000-of-00005.parquet", "text", None),
    "wikipedia": ("wikimedia/wikipedia", "20231101.en/train-00000-of-00041.parquet", "text", None),
    "arxiv": ("ccdv/arxiv-summarization", "document/test-00000-of-00001.parquet", "article", None),
    "python": ("codeparrot/github-code-clean", "data/train-00000-of-00880.parquet", "code", "Python"),
    "html": ("codeparrot/github-code-clean", "data/train-00000-of-00880.parquet", "code", "HTML"),
    "latex": ("codeparrot/github-code-clean", "data/train-00000-of-00880.parquet", "code", "TeX"),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(f"{ROOT}/data", exist_ok=True)
    manifest, cache = {}, {}
    for dom, (repo, fn, col, lang) in SOURCES.items():
        path = hf_hub_download(repo, fn, repo_type="dataset")
        if path not in cache:
            cache[path] = pd.read_parquet(path)
        df = cache[path]
        if lang:
            df = df[df["language"] == lang]
        texts = [t for t in df[col].tolist() if isinstance(t, str) and len(t) >= 500]
        rng = random.Random(f"shape_olmo-{dom}")
        rng.shuffle(texts)
        out, n = [], 0
        for t in texts:
            if n >= TARGET_CHARS:
                break
            t = t[:TARGET_CHARS // 4] if dom == "pg19" else t  # cap one book at 1/4 of the budget
            out.append(t); n += len(t)
        with open(f"{ROOT}/data/docs_{dom}.jsonl", "w") as f:
            for i, t in enumerate(out):
                f.write(json.dumps({"doc": i, "text": t}) + "\n")
        manifest[dom] = dict(repo=repo, file=fn, sha256=sha256(path), column=col, language=lang,
                             pool=len(texts), docs=len(out), chars=n)
        print(dom, manifest[dom])
    json.dump(manifest, open(f"{ROOT}/results/data_manifest.json", "w"), indent=1)


if __name__ == "__main__":
    main()
