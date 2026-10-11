"""Freeze variable-specific messages at the final query position.

Uses the native eager attention weights and cached V, without approximating QK.
The label component includes every head, avoiding output-based head selection.
"""
import argparse
import copy
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from e58_factorization import NAMES, make_contexts
from e59_mediation import encode, patch, real_contexts, score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dataset", choices=["synthetic", "real"], required=True)
    ap.add_argument("--stage", choices=["discovery", "confirmation"], required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--scope", choices=["final", "all_query"], default="final")
    a = ap.parse_args()
    torch.set_num_threads(6)
    torch.manual_seed(0)
    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ctxs = make_contexts(a.stage, a.n, a.seed) if a.dataset == "synthetic" else real_contexts(
        "train" if a.stage == "discovery" else "test", a.n, a.seed)
    labels = ["yes", "no"] if a.dataset == "synthetic" and a.stage == "discovery" else ["toxic", "safe"]
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16,
                                               device_map="cuda", attn_implementation="eager").eval()
    L = model.config.num_hidden_layers
    state = {"on": False}
    sanity_rms = []
    for li, layer in enumerate(model.model.layers):
        att = layer.self_attn
        def ahook(layer_index):
            def hook(module, args, kwargs, output):
                if not state["on"]:
                    return output
                cache = kwargs["past_key_values"].layers[layer_index]
                kv_heads = cache.keys.shape[1]
                all_prob = output[1]
                factor = all_prob.shape[1] // kv_heads
                values = cache.values.repeat_interleave(factor, dim=1)
                prob = all_prob if a.scope == "all_query" else all_prob[:, :, -1:, :]
                components = {}
                for site in ("label_anchor", "source_name"):
                    positions = state["sites"][site]
                    weighted = (prob[:, :, :, positions] @ values[:, :, positions]).transpose(1, 2)
                    component = module.o_proj(weighted.reshape(weighted.shape[0], weighted.shape[1], -1))
                    components[site] = component if a.scope == "all_query" else component[:, 0]
                full = (all_prob @ values).transpose(1, 2).reshape(output[0].shape)
                reconstructed = module.o_proj(full)[:, -1].float()
                native = output[0][:, -1].float()
                if state["mode"] == "base":
                    relative_rms = float((reconstructed - native).square().mean().sqrt() / native.square().mean().sqrt().clamp_min(1e-6))
                    sanity_rms.append(relative_rms)
                    state["saved"][layer_index] = {k: v.clone() for k, v in components.items()}
                    state["saved"][layer_index]["all"] = output[0].clone() if a.scope == "all_query" else output[0][:, -1].clone()
                # Attention to base-context source labels, normalized across all label attention.
                pos = state["sites"]["label_anchor"]
                weights = all_prob[:, :, -1, pos]
                same = state["same_source"][:, None, :]
                fraction = (weights * same).sum((1, 2)) / weights.sum((1, 2)).clamp_min(1e-9)
                if state["mode"] in ("base", "sourceK"):
                    state["fractions"][layer_index] = fraction.cpu().numpy()
                    name_weights = all_prob[torch.arange(all_prob.shape[0], device="cuda"), :, state["query_name_positions"]][:, :, pos]
                    name_fraction = (name_weights * same).sum((1, 2)) / name_weights.sum((1, 2)).clamp_min(1e-9)
                    state["name_fractions"][layer_index] = name_fraction.cpu().numpy()
                mode = state["mode"]
                frozen = "label_anchor" if mode in ("freeze_label", "freeze_early_label", "freeze_late_label", "noop_label") else "source_name"
                do_freeze = mode in ("freeze_label", "freeze_name", "noop_label") or (mode == "freeze_early_label" and layer_index < L // 2) or (mode == "freeze_late_label" and layer_index >= L // 2)
                if mode == "freeze_all" or do_freeze:
                    h = output[0].clone()
                    if mode == "freeze_all":
                        if a.scope == "all_query":
                            h = state["saved"][layer_index]["all"].clone()
                        else:
                            h[:, -1] = state["saved"][layer_index]["all"]
                    else:
                        delta = state["saved"][layer_index][frozen] - components[frozen]
                        if a.scope == "all_query":
                            h = h + delta
                        else:
                            h[:, -1] = h[:, -1] + delta
                    return (h,) + output[1:]
                return output
            return hook
        att.register_forward_hook(ahook(li), with_kwargs=True)
    errors = []
    (d / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in ctxs))
    with (d / "behavior.jsonl").open("w") as f, torch.inference_mode():
        for i, ctx in enumerate(ctxs):
            state["on"] = False
            caches = {}
            for donor in ("base", "source"):
                ids, sites = encode(tok, ctx, labels, a.dataset, donor)
                caches[donor] = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
            plen = len(ids)
            item, source = ("Comment", "Annotator") if a.dataset == "real" else ("Item", "Source")
            query_ids = [tok.encode(f'{item}: {q["word"]}\n{source}: {NAMES[q["source"]]}\nLabel:', add_special_tokens=False) for q in ctx["queries"]]
            width = max(map(len, query_ids))
            name_positions = []
            for q, seq in zip(ctx["queries"], query_ids):
                nameid = tok.encode(" " + NAMES[q["source"]], add_special_tokens=False)[0]
                name_positions.append(width - len(seq) + max(j for j, x in enumerate(seq) if x == nameid))
            state.update(sites=sites, saved={}, on=True,
                         query_name_positions=torch.tensor(name_positions, device="cuda"),
                         same_source=torch.tensor([[demo["source"] == q["source"] for demo in ctx["demos"]] for q in ctx["queries"]], device="cuda", dtype=torch.float32))
            kcache = patch(caches["base"], caches["source"], sites["source_name"], "key")
            scores, fractions, name_fractions = {}, {}, {}
            for mode in ("base", "sourceK", "freeze_label", "freeze_early_label", "freeze_late_label", "freeze_name", "freeze_all", "noop_label"):
                state.update(mode=mode, fractions={}, name_fractions={})
                cache = copy.deepcopy(caches["base"] if mode in ("base", "noop_label") else kcache)
                scores[mode] = score(model, tok, cache, ctx, labels, plen, a.dataset)
                if mode in ("base", "sourceK"):
                    fractions[mode] = np.stack([state["fractions"][j] for j in range(L)]).tolist()
                    name_fractions[mode] = np.stack([state["name_fractions"][j] for j in range(L)]).tolist()
            state["on"] = False
            errors += [float(abs(scores["base"] - scores[c]).max()) for c in ("noop_label", "freeze_all")]
            f.write(json.dumps({"context": i, "signs": [2 * q["label"] - 1 for q in ctx["queries"]],
                                "scores": {k: list(map(float, v)) for k, v in scores.items()}, "fractions": fractions,
                                "name_fractions": name_fractions}) + "\n")
            f.flush()
            if i % 8 == 0:
                print(i, round(time.time() - t0, 1), flush=True)
    run = {"args": vars(a), "seconds": time.time() - t0, "sanity_max_logit_error": max(errors),
           "reconstruction_relative_rms_max": max(sanity_rms), "reconstruction_relative_rms_mean": float(np.mean(sanity_rms)),
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "gpu": torch.cuda.get_device_name()}
    (d / "run.json").write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == "__main__":
    main()
