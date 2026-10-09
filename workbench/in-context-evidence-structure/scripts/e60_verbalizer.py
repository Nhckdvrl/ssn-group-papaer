"""Matched verbalizers; transplant non-label K without changing output values."""
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
    if a.dataset == "synthetic":
        ctxs = make_contexts(a.stage, a.n, a.seed)
    else:
        ctxs = real_contexts("train" if a.stage == "discovery" else "test", a.n, a.seed)
    vocabs = {"yes_no": ["yes", "no"], "toxic_safe": ["toxic", "safe"]}
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.bfloat16,
                                               device_map="cuda", attn_implementation="sdpa").eval()
    (d / "contexts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in ctxs))
    errors = []
    with (d / "behavior.jsonl").open("w") as f, torch.inference_mode():
        for i, ctx in enumerate(ctxs):
            caches, lengths, sites = {}, {}, {}
            for vocab, labels in vocabs.items():
                ids, st = encode(tok, ctx, labels, a.dataset)
                caches[vocab] = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
                lengths[vocab], sites[vocab] = len(ids), st
            assert sites["yes_no"] == sites["toxic_safe"]
            assert lengths["yes_no"] == lengths["toxic_safe"]
            scores = {}
            for vocab, labels in vocabs.items():
                plen = lengths[vocab]
                scores[vocab + ".base"] = score(model, tok, copy.deepcopy(caches[vocab]), ctx, labels, plen, a.dataset)
                scores[vocab + ".noop"] = score(model, tok, copy.deepcopy(caches[vocab]), ctx, labels, plen, a.dataset)
                errors.append(float(abs(scores[vocab + ".base"] - scores[vocab + ".noop"]).max()))
                donor = "toxic_safe" if vocab == "yes_no" else "yes_no"
                for site, channel in [("source_name", "key"), ("source_name", "value"),
                                      ("label_prediction", "key"), ("label_anchor", "key")]:
                    scores[f"{vocab}.{site}.{channel}"] = score(model, tok, patch(caches[vocab], caches[donor], sites[vocab][site], channel),
                                                               ctx, labels, plen, a.dataset)
                ids, _ = encode(tok, ctx, labels, a.dataset, instruction=True)
                c = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
                scores[vocab + ".instruction"] = score(model, tok, c, ctx, labels, len(ids), a.dataset)
                single_scores = []
                for s in (0, 1):
                    sc = {"demos": [x for x in ctx["demos"] if x["source"] == s],
                          "queries": [q for q in ctx["queries"] if q["source"] == s]}
                    ids, _ = encode(tok, sc, labels, a.dataset)
                    c = model(input_ids=torch.tensor([ids], device="cuda"), use_cache=True, logits_to_keep=1).past_key_values
                    ss = score(model, tok, c, sc, labels, len(ids), a.dataset)
                    # Preserve original query order when source names are randomized in E56.
                    single_scores += [(qi, float(ss[j])) for j, qi in enumerate([j for j, q in enumerate(ctx["queries"]) if q["source"] == s])]
                scores[vocab + ".single"] = [v for _, v in sorted(single_scores)]
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
