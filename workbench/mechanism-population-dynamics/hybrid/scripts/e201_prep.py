#!/usr/bin/env python3
"""E201 data: tokenize one FineWeb-Edu shard with the OLMo dolma2 tokenizer (same as E194, so its items are reused),
documents joined by <|endoftext|> (100257), written as a flat uint32 memmap.
Usage: e201_prep.py PARQUET TOKENIZER_DIR OUT_BIN [MAX_TOKENS]"""
import sys
import time

import numpy as np
import pyarrow.parquet as pq
from transformers import AutoTokenizer

EOS = 100257


def main():
    src, tokdir, out = sys.argv[1:4]
    max_tok = int(sys.argv[4]) if len(sys.argv) > 4 else 600_000_000
    tok = AutoTokenizer.from_pretrained(tokdir)
    eos = tok.eos_token_id if tok.eos_token_id is not None else EOS
    pf = pq.ParquetFile(src)
    buf = np.lib.format.open_memmap(out, mode="w+", dtype=np.uint32, shape=(max_tok,))
    n, t0 = 0, time.time()
    for rg in range(pf.num_row_groups):
        texts = pf.read_row_group(rg, columns=["text"]).column("text").to_pylist()
        for i in range(0, len(texts), 1000):
            enc = tok(texts[i:i + 1000], add_special_tokens=False)["input_ids"]
            for ids in enc:
                ids = ids + [eos]
                k = min(len(ids), max_tok - n)
                buf[n:n + k] = ids[:k]
                n += k
                if n >= max_tok:
                    break
            if n >= max_tok:
                break
        print(f"row group {rg}: {n/1e6:.1f}M tokens, {time.time()-t0:.0f}s", flush=True)
        if n >= max_tok:
            break
    buf.flush()
    import json
    json.dump({"n_tokens": int(n)}, open(out.replace(".npy", ".json"), "w"))
    print("DONE", n)


if __name__ == "__main__":
    main()
