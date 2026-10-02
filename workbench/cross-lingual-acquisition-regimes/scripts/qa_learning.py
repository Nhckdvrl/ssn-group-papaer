"""E03: source-gated, answer-only generative QA task learning."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import time
import urllib.request

import nli_learning as nli

ROOT = nli.ROOT
DATA = ROOT / "artifacts/qa_learning/data.json"
FREEZE = ROOT / "results/e03_recipe_freeze.json"
REVISIONS = {"rajpurkar/squad": "7b6d24c440a36b6815f21b70d25016731768db1f",
             "google/xquad": "51adfef1c1287aab1d2d91b5bead9bcfb9c68583"}
SCORER_REVISION = "838c13b69daafb9328785d16caae2711e4012123"
CONFIG = dict(max_train_length=1024, max_new_tokens=64, micro_batch=2, accumulation=8,
              lr=2e-5, weight_decay=.01, updates=1024, warmup=102)


def prompt(row, instruction=False):
    prefix = "Copy a short answer from the context.\n" if instruction else ""
    return prefix+"Context:\n"+row["context"]+"\nQuestion:\n"+row["question"]+"\nAnswer:\n"


def encode(row, tok):
    prefix = [tok.bos_token_id]+tok.encode(prompt(row), add_special_tokens=False)
    full = [tok.bos_token_id]+tok.encode(prompt(row)+row["answers"]["text"][0].strip(), add_special_tokens=False)+[tok.eos_token_id]
    assert full[:len(prefix)] == prefix, "Context/answer token boundary changed"
    return dict(id=row["id"], ids=full, prefix_length=len(prefix))


def scorer():
    path = ROOT / "artifacts/qa_learning/evaluate_squad.py"
    spec = importlib.util.spec_from_file_location("e03_official_squad", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare():
    from datasets import load_dataset
    from transformers import AutoTokenizer
    assert not DATA.exists()
    sq = load_dataset("rajpurkar/squad", revision=REVISIONS["rajpurkar/squad"])
    en = load_dataset("google/xquad", "xquad.en", revision=REVISIONS["google/xquad"])["validation"]
    de = load_dataset("google/xquad", "xquad.de", revision=REVISIONS["google/xquad"])["validation"]
    assert list(en["id"]) == list(de["id"]) and len(en) == 1190
    original = {r["id"]:r for r in sq["validation"]}
    for r in en:
        assert r["id"] in original
        assert all(" ".join(r[k].split()) == " ".join(original[r["id"]][k].split()) for k in ("context", "question"))
    forbidden_ids = set(en["id"])
    forbidden_contexts = set(en["context"])
    titles = sorted(set(sq["train"]["title"]))
    random.Random(20261003).shuffle(titles)
    dev_titles = set(titles[:32])
    manifest = json.loads((ROOT / "artifacts/model_manifests/UCLNLP__monoweb__ckpt_exp_en_de_baseline.json").read_text())
    tok = AutoTokenizer.from_pretrained(manifest["path"], local_files_only=True)
    dev, train = [], []
    removed = collections.Counter()
    for row in sq["train"]:
        if row["id"] in forbidden_ids or row["context"] in forbidden_contexts:
            removed["test_overlap"] += 1
            continue
        encoded = encode(row, tok)
        if len(encoded["ids"]) > CONFIG["max_train_length"]:
            removed["complete_training_unit_over_1024"] += 1
            continue
        (dev if row["title"] in dev_titles else train).append(row)
    random.Random(20261003).shuffle(dev)
    random.Random(20261003).shuffle(train)
    splits = dict(train=train[:16384], en_dev=dev[:512], en_test=list(en), de_test=list(de))
    assert len(splits["train"]) == 16384 and len(splits["en_dev"]) == 512
    assert not {r["title"] for r in splits["train"]} & {r["title"] for r in splits["en_dev"]}
    metadata = dict(revisions=REVISIONS, config=CONFIG, removed=dict(removed), dev_titles=sorted(dev_titles),
                    counts={k:len(v) for k,v in splits.items()}, hashes={k:nli.digest(v) for k,v in splits.items()},
                    tokenizer_sha256=nli.digest(tok.get_vocab()), xquad_source_qa_ids_verified=True,
                    paired_test_ids_verified=True, source_article_disjoint=True)
    # Download the benchmark's pinned official scorer, rather than approximating it.
    url = f"https://raw.githubusercontent.com/google-research/xtreme/{SCORER_REVISION}/third_party/evaluate_squad.py"
    raw = urllib.request.urlopen(url, timeout=60).read()
    path = ROOT / "artifacts/qa_learning/evaluate_squad.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    metadata["scorer"] = dict(url=url, revision=SCORER_REVISION, sha256=hashlib.sha256(raw).hexdigest())
    module = scorer()
    assert module.f1_score("the United States", "United States") == 1
    assert module.exact_match_score("PARIS.", "Paris")
    assert module.f1_score("", "Paris") == 0
    nli.dump(DATA, dict(metadata=metadata, splits=splits))
    nli.dump(ROOT / "results/e03_data_manifest.json", metadata)
    print(json.dumps(metadata), flush=True)


def interval(values):
    import numpy as np
    values = np.array(values)
    rng = np.random.default_rng(20261003)
    draws = []
    for _ in range(100):
        indices = rng.integers(0, len(values), (100, len(values)))
        draws.extend(values[indices].mean(1).tolist())
    return np.quantile(draws, [.025, .975]).tolist()


def run(args):
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup
    payload = json.loads(DATA.read_text())
    for k,v in payload["splits"].items():
        assert nli.digest(v) == payload["metadata"]["hashes"][k]
    if args.phase == "train":
        freeze = json.loads(FREEZE.read_text())
        assert freeze["passed"] and freeze["config"] == CONFIG
        assert freeze["data_hashes"] == payload["metadata"]["hashes"]
        assert freeze["script_sha256"] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.set_num_threads(4)
    manifest = json.loads((ROOT / "artifacts/model_manifests" / f"UCLNLP__monoweb__ckpt_exp_en_de_{args.condition}.json").read_text())
    tok = AutoTokenizer.from_pretrained(manifest["path"], local_files_only=True)
    assert nli.digest(tok.get_vocab()) == payload["metadata"]["tokenizer_sha256"]
    tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    rows = [encode(r,tok) for r in payload["splits"]["train"]]
    random.Random(args.seed).shuffle(rows)
    out = ROOT / "artifacts/qa_learning" / f"{args.phase}_{args.condition}_seed{args.seed}"
    out.mkdir(parents=True, exist_ok=False)
    model = AutoModelForCausalLM.from_pretrained(manifest["path"], dtype=torch.float32,
                                               attn_implementation="sdpa", local_files_only=True).cuda()
    model.config.use_cache = False
    provenance = dict(config=CONFIG, model=manifest, metadata=payload["metadata"], seed=args.seed,
                      phase=args.phase, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      device=torch.cuda.get_device_name(), torch=torch.__version__, numpy=np.__version__,
                      git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                      train_encoded_sha256=nli.digest(rows))
    nli.dump(out / "provenance.json", provenance)
    metric_module = scorer()
    raw_scorer = ROOT / "artifacts/qa_learning/evaluate_squad.py"
    assert hashlib.sha256(raw_scorer.read_bytes()).hexdigest() == payload["metadata"]["scorer"]["sha256"]
    def evaluate(split, instruction=False):
        model.eval()
        results = []
        source = payload["splits"][split]
        maximum = model.config.max_position_embeddings-CONFIG["max_new_tokens"]
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            for start in range(0, len(source), 8):
                block = source[start:start+8]
                prefixes = [[tok.bos_token_id]+tok.encode(prompt(r,instruction),add_special_tokens=False) for r in block]
                valid = [(r,p) for r,p in zip(block,prefixes) if len(p) <= maximum]
                for row,p in zip(block,prefixes):
                    if len(p) > maximum:
                        results.append(dict(id=row["id"], prediction="", raw="", overflow=True,
                                            cap=False, f1=0., exact_match=0.))
                if not valid:
                    continue
                inputs = tok.pad({"input_ids":[p for r,p in valid]}, padding=True, return_tensors="pt").to("cuda")
                generated = model.generate(**inputs, do_sample=False, max_new_tokens=CONFIG["max_new_tokens"],
                                           use_cache=True, pad_token_id=tok.eos_token_id, eos_token_id=tok.eos_token_id,
                                           stop_strings=["\n"], tokenizer=tok)
                for (row,p), ids in zip(valid, generated[:,inputs.input_ids.shape[1]:].tolist()):
                    ended = tok.eos_token_id in ids
                    if ended:
                        ids = ids[:ids.index(tok.eos_token_id)]
                    raw = tok.decode(ids,skip_special_tokens=True)
                    prediction = raw.split("\n",1)[0].strip()
                    answers = row["answers"]["text"]
                    results.append(dict(id=row["id"], prediction=prediction, raw=raw, overflow=False,
                                        cap=not ended and len(ids) >= CONFIG["max_new_tokens"] and "\n" not in raw,
                                        f1=metric_module.metric_max_over_ground_truths(metric_module.f1_score,prediction,answers),
                                        exact_match=float(metric_module.metric_max_over_ground_truths(metric_module.exact_match_score,prediction,answers))))
        by_id = {r["id"]:r for r in results}
        results = [by_id[r["id"]] for r in source]
        metrics = dict(n=len(results), f1=sum(r["f1"] for r in results)/len(results),
                       exact_match=sum(r["exact_match"] for r in results)/len(results),
                       f1_item_bootstrap95=interval([r["f1"] for r in results]),
                       overflow=sum(r["overflow"] for r in results), cap=sum(r["cap"] for r in results),
                       empty=sum(not r["prediction"] for r in results))
        return metrics, results
    started = time.time()
    curve = []
    def snapshot(step):
        record = dict(updates=step, examples=step*16, elapsed_seconds=time.time()-started,metrics={})
        splits = ["en_dev"] if args.phase == "pilot" else ["en_dev","en_test","de_test"]
        for split in splits:
            metrics, predictions = evaluate(split)
            record["metrics"][split] = metrics
            nli.dump(out / f"predictions_{split}_{step}.json", predictions)
        curve.append(record)
        nli.dump(out / "curve.json", curve)
        nli.dump(ROOT / "results" / f"e03_{args.phase}_{args.condition}_seed{args.seed}.json",dict(provenance=provenance,curve=curve))
        print(json.dumps(record),flush=True)
    snapshot(0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=CONFIG["lr"],weight_decay=CONFIG["weight_decay"])
    scheduler = get_linear_schedule_with_warmup(optimizer, CONFIG["warmup"],CONFIG["updates"])
    losses = []
    input_tokens, answer_tokens = 0, 0
    updates = 512 if args.phase == "pilot" else 1024
    for step in range(updates):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        block = rows[step*16:(step+1)*16]
        denominator = sum(len(r["ids"])-r["prefix_length"] for r in block)
        loss_sum = 0.
        for start in range(0,16,2):
            micro = block[start:start+2]
            length = max(len(r["ids"]) for r in micro)
            ids = torch.full((len(micro),length),tok.eos_token_id,dtype=torch.long,device="cuda")
            mask = torch.zeros_like(ids)
            labels = torch.full_like(ids,-100)
            for i,row in enumerate(micro):
                n = len(row["ids"])
                ids[i,:n] = torch.tensor(row["ids"],device="cuda")
                mask[i,:n] = 1
                labels[i,row["prefix_length"]:n] = ids[i,row["prefix_length"]:n]
            with torch.autocast("cuda",dtype=torch.bfloat16):
                logits = model(input_ids=ids,attention_mask=mask).logits.float()
                loss = torch.nn.functional.cross_entropy(logits[:,:-1].reshape(-1,logits.shape[-1]),labels[:,1:].reshape(-1),reduction="sum")
            assert torch.isfinite(loss)
            (loss/denominator).backward()
            loss_sum += loss.item()
            input_tokens += mask.sum().item()
            answer_tokens += (labels[:,1:] != -100).sum().item()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(),1.)
        assert torch.isfinite(norm)
        optimizer.step()
        scheduler.step()
        losses.append(loss_sum/denominator)
        if (step+1)%16 == 0:
            nli.dump(out / "losses.json",losses)
            print(json.dumps(dict(update=step+1,loss=sum(losses[-16:])/16,elapsed_seconds=time.time()-started)),flush=True)
        if step+1 in (128,512,1024):
            snapshot(step+1)
    final = curve[-1]["metrics"]["en_dev"]
    passed = final["f1"] >= .50 and final["exact_match"] >= .35 and sum(losses[-32:]) < sum(losses[:32])
    record = dict(passed=passed, config=CONFIG, source_dev=final, input_tokens=input_tokens,answer_tokens=answer_tokens,
                  elapsed_seconds=time.time()-started,peak_gpu_bytes=torch.cuda.max_memory_allocated(),
                  script_sha256=provenance["script_sha256"],data_hashes=payload["metadata"]["hashes"])
    if args.phase == "train":
        record["instruction_control"] = {}
        for split in ("en_test","de_test"):
            metrics,predictions = evaluate(split,True)
            record["instruction_control"][split] = metrics
            nli.dump(out / f"predictions_{split}_instruction.json",predictions)
    if args.phase == "pilot" and passed:
        assert args.condition == "baseline" and args.seed == 17 and not FREEZE.exists()
        nli.dump(FREEZE,record)
    save_started = time.time()
    model.save_pretrained(out / "checkpoint",safe_serialization=True)
    tok.save_pretrained(out / "checkpoint")
    record["save_seconds"] = time.time()-save_started
    nli.dump(out / "completion.json",record)
    nli.dump(ROOT / "results" / f"e03_{args.phase}_{args.condition}_seed{args.seed}_completion.json",record)
    print("E03_COMPLETED",json.dumps(record),flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase",choices=("prepare","pilot","train"))
    parser.add_argument("--condition",choices=("baseline","monoweb","onlyparallel"),default="baseline")
    parser.add_argument("--seed",type=int,choices=(17,29,43),default=17)
    args = parser.parse_args()
    if args.phase == "prepare":
        prepare()
    else:
        run(args)
