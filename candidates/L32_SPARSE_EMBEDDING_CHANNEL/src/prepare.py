"""Build the frozen en->ca training pool and the Flores devtest eval set.

Deviation from the parent, recorded in notes/E01_DESIGN.md: the parent trains on
"Lego-MT 10k data". The public Lego-MT/Parallel_Dataset release is a per-language
10k *mixed-direction* sample (ca.jsonl holds only 935 en->ca pairs), so it cannot
supply a 10k bilingual en->ca set. OPUS-100 ca-en is used instead. The training
corpus is not part of the estimand -- the channel contrast reuses one trained
model -- but it is part of the first-stage replication gate, so it is frozen and
hashed here.
"""
import argparse
import hashlib
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ROOT, build_prompt, build_target  # noqa: E402


def clean(s):
    return " ".join(s.split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n-train", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=1732)
    ap.add_argument("--out", default=str(ROOT / "data"))
    args = ap.parse_args()

    from transformers import AutoTokenizer
    from datasets import load_dataset
    tok = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    eos = tok.eos_token_id

    ds = load_dataset("Helsinki-NLP/opus-100", "ca-en", split="train")
    rng = random.Random(args.seed)
    order = list(range(len(ds)))
    rng.shuffle(order)

    seen, rows = set(), []
    stats = {"scanned": 0, "dup": 0, "len": 0, "ratio": 0, "tok": 0}
    for i in order:
        if len(rows) >= args.n_train:
            break
        stats["scanned"] += 1
        tr = ds[i]["translation"]
        en, ca = clean(tr["en"]), clean(tr["ca"])
        if not (60 <= len(en) <= 400 and 60 <= len(ca) <= 400):
            stats["len"] += 1
            continue
        if not (0.5 <= len(ca) / len(en) <= 2.0):
            stats["ratio"] += 1
            continue
        if en in seen:
            stats["dup"] += 1
            continue
        ids, seg = build_prompt(tok, en)
        if ids is None:
            stats["tok"] += 1
            continue
        y = build_target(tok, ca, eos)
        if len(ids) + len(y) > 512:
            stats["len"] += 1
            continue
        seen.add(en)
        rows.append({"src": en, "tgt": ca, "ids": ids, "seg": seg, "y": y})

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tp = out / "train_en_ca.jsonl"
    with open(tp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    fl = out / "flores101_dataset" / "devtest"
    src = [clean(l) for l in open(fl / "eng.devtest", encoding="utf-8")]
    ref = [clean(l) for l in open(fl / "cat.devtest", encoding="utf-8")]
    assert len(src) == len(ref) == 1012
    ep = out / "devtest_en_ca.jsonl"
    kept = 0
    with open(ep, "w", encoding="utf-8") as f:
        for s, r in zip(src, ref):
            ids, seg = build_prompt(tok, s)
            if ids is None:
                continue
            f.write(json.dumps({"src": s, "ref": r, "ids": ids, "seg": seg,
                                "y": build_target(tok, r, eos)}, ensure_ascii=False) + "\n")
            kept += 1

    meta = {
        "n_train": len(rows), "filters": stats, "seed": args.seed,
        "n_devtest": kept,
        "train_sha256": hashlib.sha256(tp.read_bytes()).hexdigest()[:16],
        "devtest_sha256": hashlib.sha256(ep.read_bytes()).hexdigest()[:16],
        "mean_src_tokens": sum(len(r["ids"]) for r in rows) / len(rows),
        "mean_tgt_tokens": sum(len(r["y"]) for r in rows) / len(rows),
    }
    (out / "pool_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
