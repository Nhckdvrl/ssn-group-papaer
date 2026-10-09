"""Variable-specific sender edges to the answer; native direct/relay 2x2.

Interventions happen in head space; group deltas are computed in float32 from
native eager attention weights. The output projection is applied once.
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
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from e58_factorization import NAMES, make_contexts
from e59_mediation import encode, patch, real_contexts, score


def query_layout(tok, ctx, dataset, plen):
    item, source = ("Comment", "Annotator") if dataset == "real" else ("Item", "Source")
    texts = [f'{item}: {q["word"]}\n{source}: {NAMES[q["source"]]}\nLabel:' for q in ctx["queries"]]
    encoded = [tok(t, add_special_tokens=False, return_offsets_mapping=True) for t in texts]
    width = max(len(x["input_ids"]) for x in encoded)
    masks = {s: torch.zeros((len(texts), width), device="cuda", dtype=torch.bool)
             for s in ("q_input", "q_source", "q_marker", "q_relay")}
    details = []
    for qi, (text_, x) in enumerate(zip(texts, encoded)):
        ids, offsets = x["input_ids"], x["offset_mapping"]
        assert ids == tok.encode(text_, add_special_tokens=False)
        boundaries = (text_.rindex("\n" + source + ":") + 1, text_.rindex("\nLabel:") + 1)
        groups = {}
        left = width - len(ids)
        for j, (start, end) in enumerate(offsets):
            if j == len(ids) - 1:
                assert text_[start:end] == ":", (text_[start:end], ids[j])
                continue
            group = "q_input" if start < boundaries[0] else "q_source" if start < boundaries[1] else "q_marker"
            assert not any(start < b < end and text_[start:end].strip() for b in boundaries), (text_, start, end)
            masks[group][qi, left + j] = True
            masks["q_relay"][qi, left + j] = True
            groups.setdefault(group, []).append(j)
        assert torch.equal(masks["q_input"][qi] | masks["q_source"][qi] | masks["q_marker"][qi], masks["q_relay"][qi])
        assert int(masks["q_relay"][qi].sum()) == len(ids) - 1
        details.append({"text": text_, "ids": ids, "groups": groups, "left_pad": left})
    return masks, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dataset", choices=["synthetic", "real"], required=True)
    ap.add_argument("--stage", choices=["discovery", "confirmation"], required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    a = ap.parse_args()
    torch.set_num_threads(6)
    torch.manual_seed(0)
    t0 = time.time()
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    contexts = make_contexts(a.stage, a.n, a.seed) if a.dataset == "synthetic" else real_contexts(
        "train" if a.stage == "discovery" else "test", a.n, a.seed)
    labels = ["yes", "no"] if a.dataset == "synthetic" and a.stage == "discovery" else ["toxic", "safe"]
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    assert tok.is_fast
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16,
                                               device_map="cuda", attn_implementation="eager").eval()
    state = {"on": False}
    rms, errors = [], []
    all_groups = ("p_label", "p_source", "q_input", "q_source", "q_marker", "q_relay")
    for li, layer in enumerate(model.model.layers):
        def ahook(layer_index):
            def hook(module, args, kwargs, output):
                if not state["on"]:
                    return output
                cache = kwargs["past_key_values"].layers[layer_index]
                probs = output[1]
                vals = cache.values.repeat_interleave(probs.shape[1] // cache.values.shape[1], dim=1)
                heads = probs @ vals
                rebuilt = module.o_proj(heads.transpose(1, 2).reshape(output[0].shape))
                if state["mode"] == "base":
                    error = (rebuilt[:, -1].float() - output[0][:, -1].float()).square().mean().sqrt()
                    rms.append(float(error / output[0][:, -1].float().square().mean().sqrt().clamp_min(1e-6)))
                last = probs[:, :, -1:, :]
                components = {}
                for group, site in (("p_label", "label_anchor"), ("p_source", "source_name")):
                    pos = state["sites"][site]
                    components[group] = (last[..., pos].float() @ vals[:, :, pos].float()).squeeze(2)
                qweights = last[..., state["plen"]:]
                qvalues = vals[:, :, state["plen"]:]
                assert qweights.shape[-1] == state["masks"]["q_relay"].shape[-1]
                for group in ("q_input", "q_source", "q_marker", "q_relay"):
                    weights = qweights.float() * state["masks"][group][:, None, None, :]
                    components[group] = (weights @ qvalues.float()).squeeze(2)
                if state["mode"] == "base":
                    state["saved"][layer_index] = {g: c.clone() for g, c in components.items()}
                    state["saved"][layer_index]["all"] = heads[:, :, -1].clone()
                mode = state["mode"]
                if mode in ("base", "sourceK"):
                    return output
                delta = torch.zeros_like(heads[:, :, -1], dtype=torch.float32)
                if mode in ("freeze_all",):
                    heads[:, :, -1] = state["saved"][layer_index]["all"]
                else:
                    if mode == "noop":
                        groups = all_groups
                    elif mode == "freeze_direct_and_relay":
                        groups = ("p_label", "q_relay")
                    elif mode.startswith("freeze_"):
                        groups = (mode.removeprefix("freeze_"),)
                    elif mode.startswith("drop_"):
                        suffix = mode.removeprefix("drop_")
                        groups = ("p_label", "q_relay") if suffix == "both" else ("p_label",) if suffix == "direct" else ("q_relay",)
                    else:
                        raise ValueError(mode)
                    for group in groups:
                        delta += (-components[group] if mode.startswith("drop_") else
                                  state["saved"][layer_index][group] - components[group])
                    heads[:, :, -1] = (heads[:, :, -1].float() + delta).to(heads.dtype)
                h = module.o_proj(heads.transpose(1, 2).reshape(output[0].shape))
                return (h,) + output[1:]
            return hook
        layer.self_attn.register_forward_hook(ahook(li), with_kwargs=True)
    (outdir / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in contexts))
    freeze_modes = ["freeze_" + g for g in all_groups] + ["freeze_direct_and_relay", "freeze_all", "noop"]
    with (outdir / "behavior.jsonl").open("w") as f, torch.inference_mode():
        for ci, ctx in enumerate(contexts):
            state["on"] = False
            caches, sites_list, plens = {}, [], []
            for donor in ("base", "source"):
                ids, sites = encode(tok, ctx, labels, a.dataset, donor)
                caches[donor] = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
                sites_list.append(sites)
                plens.append(len(ids))
            assert plens[0] == plens[1] and sites_list[0] == sites_list[1]
            plen, sites = plens[0], sites_list[0]
            masks, details = query_layout(tok, ctx, a.dataset, plen)
            if ci == 0:
                (outdir / "query_layout.json").write_text(json.dumps(details, indent=2))
            changed = patch(caches["base"], caches["source"], sites["source_name"], "key")
            state.update(on=True, sites=sites, plen=plen, masks=masks, saved={})
            scores = {}
            for mode in ("base", "sourceK") + tuple(freeze_modes):
                state["mode"] = mode
                c = caches["base"] if mode in ("base", "noop") else changed
                scores[mode] = score(model, tok, copy.deepcopy(c), ctx, labels, plen, a.dataset)
            for variant in ("drop_direct", "drop_relay", "drop_both"):
                for condition, c in (("base", caches["base"]), ("sourceK", changed)):
                    state["mode"] = variant
                    scores[f"{variant}.{condition}"] = score(model, tok, copy.deepcopy(c), ctx, labels, plen, a.dataset)
            errors += [float(abs(scores["base"] - scores[x]).max()) for x in ("noop", "freeze_all")]
            state["on"] = False
            ids, _ = encode(tok, ctx, labels, a.dataset, instruction=True)
            c = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
            scores["instruction"] = score(model, tok, c, ctx, labels, len(ids), a.dataset)
            single = []
            for source in (0, 1):
                query_indices = [j for j, q in enumerate(ctx["queries"]) if q["source"] == source]
                sc = {"demos": [x for x in ctx["demos"] if x["source"] == source],
                      "queries": [ctx["queries"][j] for j in query_indices]}
                ids, _ = encode(tok, sc, labels, a.dataset)
                c = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
                pred = score(model, tok, c, sc, labels, len(ids), a.dataset)
                single.extend(zip(query_indices, map(float, pred)))
            scores["single"] = [x for _, x in sorted(single)]
            f.write(json.dumps({"context": ci, "signs": [2 * q["label"] - 1 for q in ctx["queries"]],
                                "scores": {k: list(map(float, v)) for k, v in scores.items()}}) + "\n")
            f.flush()
            if ci % 8 == 0:
                print(ci, round(time.time() - t0, 1), flush=True)
    assert max(rms) < 0.02 and max(errors) <= 0.1, (max(rms), max(errors))
    run = {"args": vars(a), "seconds": time.time() - t0, "sanity_max_error": max(errors),
           "reconstruction_relative_rms_max": max(rms), "torch": torch.__version__, "transformers": transformers.__version__,
           "host": platform.node(), "gpu": torch.cuda.get_device_name(),
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "config_sha256": hashlib.sha256((Path(a.model) / "config.json").read_bytes()).hexdigest(),
           "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}
    (outdir / "run.json").write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == "__main__":
    main()
