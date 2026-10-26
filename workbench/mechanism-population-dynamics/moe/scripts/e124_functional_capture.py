"""E124 fixed-input functional fingerprints; see the experiment card before use.

prepare: document-disjoint cal/held selection from E121 POS, seed=124, <=512/side.
capture: U is an equal-coefficient probe in the ORIGINAL dense background;
         A removes one actual gated contribution in the trained MoE background.
         Only the final INPUT position is changed. next_id is a target, not input.
self-test: tiny CPU hook/alignment, expert-permutation, and identical-expert tests.

Large arrays go to --output outside git; small provenance goes to --summary or
WB/results/e124/<run-id>.json. Checkpoint mmap stays on CPU; only MoE state_dict
tensors are loaded into the module, never optimizer tensors. No training occurs.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import platform
import tempfile
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import OlmoConfig, OlmoForCausalLM

from e123_frozen_moe import TensorMoE, TokenData, sampled_parameter_hash, sha256_file, write_json, digest_json

WB = Path(__file__).resolve().parents[1]
DEFAULT_ITEMS = WB / "results/e121/items_pos.jsonl"
DEFAULT_PLAN = WB / "results/e124/plan.json"


def emit(event, **values):
    print(json.dumps({"event": event, **values}, ensure_ascii=False, allow_nan=False), flush=True)


def read_items(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def item_hash(item):
    return digest_json({"ids": item["ids"], "next_id": item["next_id"], "word": item["word"],
                        "label": item["label"], "sent": item["sent"]})


def prepare(args):
    source = Path(args.items).resolve()
    items = read_items(source)
    documents = sorted({item["sent"].rsplit("-", 1)[0] for item in items})
    rng = np.random.default_rng(args.sample_seed)
    shuffled = rng.permutation(len(documents))
    assignment = {documents[int(index)]: "cal" if rank % 2 == 0 else "held"
                  for rank, index in enumerate(shuffled)}
    selected = {}
    coverage = {}
    for split in ("cal", "held"):
        eligible = [i for i, item in enumerate(items) if assignment[item["sent"].rsplit("-", 1)[0]] == split]
        chosen = sorted(int(i) for i in rng.choice(eligible, min(args.samples_per_split, len(eligible)), replace=False))
        selected[split] = chosen
        words = sorted({items[i]["word"] for i in chosen})
        coverage[split] = {"items": len(chosen), "eligible_items": len(eligible), "words": words,
                           "documents": len({items[i]["sent"].rsplit("-", 1)[0] for i in chosen}),
                           "conditions": {label: sum(items[i]["label"] == label for i in chosen)
                                          for label in sorted({items[i]["label"] for i in chosen})}}
    plan = {"schema": 1, "source": str(source), "source_sha256": sha256_file(source),
            "sample_seed": args.sample_seed, "samples_per_split": args.samples_per_split,
            "document_definition": "sent.rsplit('-',1)[0]", "document_assignment": assignment,
            "selected_indices": selected, "coverage": coverage,
            "selected_inputs_sha256": digest_json([(i, item_hash(items[i])) for side in ("cal", "held") for i in selected[side]]),
            "sampling_note": "all E121 POS rows; original cal/held ignored; no outcome-based filtering",
            "script_sha256": sha256_file(__file__)}
    target = Path(args.plan)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        previous = json.loads(target.read_text())
        # Code provenance is not sampling identity; preserve an already fixed plan.
        without_code = lambda value: {key: item for key, item in value.items() if key != "script_sha256"}
        if without_code(previous) != without_code(plan):
            raise ValueError(f"Refusing to overwrite a different sample plan: {target}")
        emit("plan_reused", plan=str(target), selected_inputs_sha256=previous["selected_inputs_sha256"])
        return previous
    write_json(target, plan)
    emit("prepared", plan=str(target), coverage=coverage, selected_inputs_sha256=plan["selected_inputs_sha256"])
    return plan


def load_plan(path):
    plan = json.loads(Path(path).read_text())
    source = Path(plan["source"])
    if sha256_file(source) != plan["source_sha256"]:
        raise ValueError("POS source hash no longer matches fixed plan")
    items = read_items(source)
    chosen, metadata = [], []
    seen_documents = {"cal": set(), "held": set()}
    for split in ("cal", "held"):
        for index in plan["selected_indices"][split]:
            item = items[index]
            document = item["sent"].rsplit("-", 1)[0]
            if plan["document_assignment"][document] != split:
                raise ValueError("Plan selected an item from the wrong document split")
            seen_documents[split].add(document)
            chosen.append(item)
            metadata.append({"item_id": index, "split": split, "word": item["word"],
                             "label": item["label"], "document": document, "input_sha256": item_hash(item)})
    if seen_documents["cal"] & seen_documents["held"]:
        raise ValueError("Document overlap across calibration and held")
    signature = digest_json([(row["item_id"], row["input_sha256"]) for row in metadata])
    if signature != plan["selected_inputs_sha256"]:
        raise ValueError("Selected input content differs from the fixed plan")
    return plan, chosen, metadata


def batches(items, batch_size, device, pad_id):
    for start in range(0, len(items), batch_size):
        chunk = items[start:start + batch_size]
        width = max(len(item["ids"]) for item in chunk)
        ids = torch.full((len(chunk), width), pad_id, dtype=torch.long, device=device)
        mask = torch.zeros_like(ids)
        last = torch.tensor([len(item["ids"]) - 1 for item in chunk], device=device)
        for row, item in enumerate(chunk):
            ids[row, :len(item["ids"])] = torch.tensor(item["ids"], device=device)
            mask[row, :len(item["ids"])] = 1
        # The only model input is the recorded left prefix (including target word).
        target = torch.tensor([item["next_id"] for item in chunk], device=device)
        yield start, ids, mask, last, target


def amp(args):
    return torch.autocast("cuda", dtype=getattr(torch, args.dtype)) if args.device.startswith("cuda") and args.dtype != "float32" else contextlib.nullcontext()


def target_log_prob(model, ids, mask, last, targets, args):
    with amp(args):
        hidden = model.model(input_ids=ids, attention_mask=mask, use_cache=False).last_hidden_state
    # Final vocabulary projection is fp32, not merely a cast of bf16 logits.
    at_target_hidden = hidden[torch.arange(len(ids), device=ids.device), last].float()
    at_target = F.linear(at_target_hidden, args._head_weight_fp32, args._head_bias_fp32)
    return F.log_softmax(at_target, dim=-1).gather(1, targets[:, None])[:, 0]


class MeasuredMoE(TensorMoE):
    """The ordinary HF path plus a weight-zero intervention with no renormalizing.

    The drop/identity path repeats the HF block algebra and expert batch shapes;
    dropping sets ONE original selected weight to zero before accumulation.
    This avoids subtracting a rounded contribution from a bf16 aggregate.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.measurement = {}

    def forward(self, hidden_states):
        context = self.measurement
        if not context.get("intervention"):
            return super().forward(hidden_states)
        batch_size, sequence_length, hidden_dim = hidden_states.shape
        flat = hidden_states.view(-1, hidden_dim)
        logits = self.block.gate(flat)
        self.last_router_logits = logits
        weights = F.softmax(logits, dim=1, dtype=torch.float32)
        weights, selected = torch.topk(weights, self.block.top_k, dim=-1)
        if self.block.norm_topk_prob:
            raise ValueError("E124 requires no top-k renormalization")
        if context.get("drop_slot") is not None:
            weights = weights.clone()
            target_rows = torch.arange(batch_size, device=flat.device) * sequence_length + context["last"]
            weights[target_rows, context["drop_slot"]] = 0
        weights = weights.to(flat.dtype)
        result = torch.zeros_like(flat)
        expert_mask = F.one_hot(selected, num_classes=self.block.num_experts).permute(2, 1, 0)
        for expert_index in range(self.block.num_experts):
            slot, token_row = torch.where(expert_mask[expert_index])
            current = flat[None, token_row].reshape(-1, hidden_dim)
            values = self.block.experts[expert_index](current) * weights[token_row, slot, None]
            result.index_add_(0, token_row, values.to(flat.dtype))
        return result.reshape(batch_size, sequence_length, hidden_dim)


def dense_probe_hook(moe, context):
    def hook(module, inputs, output):
        hidden = inputs[0]
        if "calibration" in context:
            context["calibration"].append(hidden[:, ::context["cal_stride"]].detach().float().cpu().reshape(-1, hidden.shape[-1]))
            return output
        rows, last = context["rows"], context["last"]
        if context["mode"] == "dense":
            context["Htarget"] = hidden[rows, last].detach().float().cpu()
            return output
        changed = output.clone()
        if context["mode"] == "zero":
            changed[rows, last] = 0
        elif context["mode"] == "identity":
            changed[rows, last] = output[rows, last] + torch.zeros_like(output[rows, last])
        elif context["mode"] == "inject":
            contribution = moe.block.experts[context["expert"]](hidden[rows, last])
            changed[rows, last] = context["alpha"] * contribution
        else:
            raise ValueError(context["mode"])
        return changed
    return hook


def tensor_state_hash(state):
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        value = tensor.detach().cpu().contiguous()
        digest.update(f"{name}|{tuple(value.shape)}|{value.dtype}".encode())
        digest.update(value.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def resolve_output(args):
    path = Path(args.output).expanduser().resolve()
    return path if path.suffix == ".npz" else path / "capture.npz"


@torch.no_grad()
def capture(args):
    output = resolve_output(args)
    if output.exists():
        raise FileExistsError(f"Capture output already exists: {output}")
    started = time.monotonic()
    plan, items, metadata = load_plan(args.plan)
    if not items:
        raise ValueError("Plan contains no inputs")
    dtype = getattr(torch, args.dtype)
    if args.device == "cpu" and dtype != torch.float32:
        raise ValueError("CPU captures/self-tests require float32")
    model = OlmoForCausalLM.from_pretrained(args.model, dtype=dtype, local_files_only=True,
                                          attn_implementation="sdpa").to(args.device).eval()
    model.requires_grad_(False)
    model.config.use_cache = False
    args._head_weight_fp32 = model.lm_head.weight.detach().float()
    args._head_bias_fp32 = model.lm_head.bias.detach().float() if model.lm_head.bias is not None else None
    dense = model.model.layers[args.layer].mlp
    if dense.up_proj.out_features != args.top_k * args.expert_size:
        raise ValueError("Expert active width differs from dense FFN width")
    if any(max(item["ids"]) >= model.config.vocab_size or item["next_id"] >= model.config.vocab_size for item in items):
        raise ValueError("Sample tokenizer IDs exceed backbone vocabulary")
    prefix = f"model.layers.{args.layer}.mlp."
    backbone_hash = sampled_parameter_hash(model, prefix)
    # mmap keeps optimizer storages on CPU; only the MoE state is dereferenced.
    checkpoint = torch.load(args.checkpoint, map_location="cpu", mmap=True, weights_only=False)
    checkpoint_step = int(checkpoint["step"])
    if checkpoint.get("frozen_sample_hash") and checkpoint["frozen_sample_hash"] != backbone_hash:
        raise ValueError("Checkpoint frozen backbone fingerprint does not match loaded dense model")
    moe_state = checkpoint["moe"]
    moe_hash = tensor_state_hash(moe_state)
    moe = MeasuredMoE(model.config.hidden_size, args.expert_size, args.experts, args.top_k, .02)
    moe.load_state_dict(moe_state, strict=True)
    moe = moe.to(args.device).eval()
    moe.requires_grad_(False)
    checkpoint_config_hash = checkpoint.get("config_hash")
    del moe_state, checkpoint
    provenance_path = Path(args.checkpoint).parent / "provenance.json"
    checkpoint_provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {}
    training_args = checkpoint_provenance.get("args", {})
    load_seconds = time.monotonic() - started
    count, experts, top_k = len(items), args.experts, args.top_k
    arrays = {"U": np.zeros((count, experts), np.float32), "A": np.zeros((count, experts), np.float32),
              "inject_target_log_prob_fp32": np.zeros((count, experts), np.float32),
              "drop_target_log_prob_fp32": np.zeros((count, experts), np.float32),
              "dense_nll": np.zeros(count, np.float32), "zero_nll": np.zeros(count, np.float32),
              "normal_nll": np.zeros(count, np.float32),
              "Htarget": np.zeros((count, model.config.hidden_size), np.float32),
              "selected_experts": np.zeros((count, top_k), np.int64),
              "selected_weights": np.zeros((count, top_k), np.float32),
              "selected_mask": np.zeros((count, experts), bool),
              "gate_weights": np.zeros((count, experts), np.float32),
              "gate": moe.block.gate.weight.detach().float().cpu().numpy().copy()}
    noise = {name: np.zeros(count, np.float32) for name in
             ("dense_identity_lp", "zero_repeat_lp", "inject_repeat_lp", "natural_repeat_lp", "natural_identity_lp")}
    context = {"alpha": args.alpha}
    hook = dense.register_forward_hook(dense_probe_hook(moe, context))
    u_started = time.monotonic()
    try:
        for start, ids, mask, last, target in batches(items, args.batch_size, args.device, model.config.pad_token_id or 1):
            end = start + len(ids)
            context.update({"rows": torch.arange(len(ids), device=args.device), "last": last, "mode": "dense"})
            original_lp = target_log_prob(model, ids, mask, last, target, args)
            arrays["Htarget"][start:end] = context["Htarget"].numpy()
            arrays["dense_nll"][start:end] = -original_lp.cpu().numpy()
            context["mode"] = "identity"
            noise["dense_identity_lp"][start:end] = (target_log_prob(model, ids, mask, last, target, args) - original_lp).cpu().numpy()
            context["mode"] = "zero"
            zero_lp = target_log_prob(model, ids, mask, last, target, args)
            arrays["zero_nll"][start:end] = -zero_lp.cpu().numpy()
            noise["zero_repeat_lp"][start:end] = (target_log_prob(model, ids, mask, last, target, args) - zero_lp).cpu().numpy()
            context["mode"] = "inject"
            for expert in range(experts):
                context["expert"] = expert
                injected_lp = target_log_prob(model, ids, mask, last, target, args)
                arrays["inject_target_log_prob_fp32"][start:end, expert] = injected_lp.cpu().numpy()
                arrays["U"][start:end, expert] = (injected_lp - zero_lp).cpu().numpy()
                if expert == 0:
                    noise["inject_repeat_lp"][start:end] = (target_log_prob(model, ids, mask, last, target, args) - injected_lp).cpu().numpy()
            emit("U_batch", completed=end, total=count)
        u_seconds = time.monotonic() - u_started
        hcal = []
        hcal_meta = None
        if args.data and args.cal_sequences:
            data = TokenData(args.data, args.seq_len)
            windows = data.fixed_windows("train", args.cal_sequences, args.cal_seed)
            context.clear()
            # An explicit flag is used because an empty collection is falsey.
            context.update({"calibration": hcal, "cal_stride": args.cal_stride, "mode": "collect_cal"})
            for batch, _ in data.iter_fixed("train", windows, args.batch_size):
                with amp(args):
                    model.model(input_ids=batch[:, :-1].to(args.device), use_cache=False)
            hcal_meta = {"data_manifest_sha256": sha256_file(args.data) if Path(args.data).is_file() else None,
                         "data_identity_sha256": digest_json(data.provenance), "window_hash": digest_json(windows),
                         "windows": windows, "split": "train", "cal_seed": args.cal_seed,
                         "seq_len": args.seq_len, "stride": args.cal_stride}
        arrays["Hcal"] = torch.cat(hcal).numpy() if hcal else np.empty((0, model.config.hidden_size), np.float32)
    finally:
        hook.remove()
    a_started = time.monotonic()
    model.model.layers[args.layer].mlp = moe
    for start, ids, mask, last, target in batches(items, args.batch_size, args.device, model.config.pad_token_id or 1):
        end = start + len(ids)
        moe.measurement = {}
        normal_lp = target_log_prob(model, ids, mask, last, target, args)
        logits = moe.last_router_logits.reshape(len(ids), ids.shape[1], experts)[torch.arange(len(ids), device=args.device), last].float()
        weights, selected = logits.softmax(-1).topk(top_k, dim=-1)
        selected_cpu = selected.cpu().numpy()
        arrays["normal_nll"][start:end] = -normal_lp.cpu().numpy()
        arrays["selected_experts"][start:end] = selected_cpu
        arrays["selected_weights"][start:end] = weights.cpu().numpy()
        np.put_along_axis(arrays["selected_mask"][start:end], selected_cpu, True, axis=1)
        np.put_along_axis(arrays["gate_weights"][start:end], selected_cpu, weights.cpu().numpy(), axis=1)
        arrays["drop_target_log_prob_fp32"][start:end] = normal_lp.cpu().numpy()[:, None]
        noise["natural_repeat_lp"][start:end] = (target_log_prob(model, ids, mask, last, target, args) - normal_lp).cpu().numpy()
        moe.measurement = {"intervention": True, "drop_slot": None, "last": last}
        noise["natural_identity_lp"][start:end] = (target_log_prob(model, ids, mask, last, target, args) - normal_lp).cpu().numpy()
        for slot in range(top_k):
            moe.measurement["drop_slot"] = slot
            dropped_lp = target_log_prob(model, ids, mask, last, target, args)
            values = (normal_lp - dropped_lp).cpu().numpy()
            arrays["A"][np.arange(start, end), selected_cpu[:, slot]] = values
            arrays["drop_target_log_prob_fp32"][np.arange(start, end), selected_cpu[:, slot]] = dropped_lp.cpu().numpy()
        emit("A_batch", completed=end, total=count)
    a_seconds = time.monotonic() - a_started
    model.model.layers[args.layer].mlp = dense
    if sampled_parameter_hash(model, prefix) != backbone_hash:
        raise RuntimeError("Frozen backbone parameters changed during capture")
    for key in ("word", "label", "split", "document", "input_sha256"):
        arrays[key] = np.array([row[key] for row in metadata], dtype=str)
    arrays["item_id"] = np.array([row["item_id"] for row in metadata], np.int64)
    arrays.update({"noise_" + key: value for key, value in noise.items()})
    run_id = args.run_id or (output.parent.name if output.name == "capture.npz" else output.stem)
    run_metadata = {"schema": 1, "run_id": run_id, "alpha": args.alpha, "layer": args.layer,
                    "experts": experts, "top_k": top_k, "step": checkpoint_step,
                    "seed": args.seed if args.seed is not None else training_args.get("seed"),
                    "order_seed": args.order_seed if args.order_seed is not None else training_args.get("order_seed"),
                    "model": str(Path(args.model).resolve()), "checkpoint": str(Path(args.checkpoint).resolve()),
                    "checkpoint_config_hash": checkpoint_config_hash, "checkpoint_moe_tensor_sha256": moe_hash,
                    "checkpoint_file_bytes": Path(args.checkpoint).stat().st_size,
                    "backbone_sample_hash": backbone_hash, "plan_sha256": sha256_file(args.plan),
                    "source_sha256": plan["source_sha256"], "selected_inputs_sha256": plan["selected_inputs_sha256"],
                    "script_sha256": sha256_file(__file__), "e123_script_sha256": sha256_file(WB / "scripts/e123_frozen_moe.py"),
                    "hcal": hcal_meta, "device": args.device, "dtype": args.dtype, "torch": torch.__version__,
                    "readout_precision": "backbone/expert forward in selected dtype; last hidden cast to fp32 before F.linear with fp32 lm_head and fp32 log_softmax",
                    "hardware": torch.cuda.get_device_name(args.device) if args.device.startswith("cuda") else platform.processor(),
                    "U_scope": "dense background; target FFN output=alpha*expert; U=NLL(target FFN zero)-NLL(injection); probe, not natural role",
                    "A_scope": "trained MoE background; zero original target top-k weight without renormalization; A=NLL(drop)-NLL(normal)",
                    "unselected_drop_lp_note": "unselected A=0; drop log-prob filled with normal log-prob; use selected_mask",
                    "noise": {key: {"mean_abs": float(np.abs(value).mean()), "max_abs": float(np.abs(value).max())}
                              for key, value in noise.items()},
                    "timing": {"load_seconds": load_seconds, "U_seconds": u_seconds, "A_seconds": a_seconds,
                               "total_before_save_seconds": time.monotonic() - started}}
    arrays["metadata_json"] = np.array(json.dumps(run_metadata, ensure_ascii=False, allow_nan=False))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        np.savez(handle, **arrays)
    summary = {**run_metadata, "output": str(output), "shapes": {key: list(value.shape) for key, value in arrays.items()},
               "baseline_nll": {key: float(arrays[key].mean()) for key in ("dense_nll", "zero_nll", "normal_nll")},
               "coverage": plan["coverage"], "output_bytes": output.stat().st_size,
               "total_seconds": time.monotonic() - started}
    summary_path = Path(args.summary) if args.summary else WB / "results/e124" / f"{run_id}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(summary_path, summary)
    emit("captured", output=str(output), summary=str(summary_path), total_seconds=summary["total_seconds"])
    return arrays, summary


def parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=("prepare", "capture", "self-test"), required=True)
    ap.add_argument("--model", "--model-dir", dest="model")
    ap.add_argument("--checkpoint")
    ap.add_argument("--output")
    ap.add_argument("--summary")
    ap.add_argument("--plan", default=str(DEFAULT_PLAN))
    ap.add_argument("--items", default=str(DEFAULT_ITEMS))
    ap.add_argument("--sample-seed", type=int, default=124)
    ap.add_argument("--samples-per-split", type=int, default=512)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--dtype", choices=("float32", "bfloat16"), default="bfloat16")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--layer", type=int, default=9)
    ap.add_argument("--experts", type=int, default=64)
    ap.add_argument("--expert-size", type=int, default=1024)
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--alpha", type=float, default=1 / 8)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--order-seed", type=int)
    ap.add_argument("--run-id")
    ap.add_argument("--data", default=str(WB / "results/e123/manifest.json"), help="Empty string disables optional shared Hcal")
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--cal-sequences", type=int, default=64)
    ap.add_argument("--cal-seed", type=int, default=91024)
    ap.add_argument("--cal-stride", type=int, default=4)
    return ap


def self_test():
    torch.set_num_threads(1)
    with tempfile.TemporaryDirectory(prefix="e124_cpu_") as directory:
        root = Path(directory)
        rng = np.random.default_rng(124)
        rows = []
        for document in range(10):
            for condition in range(2):
                rows.append({"sent": f"doc{document}-00{condition}", "word": "w" + str(document % 2),
                             "label": "NOUN" if condition == 0 else "VERB", "split": "original_unused",
                             "ids": rng.integers(3, 40, 3 + document % 4).tolist(), "next_id": 63})
        source = root / "items.jsonl"
        source.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        for split in ("train", "held"):
            np.save(root / f"{split}.npy", rng.integers(3, 40, 90, dtype=np.uint16))
        plan_path = root / "plan.json"
        prepare(parser().parse_args(["--mode", "prepare", "--items", str(source), "--plan", str(plan_path), "--samples-per-split", "4"]))
        torch.manual_seed(124)
        config = OlmoConfig(vocab_size=64, hidden_size=16, intermediate_size=32, num_hidden_layers=2,
                            num_attention_heads=4, num_key_value_heads=4, max_position_embeddings=32,
                            attention_dropout=0., pad_token_id=1, eos_token_id=2)
        base = OlmoForCausalLM(config).eval()
        base.save_pretrained(root / "model")
        moe = MeasuredMoE(16, 16, 4, 2, .02)
        original_state = {key: value.detach().clone() for key, value in moe.state_dict().items()}
        checkpoints = {}
        permutation = [2, 0, 3, 1]
        for name in ("original", "permuted", "identical"):
            state = {key: value.clone() for key, value in original_state.items()}
            if name == "permuted":
                state["block.gate.weight"] = original_state["block.gate.weight"][permutation].clone()
                for expert in range(4):
                    for component in ("up_proj", "gate_proj", "down_proj"):
                        state[f"block.experts.{expert}.{component}.weight"] = original_state[f"block.experts.{permutation[expert]}.{component}.weight"].clone()
            elif name == "identical":
                for expert in range(4):
                    for component in ("up_proj", "gate_proj", "down_proj"):
                        state[f"block.experts.{expert}.{component}.weight"] = original_state[f"block.experts.0.{component}.weight"].clone()
            checkpoints[name] = root / f"{name}.pt"
            torch.save({"step": 3, "moe": state, "optimizer": {"cpu_only_sentinel": torch.ones(2)}}, checkpoints[name])
        captured = {}
        for name, checkpoint in checkpoints.items():
            args = parser().parse_args(["--mode", "capture", "--model", str(root / "model"),
                                       "--checkpoint", str(checkpoint), "--output", str(root / f"{name}.npz"),
                                       "--summary", str(root / f"{name}.json"), "--plan", str(plan_path),
                                       "--device", "cpu", "--dtype", "float32", "--layer", "1", "--experts", "4",
                                       "--expert-size", "16", "--top-k", "2", "--batch-size", "3", "--data", str(root),
                                       "--seq-len", "8", "--cal-sequences", "2", "--cal-stride", "2"])
            captured[name], _ = capture(args)
        first, second, identical = captured["original"], captured["permuted"], captured["identical"]
        errors = {key: float(np.max(np.abs(first[key][:, permutation] - second[key]))) for key in ("U", "A", "gate_weights")}
        if max(errors.values()) > 1e-6:
            raise AssertionError(f"Expert permutation changed functional fingerprint: {errors}")
        if not np.array_equal(first["selected_mask"][:, permutation], second["selected_mask"]):
            raise AssertionError("Selected mask did not follow expert permutation")
        identical_u_error = float(np.max(np.abs(identical["U"] - identical["U"][:, :1])))
        if identical_u_error != 0 or np.any(first["A"][~first["selected_mask"]] != 0):
            raise AssertionError("Identical-expert or unselected-zero known answer failed")
        if first["Hcal"].shape != (8, 16) or not np.isfinite(first["Hcal"]).all():
            raise AssertionError(f"Shared train calibration/stride count failed: {first['Hcal'].shape}")
        # Independent unpadded single-input pre-hooks verify padded last-position indexing.
        _, selected_items, _ = load_plan(plan_path)
        saved = []
        handle = base.model.layers[1].mlp.register_forward_pre_hook(lambda module, inputs: saved.append(inputs[0][:, -1].detach().clone()))
        with torch.no_grad():
            for item in selected_items:
                ids = torch.tensor([item["ids"]])
                if torch.any(ids == 63):
                    raise AssertionError("Synthetic future token entered the input")
                base(input_ids=ids, use_cache=False)
        handle.remove()
        h_error = float(np.max(np.abs(torch.cat(saved).numpy() - first["Htarget"])))
        if h_error > 1e-5:
            raise AssertionError(f"Target capture was not the last INPUT position: {h_error}")
        noise = {key: float(np.max(np.abs(first[key]))) for key in first if key.startswith("noise_")}
        if max(noise.values()) > 1e-6:
            raise AssertionError(f"Identity/repeat numerical check failed: {noise}")
        result = {"passed": True, "device": "cpu", "script_sha256": sha256_file(__file__),
                  "e123_script_sha256": sha256_file(WB / "scripts/e123_frozen_moe.py"),
                  "permutation_max_errors": errors, "identical_experts_U_column_difference": identical_u_error,
                  "last_input_Htarget_max_error": h_error, "repeat_identity_noise": noise,
                  "Hcal_shape": list(first["Hcal"].shape),
                  "checks": ["document-disjoint fixed plan", "next_id excluded from model input",
                             "last input position under variable padding", "gate+expert permutation equivariance",
                             "identical experts have identical U", "unselected A=0", "CPU mmap checkpoint MoE-only load",
                             "Hcal collected from train windows with exact stride count", "fp32 last-position vocabulary projection"]}
        destination = WB / "results/e124/self_test.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_json(destination, result)
        emit("self_test_passed", **result)
        return result


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "prepare":
        prepare(args)
    elif args.mode == "self-test":
        self_test()
    else:
        if not args.model or not args.checkpoint or not args.output:
            raise ValueError("capture requires --model, --checkpoint and --output")
        if args.alpha != 1 / 8:
            raise ValueError("E124 predeclares alpha=1/8")
        capture(args)
