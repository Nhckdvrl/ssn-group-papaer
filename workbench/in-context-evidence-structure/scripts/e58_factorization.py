"""E58: balanced source x label probes and matched cache interventions.

No adapter training. Paired prefixes differ only in source names. All decoder
splits keep a context and its source-swapped twin in the same partition.
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


LEXICA = {
    "discovery": (
        "cat dog horse cow pig sheep goat rabbit mouse lion tiger bear wolf fox deer monkey elephant zebra giraffe panda".split(),
        "apple pear banana orange peach plum grape cherry mango lemon lime melon papaya kiwi apricot pineapple coconut fig date berry".split(),
    ),
    "confirmation": (
        "doctor nurse teacher lawyer judge painter singer dancer farmer baker chef pilot sailor soldier engineer scientist dentist plumber carpenter librarian".split(),
        "car bus truck train taxi bicycle motorcycle airplane helicopter boat ship ferry canoe yacht scooter tram subway wagon ambulance tractor".split(),
    ),
}
NAMES = ["Alex", "Sam"]
HEAD = "Below are items and the labels that individual sources gave them. Labels are arbitrary classification codes.\n\n"
INSTRUCTION = "Use only examples from the requested source; each source may use a different mapping.\n\n"


def make_contexts(stage, n, seed):
    rng = np.random.default_rng(seed)
    contexts = []
    for ci in range(n):
        words = [rng.choice(pool, 10, replace=False).tolist() for pool in LEXICA[stage]]
        orientation = int(rng.integers(2))
        demos = []
        for source in range(2):
            for kind in range(2):
                for word in words[kind][source * 4:(source + 1) * 4]:
                    label = kind ^ source ^ orientation
                    demos.append({"word": word, "source": source, "kind": kind, "label": label})
        demos = [demos[i] for i in rng.permutation(16)]
        queries = [{"word": words[kind][8], "source": source, "kind": kind,
                    "label": kind ^ source ^ orientation} for source in range(2) for kind in range(2)]
        assert all(sum(d["source"] == s and d["label"] == y for d in demos) == 4
                   for s in range(2) for y in range(2))
        contexts.append({"context": ci, "orientation": orientation, "demos": demos, "queries": queries})
    return contexts


def encode_prefix(tok, ctx, labels, swapped=False, instruction=False):
    enc = lambda s: tok.encode(s, add_special_tokens=False)
    ids = enc(HEAD + (INSTRUCTION if instruction else ""))
    anchors = []
    for d in ctx["demos"]:
        ids += enc(f'Item: {d["word"]}\nSource: {NAMES[d["source"] ^ int(swapped)]}\nLabel:')
        anchors.append(len(ids))
        answer = enc(" " + labels[d["label"]])
        assert len(answer) == 1, (labels, answer)
        ids += answer + enc("\n\n")
    return ids, anchors


def cache_layers(cache):
    return cache.layers


def modified_cache(base, donor, anchors, condition):
    out = copy.deepcopy(donor if condition == "full" else base)
    if condition in ("key", "value", "kv"):
        for dst, src in zip(cache_layers(out), cache_layers(donor)):
            if condition in ("key", "kv"):
                dst.keys[:, :, anchors, :] = src.keys[:, :, anchors, :]
            if condition in ("value", "kv"):
                dst.values[:, :, anchors, :] = src.values[:, :, anchors, :]
    return out


@torch.inference_mode()
def score_queries(model, tok, cache, ctx, labels, plen):
    seqs = [tok.encode(f'Item: {q["word"]}\nSource: {NAMES[q["source"]]}\nLabel:',
                       add_special_tokens=False) for q in ctx["queries"]]
    width = max(map(len, seqs))
    ids = torch.full((len(seqs), width), tok.pad_token_id or 0, dtype=torch.long, device="cuda")
    mask = torch.zeros((len(seqs), plen + width), dtype=torch.long, device="cuda")
    mask[:, :plen] = 1
    pos = torch.zeros_like(ids)
    for i, seq in enumerate(seqs):
        ids[i, -len(seq):] = torch.tensor(seq, device="cuda")
        mask[i, -len(seq):] = 1
        pos[i, -len(seq):] = torch.arange(plen, plen + len(seq), device="cuda")
    cache.batch_repeat_interleave(len(seqs))
    logits = model(input_ids=ids, attention_mask=mask, position_ids=pos,
                   past_key_values=cache, logits_to_keep=1, use_cache=True).logits[:, -1].float()
    label_ids = [tok.encode(" " + x, add_special_tokens=False)[0] for x in labels]
    return (logits[:, label_ids[1]] - logits[:, label_ids[0]]).cpu().numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stage", choices=list(LEXICA), default="discovery")
    ap.add_argument("--train", type=int, default=64)
    ap.add_argument("--test", type=int, default=64)
    ap.add_argument("--seed", type=int, default=58001)
    a = ap.parse_args()
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(6)
    torch.manual_seed(0)
    t0 = time.time()
    labels = ["yes", "no"] if a.stage == "discovery" else ["toxic", "safe"]
    contexts = make_contexts(a.stage, a.train + a.test, a.seed)
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True,
                                               dtype=torch.bfloat16, device_map="cuda",
                                               attn_implementation="sdpa").eval()
    L = model.config.num_hidden_layers
    residual_layers = list(range(0, L, 4)) + [L]
    attention_layers = list(range(3, L, 4))
    capture = {"on": False}
    handles = []
    for li in attention_layers:
        att = model.model.layers[li].self_attn
        def hook(space, layer):
            def f(module, args, output):
                if capture["on"]:
                    x = output[0, capture["anchors"]].reshape(16, -1)
                    capture[(space, layer)] = x.float().cpu().numpy()
            return f
        handles.append((att.k_norm if hasattr(att, "k_norm") else att.k_proj).register_forward_hook(hook("key", li)))
        handles.append(att.v_proj.register_forward_hook(hook("value", li)))
    features = {x: [] for x in ("residual", "key", "value")}
    sources, label_meta = [], []
    noop_errors, full_errors, repeat_errors = [], [], []
    with (outdir / "contexts.jsonl").open("w") as f:
        for ctx in contexts:
            f.write(json.dumps(ctx) + "\n")
    with (outdir / "behavior.jsonl").open("w") as f, torch.inference_mode():
        for ci, ctx in enumerate(contexts):
            pair_features = {x: [] for x in features}
            caches, anchor_positions, prefix_lengths = [], [], []
            for swapped in (False, True):
                ids, anchors = encode_prefix(tok, ctx, labels, swapped)
                capture.update(on=True, anchors=anchors)
                result = model(input_ids=torch.tensor([ids], device="cuda"), output_hidden_states=True,
                               use_cache=True, logits_to_keep=1)
                pair_features["residual"].append(np.stack([result.hidden_states[l][0, anchors].float().cpu().numpy()
                                                           for l in residual_layers]))
                for space in ("key", "value"):
                    pair_features[space].append(np.stack([capture[(space, l)] for l in attention_layers]))
                caches.append(result.past_key_values)
                anchor_positions.append(anchors)
                prefix_lengths.append(len(ids))
                del result
            capture["on"] = False
            assert anchor_positions[0] == anchor_positions[1]
            assert prefix_lengths[0] == prefix_lengths[1]
            for space in features:
                features[space].append(np.stack(pair_features[space]).astype(np.float16))
            sources.append([d["source"] for d in ctx["demos"]])
            label_meta.append([d["label"] for d in ctx["demos"]])
            if ci >= a.train:
                scores = {}
                for condition in ("base", "renamed", "key", "value", "kv", "full", "noop"):
                    if condition == "renamed":
                        cache = copy.deepcopy(caches[1])
                    else:
                        cache = modified_cache(caches[0], caches[1], anchor_positions[0], condition)
                    scores[condition] = score_queries(model, tok, cache, ctx, labels, prefix_lengths[0])
                noop_errors.append(float(np.max(np.abs(scores["base"] - scores["noop"]))))
                full_errors.append(float(np.max(np.abs(scores["full"] - scores["renamed"]))))
                if ci < a.train + 8:
                    repeat = score_queries(model, tok, copy.deepcopy(caches[0]), ctx, labels, prefix_lengths[0])
                    repeat_errors.append(float(np.max(np.abs(repeat - scores["base"]))))
                ids, _ = encode_prefix(tok, ctx, labels, instruction=True)
                instruction_cache = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True,
                                          logits_to_keep=1).past_key_values
                scores["instruction"] = score_queries(model, tok, instruction_cache, ctx, labels, len(ids))
                signs = np.array([2 * q["label"] - 1 for q in ctx["queries"]])
                f.write(json.dumps({"context": ci, "signs": signs.tolist(),
                                    "scores": {k: v.tolist() for k, v in scores.items()}}) + "\n")
                f.flush()
            del caches
            if ci % 8 == 0:
                print(json.dumps({"context": ci, "seconds": round(time.time() - t0, 1)}), flush=True)
    for space, data in features.items():
        np.save(outdir / f"{space}.npy", np.stack(data))
    np.savez(outdir / "metadata.npz", source=np.array(sources), label=np.array(label_meta),
             residual_layers=residual_layers, attention_layers=attention_layers, train=a.train)
    meta = {"args": vars(a), "labels": labels, "torch": torch.__version__, "transformers": transformers.__version__,
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "config_sha256": hashlib.sha256((Path(a.model) / "config.json").read_bytes()).hexdigest(),
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "host": platform.node(), "gpu": torch.cuda.get_device_name(), "seconds": time.time() - t0,
            "noop_max_error": max(noop_errors, default=None), "full_max_error": max(full_errors, default=None),
            "repeat_max_error": max(repeat_errors, default=None)}
    (outdir / "run.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta), flush=True)


if __name__ == "__main__":
    main()
