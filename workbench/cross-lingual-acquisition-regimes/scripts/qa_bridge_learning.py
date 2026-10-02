"""E04: controlled QA bridge CPT followed by the frozen generation recipe."""
import argparse
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
import qa_learning as qa

ROOT = Path(__file__).resolve().parents[1]
CONFIG = dict(max_length=2048,micro_batch=1,accumulation=32,updates=256,
              lr=2e-5,warmup=26,weight_decay=.01)
CONDITIONS = ("new_paired","new_split","reused_paired","reused_split")


def run(args):
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup
    assert (ROOT / "results/e03_train_analysis_seed17.json").exists(), "Audit the full E03 baseline before E04 GPU work"
    freeze = json.loads(qa.FREEZE.read_text())
    assert freeze["passed"]
    assert freeze["script_sha256"] == hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest()
    payload = json.loads((ROOT / "artifacts/qa_bridge/data.json").read_text())
    metadata = payload["metadata"]
    assert metadata["task_hashes"] == freeze["data_hashes"]
    assert metadata["max_length"] == CONFIG["max_length"]
    assert metadata["unique_contexts_per_training_pool"] == 4096 and metadata["repeat_per_unit"] == 2
    for name,rows in payload["pools"].items():
        assert nli.digest(rows) == metadata["hashes"][name]
    for name in ("new","reused"):
        assert metadata["counts"][name] == 8192
        assert metadata["context_repetition"][name] == dict(unique=4096,max_questions_per_context=2)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.set_num_threads(4)
    model = AutoModelForCausalLM.from_pretrained(metadata["base_model"]["path"],dtype=torch.float32,
                                               attn_implementation="sdpa",local_files_only=True).cuda()
    model.config.use_cache = False
    check = bridge.mask_check(model,payload["pools"]["new"][0],metadata["pad"])
    if args.phase == "check":
        nli.dump(ROOT / "results/e04_mask_check.json",dict(check=check,device=torch.cuda.get_device_name(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
        print("E04_MASK_CHECK",check,flush=True)
        return
    name = f"{args.condition}_seed{args.seed}"
    out = ROOT / "artifacts/qa_bridge" / name
    out.mkdir(parents=True,exist_ok=False)
    coverage,mode = args.condition.split("_")
    rows = payload["pools"][coverage].copy()
    random.Random(args.seed).shuffle(rows)
    provenance = dict(condition=args.condition,seed=args.seed,config=CONFIG,metadata=metadata,mask_check=check,
                      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      mask_script_sha256=hashlib.sha256(Path(bridge.__file__).read_bytes()).hexdigest(),
                      qa_script_sha256=freeze["script_sha256"],encoded_order_sha256=nli.digest(rows),
                      git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                      device=torch.cuda.get_device_name(),torch=torch.__version__,numpy=np.__version__)
    nli.dump(out / "provenance.json",provenance)
    def evaluate():
        model.eval()
        total,count = 0.,0
        with torch.inference_mode(),torch.autocast("cuda",dtype=torch.bfloat16):
            for row in payload["pools"]["holdout"]:
                ids,mask,labels = bridge.batch([row],"paired",metadata["pad"],True)
                logits = model(input_ids=ids,attention_mask=mask).logits.float()
                loss = torch.nn.functional.cross_entropy(logits[:,:-1].reshape(-1,logits.shape[-1]),labels[:,1:].reshape(-1),reduction="sum")
                total += loss.item()
                count += (labels[:,1:] != -100).sum().item()
        return dict(de_conditional_nll=total/count,target_loss_tokens=count)
    started = time.time()
    before = evaluate()
    optimizer = torch.optim.AdamW(model.parameters(),lr=CONFIG["lr"],weight_decay=CONFIG["weight_decay"])
    scheduler = get_linear_schedule_with_warmup(optimizer,CONFIG["warmup"],CONFIG["updates"])
    losses,input_tokens,loss_tokens = [],0,0
    for step in range(CONFIG["updates"]):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        block = rows[step*32:(step+1)*32]
        assert len(block) == 32
        denominator = sum(len(r["ids"])-2 for r in block)
        loss_sum = 0.
        for row in block:
            ids,mask,labels = bridge.batch([row],mode,metadata["pad"])
            with torch.autocast("cuda",dtype=torch.bfloat16):
                logits = model(input_ids=ids,attention_mask=mask).logits.float()
                loss = torch.nn.functional.cross_entropy(logits[:,:-1].reshape(-1,logits.shape[-1]),labels[:,1:].reshape(-1),reduction="sum")
            assert torch.isfinite(loss)
            (loss/denominator).backward()
            loss_sum += loss.item()
            input_tokens += len(row["ids"])
            loss_tokens += len(row["ids"])-2
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(),1.)
        assert torch.isfinite(norm)
        optimizer.step()
        scheduler.step()
        losses.append(loss_sum/denominator)
        if (step+1)%16 == 0:
            nli.dump(out / "losses.json",losses)
            print(json.dumps(dict(condition=args.condition,update=step+1,loss=sum(losses[-16:])/16,
                                  elapsed_seconds=time.time()-started)),flush=True)
    after = evaluate()
    record = dict(provenance=provenance,before=before,after=after,losses=losses,input_tokens=input_tokens,
                  loss_tokens=loss_tokens,elapsed_seconds=time.time()-started,
                  peak_gpu_bytes=torch.cuda.max_memory_allocated(),finite=True,
                  loss_decreased=sum(losses[-32:]) < sum(losses[:32]))
    assert loss_tokens == sum(metadata["token_totals"][coverage].values())
    nli.dump(out / "metrics.json",record)
    save_started = time.time()
    model.save_pretrained(out / "checkpoint",safe_serialization=True)
    AutoTokenizer.from_pretrained(metadata["base_model"]["path"],local_files_only=True).save_pretrained(out / "checkpoint")
    record["save_seconds"] = time.time()-save_started
    manifest = dict(metadata["base_model"],path=str(out / "checkpoint"),parent=metadata["base_model"],
                    local_intervention=dict(condition=args.condition,seed=args.seed,data_hash=metadata["hashes"][coverage],
                                            script_sha256=provenance["script_sha256"]))
    nli.dump(ROOT / "artifacts/model_manifests" / f"UCLNLP__monoweb__ckpt_exp_en_de_e04_{args.condition}.json",manifest)
    nli.dump(ROOT / "results" / f"e04_cpt_{name}.json",record)
    del model,optimizer,scheduler,logits,loss
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    qa.run(SimpleNamespace(phase="train",condition=f"e04_{args.condition}",seed=args.seed))
    nli.dump(out / "completion.json",dict(condition=args.condition,seed=args.seed,cpt=record,
                  task_folder=f"artifacts/qa_learning/train_e04_{args.condition}_seed{args.seed}"))
    print("E04_COMPLETED",name,flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase",choices=("check","run"))
    parser.add_argument("--condition",choices=CONDITIONS,default="new_paired")
    parser.add_argument("--seed",type=int,choices=(17,29,43),default=17)
    run(parser.parse_args())
