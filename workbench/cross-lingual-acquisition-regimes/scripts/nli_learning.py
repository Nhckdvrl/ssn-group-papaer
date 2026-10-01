"""Preregistered E01: real task learning, source-only recipe validation."""
import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import time
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "artifacts/nli_learning/data.json"
FREEZE = ROOT / "results/nli_recipe_freeze.json"
REVISIONS = {"nyu-mll/multi_nli": "da70db2af9d09693783c3320c4249840212ee221",
             "facebook/xnli": "b8dd5d7af51114dbda02c0e3f6133f332186418e"}
CONFIG = dict(max_length=256, batch_size=8, accumulation=4, lr=2e-5,
              weight_decay=.01, total_updates=1024, warmup_updates=102)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False,
                                    sort_keys=True).encode()).hexdigest()


def pair(row):
    return tuple(" ".join(unicodedata.normalize("NFKC", row[k]).casefold().split())
                 for k in ("premise", "hypothesis"))


def prepare():
    from datasets import load_dataset
    mn = load_dataset("nyu-mll/multi_nli", revision=REVISIONS["nyu-mll/multi_nli"])
    en = load_dataset("facebook/xnli", "en", revision=REVISIONS["facebook/xnli"])["test"]
    de = load_dataset("facebook/xnli", "de", revision=REVISIONS["facebook/xnli"])["test"]
    for ds in (mn["train"], en, de):
        assert ds.features["label"].names == ["entailment", "neutral", "contradiction"]
    assert len(en) == len(de) == 5010
    assert list(en["label"]) == list(de["label"])
    forbidden = {pair(r) for r in en}
    seen, eligible, removed = set(), [], collections.Counter()
    for i, r in enumerate(mn["train"]):
        p = pair(r)
        if r["label"] not in (0, 1, 2):
            removed["invalid_label"] += 1
        elif p in forbidden:
            removed["test_overlap"] += 1
        elif p in seen:
            removed["duplicate"] += 1
        else:
            seen.add(p)
            eligible.append(i)
    random.Random(20261002).shuffle(eligible)
    def rows(indices):
        return [dict(id=i, premise=mn["train"][i]["premise"],
                     hypothesis=mn["train"][i]["hypothesis"],
                     label=mn["train"][i]["label"]) for i in indices]
    selected = {"en_dev": rows(eligible[:4096]), "train": rows(eligible[4096:4096+32768]),
                "en_test": [dict(id=i, **r) for i, r in enumerate(en)],
                "de_test": [dict(id=i, **r) for i, r in enumerate(de)]}
    assert not {pair(r) for r in selected["train"]} & {pair(r) for r in selected["en_dev"]}
    metadata = dict(revisions=REVISIONS, removed=dict(removed),
                    counts={k: len(v) for k, v in selected.items()},
                    hashes={k: digest(v) for k, v in selected.items()}, split_seed=20261002,
                    labels=["entailment", "neutral", "contradiction"])
    dump(DATA, dict(metadata=metadata, splits=selected))
    dump(ROOT / "results/nli_data_manifest.json", metadata)
    print(json.dumps(metadata), flush=True)


def metrics(labels, predictions):
    matrix = [[0] * 3 for _ in range(3)]
    for y, p in zip(labels, predictions):
        matrix[y][p] += 1
    n = len(labels)
    correct = sum(matrix[i][i] for i in range(3))
    acc = correct / n
    z = 1.959963984540054
    center = (acc + z*z/(2*n)) / (1+z*z/n)
    radius = z * math.sqrt(acc*(1-acc)/n+z*z/(4*n*n)) / (1+z*z/n)
    f1 = []
    for i in range(3):
        denominator = sum(matrix[i]) + sum(row[i] for row in matrix)
        f1.append(2*matrix[i][i]/denominator if denominator else 0.)
    return dict(n=n, accuracy=acc, wilson95=[center-radius, center+radius],
                macro_f1=sum(f1)/3, confusion=matrix,
                predictions_per_class=[sum(row[i] for row in matrix) for i in range(3)],
                majority_baseline=max(collections.Counter(labels).values())/n)


def run(args):
    import numpy as np
    import torch
    from transformers import AutoModel, AutoTokenizer, get_linear_schedule_with_warmup
    if args.phase == "train":
        freeze = json.loads(FREEZE.read_text())
        assert freeze["passed"] and freeze["config"] == CONFIG
        assert freeze["script_sha256"] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    started = time.time()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_num_threads(4)
    payload = json.loads(DATA.read_text())
    if args.phase == "train":
        assert payload["metadata"]["hashes"] == freeze["data_hashes"]
    manifest = json.loads((ROOT / "artifacts/model_manifests" /
                          f"UCLNLP__monoweb__ckpt_exp_en_de_{args.condition}.json").read_text())
    tok = AutoTokenizer.from_pretrained(manifest["path"], local_files_only=True)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    def encode(rows):
        encoded, truncations = [], 0
        for r in rows:
            # Same language-independent sentence boundary and final pooling site.
            a = tok.encode(r["premise"], add_special_tokens=False)
            b = tok.encode(r["hypothesis"], add_special_tokens=False)
            if len(a)+len(b)+3 > CONFIG["max_length"]:
                truncations += 1
                while len(a)+len(b)+3 > CONFIG["max_length"]:
                    (a if len(a) > len(b) else b).pop()
            ids = [tok.bos_token_id] + a + [tok.eos_token_id] + b + [tok.eos_token_id]
            encoded.append(dict(id=r["id"], ids=ids, label=r["label"]))
        return encoded, truncations
    splits = {k: encode(v) for k, v in payload["splits"].items()
              if k in ("train", "en_dev") or args.phase == "train"}
    print("Loading backbone", args.condition, flush=True)
    backbone = AutoModel.from_pretrained(manifest["path"], dtype=torch.float32,
                                        local_files_only=True, attn_implementation="sdpa")
    backbone.config.use_cache = False
    torch.manual_seed(args.seed)
    head = torch.nn.Linear(backbone.config.hidden_size, 3, bias=False)
    torch.nn.init.normal_(head.weight, mean=0., std=.02)
    initial_head_hash = hashlib.sha256(head.weight.detach().numpy().tobytes()).hexdigest()
    backbone.cuda()
    head.cuda()
    def batch(rows):
        length = max(len(r["ids"]) for r in rows)
        ids = torch.full((len(rows), length), pad, dtype=torch.long, device="cuda")
        mask = torch.zeros_like(ids)
        for i, r in enumerate(rows):
            ids[i, :len(r["ids"])] = torch.tensor(r["ids"], device="cuda")
            mask[i, :len(r["ids"])] = 1
        labels = torch.tensor([r["label"] for r in rows], device="cuda")
        return ids, mask, labels
    def forward(ids, mask):
        hidden = backbone(input_ids=ids, attention_mask=mask).last_hidden_state
        last = hidden[torch.arange(len(ids), device=ids.device), mask.sum(1)-1]
        return head(last)
    def evaluate(rows):
        backbone.eval()
        head.eval()
        preds, labels, loss = [], [], 0.
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for start in range(0, len(rows), 16):
                ids, mask, y = batch(rows[start:start+16])
                logits = forward(ids, mask).float()
                preds += logits.argmax(1).tolist()
                labels += y.tolist()
                loss += torch.nn.functional.cross_entropy(logits, y, reduction="sum").item()
        return dict(**metrics(labels, preds), loss=loss/len(rows)), preds
    name = f"{args.phase}_{args.condition}_seed{args.seed}"
    out = ROOT / "artifacts/nli_learning" / name
    out.mkdir(parents=True, exist_ok=False)
    provenance = dict(config=CONFIG, model=manifest, data=payload["metadata"],
                      seed=args.seed, phase=args.phase, initial_head_sha256=initial_head_hash,
                      encoded_hashes={k: digest(v[0]) for k, v in splits.items()},
                      truncations={k: v[1] for k, v in splits.items()},
                      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
                      torch=torch.__version__, device=torch.cuda.get_device_name(),
                      tokenizer_sha256=digest(tok.get_vocab()))
    dump(out / "provenance.json", provenance)
    curve = []
    def snapshot(step):
        result = dict(updates=step, examples=step*32, elapsed_seconds=time.time()-started, metrics={})
        for split, (rows, _) in splits.items():
            if split != "train":
                m, predictions = evaluate(rows)
                result["metrics"][split] = m
                dump(out / f"predictions_{split}_{step}.json", predictions)
        curve.append(result)
        dump(out / "curve.json", curve)
        dump(ROOT / "results" / f"nli_{name}.json", dict(provenance=provenance, curve=curve))
        print(json.dumps(result), flush=True)
    snapshot(0)
    parameters = list(backbone.parameters()) + list(head.parameters())
    optimizer = torch.optim.AdamW(parameters, lr=CONFIG["lr"], weight_decay=CONFIG["weight_decay"])
    scheduler = get_linear_schedule_with_warmup(optimizer, CONFIG["warmup_updates"], CONFIG["total_updates"])
    train = splits["train"][0].copy()
    random.Random(args.seed).shuffle(train)
    losses = []
    updates = 256 if args.phase == "pilot" else 1024
    train_tokens = 0
    for step in range(1, updates+1):
        backbone.train()
        head.train()
        optimizer.zero_grad(set_to_none=True)
        update_loss = 0.
        for micro in range(4):
            rows = train[(step-1)*32+micro*8:(step-1)*32+(micro+1)*8]
            ids, mask, labels = batch(rows)
            train_tokens += mask.sum().item()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = forward(ids, mask).float()
                loss = torch.nn.functional.cross_entropy(logits, labels)
            assert torch.isfinite(loss), "Nonfinite task loss"
            (loss/4).backward()
            update_loss += loss.item()/4
        norm = torch.nn.utils.clip_grad_norm_(parameters, 1.)
        assert torch.isfinite(norm), "Nonfinite gradients"
        optimizer.step()
        scheduler.step()
        losses.append(update_loss)
        if step % 16 == 0:
            print(json.dumps(dict(update=step, loss=sum(losses[-16:])/16,
                                  seconds=time.time()-started)), flush=True)
            dump(out / "training_loss.json", losses)
        if step in (64, 256, 1024):
            snapshot(step)
    final = curve[-1]["metrics"]["en_dev"]
    passed = (final["accuracy"] >= .55 and final["accuracy"] > final["majority_baseline"]
              and min(final["predictions_per_class"]) > 0
              and sum(losses[-32:]) < sum(losses[:32]))
    record = dict(passed=passed, phase=args.phase, condition=args.condition, seed=args.seed,
                  config=CONFIG, final_source_dev=final, train_tokens=train_tokens,
                  elapsed_seconds=time.time()-started, peak_gpu_bytes=torch.cuda.max_memory_allocated(),
                  script_sha256=provenance["script_sha256"], data_hashes=payload["metadata"]["hashes"])
    dump(out / "completion.json", record)
    dump(ROOT / "results" / f"nli_{name}_completion.json", record)
    if args.phase == "train":
        backbone.save_pretrained(out / "checkpoint", safe_serialization=True)
        torch.save(head.state_dict(), out / "classification_head.pt")
    if args.phase == "pilot" and passed:
        assert args.condition == "baseline" and args.seed == 17
        assert not FREEZE.exists(), "Never silently replace source recipe freeze"
        dump(FREEZE, record)
    print("COMPLETED", json.dumps(record), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "pilot", "train"])
    parser.add_argument("--condition", choices=["baseline", "monoweb", "onlyparallel"], default="baseline")
    parser.add_argument("--seed", type=int, choices=[17, 29, 43], default=17)
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare()
    else:
        run(args)
