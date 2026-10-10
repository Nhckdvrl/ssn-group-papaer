"""Same-name criterion interchange before any test review; recipient demos stay.

No layer selection, learned probe, or sample filtering. See E88 preregistration.
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


NAMES = ["Alice", "Bob"]
LABELS = ["negative", "positive"]
# Development and confirmation vocabularies are disjoint within each aspect/sign.
PHRASES = {
    "discovery": {
        "demo": [
            ["The meal was delicious", "The dishes tasted wonderful", "The food was excellent"],
            ["The meal was awful", "The dishes tasted terrible", "The food was disappointing"],
            ["The staff were helpful", "The service was attentive", "The waiters were friendly"],
            ["The staff were rude", "The service was careless", "The waiters were unhelpful"],
        ],
        "query": [
            ["The cooking impressed me", "The flavors were delightful", "The dinner tasted fantastic"],
            ["The cooking disgusted me", "The flavors were unpleasant", "The dinner tasted horrible"],
            ["The employees treated us kindly", "The servers took great care of us", "The team served us promptly"],
            ["The employees treated us badly", "The servers neglected us", "The team kept us waiting rudely"],
        ],
    },
    "confirmation": {
        "demo": [
            ["The cuisine was superb", "The entree was tasty", "The chef prepared a lovely meal"],
            ["The cuisine was dreadful", "The entree was inedible", "The chef prepared a revolting meal"],
            ["The host was courteous", "The waiter was considerate", "The staff gave us a warm welcome"],
            ["The host was impolite", "The waiter was dismissive", "The staff ignored our requests"],
        ],
        "query": [
            ["I loved every bite", "The soup was heavenly", "The pasta was appetizing"],
            ["I hated every bite", "The soup was foul", "The pasta was tasteless"],
            ["We received thoughtful assistance", "Our requests were handled with care", "The waitress was exceptionally polite"],
            ["We received insulting treatment", "Our requests were brushed aside", "The waitress was exceptionally nasty"],
        ],
    },
}


def contexts(n, seed, stage):
    rng = np.random.default_rng(seed)
    pools = PHRASES[stage]
    out = []
    for ci in range(n):
        criteria = [int(rng.integers(2)), 0]
        criteria[1] = 1 - criteria[0]
        demo_phrases = [str(rng.choice(p)) for p in pools["demo"]]
        samples = [rng.choice(p, 2, replace=False).tolist() for p in pools["query"]]
        order_food_first = bool(rng.integers(2))

        def review(f, s, ps):
            parts = [ps[0 if f == 1 else 1], ps[2 if s == 1 else 3]]
            if not order_food_first:
                parts.reverse()
            return ". ".join(parts) + "."

        demos = []
        queries = []
        for f in (-1, 1):
            for s in (-1, 1):
                for source in (0, 1):
                    demos.append({"source": source, "food": f, "service": s,
                                  "text": review(f, s, demo_phrases)})
        rng.shuffle(demos)
        for template in (0, 1):
            ps = [p[template] for p in samples]
            for source in (0, 1):
                for f in (-1, 1):
                    for s in (-1, 1):
                        gold = (f, s)[criteria[source]]
                        queries.append({"source": source, "food": f, "service": s,
                                        "template": template, "text": review(f, s, ps),
                                        "recipient_gold": gold, "donor_gold": (s, f)[criteria[source]]})
        assert not {d["text"] for d in demos} & {q["text"] for q in queries}
        out.append({"context": ci, "criteria": criteria, "demos": demos, "queries": queries})
    return out


def prefix_text(ctx, flip=False, instruction=False, explicit=False):
    criteria = [1 - c if flip else c for c in ctx["criteria"]]
    head = "Below are restaurant reviews and judgments from two reviewers.\n\n"
    if instruction:
        head += "Infer each reviewer's judgment criterion from their examples and answer according to the requested reviewer.\n\n"
    if explicit:
        head += " ".join(f"{name} judges only the {'food' if c == 0 else 'service'}."
                         for name, c in zip(NAMES, criteria)) + "\n\n"
    for d in ctx["demos"]:
        sign = (d["food"], d["service"])[criteria[d["source"]]]
        head += f"Source: {NAMES[d['source']]}\nReview: {d['text']}\nLabel: {LABELS[int(sign > 0)]}\n\n"
    return head


def interval(v):
    v = np.asarray(v, dtype=float)
    indices = np.random.default_rng(880).integers(len(v), size=(10000, len(v)))
    return {"mean": float(v.mean()), "ci95": np.quantile(v[indices].mean(1), [.025, .975]).tolist(),
            "n_contexts": len(v)}


def analyze(dest):
    rows = [json.loads(line) for line in (dest / "behavior.jsonl").read_text().splitlines()]
    run = json.loads((dest / "run.json").read_text())
    assert len(rows) == run["args"]["n"]
    assert run["numeric_max_error"] <= .01
    f = np.array([[q["food"] for q in r["queries"]] for r in rows])
    s = np.array([[q["service"] for q in r["queries"]] for r in rows])
    g = np.array([[q["recipient_gold"] for q in r["queries"]] for r in rows])
    dg = np.array([[q["donor_gold"] for q in r["queries"]] for r in rows])
    disagree = f[0] != s[0]
    out = {"run": run, "conditions": {}, "contrasts": {}}
    scores = {k: np.array([[q[k]["z"] for q in r["scores"]] for r in rows])
              for k in rows[0]["scores"][0]}
    for key, z in scores.items():
        c = {"recipient_accuracy": interval(((z > 0) == (g > 0)).mean(1)),
             "donor_accuracy": interval(((z > 0) == (dg > 0)).mean(1)),
             "disagree_recipient_accuracy": interval(((z[:, disagree] > 0) == (g[:, disagree] > 0)).mean(1)),
             "bias": interval(z.mean(1)), "food_coefficient": interval((z * f).mean(1)),
             "service_coefficient": interval((z * s).mean(1)),
             "criterion_selectivity": interval((z * (g - dg) / 2).mean(1)),
             "unrestricted_label_argmax_fraction": interval(np.array([
                 [int(q[key]["argmax_is_label"]) for q in r["scores"]] for r in rows]).mean(1))}
        # Criteria and source assignment vary between contexts: semantic coefficients
        # must also be reported per source, not only averaged over both reviewers.
        c["by_source"] = {}
        for source in (0, 1):
            mask = np.array([q["source"] == source for q in rows[0]["queries"]])
            c["by_source"][NAMES[source]] = {
                "food_coefficient": interval((z[:, mask] * f[:, mask]).mean(1)),
                "service_coefficient": interval((z[:, mask] * s[:, mask]).mean(1)),
                "criterion_selectivity": interval((z[:, mask] * (g[:, mask] - dg[:, mask]) / 2).mean(1))}
        out["conditions"][key] = c
    for patch, base in [("criterion_patch", "base"), ("name_patch", "base"),
                        ("flip", "base"), ("instruction", "base"),
                        ("explicit_criterion_patch", "explicit"), ("explicit_flip", "explicit")]:
        delta = scores[patch] - scores[base]
        directional = delta * (dg - g) / 2
        vals = directional[:, disagree].mean(1)
        d = {"donor_directed_transfer": interval(vals), "bias_shift": interval(delta.mean(1)),
             "agree_absolute_shift": interval(np.abs(delta[:, ~disagree]).mean(1)),
             "recipient_accuracy_change": interval((((scores[patch] > 0) == (g > 0)).astype(float)
                                                      - ((scores[base] > 0) == (g > 0))).mean(1))}
        for direction in (-1, 1):
            # Balance both source identities and opposite-sign reviews; no cancellation
            # of an unconditional positive/negative preference can count as transfer.
            mask = disagree[None, :] & (dg == direction)
            d[f"donor_sign_{direction}"] = interval((directional * mask).sum(1) / mask.sum(1))
        out["contrasts"][patch + "_minus_" + base] = d
    num = out["contrasts"]["criterion_patch_minus_base"]["donor_directed_transfer"]["mean"]
    den = out["contrasts"]["flip_minus_base"]["donor_directed_transfer"]["mean"]
    out["transfer_native_ratio_descriptive"] = num / den if abs(den) > .1 else None
    (dest / "analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    for k, c in out["conditions"].items():
        print(k, "accuracy", c["recipient_accuracy"], "selectivity", c["criterion_selectivity"], flush=True)
    for k, c in out["contrasts"].items():
        print(k, "T", c["donor_directed_transfer"], flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--seed", type=int, default=88001)
    ap.add_argument("--stage", choices=list(PHRASES), default="discovery")
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--analyze-only", action="store_true")
    args = ap.parse_args()
    dest = Path(args.out)
    if args.analyze_only:
        analyze(dest)
        return
    from transformers import AutoTokenizer
    dest.mkdir(parents=True, exist_ok=True)
    cs = contexts(args.n, args.seed, args.stage)
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    encode = lambda text: tokenizer.encode(text, add_special_tokens=False)
    label_ids = [encode(" " + label) for label in LABELS]
    assert all(len(ids) == 1 for ids in label_ids), label_ids
    source_ids = [encode(f"Source: {name}\n") for name in NAMES]
    assert len(source_ids[0]) == len(source_ids[1])
    preflight = {"args": vars(args), "label_ids": label_ids, "source_ids": source_ids,
                 "conditions": ["base", "flip", "instruction", "explicit", "explicit_flip",
                                "criterion_patch", "name_patch", "explicit_criterion_patch"],
                 "example_recipient": prefix_text(cs[0]), "example_donor": prefix_text(cs[0], flip=True),
                 "example_query": cs[0]["queries"][0]}
    for ctx in cs:
        for explicit in (False, True):
            base = encode(prefix_text(ctx, explicit=explicit))
            donor = encode(prefix_text(ctx, flip=True, explicit=explicit))
            assert len(base) == len(donor), (len(base), len(donor))
            if not explicit:
                assert all(x == y or {x, y} == {label_ids[0][0], label_ids[1][0]}
                           for x, y in zip(base, donor))
    (dest / "preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    if args.preflight_only:
        print("preflight passed: all contexts, labels, source spans, donor token alignment", flush=True)
        return
    assert not (dest / "behavior.jsonl").exists(), "Refuse overwriting an existing run"
    import torch
    import transformers
    from transformers import AutoModelForCausalLM
    torch.set_num_threads(6)
    torch.manual_seed(0)
    started = time.time()
    print("loading model", flush=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, dtype=torch.float32,
                                               device_map="cuda", attn_implementation="eager").eval()
    print("model loaded", flush=True)
    errors = []
    (dest / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in cs))

    def forward(cache, ids):
        cache = copy.deepcopy(cache)
        plen = cache.get_seq_length() if cache is not None else 0
        ids = torch.tensor([ids], device="cuda")
        output = model(input_ids=ids, past_key_values=cache, use_cache=True, logits_to_keep=1,
                       attention_mask=torch.ones((1, plen + ids.shape[1]), dtype=torch.long, device="cuda"),
                       position_ids=torch.arange(plen, plen + ids.shape[1], device="cuda")[None])
        logits = output.logits[0, -1].float()
        top = int(logits.argmax())
        return output.past_key_values, {"z": float(logits[label_ids[1][0]] - logits[label_ids[0][0]]),
                                      "argmax_token": top, "argmax_is_label": top in [x[0] for x in label_ids]}

    def transplant(base, donor, start):
        patched = copy.deepcopy(base)
        assert base.get_seq_length() == donor.get_seq_length()
        for dst, src in zip(patched.layers, donor.layers):
            dst.keys[..., start:, :] = src.keys[..., start:, :]
            dst.values[..., start:, :] = src.values[..., start:, :]
        return patched

    with torch.inference_mode(), (dest / "behavior.jsonl").open("w") as stream:
        for ci, ctx in enumerate(cs):
            settings = {"base": {}, "flip": {"flip": True}, "instruction": {"instruction": True},
                        "explicit": {"explicit": True}, "explicit_flip": {"explicit": True, "flip": True}}
            prefixes, prefix_ids, capsules = {}, {}, {}
            for key, setting in settings.items():
                prefix_ids[key] = encode(prefix_text(ctx, **setting))
                prefixes[key] = forward(None, prefix_ids[key])[0]
                for source in (0, 1):
                    capsules[key, source] = forward(prefixes[key], source_ids[source])[0]
            for source in (0, 1):
                start = len(prefix_ids["base"])
                capsules["criterion_patch", source] = transplant(capsules["base", source], capsules["flip", source], start)
                capsules["name_patch", source] = transplant(capsules["base", source], capsules["base", 1-source], start)
                capsules["explicit_criterion_patch", source] = transplant(
                    capsules["explicit", source], capsules["explicit_flip", source], len(prefix_ids["explicit"]))
            scores = []
            for qi, query in enumerate(ctx["queries"]):
                source = query["source"]
                suffix = encode(f"Review: {query['text']}\nLabel:")
                row = {key: forward(capsules[key, source], suffix)[1] for key in preflight["conditions"]}
                if qi in (0, 8):
                    unsplit = forward(prefixes["base"], source_ids[source] + suffix)[1]
                    noop = forward(transplant(capsules["base", source], capsules["base", source],
                                             len(prefix_ids["base"])), suffix)[1]
                    errors.extend([abs(row["base"]["z"] - unsplit["z"]), abs(row["base"]["z"] - noop["z"])])
                scores.append(row)
            stream.write(json.dumps({"context": ci, "criteria": ctx["criteria"], "queries": ctx["queries"],
                                     "scores": scores}) + "\n")
            stream.flush()
            print(f"context {ci + 1}/{len(cs)}, elapsed {time.time() - started:.1f}s, numeric {max(errors):.6g}", flush=True)
            assert max(errors) <= .01, "Numerical control failed; keep this VOID run"
    run = {"args": vars(args), "seconds": time.time() - started, "numeric_max_error": max(errors),
           "torch": torch.__version__, "transformers": transformers.__version__, "host": platform.node(),
           "gpu": torch.cuda.get_device_name(), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "config_sha256": hashlib.sha256((Path(args.model) / "config.json").read_bytes()).hexdigest(),
           "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}
    (dest / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    analyze(dest)


if __name__ == "__main__":
    main()
