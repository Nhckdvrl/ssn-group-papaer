"""Separate source-specific example encoding from query-time source selection.

Natural comments and the frozen E56 adapter; no new training or layer search.
The foreign source alone changes its mapping. All current-source evidence stays.
See E90 for the preregistered interpretation of this factorial intervention.
"""
import argparse
import copy
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np

from e56_query_adapter import HEAD, contexts, pools


def interval(values):
    v = np.asarray(values, dtype=float)
    draws = np.random.default_rng(900).integers(len(v), size=(10000, len(v)))
    return {"mean": float(v.mean()),
            "ci95": np.quantile(v[draws].mean(1), [.025, .975]).tolist(),
            "n_contexts": len(v)}


def analyze(dest):
    run = json.loads((dest / "run.json").read_text())
    rows = [json.loads(s) for s in (dest / "behavior.jsonl").read_text().splitlines()]
    assert len(rows) == run["args"]["n"]
    assert [r["context"] for r in rows] == list(range(len(rows)))
    assert run["numeric_max_error"] <= .001
    names = list(rows[0]["conditions"])
    gold = np.array([r["gold"] for r in rows])
    z = {k: np.array([r["conditions"][k]["z"] for r in rows]) for k in names}
    metrics = {}
    for k in names:
        top = np.array([r["conditions"][k]["argmax_is_label"] for r in rows])
        full_correct = np.array([r["conditions"][k]["argmax_correct"] for r in rows])
        metrics[k] = {
            "accuracy": interval(((z[k] > 0) == (gold > 0)).mean(1)),
            "signed_margin": interval((z[k] * gold).mean(1)),
            "rule_contrast": interval(2 * (z[k] * gold).mean(1)),
            "argmax_label_rate": interval(top.mean(1)),
            "argmax_accuracy": interval(full_correct.mean(1)),
        }
    contrasts = {}
    for k in ["native", "early", "late", "both", "instruction", "adapter", "adapter_late"]:
        contrasts[f"foreign_mapping_effect_{k}"] = interval(
            ((z[f"aligned_{k}"] - z[f"conflict_{k}"]) * gold).mean(1))
    for k in ["early", "late", "both", "instruction", "adapter", "adapter_late", "single"]:
        key = "single" if k == "single" else f"conflict_{k}"
        contrasts[f"accuracy_vs_native_{k}"] = interval(
            (((z[key] > 0) == (gold > 0)).mean(1)
             - ((z["conflict_native"] > 0) == (gold > 0)).mean(1)))
    for left, right in [("both", "late"), ("late", "early"), ("adapter", "both"),
                        ("adapter_late", "late"), ("adapter_late", "adapter")]:
        contrasts[f"accuracy_{left}_minus_{right}"] = interval(
            (((z[f"conflict_{left}"] > 0) == (gold > 0)).mean(1)
             - ((z[f"conflict_{right}"] > 0) == (gold > 0)).mean(1)))
    contrasts["early_late_accuracy_interaction"] = interval(
        ((z["conflict_both"] > 0) == (gold > 0)).mean(1)
        - ((z["conflict_early"] > 0) == (gold > 0)).mean(1)
        - ((z["conflict_late"] > 0) == (gold > 0)).mean(1)
        + ((z["conflict_native"] > 0) == (gold > 0)).mean(1))
    contrasts["indirect_foreign_mapping_removed_by_early"] = interval(
        ((z["aligned_late"] - z["conflict_late"]
          - z["aligned_both"] + z["conflict_both"]) * gold).mean(1))
    out = {"metrics": metrics, "contrasts": contrasts,
           "numeric_max_error": run["numeric_max_error"],
           "source": "All contexts, paired context bootstrap; no surviving-query selection."}
    (dest / "analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    for k in names:
        print(k, "acc", round(metrics[k]["accuracy"]["mean"], 4),
              "margin", round(metrics[k]["signed_margin"]["mean"], 4), flush=True)
    for k, v in contrasts.items():
        print(k, v, flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="/tmp/ices_models/Qwen3-8B")
    ap.add_argument("--weights", default="results/e56/Qwen3-8B_query_saved.pt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--seed", type=int, default=90001)
    ap.add_argument("--queries-per-kind", type=int, default=4)
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--analyze-only", action="store_true")
    args = ap.parse_args()
    dest = Path(args.out)
    if args.analyze_only:
        analyze(dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    assert not (dest / "behavior.jsonl").exists(), "Never overwrite an existing experiment"
    rng = np.random.default_rng(args.seed)
    cs = contexts(pools()["test"], args.n, rng, nq=args.queries_per_kind)
    for ctx in cs:
        ctx["reverse"] = bool(rng.integers(2))
        if ctx["reverse"]:
            ctx["demos"] = [(t, role, 1-y) for t, role, y in ctx["demos"]]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    enc = lambda text: tok.encode(text, add_special_tokens=False)
    labels = [enc(" safe"), enc(" toxic")]
    assert all(len(x) == 1 for x in labels)
    label_ids = [x[0] for x in labels]

    def prefix(ctx, aligned=False, instruction=False, single=False):
        head = HEAD
        if instruction:
            head += "Use only the examples of the requested annotator to infer and apply that annotator's labeling rule.\n\n"
        ids = enc(head)
        roles = [-1] * len(ids)
        anchors = []
        for (text, role, y), name in zip(ctx["demos"], ctx["shown"]):
            if single and role != 0:
                continue
            if aligned and role == 1:
                y = 1-y
            block = enc(f"Comment: {text}\nAnnotator: {name}\nLabel:")
            anchors.append(len(ids) + len(block))
            block += enc(" " + ("toxic" if y else "safe")) + enc("\n\n")
            ids += block
            roles += [role] * len(block)
        return ids, roles, anchors

    encoded = []
    for ctx in cs:
        c = prefix(ctx)
        a = prefix(ctx, aligned=True)
        assert len(c[0]) == len(a[0]) and c[1:] == a[1:]
        allowed = {p for p, role in zip(c[2], [d[1] for d in ctx["demos"]]) if role == 1}
        diffs = [i for i, (x, y) in enumerate(zip(c[0], a[0])) if x != y]
        assert set(diffs) == allowed
        assert all({c[0][i], a[0][i]} == set(label_ids) for i in diffs)
        assert sum(d[2] for d in ctx["demos"] if d[1] == 0) == 4
        assert sum(d[2] for d in ctx["demos"] if d[1] == 1) == 4
        encoded.append((c, a))
    preflight = {"args": vars(args), "label_ids": label_ids,
                 "prefix_lengths": [len(c[0]) for c, _ in encoded],
                 "foreign_changed_labels_per_context": 8,
                 "target_source_changed_tokens": 0,
                 "reversed_contexts": sum(c["reverse"] for c in cs),
                 "query_count_per_context": 2 * args.queries_per_kind,
                 "source_block_token_ownership": "Each complete demo, including separators, belongs to its source; only the initial header is shared.",
                 "interventions": ["native", "early", "late", "both", "instruction", "adapter", "adapter_late", "single"]}
    (dest / "preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    (dest / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in cs))
    if args.preflight_only:
        print("All contexts aligned; only foreign-source labels differ; both label frequencies balanced.", flush=True)
        return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    started = time.time()
    print("Loading model", flush=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, dtype=torch.float32,
                                               device_map="cuda", attn_implementation="eager").eval()
    model.requires_grad_(False)
    print("Model loaded", flush=True)
    L = model.config.num_hidden_layers
    L1 = L // 2 - 2
    weights = torch.load(args.weights, map_location="cpu", weights_only=True)
    assert len(weights) == 2 * (L - L1)
    modules = {l: (weights[2*i].cuda().float(), weights[2*i+1].cuda().float())
               for i, l in enumerate(range(L1, L))}
    state = {"adapter": False}
    handles = []
    for layer_index in range(L1, L):
        def hook(module, inputs, output, l=layer_index):
            if not state["adapter"]:
                return output
            down, up = modules[l]
            result = output.clone()
            result[:, -1] += ((inputs[0][:, -1].float() @ down.T) @ up.T).to(result.dtype)
            return result
        handles.append(model.model.layers[layer_index].self_attn.q_proj.register_forward_hook(hook))

    def prefill(ids, roles, early):
        n = len(ids)
        positions = torch.arange(n, device="cuda")
        allowed = positions[:, None] >= positions[None, :]
        if early:
            r = torch.tensor(roles, device="cuda")
            allowed &= (r[:, None] == r[None, :]) | (r[None, :] == -1)
        mask = torch.zeros((n, n), device="cuda", dtype=torch.float32)
        mask.masked_fill_(~allowed, float("-inf"))
        state["adapter"] = False
        out = model(input_ids=torch.tensor([ids], device="cuda"), attention_mask=mask[None, None],
                    position_ids=positions[None], use_cache=True, logits_to_keep=1)
        return out.past_key_values

    def query(cache, roles, queries, late=False, adapter=False, two_dimensional=False):
        plen = len(roles)
        lengths = [len(q) for q in queries]
        qlen = max(lengths)
        n = len(queries)
        ids = torch.zeros((n, qlen), dtype=torch.long, device="cuda")
        position_ids = torch.zeros_like(ids)
        live = torch.zeros((n, qlen), dtype=torch.bool, device="cuda")
        for i, q in enumerate(queries):
            offset = qlen - len(q)
            ids[i, offset:] = torch.tensor(q, device="cuda")
            position_ids[i, offset:] = torch.arange(plen, plen + len(q), device="cuda")
            live[i, offset:] = True
        prefix_live = torch.ones(plen, dtype=torch.bool, device="cuda")
        if late:
            prefix_live = torch.tensor(roles, device="cuda") != 1
        if two_dimensional:
            assert not late
            mask = torch.cat([prefix_live[None].expand(n, -1), live], dim=1).long()
        else:
            allowed = torch.cat([prefix_live[None, None].expand(n, qlen, -1),
                                 live[:, None].expand(-1, qlen, -1) &
                                 torch.ones((qlen, qlen), dtype=torch.bool, device="cuda").tril()[None]], dim=-1)
            mask = torch.zeros(allowed.shape, dtype=torch.float32, device="cuda")
            mask.masked_fill_(~allowed, float("-inf"))
            mask = mask[:, None]
        copied = copy.deepcopy(cache)
        copied.batch_repeat_interleave(n)
        state["adapter"] = adapter
        out = model(input_ids=ids, attention_mask=mask, position_ids=position_ids,
                    past_key_values=copied, use_cache=True, logits_to_keep=1)
        state["adapter"] = False
        lo = out.logits[:, -1].float()
        top = lo.argmax(-1)
        z = lo[:, label_ids[1]] - lo[:, label_ids[0]]
        return {"z": z.cpu().tolist(), "argmax_token": top.cpu().tolist(),
                "argmax_is_label": ((top == label_ids[0]) | (top == label_ids[1])).cpu().tolist()}

    numeric = []
    with torch.inference_mode(), (dest / "behavior.jsonl").open("w") as stream:
        for ci, ctx in enumerate(cs):
            queries = [enc(f"Comment: {text}\nAnnotator: {ctx['names'][0]}\nLabel:") for text, _ in ctx["q"]]
            gold = [(-1 if ctx["reverse"] else 1) * (1 if kind == "race" else -1) for _, kind in ctx["q"]]
            conditions = {}
            caches = {}
            for relation in ["conflict", "aligned"]:
                ids, roles, _ = encoded[ci][relation == "aligned"]
                for early in [False, True]:
                    cache = prefill(ids, roles, early)
                    caches[relation, early] = cache
                    for late in [False, True]:
                        key = "both" if early and late else "early" if early else "late" if late else "native"
                        conditions[f"{relation}_{key}"] = query(cache, roles, queries, late=late)
                    if not early:
                        conditions[f"{relation}_adapter"] = query(cache, roles, queries, adapter=True)
                        conditions[f"{relation}_adapter_late"] = query(cache, roles, queries, late=True, adapter=True)
                iids, iroles, _ = prefix(ctx, aligned=(relation == "aligned"), instruction=True)
                icache = prefill(iids, iroles, False)
                conditions[f"{relation}_instruction"] = query(icache, iroles, queries)
            sids, sroles, _ = prefix(ctx, single=True)
            conditions["single"] = query(prefill(sids, sroles, False), sroles, queries)
            double_diff = max(abs(x-y) for x, y in zip(conditions["conflict_both"]["z"], conditions["aligned_both"]["z"]))
            numeric.append(double_diff)
            if ci == 0:
                ids, roles, _ = encoded[ci][0]
                # 4D mask and split-cache execution must agree with ordinary causal execution.
                ordinary = query(caches["conflict", False], roles, queries, two_dimensional=True)
                numeric.append(max(abs(x-y) for x, y in zip(ordinary["z"], conditions["conflict_native"]["z"])))
                full_ids = ids + queries[0]
                direct = model(input_ids=torch.tensor([full_ids], device="cuda"), use_cache=False, logits_to_keep=1).logits[0, -1]
                direct_z = float(direct[label_ids[1]] - direct[label_ids[0]])
                numeric.append(abs(direct_z - conditions["conflict_native"]["z"][0]))
            assert max(numeric) <= .001, numeric
            for c in conditions.values():
                c["argmax_correct"] = [top == label_ids[int(y > 0)] for top, y in zip(c["argmax_token"], gold)]
            stream.write(json.dumps({"context": ci, "gold": gold, "reverse": ctx["reverse"],
                                     "conditions": conditions, "double_block_foreign_effect_max": double_diff}) + "\n")
            stream.flush()
            print(ci+1, "/", args.n, "native", np.mean((np.array(conditions["conflict_native"]["z"]) > 0) == (np.array(gold) > 0)),
                  "late", np.mean((np.array(conditions["conflict_late"]["z"]) > 0) == (np.array(gold) > 0)),
                  "both", np.mean((np.array(conditions["conflict_both"]["z"]) > 0) == (np.array(gold) > 0)),
                  "numeric", max(numeric), flush=True)
            del caches
    elapsed = time.time() - started
    run = {"args": vars(args), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "weights_sha256": hashlib.sha256(Path(args.weights).read_bytes()).hexdigest(),
           "contexts_sha256": hashlib.sha256((dest / "contexts.jsonl").read_bytes()).hexdigest(),
           "numeric_max_error": max(numeric), "elapsed_seconds": elapsed, "gpu_hours": elapsed/3600,
           "model_revision": "b968826d9c46dd6066d109eabc6255188de91218",
           "python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__,
           "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
           "dtype": "float32", "attention": "eager", "adapter_layers": list(range(L1, L)),
           "adapter_enabled_only_on_final_answer_position": True,
           "query_masks_apply_to_all_query_positions": True}
    (dest / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    analyze(dest)


if __name__ == "__main__":
    main()
