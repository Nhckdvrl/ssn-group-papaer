"""Build the frozen L19 NQ pair set. Cutoffs come from DATA_AND_GOLD.md and are not
adjustable after any result is seen.

Shards are processed in parallel but results are concatenated in shard order and the
first N_TARGET are kept, so the output is identical to a serial scan.
"""
import sys, glob, json, hashlib, os
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from nq_extract import extract
import pyarrow.parquet as pq

MODEL       = "princeton-nlp/Llama-3-8B-ProLong-512k-Base"
MAX_SUPPORT = 512
MIN_PAGE    = 8000
MAX_PAGE    = 24000
N_TARGET    = 10000
OUT         = "data/nq_pairs.jsonl"
_TOKZ = None


def tokz():
    global _TOKZ
    if _TOKZ is None:
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        from transformers import AutoTokenizer
        _TOKZ = AutoTokenizer.from_pretrained(MODEL)
    return _TOKZ


def do_shard(f):
    t, seen, out = tokz(), 0, []
    for b in pq.ParquetFile(f).iter_batches(batch_size=64):
        for r in b.to_pylist():
            seen += 1
            e = extract(r)
            if e is None: continue
            ns = len(t(e["support"], add_special_tokens=False)["input_ids"])
            if ns > MAX_SUPPORT: continue
            np_ = len(t(e["page"], add_special_tokens=False)["input_ids"])
            if not (MIN_PAGE <= np_ <= MAX_PAGE): continue
            e["tok_support"], e["tok_page"] = ns, np_
            out.append(e)
    return seen, out


def main():
    files = sorted(glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/datasets--google-research-datasets--natural_questions"
        "/snapshots/*/default/train-*.parquet")))
    print(f"{len(files)} shards", flush=True)
    seen = kept = 0
    with open(OUT, "w") as w, ProcessPoolExecutor(int(os.environ.get("NPROC", 16))) as ex:
        for i, (s, rows) in enumerate(ex.map(do_shard, files)):
            seen += s
            for e in rows:
                if kept >= N_TARGET: break
                w.write(json.dumps(e) + "\n"); kept += 1
            if i % 10 == 0 or kept >= N_TARGET:
                print(f"  shard {i}: seen={seen} kept={kept}", flush=True)
            if kept >= N_TARGET: break
    man = dict(model=MODEL, max_support=MAX_SUPPORT, min_page=MIN_PAGE, max_page=MAX_PAGE,
               n_target=N_TARGET, n_kept=kept, n_raw_scanned=seen, yield_rate=kept/seen,
               sha256=hashlib.sha256(open(OUT, "rb").read()).hexdigest())
    json.dump(man, open("data/pairs_manifest.json", "w"), indent=1)
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main()
