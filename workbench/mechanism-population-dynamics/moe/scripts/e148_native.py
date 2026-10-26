"""E148 native full-model continuation and exact complete-batch order forks."""
from __future__ import annotations
import argparse
import os
_early = argparse.ArgumentParser(add_help=False)
_early.add_argument("--physical-gpu", type=int, default=0)
_early_args, _ = _early.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_early_args.physical_gpu)):
    raise ValueError("Process visibility/requested physical GPU mismatch")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_early_args.physical_gpu)

import gc
import hashlib
import json
import time
import numpy as np
import torch
import e148_common as c


def selected_tokens(plan, phase, i):
    with np.load(plan["plan_path"]) as raw:
        return raw[phase][i].copy()


@torch.no_grad()
def repeat_metrics(a, b, target):
    la, lb = a.float().log_softmax(-1), b.float().log_softmax(-1)
    values = c.old.prediction_metrics(la, lb, target)
    return {"logits_max_abs": float((a-b).float().abs().max()),
            "kl_reference_to_variant": float(values[..., 1].double().mean()),
            "nll_gap": float((values[..., 0]+la.gather(-1, target[..., None]).squeeze(-1)).double().mean())}


def preflight(plan, physical):
    lock = None
    try:
        with c.Budget("native_train_preflight") as budget:
            lock = c.old.gpu_lock(physical)
            torch.manual_seed(c.SPEC["seed"]); torch.cuda.manual_seed(c.SPEC["seed"])
            model = c.load_bf16(); model.config.use_cache = False
            tokens = torch.from_numpy(selected_tokens(plan, "warm", 0).astype(np.int64)).to("cuda:0")
            with torch.no_grad():
                original = model(input_ids=tokens[:, :-1], use_cache=False).logits
                repeated = model(input_ids=tokens[:, :-1], use_cache=False).logits
                repeat = repeat_metrics(original, repeated, tokens[:, 1:])
                del repeated
                model.float()
                via_master = c.shader(model, tokens[:, :-1]).logits
                casting = repeat_metrics(original, via_master, tokens[:, 1:])
                if repeat["logits_max_abs"] != 0 or casting["logits_max_abs"] != 0:
                    raise RuntimeError(f"Native BF16/FP32 master shader mismatch: {repeat}, {casting}")
                del original, via_master
            optimizer = c.make_optimizer(model)
            model.train()
            rows = []
            post_two_hash = None
            for i in range(8):
                budget.check()
                tokens = torch.from_numpy(selected_tokens(plan, "warm", i).astype(np.int64)).to("cuda:0")
                torch.cuda.synchronize(); started = time.monotonic()
                row = c.train_step(model, optimizer, tokens, c.SPEC["lr"], observe=i in (0, 7))
                torch.cuda.synchronize()
                row.update(step=i, seconds=time.monotonic()-started)
                rows.append(row)
                if i == 1:
                    post_two_hash = c.old.base.sampled_parameter_hash(model)
                c.emit("E148_native_preflight_update", step=i, seconds=row["seconds"], loss=row["loss"], peak_gb=torch.cuda.max_memory_allocated()/1e9)
            states = optimizer.state_dict()["state"]
            state_bytes = sum(v.numel()*v.element_size() for s in states.values() for v in s.values() if torch.is_tensor(v))
            for p in rows[0]["probes"].values():
                if p["gradient_rms"] is None or p["gradient_rms"] <= 0 or p["master_delta_rms"] <= 0:
                    raise RuntimeError("Native attention/router/expert training leverage check failed")
            total_parameters = sum(p.numel() for p in model.parameters())
            del model, optimizer, states
            gc.collect(); torch.cuda.empty_cache()
            torch.manual_seed(c.SPEC["seed"]); torch.cuda.manual_seed(c.SPEC["seed"])
            repeated_model = c.load_bf16().float().train()
            repeated_optimizer = c.make_optimizer(repeated_model)
            repeat_rows = []
            for i in range(2):
                budget.check()
                batch = torch.from_numpy(selected_tokens(plan, "warm", i).astype(np.int64)).to("cuda:0")
                repeat_rows.append(c.train_step(repeated_model, repeated_optimizer, batch, c.SPEC["lr"]))
            repeat_hash = c.old.base.sampled_parameter_hash(repeated_model)
            result = {"status": "passed", "phase": "train_side_only", "source_sha256": c.code_proof(),
                      "spec_hash": plan["spec_hash"], "plan_sha256": plan["plan_sha256"], "software": c.software(),
                      "native_repeat": repeat, "native_vs_FP32_master_BF16_shader": casting, "updates": rows,
                      "parameters": total_parameters, "trainable_parameters": sum(p.numel() for p in repeated_model.parameters() if p.requires_grad),
                      "same_two_update_repeat_sample_hash_equal": post_two_hash == repeat_hash,
                      "same_two_update_repeat_loss_gaps": [repeat_rows[i]["loss"]-rows[i]["loss"] for i in range(2)],
                      "FP32_optimizer_state_bytes": state_bytes, "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                      "physical_gpu": physical, "visible_device_uuid": str(torch.cuda.get_device_properties(0).uuid),
                      "estimated_main_train_gpu_seconds": float(np.mean([r["seconds"] for r in rows[2:]]))*1952,
                      "scope": "Discarded profiling model, not a scientific branch or held result; all costs charged."}
            c.write(c.RESULT / "preflight.json", result)
    finally:
        if lock is not None: lock.close()
    return {"status": "passed", "peak_allocated_GB": result["peak_allocated_bytes"]/1e9,
            "step_seconds": float(np.mean([r["seconds"] for r in rows[2:]])), "optimizer_state_GB": state_bytes/1e9}


def validate_ready(plan):
    tests = c.read(c.RESULT / "self_test.json")
    profile = c.read(c.RESULT / "preflight.json")
    if tests["status"] != "passed" or tests["source_sha256"] != c.code_proof() or profile["status"] != "passed" or profile["source_sha256"] != c.code_proof() or profile["plan_sha256"] != plan["plan_sha256"]:
        raise ValueError("Matching CPU and native training preflights required")


def train(plan, physical, branch):
    validate_ready(plan)
    lock = None
    summary_path = c.RESULT / ("parent.json" if branch == "parent" else f"{branch}.json")
    if summary_path.exists() and c.read(summary_path).get("status") == "complete":
        raise ValueError("Branch already complete; refusing an unrecorded repeat")
    with np.load(plan["plan_path"]) as raw:
        arrays = {k: raw[k].copy() for k in ("warm", "pulse", "suffix", "order_A", "order_B")}
    try:
        with c.Budget("train_"+branch) as budget:
            lock = c.old.gpu_lock(physical)
            torch.manual_seed(c.SPEC["seed"]); torch.cuda.manual_seed(c.SPEC["seed"])
            model = c.load_bf16().float().train(); model.config.use_cache = False
            optimizer = c.make_optimizer(model)
            result = {"status": "partial", "experiment": "E148", "branch": branch, "source_sha256": c.code_proof(),
                      "plan_sha256": plan["plan_sha256"], "spec_hash": plan["spec_hash"], "snapshots": [], "evaluations": [],
                      "physical_gpu": physical, "visible_device_uuid": str(torch.cuda.get_device_properties(0).uuid)}
            chains = {name: hashlib.sha256(("E148-"+name).encode()).hexdigest() for name in ("warm", "pulse", "suffix")}
            if branch == "parent":
                stream = [("warm", i, i+1) for i in range(32)]
            else:
                parent = c.read(c.RESULT / "parent.json")
                if parent["status"] != "complete": raise ValueError("Common parent incomplete")
                step, chains = c.restore(model, optimizer, parent["snapshots"][-1], plan)
                if step != 32: raise ValueError("Wrong common-parent update")
                # Prove loaded master parameters agree before any branch-specific update.
                loaded_hash = c.old.tensor_hash(model.state_dict())
                if loaded_hash != parent["snapshots"][-1]["state_tensor_sha256"]:
                    raise ValueError("Reloaded common parent differs")
                result["initial_parent_state_sha256"] = loaded_hash
                buffer_hash = c.old.tensor_hash(c.buffer_state(model))
                if buffer_hash != parent["snapshots"][-1]["buffer_tensor_sha256"]:
                    raise ValueError("Reloaded nonpersistent parent buffers differ")
                result["initial_parent_buffer_sha256"] = buffer_hash
                result["parent_checkpoint_sha256"] = parent["snapshots"][-1]["sha256"]
                order = arrays["order_B"] if branch == "B" else arrays["order_A"]
                stream = [("pulse", int(i), 33+j) for j, i in enumerate(order)] + [("suffix", i, 161+i) for i in range(512)]
            c.write(summary_path, result)
            directory = c.LOCAL / branch; directory.mkdir(parents=True, exist_ok=True)
            log_path = directory / "updates.jsonl"
            if log_path.exists(): raise ValueError("Existing update stream; do not silently mix attempts")
            with log_path.open("w") as log:
                for phase, index, step in stream:
                    if step % 8 == 0: budget.check()
                    values = arrays[phase][index]
                    tokens = torch.from_numpy(values.astype(np.int64)).to("cuda:0")
                    lr = c.SPEC["lr"] * min(1., step/c.SPEC["warmup_steps"])
                    row = c.train_step(model, optimizer, tokens, lr, observe=step in (1, 33, 160, 672))
                    chains[phase] = c.chain(chains[phase], values)
                    row.update(step=step, phase=phase, pool_index=index, lr=lr, tokens=1024,
                               token_batch_sha256=c.array_sha(values), phase_chain=chains[phase])
                    log.write(json.dumps(row, allow_nan=False)+"\n"); log.flush()
                    if step % 32 == 0:
                        c.emit("E148_train", branch=branch, step=step, phase=phase, ce=row["ce"], loss=row["loss"], gpu_seconds_used=budget.check())
                    if step in c.SPEC["snapshots"]:
                        budget.check()
                        optimizer.zero_grad(set_to_none=True)
                        proof = c.snapshot(model, optimizer, branch, step, plan, chains, full=step in c.SPEC["full_snapshots"])
                        result["snapshots"].append(proof)
                        evaluation = c.capture(model, branch, step, plan, budget, logits=step in (32, 160, 608, 672))
                        result["evaluations"].append(evaluation)
                        result.update(step=step, chains=dict(chains))
                        c.write(summary_path, result)
                        gc.collect()
                        c.emit("E148_snapshot", branch=branch, step=step, nll=evaluation["nll_mean"], full=step in c.SPEC["full_snapshots"])
            result.update(status="complete", step=stream[-1][-1], chains=dict(chains),
                          update_log={"path": str(log_path), "sha256": c.sha(log_path)}, peak_allocated_bytes=torch.cuda.max_memory_allocated())
            c.write(summary_path, result)
    finally:
        if lock is not None: lock.close()
    return {"status": result["status"], "branch": branch, "step": result["step"]}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("prepare", "preflight", "train"))
    p.add_argument("--physical-gpu", type=int, default=0)
    p.add_argument("--branch", choices=("parent", "A", "B", "A-repeat"), default="parent")
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    torch.set_num_threads(4)
    if args.mode == "prepare": output = c.prepare()
    else:
        plan = c.verify_plan()
        if args.mode == "preflight":
            tests = c.read(c.RESULT / "self_test.json")
            if tests["source_sha256"] != c.code_proof() or tests["status"] != "passed": raise ValueError("Known-answer CPU preflight required")
            output = preflight(plan, args.physical_gpu)
        else: output = train(plan, args.physical_gpu, args.branch)
    print(json.dumps(output, indent=2), flush=True)
