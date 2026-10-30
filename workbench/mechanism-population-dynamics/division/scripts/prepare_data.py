#!/usr/bin/env python3
"""Build a source-stratified Dolma v1.7 token pool for multi-seed MoE pretraining (E167).

Streams prefixes of many compressed shards in parallel and tokenizes with the
OLMo/OLMoE tokenizer (byte-identical to OLMoE). Train and held shards are
file-disjoint. Mixture weights follow the Dolma v1.7 card (tokens x sample
proportion), as in the earlier E123 script.

Usage: prepare_data.py OUT_DIR TRAIN_TOKENS HELD_TOKENS [WORKERS]
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import requests

TOKENIZER_DIR = Path("/home/xiang/mechpop_cache/hf_olmo_dense/main")
URL_LIST = Path("/home/xiang/mechpop_cache/dolma-v1_7-urls.txt")
SEED = "e167-dolma17-v1"
SHARD_CAP = 120_000_000  # max tokens taken from one shard prefix, for diversity

ROWS = [
    ("Dolma CC", 1195.5, 50), ("Refined Web", 456.4, 100),
    ("StarCoder", 263.8, 100), ("C4", 138.4, 50),
    ("Reddit", 79.9, 100), ("Semantic Scholar", 57.2, 100),
    ("arXiv", 28.0, 100), ("StackExchange", 19.6, 100),
    ("Flan", 16.5, 100), ("CC News", 14.3, 100),
    ("OpenWebMath", 12.6, 100), ("Algebraic Stack", 12.6, 100),
    ("Project Gutenberg", 5.3, 100), ("MegaWika", 4.6, 100),
    ("Wikipedia & Wikibooks", 3.7, 200),
]
GROUP_TO_SOURCE = {
    "cc_en_head": "Dolma CC", "cc_en_middle": "Dolma CC", "cc_en_tail": "Dolma CC",
    "falcon-refinedweb-filtered": "Refined Web", "starcoder": "StarCoder",
    "c4-filtered": "C4", "reddit": "Reddit", "pes2o": "Semantic Scholar",
    "redpajama-arxiv": "arXiv", "redpajama-stackexchange": "StackExchange",
    "tulu_flan": "Flan", "cc_news_head": "CC News", "cc_news_middle": "CC News",
    "cc_news_tail": "CC News", "proof_pile_2-open_web_math": "OpenWebMath",
    "proof_pile_2-algebraic_stack": "Algebraic Stack", "books": "Project Gutenberg",
    "wikiref_megawika": "MegaWika", "wiki": "Wikipedia & Wikibooks",
}

_TOK = None


def _tok():
    global _TOK
    if _TOK is None:
        from transformers import AutoTokenizer
        _TOK = AutoTokenizer.from_pretrained(TOKENIZER_DIR, local_files_only=True, use_fast=True)
    return _TOK


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def stream(url: str, target: int, out_path: Path) -> dict:
    """Tokenize documents from the shard prefix until `target` tokens (whole docs, EOS-separated)."""
    tok = _tok()
    eos = tok.eos_token_id
    t0 = time.time()
    chunks, n, docs, batch = [], 0, 0, []

    def flush():
        nonlocal n, docs
        if not batch:
            return
        for ids in tok(batch, add_special_tokens=False)["input_ids"]:
            if n >= target:
                break
            ids.append(eos)
            chunks.append(np.asarray(ids, dtype=np.uint16))
            n += len(ids)
            docs += 1
        batch.clear()

    for attempt in range(4):
        try:
            r = requests.get(url, stream=True, timeout=(20, 120))
            r.raise_for_status()
            r.raw.decode_content = True
            with gzip.GzipFile(fileobj=r.raw, mode="rb") as g:
                for raw in g:
                    if not raw.strip():
                        continue
                    text = json.loads(raw).get("text")
                    if isinstance(text, str) and text:
                        batch.append(text)
                    if len(batch) >= 64:
                        flush()
                        if n >= target:
                            break
                flush()
            r.close()
            break
        except Exception as exc:  # retry from scratch; partial chunks discarded
            chunks, n, docs, batch = [], 0, 0, []
            if attempt == 3:
                raise RuntimeError(f"{url}: {exc}") from exc
            time.sleep(10 * (attempt + 1))
    arr = np.concatenate(chunks) if chunks else np.zeros(0, np.uint16)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(out_path, arr, allow_pickle=False)
    return {"path": str(out_path), "source_url": url, "token_count": int(arr.size), "docs": docs,
            "sha256": sha256(out_path), "seconds": round(time.time() - t0, 1)}


def main() -> int:
    out_dir = Path(sys.argv[1])
    train_tokens, held_tokens = int(float(sys.argv[2])), int(float(sys.argv[3]))
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    urls = [u.strip() for u in URL_LIST.read_text().splitlines() if u.strip()]
    groups: dict[str, list[str]] = {}
    for u in urls:
        g = u.split("/dolma-v1_7/", 1)[1].split("/", 1)[0]
        groups.setdefault(g, []).append(u)
    mix_raw = {s: t * p / 100 for s, t, p in ROWS}
    mix = {s: v / sum(mix_raw.values()) for s, v in mix_raw.items()}
    # held: one shard per group (hash-last); train: remaining shards in hash order, interleaved across groups
    held_urls, train_queue = {}, {s: [] for s, _, _ in ROWS}
    for g, items in sorted(groups.items()):
        items = sorted(items, key=lambda u: hashlib.sha256((SEED + u).encode()).hexdigest())
        s = GROUP_TO_SOURCE[g]
        if len(items) >= 2:
            held_urls.setdefault(s, []).append(items[-1])
            items = items[:-1]
        train_queue[s].extend(items)
    for s in train_queue:  # interleave CC head/middle/tail etc.
        train_queue[s].sort(key=lambda u: hashlib.sha256((SEED + "t" + u).encode()).hexdigest())

    manifest = {"seed": SEED, "tokenizer": str(TOKENIZER_DIR), "url_list_sha256": sha256(URL_LIST),
                "shard_cap": SHARD_CAP, "mix": mix, "train": [], "held": []}
    used = set()
    with ProcessPoolExecutor(workers) as pool:
        # held
        futs = {}
        for s, us in held_urls.items():
            per = math.ceil(held_tokens * mix[s] / len(us))
            for u in us:
                key = hashlib.sha256(u.encode()).hexdigest()[:10]
                futs[pool.submit(stream, u, per, out_dir / "held" / f"{key}.npy")] = ("held", s)
                used.add(u)
        # train: iterate until each source budget met
        deficit = {s: train_tokens * mix[s] for s in mix}
        pending = dict(futs)
        while True:
            for s in mix:
                inflight = sum(1 for side, ss in pending.values() if side == "train" and ss == s)
                while deficit[s] - inflight * SHARD_CAP > 0 and train_queue[s]:
                    u = train_queue[s].pop(0)
                    tgt = int(min(SHARD_CAP, deficit[s] - inflight * SHARD_CAP))
                    key = hashlib.sha256(u.encode()).hexdigest()[:10]
                    pending[pool.submit(stream, u, tgt, out_dir / "train" / f"{key}.npy")] = ("train", s)
                    used.add(u)
                    inflight += 1
            if not pending:
                break
            fut = next(as_completed(pending))
            side, s = pending.pop(fut)
            rec = fut.result()
            rec["source"] = s
            manifest[side].append(rec)
            if side == "train":
                deficit[s] -= rec["token_count"]
            print(json.dumps({"side": side, "source": s, "tokens": rec["token_count"], "sec": rec["seconds"],
                              "deficit_M": {k: round(v / 1e6) for k, v in deficit.items() if v > 0}}), flush=True)
    held_set = {r["source_url"] for r in manifest["held"]}
    assert not held_set & {r["source_url"] for r in manifest["train"]}
    manifest["train_tokens"] = sum(r["token_count"] for r in manifest["train"])
    manifest["held_tokens"] = sum(r["token_count"] for r in manifest["held"])
    manifest["unmet_deficit"] = {k: v for k, v in deficit.items() if v > 0}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))
    print("DONE", manifest["train_tokens"], manifest["held_tokens"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
