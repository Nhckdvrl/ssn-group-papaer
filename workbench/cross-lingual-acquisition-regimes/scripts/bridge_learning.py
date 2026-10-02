"""E02: matched bridge coverage and cross-document conditioning before learning."""
import argparse
import collections
import gc
import hashlib
import html
import json
import os
from pathlib import Path
import random
import subprocess
import time
import unicodedata
from types import SimpleNamespace

import nli_learning as nli

ROOT = nli.ROOT
DATA = ROOT / "artifacts/bridge_learning/data.json"
N = 8192
CONDITIONS = ("new_paired", "new_split", "reused_paired", "reused_split")
CONFIG = dict(max_length=512, micro_batch=4, accumulation=8, updates=256,
              lr=2e-5, warmup=26, weight_decay=.01)


def compact(text):
    return "".join(unicodedata.normalize("NFKC", html.unescape(text)).casefold().split())


def prepare():
    from datasets import load_dataset
    from transformers import AutoTokenizer
    assert not DATA.exists(), "Never silently replace the bridge corpus"
    original = json.loads(nli.DATA.read_text())
    manifest = json.loads((ROOT / "artifacts/model_manifests/UCLNLP__monoweb__ckpt_exp_en_de_monoweb.json").read_text())
    tok = AutoTokenizer.from_pretrained(manifest["path"], local_files_only=True)
    mn = load_dataset("nyu-mll/multi_nli", revision=nli.REVISIONS["nyu-mll/multi_nli"])["train"].select_columns(["premise", "hypothesis", "label"])
    en = load_dataset("facebook/xnli", "en", revision=nli.REVISIONS["facebook/xnli"])
    de = load_dataset("facebook/xnli", "de", revision=nli.REVISIONS["facebook/xnli"])
    assert len(mn) == len(en["train"]) == len(de["train"])
    evaluation_premises = {compact(r["premise"]) for split in ("en_dev", "en_test") for r in original["splits"][split]}
    evaluation_premises.update(compact(p) for p in en["validation"]["premise"])
    task_premises = {compact(r["premise"]) for r in original["splits"]["train"]}
    forbidden_reuse = evaluation_premises | task_premises
    removed = collections.Counter()

    def units(indices):
        accepted = []
        for start in range(0, len(indices), 512):
            block = indices[start:start+512]
            a, b, c = mn[block], en["train"][block], de["train"][block]
            tokens = [tok(texts, add_special_tokens=False)["input_ids"] for texts in
                      (a["premise"], a["hypothesis"], c["premise"], c["hypothesis"])]
            for j, idx in enumerate(block):
                aligned = all(compact(a[k][j]) == compact(b[k][j]) for k in ("premise", "hypothesis"))
                assert a["label"][j] == b["label"][j] == c["label"][j], "Index/label mismatch"
                if not aligned:
                    removed["source_text_index_mismatch"] += 1
                    continue
                source = [tok.bos_token_id] + tokens[0][j] + [tok.eos_token_id] + tokens[1][j] + [tok.eos_token_id]
                target = [tok.bos_token_id] + tokens[2][j] + [tok.eos_token_id] + tokens[3][j] + [tok.eos_token_id]
                if len(source)+len(target) > CONFIG["max_length"]:
                    removed["complete_unit_over_512"] += 1
                    continue
                accepted.append(dict(mnli_id=idx, ids=source+target, boundary=len(source),
                                     stratum_label=a["label"][j]))
        return accepted

    new_indices = [r["id"] for r in original["splits"]["train"] if compact(r["premise"]) not in evaluation_premises]
    random.Random(20261003).shuffle(new_indices)
    new = units(new_indices[:N+1024])[:N]
    assert len(new) == N
    candidates = [i for i, p in enumerate(mn["premise"]) if compact(p) not in forbidden_reuse]
    random.Random(20261003).shuffle(candidates)
    reuse_candidates = units(candidates[:65536])
    buckets = collections.defaultdict(list)
    for unit in reuse_candidates:
        buckets[unit["stratum_label"], unit["boundary"], len(unit["ids"])-unit["boundary"]].append(unit)
    reused, exact_matches = [], 0
    for unit in new:
        key = (unit["stratum_label"], unit["boundary"], len(unit["ids"])-unit["boundary"])
        if buckets[key]:
            exact_matches += 1
            reused.append(buckets[key].pop())
        else:
            remaining = [k for k, v in buckets.items() if v and k[0] == key[0]]
            nearest = min(remaining, key=lambda k: (abs(k[1]-key[1])+abs(k[2]-key[2]), k))
            reused.append(buckets[nearest].pop())
    assert len({u["mnli_id"] for u in reused}) == N
    assert not {u["mnli_id"] for u in reused} & {r["id"] for r in original["splits"]["train"]+original["splits"]["en_dev"]}
    totals = {name: dict(en=sum(u["boundary"]-1 for u in pool),
                         de=sum(len(u["ids"])-u["boundary"]-1 for u in pool))
              for name, pool in (("new", new), ("reused", reused))}
    for language in ("en", "de"):
        assert abs(totals["new"][language]-totals["reused"][language])/totals["new"][language] <= .01
    holdout = []
    for i in range(128):
        a, b = en["validation"][i], de["validation"][i]
        assert a["label"] == b["label"]
        source = [tok.bos_token_id]+tok.encode(a["premise"], add_special_tokens=False)+[tok.eos_token_id]+tok.encode(a["hypothesis"], add_special_tokens=False)+[tok.eos_token_id]
        target = [tok.bos_token_id]+tok.encode(b["premise"], add_special_tokens=False)+[tok.eos_token_id]+tok.encode(b["hypothesis"], add_special_tokens=False)+[tok.eos_token_id]
        assert len(source)+len(target) <= CONFIG["max_length"]
        holdout.append(dict(mnli_id=i, ids=source+target, boundary=len(source)))
    pools = dict(new=new, reused=reused, holdout=holdout)
    metadata = dict(revisions=nli.REVISIONS, source_data_hashes=original["metadata"]["hashes"],
                    hashes={k:nli.digest(v) for k,v in pools.items()}, token_totals=totals,
                    counts={k:len(v) for k,v in pools.items()}, removed=dict(removed),
                    exact_length_matches=exact_matches, source_text_verified=True,
                    source_group_exclusion=True, candidate_count=len(reuse_candidates),
                    pad=tok.eos_token_id, base_model=manifest, config=CONFIG)
    nli.dump(DATA, dict(metadata=metadata, pools=pools))
    nli.dump(ROOT / "results/e02_data_manifest.json", metadata)
    print(json.dumps(metadata), flush=True)


def batch(rows, mode, pad, target_only=False):
    import torch
    length = max(len(r["ids"]) for r in rows)
    ids = torch.full((len(rows), length), pad, dtype=torch.long, device="cuda")
    segments = torch.full_like(ids, -1)
    labels = torch.full_like(ids, -100)
    for i, row in enumerate(rows):
        n, boundary = len(row["ids"]), row["boundary"]
        ids[i, :n] = torch.tensor(row["ids"], device="cuda")
        segments[i, :boundary] = 0
        segments[i, boundary:n] = 1
        labels[i, :n] = ids[i, :n]
        labels[i, 0] = labels[i, boundary] = -100
        if target_only:
            labels[i, :boundary] = -100
    causal = torch.ones((length, length), dtype=torch.bool, device="cuda").tril()
    allowed = causal[None] & (segments[:, :, None] >= 0) & (segments[:, None, :] >= 0)
    if mode == "split":
        allowed &= segments[:, :, None] == segments[:, None, :]
    # Padding queries attend only to themselves, avoiding fully masked rows.
    allowed |= (segments[:, :, None] < 0) & torch.eye(length, dtype=torch.bool, device="cuda")[None]
    mask = torch.zeros(allowed.shape, dtype=torch.float32, device="cuda").masked_fill(~allowed, float("-inf"))
    return ids, mask[:, None], labels


def mask_check(model, row, pad):
    import torch
    changed = dict(row, ids=row["ids"].copy())
    changed["ids"][1:row["boundary"]-1] = list(reversed(changed["ids"][1:row["boundary"]-1]))
    results = {}
    model.eval()
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
        for mode in ("paired", "split"):
            ids, mask, labels = batch([row, changed], mode, pad)
            logits = model(input_ids=ids, attention_mask=mask).logits.float()
            assert torch.isfinite(logits).all()
            difference = (logits[0, row["boundary"]:len(row["ids"])]-logits[1, row["boundary"]:len(row["ids"])]).abs().max().item()
            assert labels[0, row["boundary"]] == -100
            results[mode] = difference
    assert results["split"] < 1e-5 and results["paired"] > 1e-5, results
    return results


def run(args):
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup
    payload = json.loads(DATA.read_text())
    metadata = payload["metadata"]
    assert metadata["config"] == CONFIG
    for key, rows in payload["pools"].items():
        assert nli.digest(rows) == metadata["hashes"][key]
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.set_num_threads(4)
    model = AutoModelForCausalLM.from_pretrained(metadata["base_model"]["path"], dtype=torch.float32,
                                               attn_implementation="sdpa", local_files_only=True).cuda()
    model.config.use_cache = False
    check = mask_check(model, payload["pools"]["new"][0], metadata["pad"])
    if args.phase == "check":
        nli.dump(ROOT / "results/e02_mask_check.json", dict(check=check, device=torch.cuda.get_device_name(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
        print("MASK_CHECK", check, flush=True)
        return
    name = args.condition+f"_seed{args.seed}"
    out = ROOT / "artifacts/bridge_learning" / name
    assert not out.exists(), "Keep completed and interrupted runs; never overwrite"
    out.mkdir(parents=True)
    coverage, mode = args.condition.split("_")
    rows = payload["pools"][coverage].copy()
    random.Random(args.seed).shuffle(rows)
    provenance = dict(condition=args.condition, seed=args.seed, config=CONFIG,
                      metadata=metadata, mask_check=check, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                      torch=torch.__version__, numpy=np.__version__, device=torch.cuda.get_device_name())
    nli.dump(out / "provenance.json", provenance)
    def evaluate():
        model.eval()
        total, count = 0., 0
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            for start in range(0, len(payload["pools"]["holdout"]), 4):
                ids, mask, labels = batch(payload["pools"]["holdout"][start:start+4], "paired", metadata["pad"], True)
                logits = model(input_ids=ids, attention_mask=mask).logits.float()
                loss = torch.nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]), labels[:, 1:].reshape(-1), reduction="sum")
                total += loss.item()
                count += (labels[:, 1:] != -100).sum().item()
        return dict(de_conditional_nll=total/count, target_loss_tokens=count)
    started = time.time()
    before = evaluate()
    optimizer = torch.optim.AdamW(model.parameters(), lr=CONFIG["lr"], weight_decay=CONFIG["weight_decay"])
    scheduler = get_linear_schedule_with_warmup(optimizer, CONFIG["warmup"], CONFIG["updates"])
    losses = []
    for step in range(CONFIG["updates"]):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        block = rows[step*32:(step+1)*32]
        assert len(block) == 32
        denominator = sum(len(r["ids"])-2 for r in block)
        loss_sum = 0.
        for start in range(0, 32, 4):
            ids, mask, labels = batch(block[start:start+4], mode, metadata["pad"])
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(input_ids=ids, attention_mask=mask).logits.float()
                loss = torch.nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]), labels[:, 1:].reshape(-1), reduction="sum")
            assert torch.isfinite(loss)
            (loss/denominator).backward()
            loss_sum += loss.item()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
        assert torch.isfinite(norm)
        optimizer.step()
        scheduler.step()
        losses.append(loss_sum/denominator)
        if (step+1) % 16 == 0:
            nli.dump(out / "losses.json", losses)
            print(json.dumps(dict(condition=args.condition, update=step+1, loss=sum(losses[-16:])/16,
                                  elapsed_seconds=time.time()-started)), flush=True)
    after = evaluate()
    record = dict(provenance=provenance, before=before, after=after, losses=losses,
                  elapsed_seconds=time.time()-started, peak_gpu_bytes=torch.cuda.max_memory_allocated(),
                  finite=True, loss_decreased=sum(losses[-32:]) < sum(losses[:32]))
    nli.dump(out / "metrics.json", record)
    nli.dump(ROOT / "results" / f"e02_cpt_{name}.json", record)
    save_started = time.time()
    model.save_pretrained(out / "checkpoint", safe_serialization=True)
    AutoTokenizer.from_pretrained(metadata["base_model"]["path"], local_files_only=True).save_pretrained(out / "checkpoint")
    record["save_seconds"] = time.time()-save_started
    manifest = dict(metadata["base_model"], path=str(out / "checkpoint"), parent=metadata["base_model"],
                    local_intervention=dict(condition=args.condition, seed=args.seed,
                                            data_hash=metadata["hashes"][coverage], script_sha256=provenance["script_sha256"]))
    nli.dump(ROOT / "artifacts/model_manifests" / f"UCLNLP__monoweb__ckpt_exp_en_de_e02_{args.condition}.json", manifest)
    nli.dump(ROOT / "results" / f"e02_cpt_{name}.json", record)
    del model, optimizer, scheduler, logits, loss
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    print("CPT_SAVED", name, flush=True)
    nli.run(SimpleNamespace(phase="train", condition=f"e02_{args.condition}", seed=args.seed))
    nli.dump(out / "completion.json", dict(condition=args.condition, seed=args.seed, cpt=record,
                                          task_folder=f"artifacts/nli_learning/train_e02_{args.condition}_seed{args.seed}"))
    print("E02_COMPLETED", name, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("prepare", "check", "run"))
    parser.add_argument("--condition", choices=CONDITIONS, default="new_paired")
    parser.add_argument("--seed", type=int, choices=(17, 29, 43), default=17)
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare()
    else:
        run(args)
