"""Prepare the local inputs that are not downloaded on demand by the other scripts.

  prepare_data.py corpora   -> $MECHPOP_CACHE/controlled_data/{c4,code,papers,books,flan}.u16
      Fixed-size prefixes of single source files of allenai/DataDecide-data-recipes (already tokenized with the OLMo
      tokenizer, uint16 ids), read by HTTP range request. Used by controlled_pretraining.py (controlled pretraining) and
      habit_continued_pretraining.py (continued pretraining; run `habit_continued_pretraining.py --prep` afterwards).
  prepare_data.py probes    -> $MECHPOP_CACHE/pile_eval_2000_seed42.pt
      2,000 random 1,024-token windows of NeelNanda/pile-10k (Pythia tokenizer, torch seed 42): the natural-text
      probe material of head_roles.py / crossing_1b.py.

Set HF_TOKEN if the dataset requires authentication.
"""
import os
import sys
import urllib.request
from pathlib import Path

CACHE = Path(os.environ.get("MECHPOP_CACHE", Path(__file__).resolve().parents[1] / "cache"))
URL = "https://huggingface.co/datasets/allenai/DataDecide-data-recipes/resolve/main/"
N = 800_000_000  # bytes = 400M uint16 tokens per corpus
CORPORA = {
    "c4": ("preprocessed/c4/v1_7-dd_ngram_dp_030-qc_cc_en_bin_001-fix/gpt-neox-olmo-dolma-v1_5/part-062-00000.npy", N),
    "code": ("preprocessed/starcoder/v0_decontaminated_doc_only/gpt-neox-olmo-dolma-v1_5/part-43-00000.npy", N),
    "papers": ("preprocessed/olmo-mix/v1_6-decontaminated/pes2o/gpt-neox-olmo-dolma-v1_5/part-06-00000.npy", N),
    "books": ("preprocessed/olmo-mix/v1_6-decontaminated/books/gpt-neox-olmo-dolma-v1_5/part-0-00000.npy", N),
    "flan": ("preprocessed/tulu_flan/v2-decontaminated-60M-shots_all-upweight_1-dialog_false-sep_newline/train/"
             "gpt-neox-olmo-dolma-v1_5/part-48-00000.npy", 548_408_740),
}


def corpora():
    out = CACHE / "controlled_data"
    out.mkdir(parents=True, exist_ok=True)
    headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"} if os.environ.get("HF_TOKEN") else {}
    for name, (path, nbytes) in CORPORA.items():
        dst = out / f"{name}.u16"
        if dst.exists() and dst.stat().st_size >= nbytes * 0.99:
            print("exists", name)
            continue
        req = urllib.request.Request(URL + path, headers={**headers, "Range": f"bytes=0-{nbytes - 1}"})
        with urllib.request.urlopen(req, timeout=1800) as r, open(dst, "wb") as f:
            while True:
                b = r.read(1 << 24)
                if not b:
                    break
                f.write(b)
        print("done", name, dst.stat().st_size)


def probes(n=2000):
    import torch
    from datasets import load_dataset
    from transformer_lens import utils as tl_utils
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m")
    ds = load_dataset("NeelNanda/pile-10k", split="train")
    toks = tl_utils.tokenize_and_concatenate(ds, tok)
    idx = torch.randperm(len(toks), generator=torch.Generator().manual_seed(42))[:n]
    CACHE.mkdir(parents=True, exist_ok=True)
    torch.save({"tokens": toks["tokens"][idx], "idx": idx}, CACHE / "pile_eval_2000_seed42.pt")
    print("done probes", n)


if __name__ == "__main__":
    {"corpora": corpora, "probes": probes}[sys.argv[1]]()
