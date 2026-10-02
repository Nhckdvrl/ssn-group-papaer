"""Same reused content and token budget in both language orders, then frozen QA."""
import argparse
import collections
import gc
import hashlib
import json
from pathlib import Path
import random
import subprocess
import time
from types import SimpleNamespace

import bridge_learning as bridge
import nli_learning as nli
import qa_bridge_learning as e04
import qa_learning as qa

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "artifacts/symmetric_bridge/data.json"
CONFIG = e04.CONFIG.copy()


def reverse(row):
    boundary = row["boundary"]
    return dict(row, ids=row["ids"][boundary:] + row["ids"][:boundary],
                boundary=len(row["ids"]) - boundary, direction="de->en")


def prepare():
    assert not DATA.exists(), "Keep previously prepared pools"
    original_path = ROOT / "artifacts/qa_bridge/data.json"
    original = json.loads(original_path.read_text())
    metadata = original["metadata"]
    rows = original["pools"]["reused"]
    assert nli.digest(rows) == metadata["hashes"]["reused"]
    assert len(rows) == 8192 and rows[:4096] == rows[4096:]
    unique = rows[:4096]
    assert len({row["id"] for row in unique}) == 4096
    symmetric = [dict(row, direction="en->de") for row in unique] + [reverse(row) for row in unique]
    assert collections.Counter(row["id"] for row in rows) == collections.Counter(row["id"] for row in symmetric)
    token_totals = collections.Counter()
    by_id = {row["id"]: row for row in unique}
    for row in symmetric:
        source = by_id[row["id"]]
        first, second = row["ids"][:row["boundary"]], row["ids"][row["boundary"]:]
        en, de = (first, second) if row["direction"] == "en->de" else (second, first)
        assert en == source["ids"][:source["boundary"]]
        assert de == source["ids"][source["boundary"]:]
        assert len(row["ids"]) <= CONFIG["max_length"]
        token_totals.update(en=len(en)-1, de=len(de)-1)
    assert dict(token_totals) == metadata["token_totals"]["reused"]
    holdout = original["pools"]["holdout"]
    report = dict(parent_metadata=metadata, parent_file_sha256=hashlib.sha256(original_path.read_bytes()).hexdigest(),
        pool_sha256=nli.digest(symmetric), holdout_sha256=nli.digest(holdout), token_totals=dict(token_totals),
        unique_contexts=4096, units=8192, direction_counts=dict(collections.Counter(r["direction"] for r in symmetric)),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), config=CONFIG,
        limits="Paired/split share positions; forward-only comparison also changes language positions. Same-domain reused pool, single family and joint seed.")
    nli.dump(DATA, dict(metadata=report, rows=symmetric, holdout=holdout))
    nli.dump(ROOT / "results/e11_data_manifest.json", report)
    print(json.dumps(report), flush=True)


def run(args):
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup
    freeze = json.loads(qa.FREEZE.read_text())
    assert freeze["passed"] and freeze["script_sha256"] == hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest()
    payload = json.loads(DATA.read_text())
    metadata = payload["metadata"]
    parent = metadata["parent_metadata"]
    assert metadata["config"] == CONFIG and parent["task_hashes"] == freeze["data_hashes"]
    assert nli.digest(payload["rows"]) == metadata["pool_sha256"]
    assert nli.digest(payload["holdout"]) == metadata["holdout_sha256"]
    assert metadata["script_sha256"] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    assert metadata["token_totals"] == parent["token_totals"]["reused"]
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.set_num_threads(4)
    model = AutoModelForCausalLM.from_pretrained(parent["base_model"]["path"], dtype=torch.float32,
        attn_implementation="sdpa", local_files_only=True).cuda()
    assert torch.cuda.get_device_name() == "NVIDIA A100 80GB PCIe"
    model.config.use_cache = False
    checks = {direction: bridge.mask_check(model, next(r for r in payload["rows"] if r["direction"] == direction), parent["pad"])
              for direction in ("en->de", "de->en")}
    name = f"{args.condition}_seed{args.seed}"
    out = ROOT / "artifacts/symmetric_bridge" / name
    out.mkdir(parents=True, exist_ok=False)
    rows = payload["rows"].copy()
    random.Random(args.seed).shuffle(rows)
    provenance = dict(condition=args.condition, seed=args.seed, config=CONFIG, metadata=metadata, mask_checks=checks,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        mask_script_sha256=hashlib.sha256(Path(bridge.__file__).read_bytes()).hexdigest(),
        qa_script_sha256=freeze["script_sha256"], encoded_order_sha256=nli.digest(rows),
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        device=torch.cuda.get_device_name(), torch=torch.__version__, numpy=np.__version__)
    nli.dump(out / "provenance.json", provenance)

    def evaluate():
        model.eval()
        measurements = {}
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            for direction in ("en->de", "de->en"):
                total, count = 0., 0
                for row in payload["holdout"]:
                    unit = row if direction == "en->de" else reverse(row)
                    ids, mask, labels = bridge.batch([unit], "paired", parent["pad"], True)
                    logits = model(input_ids=ids, attention_mask=mask).logits.float()
                    loss = torch.nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]),
                        labels[:, 1:].reshape(-1), reduction="sum")
                    total += loss.item()
                    count += (labels[:, 1:] != -100).sum().item()
                measurements[direction] = dict(conditional_nll=total/count, target_loss_tokens=count)
        return measurements

    started = time.time()
    before = evaluate()
    optimizer = torch.optim.AdamW(model.parameters(), lr=CONFIG["lr"], weight_decay=CONFIG["weight_decay"])
    scheduler = get_linear_schedule_with_warmup(optimizer, CONFIG["warmup"], CONFIG["updates"])
    losses, input_tokens, loss_tokens = [], 0, 0
    for step in range(CONFIG["updates"]):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        block = rows[step*32:(step+1)*32]
        assert len(block) == 32
        denominator = sum(len(r["ids"])-2 for r in block)
        loss_sum = 0.
        for row in block:
            ids, mask, labels = bridge.batch([row], args.condition, parent["pad"])
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(input_ids=ids, attention_mask=mask).logits.float()
                loss = torch.nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]),
                    labels[:, 1:].reshape(-1), reduction="sum")
            assert torch.isfinite(loss)
            (loss/denominator).backward()
            loss_sum += loss.item()
            input_tokens += len(row["ids"])
            loss_tokens += len(row["ids"])-2
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
        assert torch.isfinite(norm)
        optimizer.step()
        scheduler.step()
        losses.append(loss_sum/denominator)
        if (step+1) % 16 == 0:
            nli.dump(out / "losses.json", losses)
            print(json.dumps(dict(condition=args.condition, update=step+1,
                loss=sum(losses[-16:])/16, elapsed_seconds=time.time()-started)), flush=True)
    after = evaluate()
    assert loss_tokens == sum(metadata["token_totals"].values())
    record = dict(provenance=provenance, before=before, after=after, losses=losses,
        input_tokens=input_tokens, loss_tokens=loss_tokens, elapsed_seconds=time.time()-started,
        peak_gpu_bytes=torch.cuda.max_memory_allocated(), finite=True,
        loss_decreased=sum(losses[-32:]) < sum(losses[:32]))
    save_started = time.time()
    model.save_pretrained(out / "checkpoint", safe_serialization=True)
    AutoTokenizer.from_pretrained(parent["base_model"]["path"], local_files_only=True).save_pretrained(out / "checkpoint")
    record["save_seconds"] = time.time()-save_started
    nli.dump(out / "metrics.json", record)
    condition = f"e11_{args.condition}"
    manifest = dict(parent["base_model"], path=str(out / "checkpoint"), parent=parent["base_model"],
        local_intervention=dict(experiment="E11", condition=args.condition, seed=args.seed,
            data_hash=metadata["pool_sha256"], script_sha256=provenance["script_sha256"]))
    nli.dump(ROOT / "artifacts/model_manifests" / f"UCLNLP__monoweb__ckpt_exp_en_de_{condition}.json", manifest)
    nli.dump(ROOT / "results" / f"e11_cpt_{name}.json", record)
    del model, optimizer, scheduler, logits, loss
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    qa.run(SimpleNamespace(phase="train", condition=condition, seed=args.seed))
    nli.dump(out / "completion.json", dict(condition=args.condition, seed=args.seed, cpt=record,
        task_folder=f"artifacts/qa_learning/train_{condition}_seed{args.seed}"))
    print("E11_COMPLETED", name, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("prepare", "run"))
    parser.add_argument("--condition", choices=("paired", "split"), default="paired")
    parser.add_argument("--seed", type=int, choices=(17,), default=17)
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare()
    else:
        run(args)
