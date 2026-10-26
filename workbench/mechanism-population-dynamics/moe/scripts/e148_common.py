"""E148: full native MoE, FP32 masters and differentiable BF16 forwards.

The public optimizer state is unavailable. Adafactor defines our controlled
continuation, not an assertion about the original pretraining optimizer.
"""
from __future__ import annotations
import fcntl
import hashlib
import inspect
import json
import os
import socket
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F
from transformers import Adafactor, OlmoeForCausalLM
import transformers
import e144145_common as old

WB = Path(__file__).resolve().parents[1]
RESULT = WB / "results/e148"
LOCAL = Path("/tmp/xiang-moe-20261026/e148")
DURABLE = Path.home() / "mechpop_cache/e148_native_order_forks"
SPEC = {"experiment": "E148", "revision": "step5000-tokens20B", "seq_len": 512, "batch_size": 2,
        "microbatch": 2, "warm_steps": 32, "pulse_steps": 128, "suffix_steps": 512, "lr": 1e-5,
        "warmup_steps": 16, "grad_clip": 1., "aux_coef": .001, "layer": 9, "seed": 148,
        "optimizer": "HF_Adafactor_FP32_master", "beta1": None, "weight_decay": 0.,
        "relative_step": False, "scale_parameter": False, "held_sequences": 64, "eval_batch": 8,
        "snapshots": [32, 160, 288, 608, 672], "full_snapshots": [32, 160, 672], "max_gpu_seconds": 10800}

sha, read, write, emit = old.sha, old.read, old.write, old.emit


def code_proof():
    names = ("e148_common.py", "e148_native.py", "e148_readout.py", "e148_test.py", "e123_frozen_moe.py", "e144145_common.py")
    return {name: sha(WB / "scripts" / name) for name in names}


def software():
    return {"torch": torch.__version__, "transformers": transformers.__version__,
            "Adafactor_source_sha256": hashlib.sha256(inspect.getsource(Adafactor).encode()).hexdigest()}


def array_sha(array):
    return hashlib.sha256(np.asarray(array).astype("<u2", copy=False).tobytes()).hexdigest()


def immutable(path, value):
    old.immutable_json(path, value)


def prepare():
    assets = read(LOCAL / "model_assets.json")
    for name, record in assets["files"].items():
        path = Path(record["path"])
        if path.stat().st_size != record["size_bytes"] or sha(path) != record["sha256"]:
            raise ValueError("Staged native public model differs")
    recipe = read(old.RECIPE / "manifest.json")
    for name in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"):
        if assets["files"][name]["sha256"] != recipe["prepare_proof"]["assets"]["assets"][name]["sha256"]:
            raise ValueError("Native checkpoint/token-source tokenizer differs")
    data = old.base.TokenData(recipe["data"], 512)
    rng = np.random.default_rng(14800)
    def random_batch():
        value = data.train_batch(rng, 2).numpy().astype(np.uint16)
        return value
    warm = np.stack([random_batch() for _ in range(32)])
    suffix = np.stack([random_batch() for _ in range(512)])
    sources = sorted({r["source"] for r in data.files["train"]})
    weights = np.array([sum(p for p, r in zip(data.train_probabilities, data.files["train"]) if r["source"] == s) for s in sources])
    pulse, pulse_rows = [], []
    for index in range(128):
        source = str(rng.choice(sources, p=weights/weights.sum()))
        indices = [i for i, r in enumerate(data.files["train"]) if r["source"] == source]
        probs = data.train_probabilities[indices]; probs = probs/probs.sum()
        keys = [(int(rng.choice(indices, p=probs)), None) for _ in range(2)]
        keys = [(i, int(rng.integers(data.files["train"][i]["windows"]))) for i, _ in keys]
        pulse.append(np.stack([data.window("train", f, w) for f, w in keys]).astype(np.uint16))
        pulse_rows.append({"pool_id": index, "source": source,
                           "windows": [{"file_index": f, "file_id": data.files["train"][f]["file_id"], "window": w} for f, w in keys]})
    pulse = np.stack(pulse)
    order_a = np.array(sorted(range(128), key=lambda i: (pulse_rows[i]["source"], i)))
    order_b = np.random.default_rng(14803).permutation(128)
    legacy = set(tuple(k) for k in data.fixed_windows("held", 512, 91023))
    candidates = [(i, w) for i, r in enumerate(data.files["held"]) for w in range(r["windows"]) if (i, w) not in legacy]
    if len(candidates) < 64:
        raise ValueError("Fewer than 64 new held windows; do not silently reuse old ones")
    chosen = np.random.default_rng(14802).choice(len(candidates), 64, replace=False)
    selected = [candidates[int(i)] for i in chosen]
    held = np.stack([data.window("held", f, w) for f, w in selected]).astype(np.uint16)
    held_rows = [{"sequence": i, "source": data.files["held"][f]["source"], "file_id": data.files["held"][f]["file_id"],
                  "window": w, "tokens": 512, "token_sha256": array_sha(held[i])} for i, (f, w) in enumerate(selected)]
    cal_windows = data.fixed_windows("train", 16, 14804)
    cal = np.stack([data.window("train", f, w) for f, w in cal_windows]).astype(np.uint16)
    if any(a.max() >= 50304 for a in (warm, pulse, suffix, held, cal)):
        raise ValueError("Token IDs outside the public model vocabulary")
    plan_path = LOCAL / "plan.npz"
    if not plan_path.exists():
        np.savez(plan_path, warm=warm, pulse=pulse, suffix=suffix, held=held, cal=cal, order_A=order_a, order_B=order_b)
    else:
        with np.load(plan_path) as previous:
            for key, value in dict(warm=warm, pulse=pulse, suffix=suffix, held=held, cal=cal, order_A=order_a, order_B=order_b).items():
                if not np.array_equal(previous[key], value): raise ValueError("Refusing to change frozen E148 plan")
    proof = {"spec": SPEC, "spec_hash": old.base.digest_json(SPEC), "source_sha256": code_proof(), "software": software(),
             "model_assets": assets, "model_assets_sha256": sha(LOCAL / "model_assets.json"),
             "plan_path": str(plan_path), "plan_sha256": sha(plan_path), "data_manifest": recipe["data"],
             "data_manifest_sha256": sha(recipe["data"]), "data_provenance": data.provenance,
             "selected": held_rows, "cal_windows": [list(x) for x in cal_windows], "pulse_pool": pulse_rows,
             "phase_token_sha256": {"warm": array_sha(warm), "pulse_sorted_pool": array_sha(pulse), "suffix": array_sha(suffix), "held": array_sha(held)},
             "old_held_excluded": len(legacy), "new_held_available": len(candidates),
             "input_file_clusters": len({(r["source"], r["file_id"]) for r in held_rows}),
             "scope": "One native pretrained parent; only the order of 128 complete batches differs. A-repeat is not an independent seed. Held exclusion is relative to the specified old512, not a claim that no historical evaluation ever touched these windows."}
    immutable(RESULT / "plan.json", proof)
    return {"status": "prepared", "held_file_clusters": proof["input_file_clusters"], "new_held_available": len(candidates)}


def verify_plan():
    plan = read(RESULT / "plan.json")
    if plan["source_sha256"] != code_proof() or plan["software"] != software() or plan["spec_hash"] != old.base.digest_json(SPEC):
        raise ValueError("Frozen E148 code/software/protocol differs")
    if sha(plan["plan_path"]) != plan["plan_sha256"]:
        raise ValueError("Frozen input bytes differ")
    return plan


class Budget:
    def __init__(self, phase):
        self.phase = phase; self.identity = f"{os.getpid()}-{time.time_ns()}"; self.start = None
    def update(self, fn):
        RESULT.mkdir(parents=True, exist_ok=True)
        with (RESULT / "budget.lock").open("a+") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            path = RESULT / "budget.json"
            d = read(path) if path.exists() else {"experiment": "E148", "host": socket.gethostname(), "limit_gpu_seconds": SPEC["max_gpu_seconds"], "completed_seconds": 0., "active": {}, "attempts": []}
            if d["host"] != socket.gethostname(): raise ValueError("This budget ledger is host-local")
            result = fn(d); write(path, d); return result
    def __enter__(self):
        self.start = time.monotonic()
        self.update(lambda d: d["active"].update({self.identity: {"phase": self.phase, "started_monotonic": self.start, "pid": os.getpid()}}))
        self.check(); return self
    def check(self):
        used = self.update(lambda d: d["completed_seconds"]+sum(time.monotonic()-a["started_monotonic"] for a in d["active"].values()))
        if used >= SPEC["max_gpu_seconds"]: raise TimeoutError("E148 total three-GPU-hour package exhausted")
        return used
    def __exit__(self, kind, error, tb):
        elapsed = time.monotonic()-self.start
        def end(d):
            d["active"].pop(self.identity, None); d["completed_seconds"] += elapsed
            d["attempts"].append({"phase": self.phase, "gpu_seconds": elapsed, "status": "complete" if error is None else "failed", "error": None if error is None else str(error)})
        self.update(end)


def load_bf16():
    return OlmoeForCausalLM.from_pretrained(LOCAL / "model", dtype=torch.bfloat16, local_files_only=True,
                                           attn_implementation="sdpa").to("cuda:0").eval()


def make_optimizer(model):
    return Adafactor(model.parameters(), lr=SPEC["lr"], relative_step=False, scale_parameter=False, beta1=None,
                     weight_decay=0., eps=(1e-30, 1e-3), clip_threshold=1., decay_rate=-.8)


def shader(model, ids, *, routers=False):
    if any(p.dtype != torch.float32 for p in model.parameters()):
        raise ValueError("Native training requires FP32 master parameters")
    shadow = {name: value.to(torch.bfloat16) for name, value in model.named_parameters()}
    out = torch.func.functional_call(model, shadow, (), {"input_ids": ids, "use_cache": False, "output_router_logits": routers}, strict=False)
    if out.logits.dtype != torch.bfloat16:
        raise ValueError("Native shader/logit dtype changed")
    return out


def objective(model, tokens):
    out = shader(model, tokens[:, :-1], routers=True)
    ce = F.cross_entropy(out.logits.float().reshape(-1, out.logits.shape[-1]), tokens[:, 1:].reshape(-1))
    aux = out.aux_loss
    if aux is None: raise ValueError("Native router aux missing")
    return ce + SPEC["aux_coef"]*aux, ce, aux


def train_step(model, optimizer, tokens, lr, *, microbatch=2, observe=False):
    optimizer.zero_grad(set_to_none=True)
    for group in optimizer.param_groups: group["lr"] = lr
    metrics = np.zeros(3, np.float64)
    total = len(tokens)
    for i in range(0, total, microbatch):
        batch = tokens[i:i+microbatch]
        loss, ce, aux = objective(model, batch)
        (loss*(len(batch)/total)).backward()
        metrics += np.array([float(loss.detach()), float(ce.detach()), float(aux.detach())])*(len(batch)/total)
        del loss, ce, aux
    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), SPEC["grad_clip"], error_if_nonfinite=True)
    probes = {}
    if observe:
        for name in ("model.layers.0.self_attn.q_proj.weight", "model.layers.9.mlp.gate.weight", "model.layers.9.mlp.experts.0.up_proj.weight"):
            p = dict(model.named_parameters())[name]
            probes[name] = {"before": p.detach().clone(), "gradient_rms": float(p.grad.square().mean().sqrt()) if p.grad is not None else None}
    optimizer.step()
    for name, row in probes.items():
        p = dict(model.named_parameters())[name]
        before = row.pop("before")
        row.update(master_delta_rms=float((p-before).square().mean().sqrt()),
                   bf16_changed_fraction=float((p.bfloat16()!=before.bfloat16()).float().mean()))
    return {"loss": float(metrics[0]), "ce": float(metrics[1]), "aux": float(metrics[2]), "grad_norm_before_clip": float(grad_norm), "probes": probes}


def cpu_tree(value):
    if torch.is_tensor(value): return value.detach().cpu()
    if isinstance(value, dict): return {k: cpu_tree(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return type(value)(cpu_tree(v) for v in value)
    return value


def save_torch(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".partial")
    torch.save(obj, temp); temp.replace(path)
    return {"path": str(path), "sha256": sha(path), "size_bytes": path.stat().st_size}


def snapshot(model, optimizer, branch, step, plan, chains, *, full):
    directory = LOCAL / branch; directory.mkdir(parents=True, exist_ok=True)
    state = cpu_tree(model.state_dict()) if full else {k: v.detach().cpu() for k, v in model.state_dict().items()
        if k.startswith("model.layers.9.mlp.") or ".mlp.gate." in k}
    obj = {"schema": "E148-full-v1" if full else "E148-thin-v1", "experiment": "E148", "branch": branch, "step": step,
           "state": state, "optimizer": cpu_tree(optimizer.state_dict()) if full else None,
           "torch_rng": torch.get_rng_state(), "cuda_rng": torch.cuda.get_rng_state(0).cpu(),
           "spec_hash": plan["spec_hash"], "plan_sha256": plan["plan_sha256"], "source_sha256": code_proof(), "chains": dict(chains)}
    proof = save_torch(directory / f"{'full' if full else 'thin'}_{step:06d}.pt", obj)
    proof.update(step=step, branch=branch, schema=obj["schema"], state_tensor_sha256=old.tensor_hash(state))
    write(directory / f"snapshot_{step:06d}.json", proof)
    del obj, state
    return proof


def restore(model, optimizer, proof, plan):
    path = Path(proof["path"])
    if sha(path) != proof["sha256"]: raise ValueError("Parent checkpoint bytes differ")
    cp = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
    if cp["schema"] != "E148-full-v1" or cp["spec_hash"] != plan["spec_hash"] or cp["plan_sha256"] != plan["plan_sha256"] or cp["source_sha256"] != code_proof():
        raise ValueError("Parent endpoint/config identity differs")
    model.load_state_dict(cp["state"], strict=True)
    optimizer.load_state_dict(cp["optimizer"])
    torch.set_rng_state(cp["torch_rng"]); torch.cuda.set_rng_state(cp["cuda_rng"], device=0)
    return cp["step"], cp["chains"]


def chain(previous, tokens):
    return hashlib.sha256(bytes.fromhex(previous)+np.asarray(tokens).astype("<u2", copy=False).tobytes()).hexdigest()


@torch.no_grad()
def capture(model, branch, step, plan, budget, *, logits=True):
    model.eval()
    with np.load(plan["plan_path"]) as data:
        held, cal = data["held"], data["cal"]
    directory = LOCAL / branch; directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"logits_{step:06d}.npy"
    if logits and path.exists(): raise ValueError("Refusing to replace prediction snapshot")
    raw = np.lib.format.open_memmap(path, mode="w+", dtype=np.uint16, shape=(64, 512, 50304)) if logits else None
    nll_rows, cal_rows, hidden, weights = [], [], [], []
    for start in range(0, 64, 8):
        budget.check()
        tokens = torch.from_numpy(held[start:start+8].astype(np.int64)).to("cuda:0")
        out = shader(model, tokens[:, :-1])
        lp = out.logits.float().log_softmax(-1)
        nll_rows.extend((-lp.gather(-1, tokens[:, 1:, None]).squeeze(-1)).double().mean(-1).cpu().tolist())
        if raw is not None: raw[start:start+8] = out.logits.contiguous().view(torch.uint16).cpu().numpy()
        del out, lp, tokens
    if raw is not None: raw.flush(); del raw
    captured = {}
    def hook(module, args): captured["H"] = args[0].detach()
    handle = model.model.layers[9].mlp.register_forward_pre_hook(hook)
    try:
        for start in range(0, 16, 8):
            budget.check()
            tokens = torch.from_numpy(cal[start:start+8].astype(np.int64)).to("cuda:0")
            out = shader(model, tokens[:, :-1], routers=True)
            h = captured.pop("H").contiguous().view(torch.uint16).cpu().numpy()
            hidden.append(h)
            for layer, router in enumerate(out.router_logits):
                probs = router.float().softmax(-1)
                applied, selected = probs.topk(8, -1)
                cal_rows.append({"batch": start//8, "layer": layer,
                                 "selected": selected.cpu().numpy().astype(np.uint8),
                                 "weights": applied.bfloat16().view(torch.uint16).cpu().numpy()})
            del out, tokens
    finally: handle.remove()
    routing = directory / f"routing_{step:06d}.npz"
    np.savez_compressed(routing, H9=np.concatenate(hidden), gate9=model.model.layers[9].mlp.gate.weight.detach().cpu().numpy(),
                        selected=np.stack([x["selected"] for x in cal_rows]), weights=np.stack([x["weights"] for x in cal_rows]))
    record = {"branch": branch, "step": step, "nll_mean": float(np.mean(nll_rows)), "nll_rows": nll_rows,
              "routing": {"path": str(routing), "sha256": sha(routing)},
              "logits": {"path": str(path), "sha256": sha(path), "size_bytes": path.stat().st_size} if logits else None,
              "selected_sha256": plan["phase_token_sha256"]["held"], "source_sha256": code_proof()}
    write(directory / f"evaluation_{step:06d}.json", record)
    model.train()
    return record
