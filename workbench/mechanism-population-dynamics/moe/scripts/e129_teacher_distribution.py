"""E129: one teacher-KL oracle diagnostic, not a replacement for the CE cohort.
Same E125 initialization/data/schedule; KL(q_dense || p_student), temperature 1,
sum over vocabulary then MEAN OVER TOKENS. GT CE is logged separately.
"""
import hashlib
import json
import random
import tempfile
import time
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoConfig, OlmoForCausalLM
import e123_frozen_moe as base
import e125_coverage_control as control
import e127_predictive_fidelity as fidelity
from e124_functional_capture import batches, tensor_state_hash

WB = Path(__file__).resolve().parents[1]
MATCH = ("seed", "order_seed", "layer", "experts", "expert_size", "top_k", "init_std", "steps", "seq_len",
         "batch_size", "accum", "lr", "warmup_fraction", "weight_decay", "lb_coef", "z_coef", "grad_clip",
         "dtype", "eval_sequences", "eval_seed", "eval_every", "max_train_tokens")


def log_probs(model, ids, args, mask=None, last=None):
    logits = base.forward_logits(model, ids, args, mask)
    if last is not None:
        logits = logits[torch.arange(len(ids), device=ids.device), last]
    return logits.float().log_softmax(-1)


def kl_tokens(q, p):
    return (q.exp() * (q - p)).sum(-1)


def replay_batch(data, rng, size):
    chosen = rng.source.choice(len(data.files["train"]), size=size, p=data.train_probabilities)
    return torch.from_numpy(np.stack([data.window("train", int(i), int(rng.window.integers(data.files["train"][i]["windows"]))) for i in chosen]))


def chain(previous, batch):
    return hashlib.sha256(bytes.fromhex(previous) + batch.numpy().astype("<i8", copy=False).tobytes()).hexdigest()


@torch.no_grad()
def measure(model, original, moe, data, windows, items, args):
    rows, pos_rows = [], []
    for batch, metadata in data.iter_fixed("held", windows, args.batch_size):
        batch = batch.to(args.device)
        model.model.layers[args.layer].mlp = original
        q = log_probs(model, batch[:, :-1], args)
        model.model.layers[args.layer].mlp = moe
        p = log_probs(model, batch[:, :-1], args)
        sums = fidelity.token_metrics(q, p, batch[:, 1:]).double().sum(1).cpu().tolist()
        rows.extend({**meta, "tokens": args.seq_len, **dict(zip(fidelity.METRICS, values))} for meta, values in zip(metadata, sums))
    for start, ids, mask, last, targets in batches(items, args.batch_size, args.device, model.config.pad_token_id or 1):
        model.model.layers[args.layer].mlp = original
        q = log_probs(model, ids, args, mask, last)
        model.model.layers[args.layer].mlp = moe
        p = log_probs(model, ids, args, mask, last)
        values = fidelity.token_metrics(q, p, targets).cpu().tolist()
        pos_rows.extend({"word": item["word"], "label": item["label"], **dict(zip(fidelity.METRICS, v))} for item, v in zip(items[start:start + len(ids)], values))
    def word_summary(selected):
        groups = {}
        for row in selected:
            groups.setdefault(row["word"], []).append([row[k] for k in fidelity.METRICS])
        balanced = [{"source": "POS", "file_id": word, "tokens": 1, **dict(zip(fidelity.METRICS, np.mean(values, axis=0)))} for word, values in groups.items()]
        return fidelity.summarize(balanced, args.bootstrap) if balanced else None
    summary = {"held": fidelity.summarize(rows, args.bootstrap), "POS_word_balanced": word_summary(pos_rows),
               "POS_conditions": {label: word_summary([r for r in pos_rows if r["label"] == label]) for label in sorted({r["label"] for r in pos_rows})},
               "POS_ci_unit": "word form", "scope": "oracle function learning diagnostic; not label-noise attribution or CE-cohort substitution"}
    return summary, rows, pos_rows


def gradient_audit(main, lb, z, moe):
    gate = moe.block.gate.weight
    selected = moe.last_router_logits.detach().topk(moe.block.top_k, -1).indices.flatten().bincount(minlength=moe.block.num_experts).argmax()
    expert = moe.block.experts[int(selected)].up_proj.weight
    result = {}
    for name, objective, parameters in (("kl", main, [gate, expert]), ("lb", lb, [gate]), ("z", z, [gate])):
        values = torch.autograd.grad(objective, parameters, retain_graph=True, allow_unused=True)
        norms = [float(v.float().norm()) if v is not None else 0. for v in values]
        if any(not np.isfinite(v) or v == 0 for v in norms):
            raise RuntimeError(f"Missing/nonfinite {name} gradient: {norms}")
        result[name + "_gradient_norms"] = norms
    return result


def run(args):
    if args.replacement != "moe":
        raise ValueError("E129 is the single original 64top8 MoE diagnostic")
    started = time.monotonic()
    output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
    if (output / "checkpoint.pt").exists() and not args.resume:
        raise ValueError("Existing checkpoint requires explicit --resume")
    reference = json.loads(Path(args.ce_reference).read_text())
    if any(getattr(args, k) != reference["args"][k] for k in MATCH):
        raise ValueError("KL diagnostic differs from matched CE training protocol")
    data = control.CoverageTokenData(args.data, args.seq_len, args.token_dtype)
    identity = lambda entries: [(r["source"], r["file_id"], r["sha256"], r["windows"], r["sampling_weight"]) for r in entries]
    if any(identity(data.provenance[s]) != identity(reference["data"][s]) for s in ("train", "held")):
        raise ValueError("Data content/order/probabilities differ from CE reference")
    source_log = Path(args.ce_source_log or Path(reference["args"]["output"]) / "train_steps.jsonl")
    ce_sources = {r["step"]: r["coverage"]["source_schedule_hash"] for r in map(json.loads, source_log.read_text().splitlines())}
    if any(step not in ce_sources for step in range(1, args.steps + 1)):
        raise ValueError("Complete matched CE source-schedule log is required")
    windows = data.fixed_windows("held", args.eval_sequences, args.eval_seed)
    if base.digest_json(windows) != reference["held_window_hash"]:
        raise ValueError("Held evaluation windows differ from CE reference")
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    model = OlmoForCausalLM.from_pretrained(args.model, local_files_only=True, dtype=getattr(torch, args.dtype), attn_implementation="sdpa").to(args.device).eval()
    model.requires_grad_(False)
    original = model.model.layers[args.layer].mlp
    frozen_hash = base.sampled_parameter_hash(model, f"model.layers.{args.layer}.mlp.")
    teacher_hash = base.sampled_parameter_hash(model)
    moe = control.build_replacement(model, args)
    initial_hash = tensor_state_hash(moe.state_dict())
    if initial_hash != reference["initial_tensor_sha256"] or frozen_hash != reference["frozen_sample_hash"]:
        raise ValueError("Initialization/frozen backbone differs from matched CE")
    moe = moe.to(args.device).train(); moe.requires_grad_(True)
    model.model.layers[args.layer].mlp = moe
    optimizer = torch.optim.AdamW(moe.parameters(), lr=args.lr, betas=(.9, .95), eps=1e-8, weight_decay=args.weight_decay)
    stream, replay = control.SplitStream(args.order_seed), control.SplitStream(args.order_seed)
    input_hash = hashlib.sha256(b"E125-input-batch-chain-v1").hexdigest()
    operational = {"mode", "output", "summary", "run_id", "resume", "max_updates", "max_hours"}
    config_hash = base.digest_json({"args": {k: v for k, v in vars(args).items() if k not in operational}, "data": data.provenance,
                                  "script_sha256": base.sha256_file(__file__), "ce_provenance_sha256": base.sha256_file(args.ce_reference)})
    step, previous_wall = 0, 0.
    if args.resume:
        state = torch.load(args.resume, map_location="cpu", mmap=True, weights_only=False)
        if state["config_hash"] != config_hash or state["teacher_sample_hash"] != teacher_hash:
            raise ValueError("Resume protocol or teacher differs")
        moe.load_state_dict(state["moe"]); optimizer.load_state_dict(state["optimizer"])
        stream.load_state_dict(state["stream_rng"]); replay.load_state_dict(state["stream_rng"])
        data.restore_coverage(state["coverage"]); base.restore_rng(state["rng"], args)
        step, input_hash, previous_wall = state["step"], state["input_chain_hash"], state["elapsed_wall_seconds"]
        del state
    start_step = step
    provenance = {"args": vars(args), "objective": "teacher_full_distribution_KL_T1", "initial_tensor_sha256": initial_hash,
                  "frozen_sample_hash": frozen_hash, "teacher_sample_hash": teacher_hash, "data": data.provenance,
                  "held_window_hash": base.digest_json(windows), "config_hash": config_hash, "script_sha256": base.sha256_file(__file__),
                  "input_control": "same frozen E125 SplitStream algorithm/data; every batch checked against independent exact CPU replay; source hashes checked against actual CE log",
                  "precision": "training-dtype logits then FP32 log_softmax", "KL_reduction": "sum vocabulary, mean all batch*sequence tokens"}
    base.write_json(output / "provenance.json", provenance)
    items = base.read_pos(args.pos_items)
    prior = json.loads((output / "training_summary.json").read_text()) if args.resume and (output / "training_summary.json").exists() else {}
    evaluations = prior.get("evaluations", [])
    def evaluate_now():
        values, rows, pos = measure(model, original, moe, data, windows, items, args)
        return {"step": step, **values}, rows, pos
    if not any(r["step"] == step for r in evaluations):
        evaluations.append(evaluate_now()[0])
    elapsed = lambda: previous_wall + time.monotonic() - started
    def save():
        model.model.layers[args.layer].mlp = original
        if base.sampled_parameter_hash(model) != teacher_hash:
            raise RuntimeError("Teacher parameters changed")
        model.model.layers[args.layer].mlp = moe
        weights = moe.state_dict()
        state = {"schema": 3, "step": step, "replacement_kind": "moe", "replacement_state": weights, "moe": weights,
                 "optimizer": optimizer.state_dict(), "stream_rng": stream.state_dict(), "rng": base.rng_state(args),
                 "coverage": data.coverage_state(), "input_chain_hash": input_hash, "config_hash": config_hash,
                 "teacher_sample_hash": teacher_hash, "frozen_sample_hash": frozen_hash, "initial_tensor_sha256": initial_hash,
                 "elapsed_wall_seconds": elapsed(), "objective": "teacher_KL_T1"}
        torch.save(state, output / "checkpoint.tmp"); (output / "checkpoint.tmp").replace(output / "checkpoint.pt")
    status = "complete"
    with (output / "train_steps.jsonl").open("a" if args.resume else "w") as handle:
        while step < args.steps:
            if args.max_updates and step - start_step >= args.max_updates:
                status = "invocation_update_limit"; break
            if elapsed() >= args.max_hours * 3600 or (step + 1) * args.seq_len * args.batch_size * args.accum > args.max_train_tokens:
                status = "budget_limit"; break
            tick = time.monotonic(); optimizer.zero_grad(set_to_none=True)
            for group in optimizer.param_groups:
                group["lr"] = base.lr_at(step, args)
            totals = np.zeros(5); loads = torch.zeros(args.experts, device=args.device)
            for micro in range(args.accum):
                cpu_batch = data.train_batch(stream, args.batch_size)
                expected = replay_batch(data, replay, args.batch_size)
                if not torch.equal(cpu_batch, expected):
                    raise RuntimeError("Input batch differs from matched CE replay")
                input_hash = chain(input_hash, cpu_batch)
                batch = cpu_batch.to(args.device)
                model.model.layers[args.layer].mlp = original
                with torch.no_grad():
                    q = log_probs(model, batch[:, :-1], args)
                if q.requires_grad or stream.state_dict() != replay.state_dict():
                    raise RuntimeError("Teacher must be no-grad and must not consume training RNG")
                model.model.layers[args.layer].mlp = moe
                p = log_probs(model, batch[:, :-1], args)
                main = kl_tokens(q, p).mean()
                teacher_ce = -q.gather(-1, batch[:, 1:, None]).mean()
                student_ce = -p.gather(-1, batch[:, 1:, None]).mean()
                lb, z, frequency, _ = moe.losses_and_load()
                if step == 0 and micro == 0:
                    base.write_json(output / "gradient_audit.json", gradient_audit(main, lb, z, moe))
                objective = main + args.lb_coef * lb + args.z_coef * z
                if not torch.isfinite(objective):
                    raise RuntimeError("Nonfinite teacher-KL objective")
                (objective / args.accum).backward()
                totals += np.array([float(v.detach()) for v in (main, teacher_ce, student_ce, lb, z)]) / args.accum
                loads += frequency / args.accum
                moe.last_router_logits = None
            if any(p.grad is not None for p in original.parameters()) or any(p.grad is not None for n, p in model.named_parameters() if not n.startswith(f"model.layers.{args.layer}.mlp.")):
                raise RuntimeError("Teacher/frozen backbone received gradients")
            norm = float(torch.nn.utils.clip_grad_norm_(moe.parameters(), args.grad_clip, error_if_nonfinite=True))
            optimizer.step(); step += 1
            if data.source_schedule_hash != ce_sources[step] or data.draws != step * args.batch_size * args.accum:
                raise RuntimeError("Source/exposure schedule differs from matched CE")
            record = {"step": step, "train_tokens": step * args.seq_len * args.batch_size * args.accum,
                      **dict(zip(("train_kl", "teacher_gt_ce", "student_gt_ce", "lb_raw", "z_raw"), totals.tolist())),
                      "coverage": data.coverage_summary(), "input_chain_hash": input_hash, "matched_CE_source": True,
                      "gradient_norm_before_clip": norm, "expert_load": loads.cpu().tolist(),
                      "dead_experts": int((loads == 0).sum()), "seconds": time.monotonic() - tick}
            handle.write(json.dumps(record, allow_nan=False) + "\n"); handle.flush()
            base.emit("train", **{k: v for k, v in record.items() if k != "expert_load"})
            if args.eval_every and step % args.eval_every == 0:
                evaluations.append(evaluate_now()[0]); base.write_json(output / "training_summary.json", {"evaluations": evaluations})
            if args.save_every and step % args.save_every == 0:
                save()
    final, rows, pos = evaluate_now()
    if not evaluations or evaluations[-1]["step"] != step:
        evaluations.append(final)
    save()
    result = {"status": status, "step": step, "objective": "teacher_KL_T1", "evaluations": evaluations,
              "teacher_sample_hash": teacher_hash, "teacher_unchanged": True, "teacher_gradients_absent": True,
              "coverage": data.coverage_summary(per_file=True), "input_chain_hash": input_hash, "elapsed_wall_seconds": elapsed()}
    for path, value in ((output / "training_summary.json", result), (output / "final_held_sequences.json", rows), (output / "final_POS.json", pos)):
        base.write_json(path, value)
    if args.summary:
        Path(args.summary).parent.mkdir(parents=True, exist_ok=True); base.write_json(args.summary, result)
    return result


def parser():
    ap = control.parser(); ap.description = __doc__
    ap.add_argument("--ce-reference", default=str(WB / "results/e125/preflight/M-cover/provenance.json"))
    ap.add_argument("--ce-source-log")
    return ap


def self_test():
    torch.set_num_threads(1)
    with tempfile.TemporaryDirectory(prefix="e129_cpu_") as directory:
        root = Path(directory); rng = np.random.default_rng(129)
        train = []
        for i, size in enumerate((90, 45)):
            np.save(root / f"train{i}.npy", rng.integers(3, 31, size, dtype=np.uint16))
            train.append({"path": str(root / f"train{i}.npy"), "source": str(i), "file_id": str(i), "sampling_weight": (.7, .3)[i]})
        np.save(root / "held.npy", rng.integers(3, 31, 90, dtype=np.uint16))
        base.write_json(root / "manifest.json", {"train": train, "held": [{"path": str(root / "held.npy"), "source": "0", "file_id": "held"}]})
        pos = [{"ids": [3, 4, 5][:2 + i % 2], "next_id": 31, "word": "w", "label": "NOUN" if i % 2 else "VERB", "split": "held"} for i in range(4)]
        (root / "pos.jsonl").write_text("\n".join(map(json.dumps, pos)))
        torch.manual_seed(129)
        cfg = OlmoConfig(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=4, max_position_embeddings=32, pad_token_id=1)
        OlmoForCausalLM(cfg).save_pretrained(root / "model")
        common = ["--mode", "train", "--model", str(root / "model"), "--data", str(root / "manifest.json"), "--reference-data", str(root / "manifest.json"),
                  "--init-registry", str(root / "registry.json"), "--device", "cpu", "--dtype", "float32", "--layer", "1", "--experts", "4", "--expert-size", "16", "--top-k", "2",
                  "--seq-len", "8", "--batch-size", "2", "--steps", "3", "--eval-sequences", "4", "--bootstrap", "30", "--pos-items", str(root / "pos.jsonl"), "--eval-every", "0", "--save-every", "0", "--diagnostic-sequences", "0"]
        control.run(control.parser().parse_args([*common, "--output", str(root / "CE")]))
        extra = ["--ce-reference", str(root / "CE/provenance.json")]
        full = run(parser().parse_args([*common, *extra, "--output", str(root / "full")]))
        run(parser().parse_args([*common, *extra, "--output", str(root / "resume"), "--max-updates", "1"]))
        resumed = run(parser().parse_args([*common, *extra, "--output", str(root / "resume"), "--resume", str(root / "resume/checkpoint.pt")]))
        errors = control.compare_checkpoints(root / "full/checkpoint.pt", root / "resume/checkpoint.pt")
        q = torch.tensor([[[0., 1., 2.]]]).log_softmax(-1); p = torch.tensor([[[2., 1., 0.]]]).log_softmax(-1)
        assert float(kl_tokens(q, q).max()) == 0 and float(kl_tokens(q, p).mean()) > 0
        assert torch.allclose(kl_tokens(q.expand(2, 7, 3), p.expand(2, 7, 3)).mean(), kl_tokens(q, p).mean())
        assert full["input_chain_hash"] == resumed["input_chain_hash"] and full["teacher_unchanged"] and resumed["teacher_gradients_absent"]
        result = {"passed": True, "device": "cpu", "resume": errors, "teacher_unchanged_and_no_grad": True,
                  "self_KL": 0., "shifted_KL": float(kl_tokens(q, p).mean()), "token_mean_batch_sequence_invariant": True,
                  "same_initialization_and_every_step_CE_source_input_replay": True, "resume_input_chain_equal": True,
                  "gradient_audit": json.loads((root / "full/gradient_audit.json").read_text()), "script_sha256": base.sha256_file(__file__)}
        target = WB / "results/e129/self_test.json"; target.parent.mkdir(parents=True, exist_ok=True); base.write_json(target, result)
        return result


if __name__ == "__main__":
    args = parser().parse_args()
    print(json.dumps(self_test() if args.mode == "self-test" else run(args), ensure_ascii=False, allow_nan=False))
