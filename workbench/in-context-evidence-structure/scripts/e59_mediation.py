"""E59: compare counterfactual source and mapping effects at matched token sites.

Includes E56's real interaction task. The real confirmation run saves paired
anchor features for the frozen E58 analysis protocol, with disjoint text pools.
"""
import argparse
import copy
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from e58_factorization import HEAD, INSTRUCTION, NAMES, make_contexts, score_queries


def real_contexts(split, n, seed):
    from e56_query_adapter import contexts, correct, pools
    raw = contexts(pools()[split], n, np.random.default_rng(seed), nq=4)
    result = []
    for i, ctx in enumerate(raw):
        result.append({"context": i,
                       "demos": [{"word": t, "source": NAMES.index(name), "label": 1 - y}
                                 for (t, role, y), name in zip(ctx["demos"], ctx["shown"])],
                       "queries": [{"word": t, "source": NAMES.index(ctx["names"][role]), "label": 1 - correct(role, kind)}
                                   for role in (0, 1) for t, kind in ctx["q"]]})
    return result


def encode(tok, ctx, labels, dataset, donor="base", instruction=False):
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    head = "Below are comments and the labels that individual annotators gave them.\n\n" if dataset == "real" else HEAD
    ids = enc(head + (INSTRUCTION if instruction else ""))
    sites = {s: [] for s in ("source_name", "label_prediction", "label_anchor", "post_label", "source_span")}
    for d in ctx["demos"]:
        field, who = ("Comment", "Annotator") if dataset == "real" else ("Item", "Source")
        ids += enc(f'{field}: {d["word"]}\n{who}:')
        name = NAMES[d["source"] ^ int(donor == "source")]
        name_ids = enc(" " + name)
        assert len(name_ids) == 1, (name, name_ids)
        name_pos = len(ids)
        ids += name_ids
        ids += enc("\nLabel:")
        anchor = len(ids)
        sites["source_name"].append(name_pos)
        sites["label_prediction"].append(anchor - 1)
        sites["source_span"] += list(range(name_pos, anchor))
        sites["label_anchor"].append(anchor)
        label_ids = enc(" " + labels[d["label"] ^ int(donor == "label")])
        assert len(label_ids) == 1
        ids += label_ids
        sites["post_label"].append(len(ids))
        ids += enc("\n\n")
    sites["non_anchor"] = [p for p in range(len(ids)) if p not in sites["label_anchor"]]
    sites["full"] = list(range(len(ids)))
    return ids, sites


@torch.inference_mode()
def score(model, tok, cache, ctx, labels, plen, dataset):
    if dataset == "synthetic":
        return score_queries(model, tok, cache, ctx, labels, plen)
    seqs = [tok.encode(f'Comment: {q["word"]}\nAnnotator: {NAMES[q["source"]]}\nLabel:', add_special_tokens=False)
            for q in ctx["queries"]]
    width = max(map(len, seqs))
    ids = torch.zeros((len(seqs), width), dtype=torch.long, device="cuda")
    mask = torch.zeros((len(seqs), plen + width), dtype=torch.long, device="cuda")
    pos = torch.zeros_like(ids)
    mask[:, :plen] = 1
    for i, seq in enumerate(seqs):
        ids[i, -len(seq):] = torch.tensor(seq, device="cuda")
        mask[i, -len(seq):] = 1
        pos[i, -len(seq):] = torch.arange(plen, plen + len(seq), device="cuda")
    cache.batch_repeat_interleave(len(seqs))
    logits = model(input_ids=ids, attention_mask=mask, position_ids=pos, past_key_values=cache,
                   use_cache=True, logits_to_keep=1).logits[:, -1].float()
    label_ids = [tok.encode(" " + x, add_special_tokens=False)[0] for x in labels]
    return (logits[:, label_ids[1]] - logits[:, label_ids[0]]).cpu().numpy()


def patch(base, donor, positions, channel):
    out = copy.deepcopy(base)
    for dst, src in zip(out.layers, donor.layers):
        if channel in ("key", "kv"):
            dst.keys[:, :, positions, :] = src.keys[:, :, positions, :]
        if channel in ("value", "kv"):
            dst.values[:, :, positions, :] = src.values[:, :, positions, :]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dataset", choices=["synthetic", "real"], required=True)
    ap.add_argument("--stage", choices=["discovery", "confirmation"], required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--probe-train", type=int, default=0)
    a = ap.parse_args()
    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(6)
    torch.manual_seed(0)
    t0 = time.time()
    labels = ["yes", "no"] if a.dataset == "synthetic" and a.stage == "discovery" else ["toxic", "safe"]
    if a.dataset == "synthetic":
        contexts = make_contexts(a.stage, a.n, a.seed)
    else:
        contexts = real_contexts("train", a.probe_train, 59003) if a.probe_train else []
        contexts += real_contexts("train" if a.stage == "discovery" else "test", a.n, a.seed)
    for i, ctx in enumerate(contexts):
        ctx["context"] = i
        assert all(sum(x["source"] == s and x["label"] == y for x in ctx["demos"]) == 4
                   for s in (0, 1) for y in (0, 1))
    (d / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in contexts))
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16,
                                               device_map="cuda", attn_implementation="sdpa").eval()
    L = model.config.num_hidden_layers
    res_layers, att_layers = list(range(0, L, 4)) + [L], list(range(3, L, 4))
    capture = {"on": False}
    if a.probe_train:
        for li in att_layers:
            att = model.model.layers[li].self_attn
            def hook(space, layer):
                def f(module, args, output):
                    if capture["on"]:
                        capture[(space, layer)] = output[0, capture["anchors"]].reshape(16, -1).float().cpu().numpy()
                return f
            (att.k_norm if hasattr(att, "k_norm") else att.k_proj).register_forward_hook(hook("key", li))
            att.v_proj.register_forward_hook(hook("value", li))
    features = {x: [] for x in ("residual", "key", "value")}
    sources, label_meta = [], []
    errors = []
    with (d / "behavior.jsonl").open("w") as f, torch.inference_mode():
        for ci, ctx in enumerate(contexts):
            caches, ids_all, sites_all = {}, {}, {}
            pair = {x: [] for x in features}
            for donor in ("base", "source", "label"):
                if ci < a.probe_train and donor == "label":
                    continue
                ids, sites = encode(tok, ctx, labels, a.dataset, donor)
                capture.update(on=bool(a.probe_train and donor in ("base", "source")), anchors=sites["label_anchor"])
                out = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True,
                            output_hidden_states=capture["on"], logits_to_keep=1)
                if capture["on"]:
                    pair["residual"].append(np.stack([out.hidden_states[l][0, sites["label_anchor"]].float().cpu().numpy()
                                                       for l in res_layers]))
                    for space in ("key", "value"):
                        pair[space].append(np.stack([capture[(space, l)] for l in att_layers]))
                caches[donor], ids_all[donor], sites_all[donor] = out.past_key_values, ids, sites
                del out
            capture["on"] = False
            for donor in caches:
                assert sites_all[donor] == sites_all["base"]
                assert len(ids_all[donor]) == len(ids_all["base"])
            if a.probe_train:
                for space in features:
                    features[space].append(np.stack(pair[space]).astype(np.float16))
                sources.append([x["source"] for x in ctx["demos"]])
                label_meta.append([x["label"] for x in ctx["demos"]])
            if ci < a.probe_train:
                continue
            plen = len(ids_all["base"])
            scores = {c: score(model, tok, copy.deepcopy(cache), ctx, labels, plen, a.dataset) for c, cache in caches.items()}
            for donor in ("source", "label"):
                for site, positions in sites_all["base"].items():
                    for channel in ("key", "value", "kv"):
                        scores[f"{donor}.{site}.{channel}"] = score(model, tok, patch(caches["base"], caches[donor], positions, channel),
                                                                     ctx, labels, plen, a.dataset)
                errors.append(float(np.max(np.abs(scores[donor] - scores[f"{donor}.full.kv"]))))
            scores["noop"] = score(model, tok, copy.deepcopy(caches["base"]), ctx, labels, plen, a.dataset)
            errors.append(float(np.max(np.abs(scores["base"] - scores["noop"]))))
            ids, _ = encode(tok, ctx, labels, a.dataset, instruction=True)
            ins = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
            scores["instruction"] = score(model, tok, ins, ctx, labels, len(ids), a.dataset)
            f.write(json.dumps({"context": ci, "signs": [2 * q["label"] - 1 for q in ctx["queries"]],
                                "scores": {k: v.tolist() for k, v in scores.items()}}) + "\n")
            f.flush()
            if ci % 4 == 0:
                print(ci, round(time.time() - t0, 1), flush=True)
    if a.probe_train:
        for space, data in features.items():
            np.save(d / f"{space}.npy", np.stack(data))
        np.savez(d / "metadata.npz", source=sources, label=label_meta, train=a.probe_train,
                 residual_layers=res_layers, attention_layers=att_layers)
    run = {"args": vars(a), "seconds": time.time() - t0, "sanity_max_error": max(errors),
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "model_config_sha256": hashlib.sha256((Path(a.model) / "config.json").read_bytes()).hexdigest(),
           "host": platform.node(), "gpu": torch.cuda.get_device_name(),
           "torch": torch.__version__, "transformers": transformers.__version__}
    (d / "run.json").write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == "__main__":
    main()
