"""Do independently effective source K and label V interventions compose?"""
import argparse
import copy
import hashlib
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from e58_factorization import make_contexts
from e59_mediation import encode, patch, real_contexts, score


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
    d = Path(a.out)
    d.mkdir(parents=True, exist_ok=True)
    ctxs = make_contexts(a.stage, a.n, a.seed) if a.dataset == "synthetic" else real_contexts(
        "train" if a.stage == "discovery" else "test", a.n, a.seed)
    labels = ["yes", "no"] if a.dataset == "synthetic" and a.stage == "discovery" else ["toxic", "safe"]
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16,
                                               device_map="cuda", attn_implementation="sdpa").eval()
    (d / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in ctxs))
    errors = []
    with (d / "behavior.jsonl").open("w") as f, torch.inference_mode():
        for i, ctx in enumerate(ctxs):
            caches, lengths, sites = {}, {}, {}
            for donor in ("base", "source", "label", "natural_double"):
                cc = copy.deepcopy(ctx)
                if donor == "natural_double":
                    for demo in cc["demos"]:
                        demo["source"] ^= 1
                        demo["label"] ^= 1
                ids, st = encode(tok, cc, labels, a.dataset, donor if donor != "natural_double" else "base")
                caches[donor] = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
                lengths[donor], sites[donor] = len(ids), st
                assert st == sites["base"] and len(ids) == lengths["base"]
            plen, st = lengths["base"], sites["base"]
            scores = {c: score(model, tok, copy.deepcopy(cache), ctx, labels, plen, a.dataset) for c, cache in caches.items()}
            kcache = patch(caches["base"], caches["source"], st["source_name"], "key")
            scores["K"] = score(model, tok, copy.deepcopy(kcache), ctx, labels, plen, a.dataset)
            for channel, name in (("value", "V"), ("kv", "YKV")):
                vc = patch(caches["base"], caches["label"], st["label_anchor"], channel)
                kcvc = patch(kcache, caches["label"], st["label_anchor"], channel)
                scores[name] = score(model, tok, vc, ctx, labels, plen, a.dataset)
                scores["K+" + name] = score(model, tok, kcvc, ctx, labels, plen, a.dataset)
            scores["noop"] = score(model, tok, copy.deepcopy(caches["base"]), ctx, labels, plen, a.dataset)
            errors.append(float(abs(scores["base"] - scores["noop"]).max()))
            f.write(json.dumps({"context": i, "signs": [2 * q["label"] - 1 for q in ctx["queries"]],
                                "scores": {k: list(map(float, v)) for k, v in scores.items()}}) + "\n")
            f.flush()
            if i % 8 == 0:
                print(i, round(time.time() - t0, 1), flush=True)
    run = {"args": vars(a), "seconds": time.time() - t0, "sanity_max_error": max(errors),
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "gpu": torch.cuda.get_device_name()}
    (d / "run.json").write_text(json.dumps(run, indent=2))
    print(json.dumps(run), flush=True)


if __name__ == "__main__":
    main()
