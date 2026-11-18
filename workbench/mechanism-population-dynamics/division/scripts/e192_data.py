#!/usr/bin/env python3
"""E192 (card: division/experiments/E192-frozen-router-intervention.md): training / held-out data for the FLAME-MoE-290M
continued-training arms, all node-local.
  tokenize  : DCLM-baseline-1.0 shards global-shard_10_of_10/local-shard_9_of_10/shard_000000{00..23} (jsonl.zst, field
              "text"), pythia-12b tokenizer (add_special_tokens=False), EOD = <|endoftext|> (id 0) appended after every
              document (Megatron --append-eod convention; FLAME's exact preprocessing not checked), uint16 per shard.
  pools     : shards concatenated in shard order; the LAST shard (23) is reserved: its first EVAL_TOK tokens = held-out DCLM
              eval stream (never trained on by any arm).  Training pools: P1 = first POOL_TOK tokens of shards 0.., P2 = the
              next POOL_TOK tokens.  POOL_TOK = 540 iters x 1024 sequences x 2048 + 1.  A training sequence = window
              [j*2048, j*2048 + 2049) of a pool (Megatron-style packing across document boundaries, causal attention across
              documents, no EOD loss mask); the order of the 552,960 windows is a permutation drawn from the data seed.
  wikitext  : wikitext-103-raw-v1 test (HF Salesforce/wikitext parquet), lines joined as in the raw file, one stream.
usage: e192_data.py tokenize|pools|wikitext --root /tmp/xiang_e192"""
import argparse, glob, io, json, os, sys, time
import numpy as np

SEQ, GB, NIT = 2048, 1024, 540
POOL_TOK = NIT * GB * SEQ + 1
EVAL_TOK = 1024 * SEQ + 1           # 1024 eval windows = 2.10M tokens


def tok_shard(args):
    path, out, tokdir = args
    if os.path.exists(out):
        return out, int(os.path.getsize(out) // 2)
    os.environ["RAYON_NUM_THREADS"] = "2"
    import zstandard
    from tokenizers import Tokenizer
    tk = Tokenizer.from_file(os.path.join(tokdir, "tokenizer.json"))
    eod = tk.token_to_id("<|endoftext|>")
    assert eod == 0
    chunks, buf = [], []
    with open(path, "rb") as fh:
        rd = io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(fh), encoding="utf-8")
        for line in rd:
            buf.append(json.loads(line)["text"])
            if len(buf) == 2000:
                for e in tk.encode_batch(buf, add_special_tokens=False):
                    chunks.append(np.array(e.ids + [eod], np.uint16))
                buf = []
        if buf:
            for e in tk.encode_batch(buf, add_special_tokens=False):
                chunks.append(np.array(e.ids + [eod], np.uint16))
    arr = np.concatenate(chunks)
    arr.tofile(out + ".tmp"); os.replace(out + ".tmp", out)
    return out, len(arr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd"); ap.add_argument("--root", default="/tmp/xiang_e192"); ap.add_argument("--procs", type=int, default=12)
    a = ap.parse_args()
    R = a.root; D = f"{R}/dclm"; os.makedirs(f"{D}/tok", exist_ok=True)
    if a.cmd == "tokenize":
        from multiprocessing import Pool
        raws = sorted(glob.glob(f"{D}/raw/shard_*_processed.jsonl.zst"))
        assert len(raws) == 24, len(raws)
        jobs = [(p, f"{D}/tok/{os.path.basename(p).split('_processed')[0]}.u16", f"{R}/tok/pythia12b") for p in raws]
        t0 = time.time()
        with Pool(a.procs) as pool:
            for out, n in pool.imap_unordered(tok_shard, jobs):
                print(f"[{time.time() - t0:.0f}s] {out} {n / 1e6:.1f}M tokens", flush=True)
    elif a.cmd == "pools":
        toks = sorted(glob.glob(f"{D}/tok/shard_*.u16"))
        assert len(toks) == 24
        ev = np.fromfile(toks[-1], np.uint16)[:EVAL_TOK]
        assert len(ev) == EVAL_TOK
        ev.tofile(f"{D}/eval_dclm.u16")
        need = 2 * POOL_TOK; parts, have = [], 0
        for p in toks[:-1]:
            x = np.fromfile(p, np.uint16); parts.append(x); have += len(x)
            if have >= need: break
        assert have >= need, f"only {have} tokens in shards 0..22, need {need}"
        allt = np.concatenate(parts)
        allt[:POOL_TOK].tofile(f"{D}/pool_P1.u16"); allt[POOL_TOK:2 * POOL_TOK].tofile(f"{D}/pool_P2.u16")
        info = {"pool_tokens": POOL_TOK, "eval_tokens": EVAL_TOK, "shards_used": [os.path.basename(p) for p in toks[:len(parts)]],
                "eval_shard": os.path.basename(toks[-1]), "tokens_available": int(have),
                "md5_head": {k: __import__("hashlib").md5(np.fromfile(f"{D}/{k}.u16", np.uint16, count=1 << 20).tobytes()).hexdigest()
                             for k in ("pool_P1", "pool_P2", "eval_dclm")}}
        json.dump(info, open(f"{D}/pools.json", "w"), indent=1); print(info)
    elif a.cmd == "wikitext":
        import pyarrow.parquet as pq
        from tokenizers import Tokenizer
        p = f"{R}/wikitext/test-00000-of-00001.parquet"
        lines = pq.read_table(p).column("text").to_pylist()
        text = "".join(lines)
        tk = Tokenizer.from_file(f"{R}/tok/pythia12b/tokenizer.json")
        ids = np.array(tk.encode(text, add_special_tokens=False).ids, np.uint16)
        ids.tofile(f"{D}/eval_wikitext.u16")
        print("wikitext-103 test", len(lines), "lines", len(ids), "tokens")
    elif a.cmd == "evalshard3":
        # p6 check (11-18, card 追加臂): held-out stream from a third DCLM global shard (not 03 = official training, not
        # 10 = our pools / eval): global-shard_05_of_10/local-shard_0_of_10/shard_00000000, same tokenisation + EOD
        import subprocess
        raw = f"{D}/raw3/shard_00000000_processed.jsonl.zst"; os.makedirs(os.path.dirname(raw), exist_ok=True)
        if not os.path.exists(raw):
            url = "https://huggingface.co/datasets/mlfoundations/dclm-baseline-1.0/resolve/main/global-shard_05_of_10/local-shard_0_of_10/shard_00000000_processed.jsonl.zst"
            assert subprocess.run(["curl", "-sSL", "--retry", "5", "--max-time", "3600", "-o", raw + ".part", url]).returncode == 0
            os.replace(raw + ".part", raw)
        out, n = tok_shard((raw, f"{D}/tok3_gs05_ls0_s0.u16", f"{R}/tok/pythia12b"))
        x = np.fromfile(out, np.uint16)[:EVAL_TOK]; assert len(x) == EVAL_TOK
        x.tofile(f"{D}/eval_dclm3.u16"); print("eval_dclm3", len(x), "of", n)
    elif a.cmd == "gs03pool":
        # p6 test (round 3, 11-18): official training data = DCLM global-shard_03, local shards 1/3/6/8/9 (all 279 shards
        # each are in the official data_path).  We take global-shard_03/local-shard_1_of_10/shard_00000000..02, same
        # tokenisation + EOD, and keep the first 108 x 1024 x 2048 + 1 tokens as pool_GS03.u16.
        import subprocess
        need = 108 * GB * SEQ + 1; parts, have = [], 0
        for i in range(6):
            raw = f"{D}/raw_gs03/shard_{i:08d}_processed.jsonl.zst"; os.makedirs(os.path.dirname(raw), exist_ok=True)
            if not os.path.exists(raw):
                url = f"https://huggingface.co/datasets/mlfoundations/dclm-baseline-1.0/resolve/main/global-shard_03_of_10/local-shard_1_of_10/shard_{i:08d}_processed.jsonl.zst"
                assert subprocess.run(["curl", "-sSL", "--retry", "5", "--max-time", "3600", "-o", raw + ".part", url]).returncode == 0
                os.replace(raw + ".part", raw)
            out, n = tok_shard((raw, f"{D}/tok_gs03_ls1_s{i}.u16", f"{R}/tok/pythia12b"))
            parts.append(np.fromfile(out, np.uint16)); have += n; print(out, n, have, flush=True)
            if have >= need:
                break
        x = np.concatenate(parts)[:need]; assert len(x) == need
        x.tofile(f"{D}/pool_GS03.u16"); print("pool_GS03", len(x))
    else:
        raise SystemExit(a.cmd)


if __name__ == "__main__":
    main()
