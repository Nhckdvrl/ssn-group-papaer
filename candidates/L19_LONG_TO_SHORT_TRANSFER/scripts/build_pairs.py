"""Build the frozen L19 NQ pair set. Cutoffs come from DATA_AND_GOLD.md and are not
adjustable after any result is seen."""
import sys, glob, json, hashlib, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from nq_extract import extract
import pyarrow.parquet as pq
from transformers import AutoTokenizer

MODEL      = "princeton-nlp/Llama-3-8B-ProLong-512k-Base"
MAX_SUPPORT= 512
MIN_PAGE   = 8000
MAX_PAGE   = 24000
N_TARGET   = 10000
OUT        = "data/nq_pairs.jsonl"

def main():
    tokz = AutoTokenizer.from_pretrained(MODEL)
    files = sorted(glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/datasets--google-research-datasets--natural_questions"
        "/snapshots/*/default/train-*.parquet")))
    print(f"{len(files)} shards available", flush=True)
    seen = kept = 0
    out = open(OUT, "w")
    for f in files:
        if kept >= N_TARGET: break
        for b in pq.ParquetFile(f).iter_batches(batch_size=64):
            for r in b.to_pylist():
                seen += 1
                e = extract(r)
                if e is None: continue
                ns = len(tokz(e["support"], add_special_tokens=False)["input_ids"])
                if ns > MAX_SUPPORT: continue
                np_ = len(tokz(e["page"], add_special_tokens=False)["input_ids"])
                if not (MIN_PAGE <= np_ <= MAX_PAGE): continue
                e["tok_support"], e["tok_page"] = ns, np_
                out.write(json.dumps(e) + "\n"); kept += 1
                if kept >= N_TARGET: break
            if kept >= N_TARGET: break
        print(f"  shard done: seen={seen} kept={kept}", flush=True)
    out.close()
    man = dict(model=MODEL, max_support=MAX_SUPPORT, min_page=MIN_PAGE, max_page=MAX_PAGE,
               n_target=N_TARGET, n_kept=kept, n_raw_scanned=seen,
               yield_rate=kept/seen,
               sha256=hashlib.sha256(open(OUT,'rb').read()).hexdigest())
    json.dump(man, open("data/pairs_manifest.json","w"), indent=1)
    print(json.dumps(man, indent=1))

if __name__ == "__main__":
    main()
